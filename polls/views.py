from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response

import polls.models
import polls.serializers

@api_view(['GET'])
def health_check(request):
    return Response({"status": "ok"})


class PollViewSet(ReadOnlyModelViewSet):
    queryset = polls.models.Poll.objects.filter(
        Q(session__isnull=True) | ~Q(session__current_question__isnull=True),
        archive=False)
    serializer_class = polls.serializers.PollSerializer
