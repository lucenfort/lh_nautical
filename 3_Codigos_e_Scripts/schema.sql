-- =============================================================================
-- DESAFIO LH NAUTICAL — SCHEMA DDL (PostgreSQL)
-- Gerado automaticamente por: 1_gerar_schema.py (Python 3 Puro)
-- Autor: Luciano Silva de Arruda
-- Programa: Lighthouse 2026 (Indicium AI)
-- Data de geração: 2026-08-10 12:14:30
-- Total de tabelas: 24
-- =============================================================================

-- Tabela: addresses
DROP TABLE IF EXISTS addresses CASCADE;
CREATE TABLE addresses (
    id INTEGER,
    customer_id INTEGER,
    address_type VARCHAR(50),
    postal_code VARCHAR(50),
    street VARCHAR(50),
    number INTEGER,
    complement VARCHAR(50),
    district VARCHAR(50),
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50),
    is_primary BOOLEAN
);

-- Tabela: attributes
DROP TABLE IF EXISTS attributes CASCADE;
CREATE TABLE attributes (
    id INTEGER,
    name VARCHAR(50),
    data_type VARCHAR(50)
);

-- Tabela: brands
DROP TABLE IF EXISTS brands CASCADE;
CREATE TABLE brands (
    id INTEGER,
    name VARCHAR(50),
    country VARCHAR(50),
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabela: categories
DROP TABLE IF EXISTS categories CASCADE;
CREATE TABLE categories (
    id INTEGER,
    name VARCHAR(50),
    slug VARCHAR(50),
    parent_category_id INTEGER,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabela: customers
DROP TABLE IF EXISTS customers CASCADE;
CREATE TABLE customers (
    id INTEGER,
    person_type VARCHAR(50),
    legal_name VARCHAR(50),
    trade_name VARCHAR(50),
    tax_id BIGINT,
    state_registration VARCHAR(50),
    email VARCHAR(50),
    phone VARCHAR(50),
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabela: employees
DROP TABLE IF EXISTS employees CASCADE;
CREATE TABLE employees (
    id INTEGER,
    full_name VARCHAR(50),
    cpf BIGINT,
    email VARCHAR(50),
    role VARCHAR(50),
    primary_location_id INTEGER,
    hire_date DATE,
    termination_date DATE,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabela: fiscal_invoices
DROP TABLE IF EXISTS fiscal_invoices CASCADE;
CREATE TABLE fiscal_invoices (
    id INTEGER,
    order_id INTEGER,
    nfe_number VARCHAR(50),
    nfe_access_key VARCHAR(50),
    series INTEGER,
    issued_at TIMESTAMP,
    status VARCHAR(50),
    total_amount NUMERIC,
    xml_storage_uri VARCHAR(100),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabela: goods_receipt_items
DROP TABLE IF EXISTS goods_receipt_items CASCADE;
CREATE TABLE goods_receipt_items (
    id INTEGER,
    goods_receipt_id INTEGER,
    purchase_order_item_id INTEGER,
    quantity_received NUMERIC
);

-- Tabela: goods_receipts
DROP TABLE IF EXISTS goods_receipts CASCADE;
CREATE TABLE goods_receipts (
    id INTEGER,
    purchase_order_id INTEGER,
    received_by_employee_id INTEGER,
    received_at TIMESTAMP,
    notes VARCHAR(50),
    created_at TIMESTAMP
);

-- Tabela: locations
DROP TABLE IF EXISTS locations CASCADE;
CREATE TABLE locations (
    id INTEGER,
    name VARCHAR(50),
    location_type VARCHAR(50),
    postal_code VARCHAR(50),
    street VARCHAR(50),
    number INTEGER,
    complement VARCHAR(50),
    district VARCHAR(50),
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50),
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabela: order_items
DROP TABLE IF EXISTS order_items CASCADE;
CREATE TABLE order_items (
    id INTEGER,
    order_id INTEGER,
    product_variant_id INTEGER,
    quantity INTEGER,
    unit_price NUMERIC,
    icms_rate NUMERIC,
    ipi_rate NUMERIC,
    line_total NUMERIC
);

-- Tabela: orders
DROP TABLE IF EXISTS orders CASCADE;
CREATE TABLE orders (
    id INTEGER,
    order_number VARCHAR(50),
    channel VARCHAR(50),
    customer_id INTEGER,
    salesperson_id INTEGER,
    location_id INTEGER,
    status VARCHAR(50),
    subtotal NUMERIC,
    discount_amount NUMERIC,
    total NUMERIC,
    placed_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabela: payments
DROP TABLE IF EXISTS payments CASCADE;
CREATE TABLE payments (
    id INTEGER,
    order_id INTEGER,
    method VARCHAR(50),
    installments INTEGER,
    amount NUMERIC,
    status VARCHAR(50),
    paid_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabela: product_suppliers
DROP TABLE IF EXISTS product_suppliers CASCADE;
CREATE TABLE product_suppliers (
    product_variant_id INTEGER,
    supplier_id INTEGER,
    supplier_sku VARCHAR(50),
    last_quoted_cost NUMERIC,
    lead_time_days INTEGER,
    is_preferred BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabela: product_variants
DROP TABLE IF EXISTS product_variants CASCADE;
CREATE TABLE product_variants (
    id INTEGER,
    product_id INTEGER,
    sku VARCHAR(50),
    barcode_ean BIGINT,
    sale_price NUMERIC,
    cost_price NUMERIC,
    weight_kg NUMERIC,
    icms_rate NUMERIC,
    ipi_rate NUMERIC,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabela: products
DROP TABLE IF EXISTS products CASCADE;
CREATE TABLE products (
    id INTEGER,
    name VARCHAR(50),
    description VARCHAR(50),
    brand_id INTEGER,
    category_id INTEGER,
    ncm_code INTEGER,
    unit_of_measure VARCHAR(50),
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabela: purchase_order_items
DROP TABLE IF EXISTS purchase_order_items CASCADE;
CREATE TABLE purchase_order_items (
    id INTEGER,
    purchase_order_id INTEGER,
    product_variant_id INTEGER,
    quantity_ordered INTEGER,
    unit_cost NUMERIC,
    line_total NUMERIC
);

-- Tabela: purchase_orders
DROP TABLE IF EXISTS purchase_orders CASCADE;
CREATE TABLE purchase_orders (
    id INTEGER,
    po_number VARCHAR(50),
    supplier_id INTEGER,
    buyer_id INTEGER,
    destination_location_id INTEGER,
    status VARCHAR(50),
    currency VARCHAR(50),
    subtotal NUMERIC,
    total NUMERIC,
    placed_at TIMESTAMP,
    expected_delivery_at DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabela: return_items
DROP TABLE IF EXISTS return_items CASCADE;
CREATE TABLE return_items (
    id INTEGER,
    return_id INTEGER,
    order_item_id INTEGER,
    quantity NUMERIC,
    action VARCHAR(50),
    exchange_variant_id INTEGER,
    unit_refund_amount NUMERIC
);

-- Tabela: returns
DROP TABLE IF EXISTS returns CASCADE;
CREATE TABLE returns (
    id INTEGER,
    return_number VARCHAR(50),
    order_id INTEGER,
    customer_id INTEGER,
    received_at_location_id INTEGER,
    status VARCHAR(50),
    reason VARCHAR(50),
    total_refund_amount NUMERIC,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabela: stock_levels
DROP TABLE IF EXISTS stock_levels CASCADE;
CREATE TABLE stock_levels (
    product_variant_id INTEGER,
    location_id INTEGER,
    quantity_on_hand NUMERIC,
    reorder_point VARCHAR(50),
    updated_at TIMESTAMP
);

-- Tabela: stock_movements
DROP TABLE IF EXISTS stock_movements CASCADE;
CREATE TABLE stock_movements (
    id INTEGER,
    product_variant_id INTEGER,
    location_id INTEGER,
    movement_type VARCHAR(50),
    quantity NUMERIC,
    reference_table VARCHAR(50),
    reference_id VARCHAR(50),
    employee_id VARCHAR(50),
    notes VARCHAR(50),
    occurred_at TIMESTAMP,
    created_at TIMESTAMP
);

-- Tabela: suppliers
DROP TABLE IF EXISTS suppliers CASCADE;
CREATE TABLE suppliers (
    id INTEGER,
    legal_name VARCHAR(50),
    trade_name VARCHAR(50),
    country VARCHAR(50),
    tax_id VARCHAR(50),
    tax_id_type VARCHAR(50),
    email VARCHAR(50),
    phone BIGINT,
    contact_name VARCHAR(50),
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabela: variant_attribute_values
DROP TABLE IF EXISTS variant_attribute_values CASCADE;
CREATE TABLE variant_attribute_values (
    product_variant_id INTEGER,
    attribute_id INTEGER,
    value VARCHAR(50)
);
