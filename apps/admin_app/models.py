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
    company = models.ForeignKey(
        'Company',
        related_name='search_queries',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )


    @staticmethod
    def save_result(user: User, location: str, query: str, accuracy: float, result: dict) -> None:

        search_query, created = SearchQuery.objects.update_or_create(
            location=location,
            query=query,
            defaults={
                'accuracy': accuracy,
                'result': result,
            }
        )
        search_query.company = Company.save_results(result)
        search_query.save()
        
        user.results.add(search_query)
        user.save()

    def __str__(self):
        return f"{self.query}-{self.location}"



class Company(models.Model):
    location = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    email = models.CharField(max_length=255, blank=True)
    phones = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)

    @staticmethod
    def save_results(result: dict) -> None:
        fullquery = list(result.keys())[0]
        
        for obj in result.get(fullquery, []):
            company, created = Company.objects.update_or_create(
                name=obj.get('name', ''),
                defaults={
                    'location': fullquery.split('-')[0],
                    'industry': fullquery.split('-')[1],
                    'website': obj.get('website', ''),
                    'email': obj.get('email', ''),
                    'phones': obj.get('phones', ''),
                    'address': obj.get('address', '')
                }
            )


    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Companies"