import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs

from edits_api import EditsClient, EditsError, Session, get_operation, list_operations
from edits_api.cli import main
from edits_api import _wire

FIXTURE = Path(__file__).parent / "fixtures/reel_details.synthetic.json"


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.requests = []
        self.raw = FIXTURE.read_bytes()
        def transport(request, timeout):
            self.requests.append(request)
            return 200, self.raw, "text/javascript; charset=utf-8"
        self.transport = transport
        self.session = Session.from_sessionid("999:SYNTHETIC-ONLY")
        self.client = EditsClient(self.session, transport=transport)

    def variables(self):
        return json.loads(parse_qs(self.requests[-1].data.decode())["variables"][0])

    def test_typed_retention_and_metrics(self):
        result = self.client.reel_insights("12345")
        self.assertEqual(result.retention[1].percent, 80)
        self.assertIsNone(result.retention[2].value)
        self.assertEqual(result.retention[3].value, 0)
        self.assertEqual(result.metrics["skip_rate"]["value"], 0.2)
        self.assertEqual(result.metrics["skip_rate"]["delta"], -0.1)
        self.assertIn("1fvalue", result.response.payload["data"]["1$xig_fetch_media(id:$media_id)"]["basel_media_level_insights"]["skip_rate"])
        self.assertEqual(self.variables(), {"media_id": "12345", "include_creative_tools": False})
        self.assertFalse(result.response.live_request)

    def test_packaged_retention_wire_matches_original_verified_builder(self):
        expected = _wire.make_request("12345", dict(self.session._headers))
        self.client.reel_insights("12345")
        actual = self.requests[-1]
        self.assertEqual(actual.full_url, expected.full_url)
        self.assertEqual(actual.get_method(), expected.get_method())
        self.assertEqual(actual.data, expected.data)
        self.assertEqual(dict(actual.header_items()), dict(expected.header_items()))

    def test_export_and_no_credential_leak(self):
        with tempfile.TemporaryDirectory() as temp:
            output = self.client.reel_insights("12345").export(Path(temp) / "out")
            self.assertEqual(len(list(output.iterdir())), 5)
            for path in output.iterdir():
                self.assertNotIn("SYNTHETIC-ONLY", path.read_text())
            with self.assertRaises(EditsError):
                self.client.reel_insights("12345").export(output)

    def test_session_repr_hides_credentials(self):
        self.assertNotIn("SYNTHETIC-ONLY", repr(self.session))
        self.assertNotIn("Bearer", repr(self.session))

    def test_environment_requires_exactly_one_credential(self):
        for env in ({}, {"IG_SESSIONID": "999:fake", "IG_AUTHORIZATION": "fake"}):
            with patch.dict(os.environ, env, clear=True), self.assertRaises(EditsError):
                Session.from_env()
        with patch.dict(os.environ, {"IG_SESSIONID": "999:fake"}, clear=True):
            self.assertEqual(Session.from_env().user_id, "999")

    def test_catalog_and_copy_isolation(self):
        self.assertEqual(len(list_operations()), 1663)
        self.assertEqual(len(list_operations(edits_only=True)), 88)
        op = get_operation("BaselReelDetailsQuery")
        self.assertEqual(op["client_doc_id"], "3261342854360971614358769315")
        op["client_doc_id"] = "changed"
        self.assertNotEqual(get_operation("BaselReelDetailsQuery")["client_doc_id"], "changed")

    def test_unknown_query_and_distillery_rejected_before_network(self):
        names = ["NotARealQuery", next(o["operation_name"] for o in list_operations() if o["schema"] != "instagram")]
        for name in names:
            with self.assertRaises(EditsError): self.client.execute(name, {})
        self.assertEqual(self.requests, [])

    def test_mutation_needs_explicit_per_call_opt_in(self):
        name = "BaselKitDeleteMutation"
        with self.assertRaises(EditsError): self.client.execute(name, {"kit_id": "synthetic"})
        self.assertFalse(self.requests)
        self.client.execute(name, {"kit_id": "synthetic"}, allow_mutation=True)
        self.assertEqual(parse_qs(self.requests[-1].data.decode())["fb_api_req_friendly_name"], [name])

    def test_account_page_uses_its_own_doc_id_and_variables(self):
        self.client.account_reels(first=5, after="synthetic-cursor", timeframe="ONE_WEEK", order_by="BY_VIEWS")
        self.assertEqual(self.variables()["after"], "synthetic-cursor")
        self.assertEqual(self.variables()["user_id"], "999")
        self.assertEqual(parse_qs(self.requests[-1].data.decode())["client_doc_id"], ["11900819615835482353778696516"])
        self.assertEqual(self.requests[-1].get_header("X-client-doc-id"), "11900819615835482353778696516")

    def test_page_invalid_enum_stops_before_network(self):
        for kwargs in ({"timeframe": "UNKNOWN"}, {"sort_direction": "DOWN"}, {"first": 0}, {"order_by": "INVALID"}):
            with self.assertRaises(EditsError): self.client.account_reels(**kwargs)
        self.assertFalse(self.requests)

    def test_other_wrappers(self):
        self.client.account_insights(period="caller-verified", include_time_series=True)
        self.assertTrue(self.variables()["shouldIncludeTimeSeries"])
        self.client.audience_insights(period="caller-verified", client_timezone="UTC")
        self.assertEqual(self.variables()["client_timezone"], "UTC")
        self.client.public_insights("42_999")
        self.assertEqual(self.variables(), {"media_id": "42"})
        self.client.reels_delta(["42_999", "43"])
        self.assertEqual(self.variables(), {"media_ids": ["42", "43"]})
        self.client.comment_insights("42", sort_order="caller-verified")
        self.assertEqual(self.variables()["sort_order"], "caller-verified")

    def test_http_failure_does_not_retry(self):
        calls = []
        def fail(request, timeout):
            calls.append(1); return 429, b'{}', 'application/json'
        with self.assertRaisesRegex(EditsError, "HTTP 429"):
            EditsClient(self.session, transport=fail).reel_insights("12345")
        self.assertEqual(calls, [1])

    def test_foreign_owner_rejected(self):
        client = EditsClient(Session.from_sessionid("888:fake"), transport=self.transport)
        with self.assertRaises(EditsError): client.reel_insights("12345")

    def test_response_save_json_refuses_overwrite(self):
        result = self.client.execute("BaselPublicInsightsQuery", {"media_id": "12345"})
        with tempfile.TemporaryDirectory() as temp:
            path = result.save_json(Path(temp) / "response.json")
            self.assertEqual(json.loads(path.read_text()), json.loads(self.raw))
            with self.assertRaises(FileExistsError): result.save_json(path)

    def test_cli_catalog_is_offline(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(["catalog"]), 0)
        self.assertEqual(len(json.loads(output.getvalue())), 88)

    def test_cli_retention_exports_and_missing_env_fails_without_secret(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"IG_SESSIONID":"999:SYNTHETIC-ONLY"}, clear=True):
            with patch("edits_api.cli.EditsClient", return_value=self.client):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(main(["retention", "12345", "--output", str(Path(temp)/"out")]), 0)
                self.assertIn("4 retention points", output.getvalue())
        with patch.dict(os.environ, {}, clear=True), contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(main(["retention","12345","--output","unused"]),1)
            self.assertIn("IG_SESSIONID",error.getvalue())


if __name__ == "__main__": unittest.main()
