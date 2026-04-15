from flask import Flask, render_template, request, redirect
import pandas as pd
import folium
from sklearn.cluster import KMeans
import numpy as np
import random
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'


# =====================================================
# 🔵 EXISTING DATASET FUNCTION (UNCHANGED)
# =====================================================
def process_existing_dataset(file_path):
    df = pd.read_csv(file_path)

    df = df.rename(columns={
        "Start_Lat": "latitude",
        "Start_Lng": "longitude",
        "Severity": "severity"
    })

    df = df[["latitude", "longitude", "severity"]].dropna()

    if len(df) > 1000:
        df = df.sample(1000)

    X = df[["latitude", "longitude"]]
    kmeans = KMeans(n_clusters=5, random_state=42)
    df["cluster"] = kmeans.fit_predict(X)

    m = folium.Map(location=[20.5, 78.9], zoom_start=5)

    severity_colors = {
        1: "green",
        2: "yellow",
        3: "red",
        4: "darkred"
    }

    for _, row in df.iterrows():
        severity = int(row["severity"]) if str(row["severity"]).isdigit() else 1
        color = severity_colors.get(severity, "blue")

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=5,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=f"Severity: {row['severity']} | Cluster: {int(row['cluster'])}"
        ).add_to(m)

    m.save("static/map.html")


# =====================================================
# 🟢 UPLOAD DATASET FUNCTION (LEGEND INCLUDED)
# =====================================================
def process_uploaded_dataset(file_path):

    if not os.path.exists(file_path):
        return False

    try:
        df = pd.read_csv(file_path)

        rename_map = {}
        for col in df.columns:
            col_lower = col.lower()

            if "lat" in col_lower:
                rename_map[col] = "latitude"
            elif "lng" in col_lower or "lon" in col_lower:
                rename_map[col] = "longitude"
            elif "severity" in col_lower:
                rename_map[col] = "severity"

        df = df.rename(columns=rename_map)

        if "latitude" not in df.columns or "longitude" not in df.columns:
            return False

        if "severity" not in df.columns:
            df["severity"] = np.random.randint(1, 4, len(df))

        df = df[["latitude", "longitude", "severity"]].dropna()

        if len(df) > 800:
            df = df.sample(800, random_state=42)

        places_list = [
            "Anna Salai", "T Nagar", "Velachery", "OMR Road",
            "MG Road", "Whitefield", "Electronic City", "Indiranagar"
        ]

        city_coords = {
            "Chennai": (13.08, 80.27),
            "Bangalore": (12.97, 77.59),
            "Mumbai": (19.07, 72.87),
            "Delhi": (28.61, 77.20)
        }

        cities = list(city_coords.keys())

        latitudes, longitudes, places = [], [], []

        for _ in range(len(df)):
            city = random.choice(cities)
            place = random.choice(places_list)

            base_lat, base_lon = city_coords[city]

            latitudes.append(base_lat + np.random.uniform(-0.2, 0.2))
            longitudes.append(base_lon + np.random.uniform(-0.2, 0.2))
            places.append(place)

        df["latitude"] = latitudes
        df["longitude"] = longitudes
        df["place"] = places

        X = df[["latitude", "longitude"]]
        kmeans = KMeans(n_clusters=5, random_state=42)
        df["cluster"] = kmeans.fit_predict(X)

        m = folium.Map(location=[22.5, 80], zoom_start=5)

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

        for _, row in df.iterrows():
            popup_content = f"""
            <b>📍 Place:</b> {row['place']}<br>
            <b>⚠ Severity:</b> {row['severity']}<br>
            <b>📊 Cluster:</b> {row['cluster']}
            """

            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=7,
                color=get_color(row["severity"]),
                fill=True,
                fill_color=get_color(row["severity"]),
                fill_opacity=0.9,
                popup=folium.Popup(popup_content, max_width=250)
            ).add_to(m)

        # ✅ LEGEND
        legend_html = '''
        <div style="
        position: fixed;
        bottom: 20px;
        left: 20px;
        width: 220px;
        background: white;
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        font-size: 14px;
        line-height: 1.8;
        z-index:9999;
        ">
        <b>🚦 Severity Legend</b><br><br>

        <span style="color:green;">●</span> Low - Severity 1<br>
        <span style="color:orange;">●</span> Medium - Severity 2<br>
        <span style="color:red;">●</span> High - Severity 3<br>
        <span style="color:darkred;">●</span> Critical - Severity 4<br>
        </div>
        '''

        m.get_root().html.add_child(folium.Element(legend_html))

        m.save("static/map.html")
        return True

    except Exception as e:
        print(e)
        return False


# =====================================================
# ⚡ PRE-GENERATE EXISTING MAP (INSTANT)
# =====================================================
if not os.path.exists("static/map.html"):
    process_existing_dataset("dataset/raw_data.csv")


# =====================================================
# ROUTES
# =====================================================
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/existing")
def existing():
    return redirect("/map")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]

    if file:
        path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(path)

        success = process_uploaded_dataset(path)

        if success:
            return redirect("/map")
        else:
            return "Upload failed"

    return "No file uploaded"


@app.route("/map")
def show_map():
    return render_template("map.html")


# =====================================================
if __name__ == "__main__":
    app.run(debug=True)