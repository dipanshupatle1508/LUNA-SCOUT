import numpy as np
import pytest
from backend import terrain
from backend.engine import basis,azel,disk_fraction,overlap_fraction,windows,timeline

def test_local_frame_is_orthonormal_even_at_poles():
    for la,lo in [(-90,0),(-89.9,120),(0,0),(90,-130)]:
        f=basis(la,lo)
        np.testing.assert_allclose(f@f.T,np.eye(3),atol=1e-14)
        az,el,_=azel(np.array([f[0],f[1],f[2]])*1000,f)
        np.testing.assert_allclose(el,[0,0,90],atol=1e-6)
        np.testing.assert_allclose((az[:2]-[90,0]+180)%360-180,[0,0],atol=1e-6)

def test_disc_and_eclipse_limits():
    np.testing.assert_allclose(disk_fraction(np.array([-1,0,1]),1),[0,.5,1])
    np.testing.assert_allclose(overlap_fraction(np.array([1,1,1]),np.array([2,2,2]),np.array([0,5,2])),[1,0,.44660992],rtol=1e-6)

def test_crossings_and_interval_clipping():
    assert windows(np.array([0,3600,7200]),np.array([-1,1,-1]))==[(1800,5400)]
    assert windows(np.array([0,3600]),np.array([1,1]))==[(0,3600)]
    assert windows(np.array([0,3600]),np.array([-1,-1]))==[]

def test_spherical_horizon_has_expected_observer_dip(monkeypatch):
    monkeypatch.setattr(terrain,'sample',lambda lat,lon,mode='adjusted':np.zeros(np.broadcast(np.asarray(lat),np.asarray(lon)).shape))
    monkeypatch.setattr(terrain,'load',lambda name:(None,None,None,None,80))
    terrain.profile.cache_clear()
    h=terrain.profile(-90.,0.,2.,'adjusted',120)
    dip=-np.degrees(np.arccos(terrain.R/(terrain.R+2)))
    np.testing.assert_allclose(h['el'],dip,atol=.002)
    terrain.profile.cache_clear()

@pytest.mark.parametrize('mode',['adjusted','fine'])
def test_real_data_timeline_and_power(mode):
    d=timeline(-89.9,0,'2026-12-01',days=1,step_min=60,mode=mode)
    assert len(d['t'])==25
    assert d['t'][0]=='2026-12-01T00:00:00Z' and d['t'][-1]=='2026-12-02T00:00:00Z'
    for k in ['sunlit_hours','earth_hours','joint_hours','longest_dark_hours','longest_outage_hours']:
        assert 0<=d['summary'][k]<=24
    assert d['summary']['joint_hours']<=min(d['summary']['sunlit_hours'],d['summary']['earth_hours'])+.001
    assert all(0<=v<=1 for v in d['sun_fraction'])
    assert all(-90<=v<=90 for v in d['sun_el'])
    assert len(d['horizon']['el'])==360
    assert d['summary']['peak_power_w']>=0
    assert d['horizon']['resolution_m']==(80 if mode=='adjusted' else 20)

def test_input_and_hardware_scaling():
    with pytest.raises(ValueError):timeline(-89,0,'1800-01-01',1)
    with pytest.raises(ValueError):timeline(-89,0,'2050-12-31',2)
    a=timeline(-89.9,0,'2026-12-01',1,120,area=1)
    b=timeline(-89.9,0,'2026-12-01',1,120,area=2)
    np.testing.assert_allclose(b['power_w'],np.array(a['power_w'])*2,atol=1e-5)

def test_geometric_vectors_match_surface_observer_api():
    import spiceypy as sp
    from backend.engine import R
    f=basis(-85.9,0);h=float(terrain.sample(-85.9,0));site=f[2]*(R+h+2)/1000
    et=sp.str2et('2026-12-01T00:00:00')
    for body in ['SUN','EARTH']:
        expected=sp.spkcpo(body,et,'MOON_ME','OBSERVER','NONE',site,'MOON','MOON_ME')[0][:3]
        calculated=sp.spkpos(body,et,'MOON_ME','NONE','MOON')[0]-site
        np.testing.assert_allclose(calculated,expected,atol=1e-6)
