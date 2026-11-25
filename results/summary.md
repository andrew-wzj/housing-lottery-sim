# Simulation results

1000 trials, 1000 students each, 1.05 beds per student, 6 halls. Runtime 73.9s.
All data is synthetic. Numbers are means over trials.

## First-choice hall, by class year

| Rule | Senior | Junior | Sophomore | Freshman | All |
|---|---:|---:|---:|---:|---:|
| average | 84.8% | 79.6% | 55.9% | 38.8% | 63.7% |
| highest | 86.2% | 75.8% | 55.8% | 41.4% | 63.7% |
| lowest | 81.5% | 78.5% | 58.9% | 39.1% | 63.6% |
| pure lottery | 64.1% | 63.7% | 63.8% | 63.5% | 63.8% |
| v1: halls only (average) | 78.7% | 75.4% | 60.1% | 43.6% | 63.7% |

## Top-3 hall, by class year

| Rule | Senior | Junior | Sophomore | Freshman | All |
|---|---:|---:|---:|---:|---:|
| average | 97.7% | 95.7% | 86.0% | 75.1% | 88.2% |
| highest | 98.3% | 93.8% | 85.9% | 76.5% | 88.2% |
| lowest | 95.7% | 94.6% | 87.9% | 75.4% | 88.0% |
| pure lottery | 88.3% | 88.2% | 88.0% | 88.1% | 88.1% |
| v1: halls only (average) | 96.5% | 93.3% | 86.7% | 77.6% | 88.1% |

## Unplaced and split students

| Rule | Unplaced | In a split group | Groups split per lottery |
|---|---:|---:|---:|
| average | 6.2% | 19.1% | 53.0 |
| highest | 6.1% | 19.1% | 52.9 |
| lowest | 6.2% | 19.0% | 52.4 |
| pure lottery | 6.2% | 19.1% | 52.9 |
| v1: halls only (average) | 7.9% | 15.5% | 42.2 |

## Does joining an older group help underclass students?

First-choice rate of sophomores and freshmen, depending on whether their group
has older members.

| Rule | In a mixed-year group | In a same-year group | Gap |
|---|---:|---:|---:|
| average | 58.2% | 46.2% | +11.9 pts |
| highest | 73.1% | 45.1% | +28.0 pts |
| lowest | 42.2% | 50.9% | -8.7 pts |
| pure lottery | 59.7% | 64.5% | -4.8 pts |

## How risky is a short list?

Share of students left unplaced, by how many halls their group listed (average rule).

| Mechanism | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| v2: hall + room size | 16.3% | 8.6% | 6.5% | 5.0% | 4.7% | 4.5% |
| v1: halls only | 27.0% | 11.6% | 8.2% | 6.4% | 5.5% | 4.9% |

## The fallback option

Share of groups that tick "if all our options are full, place us anywhere"
(average rule, v2). Groups that accept splitting also tick "you may split us".
Same campuses and tickets in every column.

| Groups that tick it | 0% | 25% | 50% | 75% | 100% |
|---|---:|---:|---:|---:|---:|
| Unplaced, all students | 7.6% | 6.9% | 6.2% | 5.4% | 4.6% |
| Unplaced, listed 1 hall | 28.1% | 22.2% | 16.3% | 10.6% | 4.7% |
| Placed by the fallback | 0.0% | 0.8% | 1.7% | 2.5% | 3.5% |
| Unplaced, groups of 4 | 21.0% | 19.7% | 18.4% | 17.0% | 15.6% |
| First-choice hall, all | 63.9% | 63.8% | 63.7% | 63.6% | 63.6% |
| Fallback hall, rank in own taste (1-6) | n/a | 3.6 | 3.7 | 3.7 | 3.8 |

## Verifiable draw (rule R5)

Example: before the draw, publish the commitment; after, publish the seed.

- seed: `trial-0`
- SHA-256 commitment: `89a51b8bcbeefb51eb69c1a1d679f83510897e448db01513f25188b0c6f950ed`
