import pandas as pd
import folium
from sklearn.cluster import KMeans
import numpy as np
import random

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("dataset/raw_data.csv")

df = df.rename(columns={
    "Start_Lat": "latitude",
    "Start_Lng": "longitude",
    "Severity": "severity"
})

df = df[["latitude", "longitude", "severity"]].dropna()
df = df.sample(800, random_state=42)

# -----------------------------
# INDIAN CITIES + LOCAL AREAS
# -----------------------------
locations = {
    "Chennai": ["Anna Salai", "T Nagar", "Velachery", "OMR Road"],
    "Bangalore": ["MG Road", "Whitefield", "Electronic City", "Indiranagar"],
    "Mumbai": ["Andheri", "Bandra", "Dadar", "Powai"],
    "Delhi": ["Connaught Place", "Karol Bagh", "Dwarka", "Rohini"],
    "Hyderabad": ["Banjara Hills", "Gachibowli", "Madhapur", "Secunderabad"],
    "Kolkata": ["Salt Lake", "Park Street", "Howrah", "Dum Dum"],
    "Pune": ["Hinjewadi", "Kothrud", "Shivajinagar", "Wakad"],
    "Ahmedabad": ["Navrangpura", "Maninagar", "Satellite", "Bopal"]
}

city_coords = {
    "Chennai": (13.08, 80.27),
    "Bangalore": (12.97, 77.59),
    "Mumbai": (19.07, 72.87),
    "Delhi": (28.61, 77.20),
    "Hyderabad": (17.38, 78.48),
    "Kolkata": (22.57, 88.36),
    "Pune": (18.52, 73.85),
    "Ahmedabad": (23.02, 72.57)
}

latitudes, longitudes, place_names = [], [], []

for _ in range(len(df)):
    city = random.choice(list(locations.keys()))
    area = random.choice(locations[city])

    base_lat, base_lon = city_coords[city]

    latitudes.append(base_lat + np.random.uniform(-0.2, 0.2))
    longitudes.append(base_lon + np.random.uniform(-0.2, 0.2))

    place_names.append(f"{area}, {city}")

df["latitude"] = latitudes
df["longitude"] = longitudes
df["place"] = place_names

# -----------------------------
# KMEANS CLUSTERING
# -----------------------------
X = df[["latitude", "longitude"]]
kmeans = KMeans(n_clusters=5, random_state=42)
df["cluster"] = kmeans.fit_predict(X)

# -----------------------------
# CREATE MAP
# -----------------------------
m = folium.Map(location=[22.5, 80], zoom_start=5)

# -----------------------------
# COLOR FUNCTION
# -----------------------------
def get_color(severity):
    try:
        severity = int(severity)
    except:
        severity = 1

    return {
        1: "green",
        2: "orange",
        3: "red",
        4: "darkred"
    }.get(severity, "blue")

# -----------------------------
# ADD MARKERS
# -----------------------------
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=4,
        color=get_color(row["severity"]),
        fill=True,
        fill_opacity=0.7,
        popup=folium.Popup(f"""
        <div style="font-size:14px;">
            <b>📍 Location:</b> {row['place']}<br>
            <b>⚠ Severity:</b> {row['severity']}<br>
            <b>📊 Cluster:</b> {row['cluster']}
        </div>
        """, max_width=250)
    ).add_to(m)

# -----------------------------
# ENHANCED LEGEND BOX
# -----------------------------
legend_html = '''
<div style="
position: fixed;
bottom: 50px;
left: 50px;
width: 230px;
background-color: white;
border: 2px solid black;
z-index: 9999;
padding: 15px;
font-size: 14px;
border-radius: 10px;
box-shadow: 0 0 15px rgba(0,0,0,0.5);
">

<b style="font-size:16px;">🚦 Severity Legend</b><br><br>

<span style="color:green; font-size:18px;">●</span>
Low - Severity 1<br>

<span style="color:orange; font-size:18px;">●</span>
Medium - Severity 2<br>

<span style="color:red; font-size:18px;">●</span>
High - Severity 3<br>

<span style="color:darkred; font-size:18px;">●</span>
Critical - Severity 4<br>

</div>
'''

m.get_root().html.add_child(folium.Element(legend_html))

# -----------------------------
# SAVE MAP
# -----------------------------
m.save("static/map.html")

print("✅ Enhanced India hotspot map ready!")