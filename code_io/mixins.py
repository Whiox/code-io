import logging
from django.utils.timezone import now

logger = logging.getLogger('app')

class LoggingMixin:
    def dispatch(self, request, *args, **kwargs):
        view_name = self.__class__.__name__
        ts = now().strftime('%Y-%m-%d %H:%M:%S')
        logger.debug(f"{ts} → Enter {view_name}: {request.method} {request.get_full_path()}")
        response = super().dispatch(request, *args, **kwargs)
        logger.debug(f"{ts} ← Exit  {view_name}: status={response.status_code}")
        return response
