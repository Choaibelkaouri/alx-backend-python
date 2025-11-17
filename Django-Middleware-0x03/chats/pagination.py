from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class MessagePagination(PageNumberPagination):
    """
    Paginate message lists: 20 messages per page.
    """
    page_size = 20
    page_query_param = 'page'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Custom paginated response including:
        - total count of messages (page.paginator.count)
        - next / previous links
        - current page results
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
