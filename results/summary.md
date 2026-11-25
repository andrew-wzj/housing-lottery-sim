# Simulation results

1000 trials, 1000 students each, 1.05 beds per student, 6 halls. Runtime 23.0s.
All data is synthetic. Numbers are means over trials.

## First-choice hall, by class year

| Rule | Senior | Junior | Sophomore | Freshman | All |
|---|---:|---:|---:|---:|---:|
| average | 78.8% | 75.7% | 59.7% | 44.4% | 63.9% |
| highest | 79.2% | 73.6% | 59.3% | 45.6% | 63.7% |
| lowest | 76.7% | 75.2% | 61.0% | 45.7% | 64.0% |
| pure lottery | 63.9% | 63.9% | 63.4% | 63.9% | 63.8% |

## Top-3 hall, by class year

| Rule | Senior | Junior | Sophomore | Freshman | All |
|---|---:|---:|---:|---:|---:|
| average | 96.5% | 93.6% | 86.5% | 77.8% | 88.2% |
| highest | 97.1% | 91.5% | 86.8% | 78.8% | 88.1% |
| lowest | 95.1% | 93.3% | 87.0% | 78.5% | 88.2% |
| pure lottery | 88.3% | 88.3% | 87.9% | 88.2% | 88.2% |

## Unplaced and split students

| Rule | Unplaced | In a split group | Split operations per lottery |
|---|---:|---:|---:|
| average | 7.9% | 15.5% | 45.1 |
| highest | 7.9% | 15.4% | 44.7 |
| lowest | 8.0% | 15.6% | 45.7 |
| pure lottery | 7.9% | 15.4% | 45.0 |

## Does joining an older group help underclass students?

First-choice rate of sophomores and freshmen, depending on whether their group
has older members.

| Rule | In a mixed-year group | In a same-year group | Gap |
|---|---:|---:|---:|
| average | 60.8% | 51.1% | +9.7 pts |
| highest | 68.1% | 50.5% | +17.6 pts |
| lowest | 48.6% | 54.6% | -6.0 pts |
| pure lottery | 59.8% | 64.6% | -4.7 pts |

## How risky is a short list?

Share of students left unplaced, by how many halls their group ranked (average rule).

| Halls ranked | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| Unplaced | 26.7% | 11.7% | 8.1% | 6.5% | 5.6% | 4.9% |

## Verifiable draw (rule R5)

Example: before the draw, publish the commitment; after, publish the seed.

- seed: `trial-0`
- SHA-256 commitment: `89a51b8bcbeefb51eb69c1a1d679f83510897e448db01513f25188b0c6f950ed`
