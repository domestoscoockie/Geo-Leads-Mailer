from django.shortcuts import render, redirect
from django.http import JsonResponse

from apps.admin_app.models import SearchQuery, Company, User
from apps.app.utils import additional_user_access_to_search_query, google_search, extract_companies, save_files
from .forms import SearchForm, SendEmailForm, LoginForm, RegisterForm
from apps.config import logger
from django.views.decorators.http import require_GET
from django.contrib.auth.hashers import make_password, check_password
from functools import wraps
from .tasks import send_bulk_emails
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from pathlib import Path
from django.conf import settings
from apps.web.mail_send import SCOPES
from django.core.files.base import ContentFile

def _get_session_user(request):
    uid = request.session.get('uid')
    if uid:
        try:
            return User.objects.get(id=uid)
        except User.DoesNotExist:
            request.session.pop('uid', None)
    return None


def session_login_required_json(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not _get_session_user(request):
            return JsonResponse({'error': 'Authentication required'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


def index(request):
    user = _get_session_user(request)
    if request.method == 'POST':
        if not user:
            return JsonResponse({'error': 'Login required'}, status=401)
        form = SearchForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            query = form.cleaned_data['query']
            grid_size_km = form.cleaned_data['grid_size']
            try:
                search_query = SearchQuery.objects.get(location=city, query=query)
                additional_user_access_to_search_query(user, search_query)
                if search_query.accuracy > grid_size_km:
                    search_query = google_search(city, query, grid_size_km, user=user)
            except SearchQuery.DoesNotExist:
                search_query = google_search(city, query, grid_size_km, user=user)
            except ValueError:
                return JsonResponse({"error": "No results found"}, status=404)
            return JsonResponse(extract_companies(search_query, grid_size_km, user), status=200)
        else:
            return JsonResponse({'error': 'Invalid input', 'details': form.errors}, status=400)
    return render(request, 'app/index.html', {'current_user': user})

def send_email(request):
    user = _get_session_user(request)
    if not user:
        return redirect('login')
    locations = user.results.values_list('location', flat=True).distinct()
    queries = []
    companies = []

    if request.method == 'POST':
        form = SendEmailForm(request.POST, request.FILES)
        if form.is_valid():
            recipients = request.POST.getlist('recipients[]') or request.POST.getlist('reciver')
            subject = form.cleaned_data['subject']
            text = form.cleaned_data['text']
            delay_min = form.cleaned_data.get('delay_min') or 1
            upload_files = request.FILES.getlist('attachments')
            attachment_paths: list[str] = []
            if upload_files:
                attachment_paths = save_files(upload_files)
            delay_s = max(0, int(delay_min)) * 60
            payloads = [
                {
                    "to": r,
                    "subject": subject,
                    "text": text,
                    "attachments": attachment_paths,
                    "sender_email": user.email,
                }
                for r in recipients if r
            ]
            if payloads:
                send_bulk_emails.delay(payloads, user_id=user.id, delay_s=delay_s)
            return JsonResponse({"queued": len(payloads), "delay_min": delay_s // 60, "attachments": len(attachment_paths)})
        else:
            return JsonResponse({'error': 'Invalid input', 'details': form.errors}, status=400)

    return render(request, 'app/send_email.html', {
        'locations': locations,
        'queries': queries,
        'companies': companies
    })


@require_GET
@session_login_required_json
def get_queries_for_location(request):
    location = request.GET.get('location')
    user = _get_session_user(request)
    queries = user.results.filter(location=location).values_list('query', flat=True).distinct()
    logger.info(f"Queries for location {location}: {list(queries)}")
    return JsonResponse({'queries': list(queries)})


@require_GET
@session_login_required_json
def get_companies_for_location_query(request):
    location = request.GET.get('location')
    query = request.GET.get('query')
    user = _get_session_user(request)
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

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            language = form.cleaned_data.get('language','pl')
            country = form.cleaned_data.get('country','PL')
            credentials = form.cleaned_data.get('credentials')
            if User.objects.filter(username=username).exists():
                return render(request, 'app/register.html', {'error': 'Username already taken', 'form': form})
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                language=language,
                country=country,
                credentials=credentials
            )
            request.session['uid'] = user.id
            # Redirect user to manual OAuth start page instead of launching local server inside container
            return redirect('oauth_start')
        else:
            return render(request, 'app/register.html', {'error': 'Fix the errors below', 'form': form})
    return render(request, 'app/register.html', {'form': RegisterForm()})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(username=username)
                if check_password(password, user.password):
                    request.session['uid'] = user.id
                    return redirect('index')
                else:
                    raise User.DoesNotExist
            except User.DoesNotExist:
                return render(request, 'app/login.html', {'error': 'Invalid credentials', 'form': form})
        else:
            return render(request, 'app/login.html', {'error': 'Invalid input', 'form': form})
    return render(request, 'app/login.html', {'form': LoginForm()})


def logout(request):
    request.session.flush()
    return redirect('login')


def oauth_start(request):
    user = _get_session_user(request)
    if not user:
        return redirect('login')
    cred_path = getattr(user.credentials, 'path', None)
    if not cred_path or not Path(cred_path).is_file():
        return render(request, 'app/oauth.html', {"error": "Brak pliku credentials."})
    
    if user.token and user.token.name and Path(user.token.path).is_file():
        try:
            creds = Credentials.from_authorized_user_file(user.token.path, SCOPES)
            if creds and creds.valid and not creds.expired:
                return redirect('send_email')
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                user.token.save(user.token.name.split('/')[-1], ContentFile(creds.to_json()), save=True)
                return redirect('send_email')
        except Exception:
            pass

    flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob")
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')

    if request.method == 'POST':
        code = request.POST.get('code')
        if not code:
            return render(request, 'app/oauth.html', {"auth_url": auth_url, "error": "Podaj kod."})
        try:
            flow.fetch_token(code=code)
            creds = flow.credentials
            user.token.save(f"token_{user.id}.json", ContentFile(creds.to_json()), save=True)
            return redirect('send_email')
        except Exception as e:
            return render(request, 'app/oauth.html', {"auth_url": auth_url, "error": f"Błąd: {e}"})

    return render(request, 'app/oauth.html', {"auth_url": auth_url})

