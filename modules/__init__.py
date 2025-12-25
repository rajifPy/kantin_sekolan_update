"""
Package modules untuk Aplikasi Kantin Sekolah
Berisi fungsi-fungsi CRUD, Barcode, Chart, dan Utilities
"""

__version__ = "1.0.0"
__author__ = "Tim Proyek Kantin Sekolah"

# Import fungsi utama untuk memudahkan akses
from .data_handler import (
    load_products_data,
    save_products_data,
    load_transactions_data,
    save_transactions_data,
    add_product,
    update_product,
    delete_product,
    get_product_by_barcode,
    search_product,
    reduce_stock,
    add_stock
)

from .barcode_handler import (
    generate_barcode,
    scan_barcode_from_camera,
    scan_barcode_from_image,
    validate_barcode_format
)

from .chart_handler import (
    create_stock_chart,
    create_sales_chart,
    create_profit_chart,
    calculate_statistics
)

from .utils import (
    validate_number,
    validate_not_empty,
    format_currency,
    create_backup,
    export_to_excel
)

__all__ = [
    # Data Handler
    'load_products_data',
    'save_products_data',
    'load_transactions_data',
    'save_transactions_data',
    'add_product',
    'update_product',
    'delete_product',
    'get_product_by_barcode',
    'search_product',
    'reduce_stock',
    'add_stock',
    
    # Barcode Handler
    'generate_barcode',
    'scan_barcode_from_camera',
    'scan_barcode_from_image',
    'validate_barcode_format',
    
    # Chart Handler
    'create_stock_chart',
    'create_sales_chart',
    'create_profit_chart',
    'calculate_statistics',
    
    # Utils
    'validate_number',
    'validate_not_empty',
    'format_currency',
    'create_backup',
    'export_to_excel'
]