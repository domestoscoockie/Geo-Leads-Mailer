from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from apps.admin_app.models import SearchQuery, Company, User
from apps.web.web_search import LocationQuery
from apps.app.utils import google_search, extract_companies
from apps.config import logger
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .tasks import send_bulk_emails

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
    queries = []
    companies = []

    if request.method == 'POST':
        location = request.POST.get('location')
        query = request.POST.get('query')
        if location and query:
            recipients = request.POST.getlist('recipients[]') or request.POST.getlist('reciver')
            subject = request.POST.get('subject', '')
            text = request.POST.get('text', '')
            # Accept minutes from UI and convert to seconds; fallback to delay_s for backward compatibility
            delay_min = request.POST.get('delay_min')
            if delay_min is not None and delay_min != '':
                delay_s = max(0, int(delay_min)) * 60
            else:
                delay_s = int(request.POST.get('delay_s', '60'))
            payloads = [{"to": r, "subject": subject, "text": text} for r in recipients if r]
            send_bulk_emails.delay(payloads, delay_s=delay_s)
            return JsonResponse({"queued": len(payloads), "delay_min": delay_s // 60})

    return render(request, 'app/send_email.html', {
        'locations': locations,
        'queries': queries,
        'companies': companies
    })


@require_GET
@login_required
def get_queries_for_location(request):
    location = request.GET.get('location')
    user = User.objects.get(username='user')
    queries = user.results.filter(location=location).values_list('query', flat=True).distinct()
    logger.info(f"Queries for location {location}: {list(queries)}")
    return JsonResponse({'queries': list(queries)})


@require_GET
@login_required
def get_companies_for_location_query(request):
    location = request.GET.get('location')
    query = request.GET.get('query')
    user = User.objects.get(username='user')
    search_queries = user.results.filter(location=location, query=query)
    companies = (
        Company.objects
        .filter(search_queries__in=search_queries)
        .exclude(email__isnull=True)
        .exclude(email__in=['', '[]',])
        .distinct()
    )
    companies_data = [
        {'id': c.id, 'name': c.name, 'email': c.email} for c in companies
    ]
    return JsonResponse({'companies': companies_data})

