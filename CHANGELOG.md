# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-08

### Added
- `survey_opus.rinex`: RINEX observation-header parser (`parse_header`) and
  OPUS pre-submission check (`validate_for_opus`); `RinexError` on malformed input.
- `survey_opus.client`: OPUS upload client (`submit`) targeting the verified
  NGS endpoints (static + rapid-static), multipart/form-data POST, works with
  `requests` when installed and stdlib `urllib` otherwise; injectable
  `session` for mock-HTTP tests (zero live submissions during build).
- `survey_opus.client`: OPUS solution-report parser (`parse_solution`) and
  JSON export (`solution_to_json`); `OpusSolution` dataclass with NAD83/ITRF
  coordinates, UTM/SPC grids, RMS, observation/ambiguity statistics,
  peak-to-peak spreads, base-station list, and provenance lines.
- `survey-opus` console CLI: `validate`, `submit` (with NGS etiquette note in
  `--help`), and `parse` (human summary or `--json`); stdlib only.
- Docs: README, `docs/quickstart.md`, `docs/api.md`, `docs/opus-workflow.md`,
  `docs/etiquette.md`; MIT license; pytest suite incl. CLI tests.
- Upload endpoint verified live 2026-10-08 against the post-migration NGS URLs
  (`/OPUS-cgi/OPUS/Upload/Opusup.prl`, `/OPUS-cgi/OPUS/Upload/Opus-rsup.prl`).

### Notes
- NGS emails the solution report; there is no polling/status API, so v0.1.0
  intentionally has no job-tracking — submit, then watch your inbox.
- Zero intra-suite imports at v0.1.0; integration with survey-geodesy /
  survey-cogo conventions is planned for a later release.
