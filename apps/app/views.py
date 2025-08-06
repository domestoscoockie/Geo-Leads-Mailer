from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from apps.admin_app.models import SearchQuery, Company
from apps.web.web_search import LocationQuery

def index(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        query = request.POST.get('query')
        obj = SearchQuery.objects.get(location=city, query=query) 
        if not obj:
            location_search = LocationQuery(location=city, language="pl", country="PL").set_query(query)
            rectangles = location_search.generate_rectangles(step_minutes=10.0)
            result = location_search.search(rectangles)
            
            SearchQuery.save_result(
                user=request.user,
                location=city,
                query=query,
                accuracy=result.get('accuracy', 0.0),
                result=result
            )
            companies = Company.save_results(result)
        print(' ')
        return JsonResponse(result)

    return render(request, 'app/index.html')

def querie(request, location, query):
    return HttpResponse(f"This is the querie page for location: {SearchQuery.objects.filter(location=location, query=query).first()}")
