from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.db import models
from django.contrib import admin

from .models import Program, Part, Page, Pagelet
from plumbing.forms import PlumbingField
from suit.widgets import SuitSplitDateTimeWidget


class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', )
    search_fields = ('program', )


class PartForm(forms.ModelForm):
    plumbing = PlumbingField()

    class Meta:
        model = Part


class PartAdmin(admin.ModelAdmin):
    list_display = ('title', 'program', 'start_time', 'end_time', )
    list_editable = ('start_time', 'end_time', )
    search_fields = ('title', 'program', )
    ordering = ('-start_time', )
    date_hierarchy = 'start_time'

    form = PartForm
    formfield_overrides = {
        models.DateTimeField: { 'widget': SuitSplitDateTimeWidget }
    }


class PageletInline(admin.TabularInline):
    model = Pagelet


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', )
    inlines = (PageletInline, )


admin.site.register(Program, ProgramAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(Page, PageAdmin)
