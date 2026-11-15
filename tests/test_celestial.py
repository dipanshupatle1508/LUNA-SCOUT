import numpy as np
from fastapi.testclient import TestClient
from backend.app import app
from backend.engine import sp,LOCK
client=TestClient(app)

def test_geometric_body_vectors_and_earth_orientation():
    r=client.get('/api/celestial',params={'start':'2026-11-15T00:00:00Z','days':2,'step_hours':6})
    assert r.status_code==200,r.text
    d=r.json();assert len(d['t'])==9
    for key in ['earth_km','sun_km']:
        assert np.array(d[key]).shape==(9,3)
        assert np.isfinite(d[key]).all()
    with LOCK:
        et=sp.str2et('2026-11-15T00:00:00')
        for name,key in [('EARTH','earth_km'),('SUN','sun_km')]:
            expected=sp.spkpos(name,et,'MOON_ME','NONE','MOON')[0]
            np.testing.assert_allclose(d[key][0],expected,atol=.001,rtol=0)
    for flat in d['earth_fixed_to_moon']:
        m=np.array(flat).reshape(3,3)
        np.testing.assert_allclose(m@m.T,np.eye(3),atol=2e-12)
        assert np.linalg.det(m)>0.999999

def test_body_motion_and_bounds():
    d=client.get('/api/celestial?start=2026-11-15&days=30&step_hours=24').json()
    assert not np.allclose(d['earth_km'][0],d['earth_km'][-1])
    assert not np.allclose(d['sun_km'][0],d['sun_km'][-1])
    assert 350000<np.linalg.norm(d['earth_km'][0])<420000
    for p in [{'start':'bad'},{'start':'1800-01-01'},{'start':'2050-12-31','days':10},{'days':500},{'step_hours':0}]:
        assert client.get('/api/celestial',params=p).status_code==422

def test_flight_assets():
    for path in ['/navigator.html','/js/flight.js','/js/flight-core.js','/js/moon-sky.js','/assets/earth-atmosphere.jpg']:
        assert client.get(path).status_code==200
    text=client.get('/navigator.html').text
    assert 'Fly to beacon' in text and 'Lift off' in text
    assert 'BEGIN EVA' not in text
