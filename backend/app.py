from pathlib import Path
import csv,io,json,logging,threading
from functools import lru_cache
from fastapi import FastAPI,HTTPException,Query
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from .engine import timeline

BASE=Path(__file__).resolve().parents[1]
SITES=json.loads((BASE/'backend'/'sites.json').read_text(encoding='utf-8'))
app=FastAPI(title='Luna Scout API',version='1.0.0',description='Terrain-aware lunar scenario screening. All dates are UTC.')
COMPUTE_LOCK=threading.RLock()

@lru_cache(maxsize=12)
def cached(*args):
    with COMPUTE_LOCK: return timeline(*args)

@app.get('/api/sites')
def sites(): return SITES

@app.get('/api/health')
def health(): return {'status':'ok','engine':'SPICE + LOLA','date_range':'2000-01-01 through 2050-12-31','offline':True}

@app.get('/api/timeline')
def get_timeline(site:str|None=None,lat:float|None=Query(None,ge=-90,le=90),lon:float|None=Query(None,ge=-180,le=360),start:str='2026-12-01T00:00:00Z',days:float=Query(14,ge=1,le=60),step_min:int=Query(30,ge=5,le=120),height:float=Query(2,ge=0,le=100),mode:str=Query('adjusted',pattern='^(adjusted|fine)$'),earth_margin:float=Query(0,ge=0,le=10),area:float=Query(1,gt=0,le=1000),efficiency:float=Query(.28,gt=0,le=1),panel:str=Query('horizontal',pattern='^(horizontal|tracking)$'),radius_km:int=Query(120,ge=30,le=240)):
    selected=next((s for s in SITES if s['id']==site),None)
    if site and not selected: raise HTTPException(404,'Unknown curated site.')
    if selected: lat,lon=selected['lat'],selected['lon']
    if lat is None or lon is None: raise HTTPException(422,'Choose a site or supply both latitude and longitude.')
    if days*1440/step_min>18000: raise HTTPException(422,'Too many samples; shorten the interval or increase cadence.')
    try:
        result=cached(lat,lon,start,days,step_min,height,mode,earth_margin,area,efficiency,panel,radius_km)
        from .safety import terrain_metrics,rank_record
        limits=dict(slope_limit=10,roughness_limit=20,steep_limit=20,sun_min=20,earth_min=20,elevation_min=None,elevation_max=None)
        assessment=rank_record({'id':site or 'custom','name':selected['name'] if selected else 'Custom coordinate','lat':lat,'lon':lon},terrain_metrics(lat,lon),{'sun':{'fraction':result['sun_fraction'][0]},'earth':{'status':'CLEAR' if result['earth_visible'][0] else 'BLOCKED'}},result['summary'],limits)
        result={**result,'assessment':assessment,'assessment_limits':limits,'assessment_note':'Terrain screening always uses adjusted LOLA at a 1 km radius; solar/communication metrics use this scenario request. Default screening limits; change limits on the ranking page.'}
        return {**result,'site':{**result['site'],'name':selected['name'] if selected else 'Custom coordinate','note':selected['note'] if selected else 'User-specified coordinate; verify the reference frame and terrain resolution.'}}
    except ValueError as e: raise HTTPException(422,str(e))
    except Exception:
        logging.exception('Scenario calculation failed')
        raise HTTPException(503,'Calculation failed. Verify that all supplied terrain and SPICE files are present; consult the server log.')

@app.get('/api/celestial')
def get_celestial(start:str='2026-11-15T00:00:00Z',days:int=Query(120,ge=1,le=366),step_hours:int=Query(6,ge=3,le=24)):
    from .celestial import celestial
    try:
        with COMPUTE_LOCK: return celestial(start,days,step_hours)
    except ValueError as e: raise HTTPException(422,str(e))
    except Exception:
        logging.exception('Moon-relative ephemeris failed')
        raise HTTPException(503,'Sun and Earth geometry could not be loaded. See the server log.')

@app.get('/api/flight-status')
def get_flight_status(lat:float=Query(...,ge=-90,le=90),lon:float=Query(...,ge=-180,le=360),at:str='2026-11-15T00:00:00Z',altitude:float=Query(0,ge=0,le=800000)):
    from .flight_status import flight_status
    try:
        with COMPUTE_LOCK: return flight_status(lat,lon,at,altitude)
    except ValueError as e: raise HTTPException(422,str(e))
    except Exception:
        logging.exception('Spacecraft visibility failed')
        raise HTTPException(503,'Live visibility unavailable. Verify terrain and SPICE files; see server log.')

@app.get('/api/surface')
def get_surface(site:str|None=None,lat:float|None=Query(None,ge=-90,le=90),lon:float|None=Query(None,ge=-180,le=360)):
    from .surface import surface
    selected=next((s for s in SITES if s['id']==site),None)
    if site and not selected: raise HTTPException(404,'Unknown landing region.')
    if selected: lat,lon=selected['lat'],selected['lon']
    if lat is None or lon is None: raise HTTPException(422,'Choose a site or supply both coordinates.')
    try:
        with COMPUTE_LOCK: result=surface(float(lat),((float(lon)+180)%360)-180)
        return {**result,'name':selected['name'] if selected else 'Custom coordinate'}
    except ValueError as e: raise HTTPException(422,str(e))
    except Exception:
        logging.exception('Navigator terrain failed')
        raise HTTPException(503,'Terrain could not be loaded. See the server log.')

@app.get('/api/rank')
def rank(at:str='2026-11-15T00:00:00Z',days:int=Query(14,ge=1,le=30),slope_limit:float=Query(10,ge=1,le=30),roughness_limit:float=Query(20,ge=1,le=200),steep_limit:float=Query(20,ge=1,le=100),sun_min:float=Query(20,ge=0,le=100),earth_min:float=Query(20,ge=0,le=100),elevation_min:float|None=Query(None,ge=-30000,le=30000),elevation_max:float|None=Query(None,ge=-30000,le=30000)):
    from .safety import rank_sites
    if elevation_min is not None and elevation_max is not None and elevation_min>elevation_max: raise HTTPException(422,'Elevation minimum exceeds maximum.')
    try:
        with COMPUTE_LOCK: return rank_sites(SITES,at,days,slope_limit=slope_limit,roughness_limit=roughness_limit,steep_limit=steep_limit,sun_min=sun_min,earth_min=earth_min,elevation_min=elevation_min,elevation_max=elevation_max)
    except ValueError as e: raise HTTPException(422,str(e))
    except Exception:
        logging.exception('Safety screening failed')
        raise HTTPException(503,'Ranking failed. Verify terrain and SPICE data; see server log.')

@app.get('/api/south-pole')
def south_pole(at:str='2026-11-15T00:00:00Z',days:int=Query(14,ge=1,le=30),slope_limit:float=Query(10,ge=1,le=30),roughness_limit:float=Query(20,ge=1,le=200),steep_limit:float=Query(20,ge=1,le=100),sun_min:float=Query(20,ge=0,le=100),earth_min:float=Query(20,ge=0,le=100),elevation_min:float|None=Query(None,ge=-30000,le=30000),elevation_max:float|None=Query(None,ge=-30000,le=30000)):
    from .polar_survey import ranked_survey
    if elevation_min is not None and elevation_max is not None and elevation_min>elevation_max: raise HTTPException(422,'Elevation minimum exceeds maximum.')
    try:
        with COMPUTE_LOCK: return ranked_survey(SITES,at,days,slope_limit=slope_limit,roughness_limit=roughness_limit,steep_limit=steep_limit,sun_min=sun_min,earth_min=earth_min,elevation_min=elevation_min,elevation_max=elevation_max)
    except ValueError as e: raise HTTPException(422,str(e))
    except Exception:
        logging.exception('South-pole survey failed')
        raise HTTPException(503,'Polar survey failed. Check the server log.')

@app.get('/api/export.csv')
def export_csv(site:str,start:str='2026-12-01',days:float=Query(14,ge=1,le=60)):
    d=get_timeline(site=site,start=start,days=days,lat=None,lon=None,step_min=30,height=2,mode='adjusted',earth_margin=0,area=1,efficiency=.28,panel='horizontal',radius_km=120)
    stream=io.StringIO(); writer=csv.writer(stream)
    fields=['t','sun_az','sun_el','sun_horizon','earth_az','earth_el','earth_horizon','sun_fraction','sun_visible','earth_visible','earth_clearance','power_w']
    writer.writerow(fields); writer.writerows(zip(*(d[k] for k in fields)))
    return StreamingResponse(iter([stream.getvalue()]),media_type='text/csv',headers={'Content-Disposition':'attachment; filename="luna-scout-timeline.csv"'})

app.mount('/',StaticFiles(directory=BASE/'frontend',html=True),name='frontend')
