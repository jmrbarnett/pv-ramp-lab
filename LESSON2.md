# Lesson 2 – Curtailment and Setpoint Tracking (Fixtures)

**Goal:** Test a closed-loop power plant controller (PPC) using pytest **fixtures**, and practice three GitHub skills: **Issues linked to PRs**, **code review**, and **resolving a merge conflict**.

Take it one part at a time. Each part ends at a natural stopping point.

## Background

A grid operator can **curtail** a plant (for example, "limit to 60% of rated"). The PPC measures power at the **point of interconnection (POI)** and adjusts the inverter command so POI power tracks the limit.

| File | What it does |
|------|--------------|
| `pv_controls/plant.py` | Plant model: first-order lag, 2% collection losses, available-power limit (clouds) |
| `pv_controls/curtailment.py` | PI controller with integral clamp (anti-windup), optional ramp limit (reuses Lesson 1), simulation and CSV helpers |
| `tests/conftest.py` | Shared fixtures – **you add most of them** |
| `tests/test_curtailment.py` | Exercises 1–8 |
| `solutions/` | Reference answers (`pytest solutions/`) |

Key controller ideas:
- **Proportional (kp):** reacts to the current error.
- **Integral (ki):** removes the steady error that the 2% losses would leave.
- **Anti-windup:** caps the integral so a cloud can't make it grow huge and cause overshoot afterward.

---

## Part A – Issue, Branch, and Files

### Step 1 – Create an Issue

On GitHub: **Issues → New issue**.
- **Title:** `Add tests for curtailment controller`
- **Body:** paste this checklist:
  ```
  - [ ] Exercises 1-4
  - [ ] Exercises 5-8
  - [ ] Coverage checked
  ```

Note the issue number. Issues and PRs share numbering, so it's probably **#2**. Use your actual number wherever this guide says `#2`.

### Step 2 – Update `main` and Create a Branch

```bash
git checkout main
git pull
git checkout -b 2-curtailment-tests
```

Starting a branch name with the issue number is a common convention.

### Step 3 – Add the Lesson Files

Copy everything inside the zip's `lesson2-files` folder into your `pv-ramp-lab` folder. The folders merge; no existing files are replaced.

```bash
pytest -v
```

**Expected:** all your Lesson 1 tests plus `test_open_loop_output_shows_losses` pass.

```bash
git add .
git commit -m "Add curtailment controller and plant model (refs #2)"
```

Writing `refs #2` in a commit message links the commit to the issue on GitHub.

---

## Part B – Fixtures (the pytest Focus)

### Step 4 – Complete Exercises 1–8

A **fixture** is a function that prepares something a test needs. A test requests a fixture by naming it as an argument. Fixtures in `conftest.py` are shared automatically, with no import needed. Each test gets a **fresh** copy, so tests can't affect each other.

| # | Skill |
|---|-------|
| 1 | Warm-up: parametrize and `pytest.raises` (no fixtures) |
| 2 | Basic fixtures (`plant`, `controller`) |
| 3 | **Factory fixtures** (`make_plant`, `make_controller`) |
| 4 | **Fixtures that use other fixtures** (`step_down_result`) |
| 5 | **Parametrized fixtures** (`rated_kw` → 3 runs) |
| 6 | Anti-windup test: proving a safeguard matters |
| 7 | Ramp limit (Lesson 1 reused) |
| 8 | Built-in fixture `tmp_path` |

Useful commands:

```bash
pytest -v                      # run the tests
pytest --fixtures tests/       # list available fixtures
pytest --setup-show -k step    # watch fixtures being created
```

Commit as you go, for example `git commit -m "Add fixture exercises 1-4 (refs #2)"`.

### Step 5 – Push and Open a PR That Closes the Issue

```bash
git push -u origin 2-curtailment-tests
```

Open the PR. In the **description**, write:

```
Closes #2
```

Open the issue and confirm it now shows the linked PR. When the PR merges, GitHub closes the issue automatically.

---

## Part C – Code Review

### Step 6 – Review Your Own PR

Real teams review every PR. You can't **approve** your own PR, but you can practice everything else.

1. On the PR, open the **Files changed** tab.
2. **Comment on a line:** hover over a line, click the blue **+**, and ask a reviewer-style question (for example, on `integral_limit_kw`: *"Why 5% of rated?"*). Click **Start a review**.
3. **Suggest a change:** there's a typo in the `save_csv` docstring in `curtailment.py` ("ploting"). Comment on that line, click the **suggestion** icon (±), correct the word, and add it to your review.
4. Click **Finish your review** → **Comment** → **Submit review**.
5. Back on the **Conversation** tab, click **Commit suggestion** on the typo fix.
6. Reply to your own question with an answer, then **Resolve conversation**.

Committing the suggestion created a commit **on GitHub**, so bring it down to your computer:

```bash
git pull
```

If you skip this step, your next push will be rejected because GitHub has a commit you don't.

### Step 7 – Merge and Confirm the Issue Closed

Merge the PR, then confirm issue #2 shows **Closed**. Then sync and clean up:

```bash
git checkout main
git pull
git branch -d 2-curtailment-tests
```

---

## Part D – Merge Conflict

A conflict happens when two branches change the **same line** differently. You'll create one on purpose.

### Step 8 – Make Two Competing Branches

```bash
git checkout main
git pull
git checkout -b tune-kp-low
```

In `pv_controls/curtailment.py`, change `kp: float = 0.3` to `kp: float = 0.25`. Then:

```bash
git commit -am "Lower default kp to 0.25"
git push -u origin tune-kp-low
git checkout main
git checkout -b tune-kp-high
```

Change the same line to `kp: float = 0.35`. Then:

```bash
git commit -am "Raise default kp to 0.35"
```

### Step 9 – Merge the First Branch

On GitHub, open a PR for `tune-kp-low`, wait for green checks, and merge it.

### Step 10 – Trigger and Resolve the Conflict

```bash
git fetch
git merge origin/main
```

Git reports `CONFLICT (content): Merge conflict in pv_controls/curtailment.py`. The file now contains:

```
<<<<<<< HEAD
    def __init__(self, rated_kw: float, kp: float = 0.35, ki: float = 0.2,
=======
    def __init__(self, rated_kw: float, kp: float = 0.25, ki: float = 0.2,
>>>>>>> origin/main
```

- **HEAD / Current:** your branch's version (0.35).
- **Incoming:** what's on `main` (0.25).

To resolve it:
1. In VS Code, use **Accept Current**, **Accept Incoming**, or **Resolve in Merge Editor**. You can also edit the text by hand. Pick one value and make sure every `<<<<<<<`, `=======`, and `>>>>>>>` line is gone.
2. Run `pytest -v`. Both values pass the test suite, so the choice is an engineering decision, not a testing one.
3. Finish the merge:
   ```bash
   git add pv_controls/curtailment.py
   git commit -m "Merge main; resolve kp conflict"
   git push -u origin tune-kp-high
   ```
4. Open the PR, then merge it. Delete both `tune-kp-*` branches.

If anything goes wrong mid-merge, `git merge --abort` returns you to where you started.

---

## Step 11 – Coverage

```bash
pytest --cov=pv_controls --cov-report=term-missing
```

The input-validation lines in `plant.py` and `curtailment.py` will show as missing. Add `pytest.raises` tests to reach 100%, then tick the last box on your issue.

## Skills Checklist

- [ ] GitHub Issue with task list; `refs #N` and `Closes #N`
- [ ] Basic, factory, dependent, and parametrized fixtures
- [ ] `conftest.py` and the built-in `tmp_path` fixture
- [ ] `pytest --fixtures` and `--setup-show`
- [ ] Line comments, suggested changes, and review submission
- [ ] Pulling commits made on GitHub
- [ ] Creating and resolving a merge conflict
- [ ] `git merge --abort`

## Stretch Goals

- Add `scope="module"` to `step_down_result`, then use `--setup-show` to see how often it runs. When is a shared fixture risky?
- Write a **yield fixture** that saves a CSV of every simulation to `tmp_path` and prints the path after the test (teardown).
- Plot a saved CSV with matplotlib and compare the default controller against the one with anti-windup disabled.
