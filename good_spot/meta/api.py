from rest_framework import views, parsers, renderers, response
from constance import config


class AndroidVersion(views.APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def get(self, request, *args, **kwargs):
        return response.Response({'version': config.ANDROID_CURRENT_VERSION})


class IOSVersion(views.APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def get(self, request, *args, **kwargs):
        return response.Response({'version': config.IOS_CURRENT_VERSION})
