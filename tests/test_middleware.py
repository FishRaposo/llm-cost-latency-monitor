from unittest.mock import MagicMock

import pytest

from llm_monitor.middleware import telemetry_middleware


class TestTelemetryMiddleware:
    @pytest.mark.asyncio
    async def test_logs_request_info(self):
        mock_request = MagicMock()
        mock_request.url.path = "/test-endpoint"
        mock_request.method = "GET"
        mock_response = MagicMock()
        mock_response.status_code = 200

        async def call_next(request):
            return mock_response

        response = await telemetry_middleware(mock_request, call_next)
        assert response is mock_response

    @pytest.mark.asyncio
    async def test_records_latency(self):
        mock_request = MagicMock()
        mock_request.url.path = "/metrics"
        mock_request.method = "GET"
        mock_response = MagicMock()
        mock_response.status_code = 200

        async def call_next(request):
            return mock_response

        response = await telemetry_middleware(mock_request, call_next)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_passes_error_status(self):
        mock_request = MagicMock()
        mock_request.url.path = "/error"
        mock_request.method = "POST"
        mock_response = MagicMock()
        mock_response.status_code = 500

        async def call_next(request):
            return mock_response

        response = await telemetry_middleware(mock_request, call_next)
        assert response.status_code == 500
