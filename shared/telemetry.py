import logging
import json
import time
import uuid
from typing import Dict, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class JSONFormatter(logging.Formatter):
    def format(self, record) -> str:
        log_obj: Dict[str, Any] = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
        }
        if hasattr(record, 'extra_data') and isinstance(record.extra_data, dict):
            log_obj.update(record.extra_data)
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def setup_telemetry_logger(service_name: str):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    mh = logging.StreamHandler()
    mh.setFormatter(JSONFormatter())
    logger.addHandler(mh)
    return logging.getLogger(service_name)

class TelemetryMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.logger = logging.getLogger(service_name)

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        request_id = str(uuid.uuid4())
        try:
            response = await call_next(request)
            duration = time.perf_counter() - start_time
            self.logger.info(
                f'Request {request.method} {request.url.path} completed',
                extra={
                    'extra_data': {
                        'http.method': request.method,
                        'http.path': request.url.path,
                        'http.status_code': response.status_code,
                        'duration_seconds': round(duration, 4),
                        'request_id': request_id,
                        'metric_type': 'http_request'
                    }
                }
            )
            return response
        except Exception as e:
            duration = time.perf_counter() - start_time
            self.logger.error(
                f'Request {request.method} {request.url.path} failed',
                exc_info=True,
                extra={
                    'extra_data': {
                        'http.method': request.method,
                        'http.path': request.url.path,
                        'http.status_code': 500,
                        'duration_seconds': round(duration, 4),
                        'request_id': request_id,
                        'metric_type': 'http_request_error'
                    }
                }
            )
            raise
