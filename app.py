from flask import Flask, render_template, request
from flask_restful import Resource, Api
from funcs import get_geom_wkt_and_bounds, save_metadata, get_epsg_from_dataset
from osgeo import gdal
import os
from datetime import datetime

app = Flask(__name__)
api = Api(app)

@app.route('/index')
def index():
    return render_template("index.html")


class UploadTIFF(Resource):
    @staticmethod
    def post():
        try:
            file = request.files.get('tiff_file')
        except FileNotFoundError :
            return {"error": "Can't get the tiff file"}, 400

        filename = file.filename
        filepath = f'uploads/{filename}'
        file.save(filepath)

        dataset = gdal.Open(filepath)
        metadata = dataset.GetMetadata()
        key = "AREA_OR_POINT"
        value = metadata.get(key)

        print(metadata)

        geom_str, _ = get_geom_wkt_and_bounds(dataset)
        epsg_code = get_epsg_from_dataset(dataset)
        upload_time = datetime.now()

        save_metadata(filename, upload_time, epsg_code, value, geom_str)

        #Reproject to EPSG:4326 and store permanently
        reprojected_path = f'temp/reprojected_{filename}'
        warp_result = gdal.Warp(reprojected_path, filepath, dstSRS='EPSG:4326')
        if warp_result is None:
            return {"error": "Warp failed"}, 500

        ds = gdal.Open(reprojected_path)
        gt = ds.GetGeoTransform()
        minx = gt[0]
        maxy = gt[3]
        maxx = minx + (ds.RasterXSize * gt[1])
        miny = maxy + (ds.RasterYSize * gt[5])

        return {
            "message": "TIFF Uploaded Successfully.",
            "minx": minx,
            "miny": miny,
            "maxx": maxx,
            "maxy": maxy,
            "filename": filename
        }, 201

api.add_resource(UploadTIFF, '/upload')


class CropImage(Resource):
    @staticmethod
    def post():
        data = request.get_json()
        filename = data.get('filename')
        minx = float(data['minx'])
        miny = float(data['miny'])
        maxx = float(data['maxx'])
        maxy = float(data['maxy'])

        reprojected_path = f'temp/reprojected_{filename}'
        output_path = f'static/outputs/{os.path.splitext(filename)[0]}_cropped.png'

        if not os.path.exists(reprojected_path):
            return {"error": "Reprojected file not found"}, 404

        options = gdal.TranslateOptions(
            format='PNG',
            projWin=[minx, maxy, maxx, miny],
            outputType=gdal.GDT_Byte,
            scaleParams=[[0, 1, 0, 255]]
        )

        gdal.Translate(output_path, reprojected_path, options=options)

        return {"image_url": output_path}

api.add_resource(CropImage, "/crop")

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    os.makedirs("static/outputs", exist_ok=True)
    app.run(debug=True, use_reloader=False)
