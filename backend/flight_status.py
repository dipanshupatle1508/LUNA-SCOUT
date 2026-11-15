"""Instant spacecraft visibility: exact SPICE geometry and two sampled LOLA rays."""
from datetime import datetime, timezone
import numpy as np
from .engine import sp, LOCK, basis, azel, disk_fraction, overlap_fraction, iso
from .terrain import R, sample, destination, layers, load


def ray_horizon(lat, lon, ground, height, az, resolution):
    # Include the spherical limb at flight altitude, plus nearby/distant terrain.
    distance = min(2400000, max(120000, R*np.arccos(R/(R+height))+120000))
    near = max(20, resolution)
    d = np.unique(np.r_[np.arange(near, 10000, near),
                         np.arange(10000, 120001, max(160, resolution)),
                         np.arange(120000, distance, 2000), distance])
    la, lo = destination(lat, lon, np.radians(az), d)
    terrain = sample(la, lo)
    if not np.isfinite(terrain).all():
        raise ValueError('Incomplete terrain on the visibility ray.')
    theta = d/R
    angles = np.degrees(np.arctan2((R+terrain)*np.cos(theta)-(R+ground+height),
                                   (R+terrain)*np.sin(theta)))
    return float(angles.max())


def flight_status(lat, lon, at, altitude=0):
    dt = datetime.fromisoformat(at.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    if not datetime(2000, 1, 1, tzinfo=timezone.utc) <= dt < datetime(2051, 1, 1, tzinfo=timezone.utc):
        raise ValueError('Choose a time within 2000–2050 UTC.')
    lon = (lon+180)%360-180
    ground = float(sample(lat, lon))
    if not np.isfinite(ground):
        raise ValueError('No valid terrain at the spacecraft coordinate.')
    resolution = next(load(n)[4] for n, limit in layers('adjusted') if lat <= limit)
    height = float(altitude)+2.0  # landed antenna / illumination reference, 2 m AGL
    frame = basis(lat, lon)
    observer = frame[2]*(R+ground+height)/1000
    with LOCK:
        et = sp.str2et(dt.strftime('%Y-%m-%dT%H:%M:%S.%f'))
        sun_c = np.array(sp.spkpos('SUN', et, 'MOON_ME', 'NONE', 'MOON')[0])
        earth_c = np.array(sp.spkpos('EARTH', et, 'MOON_ME', 'NONE', 'MOON')[0])
    sun, earth = sun_c-observer, earth_c-observer
    saz, sel, sr = (float(x[0]) for x in azel(sun[None, :], frame))
    eaz, eel, er = (float(x[0]) for x in azel(earth[None, :], frame))
    sh = ray_horizon(lat, lon, ground, height, saz, resolution)
    eh = ray_horizon(lat, lon, ground, height, eaz, resolution)
    sun_radius = np.degrees(np.arcsin(695700/sr))
    earth_radius = np.degrees(np.arcsin(6378.137/er))
    sep = np.degrees(np.arccos(np.clip(np.dot(sun, earth)/(sr*er), -1, 1)))
    eclipse = float(overlap_fraction(np.array([sun_radius]), np.array([earth_radius]), np.array([sep]))[0])
    light = float(disk_fraction(sel-sh, sun_radius))*(1-eclipse)
    earth_fraction = float(disk_fraction(eel-eh, earth_radius))
    earth_clearance = eel-eh-earth_radius
    es, eo = sun_c-earth_c, observer-earth_c
    earth_phase = .5*(1+np.clip(np.dot(es, eo)/(np.linalg.norm(es)*np.linalg.norm(eo)), -1, 1))
    return {'t': iso(dt.timestamp()), 'lat': lat, 'lon': lon,
            'altitude_m': altitude, 'observer_height_m': height, 'ground_m': ground,
            'resolution_m': resolution,
            'sun': {'az': saz, 'el': sel, 'horizon': sh, 'fraction': light,
                    'status': 'SHADOWED' if light <= 1e-6 else 'PARTLY SUNLIT' if light < .999 else 'SUNLIT'},
            'earth': {'az': eaz, 'el': eel, 'horizon': eh, 'fraction': earth_fraction,
                      'phase': float(earth_phase), 'clearance': earth_clearance,
                      'status': 'CLEAR' if earth_clearance > 0 else 'PARTIAL / BLOCKED' if earth_fraction > 0 else 'BLOCKED'},
            'method': 'Geometric SPICE at observer position; two directed LOLA skyline rays, spherical limb, Sun/Earth disks, approximate Earth occultation of Sun; no refraction.',
            'note': 'Direct-to-Earth CLEAR requires the full Earth disk above sampled terrain; geometric visibility only, not a radio link budget. Sub-grid obstacles omitted. Landed reference is 2 m AGL.'}
