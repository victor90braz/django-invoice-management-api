from drf_yasg import openapi

OPEN_API_SCHEMA_CONFIG = openapi.Info(
    title="Invoices API",
    default_version='v1',
    description="API for managing invoices",
    terms_of_service="https://www.google.com/policies/terms/",
    contact=openapi.Contact(email="victor.90braz@gmail.com"),
    license=openapi.License(name="BSD License"),
)