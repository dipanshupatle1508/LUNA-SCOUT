"""Reproducible geometric Sun/Earth timelines using supplied NAIF kernels."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import threading
import numpy as np
import spiceypy as sp
from .terrain import R,profile

KERNELS=Path(__file__).resolve().parents[1]/'data'/'kernels'
LOCK=threading.RLock()
for name in ['naif0012.tls.txt','pck00011.tpc.txt','de440s.bsp','moon_pa_de440_200625.bpc','moon_de440_250416.tf.txt']:
    sp.furnsh(str(KERNELS/name))


def basis(lat,lon):
    la,lo=np.radians([lat,lon])
    return np.array([[-np.sin(lo),np.cos(lo),0],[-np.sin(la)*np.cos(lo),-np.sin(la)*np.sin(lo),np.cos(la)],[np.cos(la)*np.cos(lo),np.cos(la)*np.sin(lo),np.sin(la)]])


def azel(vec,frame):
    enu=vec@frame.T; distance=np.linalg.norm(vec,axis=1)
    return np.degrees(np.arctan2(enu[:,0],enu[:,1]))%360,np.degrees(np.arcsin(np.clip(enu[:,2]/distance,-1,1))),distance


def disk_fraction(clearance,radius):
    """Area above a straight skyline as fraction of an extended uniform disc."""
    x=np.clip(np.asarray(clearance)/radius,-1,1)
    return (np.arccos(-x)+x*np.sqrt(1-x*x))/np.pi


def overlap_fraction(r,Rb,d):
    """Fraction of Sun disk occulted by Earth; small-angle planar circles."""
    r,Rb,d=np.broadcast_arrays(r,Rb,d); result=np.zeros(r.shape)
    inside=d<=np.abs(Rb-r)
    result[inside]=np.minimum(1,(Rb[inside]/r[inside])**2)
    part=(d<r+Rb)&~inside
    a,b,c=r[part],Rb[part],d[part]
    if a.size:
        area=a*a*np.arccos(np.clip((c*c+a*a-b*b)/(2*c*a),-1,1))+b*b*np.arccos(np.clip((c*c+b*b-a*a)/(2*c*b),-1,1))-.5*np.sqrt(np.maximum(0,(-c+a+b)*(c+a-b)*(c-a+b)*(c+a+b)))
        result[part]=area/(np.pi*a*a)
    return result


def windows(t,clearance):
    """Linearly interpolate sampled signed-clearance crossings; clipped to span."""
    good=np.asarray(clearance)>0; result=[]; begin=float(t[0]) if good[0] else None
    for i in range(len(t)-1):
        if good[i]==good[i+1]: continue
        cross=float(t[i]+(t[i+1]-t[i])*(-clearance[i])/(clearance[i+1]-clearance[i]))
        if good[i]: result.append((begin,cross)); begin=None
        else: begin=cross
    if good[-1]: result.append((begin,float(t[-1])))
    return result


def iso(seconds): return datetime.fromtimestamp(float(seconds),timezone.utc).isoformat().replace('+00:00','Z')
def rounded(a): return np.round(a,5).tolist()


def timeline(lat,lon,start,days=14,step_min=30,height=2,mode='adjusted',earth_margin=0,area=1,efficiency=.28,panel='horizontal',radius_km=120):
    dt=datetime.fromisoformat(start.replace('Z','+00:00'))
    if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
    dt=dt.astimezone(timezone.utc); end=dt+timedelta(days=days)
    if dt<datetime(2000,1,1,tzinfo=timezone.utc) or end>datetime(2051,1,1,tzinfo=timezone.utc):
        raise ValueError('Choose a complete mission interval within 2000–2050 UTC.')
    lat=float(lat);lon=((float(lon)+180)%360)-180
    with LOCK:
        hz=profile(lat,lon,float(height),mode,int(radius_km))
        seconds=np.r_[np.arange(0,days*86400,step_min*60,dtype=float),days*86400]
        ets=sp.str2et(dt.strftime('%Y-%m-%dT%H:%M:%S.%f'))+seconds
        t=dt.timestamp()+seconds; frame=basis(lat,lon)
        site=frame[2]*(R+hz['ground_m']+height)/1000
        vectors={name:np.array(sp.spkpos(name,ets,'MOON_ME','NONE','MOON')[0])-site for name in ['SUN','EARTH']}
    saz,sel,srange=azel(vectors['SUN'],frame); eaz,eel,erange=azel(vectors['EARTH'],frame)
    sh=np.interp(saz,hz['az'],hz['el'],period=360); eh=np.interp(eaz,hz['az'],hz['el'],period=360)
    sr=np.degrees(np.arcsin(695700/srange)); er=np.degrees(np.arcsin(6378.137/erange))
    sf=disk_fraction(sel-sh,sr)
    sep=np.degrees(np.arccos(np.clip(np.sum(vectors['SUN']*vectors['EARTH'],axis=1)/(srange*erange),-1,1)))
    eclipse=1-overlap_fraction(sr,er,sep)
    light=sf*eclipse
    # Sun upper limb; Earth entire disk and user-defined angular clearance.
    sun_clear=np.minimum(sel-sh+sr,np.where(eclipse>1e-8,90.,-1.))
    earth_clear=eel-eh-er-earth_margin
    sw=windows(t,sun_clear); ew=windows(t,earth_clear)
    dark=windows(t,-sun_clear); outages=windows(t,-earth_clear)
    joint=windows(t,np.minimum(sun_clear,earth_clear))
    incidence=np.ones(len(t)) if panel=='tracking' else np.maximum(0,np.sin(np.radians(sel)))
    power=1361*(149597870.7/srange)**2*area*efficiency*incidence*light
    integrate = np.trapezoid if hasattr(np, 'trapezoid') else np.trapz
    def duration(w): return round(sum(b-a for a,b in w)/3600,3)
    def longest(w): return round(max((b-a for a,b in w),default=0)/3600,3)
    def winjson(w): return [{'start':iso(a),'end':iso(b),'hours':round((b-a)/3600,3),'clipped_start':bool(abs(a-t[0])<.01),'clipped_end':bool(abs(b-t[-1])<.01)} for a,b in w]
    def next_set(w):
        if not w or w[0][0]>t[0]+.01: return None
        return None if abs(w[0][1]-t[-1])<.01 else round((w[0][1]-t[0])/3600,3)
    return {'site':{'lat':lat,'lon':lon},'t':[iso(x) for x in t],
      'sun_el':rounded(sel),'sun_az':rounded(saz),'earth_el':rounded(eel),'earth_az':rounded(eaz),
      'sun_horizon':rounded(sh),'earth_horizon':rounded(eh),'sun_fraction':rounded(light),'earth_clearance':rounded(earth_clear),
      'sun_visible':(sun_clear>0).tolist(),'earth_visible':(earth_clear>0).tolist(),'power_w':rounded(power),'eclipse_fraction':rounded(1-eclipse),
      'horizon':hz,'sun_windows':winjson(sw),'earth_windows':winjson(ew),'joint_windows':winjson(joint),
      'summary':{'terrain_aware':True,'sunlit_hours':duration(sw),'earth_hours':duration(ew),'joint_hours':duration(joint),'longest_dark_hours':longest(dark),'longest_outage_hours':longest(outages),'max_sun_el':round(float(sel.max()),3),'energy_wh':round(float(integrate(power,seconds))/3600,3),'peak_power_w':round(float(power.max()),3),'sunset_in_hours':next_set(sw),'earthset_in_hours':next_set(ew),'sunlit_percent':round(duration(sw)/(days*24)*100,2),'earth_percent':round(duration(ew)/(days*24)*100,2)},
      'method':{'frame':'MOON_ME (DE440_ME421)','ephemeris':'DE440s','orientation':'DE440 binary PCK','correction':'NONE: simultaneous geometric positions','azimuth':'clockwise from local north; east-positive longitude','radius_m':R,'height_m':height,'step_min':step_min,'terrain_mode':mode,'horizon_azimuth_step_deg':1,'radial_step':'source spacing to 10 km, 160 m farther out (minimum 20 m)','earth_criterion':'full disk above skyline plus margin','earth_margin_deg':earth_margin,'sun_criterion':'any direct Sun disk visible, excluding full Earth occultation','panel':panel,'panel_area_m2':area,'panel_efficiency':efficiency,'warnings':['Prototype screening, not flight-qualified mission analysis.','Geometric visibility does not include DSN scheduling, station location, antenna limits or link budget.','Horizon limited to requested radius; sub-pixel obstacles and distant terrain can be missed.','Crossings interpolated between samples; short events may be missed.','Terrain data versions can create seams in fallback regions.','Uniform disks, straight local skyline and approximate eclipse overlap; no refraction, diffuse light, thermal or battery model.']}}
