from rest_framework.pagination import PageNumberPagination

class MessagePagination(PageNumberPagination):
    # Paginate message lists: 20 messages per page.
    page_size = 20
    page_query_param = 'page'
    max_page_size = 100
