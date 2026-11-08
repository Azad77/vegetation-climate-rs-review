"""compute_biome_areas.py - area of each RESOLVE Ecoregions 2017 biome (Dinerstein et al., 2017) in the Mollweide equal-area
projection. Input: Ecoregions2017.shp from https://storage.googleapis.com/teow2016/Ecoregions2017.zip (not redistributed).
Usage: python compute_biome_areas.py /path/to/Ecoregions2017.shp   ->  ../reviewer_response/geography/biome_areas.csv"""
import os, sys, geopandas as gpd
g = gpd.read_file(sys.argv[1], columns=['BIOME_NUM', 'BIOME_NAME']).to_crs('ESRI:54009')
g['km2'] = g.geometry.area / 1e6
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reviewer_response', 'geography', 'biome_areas.csv')
g.groupby(['BIOME_NUM', 'BIOME_NAME']).km2.sum().reset_index().to_csv(out, index=False); print('wrote', out)
