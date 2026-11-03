from django.contrib.auth.models import User
from django.db import models


class Answer(models.Model):
    """ Вариант ответа """
    text = models.CharField(verbose_name='текст ответа', max_length=1024)
    # пока решил, что если ответа нет ни в одном вопросе, то он кастомный
    # custom = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.text

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'


class Question(models.Model):
    text = models.CharField(verbose_name='текст вопроса', max_length=2048)
    answers = models.ManyToManyField(
        Answer,
        verbose_name='Допустимые варианты ответов',
        through='QuestionAnswerM2m',
        related_name='answers'
    )
    allow_custom = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self) -> str:
        return self.text


class Session(models.Model):
    """ Сессия прохождения опроса """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    #TODO: Время завершения прохождения?
    current_question = models.ForeignKey(
        Question,
        verbose_name='Текущий вопрос',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Сессия прохождения'
        verbose_name_plural = 'Сессии прохождения'

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.current_question = self.poll.questions.first()
        super().save(*args, **kwargs)

    @property
    def next_question(self) -> Question | None:
        current_index = PollQuestionM2m.objects.get(
            poll = self.poll,
            question=self.current_question
        ).order
        next_pq = PollQuestionM2m.objects.filter(
            poll = self.poll,
            order__gt=current_index
        ).order_by('order').first()
        if not next_pq:
            return None
        return next_pq.question


class UserAnswer(models.Model):
    """ Ответ пользователя """
    # Возможно тут можно было бы избежать указания question, изменив схему моделей: прявязать к Answer ForeignKey Question
    # Но я намеренно решил привязывать именно ответы к вопросам. Так как один ответ, может соответствовать разным вопросам.
    # Например "да", "нет". Так же в этой схеме проще будет реализовать кастомные ответы пользователя
    question = models.ForeignKey(Question, verbose_name='Вопрос', on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, verbose_name='Вариант ответа', on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(Session, verbose_name='Сессия прохождения', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'Ответы пользователя'


class Poll(models.Model):
    """ Шаблон опроса """
    name = models.CharField(
        verbose_name='Название',
        max_length=255
    )
    questions = models.ManyToManyField(Question, verbose_name='Вопросы', through='PollQuestionM2m')
    archive = models.BooleanField(default=False, verbose_name='Архивный?')

    class Meta:
        verbose_name = 'Шаблон опроса'
        verbose_name_plural = 'Шаблоны опроса'

    def __str__(self) -> str:
        return self.name


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


class PollQuestionM2m(models.Model):
    """ То же самое что и у QuestionAnswerM2m """

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['order']
        unique_together = ['question', 'poll']
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self) -> str:
        return self.question.text
