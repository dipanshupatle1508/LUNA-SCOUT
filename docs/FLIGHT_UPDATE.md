> Updated: live spacecraft telemetry and the new surface rendering are described in [ILLUMINATION_TERRAIN_UPDATE.md](ILLUMINATION_TERRAIN_UPDATE.md).

# Spacecraft flight update

## Install over the existing Luna Scout project

1. Stop the Python server (Ctrl+C).
2. Back up your current frontend and backend folders.
3. Extract this update beside your existing run.py. Merge frontend/backend folders and replace matching files. Keep your original data folder. Do not create a nested project folder.
4. Restart with `.venv\Scripts\python.exe run.py` on Windows, or your usual Python command.
5. Open http://127.0.0.1:8000 and press Ctrl+F5.

No new Python dependencies. This is a cumulative update: the earlier markers, module viewer, surface API and NumPy compatibility correction are included. The large SPICE and terrain files are deliberately omitted.

## Fly around the Moon

Choose a named region on the homepage, then click its surface marker. Alternatively click any unmarked point on the Moon to begin above those coordinates. Flight begins 60 km above the surface; there is no walking or jumping mode.

- W / S: increase / decrease throttle.
- A / D or left / right arrows: steer.
- R / F: ascend / descend.
- Hold Shift: exploration boost (up to 180 km/s); normal maximum 6 km/s.
- Space or Brake / hover: stop and hover.
- Drag: orbit the chase camera.
- Choose a beacon and press Fly to beacon for an assisted journey along the lunar surface. This moves the spacecraft rather than teleporting it.
- Fly within 3 km horizontally of any beacon while at or below 12 km altitude: contact initiates assisted descent and exact site touchdown. Passing above that height does not land. Fast passes use swept-path contact detection.
- After touchdown the view switches to the site's local LOLA terrain and full-sized lander. Drag to inspect it; choose Lift off to return to flight. T also initiates lift-off.
- Pause flight stops the craft; the separate sky-time control determines astronomy time.

The six markers use the catalogue below. The Moon is continuous: you can travel beyond the old local walking tile and cross poles and the longitude seam. Mobile controls provide steering, thrust, altitude and boost.

## Real Moon-relative sky

The homepage and flight view share a SPICE-based sky clock. Choose a UTC date or accelerate time to 1 hour, 1 day or 7 days per real second. Body positions, Moon illumination and Earth orientation follow that date. Changing the homepage time carries the date into flight.

`GET /api/celestial?start=2026-11-15T00:00:00Z&days=120&step_hours=6` supplies geometric Sun/Earth centre positions relative to the Moon in MOON_ME, plus IAU_EARTH-to-MOON_ME orientation matrices. The frontend interpolates six-hour samples; this is a visual sky display, separate from the planner's visibility calculations. Dates span 2000–2050. The clock pauses at the loaded interval's end; choose a new date to load another interval. Missing kernels or a failed request produce a visible status rather than invented orbital motion.

Earth's Moon-relative direction changes through libration; it does not circle the Moon once per month in a fixed lunar frame. The Sun's direction moves over the lunar day. Both are placed at actual relative distances and radii in the 3D scene, so they can be offscreen or occulted. Drag the view to look around. The small inset always shows their directions with compressed distances, clearly labelled. This avoids placing a huge decorative Earth beside the Moon at a false distance.

The Moon has low ambient illumination and a dark night side rather than the previous bright fill lighting. A crescent or mostly dark Moon on a chosen date is expected. The local landing view includes an inspection light so the craft remains visible at night; its label identifies that light.

## Flight and terrain fidelity

This is assisted educational game flight. Throttle, boost, hover, beacon capture and descent are interaction mechanics, not orbital dynamics, fuel or engine-performance models. The detailed Apollo-style lander supplied by the user is used at all sites as an illustrative exploration craft, not a Vikram reconstruction. The overview craft is enlarged for visibility; after landing it is shown at model scale.

Global flight uses a textured spherical Moon with relief from the existing coarse global LOLA height image. Its displayed altitude is approximate above that global DEM, not a hazard-clearance measurement. On landing the backend loads the actual local LOLA tile. Polar source resolution is about 80 m, Chandrayaan-3 about 240 m, and Apollo 11 approximately 1.9 km. A dense display mesh does not improve source resolution. Local terrain includes spherical curvature. Region reference points are not certified safe landing areas.

The mission planner retains the engineering calculations; use it for terrain horizon, Sun/Earth visibility and comparisons. The flight view and sky interpolation do not replace those calculations.

## Site definitions

All longitudes below are east-positive. These definitions replace the earlier illustrative polar coordinates.

| Button | Latitude | Longitude | Meaning / source |
| --- | ---: | ---: | --- |
| Shackleton region | -89.6700 | 129.7800 | IAU/USGS Shackleton feature centre in the LOLA control network; not a historical touchdown or a selected safe landing point |
| Connecting Ridge region | -89.4890 | -137.8675 | NASA's published SCR2 candidate coordinate, documented in a 2021 site-selection record reproduced in a 2024 briefing; not IM-2's eventual touchdown |
| Malapert massif region | -85.9800 | -1.6700 | IAU/USGS centre of Mons Malapert; not the IM-1 touchdown |
| Mons Mouton region | -84.6000 | 31.0000 | IAU/USGS named feature centre; not a historical touchdown |
| Chandrayaan-3 / Shiv Shakti | -69.3730 | 32.3190 | Rounded final touchdown coordinate, NASA/JPL IPN report |
| Apollo 11 / Tranquility Base | 0.67416 | 23.47314 | Lunar Module touchdown coordinate from NASA NSSDC |

The first four are exploration regions. The last two are historical touchdowns. A pin for an extended region identifies its stated reference coordinate, not the whole footprint. The marker's latitude and longitude are accurate to the listed source convention; no independent metre-scale registration between different control networks is claimed.

Sources:

- Shackleton: https://planetarynames.wr.usgs.gov/Feature/5450 (LOLA control-network entry).
- Connecting Ridge SCR2: https://www.nasa.gov/wp-content/uploads/2024/11/mthornblom-im2-final-tagged.pdf (site-selection record).
- Mons Malapert: https://planetarynames.wr.usgs.gov/Feature/16338.
- Mons Mouton: https://planetarynames.wr.usgs.gov/Feature/16070.
- Apollo LM coordinates: https://nssdc.gsfc.nasa.gov/planetary/lunar/lunar_sites.html.
- Chandrayaan-3 final coordinate: https://www.nasa.gov/wp-content/uploads/2026/02/42-240a.pdf.

## Graphics and credits

NASA SVS LROC/LOLA Moon colour texture: https://svs.gsfc.nasa.gov/4720/. Credit NASA SVS, Ernie Wright (USRA), Noah Petro (NASA/GSFC), and LRO/LROC/LOLA teams. The original NASA asset server was unavailable during retrieval, so the unprocessed 2K asset was retrieved from the COSMOS public mirror, whose attribution identifies this source: https://github.com/sudoaanish/COSMOS/blob/master/assets/textures/ATTRIBUTION.md.

The global height image derives from the supplied LDEM_16 raster, shifted to match the Moon texture. Coordinates use +X at zero longitude, +Y north, -Z at 90 degrees east. The Sun is an emissive sphere; illumination is directional. Earth uses the Three.js r128 example texture `earth_atmos_2048.jpg`, retrieved from https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/textures/planets/earth_atmos_2048.jpg. Three.js/OrbitControls are bundled locally with the MIT license in frontend/vendor/THREE-LICENSE.txt. No NASA endorsement is implied.

Full graphics require WebGL. When unavailable, the CPU preview renders the same flight coordinates, textured Moon and sky, with simplified geometry, lighting and effects. Its global Moon is spherical rather than displaced. The software landing view is also simplified. This build browser has no WebGL; the fallback and interaction flow were visually verified, while WebGL rendering was checked through source/syntax and asset checks only.

## Validation

23 Python tests passed: existing science/API tests, six-site terrain registration, celestial vectors cross-checked with SPICE, Earth rotation orthogonality, interval validation and served assets. Node flight tests passed for great-circle travel, poles/dateline, circumnavigation, fast swept beacon contact, high-altitude flyby, automatic descent, lift-off, manual cancellation and an Apollo-to-Chandrayaan journey. New JavaScript files pass syntax checks.

Browser verification: homepage marker -> spacecraft flight -> Fly to beacon -> automatic touchdown on Connecting Ridge local terrain -> lift-off. Manual controls, sky time changes and custom surface entry are checked separately. Earlier validation files may describe the old catalogue or EVA version; this document describes the flight update.
