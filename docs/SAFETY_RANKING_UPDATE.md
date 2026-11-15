# Terrain-aware ranking and verified south-pole imagery

## Install and use

Stop the server, back up the project, and merge this cumulative ZIP into the existing project folder beside run.py. Replace matching files, keep data/, restart `.venv\Scripts\python.exe run.py`, and press Ctrl+F5. No new Python dependencies or terrain downloads are needed. All prior spacecraft, telemetry and terrain updates are included.

Open **Safety ranking** from Home, the planner, or the spacecraft controls. Choose landing UTC, mission duration and screening limits, then Rank candidates. Select either the six existing sites or South-pole survey + sites. The old planner's Compare view also sorts saved scenarios automatically under the default limits and now allows twelve scenarios. A scenario's own date, duration, observer height and engineering settings remain attached. Arbitrary durations passed from the new page are supported in the old planner selector.

## What is ranked

The detailed rank order is: WITHIN LIMITS first, LIMITS EXCEEDED next, UNASSESSED last. Within an assessed category the 0–100 score sorts descending. Every failed gate is available under “Why this position?” The score is a relative screening index, not a percentage chance of landing safely. When nobody passes, the UI says so; rank 1 does not imply a viable landing.

Terrain covers a circular, 1 km-radius neighbourhood around the reference coordinate. Source spacing is retained, not made finer by interpolation. Horn's 3×3 finite-difference formula computes slopes. The 95th-percentile slope is the conservative comparison measure; median and maximum are also returned. A least-squares plane is fitted to all neighbourhood elevations; RMS residual measures regional roughness. “Steep area” is the fraction of sampled slope centres above the chosen slope limit. These are regional terrain measures, not boulder heights or metre-scale landing-footpad clearance.

Weights: slope P95 35, plane-residual roughness 20, steep-area fraction 15, mission sunlight percentage 10, full-Earth visibility percentage 10, visible Sun fraction at arrival 5, and full Earth clearance at arrival 5. Terrain contributions decrease linearly to zero at twice their configured limit. All gates apply before the score. Prototype defaults are slope P95 ≤10 degrees, roughness ≤20 m, steep area ≤20%, mission sunlight ≥20%, mission Earth visibility ≥20%, some direct Sun at arrival, and the full Earth disk clear at arrival. These are editable design choices, not NASA lander requirements.

Elevation is measured radial height above a 1,737,400 m lunar reference sphere. It is reported for every site and can enforce a user-selected allowed elevation corridor. It is not automatically scored as “higher = safer”: a high ridge may be steep or unstable, and absolute elevation alone does not establish touchdown safety. Local elevation variability is already captured in roughness and relief.

Sun/Earth arrival geometry uses the existing instantaneous spacecraft visibility engine at a 2 m landed reference. Mission windows use SPICE/LOLA timelines, 60-minute samples and a 120 km horizon. The original Compare tab uses its scenario's chosen cadence, height, horizon radius and terrain mode for astronomy. Its terrain score always uses the adjusted LOLA stack; this distinction appears in the API. Different sample cadences can produce slightly different window fractions. Dates and libration change the dynamic contributions and can change gate categories and order.

## Whole south-pole regional survey

The survey spans 80°S–90°S on a 5 km sampling lattice, 11,553 nodes. All nodes have elevation, an 80 m-baseline Horn slope, a 3×3-neighbourhood roughness proxy, and approximate landing-time Sun/Earth terrain-ray checks. Coarse rays use near distances 80, 160, 320, 640, 1280, 2560 and 5000 m, followed by roughly 4 km steps to 120 km. They can miss narrow ridges, solar eclipses and short events, so they are a shortlist tool rather than the full planner. Exact-pole geodesic rays are handled explicitly to avoid the longitude singularity at 90°S.

Every node receives a coarse priority rank. Priority sorts sampled slope / 10 + roughness proxy / 5 + 4 if Earth is obstructed + 2 if Sun is obstructed, lowest first. It is a separate rapid index, not the detailed score. The first twenty coarse nodes appear in a second table; all 11,553, their visibility flags and priorities are in the JSON export with a cells_columns schema. Maps show slope, elevation, local roughness proxy, coarse Sun visibility or coarse Earth clearance. Clicking a map node gives its coordinate and a planner link for detailed refinement.

Twelve date-aware nodes, at least 20 km apart, are selected from that priority order. These receive the full 2 km-neighbourhood statistics and dense terrain-horizon / mission-window analysis, then are ranked alongside the six existing sites. Dense analysis can reject a candidate that passed the coarse survey. This covers the polar cap regionally, not every metre, and does not prove a global optimum among all possible coordinates. The detailed and coarse ranks are deliberately distinguished in the interface and export.

Shiv Shakti (69°S) and Apollo 11 (near the equator) are labelled outside the polar cap. They remain available as historical comparisons. Four other catalogue entries are regional reference coordinates rather than historical touchdowns or approved safe pads.

## Data scale and limits

The supplied adjusted polar LOLA raster is about 80 m/pixel. Shiv Shakti uses 240 m/pixel; Apollo 11 uses the global approximately 1.9 km/pixel grid. Apollo's terrain is too coarse for this 2 km-diameter screen and is UNASSESSED, not called safer or dangerous. The condition is source spacing no greater than one quarter of the assessment radius. Even the 80 m grid cannot resolve lander-scale obstacles. Coarser sources can hide hazards; source spacing is always exposed and no equal-confidence comparison is implied. The available unadjusted finer JP2 layers are not silently mixed into the adjusted scoring datum.

Images do not supply DEM gradients in this implementation. No boulder detector, bearing-strength model, dust/plume assessment, guidance dispersion, vehicle footprint/tilt model, terrain-relative navigation confidence, antenna link budget or DSN schedule is inferred. Operational site selection requires registered high-resolution DTMs/images and vehicle-specific limits. Illumination and communication are geometric screening, with the existing model's sampling and horizon limits.

## Verified imagery and sources

Three observational products are bundled, displayed with coverage/date/credit and linked to their primary source pages:

1. **PIA13523**: LROC WAC mosaic of the lunar south pole, approximately 600 km across. NASA publication 27 September 2010; mosaic has multiple acquisition times. Primary source: https://science.nasa.gov/photojournal/the-lunar-south-pole/. Downloaded directly from the NASA Science asset host at 1280×1280.
2. **M1407524099LR**: LROC oblique view of Shackleton's rim toward the geographic pole, acquired 18 May 2022; about 2.4 km wide at centre. Downloaded from the LROC team source at 1100×1100. It is a perspective image, not an orthographic map.
3. **M146846913L**: LROC nadir view of the geographic south pole, acquired 13 December 2010; about 1.1 km wide. Downloaded from the same source at 1100×1100. The red pole marker is the source annotation.

Primary LROC source for 2 and 3: https://lroc.im-ldi.com/images/1276. Credit for all three: NASA / GSFC / Arizona State University. Source bytes, exact URLs, dimensions, image IDs and SHA-256 hashes are recorded in SOUTH_POLE_IMAGE_SOURCES.json. These are actual observations/mosaics, not AI-generated pictures. They are reference images, not selected-date illumination maps and not automatically registered to all candidate coordinates. No NASA endorsement is implied. The Apollo 11 soil texture in the spacecraft view remains an illustrative non-polar material and is explicitly distinguished.

Elevation archive: https://pds-geosciences.wustl.edu/missions/lro/lola.htm. The actual analysis uses the user's supplied LOLA files already in data/terrain, with filenames and resolution in API results; there was no replacement of their bytes. Method reference for LOLA/Horn slope mapping: https://www.lpi.usra.edu/lunar/lunar-south-pole-atlas/. This implementation computes its own metrics; it does not claim to reproduce or ingest the LPI 5 m slope maps. Sun/Earth kernels remain the supplied NAIF/JPL DE440 stack: https://naif.jpl.nasa.gov/naif/.

## Verification

38 Python tests pass, including analytic planar Horn slopes, detrended roughness, gate-first ordering, monotonic terrain penalties, elevation neutrality/corridor gates, coarse-data handling, cap coverage and spacing, date-aware coarse geometry, complete grid priorities, exact-pole geodesics, API validation, image assets, and existing science/flight APIs. Both existing Node flight and landing-terrain suites pass. Modified JavaScript syntax checks pass. Browser QA exercises both ranking modes, map layers and coordinate links, verified image loading, custom-duration handoff, and automatic reordering in the original Compare tab.
