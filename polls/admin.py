from django.contrib import admin

from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminBase

import polls.models


@admin.register(polls.models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    search_fields = ['text']
    list_display = ['text']


class AnswerInline(SortableInlineAdminMixin, admin.TabularInline):
    model = polls.models.QuestionAnswerM2m
    extra = 0
    autocomplete_fields = ['answer']
    fields = ['answer', 'order']


@admin.register(polls.models.Question)
class QuestionAdmin(SortableAdminBase, admin.ModelAdmin):
    search_fields = ['text']
    inlines = [AnswerInline]


class QuestionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = polls.models.PollQuestionM2m
    extra = 0
    autocomplete_fields = ['question']
    fields = ['question', 'order']


@admin.register(polls.models.Poll)
class PollAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = [QuestionInline]


@admin.register(polls.models.Session)
class SessionAdmin(admin.ModelAdmin):
    pass

@admin.register(polls.models.UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_session_user', 'question', 'answer']  # Указываем имя метода

    @admin.display(description='Пользователь', ordering='session__user')
    def get_session_user(self, obj):
        if obj.session and obj.session.user:
            return str(obj.session.user)
        return "—"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('session__user')