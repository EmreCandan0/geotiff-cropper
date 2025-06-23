from db import db_connection
from osgeo import gdal, osr

def get_epsg_from_dataset(dataset):
    proj = dataset.GetProjection()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(proj)

    if srs.IsProjected():
        return srs.GetAttrValue("AUTHORITY", 1)
    elif srs.IsGeographic():
        return srs.GetAttrValue("AUTHORITY", 1)
    else:
        return None

def save_metadata(filename, upload_time, epsg_code, value, geom_str, dataset):
    conn = db_connection()
    cur = conn.cursor()
    try:
        save = f"""
        INSERT INTO tiff_metadata (filename, upload_time, epsg, value, geom)
        VALUES (%s, %s, %s, %s, ST_Transform(ST_SetSRID(ST_GeomFromText(%s), {epsg_code}), 4326))
        """
        cur.execute(save, (filename, upload_time, int(epsg_code), value, geom_str))
        conn.commit()
    except Exception as e:
        print("Metadata Insert Error:", e)
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
