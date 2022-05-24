from ast import Pass

from django.contrib import admin

# Register your models here.
from .models import SudokuModel, CommentModel


@admin.register(SudokuModel)
class SudokuAdmin(admin.ModelAdmin):
    ordering = ('-datecreated',)
    list_display = ('name', 'datecreated', 'author')


@admin.register(CommentModel)
class CommentAdmin(admin.ModelAdmin):
    ordering = ('-datecreated',)
    list_display = ('datecreated', 'author')
