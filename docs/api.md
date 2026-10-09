# API reference

All public names are re-exported from the top-level `survey_opus` package.

## Endpoints

```python
OPUS_UPLOAD_URL     # "https://www.ngs.noaa.gov/OPUS-cgi/OPUS/Upload/Opusup.prl"     (static)
OPUS_RS_UPLOAD_URL  # "https://www.ngs.noaa.gov/OPUS-cgi/OPUS/Upload/Opus-rsup.prl"  (rapid-static)
```

Verified live 2026-10-08 (the pre-migration `/OPUScgi/...` URL now 404s; NGS is
migrating their site, so re-check if uploads fail in the future).

## RINEX — `survey_opus.rinex`

```python
parse_header(path: str | Path) -> RinexHeader
```

Parse a RINEX 2.x/3.x observation header. Raises `RinexError(ValueError)` on
malformed input.

```python
validate_for_opus(header: RinexHeader) -> list[str]
```

Return a list of problem strings; empty list means the file looks submittable.

```python
@dataclasses.dataclass
class RinexHeader:
    rinex_version: str            # e.g. "2.11", "3.04"
    marker_name: str
    antenna_type: str             # from ANT # / TYPE header
    antenna_height: float         # meters (ANTENNA: DELTA H/E/N -> H)
    approx_position: tuple[float, float, float]  # XYZ ECEF, meters
    start_time: datetime          # TIME OF FIRST OBS
    end_time: datetime | None     # TIME OF LAST OBS (may be None)
    constellations: set[str]      # {"G","R","E","C","J",...}
    obs_types: dict[str, list[str]]  # per-constellation codes (RINEX3); flat list (RINEX2)
    interval: float | None

class RinexError(ValueError): ...
```

## Client — `survey_opus.client`

```python
submit(rinex_path, email, antenna_type, antenna_height,
       mode="static", timeout=60, session=None) -> SubmissionReceipt
```

- `mode`: `"static"` or `"rapid-static"` (selects the endpoint).
- Validates the email format and the file before any network traffic.
- Uses `requests` when installed, stdlib `urllib` otherwise.
- `session`: optional requests-like object — inject a mock in tests so the suite
  never touches the live NGS endpoint.
- Raises `OpusError` on transport/validation failure.

```python
@dataclasses.dataclass
class SubmissionReceipt:
    submitted_at: str; email: str; rinex_filename: str
    antenna_type: str; antenna_height: float; mode: str
    endpoint_url: str; seqnum: str
    response_status: int; response_excerpt: str
```

```python
parse_solution(report_text: str) -> OpusSolution
```

Parse an OPUS solution report (the emailed text). Raises `OpusError` if the text
is not recognizable as an OPUS report — it never guesses.

```python
solution_to_json(solution: OpusSolution) -> str
```

Serialize the solution to a JSON string (frames, coordinates, statistics,
base stations, provenance).

```python
@dataclasses.dataclass
class Coordinate:      # one realization
    frame: str         # "NAD83(2011)" / "ITRF2014" (as reported)
    epoch: str         # e.g. "2010.0000"
    lat_deg: float; lon_deg: float   # decimal degrees, lon signed (-180..180)
    ell_ht_m: float

@dataclasses.dataclass
class GridCoordinate:
    system: str        # "UTM" / "SPC"
    zone: str          # "18N" / "NY W-3101" as reported
    northing_m: float; easting_m: float

@dataclasses.dataclass
class OpusSolution:
    file: str; email: str; processing_date: str
    nad83: Coordinate | None; itrf: Coordinate | None
    utm: GridCoordinate | None; spc: GridCoordinate | None
    overall_rms_m: float | None
    pct_obs_used: float | None; pct_ambiguities_fixed: float | None
    peak_to_peak_m: dict[str, float]   # {"lat":..,"lon":..,"ht":..} etc.
    base_stations: list[str]
    software: str; ephemeris: str
    raw_text: str

class OpusError(Exception): ...
```

## CLI — `survey_opus.cli`

`main(argv: list[str] | None = None) -> int` — entry point for the
`survey-opus` console script; returns an int exit code. Subcommands:

- `validate <rinex>` → 0 submittable / 1 problems listed / 2 unreadable.
- `submit <rinex> --email E --antenna-type T --antenna-height H
  [--mode static|rapid-static] [--timeout S]` → prints the receipt; 2 on failure.
  `submit --help` prints the NGS etiquette note.
- `parse <report.txt> [--json]` → human summary or JSON; 2 on failure.
