from rest_framework.pagination import CursorPagination


class ImageCursorPagination(CursorPagination):
    page_size = 10
    ordering = 'created'
