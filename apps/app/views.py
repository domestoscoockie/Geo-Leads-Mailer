from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from apps.admin_app.models import SearchQuery, Company, User
from apps.web.web_search import LocationQuery
from apps.app.utils import google_search, extract_companies
from apps.config import logger
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

def index(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        query = request.POST.get('query')
        try:
            search_query = SearchQuery.objects.get(location=city, query=query)
            logger.info(f"Found existing search query: {search_query.location} - {search_query.query}")
        except SearchQuery.DoesNotExist:
            try:
                search_query = google_search(city, query)
                logger.info(f"Created new search query: {search_query.location} - {search_query.query}")
            except ValueError:
                return JsonResponse({"error": "No results found"}, status=404)

        return JsonResponse(extract_companies(search_query))

    return render(request, 'app/index.html')

def send_email(request):
    user = User.objects.get(username='user')  # zakładamy, że użytkownik jest zalogowany
    locations = user.results.values_list('location', flat=True).distinct()
    queries = []  # queries i companies będą pobierane AJAXem
    companies = []
    return render(request, 'app/send_email.html', {
        'locations': locations,
        'queries': queries,
        'companies': companies
    })

# AJAX endpoint: queries dla wybranego miasta

@require_GET
@login_required
def get_queries_for_location(request):
    location = request.GET.get('location')
    user = User.objects.get(username='user')
    queries = user.results.filter(location=location).values_list('query', flat=True).distinct()
    return JsonResponse({'queries': list(queries)})

# AJAX endpoint: companies dla wybranego miasta i query
@require_GET
@login_required
def get_companies_for_location_query(request):
    location = request.GET.get('location')
    query = request.GET.get('query')
    user = User.objects.get(username='user')
    search_queries = user.results.filter(location=location, query=query)
    companies = Company.objects.filter(search_queries__in=search_queries).distinct()
    companies_data = [
        {'id': c.id, 'name': c.name, 'email': c.email} for c in companies
    ]
    return JsonResponse({'companies': companies_data})
