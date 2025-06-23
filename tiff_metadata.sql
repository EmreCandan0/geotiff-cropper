CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS tiff_metadata (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    upload_time TIMESTAMP NOT NULL,
    epsg INTEGER,
    value TEXT,
    geom geometry(Polygon, 4326)
);