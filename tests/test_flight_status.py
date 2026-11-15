import numpy as np
import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.flight_status import flight_status, ray_horizon
from backend.terrain import R
from backend.engine import timeline

client = TestClient(app)


def test_altitude_changes_earth_visibility():
    ground = flight_status(-89.489, -137.8675, '2026-11-15T00:00:00Z', 0)
    flying = flight_status(-89.489, -137.8675, '2026-11-15T00:00:00Z', 60000)
    assert ground['earth']['status'] == 'BLOCKED'
    assert flying['earth']['status'] == 'CLEAR'
    assert flying['earth']['horizon'] < ground['earth']['horizon']
    assert flying['sun']['fraction'] >= ground['sun']['fraction']
    assert ground['observer_height_m'] == 2


def test_ground_angles_agree_with_planner():
    d = flight_status(-89.489, -137.8675, '2026-11-15T00:00:00Z', 0)
    p = timeline(-89.489, -137.8675, '2026-11-15T00:00:00Z', days=1, step_min=120)
    for body in ['sun', 'earth']:
        assert d[body]['el'] == pytest.approx(p[body+'_el'][0], abs=1e-5)
        assert d[body]['az'] == pytest.approx(p[body+'_az'][0], abs=1e-5)
        # Direct ray sampling differs slightly from the planner's 1-degree azimuth interpolation.
        assert d[body]['horizon'] == pytest.approx(p[body+'_horizon'][0], abs=.15)


def test_spherical_limb_at_flight_altitude(monkeypatch):
    import backend.flight_status as module
    monkeypatch.setattr(module, 'sample', lambda lat, lon: np.zeros(np.broadcast(lat, lon).shape))
    actual = ray_horizon(0, 0, 0, 60000, 30, 80)
    expected = -np.degrees(np.arccos(R/(R+60000)))
    assert actual == pytest.approx(expected, abs=.0001)


def test_status_changes_with_position_and_time():
    a = flight_status(0.67416, 23.47314, '2026-11-15T00:00:00Z', 0)
    b = flight_status(0.67416, 23.47314, '2026-11-29T00:00:00Z', 0)
    assert abs((a['sun']['az']-b['sun']['az']+180)%360-180) > 120
    assert abs(a['earth']['phase']-b['earth']['phase']) > .2
    for d in [a, b]:
        assert 0 <= d['sun']['fraction'] <= 1
        assert 0 <= d['earth']['fraction'] <= 1
        assert 0 <= d['earth']['phase'] <= 1


def test_status_api_and_validation():
    r = client.get('/api/flight-status', params={'lat':-89.489, 'lon':-137.8675, 'altitude':60000})
    assert r.status_code == 200
    assert r.json()['altitude_m'] == 60000
    for change in [{'lat':91}, {'altitude':-1}, {'altitude':800001}, {'at':'2099-01-01'}, {'at':'invalid'}]:
        assert client.get('/api/flight-status', params={'lat':0,'lon':0, **change}).status_code == 422


def test_texture_and_telemetry_assets_served():
    for path in ['js/flight-telemetry.js','js/landing-terrain.js','assets/apollo11-undisturbed-soil.png']:
        assert client.get('/'+path).status_code == 200
    html = client.get('/navigator.html').text
    assert 'Live illumination and direct-to-Earth status' in html
    assert 'terrain-credit' in html
