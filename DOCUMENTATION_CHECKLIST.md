# Documentation Maintenance Checklist

> **Purpose:** Ensure documentation stays current to avoid having to rethink context in every chat session. This checklist should be reviewed **before every commit**.

## Why This Matters

**The Problem:** Outdated documentation forces developers (and AI assistants) to re-discover context, architecture decisions, and current status in every conversation. This wastes time and introduces errors.

**The Solution:** Make documentation updates a **standard part of every commit**, not an afterthought.

## Pre-Commit Documentation Checklist

### 🔍 Before Every Commit

Run through this checklist before staging your commit:

#### 1. **Core Documentation Files**

- [ ] **README.md** - Does it need updates for:
  - [ ] Project status percentage (currently 80%)
  - [ ] Validation pass rate (currently 83.8%)
  - [ ] New features or capabilities
  - [ ] Installation instructions
  - [ ] Status badges (CI, validation, progress)
  - [ ] Quick start examples

- [ ] **NEXT_STEPS.md** - Should be updated for:
  - [ ] Completed tasks (move to "Done" section)
  - [ ] New priorities discovered during implementation
  - [ ] Updated timeline or phase progress
  - [ ] New blockers or dependencies identified
  - [ ] Changes to the roadmap

- [ ] **CONTRIBUTING.md** - Update if you changed:
  - [ ] Development setup process
  - [ ] Testing requirements
  - [ ] Code style guidelines
  - [ ] New tools or dependencies

#### 2. **API & Usage Documentation**

- [ ] **docs/USAGE.md** - Update when:
  - [ ] Adding new public APIs or classes
  - [ ] Changing function signatures
  - [ ] Adding new usage patterns
  - [ ] Deprecating old APIs

- [ ] **docs/INTEGRATION.md** - Update when:
  - [ ] Changing integration patterns
  - [ ] Adding new web app features
  - [ ] Modifying API endpoints
  - [ ] Updating dashboard capabilities

- [ ] **examples/** directory - Ensure examples work:
  - [ ] Run all example scripts to verify they execute
  - [ ] Update examples if API changed
  - [ ] Add new examples for new features

#### 3. **Validation & Testing Documentation**

- [ ] **VALIDATION_STRATEGY.md** - Update when:
  - [ ] Adding new validation test cases
  - [ ] Changing acceptance criteria
  - [ ] Discovering new validation methodology
  - [ ] Updating pass rate targets

- [ ] **VALIDATION_SUMMARY.md** - Update when:
  - [ ] Validation pass rates change (currently 83.8%)
  - [ ] New test cases added
  - [ ] Bugs fixed that affect validation
  - [ ] New validation data generated

- [ ] **VALIDATION.md** - Keep current with:
  - [ ] Latest validation run results
  - [ ] Status of reference data generation
  - [ ] Known validation issues

- [ ] **Phase/Weekly Completion Reports** - Create when:
  - [ ] Completing a major phase
  - [ ] Finishing a week's planned work
  - [ ] Achieving a significant milestone
  - [ ] Format: `WEEK_X_Y_<TOPIC>_COMPLETE.md` or `PHASE<N>_VALIDATION_REPORT.md`

#### 4. **Technical Analysis Documentation**

- [ ] **Investigation Reports** - Create new reports when:
  - [ ] Debugging complex issues (e.g., `ABSORPTION_BUG_ANALYSIS.md`)
  - [ ] Investigating discrepancies (e.g., `RELIABILITY_INVESTIGATION.md`)
  - [ ] Comparing implementations (e.g., `ANALYSIS_GN55_IN25_COMPARISON.md`)
  - [ ] Include: problem statement, methodology, findings, resolution

- [ ] **Algorithm Documentation** - Update when:
  - [ ] Implementing new algorithms
  - [ ] Discovering bugs in algorithm implementation
  - [ ] Verifying against original VOACAP/DVOACAP
  - [ ] See: `ALGORITHMIC_COMPONENTS.md`, `FORTRAN_ANALYSIS_AND_RECOMMENDATIONS.md`

#### 5. **Dashboard Documentation**

- [ ] **Dashboard/README.md** - Update when:
  - [ ] Adding new dashboard features
  - [ ] Changing API endpoints
  - [ ] Modifying configuration options
  - [ ] Updating deployment instructions

- [ ] **Dashboard Design Docs** - Update when:
  - [ ] Making UI/UX changes
  - [ ] Adding new visualizations
  - [ ] Changing data models
  - [ ] See: `DASHBOARD_DESIGN_RECOMMENDATIONS.md`, `MOCKUPS_README.md`

#### 6. **Code Comments & Docstrings**

- [ ] **Inline Comments** - Add when:
  - [ ] Implementing complex algorithms
  - [ ] Working around edge cases
  - [ ] Matching original FORTRAN/Pascal logic
  - [ ] Making non-obvious design decisions

- [ ] **Function Docstrings** - Every function should have:
  - [ ] Purpose/description
  - [ ] Parameter types and meanings
  - [ ] Return value description
  - [ ] Example usage (for public APIs)
  - [ ] References to original VOACAP code if porting

- [ ] **Class Docstrings** - Every class should have:
  - [ ] Purpose and responsibility
  - [ ] Key attributes
  - [ ] Usage examples
  - [ ] Related classes/modules

#### 7. **Type Hints**

- [ ] Add type hints to new functions
- [ ] Add type hints to new class methods
- [ ] Update type hints if signatures changed
- [ ] Ensure mypy passes (planned for future)

## Quick Documentation Decision Tree

```
Did you modify code?
├─ YES → What kind?
│  ├─ Bug fix
│  │  └─ Update: NEXT_STEPS.md (mark task done), investigation report if complex
│  │
│  ├─ New feature
│  │  └─ Update: README.md (features), docs/USAGE.md (API), NEXT_STEPS.md (mark done)
│  │
│  ├─ Algorithm change
│  │  └─ Update: Algorithm docs, validation reports, inline comments
│  │
│  ├─ Validation/testing
│  │  └─ Update: VALIDATION_SUMMARY.md, validation reports, README.md (pass rate)
│  │
│  └─ Dashboard change
│     └─ Update: Dashboard/README.md, design docs, mockups
│
└─ NO → Documentation-only commit (great!)
   └─ Ensure documentation is accurate and complete
```

## Common Documentation Patterns

### Pattern 1: Completing a Task from NEXT_STEPS.md

**Before committing:**
1. Mark task as complete in NEXT_STEPS.md
2. Update README.md progress percentage if significant
3. Create completion report if it's a major phase/week
4. Update validation metrics if applicable

### Pattern 2: Fixing a Bug

**Before committing:**
1. Document the bug in an investigation report (if complex)
2. Update NEXT_STEPS.md to mark debugging task complete
3. Update validation reports if bug affected test results
4. Add inline comments explaining the fix
5. Update README.md validation % if it improved

### Pattern 3: Adding a New Feature

**Before committing:**
1. Update README.md to list the new feature
2. Add usage examples to docs/USAGE.md
3. Create example script in examples/ directory
4. Add tests and update test documentation
5. Update NEXT_STEPS.md roadmap if priorities changed
6. Update Dashboard/README.md if dashboard feature

### Pattern 4: Refactoring Code

**Before committing:**
1. Update architecture docs if structure changed
2. Update examples if API changed
3. Update CONTRIBUTING.md if dev process changed
4. Ensure inline comments are still accurate
5. Update integration docs if needed

## Documentation Quality Standards

### Good Documentation is:

- **Current** - Reflects the actual state of the code
- **Complete** - Covers all public APIs and major features
- **Clear** - Easy to understand for target audience
- **Correct** - Technically accurate and tested
- **Concise** - No unnecessary verbosity
- **Consistent** - Follows project conventions

### Documentation Red Flags:

- ❌ "TODO: Document this later"
- ❌ Commented-out old instructions
- ❌ Examples that don't run
- ❌ Status percentages that haven't been updated
- ❌ Validation reports older than the code
- ❌ API docs that don't match function signatures

## Tools & Automation

### Pre-Commit Hook

The repository includes a pre-commit hook (`.git/hooks/pre-commit`) that:
- Detects code changes without documentation updates
- Prompts you to confirm documentation is current
- Warns about documentation files older than 30 days
- Can be bypassed with "skip" for trivial changes

**Installation:** Already installed if you cloned the repo. Hook is at `.git/hooks/pre-commit`.

### Manual Check

Before any commit, run:
```bash
# See what you're about to commit
git diff --cached --name-only

# Review this checklist
cat DOCUMENTATION_CHECKLIST.md

# Stage documentation updates
git add README.md NEXT_STEPS.md docs/USAGE.md
```

### Recommended Workflow

```bash
# 1. Make code changes
vim src/dvoacap/my_module.py

# 2. Update documentation IMMEDIATELY
vim README.md NEXT_STEPS.md docs/USAGE.md

# 3. Run tests
pytest tests/

# 4. Review changes together
git diff src/ docs/ *.md

# 5. Stage both code AND docs
git add src/dvoacap/my_module.py README.md NEXT_STEPS.md

# 6. Commit (pre-commit hook will verify)
git commit -m "Add feature X with documentation"
```

## Documentation Maintenance Schedule

### Before Every Commit (Required)
- [ ] Run through quick checklist above
- [ ] Stage relevant documentation files
- [ ] Ensure pre-commit hook passes

### Weekly (Recommended)
- [ ] Review NEXT_STEPS.md for completed items
- [ ] Update progress percentages in README.md
- [ ] Check validation pass rates are current
- [ ] Create weekly completion report if significant progress made

### Monthly (Recommended)
- [ ] Review all root-level .md files for accuracy
- [ ] Check that examples/ scripts all run
- [ ] Update Dashboard documentation
- [ ] Review and clean up old investigation reports

### Before Each Release (Required)
- [ ] Update all version numbers
- [ ] Regenerate all validation reports
- [ ] Update README.md status badges
- [ ] Review and update CONTRIBUTING.md
- [ ] Ensure all docs reflect current API

## FAQs

### Q: Do I need to update documentation for every tiny change?

**A:** Use judgment. For truly trivial changes (fixing typos, formatting), you can skip. But for:
- Bug fixes that affect behavior
- New functions or classes
- API changes
- Algorithm modifications
- Validation results changes

**Always update documentation.**

### Q: Which documentation files are most critical?

**A:** Priority order:
1. **README.md** - First thing users see
2. **NEXT_STEPS.md** - Keeps team aligned on priorities
3. **docs/USAGE.md** - Critical for API users
4. **Validation reports** - Prove the code works
5. **Phase completion docs** - Track progress
6. **Investigation reports** - Preserve debugging knowledge

### Q: What if I'm not sure what documentation needs updating?

**A:** Start with this checklist:
1. Did I change public API? → Update docs/USAGE.md
2. Did I complete a task? → Update NEXT_STEPS.md
3. Did I add a feature? → Update README.md
4. Did I fix a validation bug? → Update validation reports
5. Did I change the dashboard? → Update Dashboard/README.md

When in doubt, **add more documentation rather than less**.

### Q: Can I skip the pre-commit hook?

**A:** Yes, by answering "skip" when prompted. But use this sparingly:
- Only for truly trivial commits (typo fixes, comment changes)
- Never for code changes that affect behavior
- Never when adding new features or APIs

### Q: How do I know if documentation is outdated?

**A:** Look for:
- Dates older than the code they describe
- Examples that don't run
- API docs that don't match function signatures
- Status percentages that seem wrong
- References to "planned" features that are already implemented

## Summary

**Key Principle:** Documentation is not a separate task—it's part of writing code.

**Goal:** Any developer (or AI assistant) should be able to:
1. Read README.md and understand the project
2. Read NEXT_STEPS.md and know what to work on
3. Read docs/USAGE.md and use the API
4. Read validation reports and trust the code
5. Read investigation reports and understand past debugging

**Result:** No more "re-thinking at every chat" because the documentation already captures the context.

---

**Last Updated:** 2025-11-15
**Maintained By:** All contributors
**Status:** Living document - update as processes evolve
