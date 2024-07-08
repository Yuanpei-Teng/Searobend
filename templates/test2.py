import folium
from folium import IFrame
from jinja2 import Template

# 创建Folium地图对象
m = folium.Map(location=[37.7749, -122.4194], zoom_start=13)

# 添加一些带有标签的Marker
locations = [
    {"location": [37.7749, -122.4194], "popup": "San Francisco", "tags": ["city", "popular"]},
    {"location": [37.7849, -122.4094], "popup": "Downtown", "tags": ["city", "business"]},
    {"location": [37.7649, -122.4294], "popup": "Suburb", "tags": ["residential", "quiet"]},
]

for loc in locations:
    marker = folium.Marker(location=loc["location"], popup=loc["popup"])
    marker.add_to(m)
    marker.add_child(folium.Popup(IFrame(f'Tags: {", ".join(loc["tags"])}', width=200, height=50)))

# 自定义JavaScript和CSS文件的URL
tag_filter_button_js = "https://cdn.jsdelivr.net/npm/leaflet-tag-filter-button/src/leaflet-tag-filter-button.js"
tag_filter_button_css = "https://cdn.jsdelivr.net/npm/leaflet-tag-filter-button/src/leaflet-tag-filter-button.css"

# 在地图上引入TagFilterButton插件的JavaScript和CSS
template = Template(f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="{tag_filter_button_css}" />
</head>
<body>
    <div id="map" style="width: 100%; height: 100%;"></div>
    <script src="{tag_filter_button_js}"></script>
    <script>
        var map = L.map('map').setView([37.7749, -122.4194], 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {{
            maxZoom: 19
        }}).addTo(map);

        var markers = [];

        var locations = {locations};

        locations.forEach(function(loc) {{
            var marker = L.marker(loc.location).bindPopup(loc.popup);
            marker.tags = loc.tags;
            marker.addTo(map);
            markers.push(marker);
        }});

        var tagFilterButton = new L.Control.TagFilterButton({{
            data: ['city', 'popular', 'business', 'residential', 'quiet'],
            filterOnEveryClick: true
        }});

        tagFilterButton.addTo(map);

        tagFilterButton.on('filter:selection:changed', function(e) {{
            var selectedTags = e.detail.selection;
            markers.forEach(function(marker) {{
                if (selectedTags.some(tag => marker.tags.includes(tag))) {{
                    marker.addTo(map);
                }} else {{
                    map.removeLayer(marker);
                }}
            }});
        }});
    </script>
</body>
</html>
""")

# 保存为HTML文件并显示
with open("map_with_tag_filter_button.html", "w") as f:
    f.write(template.render())

m.save('map_with_tag_filter_button.html')
