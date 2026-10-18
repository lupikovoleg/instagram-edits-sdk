"""Synthetic unit/integration tests. These do not call Instagram."""
import base64
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import io
from urllib.parse import parse_qs

from edits_api import _wire as fr


def body(points=None, owner="123", pk="42"):
    return {"data": {"xig_fetch_media": {
        "id": pk, "user": {"pk": owner}, "basel_media_level_insights": {
            "reels_retentions": points if points is not None else [
                {"index": 0, "value": 1}, {"index": 1, "value": 0.65},
                {"index": 2, "value": 0}, {"index": 3, "value": None}]}}}}


class RetentionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.session = self.root / "session.json"
        self.session_data = {"authorization_data": {"ds_user_id": "123", "sessionid": "123:FAKE-TEST-ONLY"},
                             "user_agent": "Instagram UnitTest Android", "app_id": "954255173121948"}
        self.save_session()

    def tearDown(self):
        self.temp.cleanup()

    def save_session(self):
        self.session.write_text(json.dumps(self.session_data))

    def test_shortcode_and_id(self):
        self.assertEqual(fr.media_id("https://www.instagram.com/reel/Bq/?igsh=test"), "106")
        self.assertEqual(fr.media_id("42_123"), "42")
        self.assertEqual(fr.media_id("42"), "42")

    def test_reject_non_instagram_or_non_https(self):
        for url in ("https://www.instagram.com.evil/reel/Bq", "http://instagram.com/reel/Bq",
                    "https://instagram.com@evil/reel/Bq", "https://instagram.com:443/reel/Bq"):
            with self.subTest(url=url), self.assertRaises(fr.RetentionError):
                fr.media_id(url)

    def test_wire_contract(self):
        headers = fr.session_headers(self.session)
        request = fr.make_request("42", headers)
        form = parse_qs(request.data.decode())
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.full_url, "https://i.instagram.com/graphql_www")
        self.assertEqual(form["client_doc_id"], ["3261342854360971614358769315"])
        self.assertEqual(form["fb_api_req_friendly_name"], ["BaselReelDetailsQuery"])
        self.assertEqual(json.loads(form["variables"][0]), {"media_id": "42", "include_creative_tools": False})
        encoded = headers["authorization"].split(":", 2)[2]
        self.assertEqual(json.loads(base64.b64decode(encoded)), self.session_data["authorization_data"])

    def test_cookie_encoded_session(self):
        self.session_data.pop("authorization_data")
        self.session_data["cookies"] = {"sessionid": "123%3AFAKE-TEST-ONLY"}
        self.save_session()
        self.assertEqual(fr.session_headers(self.session)["ig-intended-user-id"], "123")

    def test_instagrapi_settings(self):
        self.session_data.pop("app_id")
        self.session_data["device_settings"] = {"model": "test"}
        self.save_session()
        self.assertEqual(fr.session_headers(self.session)["x-ig-app-id"], "567067343352427")

    def test_missing_auth_stops_before_network(self):
        self.session_data.pop("authorization_data")
        self.save_session()
        called = []
        with self.assertRaises(fr.RetentionError):
            fr.fetch_retention("42", self.session, self.root / "out", transport=lambda *args: called.append(args))
        self.assertEqual(called, [])
        self.assertFalse((self.root / "out").exists())

    def test_bad_header_and_inconsistent_owner(self):
        for headers in ({"X-Test": "x\r\nAuthorization: leak"}, {"IG-INTENDED-USER-ID": "987"}):
            self.session_data["headers"] = headers
            self.save_session()
            with self.assertRaises(fr.RetentionError):
                fr.session_headers(self.session)

    def test_success_exports_private_no_credentials(self):
        raw = json.dumps(body()).encode()
        result = fr.fetch_retention("42", self.session, self.root / "out",
                                    transport=lambda req, timeout: (200, raw, "application/json"))
        self.assertTrue(result["success"])
        self.assertTrue(result["owner_verified"])
        self.assertFalse(result["live_attempted"])
        self.assertEqual(result["point_count"], 4)
        with (self.root / "out/retention.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(rows[2]["value"], "0")
        self.assertEqual(rows[3]["value"], "")
        for path in (self.root / "out").iterdir():
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertNotIn("FAKE-TEST-ONLY", path.read_text())
        self.assertIn("<svg", (self.root / "out/retention.svg").read_text())

    def test_http200_graphql_error_fails_and_saves_evidence(self):
        raw = json.dumps({"errors": [{"message": "Unit test"}]}).encode()
        with self.assertRaises(fr.RetentionError):
            fr.fetch_retention("42", self.session, self.root / "fail",
                               transport=lambda *args: (200, raw, "application/json"))
        result = json.loads((self.root / "fail/manifest.json").read_text())
        self.assertFalse(result["success"])
        self.assertEqual((self.root / "fail/response.body").read_bytes(), raw)
        self.assertFalse((self.root / "fail/retention.svg").exists())

    def test_non200_never_parse_as_success(self):
        with self.assertRaisesRegex(fr.RetentionError, "HTTP 429"):
            fr.fetch_retention("42", self.session, self.root / "fail",
                               transport=lambda *args: (429, json.dumps(body()).encode(), "application/json"))

    def test_no_empty_curve_or_wrong_owner(self):
        for payload in (body([]), body(owner="321"), body(pk="43"), {"data": {"xig_fetch_media": None}}):
            with self.assertRaises(fr.RetentionError):
                fr.extract_curve(payload, "42", "123")

    def test_preserve_null_zero_and_over100(self):
        points, meta = fr.extract_curve(body([{"index": 0, "value": 1.1}, {"index": 1, "value": 0},
                                              {"index": 2, "value": None}]), "42", "123")
        self.assertAlmostEqual(points[0]["percent"], 110)
        self.assertEqual(points[1]["value"], 0)
        self.assertIsNone(points[2]["value"])
        self.assertEqual(len(meta["warnings"]), 1)

    def test_reject_bad_point_types(self):
        for point in ({"index": True, "value": 1}, {"index": 0, "value": "0.5"},
                      {"index": 0, "value": float("nan")}, {"index": -1, "value": 1}):
            with self.assertRaises(fr.RetentionError):
                fr.extract_curve(body([point]), "42", "123")

    def test_ndjson_patch_and_errors(self):
        first = body([])
        first["hasNext"] = True
        patch = {"path": ["xig_fetch_media", "basel_media_level_insights", "reels_retentions"],
                 "data": [{"index": 0, "value": 1}], "hasNext": False}
        result = fr.parse_response((json.dumps(first) + "\n" + json.dumps(patch)).encode())
        points, _ = fr.extract_curve(result, "42", "123")
        self.assertEqual(points[0]["value"], 1)
        error = {"errors": [{"message": "unit test incremental failure"}]}
        with self.assertRaises(fr.RetentionError):
            fr.parse_response((json.dumps(first) + "\n" + json.dumps(error)).encode())

    def test_incremental_list_items_and_unfinished(self):
        first = body([])
        first["incremental"] = [{"path": ["data", "xig_fetch_media", "basel_media_level_insights", "reels_retentions", 0],
                                  "items": [{"index": 0, "value": 1}]}]
        result = fr.parse_response(json.dumps(first).encode())
        self.assertEqual(fr.extract_curve(result, "42", "123")[0][0]["value"], 1)
        with self.assertRaises(fr.RetentionError):
            fr.parse_response(b'{"data":{}, "hasNext":true}')

    def test_nonjson_and_server_fail(self):
        for raw in (b"<html>Login</html>", b'{"status":"fail"}', b"[]"):
            with self.assertRaises(fr.RetentionError):
                fr.parse_response(raw)

    def test_redirect_is_never_followed(self):
        self.assertIsNone(fr.NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.invalid"))

    def test_canonical_pando_fields_and_composite_owner(self):
        payload = {"data": {"1$xig_fetch_media(id:$media_id)": {
            "id": "42_123", "basel_media_level_insights": {"reels_retentions": [
                {"index": 0, "1fvalue": 1}, {"index": 1, "1fvalue": 0.5}]}}}}
        points, details = fr.extract_curve(payload, "42", "123")
        self.assertEqual(points[1]["percent"], 50)
        self.assertTrue(details["owner_verified"])
        self.assertEqual(details["owner_id_source"], "composite_media_id_suffix")
        self.assertEqual(details["wire_value_fields"], ["1fvalue"])
        with self.assertRaises(fr.RetentionError):
            fr.extract_curve(payload, "42", "456")

    def test_stdin_session(self):
        with patch('sys.stdin', io.StringIO(json.dumps(self.session_data))):
            self.assertEqual(fr.session_headers(Path('-'))['ig-intended-user-id'], '123')

    def test_complete_json_does_not_wait_for_connection_close(self):
        class StreamingResponse:
            code = 200
            headers = {"Content-Type": "text/javascript; charset=utf-8"}
            reads = 0
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read1(self, size):
                self.reads += 1
                if self.reads == 1: return json.dumps(body()).encode()
                raise TimeoutError('Connection deliberately stays open after document')
        response = StreamingResponse()
        opener = unittest.mock.Mock()
        opener.open.return_value = response
        with patch.object(fr.urllib.request, 'build_opener', return_value=opener):
            status, raw, kind = fr.send(fr.make_request('42', fr.session_headers(self.session)), 1)
        self.assertEqual(status, 200)
        self.assertEqual(response.reads, 1)
        self.assertEqual(len(fr.extract_curve(fr.parse_response(raw), '42', '123')[0]), 4)


if __name__ == "__main__":
    unittest.main()
