from apps.admin_app.models import SearchQuery, Company, User,\
    CompanySerializer
from apps.web.web_search import LocationQuery
from apps.web.mail_extract import EmailExtractor
from apps.config import logger

def google_search(city: str, query: str) -> SearchQuery:
    location_search = LocationQuery(location=city, language="pl", country="PL").set_query(query)
    rectangles = location_search.generate_rectangles(step_minutes=10.0)
    result = location_search.search(rectangles)

    search_query = SearchQuery.save_result(
        user=User.objects.get(username='user'), 
        location=city, 
        query=query, 
        accuracy=10.0, 
        result=result
        )
    return search_query


def extract_companies(search_query: SearchQuery) -> dict:
    extractor = EmailExtractor()
    
    for company in search_query.companies.all():
        if not company.email:
            company.save_mail(extractor)
    
    response_data = {
        'search_query': f"{search_query.location}-{search_query.query}",
        'company_count': search_query.companies.count(),
        'companies': CompanySerializer(search_query.companies.all(), many=True).data
    }

    return response_data