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
- Groups rank **(hall, room size) options** from 1 to 6 halls, for example
  "Alder quad > Cedar triple > Alder doubles (split)". Listing a room size smaller than the
  group is how a group agrees to split; it then splits only inside that hall.

- A group may tick **"if all our options are full, place us anywhere"**. After its listed
  options fail, it gets the tightest room in any hall that holds the whole group. A second
  box, "you may split us if needed", lets it be halved when the whole group fits nowhere. The form warns groups that list only one or two halls, using the simulated risk.

## Algorithm

Random Serial Dictatorship over options: groups take turns in lottery order. On its turn,
a group gets the first option on its list that can be filled completely (every piece of
the group in its own room of that size, all in that hall). Nothing is reserved unless the
whole option fits. If no option fits, the group goes to the admin's unplaced list.
Listing options honestly is always a group's best strategy, including split options;
`tests/test_assign.py` checks this by brute force on small cases.

`assign_v1` keeps the first design for comparison: groups rank halls only, the room is
picked by best fit, and a group that allowed it is halved automatically when nothing fits.

## Run

```sh
python3 -m unittest            # tests (standard library only, Python 3.9+)
python3 simulate.py --trials 1000 --out results
```

`simulate.py` builds a synthetic campus per trial, draws one set of tickets, and runs the
assignment under four priority rules (average, highest, lowest, pure lottery) plus the v1
mechanism, all on the same inputs. Results go to `results/summary.md` and `results/summary.csv`.

## Limitations

- Groups and preferences are generated, not observed; real students would form groups
  differently in response to the rules.
- Rooms are assigned by hall and size; exact room numbers stay an admin step.
- How groups order their options (together first vs. same hall first) is an assumption
  (`together_first_share`, default 0.5) and moves the split rate noticeably.
