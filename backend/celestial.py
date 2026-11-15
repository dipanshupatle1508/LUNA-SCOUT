"""Geometric Moon-relative body vectors for both flight and home lighting."""
from datetime import datetime,timezone,timedelta
from functools import lru_cache
import numpy as np
from .engine import sp,LOCK,iso

@lru_cache(maxsize=6)
def celestial(start,days=120,step_hours=6):
    dt=datetime.fromisoformat(start.replace('Z','+00:00'))
    if dt.tzinfo is None:dt=dt.replace(tzinfo=timezone.utc)
    dt=dt.astimezone(timezone.utc)
    if dt<datetime(2000,1,1,tzinfo=timezone.utc) or dt+timedelta(days=days)>datetime(2051,1,1,tzinfo=timezone.utc):
        raise ValueError('Choose an interval within 2000–2050 UTC.')
    elapsed=np.r_[np.arange(0,days*86400,step_hours*3600,dtype=float),days*86400]
    with LOCK:
        times=sp.str2et(dt.strftime('%Y-%m-%dT%H:%M:%S'))+elapsed
        earth=np.array(sp.spkpos('EARTH',times,'MOON_ME','NONE','MOON')[0])
        sun=np.array(sp.spkpos('SUN',times,'MOON_ME','NONE','MOON')[0])
        rotation=[np.round(sp.pxform('IAU_EARTH','MOON_ME',et),12).ravel().tolist() for et in times]
    return {'t':[iso(dt.timestamp()+x) for x in elapsed],
            'earth_km':np.round(earth,6).tolist(),'sun_km':np.round(sun,3).tolist(),
            'earth_fixed_to_moon':rotation,'radii_km':{'moon':1737.4,'earth':6378.137,'sun':695700},
            'method':{'frame':'MOON_ME (DE440_ME421)','ephemeris':'DE440s','orientation':'DE440 PCK',
                      'correction':'NONE: geometric positions','step_hours':step_hours,
                      'earth_texture_orientation':'IAU_EARTH rotation; visual globe orientation, not station-grade ITRF',
                      'note':'Positions and directions are geometric. Display lighting/exposure and the schematic inset are illustrative.'}}
