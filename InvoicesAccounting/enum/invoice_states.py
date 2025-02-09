from enum import Enum

class InvoiceStates(Enum):
    DRAFT = "draft"
    ACCOUNTED = "accounted"
    PAID = "paid"
    CANCELED = "canceled"
    PENDING = "pending" 
