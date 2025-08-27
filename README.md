# GeoLeads Mailer 1.0

## Project Description
GeoLeads Mailer is an application designed to automate finding lead's mails via geocoding, google maps location search api and web scraping. The project uses Django as the backend framework along with other supporting tools such as Celery, Redis and RabbitMQ.

## Project Structure
- **apps/**: Main Django applications, including configurations, models, views, and tests.
- **web/**: Modules responsible for email processing and web searching.
- **uploads/**: Directory for storing uploaded files, such as credentials.

## Requirements
- Python 3.10+
- Django
- Celery
- RabbitMQ
- Redis
- Docker (optional)

## Application Flow

Below is a simplified ASCII diagram showing the flow of the application:

```
+----------------+       +----------------+       +----------------+
|  User Input    | --->  |  Django Views  | --->  |  Celery Tasks  |
+----------------+       +----------------+       +----------------+
        |                        |                        |
        v                        v                        v
+----------------+       +----------------+       +----------------+
|  Database      | <-->  |  Redis Queue   |       |  Email Sender  |
+----------------+       +----------------+       +----------------+
```

This diagram illustrates the following steps:
1. **User Input**: Data is provided by the user through the frontend.
2. **Django Views**: The backend processes the input and triggers tasks.
3. **Celery Tasks**: Background tasks are queued and executed asynchronously.
4. **Database**: Data is stored or retrieved as needed.
5. **Redis Queue**: Tasks are managed in the queue for processing and interact with the database.
6. **Email Sender**: Emails are sent to the leads at regular intervals to ensure higher delivery reliability.


