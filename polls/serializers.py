from rest_framework import serializers

from polls import models


class QuestionSerializer(serializers.ModelSerializer):
    available_answers = serializers.SlugRelatedField(
        many=True,
        source='answers',
        slug_field='text',
        read_only=True
    )

    class Meta:
        model = models.Question
        exclude = ['answers']


class PollListSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Poll
        fields = ['id', 'name']


class AnswerSerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=2048, required=False, allow_null=True)
    poll = serializers.PrimaryKeyRelatedField(queryset=models.Poll.objects.filter(archive=False))

    class Meta:
        model = models.UserAnswer
        fields =['answer', 'text', 'question', 'poll']


    def validate(self, attrs):
        question = attrs['question']
        answer = attrs['answer']

        if answer and not question.answers.filter(pk=answer.pk).exists():
            raise serializers.ValidationError(
                {'answer': f'Ответ не соответствует допустимым вариантам ответов вопроса "{question.text}"'}
            )
        if not attrs['poll'].questions.filter(pk=question.pk).exists():
            raise serializers.ValidationError(
                {'question': 'Предоставленного вопроса нет в опросе'}
            )

        return attrs
