import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.test import APIClient
from polls.factories import UserFactory, PollFactory, QuestionFactory, AnswerFactory
from polls.models import Poll, UserAnswer, Question


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return UserFactory()

@pytest.fixture
def poll():
    return PollFactory()

@pytest.fixture
def polls():
    """ Чаще всего мне нужно 2 опроса. Если нужно больше, тогда уже буду создавать с помощью Factory boy фабрики прям тесте.
     Мне нравиться держать тесты в чистоте - все подготовки в фикстурах и не очень нравятся фикстуры-фабрики(пока что...)
     Как создавать n-ое количество тестовых объектов именно в фикстуре пока не придумал. Можно параметризированную фикстуру,
     но это сильно сложней. Поэтому пока вот так.
     """
    return PollFactory.create_batch(2)

def test_health_check(api_client):
    response = api_client.get(reverse('health_check'))

    assert response.status_code == status.HTTP_200_OK

class TestAnswerView:

    @staticmethod
    def test_answer_submit(api_client, user, polls: list[Poll]):
        api_client.force_authenticate(user)

        question = polls[0].questions.first()
        answer = question.answers.first().pk
        response = api_client.post(
            reverse('question-answers-list', kwargs={
                'question_pk': question.pk,
                'poll_pk': polls[0].pk
            }),
            data={'answer': answer})

        assert response.status_code == HTTP_201_CREATED, response.json()
        assert UserAnswer.objects.get(question=question, answer=answer, session__poll=polls[0])

    @staticmethod
    def test_wrong_question(api_client, user, polls: list[Poll]):
        """ Проверяем, что при указании вопроса(из poll[1]) из другого опроса(poll[0]), возвращается ошибка """
        api_client.force_authenticate(user)

        wrong_question = polls[1].questions.first()

        response = api_client.post(
            reverse('question-answers-list', kwargs={
                'question_pk': wrong_question.pk,
                'poll_pk': polls[0].pk
            }),
            data={'answer': wrong_question.answers.first().pk})


        assert response.status_code == HTTP_400_BAD_REQUEST, response.json()
        assert response.json().get('question') == ['Предоставленного вопроса нет в опросе']

    @staticmethod
    def test_wrong_answer(api_client, user, polls: list[Poll]):
        """ Проверяем, что при указании ответа, которого нет в списке возможных ответов вопроса, запрос вернет ошибку """
        api_client.force_authenticate(user)

        question = polls[0].questions.first()
        wrong_answer = polls[0].questions.last().answers.first()

        response = api_client.post(
            reverse('question-answers-list', kwargs={
                'question_pk': question.pk,
                'poll_pk': polls[0].pk
            }),
            data={'answer': wrong_answer.pk})

        assert response.status_code == HTTP_400_BAD_REQUEST, response.json()
        assert 'Ответ не соответствует допустимым вариантам ответов вопроса' in response.json()['answer'][0]

    @staticmethod
    def test_custom_answer(api_client, user, poll: Poll):
        answer_text = 'какой-то ответ'
        # А не пора ли вынести это в фикстуру?
        api_client.force_authenticate(user)

        question = poll.questions.first()
        question.allow_custom = True
        question.save()

        response = api_client.post(
            reverse('question-answers-list', kwargs={
                'question_pk': question.pk,
                'poll_pk': poll.pk
            }),
            data={'text': answer_text}
        )

        assert response.status_code == HTTP_201_CREATED, response.json()
        assert UserAnswer.objects.get(session__poll=poll, question=question, answer__text='какой-то ответ')


# А еще можно было бы подключить django-zeal
class TestNPlusOne:
    @pytest.mark.parametrize("n", [1, 5, 50])
    def test_list_polls(self, api_client, django_assert_num_queries, user, n):
        PollFactory.create_batch(n)
        api_client.force_authenticate(user)
        with django_assert_num_queries(1):
            response = api_client.get(reverse('poll-list'))
            assert response.status_code == HTTP_200_OK

    # А вдруг? Рассуждения в polls/serializers.py:8 навели на мысли
    @pytest.mark.parametrize("n", [1, 5, 50])
    def test_question_detail(self, api_client, django_assert_num_queries, user, n, poll):
        # для одного теста не хочу ближайшие 3 строки в фикстуру складывать
        answers = AnswerFactory.create_batch(n)
        question = poll.questions.first()
        question.answers.set(answers)

        api_client.force_authenticate(user)
        with django_assert_num_queries(2): # в таблицу question + таблицу answer
            response = api_client.get(reverse('poll-questions-detail', kwargs={
                'poll_pk': poll.pk,
                'pk': question.pk
            }))
            assert response.status_code == HTTP_200_OK
