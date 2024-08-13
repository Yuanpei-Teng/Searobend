import hashlib
import os

from flask import Flask, render_template, request, jsonify
from SPARQLWrapper import SPARQLWrapper, JSON
import folium
from folium.plugins import TagFilterButton
from geopy.geocoders import Nominatim
import re
import json

app = Flask(__name__)
geolocator = Nominatim(user_agent="Searobend")

# Setup SPARQL endpoint
sparql = SPARQLWrapper("https://searobend.adaptcentre.ie/blazegraph/namespace/searobend/sparql")


def fetch_all_data(query, limit=2000):
    offset = 0
    all_results = []

    while True:
        paginated_query = f"{query} LIMIT {limit} OFFSET {offset}"
        sparql.setQuery(paginated_query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        bindings = results['results']['bindings']
        print(f"Offset: {offset}, Results: {bindings}")  # Print result for single query
        if not bindings:
            break

        all_results.extend(bindings)
        offset += limit
        print(f"Current total results: {len(all_results)}")  # Print total amount of results

    return all_results, len(all_results)


def obtain_city_query():
    query = """
    PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
    PREFIX searobend: <https://searobend.adaptcentre.ie/ontology#>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX rr: <http://www.w3.org/ns/r2rml#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT ?place ?placename ?longLat 
    WHERE {
        ?manuscript a searobend:NotionalManuscript .
    
        ?place a cidoc:E53_Place .
        ?place cidoc:P2_has_type searobend:CityTownVillage .
        ?place rdfs:label ?placename .
        ?place geo:hasGeometry ?dimension .
        ?dimension geo:asWKT ?longLat .
    
        OPTIONAL {
            ?event cidoc:P7_took_place_at ?prodPlace .
            ?prodPlace owl:sameAs ?place . 
        }
    }
    GROUP BY ?place ?placename ?longLat

    """
    # sparql.setReturnFormat(JSON)
    results, _ = fetch_all_data(query)
    cities = []
    for result in results:
        cities.append(result["placename"]["value"])

    return list(set(cities))


def obtain_country_query():
    query = """
    PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
    PREFIX searobend: <https://searobend.adaptcentre.ie/ontology#>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX rr: <http://www.w3.org/ns/r2rml#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?place ?placename ?longLat 
    WHERE {
        ?manuscript a searobend:NotionalManuscript .

        ?place a cidoc:E53_Place .
        ?place cidoc:P2_has_type searobend:Country .
        ?place rdfs:label ?placename .
        ?place geo:hasGeometry ?dimension .
        ?dimension geo:asWKT ?longLat .

        OPTIONAL {
            ?event cidoc:P7_took_place_at ?prodPlace .
            ?prodPlace owl:sameAs ?place . 
        }
    }
    GROUP BY ?place ?placename ?longLat

    """
    # sparql.setReturnFormat(JSON)
    results, _ = fetch_all_data(query)
    countries = []
    for result in results:
        countries.append(result["placename"]["value"])

    return list(set(countries))


def obtain_county_query():
    query = """
    PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
    PREFIX searobend: <https://searobend.adaptcentre.ie/ontology#>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX rr: <http://www.w3.org/ns/r2rml#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?place ?placename ?longLat 
    WHERE {
        ?manuscript a searobend:NotionalManuscript .

        ?place a cidoc:E53_Place .
        ?place cidoc:P2_has_type searobend:County .
        ?place rdfs:label ?placename .
        ?place geo:hasGeometry ?dimension .
        ?dimension geo:asWKT ?longLat .

        OPTIONAL {
            ?event cidoc:P7_took_place_at ?prodPlace .
            ?prodPlace owl:sameAs ?place . 
        }
    }
    GROUP BY ?place ?placename ?longLat

    """
    # sparql.setReturnFormat(JSON)
    results, _ = fetch_all_data(query)
    counties = []
    for result in results:
        counties.append(result["placename"]["value"])

    return list(set(counties))


def obtain_site_query():
    query = """
    PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
    PREFIX searobend: <https://searobend.adaptcentre.ie/ontology#>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX rr: <http://www.w3.org/ns/r2rml#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?place ?placename ?longLat 
    WHERE {
        ?manuscript a searobend:NotionalManuscript .

        ?place a cidoc:E53_Place .
        ?place cidoc:P2_has_type searobend:ReligiousSite .
        ?place rdfs:label ?placename .
        ?place geo:hasGeometry ?dimension .
        ?dimension geo:asWKT ?longLat .

        OPTIONAL {
            ?event cidoc:P7_took_place_at ?prodPlace .
            ?prodPlace owl:sameAs ?place . 
        }
    }
    GROUP BY ?place ?placename ?longLat

    """
    # sparql.setReturnFormat(JSON)
    results, _ = fetch_all_data(query)
    sites = []
    for result in results:
        sites.append(result["placename"]["value"])

    return list(set(sites))


cities = obtain_city_query()
countries = obtain_country_query()
counties = obtain_county_query()
sites = obtain_site_query()



# 检查 placename 是否包含城市名字
def contains_city_name(placename):
    return placename in cities


def contains_country_name(placename):
    return placename in countries


def contains_county_name(placename):
    return placename in counties


# SPARQL查询函数
def query_coordinates():
    query = """
    PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
    PREFIX searobend: <https://searobend.adaptcentre.ie/ontology#>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX rr: <http://www.w3.org/ns/r2rml#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?place ?placename ?longLat 
    WHERE {
        ?manuscript a searobend:NotionalManuscript .

        ?place a cidoc:E53_Place .
        ?place rdfs:label ?placename .
        ?place geo:hasGeometry ?dimension .
        ?dimension geo:asWKT ?longLat .
    }
    GROUP BY ?place ?placename ?longLat
    """
    results, _ = fetch_all_data(query)
    return results


# 检查坐标范围的函数
def is_valid_coordinate(lat, long):
    return -90 <= lat <= 90 and -180 <= long <= 180


def generate_color_from_string(s):
    # 使用哈希函数将字符串转换为颜色
    hash_object = hashlib.md5(s.encode())
    hash_hex = hash_object.hexdigest()
    color = f'#{hash_hex[:6]}'  # 取前6位作为颜色代码
    return color




#Creat Folium Map
def create_map():
    fmap = folium.Map(location=[51.5074, -0.1278], zoom_start=12, tiles='CartoDB positron')
    coordinates = query_coordinates()

    city_group = folium.FeatureGroup(name='City')
    country_group = folium.FeatureGroup(name='Country')
    county_group = folium.FeatureGroup(name='County')
    other_group = folium.FeatureGroup(name='Other')

    # Load JSON data
    json_files = [
        'austria.json',
        'brussels.json',
        'counties.json',
        'france.json',
        'germany.json',
        'it.json',
        'switzerland.json',
        'luxembourg.json',
        'ireland.json'
    ]
    colors = {
        'austria.json': '#FF0000',  # red
        'brussels.json': '#00FF00',  # green
        'france.json': '#FFFF00',  # yellow
        'germany.json': '#FF00FF',  # purple
        'it.json': '#00FFFF',  # Blue
        'switzerland.json': '#FFA500',  # orange
        'luxembourg.json': '#C0C0C0',
        'ireland.json': '#00FF00'
    }

    geojson_data = []
    for file in json_files:
        file_path = os.path.join(app.static_folder, 'geojson', file)
        with open(file_path) as f:
            data = json.load(f)
            if file == 'counties.json':
                # Apply generate_color_from_string function for counties.json
                folium.GeoJson(
                    data,
                    style_function=lambda feature: {
                        'fillColor': generate_color_from_string(feature['properties'].get('name', '')),
                        'color': 'blue',
                        'weight': 0.5
                    }
                ).add_to(fmap)
            else:
                # Used fixed colors for other JSON files
                folium.GeoJson(
                    data,
                    style_function=lambda feature, color=colors[file]: {
                        'fillColor': color,
                        'color': 'blue',
                        'weight': 0.5
                    }
                ).add_to(fmap)
            geojson_data.append({
                'data': data,
                'color': colors.get(file, '')
            })

    markers = []
    city_coords = {}
    county_coords = {}
    country_coords = {}
    for coord in coordinates:
        placename = coord["placename"]["value"]
        longLat = coord["longLat"]["value"]
        place = coord["place"]["value"]
        print(placename)
        # Extract long and lat
        match = re.search(r'POINT \(([^ ]+) ([^ ]+)\)', longLat)
        if match:
            long = float(match.group(1))
            lat = float(match.group(2))
            if is_valid_coordinate(lat, long):
                if contains_city_name(placename):
                    category = 'City/Towns'
                elif contains_county_name(placename):
                    category = 'County'
                elif contains_country_name(placename):
                    category = 'Country'
                else:
                    category = 'Sites'

                marker = {
                    'lat': lat,
                    'long': long,
                    'placename': placename,
                    'place': place,
                    'category': category
                }

                if contains_city_name(placename):
                    city_coords[placename] = f"{lat},{long}"
                if contains_county_name(placename):
                    county_coords[placename] = f"{lat},{long}"
                if contains_country_name(placename):
                    country_coords[placename] = f"{lat},{long}"

                if category == 'City/Towns':
                    folium.Marker(
                        location=[lat, long],
                        popup=placename,
                        tooltip=placename,
                        icon=folium.Icon(icon="info-sign", icon_size=15)
                    ).add_to(city_group)
                elif category == 'County':
                    folium.Marker(
                        location=[lat, long],
                        popup=placename,
                        tooltip=placename,
                        icon=folium.Icon(icon="info-sign", icon_size=15)
                    ).add_to(county_group)
                elif category == 'Country':
                    folium.Marker(
                        location=[lat, long],
                        popup=placename,
                        tooltip=placename,
                        icon=folium.Icon(icon="info-sign", icon_size=15)
                    ).add_to(country_group)
                else:
                    folium.Marker(
                        location=[lat, long],
                        popup=placename,
                        tooltip=placename,
                        icon=folium.Icon(icon="info-sign", icon_size=15),
                        tags=[category]
                    ).add_to(other_group)
                markers.append(marker)

                print(f"Added marker: {placename} at ({lat}, {long})")

            else:
                print(f"Invalid coordinate: {placename} at ({lat}, {long})")

    city_group.add_to(fmap)
    country_group.add_to(fmap)
    county_group.add_to(fmap)
    other_group.add_to(fmap)

    # Open layer control button as default
    script = """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                var layerControlButton = document.querySelector('.leaflet-control-layers-toggle');
                if (layerControlButton) {
                    layerControlButton.click();
                }
            });
        </script>
        """
    fmap.get_root().html.add_child(folium.Element(script))

    return fmap, markers, city_coords, county_coords, country_coords, geojson_data

'''
def query_manuscripts(placename):
    query = """
    PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
    PREFIX searobend: <https://searobend.adaptcentre.ie/ontology#>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX rr: <http://www.w3.org/ns/r2rml#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?manuscript ?kerNumber ?shelfmark ?event ?date ?beginOfTheBegin ?beginYear ?endOfTheEnd ?endYear ?place ?placename ?longLat 
    WHERE {
        ?manuscript a searobend:NotionalManuscript .

        OPTIONAL {
            ?manuscript cidoc:P1_is_identified_by ?kerNumberIdentifier .
            ?kerNumberIdentifier cidoc:P2_has_type searobend:KerNumber .
            ?kerNumberIdentifier rdfs:label ?kerNumber .
        }

        OPTIONAL {
            ?manuscript cidoc:P1_is_identified_by ?shelfmarkIdentifier .
            ?shelfmarkIdentifier cidoc:P2_has_type searobend:Shelfmark .
            ?shelfmarkIdentifier rdfs:label ?shelfmark .
        }

        ?manuscript lrmoo:R28i_was_produced_by ?event .
        ?event a lrmoo:F32_Item_Production_Event .

        OPTIONAL {
            ?event cidoc:P7_took_place_at ?prodPlace .
            ?prodPlace owl:sameAs ?place .
        }

        ?event cidoc:P4_has_time-span ?date .
        ?date cidoc:P2_has_type searobend:CommonEra .
        ?date cidoc:P82a_begin_of_the_begin ?beginOfTheBegin .
        ?date cidoc:P82b_end_of_the_end ?endOfTheEnd .

        BIND(
            IF(STRLEN(?beginOfTheBegin) = 3, ?beginOfTheBegin,
               IF(STRLEN(?beginOfTheBegin) = 4, ?beginOfTheBegin,
                  IF(STRLEN(?beginOfTheBegin) = 9, SUBSTR(?beginOfTheBegin, 1, 3),
                     IF(STRLEN(?beginOfTheBegin) = 10, SUBSTR(?beginOfTheBegin, 1, 4), "")
                  )
               )
            ) AS ?beginYear
        )

        BIND(
            IF(STRLEN(?endOfTheEnd) = 3, ?endOfTheEnd,
               IF(STRLEN(?endOfTheEnd) = 4, ?endOfTheEnd,
                  IF(STRLEN(?endOfTheEnd) = 9, SUBSTR(?endOfTheEnd, 1, 3),
                     IF(STRLEN(?endOfTheEnd) = 10, SUBSTR(?endOfTheEnd, 1, 4), "")
                  )
               )
            ) AS ?endYear
        )

        OPTIONAL {
            ?place a cidoc:E53_Place .
            ?place rdfs:label ?placename .
            ?place geo:hasGeometry ?dimension .
            ?dimension geo:asWKT ?longLat .
        }

        FILTER (str(?placename) = "%s")
    }
    """ % placename

    results = fetch_all_data(query)
    manuscripts = []
    for result in results:
        manuscripts.append({
            "manuscript": result.get("manuscript", {}).get("value", "N/A"),
            "kerNumber": result.get("kerNumber", {}).get("value", "N/A"),
            "event": result.get("event", {}).get("value", "N/A"),
            "shelfmark": result.get("shelfmark", {}).get("value", "N/A"),
            "beginYear": result.get("beginYear", {}).get("value", "N/A"),
            "endYear": result.get("endYear", {}).get("value", "N/A"),
            "placename": result.get("placename", {}).get("value", "N/A")
        })
    return manuscripts
'''
# 这是新的query
def query_manuscripts(placename):
    query = """
    PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
    PREFIX searobend: <https://searobend.adaptcentre.ie/ontology#>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX rr: <http://www.w3.org/ns/r2rml#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?manuscript ?kerNumber (SAMPLE(?shelfmark) AS ?shelfmark) ?event ?date ?beginOfTheBegin ?beginYear ?endOfTheEnd ?endYear ?prodPlace ?place ?placename ?longLat ?scribe ?handNumber
    WHERE {
        ?manuscript a searobend:NotionalManuscript .
  
        OPTIONAL {
            ?manuscript cidoc:P1_is_identified_by ?kerNumberIdentifier .
            ?kerNumberIdentifier cidoc:P2_has_type searobend:KerNumber .
            ?kerNumberIdentifier rdfs:label ?kerNumber .
        }
  
        OPTIONAL {
            ?manuscript cidoc:P1_is_identified_by ?shelfmarkIdentifier .
            ?shelfmarkIdentifier cidoc:P2_has_type searobend:Shelfmark .
            ?shelfmarkIdentifier rdfs:label ?shelfmark .
        }
  
        ?manuscript lrmoo:R28i_was_produced_by ?event .
        ?event a lrmoo:F32_Item_Production_Event .
  
        ?event cidoc:P7_took_place_at ?prodPlace .
        ?prodPlace owl:sameAs ?place .
        ?place a cidoc:E53_Place .
        ?place rdfs:label ?placename . 
        ?place geo:hasGeometry ?dimension .
        ?dimension geo:asWKT ?longLat .
  
        OPTIONAL {
            ?event cidoc:P4_has_time-span ?date .
            ?date cidoc:P2_has_type searobend:CommonEra .
            ?date cidoc:P82a_begin_of_the_begin ?beginOfTheBegin .
            ?date cidoc:P82b_end_of_the_end ?endOfTheEnd .
        }
  
        BIND(
            IF(STRLEN(?beginOfTheBegin) = 3, ?beginOfTheBegin,
                IF(STRLEN(?beginOfTheBegin) = 4, ?beginOfTheBegin,
                    IF(STRLEN(?beginOfTheBegin) = 9, SUBSTR(?beginOfTheBegin, 1, 3),
                        IF(STRLEN(?beginOfTheBegin) = 10, SUBSTR(?beginOfTheBegin, 1, 4), "")
                    )
                )
            ) AS ?beginYear
        )
  
        BIND(
            IF(STRLEN(?endOfTheEnd) = 3, ?endOfTheEnd,
               IF(STRLEN(?endOfTheEnd) = 4, ?endOfTheEnd,
                  IF(STRLEN(?endOfTheEnd) = 9, SUBSTR(?endOfTheEnd, 1, 3),
                     IF(STRLEN(?endOfTheEnd) = 10, SUBSTR(?endOfTheEnd, 1, 4), "")
                  )
               )
            ) AS ?endYear
        )
  
      OPTIONAL {
        ?event cidoc:P14_carried_out_by ?scribe .
        ?scribe cidoc:P1_is_identified_by ?handNumberUri .
        ?handNumberUri rdfs:label ?handNumber .
      }
  
        FILTER (str(?placename) = "%s")
    }
    GROUP BY ?manuscript ?kerNumber ?event ?date ?beginOfTheBegin ?beginYear ?endOfTheEnd ?endYear ?prodPlace ?place ?placename ?longLat ?scribe ?handNumber
    """ % placename

    results, total_count = fetch_all_data(query)
    manuscripts = []
    for result in results:
        manuscripts.append({
            "manuscript": result.get("manuscript", {}).get("value", "N/A"),
            "kerNumber": result.get("kerNumber", {}).get("value", "N/A"),
            "event": result.get("event", {}).get("value", "N/A"),
            "shelfmark": result.get("shelfmark", {}).get("value", "N/A"),
            "beginYear": result.get("beginYear", {}).get("value", "N/A"),
            "endYear": result.get("endYear", {}).get("value", "N/A"),
            "placename": result.get("placename", {}).get("value", "N/A")
        })
    return manuscripts,total_count


def query_provenance_manuscripts(placename):
    query = """
    PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
    PREFIX searobend: <https://searobend.adaptcentre.ie/ontology#>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX rr: <http://www.w3.org/ns/r2rml#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?manuscript ?kerNumber (SAMPLE(?shelfmark) AS ?shelfmark) ?event ?date ?beginOfTheBegin ?beginYear ?endOfTheEnd ?endYear ?provPlace ?place ?placename ?longLat
    WHERE {
      ?manuscript a searobend:NotionalManuscript .
    
      OPTIONAL {
        ?manuscript cidoc:P1_is_identified_by ?kerNumberIdentifier .
        ?kerNumberIdentifier cidoc:P2_has_type searobend:KerNumber .
        ?kerNumberIdentifier rdfs:label ?kerNumber .
      }
    
      OPTIONAL {
        ?manuscript cidoc:P1_is_identified_by ?shelfmarkIdentifier .
        ?shelfmarkIdentifier cidoc:P2_has_type searobend:Shelfmark .
        ?shelfmarkIdentifier rdfs:label ?shelfmark .
      }
    
    
      ?manuscript cidoc:P25i_was_moved_by ?event .
      ?event a cidoc:E9_Move .
    
      ?event cidoc:P26_moved_to ?provPlace .
      ?provPlace owl:sameAs ?place .
      ?place a cidoc:E53_Place .
      ?place rdfs:label ?placename .
      ?place geo:hasGeometry ?dimension .
      ?dimension geo:asWKT ?longLat .
    
    
    OPTIONAL {
      ?event cidoc:P4_has_time-span ?date .
      ?date cidoc:P2_has_type searobend:CommonEra .
      ?date cidoc:P82a_begin_of_the_begin ?beginOfTheBegin .
      ?date cidoc:P82b_end_of_the_end ?endOfTheEnd .
    }
    
    BIND(
                IF(STRLEN(?beginOfTheBegin) = 3, ?beginOfTheBegin,
                    IF(STRLEN(?beginOfTheBegin) = 4, ?beginOfTheBegin,
                        IF(STRLEN(?beginOfTheBegin) = 9, SUBSTR(?beginOfTheBegin, 1, 3),
                            IF(STRLEN(?beginOfTheBegin) = 10, SUBSTR(?beginOfTheBegin, 1, 4), "")
                        )
                    )
                ) AS ?beginYear
            )
      
    BIND(
                IF(STRLEN(?endOfTheEnd) = 3, ?endOfTheEnd,
                   IF(STRLEN(?endOfTheEnd) = 4, ?endOfTheEnd,
                      IF(STRLEN(?endOfTheEnd) = 9, SUBSTR(?endOfTheEnd, 1, 3),
                         IF(STRLEN(?endOfTheEnd) = 10, SUBSTR(?endOfTheEnd, 1, 4), "")
                      )
                   )
                ) AS ?endYear
            )
    
    FILTER (str(?placename) = "%s")
    }
    GROUP BY ?manuscript ?kerNumber ?event ?date ?beginOfTheBegin ?beginYear ?endOfTheEnd ?endYear ?provPlace ?place ?placename ?longLat
    """ % placename

    results, total_count = fetch_all_data(query)
    manuscripts = []
    for result in results:
        manuscripts.append({
            "manuscript": result.get("manuscript", {}).get("value", "N/A"),
            "kerNumber": result.get("kerNumber", {}).get("value", "N/A"),
            "event": result.get("event", {}).get("value", "N/A"),
            "shelfmark": result.get("shelfmark", {}).get("value", "N/A"),
            "beginYear": result.get("beginYear", {}).get("value", "N/A"),
            "endYear": result.get("endYear", {}).get("value", "N/A"),
            "placename": result.get("placename", {}).get("value", "N/A")
        })
    return manuscripts,total_count
'''
def query_provenance_manuscripts(placename):
    query = """
    PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
    PREFIX searobend: <https://searobend.adaptcentre.ie/ontology#>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX rr: <http://www.w3.org/ns/r2rml#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?manuscript ?kerNumber ?shelfmark ?event ?date ?beginOfTheBegin ?beginYear ?endOfTheEnd ?endYear ?place ?placename ?longLat 
    WHERE {
        ?manuscript a searobend:NotionalManuscript .

        OPTIONAL {
            ?manuscript cidoc:P1_is_identified_by ?kerNumberIdentifier .
            ?kerNumberIdentifier cidoc:P2_has_type searobend:KerNumber .
            ?kerNumberIdentifier rdfs:label ?kerNumber .
        }

        OPTIONAL {
            ?manuscript cidoc:P1_is_identified_by ?shelfmarkIdentifier .
            ?shelfmarkIdentifier cidoc:P2_has_type searobend:Shelfmark .
            ?shelfmarkIdentifier rdfs:label ?shelfmark .
        }

	    ?manuscript cidoc:P25i_was_moved_by ?event .
		?event a cidoc:E9_Move .

		OPTIONAL {
			?event cidoc:P26_moved_to ?prodPlace .
			?prodPlace owl:sameAs ?place .
		}
		
        ?event cidoc:P4_has_time-span ?date .
        ?date cidoc:P2_has_type searobend:CommonEra .
        ?date cidoc:P82a_begin_of_the_begin ?beginOfTheBegin .
        ?date cidoc:P82b_end_of_the_end ?endOfTheEnd .

        BIND(
            IF(STRLEN(?beginOfTheBegin) = 3, ?beginOfTheBegin,
               IF(STRLEN(?beginOfTheBegin) = 4, ?beginOfTheBegin,
                  IF(STRLEN(?beginOfTheBegin) = 9, SUBSTR(?beginOfTheBegin, 1, 3),
                     IF(STRLEN(?beginOfTheBegin) = 10, SUBSTR(?beginOfTheBegin, 1, 4), "")
                  )
               )
            ) AS ?beginYear
        )

        BIND(
            IF(STRLEN(?endOfTheEnd) = 3, ?endOfTheEnd,
               IF(STRLEN(?endOfTheEnd) = 4, ?endOfTheEnd,
                  IF(STRLEN(?endOfTheEnd) = 9, SUBSTR(?endOfTheEnd, 1, 3),
                     IF(STRLEN(?endOfTheEnd) = 10, SUBSTR(?endOfTheEnd, 1, 4), "")
                  )
               )
            ) AS ?endYear
        )

        OPTIONAL {
            ?place a cidoc:E53_Place .
            ?place rdfs:label ?placename .
            ?place geo:hasGeometry ?dimension .
            ?dimension geo:asWKT ?longLat .
        }

        FILTER (str(?placename) = "%s")
    }
    """ % placename

    results = fetch_all_data(query)
    manuscripts = []
    for result in results:
        manuscripts.append({
            "manuscript": result.get("manuscript", {}).get("value", "N/A"),
            "kerNumber": result.get("kerNumber", {}).get("value", "N/A"),
            "event": result.get("event", {}).get("value", "N/A"),
            "shelfmark": result.get("shelfmark", {}).get("value", "N/A"),
            "beginYear": result.get("beginYear", {}).get("value", "N/A"),
            "endYear": result.get("endYear", {}).get("value", "N/A"),
            "placename": result.get("placename", {}).get("value", "N/A")
        })
    return manuscripts

'''
def query_creation_manuscripts(placename):
    query = """
        PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
        PREFIX searobend: <https://searobend.adaptcentre.ie/ontology#>
        PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX rr: <http://www.w3.org/ns/r2rml#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?workIdentifier (SAMPLE(?work) AS ?work) (SAMPLE(?title) AS ?title) (SAMPLE(?event) AS ?event) (SAMPLE(?date) AS ?date) 
               (SAMPLE(?beginOfTheBegin) AS ?beginOfTheBegin) (SAMPLE(?beginYear) AS ?beginYear) 
               (SAMPLE(?endOfTheEnd) AS ?endOfTheEnd) (SAMPLE(?endYear) AS ?endYear) 
               (SAMPLE(?place) AS ?place) (SAMPLE(?placename) AS ?placename) (SAMPLE(?longLat) AS ?longLat)
        WHERE {
          ?work a lrmoo:Work .
          
          OPTIONAL {
            ?work cidoc:P1_is_identified_by ?workIdentifierURI .
            ?workIdentifierURI rdfs:label ?workIdentifier .
          }
          
          OPTIONAL {
            ?work cidoc:P102_has_title ?titleURI .
            ?titleURI rdfs:label ?title .
          }
        
          ?work lrmoo:16i_was_created_by ?event .
          ?event a lrmoo:F27_Work_Creation .
          
          ?event cidoc:P7_took_place_at ?creationPlace .
          ?creationPlace owl:sameAs ?place .
          ?place a cidoc:E53_Place .
          ?place rdfs:label ?placename .
          ?place geo:hasGeometry ?dimension .
          ?dimension geo:asWKT ?longLat .
          
          OPTIONAL { 
            ?event cidoc:P4_has_time-span ?date .
            ?date cidoc:P2_has_type searobend:CommonEra .
            ?date cidoc:P82a_begin_of_the_begin ?beginOfTheBegin .
            ?date cidoc:P82b_end_of_the_end ?endOfTheEnd .
          }
          
          BIND(
            IF(STRLEN(?beginOfTheBegin) = 3, ?beginOfTheBegin,
              IF(STRLEN(?beginOfTheBegin) = 4, ?beginOfTheBegin,
                IF(STRLEN(?beginOfTheBegin) = 9, SUBSTR(?beginOfTheBegin, 1, 3),
                  IF(STRLEN(?beginOfTheBegin) = 10, SUBSTR(?beginOfTheBegin, 1, 4), "")
                )
              )
            ) AS ?beginYear
          )
          
          BIND(
            IF(STRLEN(?endOfTheEnd) = 3, ?endOfTheEnd,
              IF(STRLEN(?endOfTheEnd) = 4, ?endOfTheEnd,
                IF(STRLEN(?endOfTheEnd) = 9, SUBSTR(?endOfTheEnd, 1, 3),
                  IF(STRLEN(?endOfTheEnd) = 10, SUBSTR(?endOfTheEnd, 1, 4), "")
                )
              )
            ) AS ?endYear
          )
          
          FILTER (str(?placename) = "%s")
        }
        GROUP BY ?workIdentifier
        """ % placename

    results, total_count = fetch_all_data(query)
    manuscripts = []
    for result in results:
        manuscripts.append({
            "manuscript": result.get("work", {}).get("value", "N/A"),
            "kerNumber": result.get("workIdentifier", {}).get("value", "N/A"),
            "event": result.get("event", {}).get("value", "N/A"),
            "beginYear": result.get("beginYear", {}).get("value", "N/A"),
            "endYear": result.get("endYear", {}).get("value", "N/A"),
            "placename": result.get("placename", {}).get("value", "N/A")
        })
    return manuscripts, total_count


'''
def query_manuscripts(placename):
    query = """
PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
PREFIX searobend: <https://searobend.adaptcentre.ie/ontology#>
PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX rr: <http://www.w3.org/ns/r2rml#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?manuscript ?kerNumber ?shelfmark ?date ?beginOfTheBegin ?beginYear ?endOfTheEnd ?endYear ?place ?placename ?longLat ?manuscriptCount
WHERE {
    {
        SELECT ?placename (COUNT(?manuscript) AS ?manuscriptCount)
        WHERE {
            ?manuscript a searobend:NotionalManuscript .
            ?manuscript lrmoo:R28i_was_produced_by ?event .
            ?event cidoc:P7_took_place_at ?prodPlace .
            ?prodPlace owl:sameAs ?place .
            ?place rdfs:label ?placename .
        }
        GROUP BY ?placename
    }
    
    ?manuscript a searobend:NotionalManuscript .
    OPTIONAL {
        ?manuscript cidoc:P1_is_identified_by ?kerNumberIdentifier .
        ?kerNumberIdentifier cidoc:P2_has_type searobend:KerNumber .
        ?kerNumberIdentifier rdfs:label ?kerNumber .
    }

    OPTIONAL {
        ?manuscript cidoc:P1_is_identified_by ?shelfmarkIdentifier .
        ?shelfmarkIdentifier cidoc:P2_has_type searobend:Shelfmark .
        ?shelfmarkIdentifier rdfs:label ?shelfmark .
    }

    ?manuscript lrmoo:R28i_was_produced_by ?event .
    ?event a lrmoo:F32_Item_Production_Event .

    OPTIONAL {
        ?event cidoc:P7_took_place_at ?prodPlace .
        ?prodPlace owl:sameAs ?place .
    }

    ?event cidoc:P4_has_time-span ?date .
    ?date cidoc:P2_has_type searobend:CommonEra .
    ?date cidoc:P82a_begin_of_the_begin ?beginOfTheBegin .
    ?date cidoc:P82b_end_of_the_end ?endOfTheEnd .

    BIND(
        IF(STRLEN(?beginOfTheBegin) = 3, ?beginOfTheBegin,
           IF(STRLEN(?beginOfTheBegin) = 4, ?beginOfTheBegin,
              IF(STRLEN(?beginOfTheBegin) = 9, SUBSTR(?beginOfTheBegin, 1, 3),
                 IF(STRLEN(?beginOfTheBegin) = 10, SUBSTR(?beginOfTheBegin, 1, 4), "")
              )
           )
        ) AS ?beginYear
    )

    BIND(
        IF(STRLEN(?endOfTheEnd) = 3, ?endOfTheEnd,
           IF(STRLEN(?endOfTheEnd) = 4, ?endOfTheEnd,
              IF(STRLEN(?endOfTheEnd) = 9, SUBSTR(?endOfTheEnd, 1, 3),
                 IF(STRLEN(?endOfTheEnd) = 10, SUBSTR(?endOfTheEnd, 1, 4), "")
              )
           )
        ) AS ?endYear
    )

    OPTIONAL {
        ?place a cidoc:E53_Place .
        ?place rdfs:label ?placename .
        ?place geo:hasGeometry ?dimension .
        ?dimension geo:asWKT ?longLat .
    }

    FILTER (str(?placename) = "%s")
}
    """ % placename

    results = fetch_all_data(query)
    manuscripts = []
    for result in results:
        manuscripts.append({
            "manuscript": result.get("manuscript", {}).get("value", "N/A"),
            "kerNumber": result.get("kerNumber", {}).get("value", "N/A"),
            "shelfmark": result.get("shelfmark", {}).get("value", "N/A"),
            "beginYear": result.get("beginYear", {}).get("value", "N/A"),
            "endYear": result.get("endYear", {}).get("value", "N/A"),
            "placename": result.get("placename", {}).get("value", "N/A"),
            'manuscriptCount': result.get("manuscriptCount", {}).get("value", "N/A")
        })
    return manuscripts
    '''


@app.route('/view_more', methods=['POST'])
def view_more():
    placename = request.form.get('placename')
    mapType = request.form.get('category')
    manuscripts = []
    if mapType == 'production':
        manuscripts, total_count = query_manuscripts(placename)
    elif mapType == 'creation':
        manuscripts, total_count = query_creation_manuscripts(placename)
    elif mapType == 'provenance':
        manuscripts, total_count = query_provenance_manuscripts(placename)
    return jsonify({
        'manuscripts': manuscripts,
        'total_count': total_count
    })


@app.route('/')
def index():
    # 默认年份范围，可以根据需求修改
    default_min_year = 600
    default_max_year = 1900
    fmap, markers, city_coords, county_coords, country_coords, geojson_data = create_map()
    sorted_cities = sorted(cities)
    return render_template('map8.html', map_html=fmap._repr_html_(), markers=markers, country_coords=country_coords,
                           county_coords=county_coords, city_coords=city_coords,
                           cities=sorted_cities, geojson_data=json.dumps(geojson_data),
                           min_year=default_min_year, max_year=default_max_year)

if __name__ == '__main__':
    app.run(debug=True)
