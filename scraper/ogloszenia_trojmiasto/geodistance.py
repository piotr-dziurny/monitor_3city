from geopy.geocoders import Nominatim
from shapely.geometry import Point
from shapely.ops import nearest_points
import geopandas as gpd
import os
import time
import json

geolocator = Nominatim(user_agent="geo_distance")
geocoding_cache = {} # store processed data for current scraping session

downtown_coordinates = {
    "Gdańsk": (54.3495703, 18.6477211),
    "Gdynia": (54.5197073, 18.5391734),
    "Sopot": (54.4415248, 18.5621955),
}


def get_location_data(address: str, retry_count: int = 3) -> dict:  # type: ignore
    # type of area to return from API json response
    CITY_AREA_MAPPINGS = {
        "sopot": "quarter",
        "gdynia": "suburb",
        "gdańsk": "suburb"
    }

    empty_loc = {
        "city": None,
        "area": None,
        "latitude": None,
        "longitude": None,
        "bbox": None,
    }

    if not address or address in geocoding_cache:
        return geocoding_cache.get(address, empty_loc)

    for attempt in range(1, retry_count + 1):
        try:
            time.sleep(1) # respoect api rate limits
            location = geolocator.geocode(
                address,
                addressdetails=True,
                country_codes="pl",
                language="pl",  # type: ignore
                viewbox=(
                    (54.2749189, 18.3579808),
                    (54.6241605, 19.0703029),
                ),  # bbox trójmiasta
                bounded=False,
            )

            if not location or not hasattr(location, "raw"):
                return empty_loc

            raw_data = location.raw  # type: ignore
            address_data = raw_data["address"]
            
            city_name = (
                address_data.get("city")
                or address_data.get("town")
                or address_data.get("village")
                or address_data.get("municipality")
                or address_data.get("hamlet")
            ).lower()

            area_value = (
                address_data.get(CITY_AREA_MAPPINGS.get(city_name))
                or address_data.get("suburb")
                or address_data.get("quarter")
                or address_data.get("borough")
                or address_data.get("city_district")
                or address_data.get("neighbourhood")
                or address_data.get("county")
            )

            loc = {
                "latitude": float(raw_data["lat"]),
                "longitude": float(raw_data["lon"]),
                "area": area_value,
                "city": city_name.capitalize(),
                "bbox": json.dumps(raw_data.get("boundingbox")),
            }

            geocoding_cache[address] = loc
            return loc
        except Exception:
            if attempt == retry_count:
                return empty_loc
            time.sleep(5)


def load_coastline():
    project_root = os.path.dirname(os.path.abspath(__file__))
    coastline_shapefile_path = os.path.join(
        project_root, "shapefiles", "PZP.POM. shp", "Akwen.shp"
    )  # polska linia brzegowa

    if not os.path.exists(coastline_shapefile_path):
        raise FileNotFoundError(
            f"Coastline shapefile not found at: {coastline_shapefile_path}"
        )

    coastline_gdf = gpd.read_file(coastline_shapefile_path).to_crs("EPSG:2180")
    coastline_geometry = coastline_gdf.dissolve()["geometry"].iloc[0]

    return coastline_geometry


def calculate_coastline_distance(point: Point, coastline_geometry) -> float:
    # point oraz linia brzegowa muszą być w EPSG:2180
    return (
        point.distance(nearest_points(point, coastline_geometry)[1]) / 1000
    )  # zwróć dystans w kilometrach


def calculate_city_distances(point: Point, city_centres_geoms: dict) -> dict:
    # punkt i city_centres_geoms muszą być w EPSG:2180
    distances = {}
    for city, city_point in city_centres_geoms.items():
        key = f"{city.lower()}_downtown_distance"
        distances[key] = (
            point.distance(city_point) / 1000
        )  # zwróć dystans w kilometrach

    return distances


def get_all_geodata(address: str, coastline_geometry) -> dict:
    loc_data = get_location_data(address)

    lat, lon = loc_data.get("latitude"), loc_data.get("longitude")
    if lat is None or lon is None:
        return {
            "coastline_distance": None,
            "gdynia_downtown_distance": None,
            "gdansk_downtown_distance": None,
            "sopot_downtown_distance": None,
            "city": None,
            "area": None,
            "latitude": None,
            "longitude": None,
            "bbox": None,
        }

    # creating point in EPSG:4326 and transforming to EPSG:2180
    point_wgs84 = Point(lon, lat)
    point_2180 = (
        gpd.GeoSeries([point_wgs84], crs="EPSG:4326").to_crs("EPSG:2180").iloc[0]
    )

    # preparing geometries of city centres
    city_centres_wgs84 = gpd.GeoSeries(
        [Point(lon, lat) for lat, lon in downtown_coordinates.values()], crs="EPSG:4326"
    )
    city_centres_2180 = city_centres_wgs84.to_crs("EPSG:2180")
    city_centres_geoms = dict(zip(downtown_coordinates.keys(), city_centres_2180))
    coastline_distance = calculate_coastline_distance(point_2180, coastline_geometry)
    city_distances = calculate_city_distances(point_2180, city_centres_geoms)

    return {
        "coastline_distance": coastline_distance,
        "gdynia_downtown_distance": city_distances["gdynia_downtown_distance"],
        "gdansk_downtown_distance": city_distances["gdańsk_downtown_distance"],
        "sopot_downtown_distance": city_distances["sopot_downtown_distance"],
        "city": loc_data["city"],
        "area": loc_data["area"],
        "latitude": lat,
        "longitude": lon,
        "bbox": loc_data["bbox"],
    }


if __name__ == "__main__":
    coastline_geometry = load_coastline()
    addresses = {
        "test": "alksdaksjhd",
        "cedry małe": "Cedry Małe Kolorowa",
        "sopot": "Sopot Górny Sopot 23 Marca 73",
        "gdynia": "Gdynia Śródmieście Świętojańska 39",
        "gdańsk": "Gdańsk Wrzeszcz Górny de Gaulle",
        "reda": "Reda Marii Konopnickiej",
    }
    for ad in addresses:
        result = get_all_geodata(addresses[ad], coastline_geometry)
        print(f"{ad}: {result}\n")
