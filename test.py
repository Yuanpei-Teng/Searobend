'''
# 定义伦敦的景点
london_attractions = [
    {'name': 'Big ben', 'location': [51.5007, -0.1246]},
    {'name': 'London eye', 'location': [51.5033, -0.1195]},
    {'name': 'Tower Bridge', 'location': [51.5055, -0.0754]},
    # 可以根据需要添加更多景点
]

def query_blazegraph(city):
    sparql = SPARQLWrapper("https://searobend.adaptcentre.ie/blazegraph/namespace/searobend/sparql")
    query = """   """.format(city)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()


    places = []
    for result in results["results"]["bindings"]:
        places.append({
            'name': result["name"]["value"],
            'location': [float(result["latitude"]["value"]), float(result["longitude"]["value"])],
            'description': result.get("description", {}).get("value", "")
        })

    return places


@app.route('/',methods=['GET', 'POST'])
def index():  # put application's code here
    # 设置默认位置为伦敦
    location = [51.5074, -0.1278]
    city = "London"

    # 从Blazegraph查询地点信息
    #places = query_blazegraph()
    if request.method == 'POST':
        city = request.form.get('city', '')
        location = get_location_by_city(city)
    #places = query_blazegraph(city)
    # 创建Folium地图对象
    m = folium.Map(location=location, zoom_start=12)

    # 如果检测到的城市是伦敦或用户未输入城市（使用默认值），添加伦敦景点的标记
    #if 'London' in city.lower():
    for attraction in london_attractions:
        folium.Marker(
            location=attraction['location'],
            popup=attraction['name'],
            tooltip="click to view"
        ).add_to(m)
    # 为每个地点创建标记（Marker）和弹出窗口（Popup）
    #for place in places:
        #folium.Marker(
            #location=place['location'],
            #popup=f"<b>{place['name']}</b><br>{place['description']}",
        #).add_to(m)
    # 定义地点信息
    #places = [
        #{'name': '地点1', 'location': [40.7128, -74.0060], 'description': '这里是地点1的描述信息。'},
        #{'name': '地点2', 'location': [40.7138, -74.0010], 'description': '这里是地点2的描述信息。'},
        # 可以根据需要添加更多地点
    #]


    # 将Folium地图对象转换为HTML字符串
    map_html = m._repr_html_()

    # 渲染模板
    return render_template('map.html', map_html=map_html, city=city)

def get_location_by_city(city_name):
    """根据城市名称获取经纬度"""
    location = geolocator.geocode(city_name)
    if location:
        return [location.latitude, location.longitude]
    else:
        # 如果无法找到城市，则返回默认位置（伦敦）
        return [51.5074, -0.1278]
'''


'''
@app.route('/get_info', methods=['GET'])
def get_info():
    lat = float(request.args.get('lat'))
    lng = float(request.args.get('lng'))
    print(lat)
    print(lng)
    coordinates = query_coordinates()
    for coord in coordinates:
        longLat = coord["longLat"]["value"]
        match = re.search(r'POINT \(([^ ]+) ([^ ]+)\)', longLat)
        if match:
            long = float(match.group(1))
            lat_coord = float(match.group(2))
            if lat == lat_coord and lng == long:
                placename = coord["placename"]["value"]
                return jsonify({'placename': placename, 'lat': lat, 'lng': lng})
    return jsonify({'placename': 'Unknown', 'lat': lat, 'lng': lng})
'''

json_folder = os.path.join(app.static_folder, 'geojson')
json_files = [os.path.join(json_folder, f) for f in os.listdir(json_folder) if f.endswith('.json')]

geojson_data = []
for json_file in json_files:
    with open(json_file) as f:
        geojson_data.append(json.load(f))

# 将 JSON 数据添加到地图，只显示边界
for data in geojson_data:
    folium.GeoJson(
        data,
        style_function=lambda feature: {
            'fillColor': generate_color_from_string(feature['properties'].get('name', '')),  # 根据区域名称生成固定的颜色
            'color': 'green',  # 边界颜色
            'weight': 1,  # 边界线宽度
        }
    ).add_to(fmap)

    # 添加图例控件
    folium.LayerControl().add_to(fmap)