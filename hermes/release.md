# Release actions

## Version 1.2.0
Sales and purchase ledgers

CREATE TABLE contacts (
    contact_id TEXT PRIMARY KEY,
    contact_name TEXT,
    contact_account_no TEXT UNIQUE,
    contact_foreign_account_no TEXT,
    contact_vat_registration TEXT,
    contact_company_no TEXT,
    contact_type TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    contact_main_contact TEXT,
    contact_web_address TEXT,
    org_id_fk TEXT
)

CREATE TABLE sales_invoices (
    sinv_id TEXT PRIMARY KEY,
    sinv_number TEXT UNIQUE,
    sinv_status TEXT,
    sinv_date TEXT,
    contact_id_fk TEXT,
    org_id_fk TEXT
)

CREATE TABLE purchase_invoices (
    pinv_id TEXT PRIMARY KEY,
    pinv_number TEXT,
    pinv_status TEXT,
    pinv_date TEXT,
    org_id_fk TEXT,
    contact_id_fk TEXT
)

CREATE TABLE invoice_lines (
    invlines_id TEXT PRIMARY KEY,
    category_id_fk TEXT,
    invlines_description TEXT,
    invlines_net REAL,
    invlines_vat REAL,
    invlines_gross REAL,
    vat_type_id_fk TEXT,
    inv_id_fk TEXT
)

## Version 1.1.1
Minor changes

ALTER TABLE organisation
ADD COLUMN org_vat_flag INTEGER; 

## Version 1.1.0 (VAT MTD)

VAT MTD Sandbox Implementation

### SQL

ALTER TABLE global_settings
ADD COLUMN mtd_client_id TEXT;

ALTER TABLE global_settings
ADD COLUMN mtd_client_secrets TEXT;

ALTER TABLE global_settings
ADD COLUMN mtd_server_token text;

ALTER TABLE global_settings
ADD COLUMN mtd_prod_status TEXT;
UPDATE global_settings set mtd_prod_status = 'off';

CREATE TABLE vat_mtd (
    user_id_fk TEXT,
    org_id_fk TEXT,
    vat_mtd_access_token TEXT,
    vat_mtd_access_token_expiry TEXT,
    vat_mtd_refresh_token TEXT,
    vat_mtd_refresh_token_expiry TEXT
);

## Version 1.0.1 (Settings)

Implemented settings and theme changer
Companies House API

### SQL

`ALTER TABLE user;`
`ADD COLUMN user_group TEXT;`

`DROP TABLE mailjet`;
`CREATE TABLE global_settings(
    mj_api_key TEXT,
    mj_api_secret TEXT,
    mj_api_from_email TEXT,
    companies_house_api_key TEXT
);`

`CREATE TABLE settings(
    settings_theme TEXT,
    user_id_fk TEXT
);`