# PV Controls Testing Lab – Lesson 1: Ramp-Rate Limiting

**Goal:** Write pytest tests for a PV plant ramp-rate limiter, put the project on GitHub, and have GitHub Actions run the tests automatically on every push and pull request.

**Background:** Grid operators limit how fast plant output may change (for example, 10% of rated capacity per minute). `pv_controls/ramp.py` moves the active-power setpoint toward a target no faster than that limit.

## Project Layout

```
pv-ramp-lab/
├── pv_controls/ramp.py          # code under test
├── tests/test_ramp.py           # YOUR exercises go here
├── solutions/                   # reference answers (try first!)
├── .github/workflows/tests.yml  # GitHub Actions CI pipeline
├── pyproject.toml               # pytest settings
└── requirements.txt
```

---

## Step 1 – Set Up Locally

Open the folder in VS Code, then in the terminal:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```

**Expected:** `1 passed`. Read `pv_controls/ramp.py` before moving on.

## Step 2 – Put It Under Git and on GitHub

1. On GitHub, create a new **empty** repository named `pv-ramp-lab` (no README, no .gitignore).
2. In the terminal:

```bash
git init
git add .
git commit -m "Initial ramp-rate lab"
git branch -M main
git remote add origin https://github.com/<your-username>/pv-ramp-lab.git
git push -u origin main
```

3. Open the **Actions** tab on GitHub. The `tests` workflow should run and show a green check.

## Step 3 – Write Your Tests on a Branch

```bash
git checkout -b add-ramp-tests
```

Open `tests/test_ramp.py` and complete Exercises 1–6. Run `pytest -v` after each one.

| # | Skill practiced |
|---|-----------------|
| 1 | Basic assertion (ramp down) |
| 2 | Edge case: no overshoot |
| 3 | Edge case: already at target |
| 4 | `pytest.raises` for invalid inputs |
| 5 | `@pytest.mark.parametrize` |
| 6 | Simulation-based test using `simulate_ramp()` |

Commit as you go – small commits are good practice:

```bash
git add tests/test_ramp.py
git commit -m "Add ramp-down and overshoot tests"
```

## Step 4 – Push and Open a Pull Request

```bash
git push -u origin add-ramp-tests
```

On GitHub, click **Compare & pull request**. Watch the checks run on the PR page. Don't merge yet.

## Step 5 – Watch CI Catch a Bug

Still on your branch, break the code on purpose. In `ramp.py`, change the last line:

```python
return current_kw - max_step   →   return current_kw + max_step
```

Commit and push. Your ramp-down test should fail locally **and** on the PR (red X). Click the failed check to read the log.

Then undo it:

```bash
git revert HEAD
git push
```

The PR should turn green again.

## Step 6 – Protect `main`

In the repository **Settings**, find **Branches** (branch protection rules) or **Rules → Rulesets**. Add a rule for `main` that requires the `test` status check to pass before merging. GitHub's labels change occasionally, so look for "require status checks."

Now merge your PR.

## Step 7 – Check Coverage

```bash
pytest --cov=pv_controls --cov-report=term-missing
```

The `Missing` column lists lines your tests never ran. Aim for 100% on `ramp.py`.

---

## Check Your Work

Compare with `solutions/test_ramp_solution.py` (run it with `pytest solutions/`).

## Skills Checklist

- [ ] Virtual environment and pytest setup
- [ ] Git init, commit, push, branch
- [ ] Assertions, `pytest.raises`, `parametrize`
- [ ] GitHub Actions running on push and PR
- [ ] Reading a failed CI log
- [ ] `git revert`
- [ ] Branch protection
- [ ] Coverage report

## Stretch Goals

- Add a Python version **matrix** (3.11, 3.12, 3.13) to `tests.yml`.
- Add a `rated_kw` limit so setpoints are clamped between 0 and plant capacity, plus tests for it.
- Try `git bisect` to find the commit where you introduced the bug in Step 5.
