"""LOLA spherical terrain sampling; all internal lengths in metres."""
from functools import lru_cache
from pathlib import Path
import numpy as np
import rasterio
from pyproj import Transformer, CRS

ROOT = Path(__file__).resolve().parents[1] / 'data' / 'terrain'
R = 1737400.0
GEO = CRS.from_proj4(f'+proj=longlat +R={R} +no_defs')

@lru_cache(maxsize=3)
def load(name):
    if name == 'global':
        return np.memmap(ROOT / 'LDEM_16 (2).IMG', dtype='<i2', mode='r', shape=(2880,5760)), None, None, 0.5, 1895.21
    with rasterio.open(ROOT / name) as ds:
        arr = ds.read(1)
        # LOLA legacy integer GDRs encode 0.5 m/count; adjusted float TIFF is metres.
        scale = 0.5 if name.endswith('.JP2') else 1.0
        return arr, ~ds.transform, Transformer.from_crs(GEO,ds.crs,always_xy=True), scale, abs(ds.transform.a)


def layers(mode):
    if mode == 'fine':
        return [('LDEM_875S_20M.JP2',-87.5),('LDEM_85S_40M.JP2',-85),('LDEM_80S_80M.JP2',-80),('LDEM_60S_240M.JP2',-60),('global',90)]
    return [('LDEM_80S_80MPP_ADJ.tiff',-80),('LDEM_60S_240M.JP2',-60),('global',90)]


def sample(lat,lon,mode='adjusted'):
    lat,lon=np.broadcast_arrays(np.asarray(lat,float),np.asarray(lon,float))
    out=np.full(lat.shape,np.nan)
    for name, limit in layers(mode):
        select=(lat <= limit) & ~np.isfinite(out)
        if not select.any(): continue
        a,inv,tr,scale,_=load(name)
        la,lo=lat[select],lon[select]
        if tr:
            x,y=tr.transform(lo,la); c,r=inv*(x,y)
        else:
            c=(lo%360)*16; r=(90-la)*16
        # Bilinear interpolation at pixel centres. Clamp at physical grid edges.
        c=np.asarray(c)-0.5; r=np.clip(np.asarray(r)-0.5,0,a.shape[0]-1)
        c=np.clip(c,0,a.shape[1]-1) if tr else c%a.shape[1]
        c0=np.floor(c).astype(int); r0=np.floor(r).astype(int)
        c1=(c0+1)%a.shape[1] if not tr else np.minimum(c0+1,a.shape[1]-1)
        r1=np.minimum(r0+1,a.shape[0]-1)
        dc=c-c0; dr=r-r0
        v=((1-dr)*((1-dc)*a[r0,c0]+dc*a[r0,c1])+dr*((1-dc)*a[r1,c0]+dc*a[r1,c1]))*scale
        # Fill gaps from the next, coarser source, never with a fictitious clear horizon.
        out[select]=v
    return out


def destination(lat,lon,az,d):
    la,lo=np.radians(lat),np.radians(lon); delta=d/R
    la2=np.arcsin(np.clip(np.sin(la)*np.cos(delta)+np.cos(la)*np.sin(delta)*np.cos(az),-1,1))
    lo2=lo+np.arctan2(np.sin(az)*np.sin(delta)*np.cos(la),np.cos(delta)-np.sin(la)*np.sin(la2))
    # At an exact pole the usual longitude formula becomes 0/0. Continue in the specified local north/east frame.
    lo2=np.where(np.abs(np.cos(la))<1e-12,np.where(la<0,lo+az,lo+np.pi-az),lo2)
    return np.degrees(la2),np.degrees(lo2)


@lru_cache(maxsize=24)
def profile(lat,lon,height=2.0,mode='adjusted',radius_km=120):
    h0=float(sample(lat,lon,mode))
    if not np.isfinite(h0): raise ValueError('No valid terrain elevation at this coordinate.')
    local_res=next((load(n)[4] for n,limit in layers(mode) if lat<=limit),1895.21)
    # Resolve nearby terrain at source spacing, distant rays at 160 m.
    near=max(20,local_res)
    d=np.unique(np.r_[np.arange(near,min(10000,radius_km*1000)+near,near),np.arange(10000,radius_km*1000+1,160),radius_km*1000])
    az=np.radians(np.arange(360))[:,None]
    la,lo=destination(lat,lon,az,d[None,:]); h=sample(la,lo,mode)
    if not np.isfinite(h).all(): raise ValueError('Incomplete terrain coverage along horizon rays.')
    theta=d[None,:]/R
    # Exact spherical local ENU components rather than a planar curvature approximation.
    horiz=(R+h)*np.sin(theta)
    up=(R+h)*np.cos(theta)-(R+h0+height)
    angles=np.degrees(np.arctan2(up,horiz))
    hz=angles.max(axis=1)
    used=[n for n,limit in layers(mode) if np.any(la<=limit)]
    return {'az':list(range(360)), 'el':hz.tolist(),'ground_m':h0,'resolution_m':local_res,'radius_km':radius_km,'datasets':used}
