"""
Can a lunar landing site transmit to Earth?

For each site and time step it checks:
  1. Earth is above the local terrain horizon (SPICE Earth direction + LOLA DEM horizon)
  2. At least one DSN complex can see the Moon (optional, needs DSN kernels)

Geometry only: no link budget, antenna pointing limits or power.

Install:  pip install spiceypy numpy pyproj rasterio
"""
from pathlib import Path

import numpy as np
import spiceypy as sp
from pyproj import CRS, Transformer

# ---------------- CONFIG: edit these ----------------
KERNEL_DIR = Path("kernels")                  # folder with your downloaded SPICE files
DEM_PATH = "LDEM_80S_80MPP_ADJ.TIF"           # or "LDEM_16.IMG" for a global (coarse) check
SITES = {                                     # name: (latitude deg, longitude deg east)
    "Site A": (-89.5, 0.0),
    "Site B": (-85.0, 30.0),
}
START = "2026-12-01"                          # UTC
DAYS = 30
STEP_MIN = 30
EARTH_MARGIN_DEG = 1.0     # clearance over the horizon (Earth disk is ~1 deg wide)
DSN_MIN_EL_DEG = 10.0      # lowest Moon elevation a DSN antenna will track
HORIZON_RANGE_KM = 60      # how far out to look for blocking terrain
# -----------------------------------------------------

R_MOON = 1737400.0
BASE = ["naif0012.tls", "de440s.bsp", "moon_pa_de440_200625.bpc",
        "moon_de440_250416.tf", "moon_assoc_me.tf"]
DSN_K = ["earthstns_itrf93_201023.bsp", "earth_topo_201023.tf",
         "earth_assoc_itrf93.tf", "earth_latest_high_prec.bpc"]
DSN = {"Goldstone": "DSS-14", "Canberra": "DSS-43", "Madrid": "DSS-63"}


class DEM:
    """Height above the 1737.4 km sphere, in meters, sampled by lat/lon."""

    def __init__(self, path):
        self.geo = CRS.from_proj4(f"+proj=longlat +R={R_MOON} +no_defs")
        self.tif = str(path).lower().endswith((".tif", ".tiff"))
        if self.tif:
            import rasterio
            ds = rasterio.open(path)
            self.arr = ds.read(1).astype("float32")
            self.inv = ~ds.transform
            self.tr = Transformer.from_crs(self.geo, ds.crs, always_xy=True)
            self.res = abs(ds.transform.a)
            nd = ds.nodata
            if nd is not None:
                self.arr[self.arr == nd] = np.nan
        else:  # LDEM_16.IMG: 5760 x 2880, int16, 0.5 m per count (check the .LBL)
            self.arr = np.fromfile(path, "<i2").reshape(2880, 5760) * 0.5
            self.res = 1895.0

    def height(self, lat, lon):
        lat, lon = np.asarray(lat, float), np.asarray(lon, float)
        if self.tif:
            x, y = self.tr.transform(lon, lat)
            col, row = self.inv * (x, y)
        else:
            row, col = (90 - lat) * 16, (lon % 360) * 16
        r, c = np.floor(row).astype(int), np.floor(col).astype(int)
        ok = (r >= 0) & (r < self.arr.shape[0]) & (c >= 0) & (c < self.arr.shape[1])
        out = np.full(r.shape, np.nan)
        out[ok] = self.arr[r[ok], c[ok]]
        return out


def horizon_profile(dem, lat, lon, az_step=2):
    """Highest terrain elevation angle (deg) for each azimuth from the site."""
    h0 = dem.height([lat], [lon])[0]
    az = np.radians(np.arange(0, 360, az_step))[:, None]
    d = np.arange(dem.res, HORIZON_RANGE_KM * 1000, dem.res)[None, :]
    la1, lo1, dl = np.radians(lat), np.radians(lon), d / R_MOON
    la2 = np.arcsin(np.sin(la1) * np.cos(dl) + np.cos(la1) * np.sin(dl) * np.cos(az))
    lo2 = lo1 + np.arctan2(np.sin(az) * np.sin(dl) * np.cos(la1),
                           np.cos(dl) - np.sin(la1) * np.sin(la2))
    h = dem.height(np.degrees(la2), np.degrees(lo2))
    ang = np.arctan2(h - h0 - d**2 / (2 * R_MOON), d)      # includes Moon curvature
    ang = np.where(np.isnan(ang), -np.pi / 2, ang)
    return np.degrees(az[:, 0]), np.degrees(ang.max(axis=1)), h0


def earth_azel(lat, lon, h, ets):
    la, lo = np.radians(lat), np.radians(lon)
    site = (R_MOON + h) * np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    E = np.array([-np.sin(lo), np.cos(lo), 0])
    N = np.array([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)])
    U = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    az, el = [], []
    for et in ets:
        p, _ = sp.spkpos("EARTH", et, "MOON_ME", "NONE", "MOON")   # km, Moon centre -> Earth
        v = np.array(p) * 1000 - site
        az.append(np.degrees(np.arctan2(v @ E, v @ N)) % 360)
        el.append(np.degrees(np.arcsin(v @ U / np.linalg.norm(v))))
    return np.array(az), np.array(el)


def dsn_best_moon_el(ets):
    best = np.full(len(ets), -90.0)
    for st in DSN.values():
        for i, et in enumerate(ets):
            p, _ = sp.spkpos("MOON", et, f"{st}_TOPO", "LT+S", st)
            best[i] = max(best[i], np.degrees(np.arcsin(p[2] / np.linalg.norm(p))))
    return best


def longest_false_hours(ok, step_min):
    best = cur = 0
    for v in ok:
        cur = 0 if v else cur + 1
        best = max(best, cur)
    return best * step_min / 60


def main():
    for k in BASE:
        sp.furnsh(str(KERNEL_DIR / k))
    use_dsn = all((KERNEL_DIR / k).exists() for k in DSN_K)
    if use_dsn:
        for k in DSN_K:
            sp.furnsh(str(KERNEL_DIR / k))
    else:
        print("DSN kernels not found: checking Earth visibility only.\n")

    et0 = sp.str2et(f"{START} 00:00:00")
    ets = et0 + np.arange(0, DAYS * 86400, STEP_MIN * 60)
    dsn_el = dsn_best_moon_el(ets) if use_dsn else None
    dem = DEM(DEM_PATH)

    for name, (lat, lon) in SITES.items():
        az_h, hz, h0 = horizon_profile(dem, lat, lon)
        if np.isnan(h0):
            print(f"{name}: outside the DEM coverage, skipped")
            continue
        az_e, el_e = earth_azel(lat, lon, h0, ets)
        hz_at = np.interp(az_e, az_h, hz, period=360)
        vis = el_e > hz_at + EARTH_MARGIN_DEG
        link = vis & (dsn_el > DSN_MIN_EL_DEG) if use_dsn else vis
        print(f"{name} (lat {lat}, lon {lon}, height {h0:.0f} m)")
        print(f"  Earth above horizon:   {100 * vis.mean():5.1f}% of time")
        if use_dsn:
            print(f"  Earth + DSN in view:   {100 * link.mean():5.1f}% of time")
        print(f"  Longest outage:        {longest_false_hours(link, STEP_MIN):.1f} h")
        print(f"  Earth elevation range: {el_e.min():.1f} to {el_e.max():.1f} deg\n")


if __name__ == "__main__":
    main()
