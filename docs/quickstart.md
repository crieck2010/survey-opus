# Quickstart

End-to-end OPUS run in three commands: **validate → submit → parse**.

## 1. Validate

```bash
survey-opus validate ./TESTRV0010.26o
```

Example output:

```
RINEX header summary
  RINEX version : 2.11
  Marker name   : TESTRV
  Antenna type  : TRM59900.00
  Antenna height: 0.000 m
  Approx XYZ    : 1113194.973, -4844136.215, 3985342.567 m (ECEF)
  First obs     : 2026-10-01 00:00:00
  Last obs      : 2026-10-01 04:00:00
  Constellations: G
  Interval      : 30.0 s

OK: file looks submittable to OPUS.
```

Exit codes: `0` = looks submittable, `1` = problems listed, `2` = file unreadable
or unparsable. If it reports problems, fix the underlying issue (usually antenna
metadata or a too-short session) before submitting.

## 2. Submit

```bash
survey-opus submit ./TESTRV0010.26o \
  --email you@example.com \
  --antenna-type TRM59900.00 \
  --antenna-height 1.842 \
  --mode static
```

Notes:

- `--antenna-type` must match the NGS antenna list exactly (e.g. `TRM59900.00`,
  `TRM57971.00`, `EML_REACH_RS2`). `NONE` means "unknown" — avoid it; the
  solution will be worse without a calibration model.
- `--antenna-height` is in **meters**, antenna reference point (ARP) to marker.
  Measure carefully — a wrong height biases every elevation you derive.
- `--mode static` (default, needs ≥ 2 h of data) or `--mode rapid-static`
  (needs ≥ 15 min).
- Filenames must be ≤ 44 characters with no `!@#$%^&*()+=` characters.

On success you get a receipt with the NGS sequence number. The solution report
arrives **by email in ~10–30 minutes**. There is no status page — do not
re-submit while waiting (see `etiquette.md`).

## 3. Parse

Save the emailed report as a text file, then:

```bash
survey-opus parse ./opus_report.txt
survey-opus parse ./opus_report.txt --json   # for scripts / downstream tools
```

The human summary prints NAD 83 and ITRF coordinates, UTM/SPC grid values, RMS,
observation and ambiguity statistics, peak-to-peak spreads, the base stations
NGS used, and the software/ephemeris provenance lines. `--json` emits the same
content as a JSON document.

## Same thing from Python

```python
from survey_opus import parse_header, validate_for_opus, submit, parse_solution

header = parse_header("TESTRV0010.26o")
assert validate_for_opus(header) == []

receipt = submit("TESTRV0010.26o", "you@example.com",
                 "TRM59900.00", 1.842, mode="static")

solution = parse_solution(open("opus_report.txt").read())
print(solution.nad83.lat_deg, solution.nad83.lon_deg)
```

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `validate` lists "session too short" | Occupation < 2 h (static) or < 15 min (rapid-static) |
| `submit` fails immediately | Bad email format, missing file, or antenna fields empty |
| No email after 60+ min | Spam folder first; then check the NGS OPUS page for service notices — do not just re-submit |
| `parse` says "not an OPUS report" | The file isn't a solution report (e.g. it's a rejection notice or an email wrapper) — open it and read what NGS actually said |
