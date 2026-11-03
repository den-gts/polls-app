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