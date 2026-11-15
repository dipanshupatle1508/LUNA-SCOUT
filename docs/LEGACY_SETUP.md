# Luna Scout

A working lunar landing-site comparison application built directly on your supplied minimalist Luna Scout frontend. The original landing-page theme, NASA scene, title placement, crystal glass styling, steps and pill buttons are retained. Start mission opens a second, matching page with a compact control panel and tabbed results. The calculations use your research PDFs, Earth-link script, NASA/JPL SPICE kernels and LRO/LOLA elevation maps.

## Start here

1. Extract the entire ZIP (including `data/`) into a normal folder. Do not run inside the ZIP.
2. Install **64-bit Python 3.11 or 3.12** from https://www.python.org/downloads/ (on Windows enable “Add Python to PATH”). Python 3.12 was used for validation. Allow about 2 GB of free RAM for fine-resolution terrain queries and 1 GB disk space for the extracted application and packages.
3. Open a terminal inside the `luna-scout` folder and run:

```sh
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python run.py
```

macOS / Linux:

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run.py
```

4. Open **http://127.0.0.1:8000** in Chrome, Edge or Firefox. Keep the terminal open. Stop with Ctrl+C.

Alternatively, use `start_windows.bat` or `bash start_unix.sh`. These create an isolated environment and install dependencies before starting the server. The first installation needs Internet access. Scientific calculations run locally without API keys or external ephemeris services. Your original NASA Eyes background and Google font need Internet; choose **Still scene** in the top navigation to use the bundled decorative backdrop offline, with system-font fallback. The still backdrop is visual context, not a lunar lighting simulation. The scene choice is remembered on this browser. External source links also need Internet.

Do not double-click `frontend/index.html`: it needs the Python API. Node.js is optional and only used for the development preview wrapper, not for normal operation.

## Two pages, one theme

- `/` is your minimalist landing page with a few navigation links added above and beside it.
- `/mission.html` is the matching planner. Check site, then use the **Horizon**, **Timeline**, **Compare**, **Terrain** and **Details** tabs. Only one results view is shown at a time.
- The uploaded `frontend/css/style.css` is preserved byte-for-byte. Additions live in `frontend/css/extension.css`.
- `frontend/js/app.js` handles landing-page site links; `planner.js` retains the scientific UI behavior; `scene.js` controls the optional still backdrop.

## What works

- Six curated regions / historical references plus custom lunar coordinates.
- Real DEM hillshade map; click a polar location or choose an existing marker.
- Any complete mission interval inside 2000–2050 UTC; 1–60 days, 5–120 minute API cadence (UI offers 5/15/30/60).
- Sun and Earth azimuth/elevation in the local north/east/up frame, with surface-observer parallax and lunar libration.
- Terrain skyline, finite Sun and Earth disks, observer height, clearance margin and approximate Earth occultation of the Sun.
- Sunlight, fully clear Earth-disk and simultaneous visibility windows; longest darkness and Earth obstruction; interpolated rise/set estimates clipped to the requested interval.
- Ideal solar energy estimate for fixed horizontal or tracking arrays, with configurable area and efficiency.
- Animated time scrubber in the Timeline tab and sky/horizon diagram in the Horizon tab.
- Four-scenario comparison: evaluate a site/date/settings combination, add it, change parameters, evaluate and add again. Saved rows contain the original parameters and have Load/Remove controls. Comparison rows last for the current page session.
- CSV of the displayed timeline, full JSON of timeline/horizon/summary/method/request, URL-fragment scenario restoration.
- Responsive interface, keyboard-accessible form controls, expandable explanations and API documentation at `/docs`.

## Quick demonstration

1. Evaluate Shackleton region, 1 December 2026, 14 days; add to comparison.
2. Evaluate Malapert massif region with the same date; add it.
3. Change the date by 7 days and add the new result.
4. In the Compare tab, compare direct sunlight, Earth clearance, overlapping windows, maximum darkness and solar energy. These are separate quantities; there is no arbitrary “best site” score.
5. Open the Timeline tab and move the time slider to inspect Sun/Earth elevation and terrain blockage at a specific time. The illuminated appearance of the map itself is static hillshade, not simulated shadow.
6. Export JSON for full reproducibility; the CSV contains numerical samples and uses the exact engineering settings currently displayed.

## Project layout

- `backend/`: FastAPI server, SPICE timeline engine, LOLA sampling/horizon engine, curated sites.
- `frontend/`: complete dependency-free HTML/CSS/JavaScript interface and real DEM hillshade.
- `original_frontend/`: your uploaded frontend preserved unchanged.
- `data/kernels/`: supplied kernels plus the added matched DE440s position kernel.
- `data/terrain/`: original selected terrain files and associated PDS labels.
- `docs/`: your two research PDFs and original Earth-link script; scientific method, data inventory and validation notes.
- `tests/`: numerical geometry, horizon, duration, API and export tests.
- `scripts/`: data checksum generator and optional preview adapter.

## Scientific interpretation

Read `docs/METHOD.md` and `docs/VALIDATION.md` before interpreting results. This is an educational and early screening prototype, not flight-qualified analysis. Entire-Earth-disk visibility does not establish DSN station visibility or a communications link budget. Solar estimates omit battery, thermal, self-shadowing and equipment-specific effects. DEM resolution, finite ray radius and temporal sampling constrain accuracy.

The application deliberately labels illustrative polar coordinates as regions, not verified lander touchdown points. Apollo 11 and Chandrayaan-3 are historical reference coordinates; Chandrayaan-3 is not at the geographic south pole. Current future mission target coordinates can be entered as custom coordinates after checking their source and frame.

## Tests

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Run from the project root. The test suite loads the bundled real terrain and kernels. Verification details and limitations are in `docs/VALIDATION.md`.

## Troubleshooting

- **Python not found:** install 64-bit Python and reopen the terminal; on Windows `py -3.12` can replace `python` when creating the environment.
- **Missing module:** install with the same interpreter that starts the app (`.venv/Scripts/python` on Windows or `.venv/bin/python` on Unix).
- **Port 8000 already used:** run `.venv/bin/python -m uvicorn backend.app:app --host 127.0.0.1 --port 8001` (use Windows interpreter path there) and open port 8001 instead.
- **Calculation failed:** check that the ZIP was fully extracted, data filenames were retained, and consult the terminal log. First queries load terrain; changing only the date reuses cached horizons.
- **Long calculation:** use adjusted 80 m terrain, a shorter interval or larger time cadence. Fine mode decompresses large JP2 grids on its first use. Only one geometry calculation runs at a time because SPICE global state is shared.
- **No sunset/Earthset before interval end:** the app does not extrapolate; enlarge the time window.
- **Different results in fine/adjusted modes:** they are different LOLA source products, resolutions and versions, not interchangeable truth. Compare numerical settings and source provenance.

## Attribution and code reuse

NASA/JPL NAIF provides SPICE data; NASA LRO/LOLA and the PDS Geosciences Node provide the terrain archive. The additional `de440s.bsp` was downloaded from the official NAIF archive. No NASA endorsement is implied. Keep original data labels and attribution when redistributing; see `docs/DATA_SOURCES.md`. New application code is provided under the MIT license; supplied source materials and third-party scientific data retain their respective terms.
