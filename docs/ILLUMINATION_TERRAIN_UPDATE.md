# Live illumination and realistic landing-surface update

## Install
Stop the server with Ctrl+C. Back up the project. Extract the updated spacecraft ZIP into the existing project folder beside run.py; merge folders and replace files. Keep data/. Restart `.venv\Scripts\python.exe run.py` and hard-refresh with Ctrl+F5. This cumulative patch includes the previous spacecraft update. No new Python packages or large DEM downloads are needed.

## Restored spacecraft status
A new glass panel stays visible in flight and after landing. It shows:

- Sun elevation and azimuth; SUNLIT, PARTLY SUNLIT or SHADOWED; visible fraction of the solar disk, including approximate Earth eclipse overlap.
- Earth elevation and azimuth; direct-to-Earth CLEAR, PARTIAL / BLOCKED or BLOCKED; illuminated Earth phase.
- The last sampled UTC time, position, terrain resolution and observer reference.

The frontend requests a new snapshot about every 1.5 seconds, with only one request outstanding. It uses the ship's actual current latitude, longitude, altitude and sky-clock time. LIVE means the displayed sample is recent; UPDATING identifies a sample that no longer matches a changed location, altitude or fast-running clock. It never substitutes made-up status when a request fails. Missing terrain or SPICE data produces UNAVAILABLE. Fast time or boosted motion can outpace network updates; check the displayed sample time/position.

The new /api/flight-status endpoint computes instantaneous geometric SPICE vectors at the observer, not a fixed landing-site timeline. It samples two LOLA terrain rays toward Sun and Earth. Close terrain uses source spacing; the distant rays use 160 m or source spacing to 120 km and 2 km sampling beyond that toward the flight-altitude lunar limb. Far ray length increases with altitude (up to 2400 km). Spherical curvature is included; the Moon has no atmospheric refraction in this model. On the ground, the reference is 2 m above the source DEM; in flight it is the ship's displayed AGL altitude plus that reference height.

CLEAR requires the full Earth disk to clear the sampled skyline. Partially visible Earth is labelled PARTIAL / BLOCKED. This is geometric screening, not an antenna, DSN availability, relay or radio link-budget calculation. Two directed rays and a straight skyline across each disk can miss small or off-axis obstacles; the planner retains its full sampled azimuth profile. Decorative rocks never influence the science result.

## Surface changes

The local view now includes the supplied far LOLA grid out to 80 km in each horizontal direction, the 8 km local grid, and a close-range surface patch around the lander. Real elevations are not exaggerated. The camera stays above sampled local terrain.

The close patch uses a tiled, monochrome, mirrored centre crop of NASA Apollo 11 photograph AS11-40-5876, showing undisturbed lunar soil. A fine bump layer, shallow small crater impressions and reproducible centimetre-to-submetre rocks add visual texture. Large block-shaped foreground boulders have not been copied from the screenshot. The model keeps the footprint around the craft clear for presentation. Soil photography has baked photographic lighting; it is a visual texture, not a calibrated PBR material or measured height map.

Photo source documentation:
- NASA Apollo Lunar Surface Journal, Apollo 11 EVA photo gallery: https://www.nasa.gov/wp-content/uploads/static/history/alsj/a11/a11_eva_thumbs.html (AS11-40-5876).
- Open image/source record: https://commons.wikimedia.org/wiki/File:AS11-40-5876_Undisturbed_Lunar_Soil.png.
- Included image retrieved from the Wikimedia 960-pixel preview of that NASA image. The NASA legacy high-resolution image link returned 404 during retrieval. Credit NASA / Apollo 11 / Buzz Aldrin. The Commons record identifies the NASA photograph as public domain in the United States. No NASA endorsement implied.

The same Apollo soil appearance is used at all six sites as an illustrative material. It is not a site-specific surface photograph of Shackleton, Connecting Ridge, Malapert, Mons Mouton or Shiv Shakti. Larger terrain shapes come from the existing site-specific LOLA data, whose resolution is still about 80 m polar, 240 m at Shiv Shakti and 1.9 km around Apollo 11. Photo texture, extra vertices and decorative craters do not increase measured DEM resolution. The landing-view caption labels NASA soil, LOLA relief and visual rocks separately.

Sun lighting in the landed view follows the computed visible solar fraction. A labelled inspection light remains near the craft to let users inspect it in shadow; this does not change the SHADOWED science status. The full WebGL renderer adds bump response, shadows, more mesh subdivisions and material lighting. The CPU fallback now displays the soil texture too, with simpler affine texture projection, lighting and geometry. This build browser has no WebGL; browser screenshots document the CPU fallback rather than claiming GPU visual verification.

## Flight correction

A departing lander ignores its previous beacon until it has moved more than 6 km away, preventing accidental recapture during descent toward a nearby destination. Explicitly choosing the departure beacon again allows a deliberate return. A regression test covers Shackleton lift-off followed by Connecting Ridge approach.

## Validation
29 Python tests pass, covering the original science/API checks plus observer-height effects, planner/SPICE angle agreement, spherical limb geometry, date changes, validation and new served assets. The existing Node flight suite passes. A new Node terrain check verifies surveyed base heights, curvature, repeatable small rocks, mesh flags and resource disposal. JavaScript syntax checks pass.

Browser checks verify the visible telemetry in flight, SHADOWED/BLOCKED status after Shackleton touchdown, SUNLIT/CLEAR after lift-off, texture loading, orbit-camera terrain clearance and a second landing region. Last sample time/position remain visible. No synthetic rock geometry is used in the visibility endpoint.
