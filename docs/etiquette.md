# NGS etiquette

OPUS is a **free public service** run by NOAA's National Geodetic Survey. The
compute queue is shared by every surveyor in the country. These rules aren't
optional politeness — they're how the service stays usable.

## The rules

1. **One submission at a time.** Submit a job, wait for the result email, then
   submit the next. Never have two jobs in flight.
2. **Results arrive by email (typically 10–30 minutes).** There is no status
   page and no polling API. Do not re-submit to "check on" a job — duplicates
   just clog the queue for everyone behind you.
3. **Get the metadata right the first time.** Antenna type and antenna height
   are the two most common silent solution-killers. A wrong antenna model means
   no (or wrong) phase-center calibration; a wrong height biases every height
   you derive. Double-check before you submit — every bad job wastes NGS
   processing time that could have served someone else.
4. **Respect the session minimums.** ≥ 2 hours for static, ≥ 15 minutes for
   rapid-static. Submitting a 40-minute file to static doesn't get you a
   solution faster; it gets you a rejection after consuming queue time.
5. **Keep filenames clean.** ≤ 44 characters, no `!@#$%^&*()+=` characters.
   Odd filenames can fail the upload form outright.

## If something goes wrong

- **No email after 60+ minutes:** check spam first, then look for NGS service
  notices on the OPUS page. Still nothing? Wait — do not hammer re-submits.
- **Rejection notice instead of a solution:** read it. NGS tells you why
  (short session, bad header, no precise orbits yet for the date, etc.). Fix
  the cause and submit once.
- **Suspicious coordinates:** check the peak-to-peak spread and % ambiguities
  fixed in the report before blaming the service. Re-occupy the point on a
  different day if it matters.

## Why this matters to the suite

`survey-opus validate` exists precisely so bad files never reach NGS: run it
locally, fix problems locally, and only spend queue time on files that are
actually submittable. `survey-opus submit --help` prints a condensed version of
this note so it's in front of you every time you submit.
