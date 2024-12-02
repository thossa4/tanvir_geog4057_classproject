import arcpy
import os
import ee
import pandas as pd


"""
Example usage:
python project2.py D:\project2 boundary.csv pnt_elev2.shp 32119


"""
def getGeeElevation(workspace, csv_file, outfc_name, epsg=4326):
    """
    workspace: directory that contains input and output
    csv_file: input csv filename
    epsg: wkid code for the spatial reference, e.g. 4326 for WGS CGS
    
    """
    # Load the CSV file
    csv_fullname = os.path.join(workspace, csv_file)
    df = pd.read_csv(csv_fullname)
    dem = ee.Image('USGS/3DEP/10m')
    
    print(epsg)
    geometrys = [ee.Geometry.Point([x, y], f'EPSG:{epsg}') for x, y in zip(df['X'], df['Y'])]
    fc = ee.FeatureCollection(geometrys)
    origin_info = fc.getInfo()
    
    sampled_fc = dem.sampleRegions(
        collection=fc, 
        scale=10,  # Resolution of the image
        geometries=True
    )
    sampled_info = sampled_fc.getInfo()
    
    for ind, itm in enumerate(origin_info['features']):
        itm['properties'] = sampled_info['features'][ind]['properties']

    # Create the feature class
    fcname = os.path.join(workspace, outfc_name)
    if arcpy.Exists(fcname):
        arcpy.management.Delete(fcname)
    arcpy.management.CreateFeatureclass(workspace, outfc_name, geometry_type='POINT', spatial_reference=epsg)
    arcpy.management.AddField(fcname, field_name='elevation', field_type='FLOAT')

    # Insert rows into the feature class
    with arcpy.da.InsertCursor(fcname, ['SHAPE@', 'elevation']) as cursor:
        for feat in origin_info['features']:
            # Get the coordinates and create a point geometry
            coords = feat['geometry']['coordinates']
            pnt = arcpy.PointGeometry(arcpy.Point(coords[0], coords[1]), spatial_reference=epsg)
            # Get the properties and write it to elevation
            elev = feat['properties']['elevation']
            cursor.insertRow([pnt, elev])

def main():
    import sys
    try:
        ee.Initialize(project='ee-tanvir54hossain')
    except:
        ee.Authenticate()
        ee.Initialize(project='ee-tanvir54hossain')
    workspace = sys.argv[1]
    csv_file = sys.argv[2]
    outfc_name = sys.argv[3]
    epsg = int(sys.argv[4])

    workspace = workspace
    csv_file = csv_file
    outfc_name = outfc_name
    epsg = epsg
    getGeeElevation(workspace, csv_file, outfc_name, epsg=epsg)



if __name__ == '__main__':
    main()
