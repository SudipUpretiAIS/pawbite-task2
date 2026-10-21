-- PostgreSQL schema for PawBite. Run in an empty database.
-- No user credentials or original local data are included.
BEGIN;

CREATE TABLE IF NOT EXISTS category (
	id SERIAL NOT NULL, 
	name VARCHAR(80), 
	PRIMARY KEY (id), 
	UNIQUE (name)
)

;

CREATE TABLE IF NOT EXISTS invoice_counter (
	id SERIAL NOT NULL, 
	current_number INTEGER NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE IF NOT EXISTS "user" (
	id SERIAL NOT NULL, 
	username VARCHAR(50) NOT NULL, 
	email VARCHAR(254) NOT NULL, 
	password VARCHAR(80) NOT NULL, 
	image_file TEXT NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (email)
)

;

CREATE TABLE IF NOT EXISTS product (
	id SERIAL NOT NULL, 
	name VARCHAR(80) NOT NULL, 
	price NUMERIC(10, 2) NOT NULL, 
	description VARCHAR(1000), 
	image_file TEXT NOT NULL, 
	tag VARCHAR(100) NOT NULL, 
	category_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES category (id)
)

;

CREATE TABLE IF NOT EXISTS cart (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES "user" (id), 
	FOREIGN KEY(product_id) REFERENCES product (id)
)

;

CREATE TABLE IF NOT EXISTS "like" (
	id SERIAL NOT NULL, 
	product_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES product (id), 
	FOREIGN KEY(user_id) REFERENCES "user" (id)
)

;

CREATE TABLE IF NOT EXISTS "order" (
	id SERIAL NOT NULL, 
	quantity INTEGER NOT NULL, 
	price FLOAT NOT NULL, 
	status VARCHAR(100) NOT NULL, 
	payment_status VARCHAR(100) NOT NULL, 
	invoice VARCHAR(1000), 
	user_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES "user" (id), 
	FOREIGN KEY(product_id) REFERENCES product (id)
)

;

CREATE TABLE IF NOT EXISTS rating (
	id SERIAL NOT NULL, 
	value INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES "user" (id), 
	FOREIGN KEY(product_id) REFERENCES product (id)
)

;
INSERT INTO invoice_counter (id, current_number) VALUES (1, 0) ON CONFLICT (id) DO NOTHING;
COMMIT;
