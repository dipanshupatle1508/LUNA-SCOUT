import numpy as np
import pytest
from fastapi.testclient import TestClient
from backend.app import app,SITES
from backend.safety import summarize_grid,terrain_metrics,rank_record,sort_records
from backend.polar_survey import survey
from backend.terrain import R
client=TestClient(app)
LIMITS=dict(slope_limit=10,roughness_limit=20,steep_limit=20,sun_min=20,earth_min=20,elevation_min=None,elevation_max=None)

def test_horn_plane_and_detrended_roughness():
    axis=np.arange(-15,16)*80.;x,y=np.meshgrid(axis,axis)
    d=summarize_grid(100+.1*x+.2*y,80,1000,10)
    assert d['slope_p95_deg']==pytest.approx(np.degrees(np.arctan(np.hypot(.1,.2))))
    assert d['roughness_m']<1e-10
    assert d['steep_percent']==100
    rough=summarize_grid(100+.1*x+.2*y+.00005*(x*x+y*y),80,1000,10)
    assert rough['roughness_m']>10


def fake(t=None):
    terrain=dict(assessed=True,elevation_m=100,slope_p95_deg=2,roughness_m=2,steep_percent=0)
    if t:terrain.update(t)
    return rank_record(dict(id='a',name='A'),terrain,{'sun':{'fraction':1},'earth':{'status':'CLEAR'}},{'sunlit_percent':90,'earth_percent':90},LIMITS)


def test_gate_priority_and_monotonic_terrain_score():
    good=fake();bad=fake({'slope_p95_deg':15});bad['id']='b'
    assert good['score']>bad['score']
    bad['score']=100
    unknown={'id':'c','score':None,'category':'UNASSESSED'}
    assert [r['id'] for r in sort_records([bad,unknown,good])]==['a','b','c']
    assert unknown['rank'] is None


def test_elevation_not_automatically_safer():
    assert fake({'elevation_m':-6000})['score']==fake({'elevation_m':6000})['score']
    args=dict(LIMITS,elevation_max=0)
    d=rank_record({'id':'a'},dict(assessed=True,elevation_m=100,slope_p95_deg=2,roughness_m=2,steep_percent=0),{'sun':{'fraction':1},'earth':{'status':'CLEAR'}},{'sunlit_percent':100,'earth_percent':100},args)
    assert 'Above mission elevation corridor' in d['violations']


def test_coarse_apollo_is_unknown_not_safe_or_dangerous():
    s=next(s for s in SITES if s['id']=='apollo11');d=terrain_metrics(s['lat'],s['lon'])
    assert not d['assessed']
    assert d['resolution_m']>1000


def test_cap_sampling_bounds_and_separation():
    s=survey();assert s['sample_count']>11000
    assert len(s['candidates'])==12
    for p in s['candidates']:assert -90<=p['lat']<=-80
    from backend.terrain import destination
    from backend.safety import terrain_metrics
    for a in s['candidates']:
        for b in s['candidates']:
            if a==b:continue
            la,lb,dl=np.radians([a['lat'],b['lat'],a['lon']-b['lon']]);q=np.sin((la-lb)/2)**2+np.cos(la)*np.cos(lb)*np.sin(dl/2)**2
            assert 2*R*np.arcsin(np.sqrt(q))>19500


def test_rank_api_and_date_inputs():
    response=client.get('/api/rank',params={'at':'2026-11-15T00:00:00Z','days':3});assert response.status_code==200
    d=response.json();assert len(d['records'])==6
    assert d['records'][-1]['id']=='apollo11'
    assert d['records'][-1]['category']=='UNASSESSED'
    assert sum(d['weights'].values())==100
    for r in d['records']:
        assert r['instant']['t']=='2026-11-15T00:00:00Z'
        assert r['terrain']['elevation_m'] is not None
    for change in [{'at':'bad'},{'at':'2099-01-01'},{'slope_limit':0},{'days':31},{'elevation_min':10,'elevation_max':-10}]:
        assert client.get('/api/rank',params=change).status_code==422


def test_images_and_ranking_served():
    for path in ['ranking.html','js/ranking.js','css/ranking.css','assets/south-pole-pia13523.jpg','assets/south-pole-oblique.png','assets/south-pole-nadir.png']:
        assert client.get('/'+path).status_code==200
    assert 'assessment' in client.get('/api/timeline',params={'site':'shackleton','start':'2026-11-15','days':1,'step_min':120}).json()


def test_date_aware_coarse_sky_shortlist():
    from backend.polar_survey import date_shortlist
    candidates,counts=date_shortlist('2026-11-15T00:00:00Z')
    assert len(candidates)==12
    assert 0<counts['coarse_joint_nodes']<=counts['coarse_earth_clear_nodes']<survey()['sample_count']
    assert counts['coarse_joint_nodes']<=counts['coarse_sun_visible_nodes']
    assert len({c['id'] for c in candidates})==12
    assert sorted(row[7] for row in counts['cells'])==list(range(1,survey()['sample_count']+1))
    assert all(isinstance(row[5],bool) and isinstance(row[6],bool) for row in counts['cells'])
    for c in candidates:assert -90<=c['lat']<=-80


def test_exact_pole_geodesic_rays():
    from backend.terrain import destination
    az=np.radians([0,90,180,270])
    lat,lon=destination(-90,0,az,1000)
    assert np.allclose(lat,-90+np.degrees(1000/R))
    assert np.allclose(lon%360,[0,90,180,270])
    lat,lon=destination(90,0,az,1000)
    assert np.allclose(lon%360,[180,90,0,270])
