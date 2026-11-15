# Luna Scout — complete updated project

This complete package includes the current frontend, Python backend, scientific datasets, verified images, tests and project architecture. It already incorporates the earlier marker, spacecraft, live-status, realistic-terrain and safety-ranking updates. Extract into a new folder; no earlier project or patch ZIP is needed.

## Start on Windows

1. Extract the whole ZIP. Keep the `luna-scout` folder and all its contents, especially `data/`.
2. Install 64-bit Python 3.11 or 3.12. Python 3.12 was used for validation.
3. Double-click `start_windows.bat` inside `luna-scout`. It creates a virtual environment, installs dependencies and starts the server. The first installation needs internet access.
4. Open **http://127.0.0.1:8000**. Keep the terminal open; press Ctrl+C to stop.

Manual installation from a terminal inside `luna-scout`:

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe run.py
```

On Linux/macOS:

```bash
bash start_unix.sh
```

Do not open `frontend/index.html` directly: the pages need the Python API. Normal operation does not require Node.js, an API key or a frontend build step. The scientific files and images are bundled. Optional external fonts, live background content and source links need internet.

## Included features

- Minimalist Moon home page with six named reference locations, accurate-coordinate markers and custom surface selection.
- Spacecraft flight around the Moon: throttle, steering, altitude control, boost, autopilot, beacon-triggered landing and lift-off.
- Live spacecraft illumination and geometric direct-to-Earth status at the current position, altitude and selected UTC time.
- Moon-relative Sun/Earth geometry and a controllable date/time clock.
- Local LOLA terrain, photographic soil appearance and decorative small rocks; source measurements and visual detail are identified separately.
- Mission timelines, terrain skylines, visibility windows, solar-energy estimates and CSV/JSON exports.
- Automatic comparison ordering with slope, radial elevation, roughness, steep-area coverage, sunlight and Earth visibility.
- Editable screening gates, score breakdowns and explicit insufficient-data handling.
- A 5 km polar sampling survey with 11,553 nodes, coarse date-dependent visibility checks, twelve refined candidates and detailed ranking alongside the six existing sites.
- Three verified NASA/LROC south-pole observational images, with credits, image IDs, acquisition information and primary source links.
- WebGL graphics with a simplified CPU fallback.

## Folder architecture

```text
luna-scout/
    frontend/          HTML pages, CSS, JavaScript, images and bundled graphics libraries
    backend/           FastAPI routes and terrain/astronomy/ranking calculations
    data/
        terrain/       LOLA elevation rasters and labels
        kernels/       NAIF/JPL SPICE kernels
        manifest.json  Scientific input checksums
    docs/              Architecture, methods, sources and verification notes
    tests/             Python tests and Node flight/terrain tests
    scripts/           Maintenance and development-preview utilities
    original_frontend/ Preserved original design reference
    run.py             Python application entry point
    start_windows.bat  Windows setup/start helper
    start_unix.sh      Linux/macOS setup/start helper
    requirements.txt   Python runtime dependencies
```

The full file-by-file architecture, API map and workflows are in [docs/PROJECT_ARCHITECTURE.md](docs/PROJECT_ARCHITECTURE.md).

## Which page to use

| Page | Purpose |
|---|---|
| `/` | Select a named site or point on the Moon |
| `/mission.html` | Evaluate a mission and compare saved scenarios |
| `/navigator.html` | Fly the spacecraft and inspect live illumination/Earth status |
| `/ranking.html` | Rank sites, edit gates, survey the polar cap and view verified imagery |
| `/module.html` | Inspect the spacecraft model |
| `/docs` | Interactive FastAPI documentation |

For flight: W/S throttle, A/D steer, R/F altitude, Shift boost, Space brake, drag to orbit the camera. Choose a destination and Fly to beacon for assistance; use Lift off after landing.

## Documentation and data sources

- [Project architecture](docs/PROJECT_ARCHITECTURE.md)
- [Safety ranking, survey and verified imagery](docs/SAFETY_RANKING_UPDATE.md)
- [Image provenance and checksums](docs/SOUTH_POLE_IMAGE_SOURCES.json)
- [Live visibility and landing terrain](docs/ILLUMINATION_TERRAIN_UPDATE.md)
- [Flight controls and Moon-relative sky](docs/FLIGHT_UPDATE.md)
- [Original scientific data sources](docs/DATA_SOURCES.md)
- [Original scientific method](docs/METHOD.md)

Earlier update guides, research files and validation examples are preserved for reference. Some describe earlier versions; the current safety-ranking/flight guides and this README describe the complete updated package.

## Interpretation

This is an educational and regional mission-screening prototype. Scores are not probabilities of safe touchdown. A gate-passing candidate is not landing-certified, and unassessed terrain is not labelled dangerous. Elevation supports a mission corridor rather than an automatic higher-is-safer bonus. The data cannot resolve every lander-scale obstacle. Earth visibility is geometric, not a confirmed radio link or DSN schedule. Photographic textures and decorative rocks do not supply scientific hazard measurements. Full definitions and limits appear in the interface and linked methods.

## Tests

The current scientific/API implementation passed 38 Python tests and both Node suites during the preceding update. To run them locally:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q tests
node tests/js/flight-core.test.cjs
node tests/js/landing-terrain.test.cjs
```

Use the virtual environment's Python executable for the Python commands. Node.js is needed only for the optional Node tests and development-preview wrapper.

## Troubleshooting

- If Python is not found, install 64-bit Python and reopen the terminal. On Windows, `py -3.12 -m venv .venv` can replace the environment-creation command.
- If a module is missing, install requirements with the same virtual-environment interpreter used to start the server.
- If a calculation fails, check that `data/` was fully extracted and inspect the terminal error. First queries may take longer while terrain loads.
- If port 8000 is occupied, stop the earlier server or run the app through Uvicorn on another port.
- After replacing an older installation, use Ctrl+F5 to refresh cached browser assets. A fresh extraction is recommended for this complete package.

## Credits

NASA/JPL NAIF supplies the SPICE resources; NASA LRO/LOLA and the PDS Geosciences Node supply the elevation products. The verified polar observations are credited to NASA/GSFC/Arizona State University. Bundled Three.js/OrbitControls retain their MIT license in `frontend/vendor/THREE-LICENSE.txt`. Supplied scientific materials and imagery retain their respective terms. No NASA endorsement is implied.
