# Release actions

## Version 1.1.1

## Version 1.1.0 (VAT MTD)

VAT MTD Sandbox Implementation

### SQL

ALTER TABLE globals
ADD COLUMN mtd_client_id TEXT;

ALTER TABLE globals
ADD COLUMN mtd_client_secrets TEXT;

ALTER TABLE globals
ADD COLUMN mtd_server_token text;

ALTER TABLE globals
ADD COLUMN mtd_prod_status TEXT;
UPDATE globals set mtd_prod_status = 'off';

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