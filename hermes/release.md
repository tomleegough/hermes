# Release actions

## Version 1.xxx (VAT MTD)

ALTER TABLE global settings
ADD COLUMN mtd_client_id TEXT;

ALTER TABLE global_settings
ADD COLUMN mtd_client_secrets TEXT;

ALTER TABLE global_settings
ADD COLUMN mtd_server_token text;

ALTER TABLE global_settings
ADD COLUMN mtd_prod_status TEXT;
UPDATE global_settings set mtd_prod_status = 'off';

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