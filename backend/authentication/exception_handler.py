from django.contrib.auth import logout
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    request = context.get("request")

    if response and response.status_code == 403:
        if (
            getattr(exc, "detail", "")
            == "GitHub access has been revoked. Please re-authenticate."
        ):
            logout(request)

    return response
