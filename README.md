# GEO-SEQUENCE 🛰️

A professional-grade educational application for **Geospatial ML Engineering**. Analyze vegetation trends and satellite imagery sequences (timelapses) anywhere on Earth using the Microsoft Planetary Computer.

## 🌟 Features

- **Interactive Global Map**: Select any Area of Interest (AOI) with a single click.
- **Sentinel-2 Time-lapse**: Fetch and visualize a sequence of 36 satellite passes over a 12-month period.
- **NDVI Analysis**: Calculate the Normalized Difference Vegetation Index to monitor plant health.
- **Multimodal Visualization**: View True Color (RGB) frames side-by-side with NDVI heatmaps.
- **Mission Control UI**: A high-contrast, brutalist B&W aesthetic designed for focus and clarity.
- **Manual Time Range**: Specify custom start and end dates for targeted historical analysis.

## 🛠️ Technology Stack

- **Backend**: Python, Flask, `pystac-client` (STAC), `stackstac`, `xarray`, `planetary-computer`.
- **Frontend**: Vanilla JavaScript, Leaflet.js (Mapping), Chart.js (Analytics).
- **Styling**: Modern Vanilla CSS with a focus on high-contrast aesthetics.

## 🧠 Core Concepts Explained

### STAC (SpatioTemporal Asset Catalog)
This app uses the STAC standard to query millions of satellite images. Instead of downloading whole datasets, we search for exactly what we need (location + time) and fetch only the relevant metadata first.

### COG (Cloud Optimized GeoTIFF)
All imagery is fetched from COG files. This allows the app to perform "lazy-loading"—requesting only the specific pixels for your AOI without downloading the entire satellite scene (which can be gigabytes).

## 🚀 Getting Started

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd mini_geospatial_app
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```
   The app will be available at `http://localhost:5002`.

### Deployment (Railway)

This project is pre-configured for deployment on **Railway.app** or **Render**:
- `Procfile`: Defines the start command for production.
- `requirements.txt`: Lists all necessary Python packages.
- `app.py`: Handles dynamic port assignment from the environment.

Simply connect your GitHub repository to Railway, and it will deploy automatically.

---

*Built for learning the fundamentals of modern Earth Observation pipelines.*
