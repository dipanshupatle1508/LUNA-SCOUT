# Data sources and supplied research

## Used inputs

| File | Role | Origin / interpretation |
| --- | --- | --- |
| `naif0012.tls.txt` | UTC / ET | User-supplied NASA/JPL NAIF leap seconds |
| `pck00011.tpc.txt` | Constants | User-supplied generic planetary constants |
| `moon_pa_de440_200625.bpc` | Lunar orientation | User-supplied DE440 binary PCK |
| `moon_de440_250416.tf.txt` | MOON_ME frame | User-supplied DE440 lunar FK; already defines MOON_ME, so no missing `moon_assoc_me.tf` is required for explicit frame calculations |
| `de440s.bsp` | Live position engine | Added from official NASA/JPL NAIF archive to match the supplied DE440 orientation |
| `de442s.bsp` | Diagnostic comparison | User supplied; retained, not loaded by live backend |
| `LDEM_80S_80MPP_ADJ.tiff` | Adjusted 80 m polar terrain | User-supplied float TIFF, metres; its embedded history records a 1000× conversion from source kilometre grid |
| `LDEM_875S_20M.JP2` | Fine 20 m polar terrain | User-supplied LOLA integer GDR, 0.5 m/count |
| `LDEM_85S_40M.JP2` | Fine 40 m polar terrain | User-supplied LOLA integer GDR, 0.5 m/count |
| `LDEM_80S_80M.JP2` | Legacy 80 m terrain | User-supplied LOLA integer GDR, 0.5 m/count |
| `LDEM_60S_240M.JP2` | Southern regional fallback | User-supplied LOLA integer GDR, 0.5 m/count |
| `LDEM_16 (2).IMG` | Global fallback | User supplied; 5760×2880, little-endian signed int16, 0.5 m/count; paired with supplied label |
| `south-pole.png` | UI basemap | Derived locally from the adjusted 80 m DEM, displayed at 1000×1000 with static relief shading; not an optical photograph or time-dependent illumination |

The two uploaded research PDFs and original `earth_link_check(1).py` are preserved in `docs/`. They guided architecture and horizon/communication distinctions; the live application code is in `backend/`. The untouched supplied frontend is in `original_frontend/`.

The larger original slope TIFF and overlapping 75°S/240 m and 45°S/400 m grids are not duplicated in the ZIP: the working application does not read them. The selected stack covers the whole Moon, with successively coarser data outside the polar region. A raster's nominal resolution is reported at the site; rays may cross coarser fallback terrain. Slope/hazard, Diviner thermal and ice-abundance layers are not implemented or claimed. Nothing needs downloading during normal scenario calculation.

## Official archive links

- Kernel archive: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/
- Added matched SPK: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp
- SPICE surface observer reference used in a cross-check: https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkcpo_c.html
- LOLA archive: https://pds-geosciences.wustl.edu/missions/lro/lola.htm
- LOLA polar image labels: https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/polar/img/

Matching labels `ldem_875s_20m.lbl`, `ldem_85s_40m.lbl`, `ldem_80s_80m.lbl`, and `ldem_60s_240m.lbl` were obtained from that official image-label archive and retained alongside the supplied JP2s. These establish the integer height scaling, dimensions and projection of the corresponding GDRs. No original JP2 bytes were altered.

## Presets

Polar presets are illustrative regional coordinates, not precise registered mission target locations. No claim of approved lander safety or historical touchdown is made for those presets. Use custom coordinates for the exact target a team wants to evaluate.

Apollo 11 Lunar Module coordinates (0.67416°N, 23.47314°E) follow NASA NSSDC's ME/DE421 coordinate table:
https://nssdc.gsfc.nasa.gov/planetary/lunar/lunar_sites.html

Chandrayaan-3 rounded final coordinates (-69.373°, 32.319°E) appear in NASA/JPL IPN Progress Report 42-240A, “Dynamics of a Coherent Reflection on Direct-with-Earth Links between a Planetary Body and an Earth Station” (2025), section on the Vikram lander:
https://www.nasa.gov/wp-content/uploads/2026/02/42-240a.pdf

ISRO's prime landing ellipse coordinate is a planned site and differs from this final touchdown coordinate. The preset intentionally uses the rounded final coordinate for regional comparison, not precision geodesy. The coordinate frame of the rounded report location has not been independently transformed/registered against local DEM features; metre-scale alignment is not claimed.

## Attribution

Credit NASA/JPL NAIF for SPICE data and NASA LRO/LOLA Science Team / NASA PDS Geosciences Node for terrain and archive documentation. Scientific data and supplied research retain their original notices; this prototype and its appearance do not imply NASA endorsement. Keep original labels and this attribution when sharing the project.
