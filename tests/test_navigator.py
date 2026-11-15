import numpy as np
import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.terrain import sample
client=TestClient(app)

@pytest.mark.parametrize('site',['shackleton','connecting-ridge','malapert','mons-mouton','chandrayaan3','apollo11'])
def test_each_marker_has_its_own_terrain(site):
    catalogue={s['id']:s for s in client.get('/api/sites').json()}
    s=catalogue[site]
    r=client.get('/api/surface',params={'site':site})
    assert r.status_code==200,r.text
    d=r.json();assert d['lat']==s['lat'] and d['lon']==pytest.approx(s['lon'])
    n=d['near']['size'];h=d['near']['height_m']
    assert len(h)==n*n and np.isfinite(h).all()
    assert h[(n//2)*n+n//2]==pytest.approx(float(sample(s['lat'],s['lon'])),abs=.001)
    if site=='apollo11':assert d['lat']>0 and d['resolution_m']>1000
    if site=='chandrayaan3':assert -70<d['lat']<-69

def test_real_feature_catalogue_and_touchdowns():
    sites=client.get('/api/sites').json()
    assert len(sites)==6
    assert sum(s['kind']=='touchdown' for s in sites)==2
    assert all(s.get('source','').startswith('https://') for s in sites)
    assert next(s for s in sites if s['id']=='mons-mouton')['lat']==-84.6

def test_navigator_assets_and_bad_requests():
    for path in ['/navigator.html','/module.html','/js/lunar-module.js','/js/moon-globe.js','/assets/moon-lroc-2k.jpg','/vendor/three.min.js']:
        assert client.get(path).status_code==200
    assert client.get('/api/surface?site=missing').status_code==404
    assert client.get('/api/surface?lat=-100&lon=0').status_code==422
    assert client.get('/api/surface').status_code==422
