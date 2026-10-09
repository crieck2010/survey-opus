# The OPUS service, explained

## What OPUS does

OPUS (Online Positioning User Service) is NOAA's National Geodetic Survey free
post-processing service. You upload a RINEX observation file from a static GNSS
occupation; NGS:

1. Downloads precise satellite orbits and clocks for your observation window.
2. Selects the **three nearest CORS** (Continuously Operating Reference Station)
   base stations to your approximate position.
3. Forms double-difference baselines from your rover to each base, fixes carrier
   integer ambiguities, and computes your position.
4. Emails you a solution report with coordinates, statistics, and metadata.

Because it uses precise ephemerides and a network solution rather than a single
base, OPUS routinely beats a single-baseline RTK fix in absolute accuracy for
static work.

## The two variants

### OPUS Static

- **Minimum session: 2 hours** of continuous data (more is better; 4+ h is the
  sweet spot for the tightest uncertainties).
- Expected accuracy: **~1–3 cm horizontal, ~2–5 cm vertical** (1-sigma).
- Uses precise orbits (available ~12–18 days after observation) — or rapid
  orbits if you submit sooner, with slightly larger uncertainties.
- Use for: control points, boundary ties, anything that becomes legal evidence
  or long-lived datum.

### OPUS Rapid-Static (OPUS-RS)

- **Minimum session: 15 minutes.**
- Expected accuracy: **~2–5 cm horizontal** under good conditions.
- Works by holding the nearest CORS station fixed and solving a short baseline
  to your point; needs clean data (low multipath, good sky).
- Use for: quick project control, photo-control points, reconnaissance
  positions where static's 2-hour minimum is impractical.

Pick the variant with `--mode static | rapid-static` (default: static).

## Base-station selection

NGS picks the three closest CORS stations automatically — you don't choose.
The report lists them (parsed into `OpusSolution.base_stations`), with baseline
lengths. Shorter baselines generally mean better ambiguity resolution; if your
nearest CORS is 100+ km away, expect larger uncertainties and read the
peak-to-peak values carefully.

## What each report section means

A standard OPUS solution report contains, roughly top to bottom:

- **Header** — your email, the RINEX filename, processing date.
- **REF FRAME / EPOCH** — the two realizations reported: NAD 83 (current
  realization, e.g. NAD 83 (2011) epoch 2010.0000) and the ITRF realization at
  the observation epoch. NAD 83 is what US surveyors record; ITRF is the global
  frame the solution is actually computed in.
- **XYZ / LAT-LON-EL HT** — geocentric coordinates and geodetic
  latitude/longitude/ellipsoidal height for each frame, with 1-sigma RMS per
  component. These are the numbers you take downstream.
- **UTM / SPC** — the same position projected to UTM and State Plane
  coordinates (meters), for direct use on plats and in CAD.
- **Overall RMS / observations used / ambiguities fixed** — solution quality:
  overall RMS in meters, % of observations that survived QC, and % of carrier
  ambiguities fixed to integers. Low fixed-% (< 80% or so) is a red flag —
  re-observe rather than trusting the position.
- **Peak-to-peak** — the spread between the three independent single-base
  solutions (lat/lon/ht or north/east/up, in meters). This is your honest
  external accuracy check: if peak-to-peak is 8 cm, your "2 cm RMS" is
  optimistic.
- **Base stations** — the CORS stations used, with data spans.
- **Software / ephemeris** — which NGS processing software and which orbit
  product (precise vs rapid) produced the solution. Keep these with the
  coordinates for traceability.

## Accuracy expectations, honestly

Published "1–3 cm" numbers assume: ≥ 2 h session, good sky view, correct antenna
type and height, nearby CORS, precise orbits. Real-world degraders: tree canopy,
multipath near buildings/vehicles, wrong antenna calibration, short sessions,
distant base stations. **Read the peak-to-peak spread, not just the RMS** — it
is the closest thing the report gives you to an independent check. For anything
legally binding, occupy twice on different days and compare.

## Coverage

OPUS solves against the US CORS network (plus some stations in neighboring
regions). Outside North America, use your region's equivalent service
(e.g. AUSPOS for Australia, CSRS-PPP for Canada/global).
