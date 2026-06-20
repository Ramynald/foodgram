"""Pagination classes for the API."""

from rest_framework.pagination import PageNumberPagination


class LimitPagination(PageNumberPagination):
    """Pagination with configurable limit."""

    page_size = 6
    page_size_query_param = 'limit'
