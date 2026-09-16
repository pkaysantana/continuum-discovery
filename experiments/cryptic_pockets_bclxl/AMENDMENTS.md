# Pre-execution review amendment, 2026-09-16

Reason: independent human review requested scientifically necessary changes before
any method execution and a durable Git anchor. No local detector results were
available or inspected. External Lacuna results were already known and inspected
as source evidence; this experiment is not blinded.

1. Reclassified BCL-XL as reproduction/pipeline validation. Lacuna's saved README
   and curated benchmark explicitly name 1LXL/2YXJ. This proves example/benchmark
   overlap, not fitting-data leakage.
2. Distinguished ensemble backend, detector and ranker. Current source is 1.2.0,
   commit 960523caa75c86f04111970da47c3c06ceeda8b4; replaced the unexecuted 1.1.0 plan.
   Source defaults and the incompletely specified showcase are separated from
   our explicit Analysis A/B assumptions. No assertion that NMA necessarily
   generated the README showcase result.
3. Replaced the former recall-and-Jaccard success gate with native-center distance
   <=4 A. Changed primary reference center from all-heavy-atom mean to reference
   CA mean, matching the benchmark's geometric definition. Preserved old outputs
   and heavy-atom centers as secondary. Source combined success is centroid OR
   Jaccard and source contacts use 4.5 A; our geometric-only 5.0 A primary endpoint
   deliberately differs. This is a methodological amendment, not a claim of
   exact numerical equivalence to the published headline.
4. Retained 5.0 A primary and preregistered 4.5 A sensitivity. Reconfirmed contact
   counts 24/22/19 at 5.0/4.5/4.0 A. No detector-based cutoff selection.
5. Added unambiguous matched-core selection using only sequence correspondence,
   observed backbone atoms and archive tag annotations. Retained 137 residues in
   each state, with every exclusion and mapping recorded. No target-distance rule.
6. Corrected a preprocessing implementation draft that serialized B factors as
   zero. P2Rank source lists B factor as a feature; final files preserve original
   B factors, coordinates and occupancy. The draft outputs and their manifests
   were moved, without replacement, to data/processed/superseded/bfactor_zero_v0/.
   They are not authorized method inputs. Final counts and reference geometry
   are unchanged. Both processing executions and the archive action are logged.
7. Separated Analysis A approximate reproduction from Analysis B fair comparison;
   froze second-system eligibility before candidate discovery. No second target
   was selected or searched.
8. Added bounded overlap audit. Direct exact-ID training inclusion was not found;
   target/homology and complete artifact fitting membership remain UNKNOWN.
   A recursive P2Rank dataset-tree query was truncated and logged FAILED. The
   narrower root-list query succeeded; no structure or detector predictions were
   downloaded from that dataset repository. All source snapshots were read only.
9. Added common centroid/overlap metric tests, matched-core serialization tests,
   hash verification and a preflight receipt. Original protocol/config/environment
   documents remain in manifests/pre_review/ and original reference_site.json
   remains unchanged. New replay provenance uses reference_site_v2.json.

Execution timestamps, code/input/output hashes, commands and errors are in
manifests/runs/. Source retrieval evidence is in manifests/source_review/.
The original setup_notes.json limitation on timestamps for early environment
probes remains disclosed. No historical project data or files were modified.

The preregistration anchor is a new commit and fixed annotated tag. A separate
receipt-only commit records that anchor's literal SHA in PREREGISTRATION.md;
this avoids the impossible requirement for a commit to contain its own hash.
No scientific definition changes in that receipt. Later changes need a new
dated amendment and commit; never amend or move this anchor after execution.
