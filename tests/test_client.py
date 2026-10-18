import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs

from edits_api import EditsClient, EditsError, Session, QueryResult, get_operation, list_operations
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
        self.client.account_insights(period="LAST_7_DAYS", include_time_series=True)
        self.assertTrue(self.variables()["shouldIncludeTimeSeries"])
        self.client.audience_insights(period="LAST_7_DAYS", client_timezone="UTC")
        self.assertEqual(self.variables()["client_timezone"], "UTC")
        self.client.public_insights("42_999")
        self.assertEqual(self.variables(), {"media_id": "42"})
        self.client.reels_delta(["42_999", "43"])
        self.assertEqual(self.variables(), {"media_ids": ["42", "43"]})
        self.client.comment_insights("42", sort_order="recent")
        self.assertEqual(self.variables()["sort_order"], "recent")

    def test_statistics_survive_absent_null_and_empty_retention(self):
        for state in ('missing', 'null', 'empty', 'null_points'):
            payload = json.loads(self.raw)
            insights = payload['data']['1$xig_fetch_media(id:$media_id)']['basel_media_level_insights']
            if state == 'missing': insights.pop('reels_retentions')
            elif state == 'null': insights['reels_retentions'] = None
            elif state == 'empty': insights['reels_retentions'] = []
            else: insights['reels_retentions'] = [{'index':0,'1fvalue':None}]
            raw = json.dumps(payload).encode()
            client = EditsClient(self.session, transport=lambda request, timeout:(200,raw,'application/json'))
            result = client.reel_insights('12345')
            self.assertFalse(result.retention_available)
            self.assertEqual(result.metrics['play_count'],100)
            self.assertEqual(result.metadata['retention_status'],'unavailable')
            with self.assertRaises(EditsError): client.retention('12345')
            with tempfile.TemporaryDirectory() as temp:
                out = result.export(Path(temp)/'stats')
                self.assertTrue((out/'insights.json').exists())
                self.assertFalse((out/'retention.svg').exists())
                self.assertFalse((out/'retention.csv').exists())

    def test_no_retention_does_not_bypass_owner_checks(self):
        payload=json.loads(self.raw)
        payload['data']['1$xig_fetch_media(id:$media_id)']['basel_media_level_insights'].pop('reels_retentions')
        raw=json.dumps(payload).encode()
        client=EditsClient(Session.from_sessionid('888:synthetic'),transport=lambda r,t:(200,raw,'application/json'))
        with self.assertRaises(EditsError):client.reel_insights('12345')

    def test_malformed_retention_is_not_silently_missing(self):
        payload=json.loads(self.raw)
        payload['data']['1$xig_fetch_media(id:$media_id)']['basel_media_level_insights']['reels_retentions']='bad'
        raw=json.dumps(payload).encode()
        client=EditsClient(self.session,transport=lambda r,t:(200,raw,'application/json'))
        with self.assertRaises(EditsError):client.reel_insights('12345')

    def test_recovered_enum_validation(self):
        for call in (lambda:self.client.account_insights(period='invented'),
                     lambda:self.client.audience_insights(period='invented'),
                     lambda:self.client.comment_insights('42',sort_order='invented')):
            with self.assertRaises(EditsError):call()
        self.assertEqual(self.requests,[])

    def test_logical_path_resolves_canonical_aliases_and_null(self):
        response = self.client.execute('BaselPublicInsightsQuery', {})
        self.assertEqual(response.get_data('xig_fetch_media', 'basel_media_level_insights')['play_count'], 100)
        self.assertEqual(response.get_data('xig_fetch_media', 'basel_media_level_insights', 'skip_rate', 'value'), 0.2)
        response = QueryResult('test', {'data':{'1$insights(arg:$arg)':None,'insights(arg:$arg)':{'retention':None}}}, b'',200,'','',False)
        self.assertIsNone(response.get_data('insights','retention'))
        with self.assertRaises(EditsError): response.get_data('missing')

    def test_ambiguous_logical_path_is_rejected(self):
        response = QueryResult('test', {'data':{'1$insights(arg:$a)':1,'2$insights(arg:$b)':2}}, b'',200,'','',False)
        with self.assertRaisesRegex(EditsError,'[Aa]mbiguous'): response.get_data('insights')

    def test_ndjson_alias_fragments_merge_without_mutating_raw_response(self):
        raw={'1$insights(id:$id)':{'likes':2,'nested':{'a':1}},
             'insights(id:$id)':{'retention':[1,.8],'nested':{'b':2}}}
        response=QueryResult('test',{'data':raw},b'',200,'','',False)
        merged=response.get_data('insights')
        self.assertEqual(merged,{'likes':2,'retention':[1,.8],'nested':{'a':1,'b':2}})
        self.assertNotIn('retention',raw['1$insights(id:$id)'])
        raw['insights(id:$id)']['likes']=3
        with self.assertRaisesRegex(EditsError,'Conflicting'):response.get_data('insights')

    def test_reels_page_cursor_and_invalid_connections(self):
        connection={'edges':[{'node':{'id':'12345_999'}}], 'page_info':{'has_next_page':True,'end_cursor':'test-cursor'}}
        def client_for(conn):
            data={'data':{'1$xig_user_by_igid_v2(id:$user_id)':{'basel_insights':{'1$user_reel_dicts(after:$after)':conn}}}}
            return EditsClient(self.session,transport=lambda r,t:(200,json.dumps(data).encode(),'application/json'))
        page=client_for(connection).reels_page(first=1)
        self.assertEqual(page.items[0]['id'],'12345_999')
        self.assertEqual(page.next_cursor,'test-cursor')
        self.assertTrue(page.has_next_page)
        connection['page_info']['end_cursor']=None
        with self.assertRaisesRegex(EditsError,'without end_cursor'):client_for(connection).reels_page()
        connection['page_info']['has_next_page']=False
        connection['edges']=[]
        self.assertEqual(client_for(connection).reels_page().items,())
        connection['edges']=[{}]
        with self.assertRaisesRegex(EditsError,'edge'):client_for(connection).reels_page()

    def test_kits_and_explicit_bloks_version(self):
        self.client.kits(after='test-cursor')
        self.assertEqual(self.variables(),{'after':'test-cursor'})
        self.client.extended_reel_insights('42',bloks_versioning_id='test-version')
        self.assertEqual(self.variables(),{'mediaIgid':'42','bloksVersioningId':'test-version'})
        with self.assertRaises(EditsError):self.client.extended_reel_insights('42',bloks_versioning_id='')

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
