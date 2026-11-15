from fastapi.testclient import TestClient
from backend.app import app
client=TestClient(app)

def test_frontend_and_health():
    assert client.get('/').status_code==200
    assert 'Luna Scout' in client.get('/').text
    assert client.get('/api/health').json()['status']=='ok'
    assert len(client.get('/api/sites').json())>=6
    assert client.get('/assets/south-pole.png').status_code==200


def test_valid_custom_and_curated():
    for q in [dict(site='shackleton'),dict(lat=-69.373,lon=32.319)]:
        r=client.get('/api/timeline',params={**q,'start':'2026-12-01','days':1,'step_min':60})
        assert r.status_code==200,r.text
        assert len(r.json()['t'])==25


def test_invalid_scenarios_are_actionable():
    for q,code in [({'site':'missing'},404),({'lat':-95,'lon':0},422),({'lat':0},422),({'site':'apollo11','start':'bad'},422),({'site':'apollo11','start':'2050-12-31','days':5},422),({'site':'apollo11','mode':'fake'},422)]:
        r=client.get('/api/timeline',params=q)
        assert r.status_code==code,r.text
        assert 'detail' in r.json()


def test_csv_export():
    r=client.get('/api/export.csv?site=shackleton&start=2026-12-01&days=1')
    assert r.status_code==200 and r.text.startswith('t,sun_az,sun_el')
    assert len(r.text.splitlines())==50
