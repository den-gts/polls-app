import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from polls import models

User = get_user_model()


class UserFactory(DjangoModelFactory):

    username = factory.Sequence(lambda n: f'testuser_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = 'Тестер'
    last_name = 'Тестеров'
    is_active = True
    is_staff = False

    class Meta:
        model = User
        django_get_or_create = ('username',)


class AnswerFactory(DjangoModelFactory):
    # бесить писать каждый раз locale. Каждый раз решаю какими то черноколдовскими методами.🤦 Но не сейчас не откапаю
    # в старых проектах
    text = factory.Faker('sentence', nb_words=3, locale='ru_RU')

    class Meta:
        model = models.Answer


class QuestionFactory(DjangoModelFactory):
    text = factory.Faker('sentence', nb_words=10, locale='ru_RU')
    allow_custom = False

    class Meta:
        model = models.Question

    @factory.post_generation
    def answers(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.answers.set(extracted)
        else:
            answers = AnswerFactory.create_batch(4)
            self.answers.set(answers)


class PollFactory(DjangoModelFactory):
    name = factory.Faker('sentence', nb_words=4, locale='ru_RU')
    archive = False

    class Meta:
        model = models.Poll

    @factory.post_generation
    def questions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.questions.set(extracted)
        else:
            answers = QuestionFactory.create_batch(6)
            self.questions.set(answers)
