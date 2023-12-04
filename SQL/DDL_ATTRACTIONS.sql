CREATE TABLE attractions
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    description VARCHAR,
    post_code VARCHAR(10) NOT NULL,
    rating NUMERIC(4, 2)
);