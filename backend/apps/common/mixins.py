"""View mixins: auto-wrap successful responses in the success envelope."""

from rest_framework.response import Response


class SuccessResponseMixin:
    """Wrap 2xx viewset responses as {"success": True, "message": ..., "data": ...}.

    Put first in bases so finalize_response chains correctly. 204s and already
    enveloped payloads pass through untouched. Override per action via
    `success_messages = {"create": "..."}` or a single `success_message`.
    """

    success_message = "Operation successful."
    success_messages: dict = {}
    action_messages = {
        "list": "List retrieved successfully.",
        "retrieve": "Retrieved successfully.",
        "create": "Created successfully.",
        "update": "Updated successfully.",
        "partial_update": "Updated successfully.",
    }

    def get_success_message(self) -> str:
        action = getattr(self, "action", None)
        if action in self.success_messages:
            return self.success_messages[action]
        return self.action_messages.get(action, self.success_message)

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        data = getattr(response, "data", None)
        status_code = getattr(response, "status_code", 200)
        if (
            isinstance(response, Response)
            and data is not None
            and status_code != 204
            and 200 <= status_code < 300
            and not (isinstance(data, dict) and "success" in data)
        ):
            response.data = {
                "success": True,
                "message": self.get_success_message(),
                "data": data,
            }
        return response
