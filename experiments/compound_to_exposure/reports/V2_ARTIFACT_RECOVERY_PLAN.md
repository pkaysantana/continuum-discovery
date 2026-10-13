# V2 protected-run artefact recovery plan

Scope: locate and verify the two missing outputs of protected run
`2026-09-18T215009395468_0000-4c110e67` without exposing protected outcome
values and without publishing restricted data. This document is a plan only.
Nothing in it has been executed, and executing step 3 or later requires an
explicit decision by the data owner.

## What is missing, and what is not

Per `V2_EXECUTION_001_POST_ACCESS_FORENSICS.md`, both files were written
successfully at execution time, inside the run directory
`manifests/runs/2026-09-18T215009395468_0000-4c110e67/`:

| File | State at execution | State in this repository |
| --- | --- | --- |
| `selection_manifest.json` | Persisted correctly | Not tracked on any branch |
| `primary_holdout_predictions.csv` | Persisted correctly | Not tracked on any branch |
| `.started.json` receipt | Created | Not tracked on any branch |
| Global `results/` metrics files | Not fully persisted; only `mean_mae` and `mae` recorded in the manifest | Absent |
| Tail, Sensitivity A/B, AD, HLM-HH contingency, Biogen outputs | Never written | Absent |

So this is a **publication gap, not a data-loss event**: the artefacts were
created on the execution workstation and never added to version control. The
forensics report already records their expected SHA-256 digests, which makes
verification possible without disclosing any contained value:

- `.started.json` -> `2e30562c0d04434eb7e29ee5668f810533a894231be03f96b72d3ca00b492289`
- `selection_manifest.json` -> `fea8a4c9c4d78b963669d8ee467a1276cabc9affd3efecb62716e9dcf4fe9efb`
- `primary_holdout_predictions.csv` -> `af427726da8f0c65741e32b0020d13141a3f4566f40e9c313adc88c88f7fa821`

## Why they are absent

`manifests/runs/` holds 32 tracked `*.json` receipt files and no run
subdirectories; no `.gitignore` in this repository excludes them
(`experiments/compound_to_exposure/.gitignore` lists only `.venv/`, `.cache/`,
`__pycache__/`, `*.pyc`, `reports/tmp/`). Receipt JSONs were committed in
`1371555`, `1b93269` and `4640ea7`, all dated before the 2026-09-18 protected
run, and no commit afterwards adds a run directory. The most likely explanation
is simply that the per-run output directory was never staged; it is also
consistent with deliberate exclusion of holdout-level predictions from a public
repository, which would be the correct instinct (see step 4).

## Where to look, in order of likelihood

1. The execution workstation, under the repository working tree at
   `experiments/compound_to_exposure/manifests/runs/2026-09-18T215009395468_0000-4c110e67/`.
   These are untracked working-tree files, so they are unaffected by any branch
   switch or later commit and are very likely still present.
2. `git stash list`, `git fsck --lost-found` and the reflog on that workstation,
   in case the directory was ever staged and then discarded.
3. Any workstation backup, snapshot or sync target (file-history, Time Machine,
   OneDrive/Dropbox-style sync) covering 2026-09-18 onwards.
4. `v2_execution_state.json`, which already preserves part of the HLM-HH state
   and may contain further recoverable fields.

Step 1 is a read-only directory listing plus a hash computation. It needs no
inference, no refit and no access to outcome values.

## Verification without exposing protected outcomes

For each candidate file, compute SHA-256 and compare to the digest above. A match
confirms the file is byte-identical to the one the forensics report describes,
which is sufficient to restore provenance for the reported metrics **without
reading, printing or transferring any row of the file**. Hashes are one-way: the
digest already sits in a committed report and discloses nothing further.

A match on `primary_holdout_predictions.csv` would also make the reported holdout
metrics independently recomputable *locally* (predictions versus the protected
observed values), which is what would upgrade them from REPORTED-ONLY to
VERIFIED-ARTEFACT in `../EVIDENCE_STATUS.md`. Recomputation from an existing
prediction file is arithmetic on stored outputs; it is not a model refit, not a
new holdout evaluation and not paid inference. It still touches protected
outcome values, so it requires the data owner's explicit decision and must stay
on the local workstation.

## What must not be done

- Do not commit `primary_holdout_predictions.csv` to this public repository. It
  is a per-compound prediction table over the protected 149-record holdout;
  publishing it would expose holdout-level outcome information and would
  compromise the holdout for any future prospective evaluation.
- Do not re-execute the protected run to regenerate the files. The forensics
  report already rules this out, and a rerun would not reproduce the original
  run's provenance.
- Do not refit any model, rerun V2 or V3A, or open the GSK development execution
  gate as part of recovery. That gate stays `NOT_READY`.
- Do not reconstruct the missing scaffold-bootstrap interval by re-running the
  bootstrap; the interval's provenance is recorded as unresolved and must stay
  so unless the original artefacts are recovered.

## Recommended outcome, whether or not recovery succeeds

If the files are recovered and hashes match: record the digests and the recovery
method in a short note beside this plan, commit `selection_manifest.json` only if
it is confirmed to contain no outcome values, keep the prediction CSV local, and
update the status line in `../EVIDENCE_STATUS.md`.

If they are not recovered: leave the V2 holdout metrics classified
**REPORTED-ONLY** permanently, and keep using the artefact-backed 20-seed results
in `FROZEN_RESULTS.md` as the primary quantitative record. Either way, the
defect note in `../EVIDENCE_STATUS.md` still applies: those metrics describe an
ECFP4 random forest, not a descriptor model.

To keep this gap from recurring, future runs should commit the run directory's
non-outcome files (receipt and selection manifest) in the same commit that
records the run, and record the digest of any output deliberately withheld.
