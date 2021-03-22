from rest_framework import status
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response

from good_spot.images.models import PlaceImage
from good_spot.images.pagination import ImageCursorPagination
from good_spot.images.serializers import PlaceImageSerializer, NotifierSerializer


class PlaceImageListAPIView(ListAPIView):
    '''
    Send GET parameter 'place_id' to get images for certain place.
    '''
    queryset = PlaceImage.objects.all()
    serializer_class = PlaceImageSerializer
    pagination_class = ImageCursorPagination

    def get_queryset(self):
        queryset = PlaceImage.objects.all()
        filter_place_id = self.request.query_params.get('place_id', None)
        if filter_place_id:
            queryset = queryset.filter(place_id=filter_place_id).distinct()
        return queryset


class ImageCroppedView(GenericAPIView):
    serializer_class = NotifierSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
