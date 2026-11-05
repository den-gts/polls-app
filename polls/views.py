from typing import Any

from django.db.models import Q
from django.shortcuts import redirect
from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.response import Response

import polls.models
import polls.serializers


@api_view(['GET'])
@permission_classes([AllowAny])
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

        # А может быть это надо было в сериализатор в validate? Ну такое...
        if text and question.allow_custom:
            answer, _ = polls.models.Answer.objects.get_or_create(text=text)
        else:
            answer = serializer.validated_data['answer']

        polls.models.UserAnswer.objects.create(
            answer=answer,
            question=question,
            session=session
        )

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # Так я не победил как скрестить request.data: queryDict и kwargs:dict по-нормальному.
        # request.data возвращает в значениях словаря списки. Не для 2ух значений не хочется их преобразовывать с помощью
        # dict comprehensions
        serializer = self.get_serializer(data=dict(
            question=kwargs['question_pk'],
            poll=kwargs['poll_pk'],
            answer=request.data.get('answer'),
            text=request.data.get('text')
        ))
        serializer.is_valid(raise_exception=True)

        poll = polls.models.Poll.objects.get(pk=kwargs['poll_pk'])
        session, _ = polls.models.Session.objects.get_or_create(poll=poll, user=request.user)
        if not session.current_question:
            return Response(
                status=HTTP_400_BAD_REQUEST, data={'message': 'Вы уже прошли этот опрос'}
            )

        self.perform_create(
            serializer,
            question_pk=kwargs['question_pk'],
            session=session
        )
        # Если по каким-то причинам пользователь переотвечает на ранее отвеченный вопрос,
        # то обновлять текущий вопрос не надо.
        if session.current_question.pk == int(kwargs['question_pk']):
            session.current_question = session.next_question
            session.save()
        return Response(status=HTTP_201_CREATED)
