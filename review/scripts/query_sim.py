"""Simulation of the 13-pair Scopus query on title/abstract text (shared by search_screening_eval.py and index_bias.py)."""
import re
# ---- the executed query, as 13 AND-of-OR pairs (STEP1 notebook, cell 3)
PAIRS = [[["satellite remote sensing","multispectral","hyperspectral"],["ndvi","evi","lai"],["climate change"]],
 [["modis"],["phenology","greening","browning"],["climate change"]],
 [["landsat"],["land cover change"],["climate change"],["ndvi","evi","vegetation"]],
 [["sentinel-2"],["vegetation","biomass","forest"],["climate change"]],
 [["sar","synthetic aperture radar"],["forest","biomass"],["climate change"]],
 [["random forest","convolutional neural network","lstm","xgboost","transformer"],["remote sensing"],["vegetation"],["climate change"]],
 [["deep learning"],["satellite","remote sensing"],["vegetation dynamics","phenology","ndvi"],["climate change"]],
 [["viirs","desis","hyperspectral"],["spectral index","vegetation index","ndwi","nbr","sif"],["climate change"]],
 [["drought"],["remote sensing","satellite"],["ndvi","evi"],["climate change"]],
 [["wildfire","fire"],["remote sensing","satellite"],["vegetation recovery","nbr","burn severity"],["climate change"]],
 [["aboveground biomass"],["satellite","remote sensing"],["climate change"]],
 [["grassland","tundra","savanna","dryland"],["remote sensing","satellite"],["ndvi","evi"],["climate change"]],
 [["phenology","greening","browning"],["modis","landsat"],["climate change"],["ndvi","evi","lai"]]]
def has(t, ph):
    ph = re.escape(ph).replace(r'\-', '[- ]?').replace(r'\ ', '[- ]')
    return re.search(r'\b' + ph + r's?\b', t) is not None
def query_match(t):
    t = t.lower().replace('-', ' ').replace('‐', ' ')
    t2 = t
    ok = [all(any(has(t2, p.replace('-', ' ')) for p in grp) for grp in pr) for pr in PAIRS]
    return any(ok), has(t2, 'climate change')

