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
    inlines = [AnswerInline]


@admin.register(polls.models.Poll)
class PollAdmin(admin.ModelAdmin):
    pass