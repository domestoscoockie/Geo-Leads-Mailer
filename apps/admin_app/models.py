from django.db import models

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
    accuracy = models.FloatField(default=0.0)
    location = models.CharField(max_length=255)
    query = models.CharField(max_length=255)
    result = models.JSONField()

    @staticmethod
    def save_result(user: User, location: str, query: str, accuracy: float, result: dict) -> None:
        search_query, created = SearchQuery.objects.update_or_create(
            location=location,
            query=query,
            defaults={
                'accuracy': accuracy,
                'result': result
            }
        )
        user.results.add(search_query)
        user.save()

    def __str__(self):
        return f"{self.query}-{self.location}"

    class Meta:
        ordering = ['-id']


class Company(models.Model):
    location = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    emails = models.CharField(max_length=255, blank=True)
    phones = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)

    @staticmethod
    def save_results(results: dict) -> None:
        fullquery = list(results.keys())[0]
        
        for result in results.get(fullquery, []):
            company, created = Company.objects.update_or_create(
                name=result.get('name', ''),
                defaults={
                    'location': fullquery.split('-')[0] if '-' in fullquery else fullquery,
                    'industry': fullquery.split('-')[1] if '-' in fullquery else '',
                    'website': result.get('website', ''),
                    'emails': result.get('emails', ''),
                    'phones': result.get('phones', ''),
                    'address': result.get('address', '')
                }
            )


    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['-id']