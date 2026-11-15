"""Transparent regional landing screening, never a probability of safe touchdown."""
from functools import lru_cache
import numpy as np
from .terrain import sample, destination, layers, load, R
from .engine import timeline
from .flight_status import flight_status


def summarize_grid(h, spacing, radius, slope_limit=10):
    h=np.asarray(h,float);n=h.shape[0];axis=(np.arange(n)-(n-1)/2)*spacing
    x,y=np.meshgrid(axis,axis);mask=x*x+y*y<=radius*radius
    if not np.isfinite(h).all(): raise ValueError('Incomplete terrain coverage')
    dx=((h[:-2,2:]+2*h[1:-1,2:]+h[2:,2:])-(h[:-2,:-2]+2*h[1:-1,:-2]+h[2:,:-2]))/(8*spacing)
    dy=((h[2:,:-2]+2*h[2:,1:-1]+h[2:,2:])-(h[:-2,:-2]+2*h[:-2,1:-1]+h[:-2,2:]))/(8*spacing)
    slopes=np.degrees(np.arctan(np.hypot(dx,dy)))[mask[1:-1,1:-1]]
    a=np.c_[x[mask],y[mask],np.ones(mask.sum())];v=h[mask];fit=np.linalg.lstsq(a,v,rcond=None)[0];residual=v-a@fit
    return {'slope_median_deg':float(np.median(slopes)), 'slope_p95_deg':float(np.percentile(slopes,95)),
            'slope_max_deg':float(slopes.max()), 'roughness_m':float(np.sqrt(np.mean(residual**2))),
            'steep_percent':float(100*np.mean(slopes>slope_limit)), 'local_relief_m':float(np.ptp(v)),
            'samples':int(mask.sum()),'radius_m':radius,'spacing_m':spacing}


@lru_cache(maxsize=512)
def terrain_metrics(lat,lon,slope_limit=10,radius=1000):
    name,res=next((n,load(n)[4]) for n,limit in layers('adjusted') if lat<=limit)
    elevation=float(sample(lat,lon));base={'elevation_m':elevation,'datum_radius_m':R,'dataset':name,'resolution_m':res,'radius_m':radius}
    if res>radius/4:return {**base,'assessed':False,'reason':'DEM too coarse for this 2 km-diameter assessment; do not treat it as safer.'}
    count=int(np.ceil(radius/res))+1;axis=np.arange(-count,count+1)*res;x,y=np.meshgrid(axis,axis)
    la,lo=destination(lat,lon,np.arctan2(x,-y),np.hypot(x,y));h=sample(la,lo)
    return {**base,**summarize_grid(h,res,radius,slope_limit),'assessed':True}


@lru_cache(maxsize=64)
def window_summary(lat,lon,at,days):
    return timeline(lat,lon,at,days=days,step_min=60)['summary']


def rank_record(site,t,status,window,limits):
    reasons=[]
    if not t['assessed']:return {**site,'terrain':t,'instant':status,'window':window,'score':None,'category':'UNASSESSED','violations':[t['reason']]}
    checks=[(t['slope_p95_deg']>limits['slope_limit'],'95th-percentile slope exceeds limit'),
            (t['roughness_m']>limits['roughness_limit'],'Detrended roughness exceeds limit'),
            (t['steep_percent']>limits['steep_limit'],'Too much area exceeds slope limit'),
            (window['sunlit_percent']<limits['sun_min'],'Insufficient sunlight over mission interval'),
            (window['earth_percent']<limits['earth_min'],'Insufficient full-Earth visibility over mission interval'),
            (status['sun']['fraction']<=1e-6,'Landing time is in direct shadow'),
            (status['earth']['status']!='CLEAR','Full Earth disk not clear at landing time')]
    if limits.get('elevation_min') is not None:checks.append((t['elevation_m']<limits['elevation_min'],'Below mission elevation corridor'))
    if limits.get('elevation_max') is not None:checks.append((t['elevation_m']>limits['elevation_max'],'Above mission elevation corridor'))
    reasons=[reason for bad,reason in checks if bad]
    norm=lambda v,scale:max(0,min(1,v/scale))
    parts={'slope':35*(1-norm(t['slope_p95_deg'],limits['slope_limit']*2)),
           'roughness':20*(1-norm(t['roughness_m'],limits['roughness_limit']*2)),
           'steep_area':15*(1-norm(t['steep_percent'],max(1,limits['steep_limit']*2))),
           'sun_window':10*window['sunlit_percent']/100,'earth_window':10*window['earth_percent']/100,
           'landing_sun':5*status['sun']['fraction'],'landing_earth':5*float(status['earth']['status']=='CLEAR')}
    return {**site,'terrain':t,'instant':status,'window':window,'score':round(sum(parts.values()),2),'score_parts':parts,
            'category':'WITHIN LIMITS' if not reasons else 'LIMITS EXCEEDED','violations':reasons}


def sort_records(records):
    order={'WITHIN LIMITS':0,'LIMITS EXCEEDED':1,'UNASSESSED':2}
    records.sort(key=lambda r:(order[r['category']],-(r['score'] if r['score'] is not None else -1),r['id']))
    for i,r in enumerate(records):r['rank']=i+1 if r['category']!='UNASSESSED' else None
    return records


def rank_sites(sites,at,days=14,**limits):
    records=[]
    for site in sites:
        t=terrain_metrics(site['lat'],site['lon'],limits['slope_limit'])
        st=flight_status(site['lat'],site['lon'],at,0);w=window_summary(site['lat'],site['lon'],at,days)
        records.append(rank_record(site,t,st,w,limits))
    return {'at':at,'days':days,'limits':limits,'records':sort_records(records),
            'method':'2 km-diameter regional LOLA screening; Horn 3x3 slopes at source spacing; RMS residual from fitted plane; not metre-scale rock hazards. Gate categories precede weighted score.',
            'weights':{'slope':35,'roughness':20,'steep_area':15,'sun_window':10,'earth_window':10,'landing_sun':5,'landing_earth':5},
            'elevation_note':'Elevation is radial height above a 1,737,400 m lunar sphere. No monotonic safety bonus. Optional mission elevation corridor is a hard gate.',
            'note':'Relative screening only, not a safe-touchdown probability. Unassessed sites are not labelled dangerous. Different source resolutions can hide different hazards.'}
