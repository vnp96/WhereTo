CREATE TABLE attractions
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    type VARCHAR(12) NOT NULL,
    subtype VARCHAR(20),
    description VARCHAR,
    post_code VARCHAR(10) NOT NULL,
    latitude NUMERIC(10, 6),
    longitude NUMERIC(10, 6),
    rating NUMERIC(4, 2)
);

ALTER TABLE attractions
ADD CONSTRAINT attractions_unique_name UNIQUE (name);

ALTER TABLE attractions
ADD COLUMN image_link_1 VARCHAR;

ALTER TABLE attractions
ADD COLUMN image_link_2 VARCHAR;

commit;
