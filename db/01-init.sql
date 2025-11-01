USE ogloszenia_trojmiasto;

CREATE TABLE IF NOT EXISTS scraped_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    price FLOAT,
    price_per_sqr_meter FLOAT,
    rooms INT,
    floor INT,
    square_meters FLOAT,
    year VARCHAR(255),
    address VARCHAR(255),
    city VARCHAR(255),
    area VARCHAR(255),
    coastline_distance FLOAT,
    gdynia_downtown_distance FLOAT,
    gdansk_downtown_distance FLOAT,
    sopot_downtown_distance FLOAT,
    latitude DECIMAL(15, 12),
    longitude DECIMAL(15, 12),
    created_ts TIMESTAMP,
    scraped_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_latest BOOLEAN NOT NULL DEFAULT 1
  );
