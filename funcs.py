from db import db_connection
from osgeo import osr

def get_epsg_from_dataset(dataset):
    """
       Extract the EPSG code from a GDAL dataset.

       :param dataset: GDAL dataset object.
       :type dataset: gdal.Dataset
       :return: EPSG code as a string (e.g., '4326') or None if unavailable.
       :rtype: str | None
       """

    proj = dataset.GetProjection()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(proj)

    if srs.IsProjected():
        return srs.GetAttrValue("AUTHORITY", 1)
    elif srs.IsGeographic():
        return srs.GetAttrValue("AUTHORITY", 1)
    else:
        return None

def save_metadata(filename:str, upload_time, epsg_code:int, value:str, geom_str:str):
    """
    Save metadata for a TIFF file into the database.

    :param filename: The name of the uploaded TIFF file.
    :type filename: str
    :param upload_time: The upload timestamp (UTC).
    :type upload_time: datetime.pyi
    :param epsg_code: EPSG code of the original dataset projection.
    :type epsg_code: int
    :param value: The AREA_OR_POINT metadata value.
    :type value: str
    :param geom_str: WKT representation of the bounding box.
    :type geom_str: str
    :return: None
    :rtype: Null
    """
    conn = db_connection()
    cur = conn.cursor()
    try:
        save = f"""
        INSERT INTO tiff_metadata (filename, upload_time, epsg, value, geom)
        VALUES (%s, %s, %s, %s, ST_Transform(ST_SetSRID(ST_GeomFromText(%s), {epsg_code}), 4326))
        """
        cur.execute(save, (filename, upload_time, epsg_code, value, geom_str))
        conn.commit()
    except Exception as e:
        print("Metadata Insert Error:", e)
    finally:
        cur.close()
        conn.close()

def get_geom_wkt_and_bounds(dataset):
    """
    Generate the bounding box and WKT polygon of a raster dataset.

    :param dataset: The GDAL dataset object to extract bounding info from.
    :type dataset: gdal.Dataset
    :return: A tuple containing the WKT polygon and 4326 converted bounding box coordinates (minx, miny, maxx, maxy).
    :rtype: tuple[str, tuple[float, float, float, float]]
    """
    gt = dataset.GetGeoTransform()
    minx = gt[0]
    maxy = gt[3]
    maxx = minx + (dataset.RasterXSize * gt[1])
    miny = maxy + (dataset.RasterYSize * gt[5])

    polygon_wkt = f"POLYGON(({minx} {miny}, {minx} {maxy}, {maxx} {maxy}, {maxx} {miny}, {minx} {miny}))"
    return polygon_wkt, (minx, miny, maxx, maxy)
