from django.contrib.auth.models import User
from django.db import models


class Answer(models.Model):
    """ Вариант ответа """
    text = models.CharField(verbose_name='текст ответа', max_length=1024)


    def __str__(self) -> str:
        return self.text


class Question(models.Model):
    text = models.CharField(verbose_name='текст вопроса', max_length=2048)
    answers = models.ManyToManyField(
        Answer,
        verbose_name='Допустимые варианты ответов',
        through='QuestionAnswerM2m',
        related_name='answers'
    )

    def __str__(self) -> str:
        return self.text

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class UserAnswer(models.Model):
    """ Ответ пользователя """
    question = models.ForeignKey(Question, verbose_name='Вопрос', on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, verbose_name='Вариант ответа', on_delete=models.CASCADE, null=True, blank=True)


class Poll(models.Model):
    """ Шаблон опроса """
    questions = models.ManyToManyField(Question, verbose_name='Вопросы')
    answers = models.ManyToManyField(Answer, verbose_name='Варианты ответов')


class Session(models.Model):
    """ Сессия прохождения опроса """
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class QuestionAnswerM2m(models.Model):
    """ Модель для m2m связи между вопросом и вариантами ответов. Django создает ее автоматически,
    но мы задаем явно, так как нам надо вкорячить сортировку вариантов ответов для каждого вопроса. """

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['order']
        unique_together = ['question', 'answer']
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответа'

    def __str__(self):
        return self.answer.text