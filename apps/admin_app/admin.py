from django.contrib import admin
from django import forms
from django.db import models
from .models import User, SearchQuery, Company
from django.utils.translation import gettext_lazy as _

class SearchQueryForm(forms.ModelForm):
    class Meta:
        model = SearchQuery
        fields = ['accuracy', 'location', 'query', 'companies']
        widgets = {
            'companies': forms.CheckboxSelectMultiple(),
            'query': forms.TextInput(attrs={'size': 50}),
            'location': forms.TextInput(attrs={'size': 50}),
        }

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    form = SearchQueryForm
    list_display = ('location', 'query', 'get_users', 'accuracy', 'id')
    list_filter = ('location', 'accuracy')
    search_fields = ('query', 'location')

    def get_users(self, obj):
        return ", ".join([u.username for u in obj.user.all()])
    get_users.short_description = 'Users'

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'results',]
        widgets = {
            'password': forms.PasswordInput(),
            'results': forms.CheckboxSelectMultiple(),
        }

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserForm
    list_display = ('username', 'email', 'results_count', )
    search_fields = ('username', 'email')
    filter_horizontal = ('results',)
    
    def results_count(self, obj):
        return obj.results.count()

    

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'email', 'phones', 'get_queries')

    def get_queries(self, obj):
        return ", ".join([q.query for q in obj.search_queries.all()])
    get_queries.short_description = 'Queries'


