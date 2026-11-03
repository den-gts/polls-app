from typing import Any

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser, User
from django.db.models import Q
from django.shortcuts import redirect
from rest_framework import mixins
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
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
    serializer_class = polls.serializers.PollListSerializer

    def retrieve(self, request, *args, **kwargs):
        poll = self.get_object()
        session = poll.session_set.first()
        if not session:
            session = polls.models.Session.objects.create(poll=poll, user=request.user)
        current_question = session.current_question
        return redirect('poll-questions-detail', pk=current_question.pk, poll_pk=poll.pk)


class QuestionViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = polls.models.Question.objects.all()
    serializer_class = polls.serializers.QuestionSerializer


class AnswerViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = polls.models.UserAnswer.objects.all()
    serializer_class = polls.serializers.AnswerSerializer

    def perform_create(
            self,
            serializer: BaseSerializer,
            session: polls.models.Session,
            question_pk: int,
    ) -> None:

        text = serializer.validated_data.get('text')
        question = polls.models.Question.objects.get(pk=question_pk)

        if text and question.allow_custom:
            answer = polls.models.Answer.objects.create(text=text)
        else:
            answer = serializer.validated_data['answer']

        polls.models.UserAnswer.objects.create(
            answer=answer,
            question=question,
            session=session
        )

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(username=request.headers.get('X-Username')).first() or AnonymousUser()
        session = polls.models.Session.objects.get(poll__pk=kwargs['poll_pk'], user=user)
        self.perform_create(
            serializer,
            question_pk=kwargs['question_pk'],
            session=session
        )
        session.current_question = session.next_question
        session.save()
        return Response(status=HTTP_201_CREATED)
