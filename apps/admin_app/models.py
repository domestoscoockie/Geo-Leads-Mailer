from django.db import models
from apps.web.mail_extract import EmailExtractor
from rest_framework import serializers

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    results = models.ManyToManyField(
        'SearchQuery',
        related_name='user_queries',
        blank=True)

    def __str__(self):
        return self.username


class SearchQuery(models.Model):
    user = models.ManyToManyField(User, related_name='search_queries')
    accuracy = models.FloatField(default=0.0)
    location = models.CharField(max_length=255)
    query = models.CharField(max_length=255)
    result = models.JSONField(default=dict)
    companies = models.ManyToManyField(
        'Company',
        related_name='search_queries',
        blank=True
    )

    @staticmethod
    def save_result(user: User, location: str, query: str, accuracy: float, result: dict) -> 'SearchQuery':
        search_query, created = SearchQuery.objects.update_or_create(
            location=location,
            query=query,
            defaults={
                'accuracy': accuracy,
                'result': result
            }
        )
        if created or user not in search_query.user.all():
            search_query.user.add(user)
        
        # Save companies and add them to this search query
        Company.save_results(result, search_query)
        
        user.results.add(search_query)
        user.save()
        
        return search_query

    def __str__(self):
        return f"{self.query}-{self.location}"



class Company(models.Model):
    query = models.ManyToManyField(SearchQuery, related_name='company_queries')
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    email = models.CharField(max_length=255, blank=True)
    phones = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)

    @staticmethod
    def save_results(result: dict, search_query: 'SearchQuery') -> None:
        fullquery = list(result.keys())[0]
        places_dict = result.get(fullquery, {})
        
        for place_name, place_data in places_dict.items():
            display_name = place_data.get('displayName', {}).get('text', place_name)
            website = place_data.get('websiteUri', '')
            phone = place_data.get('nationalPhoneNumber', '')
            address = place_data.get('formattedAddress', '')
            
            company, created = Company.objects.update_or_create(
                name=display_name,
                defaults={
                    'website': website,
                    'email': '',
                    'phones': phone,
                    'address': address
                }
            )

            search_query.companies.add(company)

    def save_mail(self, extractor: EmailExtractor):
        if self.website:
            response = extractor.fetch_data(self.website)
            self.email = extractor.extract_mail(response)
            self.save()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Companies"


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'