import json
import unittest
from unittest.mock import Mock, patch

import function_app


class FunctionAppTests(unittest.TestCase):
    @patch.object(function_app, "upload_sample_indicators")
    def test_http_trigger_returns_upload_result(self, upload: Mock) -> None:
        upload.return_value = {"status_code": 200, "errors": []}

        response = function_app.upload_sample_indicators_http(Mock())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.get_body()),
            {"status_code": 200, "errors": []},
        )

    @patch.object(function_app, "upload_sample_indicators")
    def test_http_trigger_returns_500_when_upload_fails(self, upload: Mock) -> None:
        upload.side_effect = RuntimeError("API failure")

        response = function_app.upload_sample_indicators_http(Mock())

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            json.loads(response.get_body()),
            {"error": "The indicator upload failed."},
        )

    @patch.object(function_app, "upload_sample_indicators")
    def test_timer_trigger_uploads_indicators(self, upload: Mock) -> None:
        upload.return_value = {"status_code": 200, "errors": []}
        timer = Mock(past_due=False)

        function_app.upload_sample_indicators_timer(timer)

        upload.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
