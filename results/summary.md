# Simulation results

1000 trials, 1000 students each, 1.05 beds per student, 6 halls. Runtime 39.4s.
All data is synthetic. Numbers are means over trials.

## First-choice hall, by class year

| Rule | Senior | Junior | Sophomore | Freshman | All |
|---|---:|---:|---:|---:|---:|
| average | 84.8% | 79.7% | 55.7% | 39.6% | 63.9% |
| highest | 86.2% | 76.0% | 55.7% | 42.2% | 64.0% |
| lowest | 81.5% | 78.7% | 58.8% | 39.9% | 63.9% |
| pure lottery | 64.1% | 64.1% | 63.8% | 63.8% | 63.9% |
| v1: halls only (average) | 78.5% | 75.4% | 59.9% | 43.9% | 63.7% |

## Top-3 hall, by class year

| Rule | Senior | Junior | Sophomore | Freshman | All |
|---|---:|---:|---:|---:|---:|
| average | 97.7% | 95.7% | 85.6% | 74.4% | 87.9% |
| highest | 98.4% | 93.8% | 85.6% | 76.1% | 88.0% |
| lowest | 95.5% | 94.5% | 87.3% | 74.7% | 87.7% |
| pure lottery | 87.8% | 87.8% | 87.8% | 87.8% | 87.8% |
| v1: halls only (average) | 96.5% | 93.5% | 86.7% | 77.8% | 88.2% |

## Unplaced and split students

| Rule | Unplaced | In a split group | Groups split per lottery |
|---|---:|---:|---:|
| average | 7.5% | 18.5% | 53.3 |
| highest | 7.4% | 18.5% | 53.3 |
| lowest | 7.7% | 18.2% | 52.5 |
| pure lottery | 7.6% | 18.4% | 53.1 |
| v1: halls only (average) | 7.9% | 15.6% | 42.4 |

## Does joining an older group help underclass students?

First-choice rate of sophomores and freshmen, depending on whether their group
has older members.

| Rule | In a mixed-year group | In a same-year group | Gap |
|---|---:|---:|---:|
| average | 58.1% | 46.6% | +11.5 pts |
| highest | 73.0% | 45.6% | +27.4 pts |
| lowest | 42.4% | 51.3% | -8.9 pts |
| pure lottery | 60.0% | 64.6% | -4.6 pts |

## How risky is a short list?

Share of students left unplaced, by how many halls their group listed (average rule).

| Mechanism | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| v2: hall + room size | 28.2% | 12.1% | 8.0% | 5.4% | 4.3% | 4.4% |
| v1: halls only | 26.7% | 11.7% | 8.2% | 6.5% | 5.2% | 4.8% |

## Verifiable draw (rule R5)

Example: before the draw, publish the commitment; after, publish the seed.

- seed: `trial-0`
- SHA-256 commitment: `89a51b8bcbeefb51eb69c1a1d679f83510897e448db01513f25188b0c6f950ed`
