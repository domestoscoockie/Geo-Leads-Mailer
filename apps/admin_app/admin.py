from django.contrib import admin
from django import forms
from django.db import models
from .models import User, SearchQuery, Company

class SearchQueryForm(forms.ModelForm):
    class Meta:
        model = SearchQuery
        fields = ['accuracy', 'location', 'query', 'result']
        widgets = {
            'result': forms.Textarea(attrs={'rows': 10, 'cols': 80}),
            'query': forms.TextInput(attrs={'size': 50}),
            'location': forms.TextInput(attrs={'size': 50}),
        }

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    form = SearchQueryForm
    list_display = ('query', 'location', 'accuracy', 'id')
    list_filter = ('location', 'accuracy')
    search_fields = ('query', 'location')
    ordering = ('-id',)

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'results']
        widgets = {
            'password': forms.PasswordInput(),
            'results': forms.CheckboxSelectMultiple(),
        }

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserForm
    list_display = ('username', 'email', 'results_count')
    search_fields = ('username', 'email')
    filter_horizontal = ('results',)
    
    def results_count(self, obj):
        return obj.results.count()
    results_count.short_description = 'Number of Queries'

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'location', 'industry', 'id')
    list_filter = ('industry', 'location')
    search_fields = ('name', 'website', 'location')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'website', 'location', 'industry')
        }),
        ('Contact Information', {
            'fields': ('emails', 'phones', 'address'),
            'classes': ('collapse',)
        }),
    )


    