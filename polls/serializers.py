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
        fields = '__all__'



class PollSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Poll
        fields = ['name', 'question_count']

    def get_question_count(self, instance: models.Poll):
        return instance.questions.count()


class SessionSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(
        source='poll',
        slug_field='name',
        read_only=True
    )

    class Meta:
        model = models.Session
        fields = ['poll']