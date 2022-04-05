from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.admin.options import get_content_type_for_model
from django.utils.encoding import force_str


class OperationLogs:

    @staticmethod
    def log_addition(obj):
        LogEntry.objects.log_action(
            user_id=obj.created_by,
            content_type_id=get_content_type_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=force_str(obj),
            action_flag=ADDITION,
        )

    @staticmethod
    def log_change(obj):
        LogEntry.objects.log_action(
            user_id=obj.updated_by,
            content_type_id=get_content_type_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=force_str(obj),
            action_flag=CHANGE,
        )

    @staticmethod
    def log_deletion(obj):
        LogEntry.objects.log_action(
            user_id=obj.created_by,
            content_type_id=get_content_type_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=force_str(obj),
            action_flag=DELETION,
        )
