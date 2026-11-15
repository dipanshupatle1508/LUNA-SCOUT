# Calculation method

## Coordinates and time

Latitude is planetocentric, longitude is east-positive and normalized to [-180,180). The reference sphere is 1,737,400 metres. Surface coordinates and the local ENU basis are expressed in `MOON_ME`, realized by the supplied `moon_de440_250416.tf.txt` as `MOON_ME_DE440_ME421`. Azimuth is clockwise from local north; elevation is measured above the radial local horizontal, not the terrain slope. At an exact pole the entered longitude chooses the local north reference meridian.

The app loads the supplied leap-second file, constants, lunar frame and binary lunar orientation kernels, and the added matching `de440s.bsp`. The supplied `de442s.bsp` is retained for diagnostic comparison, but is not loaded by the live engine. SPICE supplies actual lunar libration, orientation and orbital variation. UTC input is converted to ET; sampled ET increments are in seconds. For intervals crossing future leap seconds not recorded in the bundled LSK, conversion cannot anticipate those changes. Update the LSK when applicable.

The user-facing range is conservatively restricted to complete intervals within 2000–2050. File coverage is broader: the loaded DE440s SPK covers 1849-12-26 to 2150-01-22 TDB and lunar binary orientation covers 1549-12-31 to 2650-01-25 TDB. Runtime SPICE errors are not replaced with fabricated or extrapolated results.

## Sun and Earth geometry

For each epoch, SPICE returns a geometric vector from the Moon's centre to the body in `MOON_ME`, using `abcorr=NONE`. Subtract the observer's body-fixed vector (reference radius plus DEM elevation plus observer height) in kilometres, then project into local east/north/up. This includes topocentric parallax. Angles follow:

- azimuth = atan2(east, north), modulo 360 degrees;
- elevation = asin(up / distance).

These are simultaneous geometric positions, not apparent light-time/stellar-aberration-corrected observations. No atmospheric refraction is applied.

## Terrain sampling and horizon

Adjusted mode uses the supplied 80 m float LOLA elevation TIFF south of 80°S, legacy 240 m LOLA terrain south of 60°S outside that cap, then global `LDEM_16` elsewhere. Fine mode uses the supplied legacy 20 m grid south of 87.5°S, 40 m south of 85°S, 80 m south of 80°S, 240 m south of 60°S, then the global grid. Circular latitude limits avoid using extrapolated square corners. Invalid elevations fall back to a coarser source; unresolved missing values fail calculation.

The float adjusted TIFF stores metres; legacy integer JP2 and global IMG samples use 0.5 metres per count, as documented in the saved official PDS labels. Values are elevations relative to the reference sphere. The PDS radius offset is not added to these elevation samples until constructing 3D vectors. Projected grids use their embedded lunar polar-stereographic CRS, not Earth EPSG coordinates. Bilinear interpolation operates at pixel centres; the global raster wraps in longitude.

Trace 360 great-circle rays (1° azimuth spacing). Within 10 km sample at the local source spacing (minimum 20 m); farther away sample at 160 m. The chosen radius is 60, 120 or 240 km in the UI (API 30–240). For angular ground distance theta=d/R, terrain elevation h and observer radius r0, compute the ray point's horizontal and up components as:

```
horizontal = (R + h) * sin(theta)
up         = (R + h) * cos(theta) - r0
angle      = atan2(up, horizontal)
```

The maximum angle on a ray is its skyline. Interpolate the resulting skyline periodically at each Sun/Earth azimuth. This includes exact spherical curvature, but does not model unsampled terrain beyond the finite radius. Grid interpolation, radial spacing and 1° azimuth sampling can miss narrow ridges; grid spacing is not a guarantee of measurement accuracy. Increasing the radius or resolution can change results. Local and fallback grids are from different releases and may have seams. No error model or explicit vertical uncertainty propagation is included.

## Extended disks and windows

Solar angular radius uses 695,700 km divided by topocentric Sun range; Earth radius uses 6,378.137 km divided by topocentric Earth range, with arcsine. The Sun is counted as available if any of its disk is above terrain and it is not fully occulted by Earth. The disk's visible area is approximated against a locally straight skyline using the circular-segment area. Earth visibility is conservative: the entire Earth disk must clear the skyline plus the extra user angular margin. A partially visible Earth disk is labeled obstructed under this criterion. This is not a point-Earth test.

Earth occultation of the Sun is estimated by uniform planar-circle overlap from their angular separation. Partial solar eclipse fraction multiplies the terrain-visible Sun fraction. This approximation does not resolve the joint spatial pattern of a terrain edge plus a partially overlapping Earth disk. Lunar eclipses are therefore first-order estimates; no thermal or scattered illumination calculation is implied.

Signed clearance crossings are linearly interpolated between samples. Durations integrate those clipped visibility intervals; endpoints have no extra sample-width contribution. The start and end timestamps are both included in output, so a 24-hour run at 60-minute steps has 25 points but exactly 24 hours. Darkness and Earth outages are complements over the same span. Events shorter than the sampling interval, rapid horizon changes or grazing contacts can be missed. Set countdowns refer to the selected cursor time and only the calculated interval. “No set found” is not permanent visibility. A window beginning or ending at a boundary is labeled clipped.

## Solar model

Approximate incident solar flux is 1361 W/m² times (1 AU / Sun range)². Electrical power is flux times selected array area times efficiency times visible solar fraction. A fixed horizontal panel multiplies by max(0,sin(solar elevation)); an ideal tracking panel uses unit incidence. Energy uses trapezoidal integration of sampled power over actual elapsed seconds.

This is an idealized electrical yield estimate, not rated hardware performance or a full power subsystem simulation. It omits cell temperature, degradation, dust, lander self-shadowing, terrain tilt, actual array pointing limits, battery charge/discharge, wiring/converter losses and thermal control. The product of disk-visible fraction and centre-direction panel incidence is an approximation at partial sunrise/sunset. A sunlight hour is any direct Sun disk visibility; it is not an equivalent full-power hour.

## Communications meaning

Earth clearance is strictly geometric screening. It does not test individual Earth ground stations, Earth rotation, DSN scheduling, antenna pointing/gain, polarization, transmitter/receiver parameters, link budgets, data rate, weather or relay networks. The missing station kernels in the supplied original script are not invented. Full-disk clearance is conservative and differs from a particular ground-station contact opportunity.

## Reproducibility

Scenario JSON contains the exact UI query, UTC samples, angles, skyline, visibility fractions, flags, power, summaries, intervals and method settings. CSV is a sample-level export of the displayed scenario: angles in degrees, clearance in degrees, power in watts, fractions in [0,1], boolean visibility, UTC ISO timestamps. `data/manifest.json` records selected input file sizes and SHA-256 checksums. Run `python scripts/build_manifest.py` to reproduce it. Horizon and query caching are in-memory only and do not change the calculation definition.
