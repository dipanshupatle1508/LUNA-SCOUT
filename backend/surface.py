"""Local, site-centred LOLA grids for the supplied walking navigator."""
from functools import lru_cache
import numpy as np
from .terrain import sample,destination,layers,load,R

@lru_cache(maxsize=8)
def surface(lat,lon,mode='adjusted'):
    def grid(extent,size):
        axis=np.linspace(-extent,extent,size)
        x,z=np.meshgrid(axis,axis)
        distance=np.hypot(x,z)
        azimuth=np.arctan2(x,-z)
        la,lo=destination(lat,lon,azimuth,distance)
        heights=sample(la,lo,mode)
        if not np.isfinite(heights).all(): raise ValueError('Incomplete local elevation coverage.')
        return {'extent_m':extent,'size':size,'height_m':np.round(heights,3).ravel().tolist()}
    resolution=next(load(n)[4] for n,limit in layers(mode) if lat<=limit)
    return {'lat':lat,'lon':lon,'ground_m':float(sample(lat,lon,mode)),
            'resolution_m':resolution,'radius_m':R,'near':grid(4096,257),'far':grid(80000,129),
            'method':'Site-centred great-circle sampling of supplied LOLA elevations; grid rows increase south, columns east; bilinear resampling.',
            'note':'Fine rendering does not add DEM detail. Sub-grid rocks are decorative. This is not a landing-hazard assessment.'}
