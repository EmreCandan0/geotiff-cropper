# GeoTIFF Cropper 🗺️✂️

This project allows users to upload GeoTIFF raster files through a web interface, extract bounding boxes, and crop the image based on coordinates. The original metadata is saved to a PostgreSQL + PostGIS database, and all cropping is performed in EPSG:4326 (WGS84) for consistency and display purposes.

## 🚀 Features

- Upload GeoTIFF raster files via a simple web UI
- Extract metadata (projection, bounding box, WKT polygon)
- Save any original EPSG and geometry to a PostGIS database
- Reproject to EPSG:4326 for display and cropping
- Perform interactive cropping using coordinates
- Export the cropped result as PNG
- Built with Flask + GDAL + PostgreSQL/PostGIS

## 📦 Project Structure

```

 ── tiffcropper/
│   ├── app.py
│   ├── funcs.py
│   ├── db.py
│   ├── temp/
│   ├── static/
│   │   └── outputs/
│   └── templates/
│       └── index.html
├── init_tiff_metadata.sql
├── README.md
```
![1](https://github.com/user-attachments/assets/d625bfd5-a8d8-4daa-b6ce-f78b10feb50c)
![2](https://github.com/user-attachments/assets/f9d45076-3e82-4e17-b5e0-53ee126e7601)
![DB1](https://github.com/user-attachments/assets/092aaf1d-d38a-4adf-88d0-69731f08f9af)
![db2](https://github.com/user-attachments/assets/2610ceff-02c7-464e-af18-305c37dca6d8)




## 🛠️ Installation

1. **Create a Python environment**
   ```bash
   conda create -n test_gdal python=3.10
   conda activate test_gdal
   ```

2. **Install required packages**
   ```bash
   pip install flask flask-restful psycopg2-binary
   ```

3. **Install GDAL**
   ```bash
   conda install -c conda-forge gdal
   ```

4. **Setup PostgreSQL + PostGIS database**
   - Run the following SQL script:
     ```sql
     -- init_tiff_metadata.sql
     CREATE EXTENSION IF NOT EXISTS postgis;

     CREATE TABLE IF NOT EXISTS tiff_metadata (
         id SERIAL PRIMARY KEY,
         filename TEXT NOT NULL,
         upload_time TIMESTAMP NOT NULL,
         epsg INTEGER,
         value TEXT,
         geom geometry(Polygon, 4326)
     );
     ```

5. **Check your database connection**
   Update `db.py` with correct credentials:
   ```python
   def db_connection():
       return psycopg2.connect(
           host="localhost",
           dbname="your_database",
           user="postgres",
           password="your_password"
       )
   ```

## ▶️ Running the App

```bash
python GeoTIFF_Cropper/app.py
```

Then go to: [http://localhost:5000/index](http://localhost:5000/index)

## 💡 How to Use

1. Upload a `.tif` or `.tiff` file via the UI.
2. The app extracts the bounding box and displays EPSG:4326 coordinates.
3. You may adjust the coordinates manually.
4. Click "Crop and Convert to PNG" to generate and preview the result.

## 📂 Notes

- Uploaded files are stored in `uploads/`
- Reprojected files are temporarily saved in `temp/`
- Cropped PNGs are saved in `static/outputs/`
- The original CRS (EPSG) and geometry are preserved in the database
- All UI display and cropping actions use EPSG:4326 for consistency
