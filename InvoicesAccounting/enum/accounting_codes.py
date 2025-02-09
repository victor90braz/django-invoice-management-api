from enum import Enum

class AccountingCodes(Enum):
    PURCHASES = "6000"  # DEBE Compras
    VAT_SUPPORTED = "4720"  # DEBE IVA Soportado
    SUPPLIERS = "4000"  # HABER Proveedores
