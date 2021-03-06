import logging
import typing
import django.db

from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from .models import VisitLog
from djangoProject.settings import RECORDING_DISABLED


logger = logging.getLogger(__name__)


def save_user_visit(user_visit: VisitLog) -> None:
    try:
        user_visit.save()
    except django.db.IntegrityError:
        logger.warning("Error saving user visit (hash='%s')", user_visit.hash)


class VisitorsMiddleware:
    def __init__(self, get_response: typing.Callable) -> None:
        if RECORDING_DISABLED:
            raise MiddlewareNotUsed("UserVisit recording has been disabled")
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> typing.Optional[HttpResponse]:
        if request.user.is_anonymous:
            return self.get_response(request)

        uv = VisitLog.objects.build(request, timezone.now())
        if not VisitLog.objects.filter(hash=uv.hash).exists():
            save_user_visit(uv)

        return self.get_response(request)
