# Simulation results

1000 trials, 1000 students each, 1.05 beds per student, 6 halls. Runtime 71.7s.
All data is synthetic. Numbers are means over trials.

## First-choice hall, by class year

| Rule | Senior | Junior | Sophomore | Freshman | All |
|---|---:|---:|---:|---:|---:|
| average | 84.8% | 79.6% | 55.9% | 39.2% | 63.8% |
| highest | 86.2% | 75.8% | 55.8% | 41.8% | 63.8% |
| lowest | 81.5% | 78.5% | 58.9% | 39.5% | 63.7% |
| pure lottery | 64.2% | 63.8% | 63.9% | 63.6% | 63.9% |
| v1: halls only (average) | 78.7% | 75.4% | 60.1% | 43.6% | 63.7% |

## Top-3 hall, by class year

| Rule | Senior | Junior | Sophomore | Freshman | All |
|---|---:|---:|---:|---:|---:|
| average | 97.7% | 95.7% | 85.7% | 74.5% | 87.9% |
| highest | 98.3% | 93.8% | 85.5% | 75.9% | 87.9% |
| lowest | 95.6% | 94.5% | 87.6% | 74.7% | 87.8% |
| pure lottery | 88.0% | 87.9% | 87.7% | 87.9% | 87.9% |
| v1: halls only (average) | 96.5% | 93.3% | 86.7% | 77.6% | 88.1% |

## Unplaced and split students

| Rule | Unplaced | In a split group | Groups split per lottery |
|---|---:|---:|---:|
| average | 6.9% | 18.4% | 53.0 |
| highest | 6.8% | 18.3% | 52.9 |
| lowest | 7.0% | 18.2% | 52.4 |
| pure lottery | 6.9% | 18.3% | 52.9 |
| v1: halls only (average) | 7.9% | 15.5% | 42.2 |

## Does joining an older group help underclass students?

First-choice rate of sophomores and freshmen, depending on whether their group
has older members.

| Rule | In a mixed-year group | In a same-year group | Gap |
|---|---:|---:|---:|
| average | 58.2% | 46.5% | +11.7 pts |
| highest | 73.1% | 45.4% | +27.7 pts |
| lowest | 42.4% | 51.1% | -8.7 pts |
| pure lottery | 59.8% | 64.6% | -4.8 pts |

## How risky is a short list?

Share of students left unplaced, by how many halls their group listed (average rule).

| Mechanism | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| v2: hall + room size | 19.7% | 10.4% | 7.5% | 5.5% | 4.8% | 4.5% |
| v1: halls only | 27.0% | 11.6% | 8.2% | 6.4% | 5.5% | 4.9% |

## The fallback option

Share of groups that tick "if all our options are full, place us anywhere"
(average rule, v2). Same campuses and tickets in every column.

| Groups that tick it | 0% | 25% | 50% | 75% | 100% |
|---|---:|---:|---:|---:|---:|
| Unplaced, all students | 7.6% | 7.3% | 6.9% | 6.6% | 6.2% |
| Unplaced, listed 1 hall | 28.1% | 23.9% | 19.7% | 15.6% | 11.5% |
| Placed by the fallback | 0.0% | 0.4% | 0.8% | 1.2% | 1.6% |
| First-choice hall, all | 63.9% | 63.9% | 63.8% | 63.8% | 63.8% |
| Fallback hall, rank in own taste (1-6) | n/a | 3.8 | 3.9 | 4.0 | 4.1 |

## Verifiable draw (rule R5)

Example: before the draw, publish the commitment; after, publish the seed.

- seed: `trial-0`
- SHA-256 commitment: `89a51b8bcbeefb51eb69c1a1d679f83510897e448db01513f25188b0c6f950ed`
