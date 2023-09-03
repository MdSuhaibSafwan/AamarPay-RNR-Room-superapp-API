from rest_framework.renderers import JSONRenderer


class RNRAPIJSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context["response"].status_code
        formatted_data = {
            "success": True,
            "error": False,
            "status_code": status_code,
            "api_data": data,
            "message": data.get("status"),
        }

        if status_code > 300:
            formatted_data["error"] = True
            formatted_data["success"] = False

        return super().render(formatted_data, accepted_media_type, renderer_context)
