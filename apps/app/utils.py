from apps.admin_app.models import SearchQuery, Company, User,\
    CompanySerializer
from apps.web.web_search import LocationQuery
from apps.config import logger, config
import os
import uuid
from apps.web.email_crawler import email_crawler


def save_files(upload_files: list) -> list[str]:
    attachment_paths: list[str] = []
    base_dir = config.email_attachments_dir
    batch_dir = os.path.join(base_dir, uuid.uuid4().hex)
    os.makedirs(batch_dir, exist_ok=True)
    for f in upload_files:
        dest_path = os.path.join(batch_dir, f.name)
        with open(dest_path, 'wb') as out:
            for chunk in f.chunks():
                out.write(chunk)
        attachment_paths.append(dest_path)
    return attachment_paths


def kilometers_to_geo_minutes(km: float) -> float:
    minutes = km / 1.852
    return max(0.25, min(minutes, 60.0))


def google_search(city: str, query: str, grid_size_km: float, user: 'User') -> SearchQuery:
    step_minutes = kilometers_to_geo_minutes(grid_size_km)
    location_search = LocationQuery(location=city, language=user.language, country=user.country).set_query(query)
    rectangles = location_search.generate_rectangles(step_minutes=step_minutes)
    result = location_search.search(rectangles)

    search_query = SearchQuery.save_result(
        user=user,
        location=city,
        query=query,
        accuracy=grid_size_km,
        result=result
    )
    return search_query


def extract_companies(search_query: SearchQuery) -> dict:
    for company in search_query.companies.all():
        if not company.email:
            company.save_mail(email_crawler)
    return {
        'search_query': f"{search_query.location}-{search_query.query}",
        'company_count': search_query.companies.count(),
        'accuracy': search_query.accuracy,
        'companies': CompanySerializer(search_query.companies.all(), many=True).data
    }
