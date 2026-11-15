# Verification and limits

## Automated checks

Validated on Linux with Python 3.12. The final scientific/backend run completed with **12 passed** using `python -m pytest -q --tb=short`. Exact tested direct-package versions are in `tested_versions.txt`. Warnings were upstream test-client and affine-operator deprecation notices, not test failures.

The suite verifies:

1. Root page, local map asset, health and site list endpoints.
2. Curated and custom-coordinate API calculations with bundled real data.
3. Invalid coordinates, missing sites, malformed dates, unsupported mode and out-of-range dates produce usable errors.
4. CSV export headers and a 24-hour time grid's exact row count.
5. Orthonormal local ENU axes at ordinary coordinates and exact poles, with circular azimuth comparison.
6. Disk visibility and eclipse overlap limits.
7. Linearly interpolated crossings and boundary clipping without adding an extra interval at the final sample.
8. Curved-sphere terrain horizon against the analytic observer-height dip on synthetic flat spherical terrain.
9. Real-data duration bounds, simultaneous-visibility bounds, finite geometry, skyline length and fine/adjusted resolutions.
10. Date bounds and linear power scaling with array area.
11. Explicit body-centre subtraction versus SPICE's `spkcpo` constant-surface-observer API for both Sun and Earth.

The parameterized real-data test runs in both adjusted and fine modes, bringing the total collected test cases to 12. The SPICE API comparison is an alternate implementation path using the same ephemeris; it is not an independent astronomical measurement or a Horizons cross-validation.

JavaScript also passed `node --check frontend/js/app.js`.

## Browser verification

The final app was opened in Chrome and the following were exercised through the actual interface:

- Automatic first evaluation and rendering of metrics, polar terrain, skyline and timeline.
- Switching between polar reference regions and evaluating them.
- Custom latitude/longitude (-89.45°, -137.3°) evaluation.
- Adding multiple scenarios, preserving prior parameters, and seeing different site/date summaries side by side.
- Moving the time slider and playing/pausing the timeline.
- Shifting the same site from 1 December 2026 to 8 December 2026 and comparing results.
- Downloading a CSV through the frontend export control.

A final visual review showed populated sky positions, metrics, a terrain map, time series and three comparison rows. Mobile layouts are implemented in CSS, but a physical mobile device was not tested. Windows setup scripts are provided but were not executed on Windows in this environment.

## Recorded demonstration values

`sample_results.json` records four complete 14-day runs beginning 2026-12-01 00:00 UTC, using adjusted mode, 120 km horizon, 2 m observer height, 30-minute samples, no extra Earth margin, and a 1 m² horizontal panel at 28% efficiency. These are outputs of this implementation, not benchmark truth. Re-run those inputs to reproduce them.

For that run, the illustrative Shackleton coordinate has about 86.834 hours of any direct solar disk visibility and 0 hours of full Earth-disk clearance. The illustrative Malapert coordinate has about 20.170 hours of sunlight and 336 hours of full Earth-disk clearance. These contrasts are coordinate/date-specific; they are not a general ranking of either region.

## Kernel cross-check

`kernel_comparison.json` compares geometric Moon-centred Sun and Earth vectors from the added DE440s SPK against the supplied DE442s SPK at 2026-12-01, 2030-06-01 and 2040-01-01 in the same DE440-based MOON_ME frame. Maximum angular separation in those samples was below 0.00016 arcseconds; the largest Sun-range difference was approximately 1.02 metres. This comparison checks internal kernel consistency at those epochs, not terrain accuracy or a general independent uncertainty budget. The live app consistently uses matched DE440 positions and orientation.

## Remaining scientific validation

No independent site/date-matched Horizons verification or comparison against calibrated LOLA illumination/visibility products was completed. No convergence guarantee is claimed for 1° skyline rays, finite horizon radius, terrain versions or the requested temporal cadence. Optical imaging, fine boulder/roughness models, hazard assessment, DSN station visibility, link budgets, thermal/battery simulation and flight certification remain outside this model.

Before using outputs for an operational mission, register exact site coordinates against the correct terrain release/frame, quantify terrain uncertainties, converge spatial/temporal sampling, independently cross-validate ephemerides and visibility windows, and model the real power and communication hardware.

## Minimalist frontend revision

The home page now uses the user-supplied `luna-scout-frontend(1).zip` as its actual source, rather than presenting the previous dashboard. Original base CSS is byte-identical to the supplied version. The original NASA Eyes iframe, left-side steps, Start mission pill, top-right title and glass site chips remain. Small navigation additions lead to a separate `/mission.html` page. Its glass panels, typography, colors and scene match home. Result tools are grouped into Horizon, Timeline, Compare, Terrain and Details tabs to avoid filling the landing page.

Calculations, scientific data and backend endpoints are retained. An optional Still scene switch uses local visual assets when the external NASA viewer is slow or unavailable; that backdrop and the NASA background do not follow the calculation date. The NASA viewer is a third-party service, so its loading/rendering depends on network and browser capabilities.

Revised interface verification: home-to-planner navigation, Check site API calculation, site switching, adding two scenarios to Compare, all five result tabs, timeline play/pause, and the still-scene toggle were exercised in Chrome. The revised project's automated suite completed with 12 passed. JavaScript syntax checks passed for `app.js`, `planner.js` and `scene.js`. Base CSS was compared directly to the latest supplied ZIP and matched exactly.
