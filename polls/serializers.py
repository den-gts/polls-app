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
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Poll
        fields = ['id', 'name', 'question_count']

    def get_question_count(self, instance: models.Poll):
        return instance.questions.count()


class AnswerSerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=2048, required=False)

    class Meta:
        model = models.UserAnswer
        fields =['answer', 'text']
