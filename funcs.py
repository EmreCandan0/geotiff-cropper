from db import db_connection
from osgeo import gdal,osr
import os

def get_epsg_from_dataset(dataset):
    proj = dataset.GetProjection()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(proj)

    if srs.IsProjected():
        return srs.GetAttrValue("AUTHORITY", 1)  # EPSG kodu
    elif srs.IsGeographic():
        return srs.GetAttrValue("AUTHORITY", 1)  # EPSG kodu
    else:
        return None

def save_metadata(filename,upload_time,epsg,value,geom_str,dataset):
    conn= db_connection()
    cur=conn.cursor()
    epsg_code = get_epsg_from_dataset(dataset)

    try:
        save = f"""
        INSERT INTO tiff_metadata (filename,upload_time,epsg,value,geom)
        VALUES (%s, %s, %s,%s, ST_Transform(ST_SetSRID(ST_GeomFromText(%s), {epsg_code}), 4326))
        """

        cur.execute(save,(filename,upload_time,int(epsg_code),value,geom_str))
        conn.commit()
    except:
        print("Metadata Insert Error")
    finally:
        cur.close()
        conn.close()


def get_geom_wkt_and_bounds(dataset):
    gt = dataset.GetGeoTransform()

    minx = gt[0]
    maxy = gt[3]
    maxx = minx + (dataset.RasterXSize * gt[1])
    miny = maxy + (dataset.RasterYSize * gt[5])

    polygon_wkt = f"POLYGON(({minx} {miny}, {minx} {maxy}, {maxx} {maxy}, {maxx} {miny}, {minx} {miny}))"
    return polygon_wkt, (minx, miny, maxx, maxy)


def get_bounds_epsg4326(filepath):
    gdal.UseExceptions()

    # Projedeki tiffcropper/temp klasörünü kullan
    reprojected_path = os.path.join("temp", "reproj_temp.tif")

    dataset = gdal.Open(filepath)
    if dataset is None:
        raise Exception(f"Cannot open original file: {filepath}")

    warp_result = gdal.Warp(reprojected_path, dataset, dstSRS='EPSG:4326')
    if warp_result is None:
        raise Exception(f"GDAL Warp failed for file: {filepath}")

    ds = gdal.Open(reprojected_path)
    if ds is None:
        raise Exception(f"Failed to open reprojected file: {reprojected_path}")

    gt = ds.GetGeoTransform()
    minx = gt[0]
    maxy = gt[3]
    maxx = minx + (ds.RasterXSize * gt[1])
    miny = maxy + (ds.RasterYSize * gt[5])

    return minx, miny, maxx, maxy