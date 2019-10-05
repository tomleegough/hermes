# Release actions

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