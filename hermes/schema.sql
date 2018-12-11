-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
CREATE TABLE user (
    user_id TEXT PRIMARY KEY,
    user_name TEXT UNIQUE,
    user_pass TEXT,
    user_enabled_flag INTEGER,
    user_last_org_id TEXT
    );

DROP TABLE IF EXISTS organisation;
CREATE TABLE organisation (
    org_id TEXT PRIMARY KEY,
    org_name TEXT,
    org_enabled_flag INTEGER
);

DROP TABLE IF EXISTS user_organisation;
CREATE TABLE user_organisation(
    user_id_fk TEXT,
    org_id_fk TEXT
);

DROP TABLE IF EXISTS bank;
CREATE TABLE bank (
    bank_id TEXT PRIMARY KEY,
    bank_name TEXT,
    bank_reference TEXT,
    bank_created_date DATE,
    bank_enabled_flag INTEGER,
    bank_currency_code TEXT,
    org_id_fk TEXT
);

DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    trans_id TEXT PRIMARY KEY,
    trans_post_date DATE,
    trans_created_date DATE
    trans_value REAL,
    trans_description TEXT,
    user_id_fk TEXT,
    org_id_fk TEXT,
    bank_id_fk TEXT,
    category_id_fk TEXT
);

DROP TABLE IF EXISTS categories;
CREATE TABLE categories(
    category_id TEXT PRIMARY KEY,
    category_name TEXT,
    category_enabled_flag INTEGER,
    org_id_fk TEXT,
    cat_type_id_fk TEXT
);

DROP TABLE IF EXISTS category_type;
CREATE TABLE category_type(
    cat_type_id TEXT PRIMARY KEY,
    cat_type_name TEXT
);