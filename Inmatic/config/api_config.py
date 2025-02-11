from drf_yasg import openapi

# Swagger Schema Configuration
SWAGGER_SCHEMA_CONFIG = openapi.Info(
    title="Invoices API",
    default_version='v1',
    description="API for managing invoices",
    terms_of_service="https://www.google.com/policies/terms/",
    contact=openapi.Contact(email="victor.90braz@gmail.com"),
    license=openapi.License(name="BSD License"),
)

# Swagger Parameters
INVOICE_ID_PARAM = openapi.Parameter(
    'invoice_id', in_=openapi.IN_PATH, description="Invoice ID", type=openapi.TYPE_INTEGER
)

STATE_PARAM = openapi.Parameter(
    'state', in_=openapi.IN_QUERY, description="Filter by invoice state", type=openapi.TYPE_STRING
)

START_DATE_PARAM = openapi.Parameter(
    'start_date', in_=openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING
)

END_DATE_PARAM = openapi.Parameter(
    'end_date', in_=openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING
)