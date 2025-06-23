from flask import Flask,render_template,request
from flask_restful import Resource,Api
from funcs import get_bounds_epsg4326,get_geom_wkt_and_bounds,save_metadata,get_epsg_from_dataset
from osgeo import gdal
import os
from datetime import datetime



app=Flask(__name__)
api=Api(app)

@app.route('/index')
def index():
    return render_template("index.html")


class UploadTIFF(Resource):
    @staticmethod
    def post():
        try:
            file= request.files.get('tiff_file')
        except:
            return {"error": "Cant get the tiff file"}, 400

        filename=file.filename
        filepath= f'uploads/{filename}'
        file.save(filepath)

        dataset = gdal.Open(filepath)
        metadata = dataset.GetMetadata()

        key = "AREA_OR_POINT"
        value = metadata.get(key)

        print(metadata)

        geom_str, _ = get_geom_wkt_and_bounds(dataset)  # EPSG dönüşümsüz orijinal geometri
        epsg_code = get_epsg_from_dataset(dataset)
        upload_time = datetime.utcnow()

        save_metadata(filename, upload_time, epsg_code, value, geom_str, dataset)


        minx, miny, maxx, maxy = get_bounds_epsg4326(filepath)

        return {
            "message": "TIFF Uploaded Successfully.",
            "minx": minx,
            "miny": miny,
            "maxx": maxx,
            "maxy": maxy,
            "filename": filename
        }, 201

api.add_resource(UploadTIFF,'/upload')



class CropImage(Resource):
    def post(self):
        data = request.get_json()
        filename = data.get('filename')
        minx = float(data['minx'])
        miny = float(data['miny'])
        maxx = float(data['maxx'])
        maxy = float(data['maxy'])

        input_path = f'uploads/{filename}'
        reprojected_path = f'temp/reprojected_{filename}'
        output_path = f'static/outputs/{os.path.splitext(filename)[0]}_cropped.png'

        if not os.path.exists(input_path):
            return {"error": "Could not find the file"}, 404


        gdal.Warp(reprojected_path, input_path, dstSRS='EPSG:4326')
        options = gdal.TranslateOptions(
            format='PNG',
            projWin=[minx, maxy, maxx, miny],  # sırası bu: left, top, right, bottom
            outputType=gdal.GDT_Byte,
            scaleParams=[[0, 1, 0, 255]]
        )

        gdal.Translate(output_path, reprojected_path, options=options)

        return {"image_url": output_path}


api.add_resource(CropImage, "/crop")


if __name__=='__main__':
    app.run(debug=True,use_reloader=False)


