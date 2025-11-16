# Trójmiasto Real Estate Monitoring Tool
## Project overview
A comprehensive monitoring tool for real estate listings in the Trójmiasto area providing automated data collection, analysis, and visualization.

### Core components

- **Scraper**: Automated data collection from ogloszenia.trojmiasto.pl
- **Backend API**: Data access and processing layer
- **Frontend**: Interactive visualization with maps and analytics
- **Database**: Storage with role-based access control

### Project structure:

```
.
├── app
│   ├── backend
│   │   ├── database.py                         # MySQL setup
│   │   ├── Dockerfile                          # Fast API application
│   │   ├── main.py                             # API endpoints
│   │   └── requirements.txt
│   └── frontend
│       ├── app.py                              # Dash application
│       ├── assets                              # CSS files
│       │   └── style.css
│       ├── Dockerfile                          # Dash application
│       ├── main.py                             # Main program 
│       ├── map_generator.py                    # Map generation script
│       ├── map_utils.py                        # Map loading utilities
│       └── requirements.txt
├── db
│   ├── 01-init.sql                             # Table initialization script
│   ├── 02-setup-users.sh                       # User privileges setup
│   └── Dockerfile
├── docker-compose.yml
├── README.md
└── scraper
    ├── Dockerfile
    ├── main.py                                 # Main program for scraper execution 
    ├── ogloszenia_trojmiasto
    │   ├── db_helper.py                        # Database interaction utilities
    │   ├── geodistance.py                      # Module for geographical data extraction for scraped items
    │   ├── items.py                            # Scrapy item definitions
    │   ├── middlewares.py
    │   ├── pipelines.py
    │   ├── settings.py                         # Scraper configuration
    │   ├── shapefiles                          # Shapefiles needed for geodistance.py
    │   │   └── PZP.POM.shp
    │   └── spiders
    │       └── ogloszenia.py                   # Main spider
    ├── requirements.txt
    └── scrapy.cfg


```
## Setup and installation

### Prerequisites
* Docker and Docker Compose installed. Refer to [Docker docs](https://docs.docker.com/) for instructions.
* Git

### Initial setup

1. Clone the repository:
```
git clone <repo-url>
cd <project-directory>
```
2. Create log directories:

```
mkdir -p scraper/logs
mkdir -p app/frontend/logs
```

3. Configure environment:

```
# copy example env file
cp .env.example .env
# edit default passwords
nvim .env
```

required environment variables:
```
MYSQL_ROOT_PASSWORD=root_password
BACKEND_PASSWORD=backend_password
SCRAPER_PASSWORD=scraper_password
```
4. Build and start the services: 
```
docker compose up --build
```
## Security

### Network security
* internal services (backend, database) isolated from host
* frontend accessible only via localhost (127.0.0.1:8050)
* segregated internal networks for service communication

### Container security
* services (except MySQL database) run with dropped linux capabilities
* non-root users in containers
* no privileged containers

### Database security
Role-based access control:
* scraper user: SELECT, INSERT, UPDATE permissions
* backend user: SELECT permissions only
* no direct database exposure to host

## Service access

### Frontend dasbhroud (Dash UI)
* URL: http:/127.0.0.1:8050
* provides interactive, embedded map with real estate listings and data visualization 
* auto-update every 12 hours

### Backend API
By default, the API is only accessible within Docker networks. 

To enable API access and its Swagger/OpenAPI documentation (`http://127.0.0.1:8000/docs`) from the host:

* add port mapping in `docker-compose.yml`: 
```
backend:
  ports: # change `expose` to `ports`
    - "127.0.0.1:8000:8000" # makes api accessible from the host
```

### API Endpoints

* `GET /status`: checks API status
* `GET /listings`: all real estate listings
* `GET /listings/cities`: available cities
* `GET /listings/map`: data needed for `map_generator.py`
* `GET /listings/by-cities`: city-specific listings
* `GET /listings/top-expensive`: top 5 most expensive properties
* `GET /listings/top-affordable`: top 5 most affordable properties

## Component details

### Database
The tool uses MySQL database implementing Slowly Changing Dimension Type 2 (SCD2) for tracking historical data in property listings:

#### Table

```
CREATE TABLE scraped_items (
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
    bbox VARCHAR(255),
    bbox VARCHAIR(255),
    created_ts TIMESTAMP,
    scraped_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_latest BOOLEAN NOT NULL DEFAULT 1,
);
```
#### Data versioning
* Record identification: 
    * surrogate key: `id`
    * natural key: `url`
    * version tracking: `is_latest` boolean flag
    * timestamps: `created_ts` and `scraped_ts`
    * index: on `url` and `is_latest` for efficient querying
* Version logic:
    * new listings are inserted with `is_latest = 1`
    * duplicate listings (within 7 days) are skipped
    * duplicate listings with detected changes (after 7 days) 
        * existing item updated to `is_latest = 0`
        * new item inserted with `is_latest = 1`
---
### Scraper
* automated execution every 3 days
* multi-stage data processing:
  * `CleaningPipeline`: data cleaning 
  * `PricePipeline`: filling missing price data 
  * `SyntheticFeaturePipeline`: creating synthetic variables using `geodistance` module 
  * `DatabasePipeline`: storing scraped items in the database

Additional processing details:
> * SCD2 logic implemented in `db_helper` and `ogloszenia.py` 
> * fetching current URLS and ingestion timestamps before each scraping session 
> * 7-day change detection window 
> * automated version flag management 

#### Scraped fields:
* **url**: URL of the listing
* **title**: title of the listing
* **price**: price of the apartment
* **rooms**: number of rooms in the apartment
* **floor**: floor on which the apartment is located
* **year**: year the building was constructed
* **price per square meters**: price per square meter of the apartment
* **square meters**: total area of the apartment in square meters
* **address**: address of the apartment
* **city**: city/town/village in which the apartment is located

#### Additional fields: 
* **coastline_distance**: distance from the apartment to the nearest point on the coastline
* **gdynia_downtown_distance**: distance from the apartment to the downtown of Gdynia
* **gdansk_downtown_distance**: distance from the apartment to the downtown of Gdańsk
* **sopot_downtown_distance**: distance from the apartment to the downtown of Sopot
* **area**: district or county in which the apartment is located
* **latitude**: geographic latitude
* **longitude**: geographic longitude
* **bbox**: bounding box of the address


### Frontend Features
* interactive property map
* price analytics
* location-based insights
* automatic map generation every 12 hours

## Monitoring and maintenance

### Log access
```
# view service logs
docker compose logs -f [service_name]
```
Scraper and frontend logs are saved in Docker volumes. To access them simply create symbolic links to Docker volumes.

### Database maintenance
For development access:
```
# enter mysql client inside the container
docker exec -it <container_name> mysql -u root -p
```

### Service management
```
# stop services
docker compose down

# rebuild specific service
docker compose up --build <service_name>
```
### Full uninstall

```
docker compose down -v
docker compose down --rmi all
docker system prune
```

## Future improvements

* **Data enrichment**: additional data sources
* **Backups**: automated database backups
* **Visualizations**: more advanced analytics and visualizations
* **Permissions**: switch from Docker volumes to bind mounts for logging to improve accessibility while maintaining container security best practices
