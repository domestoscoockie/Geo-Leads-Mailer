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
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def save_result(user: User, location: str, query: str, accuracy: float, result: dict) -> 'SearchQuery':
        search_query = SearchQuery.objects.create(
            accuracy=accuracy,
            location=location,
            query=query,
            result=result
        )
        user.results.add(search_query)
        user.save()
        return search_query

    def __str__(self):
        return f"{self.query}-{self.location}"

    class Meta:
        ordering = ['-created_at']


class Company(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    emails = models.JSONField(default=list, blank=True)
    phones = models.JSONField(default=list, blank=True)
    location = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['-created_at']