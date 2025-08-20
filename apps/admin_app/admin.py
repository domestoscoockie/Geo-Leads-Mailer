from django.contrib import admin
from django import forms
from django.db import models
from .models import User, SearchQuery, Company
from django.contrib.auth.hashers import make_password, identify_hasher
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
    list_display = ('location', 'query', 'get_users', 'grid_size_display', 'id')
    list_filter = ('location', 'accuracy')
    search_fields = ('query', 'location')

    def grid_size_display(self, obj):
        return f"{obj.accuracy} km (grid)"
    grid_size_display.short_description = 'Grid Size'

    def get_users(self, obj):
        return ", ".join([u.username for u in obj.user.all()])
    get_users.short_description = 'Users'

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'language', 'country',
            'results', 'credentials'
        )
        widgets = {
            'password': forms.PasswordInput(),
            'results': forms.CheckboxSelectMultiple(),
            'credentials': forms.FileInput(),
        }

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserForm
    list_display = ('username', 'email', 'language', 'country', 'results_count', 'has_credentials')
    search_fields = ('username', 'email')
    filter_horizontal = ('results',)
    
    def results_count(self, obj):
        return obj.results.count()

    def save_model(self, request, obj, form, change):
        pwd = form.cleaned_data.get('password')
        if pwd:
            try:
                identify_hasher(pwd)
            except Exception:
                obj.password = make_password(pwd)
        super().save_model(request, obj, form, change)

    def has_credentials(self, obj):
        return True if obj.credentials else False


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'email', 'phones', 'get_queries')

    def get_queries(self, obj):
        return ", ".join([q.query for q in obj.search_queries.all()])
    get_queries.short_description = 'Queries'


