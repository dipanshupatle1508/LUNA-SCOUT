"""A cap-wide 5 km sampling lattice; terrain shortlist is explicitly non-exhaustive."""
from functools import lru_cache
import numpy as np
from .terrain import R, sample, destination
from .safety import terrain_metrics, rank_sites

@lru_cache(maxsize=1)
def survey():
    step=5000.;radius=R*np.radians(10);axis=np.arange(-300000,300001,step);x,y=np.meshgrid(axis,axis);distance=np.hypot(x,y);inside=distance<=radius
    lat=-90+np.degrees(distance/R);lon=np.degrees(np.arctan2(x,-y));lat=lat[inside];lon=lon[inside];xs=x[inside];ys=y[inside]
    spacing=80.;patch=[]
    for dy in [-spacing,0,spacing]:
        for dx in [-spacing,0,spacing]:
            la,lo=destination(lat,lon,np.arctan2(np.full_like(lat,dx),np.full_like(lat,-dy)),np.full_like(lat,np.hypot(dx,dy)))
            patch.append(sample(la,lo))
    h=np.array(patch).reshape(3,3,-1);gx=((h[0,2]+2*h[1,2]+h[2,2])-(h[0,0]+2*h[1,0]+h[2,0]))/(8*spacing);gy=((h[2,0]+2*h[2,1]+h[2,2])-(h[0,0]+2*h[0,1]+h[0,2]))/(8*spacing)
    slope=np.degrees(np.arctan(np.hypot(gx,gy)))
    # Local 3x3 residual roughness is a survey proxy, NOT the ranked 2 km-patch RMS.
    coords=np.array([(dx,dy,1.) for dy in [-spacing,0,spacing] for dx in [-spacing,0,spacing]])
    residual=h.reshape(9,-1)-coords@np.linalg.lstsq(coords,h.reshape(9,-1),rcond=None)[0];rough=np.sqrt(np.mean(residual**2,axis=0))
    priority=slope/10+rough/5;chosen=[]
    for i in np.argsort(priority):
        if all((xs[i]-xs[j])**2+(ys[i]-ys[j])**2>=20000**2 for j in chosen):chosen.append(int(i))
        if len(chosen)==12:break
    candidates=[{'id':'survey-'+str(i),'name':'Survey candidate '+str(n+1),'lat':float(lat[i]),'lon':float(lon[i]),'kind':'survey','note':'Automatically terrain-shortlisted reference point; not an approved landing site.'} for n,i in enumerate(chosen)]
    return {'south_lat':-90,'north_lat':-80,'step_m':step,'width':len(axis),'extent_m':300000,'sample_count':len(lat),
            'cells':[[int(round(a/step+60)),int(round(b/step+60)),round(float(e),1),round(float(s),2),round(float(r),2)] for a,b,e,s,r in zip(xs,ys,h[1,1],slope,rough)],
            'candidates':candidates,'note':'80°S–90°S sampled every 5 km, not every metre. Map slope uses 80 m-baseline Horn gradients at lattice nodes. Twelve spatially separated low-slope/low-roughness nodes are shortlisted before date-dependent mission ranking; other nodes have not received full visibility analysis.'}


@lru_cache(maxsize=4)
def date_shortlist(at):
    from .engine import sp,LOCK
    from datetime import datetime,timezone
    dt=datetime.fromisoformat(at.replace('Z','+00:00'))
    if dt.tzinfo is None:dt=dt.replace(tzinfo=timezone.utc)
    dt=dt.astimezone(timezone.utc)
    if not datetime(2000,1,1,tzinfo=timezone.utc)<=dt<datetime(2051,1,1,tzinfo=timezone.utc):raise ValueError('Choose a time within 2000–2050 UTC.')
    s=survey();cells=np.array(s['cells']);x=(cells[:,0]-60)*5000;y=(cells[:,1]-60)*5000
    lat=-90+np.degrees(np.hypot(x,y)/R);lon=np.degrees(np.arctan2(x,-y));la,lo=np.radians(lat),np.radians(lon)
    up=np.c_[np.cos(la)*np.cos(lo),np.cos(la)*np.sin(lo),np.sin(la)]
    north=np.c_[-np.sin(la)*np.cos(lo),-np.sin(la)*np.sin(lo),np.cos(la)]
    east=np.c_[-np.sin(lo),np.cos(lo),np.zeros_like(lo)];observer=up*((R+cells[:,2]+2)/1000)[:,None]
    visible={}
    with LOCK:
        et=sp.str2et(dt.strftime('%Y-%m-%dT%H:%M:%S.%f'))
        centers={body:np.array(sp.spkpos(body,et,'MOON_ME','NONE','MOON')[0]) for body in ['SUN','EARTH']}
    distances=np.r_[80,160,320,640,1280,2560,5000,np.arange(10000,120001,4000),120000]
    theta=distances/R
    for body,center in centers.items():
        v=center-observer;ranges=np.linalg.norm(v,axis=1);el=np.degrees(np.arcsin(np.sum(v*up,axis=1)/ranges));az=np.arctan2(np.sum(v*east,axis=1),np.sum(v*north,axis=1));horizon=np.empty(len(lat))
        for begin in range(0,len(lat),512):
            end=min(len(lat),begin+512)
            raylat,raylon=destination(lat[begin:end,None],lon[begin:end,None],az[begin:end,None],distances[None,:])
            heights=sample(raylat,raylon)
            angle=np.degrees(np.arctan2((R+heights)*np.cos(theta)-(R+cells[begin:end,2,None]+2),(R+heights)*np.sin(theta)))
            horizon[begin:end]=angle.max(axis=1)
        angular=np.degrees(np.arcsin((695700 if body=='SUN' else 6378.137)/ranges))
        visible[body]=el-horizon+(angular if body=='SUN' else -angular)>0
    priority=cells[:,3]/10+cells[:,4]/5+4*(~visible['EARTH'])+2*(~visible['SUN'])
    chosen=[]
    for j in np.argsort(priority):
        if all((x[j]-x[k])**2+(y[j]-y[k])**2>=20000**2 for k in chosen):chosen.append(int(j))
        if len(chosen)==12:break
    candidates=[{'id':'survey-'+str(j),'name':'Survey candidate '+str(n+1),'lat':float(lat[j]),'lon':float(lon[j]),'kind':'survey','note':'Date-aware coarse terrain/sky shortlist; not an approved landing site.'} for n,j in enumerate(chosen)]
    order=np.argsort(priority);ranks=np.empty(len(priority),int);ranks[order]=np.arange(1,len(priority)+1)
    annotated=[[*row,bool(visible['SUN'][i]),bool(visible['EARTH'][i]),int(ranks[i])] for i,row in enumerate(s['cells'])]
    return candidates,{'cells':annotated,'coarse_sun_visible_nodes':int(visible['SUN'].sum()),'coarse_earth_clear_nodes':int(visible['EARTH'].sum()),'coarse_joint_nodes':int((visible['SUN']&visible['EARTH']).sum())}


def ranked_survey(sites,at,days,**limits):
    candidates,counts=date_shortlist(at)
    result=rank_sites(candidates+sites,at,days,**limits)
    overview={**survey(),'candidates':candidates,**counts,'cells_columns':['column','row','elevation_m','slope_deg_80m_baseline','roughness_proxy_m','coarse_sun_visible','coarse_earth_full_clear','coarse_priority_rank'],'note':'80°S–90°S sampled every 5 km. Source-scale terrain derivatives plus coarse date-dependent Sun/Earth terrain-ray checks select twelve separated candidates. Coarse rays use 80 m–4 km radial steps to 120 km and can miss ridges/eclipses; selected candidates receive the full dense horizon and mission-window analysis.'}
    return {**result,'survey':overview,'shortlist_note':'Ranking covers twelve date-aware coarse-survey candidates and six comparison sites. It is not an exhaustive safest-point search or a metre-scale hazard map.'}
