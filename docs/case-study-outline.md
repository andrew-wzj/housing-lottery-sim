# Case study outline: Revisiting the Housing Lottery

Working title: **"We Built the Form. We Never Built the Lottery."**
Subtitle: A 2023 capstone project, revisited in 2026: redefining the problem, designing the
rules, and testing them with simulation.

Audience: portfolio readers (engineering and education hiring). Length: about 2,000–2,500
words, 4–5 charts. All simulation data is synthetic; no Gordon code or student data is used.

---

## 1. Opening (about 150 words)

- The one-sentence hook: in 2023–24 our team built a housing lottery app for a college's
  residence life office. Students loved the form. But the app never decided who lives where.
- What this piece does: go back to the question we skipped, design the rules, and test them.

## 2. The original project, 2023–24 (about 400 words)

- Customer: the Director of Residence Life and Housing. Old process: Google Forms plus
  manual sorting, or software too expensive for the budget.
- Needs from the problem statement: move the form into Gordon 360, assign lottery numbers
  by class year, let students list roommates, sort the data automatically.
- What we built (team of four): a student application (roommates, up to 6 ranked halls,
  preference questions, agreements) and an admin table with CSV export, inside Gordon 360.
- How we tested it: two user studies (8 participants, including an RA), three demo
  feedback rounds. Recurring feedback: "agree to all" button, don't force 6 halls, people
  added without consent, duplicate emails, admin table hard to scan.
- **My role:** wrote the problem statement, led most of the front-end design, built the
  admin interface, ran the user studies, worked with the back end on the data model.

## 3. What we missed (about 250 words)

- The problem statement promised "an algorithm to sort collected housing data
  automatically". The MVP collected data; the assignment still happened by hand from the
  CSV.
- One demo reviewer said it directly: "the team could implement an algorithm that does the
  room assignments."
- Why we missed it (honest reflection): user research focused on the form's usability,
  not on the decision the form fed into; the hard question (what is fair?) had no owner.

## 4. Redefining the problem (about 250 words)

- Inputs: students (class year, gender category), confirmed roommate groups, halls with
  room types, each group's ranked list.
- Output: a room for every group, or a short, explained "unplaced" list for the admin.
- Goals: rules students can understand; honest ranking is always the best strategy;
  reproducible and auditable; admins handle only exceptions.

## 5. The rules, and the decisions behind them (about 400 words)

Table: each rule, the 2023 behavior, the 2026 choice, and the reason.

- R1 Groups form by mutual confirmation (fixes "added without my consent").
- R2 One gender category per group.
- R3 Group priority = **average** class year. Alternatives: highest (the 2023 design),
  lowest. Decision backed by data in section 7.
- R4 One ticket per group, so group size doesn't change the odds.
- R5 Verifiable draw: publish the SHA-256 hash of the seed before, the seed after.
- R6 Special accommodations reserved first.
- R7 Groups rank **(hall, room size)** options, 1 to 6 halls. Listing a smaller room
  type is how a group agrees to split.
- R8 Optional fallback: "place us anywhere if our options are full", plus "you may split
  us". Students who list only 1–2 halls see a risk warning with the simulated numbers.

## 6. The algorithm (about 350 words)

- Random Serial Dictatorship in plain words: groups take turns in lottery order; each takes
  the first option on its list that can still be filled completely.
- Why it's fair in a specific sense: when your turn comes, you get your best option still
  available. Lying about your ranking can only hurt you (strategy-proofness), so students
  don't need to game it. Tested by brute force on small cases, including split options.
- Worked example (diagram): four groups, two halls, step by step.

## 7. Testing the rules with simulation (about 600 words)

Setup: 1,000 synthetic campuses, 1,000 students each, 6 made-up halls, 5% more beds than
students. Every rule is run on the same students and tickets.

Findings (one chart each):

1. **Class-year priority doesn't make more people happy; it decides who is happy.**
   About 64% get their first-choice hall under every rule. Average priority: seniors
   about 85%, freshmen about 40%. Pure lottery: everyone about 64%.
   _Chart: first-choice rate by class year, average vs. pure lottery._
2. **The "senior carries friends" effect.** Underclass students gain by grouping with a
   senior: about +28 points under the highest rule, about +12 under the average rule.
   Average reduces the incentive but doesn't remove it.
   _Chart: gap by rule._
3. **Short lists are risky.** With only 1 hall listed, 28% are left unplaced; with 6
   halls, about 4%. This led to the warning plus the fallback option. If everyone ticks the
   fallback, the 1-hall risk drops to about 5%.
   _Chart: unplaced rate by halls listed, with and without fallback._
4. **My prediction was wrong.** I expected that ranking room types would reduce splits.
   It didn't: splits rose from about 16% to 19%. Ranking room types turns splitting into a
   choice: groups that value the hall split to get it; groups that value staying together
   rarely split.
   _Chart: split rate and first-choice rate as groups lean "together first" vs.
   "hall first"._
5. **An algorithm can't create rooms.** Even with every group using the fallback, groups
   of 4 stay at risk: about 25% of students are in groups of 4, but only about 14% of beds
   are in quads, while about 41 doubles sit empty at the end. That's a housing-stock
   question for the college, not a software question.

## 8. Reflection: what I'd tell my 2023 team (about 300 words)

- Start from the decision the software supports, not from the form.
- Write the rules down before the UI; many UI questions (must I fill 6 halls?) are really
  rule questions.
- Measure the rules before shipping them; a small simulation answers questions that user
  tests can't.
- Make randomness auditable when people's housing depends on it.
- Connection to teaching now: this is a good real-world problem for an algebra or
  statistics class (expected value, fairness, simulation).

## 9. Limitations and next steps (about 150 words)

- Synthetic data; real tastes and group sizes would change the numbers, not the method.
- Groups are fixed in the simulation; real students would regroup in response to rules.
- Next: a small interactive demo of the draw; testing with real (anonymized) historical
  data if a college wanted to.

## Credits and disclosure

- 2023–24 team: four students in CPS 491/492, with Gordon Residence Life and Housing.
  _Decide whether to name teammates (ask them first)._
- 2026 redesign and simulation code written with Claude (Anthropic's AI assistant); rules
  and decisions by the author. Code: link to the housing-lottery-sim repo.
