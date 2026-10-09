# survey-opus

A Python client for **NOAA NGS OPUS** (Online Positioning User Service) — part of the
[Surveying Suite](https://github.com/crieck2010). Validate RINEX observation files,
submit them to OPUS, and parse the emailed solution reports, from the command line or
from Python.

OPUS takes your GNSS receiver's raw observation data and returns a high-accuracy
survey-grade position by post-processing it against the CORS (Continuously Operating
Reference Station) network. It is the standard free way to get centimeter-level
coordinates on a static GNSS occupation in the United States.

## What OPUS is

OPUS is a free online service run by NOAA's National Geodetic Survey. You upload a
RINEX observation file from a static GNSS occupation; NGS downloads precise satellite
orbits, picks the three nearest CORS base stations, runs a baseline solution, and
emails you a report with your position in NAD 83 and ITRF, plus UTM and State Plane
grid coordinates. Typical accuracy for a 2+ hour static session is **1–3 cm horizontal
and 2–5 cm vertical** (1-sigma).

There are two variants (see `docs/opus-workflow.md`):

| Variant | Minimum data | Accuracy | Use case |
|---|---|---|---|
| **OPUS Static** | ≥ 2 hours | ~1–3 cm horizontal | Control points, boundary ties |
| **OPUS Rapid-Static (OPUS-RS)** | ≥ 15 minutes | ~2–5 cm horizontal | Quick control when time is tight |

## Install

Requires Python ≥ 3.10. Zero required dependencies — plain `pip` install.

```bash
git clone https://github.com/crieck2010/survey-opus.git
cd survey-opus
pip install -e .
```

This installs the `survey-opus` console command. The upload path uses `requests` if
it happens to be installed, and falls back to stdlib `urllib` otherwise — no extra
install needed either way:

```bash
pip install -e ".[network]"   # optional: use requests for uploads
```

## Quickstart

The full workflow is three commands: **validate → submit → parse**.

### 1. Validate your RINEX file

```bash
survey-opus validate ./data/TESTRV0010.26o
```

Prints a header summary (marker, antenna, session span, constellations) and lists any
problems that would block submission — e.g. a session too short for the chosen mode.
Exit code 0 means the file looks submittable.

### 2. Submit to OPUS

```bash
survey-opus submit ./data/TESTRV0010.26o \
  --email you@example.com \
  --antenna-type TRM59900.00 \
  --antenna-height 1.842 \
  --mode static
```

Use the antenna model exactly as NGS lists it (no `NONE` — that means "unknown" and
degrades the solution), and the measured antenna height in meters (antenna reference
point to survey marker).

NGS emails the solution report to `--email` in roughly 10–30 minutes. **There is no
status page and no polling API** — go do something else and watch your inbox. Run
`survey-opus submit --help` to see the NGS etiquette note; the short version is:
one job at a time, don't re-submit to "check".

### 3. Parse the report

Save the emailed report to a file, then:

```bash
survey-opus parse ./data/opus_report.txt          # human-readable summary
survey-opus parse ./data/opus_report.txt --json   # machine-readable JSON
```

## The OPUS workflow, in brief

1. **Occupy** — set up on the point, measure the antenna height (slant or vertical,
   recorded carefully), log raw data for the full session.
2. **Convert** — export RINEX from the receiver (Trimble Business Center, Emlid Flow,
   etc.). Keep the original filename short (≤ 44 chars, no special characters).
3. **Validate** — `survey-opus validate` catches header problems before you waste a
   queue slot.
4. **Submit** — `survey-opus submit` uploads the file; NGS acknowledges and queues it.
5. **Wait** — the report arrives by email. Do not submit a second job meanwhile.
6. **Parse** — `survey-opus parse` turns the report into a summary or JSON you can
   feed downstream.

Details on static vs rapid-static, accuracy expectations, how NGS picks base
stations, and what each report section means: `docs/opus-workflow.md`.

## NGS etiquette

OPUS is a free public resource. Be a good citizen (full version: `docs/etiquette.md`):

- **One submission at a time.** Wait for the result email before submitting again.
- **Results arrive by email** (10–30 min typical). There is no polling API; re-submitting
  to "check on it" just clogs the queue for everyone.
- **Get the metadata right.** Antenna type and height are the two most common ways to
  silently ruin a solution — and waste NGS compute doing it.
- **Respect the minimums.** ≥ 2 h for static, ≥ 15 min for rapid-static. Shorter
  sessions get rejected after consuming processing time.

## API reference

Full reference: `docs/api.md`. The short version:

```python
from survey_opus import (
    parse_header, validate_for_opus, RinexError,   # RINEX side
    submit, parse_solution, solution_to_json,      # OPUS side
    OpusSolution, OpusError,
    OPUS_UPLOAD_URL, OPUS_RS_UPLOAD_URL,
)

# 1. Read and check the file
header = parse_header("TESTRV0010.26o")   # raises RinexError if malformed
problems = validate_for_opus(header)      # [] means submittable
print(header.marker_name, header.antenna_type, header.start_time, header.end_time)

# 2. Submit (uses requests if available, else urllib)
receipt = submit("TESTRV0010.26o", "you@example.com",
                 antenna_type="TRM59900.00", antenna_height=1.842,
                 mode="static")
print(receipt.response_status, receipt.seqnum)

# 3. Parse the emailed report later
solution: OpusSolution = parse_solution(report_text)
print(solution.nad83.lat_deg, solution.nad83.lon_deg, solution.nad83.ell_ht_m)
print(solution_to_json(solution))         # JSON string for downstream tools
```

`submit()` accepts an optional `session=` argument (any requests-like object) so tests
can inject a mock — no live submissions in the test suite.

## Interop with the Surveying Suite

The parsed solution's coordinates are plain decimal degrees / meters in named
reference frames (`Coordinate.frame` like `"NAD83(2011)"`, epoch included), ready to
feed survey-geodesy (datum/epoch handling) and survey-cogo conventions downstream.

**v0.1.0 has zero intra-suite imports by design** — `survey-opus` stands alone so the
OPUS client stays usable and testable in isolation. Integration with survey-geodesy
(datum transformations on the ITRF/NAD83 pair) and survey-cogo (coordinate geometry
from OPUS control) is planned for a later release.

## Honest limitations

- **The report is emailed by NGS — there is no polling or status API.** v0.1.0
  deliberately has no job tracking: submit, then watch your inbox.
- **Endpoint verified 2026-10-08.** NGS is actively migrating their website; the
  upload URLs used here were verified live on 2026-10-08, but NGS may change them.
  If submissions start failing, check https://www.ngs.noaa.gov/OPUS/ first.
- **Parser targets the standard/extended OPUS report format.** Unusual reports
  (rejected jobs, abridged formats) may parse partially — `parse_solution` raises
  `OpusError` on anything it can't recognize as an OPUS report rather than guessing.
- OPUS covers the US CORS network footprint. Outside it, use the equivalent service
  for your region (e.g. AUSPOS, CSRS-PPP).
- Antenna calibration matters: results are only as good as the antenna type/height
  metadata you submit.

## Development

```bash
pip install -e ".[network]"   # editable install
python -m pytest              # full test suite (mock HTTP only — never hits NGS)
```

See `docs/` for the quickstart, full API reference, the OPUS workflow explainer, and
the etiquette guide. `CHANGELOG.md` tracks releases (semver).

## License

MIT — © 2026 Charles Rieck. See `LICENSE`.
