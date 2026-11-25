# housing-lottery-sim

A simulation of a college housing lottery, written to revisit a senior capstone project
(a housing lottery app built for a college's residence life office, 2023–24). The original
app collected applications; it never assigned rooms. This project designs and tests the
missing part: the assignment rules.

All halls, students and numbers here are synthetic. No real student data is used.

## Rules

- **Groups** of 1–4 students form by mutual confirmation; one gender category per group.
- **Priority** = the average class-year points of the members (senior 4 … freshman 1).
- **One random ticket per group** breaks ties within the same priority, so group size
  does not change the odds.
- **Verifiable draw**: the SHA-256 hash of the seed is published before the draw and the
  seed after, so anyone can recompute the order.
- Groups rank **1 to 6 halls** (not forced to fill all six).
- Groups say in advance whether they may be **split** if no room fits them.

## Algorithm

Random Serial Dictatorship: groups take turns in lottery order. On its turn, a group gets
the smallest room that fits it in the highest-ranked hall that still has one. If none
fits, a group that agreed to splitting is halved and both halves try again right away;
otherwise it goes to the admin's unplaced list. Ranking halls honestly is always a
group's best strategy; `tests/test_assign.py` checks this by brute force.

## Run

```sh
python3 -m unittest            # tests (standard library only, Python 3.9+)
python3 simulate.py --trials 1000 --out results
```

`simulate.py` builds a synthetic campus per trial, draws one set of tickets, and runs the
assignment under four priority rules (average, highest, lowest, pure lottery) on the same
inputs. Results go to `results/summary.md` and `results/summary.csv`.

## Limitations

- Groups and preferences are generated, not observed; real students would form groups
  differently in response to the rules.
- Rooms are assigned by hall and size; exact room numbers stay an admin step.
