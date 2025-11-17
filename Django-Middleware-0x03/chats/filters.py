import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    # Filter messages by:
    # - sender username
    # - creation time range
    # - conversation id
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    sender = django_filters.CharFilter(field_name='sender__username', lookup_expr='icontains')

    class Meta:
        model = Message
        fields = ['sender', 'conversation', 'created_after', 'created_before']
