# Drainage Design QC

**A small, inspectable screening tool for circular drainage pipes.**

A spreadsheet may contain a reversed invert, an undersized trial diameter or insufficient cover.
This demo turns those checks into a repeatable report with named findings and traceable inputs.

**Portfolio demo · synthetic data · Python · deterministic engineering checks**

## Try the example

```sh
python3 drainage_qc.py examples/pipes.csv --out reports
```

The three-pipe fixture contains one reach without screening findings, one overloaded reach with
low cover, and one adverse slope. [Read the generated example](examples/expected/report.md).
No slope-based capacity is calculated for a non-positive slope.

```mermaid
flowchart LR
    A[Pipe schedule CSV] --> B[Validate units and identifiers]
    B --> C[Runoff and full-flow reference]
    C --> D[Named QC findings]
    D --> E[Engineer reviews assumptions]
```

## Methods and units

- Rational peak flow: `Q = C × i × A / 360`, with `i` in mm/hour, `A` in hectares and `Q` in m³/s.
- Pipe slope: `(upstream invert − downstream invert) / length` in m/m.
- Full circular area: `Ap = πD²/4`; hydraulic radius: `R = D/4`, with `D` in metres.
- SI Manning reference: `Qfull = (1/n) × Ap × R^(2/3) × sqrt(S)`.
- Crown cover: `ground level − invert level − outside diameter`; the smaller endpoint cover is reported.
- Reference velocity: `Qfull/Ap`. This is not the actual velocity at the estimated demand.

The unit conversion in the Rational formula is `0.001 × 10000 / 3600 = 1/360`.
For a hand check, `C=1`, `i=360 mm/h` and `A=1 ha` produce `1 m³/s`.

## Input contract

| CSV field | Unit / rule |
|---|---|
| `pipe_id` | Unique, nonblank identifier |
| `length_m` | Metres, greater than zero |
| `diameter_mm` | Internal diameter in millimetres, greater than zero |
| `outside_diameter_mm` | Outside diameter in millimetres, at least the internal diameter; used for crown cover |
| `invert_up_m`, `invert_down_m` | Metres, common vertical datum |
| `ground_up_m`, `ground_down_m` | Metres, same datum as inverts |
| `manning_n` | SI Manning roughness coefficient, greater than zero |
| `catchment_ha` | Hectares, non-negative; entire contributing area for this independent reach |
| `runoff_coefficient` | Dimensionless, between 0 and 1 |
| `intensity_mm_hr` | mm/hour, non-negative; supplied by the user |

[`examples/demo_criteria.json`](examples/demo_criteria.json) contains illustrative criteria:
0.9 m endpoint cover and 0.6–3.0 m/s full-flow reference velocity. These are demo settings,
not a universal design standard. Change them only with a documented project basis.

## Scope and next extension

Each row is independent. The tool does not accumulate upstream flows, select an IDF intensity,
calculate time of concentration, assess inlet capture, solve partial flow, backwater, surcharge,
hydraulic grade line, structural loading or local-code compliance. It assumes pipe slope represents
energy slope for its uniform-flow reference. The supplied outside diameter is used for cover and the internal diameter for hydraulic capacity.
Endpoint cover cannot find a low point between endpoints.

The next useful extension is a reviewed network topology and hydraulic solver integration.
AI could help explain the findings, but it should not replace these calculations or invent criteria.

## References

The [TxDOT Rational Method guidance](https://www.txdot.gov/content/txdotoms/us/en/manuals/des/hyd/chapter-4--hydrology/section-12--rational-method/procedure-for-using-the-rational-method.html)
defines the metric runoff inputs and conversion. The [USBR normal-flow guidance](https://www.usbr.gov/tsc/techreferences/mands/wmm/chap02_16.html)
explains hydraulic radius and the uniform-flow setting. These are method references, not a claim
that this demo implements a jurisdiction's drainage standard.

## Trust and reproducibility

All included data is synthetic. This is an AI-assisted portfolio demo, not an employment project
or production system. See [provenance](PROVENANCE.md) and the [MIT license](LICENSE).
Input hashes in `report.json` identify the exact files used. Examples are deterministic and run offline.
The code uses Python's standard library; no API key, paid service or additional package is needed.

Run from this repository's folder using Python 3.9 or newer. The supplied version was locally tested
on Python 3.9.6. A GitHub Actions workflow is included for Python 3.11 and 3.13; hosted runs are not
claimed until the repository is uploaded and those checks run.

```sh
python3 -m unittest discover -s tests -v
```

On Windows, use `py -3` in place of `python3`. On systems where Python 3 is named `python`, use that.
Output folders contain `report.md` for reading and `report.json` for further analysis.
Normal execution returns 0 after generating a report; `--fail-on-findings` returns 1 when review is
needed. Invalid input or an output error returns 2. Required CSV cells must be nonblank, numbers
must be finite, and duplicate identifiers are rejected. Extra CSV columns are ignored.

## Explain it in an interview

Walk through one input, show a deliberate error, explain the result, and describe what the tool
cannot establish. The value is a reproducible review process with visible assumptions.
Do not claim production use, savings, compliance approval or independent authorship of AI-assisted work.
