# V3A Gate 11 Scientific Runner Acceptance-Test Specification

## Metadata

**SOURCE:** Independent Copilot read-only design pass

**DATE:** 2026-09-24

**ROLE:** Pre-execution software acceptance specification

**EXECUTION STATUS:** NO REAL CHEMBL3301370 EXECUTION REQUIRED

## PURPOSE

Defines synthetic acceptance criteria for the future v3A scientific execution runner.

## RELATION TO EXISTING TESTS

This specification extends the audited 119-test preflight suite.

It does not replace that suite and should not unnecessarily duplicate primitive-level tests that are already covered.

## CENTRAL ARCHITECTURAL INVARIANT

```text
preflight verification
→ fold model fitting
→ OOF predictions and uncertainty scores
→ IMMUTABLE PREDICTION/UNCERTAINTY FREEZE
→ outcome-dependent evaluation
→ inference/sensitivities
→ result serialization
```

No outer-test-outcome-dependent operation may influence anything upstream of the immutable prediction/uncertainty freeze.

### Required prediction-freeze record fields

- `activity_id`
- `outer_fold`
- `rf_prediction`
- `qrf_q10`
- `qrf_q90`
- `qrf_width`
- `tanimoto_unfamiliarity`
- `physchem_knn5_distance`
- `neff_inverse`
- `local_label_sd`
- `tree_sd`
- uncertainty method/rank/tie metadata

A passing preflight-only suite is insufficient to close Gate 11 unless the future runner exposes and enforces the prediction/uncertainty freeze boundary.

No test in this specification requires real CHEMBL3301370 outcomes or scientific v3A execution.

This task preserves the specification only. It does not implement any test or runner behavior.

## Authoritative source transcription

```text
SOURCE C — COPILOT GATE 11 ACCEPTANCE-TEST SPECIFICATION

Gate 11 acceptance-test specification

All fixtures below are synthetic and outcome-controlled. None requires real  CHEMBL3301370  execution. Tests marked runner-required cannot be executed until the future scientific runner exists; they remain valid pre-execution acceptance criteria.

A. Frozen artifact integrity

┌───┬────────────────────────┬───────────┬──────────┬──────┬─────────┬─────────┬────────┐
│ T │ TEST NAME              │ INVARIANT │ MINIMAL  │ ACTI │ EXPECTE │ WHAT    │ PRE-EX │
│ E │                        │           │ SYNTHETI │ ON   │ D       │ BUG IT  │ ECUTIO │
│ S │                        │           │ C        │      │ ASSERTI │ CATCHES │ N      │
│ T │                        │           │ FIXTURE  │      │ ON      │         │        │
│ I │                        │           │          │      │         │         │        │
│ D │                        │           │          │      │         │         │        │
├───┼────────────────────────┼───────────┼──────────┼──────┼─────────┼─────────┼────────┤
│ 1 │ test_altered_sap_rejec │ SAP hash  │ Copy     │ Invo │ Executi │ Running │ Yes    │
│   │ ted                    │ must      │ manifest │ ke   │ on      │ against │        │
│   │                        │ equal     │ and      │ runn │ fails   │ altered │        │
│   │                        │ manifest  │ alter    │ er   │ with    │ protoco │        │
│   │                        │           │ one SAP  │ pref │ SAP     │ l       │        │
│   │                        │           │ byte     │ ligh │ hash    │         │        │
│   │                        │           │          │ t    │ mismatc │         │        │
│   │                        │           │          │      │ h       │         │        │
├───┼────────────────────────┼───────────┼──────────┼──────┼─────────┼─────────┼────────┤
│ 2 │ test_altered_cohort_re │ Cohort    │ Copy     │ Invo │ Executi │ Changed │ Yes    │
│   │ jected                 │ artifact  │ cohort   │ ke   │ on      │ N=744   │        │
│   │                        │ hash must │ CSV and  │ pref │ fails   │ cohort  │        │
│   │                        │ match     │ alter    │ ligh │ before  │         │        │
│   │                        │           │ one row  │ t    │ fold    │         │        │
│   │                        │           │          │      │ fitting │         │        │
├───┼────────────────────────┼───────────┼──────────┼──────┼─────────┼─────────┼────────┤
│ 3 │ test_altered_split_rej │ Split     │ Alter    │ Invo │ Executi │ Changed │ Yes    │
│   │ ected                  │ artifact  │ one fold │ ke   │ on      │ outer-f │        │
│   │                        │ hash must │ assignme │ pref │ fails   │ old     │        │
│   │                        │ match     │ nt       │ ligh │ before  │ assignm │        │
│   │                        │           │          │ t    │ fitting │ ent     │        │
├───┼────────────────────────┼───────────┼──────────┼──────┼─────────┼─────────┼────────┤
│ 4 │ test_altered_feature_m │ Feature   │ Flip one │ Invo │ Executi │ Changed │ Yes    │
│   │ atrix_rejected         │ hash must │ feature  │ ke   │ on      │ fingerp │        │
│   │                        │ match     │ bit      │ pref │ fails   │ rints   │        │
│   │                        │           │          │ ligh │ before  │         │        │
│   │                        │           │          │ t    │ fitting │         │        │
├───┼────────────────────────┼───────────┼──────────┼──────┼─────────┼─────────┼────────┤
│ 5 │ test_non_ecfp4_metadat │ Represent │ Use      │ Invo │ Executi │ Alterna │ Yes    │
│   │ a_rejected             │ ation     │ descript │ ke   │ on      │ te      │        │
│   │                        │ metadata  │ or,      │ pref │ fails   │ represe │        │
│   │                        │ is frozen │ wrong    │ ligh │ with    │ ntation │        │
│   │                        │           │ radius,  │ t    │ represe │ silentl │        │
│   │                        │           │ wrong    │      │ ntation │ y used  │        │
│   │                        │           │ bit      │      │ mismatc │         │        │
│   │                        │           │ width,   │      │ h       │         │        │
│   │                        │           │ binary=f │      │         │         │        │
│   │                        │           │ alse, or │      │         │         │        │
│   │                        │           │ chiralit │      │         │         │        │
│   │                        │           │ y=true   │      │         │         │        │
├───┼────────────────────────┼───────────┼──────────┼──────┼─────────┼─────────┼────────┤
│ 6 │ test_nonfrozen_rf_conf │ RF        │ Alter    │ Star │ Executi │ Tuning  │ Yes    │
│   │ ig_rejected            │ parameter │ each RF  │ t    │ on      │ or      │        │
│   │                        │ s equal   │ paramete │ runn │ fails   │ configu │        │
│   │                        │ C.FROZEN_ │ r        │ er   │ before  │ ration  │        │
│   │                        │ RF_PARAMS │ independ │      │ fitting │ drift   │        │
│   │                        │           │ ently    │      │         │         │        │
├───┼────────────────────────┼───────────┼──────────┼──────┼─────────┼─────────┼────────┤
│ 7 │ test_audit_state_requi │ Execution │ Manifest │ Invo │ Every   │ Executi │ Yes    │
│   │ red                    │ requires  │ with     │ ke   │ invalid │ on      │        │
│   │                        │ explicit  │ each     │ guar │ manifes │ without │        │
│   │                        │ flag,     │ required │ d    │ t fails │ audited │        │
│   │                        │ frozen    │ field    │      │ closed  │ authori │        │
│   │                        │ state,    │ removed/ │      │         │ zation  │        │
│   │                        │ hashes,   │ false    │      │         │         │        │
│   │                        │ and audit │          │      │         │         │        │
└───┴────────────────────────┴───────────┴──────────┴──────┴─────────┴─────────┴────────┘

B. Outer-fold integrity

┌───┬──────────────────────────┬──────┬────────────┬──────┬────────┬───────────┬────────┐
│ T │ TEST NAME                │ INVA │ MINIMAL    │ ACTI │ EXPECT │ WHAT BUG  │ PRE-EX │
│ E │                          │ RIAN │ SYNTHETIC  │ ON   │ ED     │ IT        │ ECUTIO │
│ S │                          │ T    │ FIXTURE    │      │ ASSERT │ CATCHES   │ N      │
│ T │                          │      │            │      │ ION    │           │        │
│ I │                          │      │            │      │        │           │        │
│ D │                          │      │            │      │        │           │        │
├───┼──────────────────────────┼──────┼────────────┼──────┼────────┼───────────┼────────┤
│ 8 │ test_each_compound_has_o │ IDs  │ Six-row    │ Vali │ Invali │ Duplicate │ Yes    │
│   │ ne_outer_test_fold       │ are  │ cohort     │ date │ d      │ /missing  │        │
│   │                          │ comp │ with       │ fold │ varian │ test      │        │
│   │                          │ lete │ duplicate, │ tabl │ ts     │ assignmen │        │
│   │                          │ and  │ missing,   │ e    │ reject │ t         │        │
│   │                          │ uniq │ and        │      │ ;      │           │        │
│   │                          │ ue   │ extra-ID   │      │ valid  │           │        │
│   │                          │      │ variants   │      │ table  │           │        │
│   │                          │      │            │      │ assign │           │        │
│   │                          │      │            │      │ s each │           │        │
│   │                          │      │            │      │ ID     │           │        │
│   │                          │      │            │      │ once   │           │        │
├───┼──────────────────────────┼──────┼────────────┼──────┼────────┼───────────┼────────┤
│ 9 │ test_train_test_ids_disj │ Trai │ Two-fold   │ Buil │ Assert │ Same      │ Yes    │
│   │ oint                     │ n/te │ table with │ d    │ ion    │ compound  │        │
│   │                          │ st   │ one ID in  │ fold │ fails  │ in train  │        │
│   │                          │ IDs  │ both       │ part │ on     │ and test  │        │
│   │                          │ disj │ partitions │ itio │ inters │           │        │
│   │                          │ oint │            │ ns   │ ection │           │        │
│   │                          │ per  │            │      │        │           │        │
│   │                          │ fold │            │      │        │           │        │
├───┼──────────────────────────┼──────┼────────────┼──────┼────────┼───────────┼────────┤
│ 1 │ test_train_test_scaffold │ Scaf │ Same       │ Vali │ Assert │ Scaffold  │ Yes    │
│ 0 │ s_disjoint               │ fold │ scaffold   │ date │ ion    │ leakage   │        │
│   │                          │ sets │ in train   │ part │ fails  │           │        │
│   │                          │ disj │ and test   │ itio │ with   │           │        │
│   │                          │ oint │            │ ns   │ leakag │           │        │
│   │                          │ per  │            │      │ e      │           │        │
│   │                          │ fold │            │      │ error  │           │        │
├───┼──────────────────────────┼──────┼────────────┼──────┼────────┼───────────┼────────┤
│ 1 │ test_oof_prediction_has_ │ Test │ Spy RF     │ Fit/ │ Query  │ In-sample │ Yes    │
│ 1 │ no_training_row          │ pred │ records    │ pred │ ID     │ predictio │        │
│   │                          │ icti │ training   │ ict  │ absent │ n         │        │
│   │                          │ on   │ IDs and    │ each │ from   │ masquerad │        │
│   │                          │ mode │ query IDs  │ fold │ that   │ ing as    │        │
│   │                          │ l    │            │      │ fold’s │ OOF       │        │
│   │                          │ excl │            │      │ traini │           │        │
│   │                          │ udes │            │      │ ng IDs │           │        │
│   │                          │ quer │            │      │        │           │        │
│   │                          │ y ID │            │      │        │           │        │
├───┼──────────────────────────┼──────┼────────────┼──────┼────────┼───────────┼────────┤
│ 1 │ test_exactly_one_rf_per_ │ One  │ Three-fold │ Run  │ Factor │ Extra/reu │ Yes    │
│ 2 │ outer_fold               │ froz │ synthetic  │ pred │ y      │ sed/missi │        │
│   │                          │ en   │ split and  │ icti │ called │ ng fold   │        │
│   │                          │ RF   │ RF factory │ on   │ exactl │ models    │        │
│   │                          │ per  │ spy        │ stag │ y once │           │        │
│   │                          │ fold │            │ e    │ per    │           │        │
│   │                          │      │            │      │ fold   │           │        │
├───┼──────────────────────────┼──────┼────────────┼──────┼────────┼───────────┼────────┤
│ 1 │ test_no_fold_specific_tu │ No   │ Spy        │ Run  │ No     │ Fold-spec │ Yes    │
│ 3 │ ning                     │ tuni │ estimator/ │ fold │ tuning │ ific      │        │
│   │                          │ ng   │ grid-searc │ stag │ /searc │ hyperpara │        │
│   │                          │ uses │ h object   │ e    │ h      │ meter     │        │
│   │                          │ test │ and        │      │ call;  │ optimizat │        │
│   │                          │ resu │ altered    │      │ model  │ ion       │        │
│   │                          │ lts  │ test       │      │ config │           │        │
│   │                          │      │ labels     │      │ unchan │           │        │
│   │                          │      │            │      │ ged    │           │        │
└───┴──────────────────────────┴──────┴────────────┴──────┴────────┴───────────┴────────┘

C. Test-outcome blindness before freeze

For tests 14–29, use identical structures,  X_train ,  y_train , fold assignments, and model state. Run the pre-freeze stage twice with  y_test_a  and radically different  y_test_b . Every output named in the assertion must be identical.

┌───┬────────────────────────┬──────────┬───────────┬────┬────────────┬─────────┬───────┐
│ T │ TEST NAME              │ INVARIAN │ MINIMAL   │ AC │ EXPECTED   │ WHAT    │ PRE-E │
│ E │                        │ T        │ SYNTHETIC │ TI │ ASSERTION  │ BUG IT  │ XECUT │
│ S │                        │          │ FIXTURE   │ ON │            │ CATCHES │ ION   │
│ T │                        │          │           │    │            │         │       │
│ I │                        │          │           │    │            │         │       │
│ D │                        │          │           │    │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 1 │ test_feature_construct │ Fingerpr │ Two       │ Bu │ Matrices   │ Outcome │ Yes   │
│ 4 │ ion_ignores_test_y     │ ints     │ test-labe │ il │ and hashes │ -depend │       │
│   │                        │ depend   │ l arrays  │ d  │ identical  │ ent     │       │
│   │                        │ only on  │           │ fe │            │ feature │       │
│   │                        │ structur │           │ at │            │ generat │       │
│   │                        │ es/confi │           │ ur │            │ ion     │       │
│   │                        │ g        │           │ es │            │         │       │
│   │                        │          │           │ tw │            │         │       │
│   │                        │          │           │ ic │            │         │       │
│   │                        │          │           │ e  │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 1 │ test_descriptor_scalin │ Scaler   │ Training/ │ Fi │ Means/scal │ Outcome │ Yes   │
│ 5 │ g_ignores_test_y       │ uses     │ test      │ t  │ es/transfo │ -driven │       │
│   │                        │ structur │ descripto │ sc │ rms        │ scaling │       │
│   │                        │ es/train │ rs plus   │ al │ identical  │         │       │
│   │                        │ ing data │ two       │ er │            │         │       │
│   │                        │ only     │ y_test    │ tw │            │         │       │
│   │                        │          │ arrays    │ ic │            │         │       │
│   │                        │          │           │ e  │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 1 │ test_descriptor_knn_ig │ KNN      │ Fixed     │ Co │ Distances  │ Test    │ Yes   │
│ 6 │ nores_test_y           │ distance │ train/tes │ mp │ identical  │ labels  │       │
│   │                        │ uses     │ t         │ ut │            │ used in │       │
│   │                        │ descript │ descripto │ e  │            │ neighbo │       │
│   │                        │ ors only │ r         │ tw │            │ r       │       │
│   │                        │          │ matrices  │ ic │            │ scoring │       │
│   │                        │          │           │ e  │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 1 │ test_tanimoto_ignores_ │ Tanimoto │ Fixed     │ Co │ Scores     │ Test    │ Yes   │
│ 7 │ test_y                 │ uses     │ query/ref │ mp │ identical  │ outcome │       │
│   │                        │ fingerpr │ erence    │ ut │            │ s       │       │
│   │                        │ ints     │ fingerpri │ e  │            │ affect  │       │
│   │                        │ only     │ nts       │ tw │            │ familia │       │
│   │                        │          │           │ ic │            │ rity    │       │
│   │                        │          │           │ e  │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 1 │ test_qrf_weights_ignor │ Weights  │ Fixed     │ Re │ Weight     │ Test    │ Yes   │
│ 8 │ e_test_y               │ use RF,  │ fitted    │ co │ matrices   │ outcome │       │
│   │                        │ X, and   │ synthetic │ ve │ identical  │ s enter │       │
│   │                        │ training │ RF and    │ r  │            │ QRF     │       │
│   │                        │ rows     │ two       │ we │            │ kernel  │       │
│   │                        │ only     │ y_test    │ ig │            │         │       │
│   │                        │          │ arrays    │ ht │            │         │       │
│   │                        │          │           │ s  │            │         │       │
│   │                        │          │           │ tw │            │         │       │
│   │                        │          │           │ ic │            │         │       │
│   │                        │          │           │ e  │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 1 │ test_qrf_width_ignores │ Q10/Q90  │ Fixed     │ Co │ Q10, Q90,  │ Test    │ Yes   │
│ 9 │ _test_y                │ use      │ weights/t │ mp │ widths     │ outcome │       │
│   │                        │ weights  │ raining   │ ut │ identical  │ s       │       │
│   │                        │ and      │ labels    │ e  │            │ affect  │       │
│   │                        │ y_train  │           │ wi │            │ uncerta │       │
│   │                        │ only     │           │ dt │            │ inty    │       │
│   │                        │          │           │ hs │            │         │       │
│   │                        │          │           │ tw │            │         │       │
│   │                        │          │           │ ic │            │         │       │
│   │                        │          │           │ e  │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 2 │ test_neff_ignores_test │ 1/N_eff  │ Fixed     │ Co │ Identical  │ Test    │ Yes   │
│ 0 │ _y                     │ uses     │ weight    │ mp │ inverse    │ outcome │       │
│   │                        │ weights  │ vectors   │ ut │ effective  │ s       │       │
│   │                        │ only     │           │ e  │ sizes      │ affect  │       │
│   │                        │          │           │ tw │            │ support │       │
│   │                        │          │           │ ic │            │ metric  │       │
│   │                        │          │           │ e  │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 2 │ test_local_sd_uses_tra │ Local SD │ Fixed     │ Co │ Identical  │ Test    │ Yes   │
│ 1 │ ining_y_only           │ uses QRF │ weights/t │ mp │ local SD   │ labels  │       │
│   │                        │ weights  │ raining   │ ut │            │ enter   │       │
│   │                        │ and      │ labels;   │ e  │            │ heterog │       │
│   │                        │ y_train  │ two       │ tw │            │ eneity  │       │
│   │                        │          │ test-labe │ ic │            │         │       │
│   │                        │          │ l arrays  │ e  │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 2 │ test_tree_sd_ignores_t │ Tree     │ Fixed     │ Co │ Identical  │ Test    │ Yes   │
│ 2 │ est_y                  │ predicti │ RF/test   │ mp │ tree SD    │ outcome │       │
│   │                        │ on SD    │ X; two    │ ut │            │ s       │       │
│   │                        │ uses     │ test-labe │ e  │            │ affect  │       │
│   │                        │ fitted   │ l arrays  │ tw │            │ tree    │       │
│   │                        │ trees    │           │ ic │            │ uncerta │       │
│   │                        │ and X    │           │ e  │            │ inty    │       │
│   │                        │ only     │           │    │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 2 │ test_point_prediction_ │ RF       │ Fixed     │ Pr │ Identical  │ Test    │ Yes   │
│ 3 │ ignores_test_y         │ predicti │ RF/test   │ ed │ prediction │ labels  │       │
│   │                        │ on uses  │ X; two    │ ic │ s          │ influen │       │
│   │                        │ fitted   │ test-labe │ t  │            │ ce      │       │
│   │                        │ RF and X │ l arrays  │ tw │            │ predict │       │
│   │                        │ only     │           │ ic │            │ ion     │       │
│   │                        │          │           │ e  │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 2 │ test_uncertainty_order │ Ordering │ Fixed     │ Ra │ Identical  │ Residua │ Yes   │
│ 4 │ _ignores_test_y        │ derives  │ uncertain │ nk │ ranks      │ l-based │       │
│   │                        │ only     │ ty        │ tw │            │ orderin │       │
│   │                        │ from     │ vector;   │ ic │            │ g       │       │
│   │                        │ frozen   │ two       │ e  │            │         │       │
│   │                        │ uncertai │ labels    │    │            │         │       │
│   │                        │ nty      │           │    │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 2 │ test_tie_breaking_igno │ Ties use │ Equal     │ Ra │ Identical  │ Outcome │ Yes   │
│ 5 │ res_test_y             │ activity │ uncertain │ nk │ hash order │ -depend │       │
│   │                        │ -ID      │ ty        │ tw │            │ ent tie │       │
│   │                        │ SHA-256  │ values;   │ ic │            │ resolut │       │
│   │                        │ only     │ two       │ e  │            │ ion     │       │
│   │                        │          │ labels    │    │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 2 │ test_retention_set_ign │ Retained │ Fixed     │ Bu │ Masks      │ Outcome │ Yes   │
│ 6 │ ores_test_y            │ IDs      │ IDs/folds │ il │ identical  │ -based  │       │
│   │                        │ depend   │ /uncertai │ d  │            │ retenti │       │
│   │                        │ only on  │ nty; two  │ ma │            │ on      │       │
│   │                        │ fold,    │ labels    │ sk │            │         │       │
│   │                        │ uncertai │           │ s  │            │         │       │
│   │                        │ nty,     │           │ tw │            │         │       │
│   │                        │ kappa    │           │ ic │            │         │       │
│   │                        │          │           │ e  │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 2 │ test_random_ids_ignore │ Random   │ Fixed     │ Ge │ Draw       │ Residua │ Yes   │
│ 7 │ _test_y                │ retained │ fold IDs  │ ne │ streams    │ l-guide │       │
│   │                        │ IDs use  │ and seed; │ ra │ identical  │ d       │       │
│   │                        │ IDs,     │ two       │ te │            │ random  │       │
│   │                        │ counts,  │ labels    │ dr │            │ baselin │       │
│   │                        │ seed     │           │ aw │            │ e       │       │
│   │                        │ only     │           │ s  │            │         │       │
│   │                        │          │           │ tw │            │         │       │
│   │                        │          │           │ ic │            │         │       │
│   │                        │          │           │ e  │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 2 │ test_bootstrap_draws_i │ Bootstra │ Fixed     │ Ge │ Draw IDs   │ Test    │ Yes   │
│ 8 │ gnore_test_y           │ p        │ fold/scaf │ ne │ and row    │ outcome │       │
│   │                        │ selectio │ fold      │ ra │ indices    │ s       │       │
│   │                        │ n uses   │ table;    │ te │ identical  │ affect  │       │
│   │                        │ scaffold │ two       │ dr │            │ resampl │       │
│   │                        │ /fold/se │ labels    │ aw │            │ ing     │       │
│   │                        │ ed only  │           │ s  │            │         │       │
│   │                        │          │           │ tw │            │         │       │
│   │                        │          │           │ ic │            │         │       │
│   │                        │          │           │ e  │            │         │       │
├───┼────────────────────────┼──────────┼───────────┼────┼────────────┼─────────┼───────┤
│ 2 │ test_conformal_split_i │ Proper/c │ Fixed     │ Sp │ Identical  │ Outcome │ Yes   │
│ 9 │ gnores_outcomes        │ alibrati │ fold      │ li │ proper/cal │ -based  │       │
│   │                        │ on       │ table;    │ t  │ ibration   │ conform │       │
│   │                        │ membersh │ altered   │ tw │ IDs        │ al      │       │
│   │                        │ ip uses  │ all       │ ic │            │ split   │       │
│   │                        │ fold/sca │ outcomes  │ e  │            │         │       │
│   │                        │ ffold/ha │           │    │            │         │       │
│   │                        │ sh only  │           │    │            │         │       │
└───┴────────────────────────┴──────────┴───────────┴────┴────────────┴─────────┴───────┘

D. Training-only information boundaries

┌───┬────────────────────────────────┬──────────┬───────┬──────┬────────┬───────┬───────┐
│ T │ TEST NAME                      │ INVARIAN │ MINIM │ ACTI │ EXPECT │ WHAT  │ PRE-E │
│ E │                                │ T        │ AL    │ ON   │ ED     │ BUG   │ XECUT │
│ S │                                │          │ SYNTH │      │ ASSERT │ IT    │ ION   │
│ T │                                │          │ ETIC  │      │ ION    │ CATCH │       │
│ I │                                │          │ FIXTU │      │        │ ES    │       │
│ D │                                │          │ RE    │      │        │       │       │
├───┼────────────────────────────────┼──────────┼───────┼──────┼────────┼───────┼───────┤
│ 3 │ test_scaler_fit_rows_are_train │ .fit()   │ Spy   │ Run  │ Fit    │ Test- │ Yes   │
│ 0 │ ing_only                       │ receives │ scale │ phys │ argume │ compo │       │
│   │                                │ only     │ r;    │ chem │ nt     │ und   │       │
│   │                                │ outer-tr │ disti │ stag │ equals │ scale │       │
│   │                                │ aining   │ nct   │ e    │ train  │ r fit │       │
│   │                                │ descript │ train │      │ matrix │       │       │
│   │                                │ ors      │ /test │      │ exactl │       │       │
│   │                                │          │ matri │      │ y      │       │       │
│   │                                │          │ ces   │      │        │       │       │
├───┼────────────────────────────────┼──────────┼───────┼──────┼────────┼───────┼───────┤
│ 3 │ test_knn_candidates_are_traini │ Neighbor │ Ident │ Run  │ Refere │ Test  │ Yes   │
│ 1 │ ng_only                        │ s come   │ ical  │ KNN  │ nce    │ refer │       │
│   │                                │ from     │ test  │ stag │ matrix │ ence  │       │
│   │                                │ outer    │ molec │ e    │ contai │ conta │       │
│   │                                │ training │ ule   │      │ ns no  │ minat │       │
│   │                                │          │ and   │      │ test   │ ion   │       │
│   │                                │          │ disti │      │ row    │       │       │
│   │                                │          │ nct   │      │        │       │       │
│   │                                │          │ train │      │        │       │       │
│   │                                │          │ ing   │      │        │       │       │
│   │                                │          │ molec │      │        │       │       │
│   │                                │          │ ules  │      │        │       │       │
├───┼────────────────────────────────┼──────────┼───────┼──────┼────────┼───────┼───────┤
│ 3 │ test_tanimoto_reference_is_tra │ Tanimoto │ Ident │ Run  │ Test   │ Test  │ Yes   │
│ 2 │ ining_only                     │ referenc │ ical  │ comp │ finger │ finge │       │
│   │                                │ e is     │ test  │ arat │ print  │ rprin │       │
│   │                                │ outer    │ finge │ or   │ never  │ t     │       │
│   │                                │ training │ rprin │      │ passed │ leaka │       │
│   │                                │          │ t     │      │ ;      │ ge    │       │
│   │                                │          │ plus  │      │ score  │       │       │
│   │                                │          │ nonid │      │ exclud │       │       │
│   │                                │          │ entic │      │ es it  │       │       │
│   │                                │          │ al    │      │        │       │       │
│   │                                │          │ train │      │        │       │       │
│   │                                │          │ finge │      │        │       │       │
│   │                                │          │ rprin │      │        │       │       │
│   │                                │          │ t     │      │        │       │       │
├───┼────────────────────────────────┼──────────┼───────┼──────┼────────┼───────┼───────┤
│ 3 │ test_qrf_weights_index_trainin │ Weight   │ RF    │ Reco │ Weight │ Test  │ Yes   │
│ 3 │ g_only                         │ vector   │ with  │ ver  │ vector │ rows  │       │
│   │                                │ indexes  │ known │ weig │ length │ in    │       │
│   │                                │ only     │ train │ hts  │ /index │ QRF   │       │
│   │                                │ train    │ ing   │      │ map    │ suppo │       │
│   │                                │ observat │ IDs   │      │ equals │ rt    │       │
│   │                                │ ions     │       │      │ train  │       │       │
│   │                                │          │       │      │ IDs    │       │       │
│   │                                │          │       │      │ only   │       │       │
├───┼────────────────────────────────┼──────────┼───────┼──────┼────────┼───────┼───────┤
│ 3 │ test_local_sd_receives_trainin │ Local SD │ Spy   │ Run  │ Captur │ Test  │ Yes   │
│ 4 │ g_labels_only                  │ input    │ local │ comp │ ed     │ outco │       │
│   │                                │ labels   │ -SD   │ arat │ labels │ mes   │       │
│   │                                │ are      │ funct │ or   │ equal  │ in    │       │
│   │                                │ y_train  │ ion   │ stag │ traini │ local │       │
│   │                                │          │       │ e    │ ng     │ SD    │       │
│   │                                │          │       │      │ labels │       │       │
├───┼────────────────────────────────┼──────────┼───────┼──────┼────────┼───────┼───────┤
│ 3 │ test_no_same_fold_test_referen │ No       │ Expli │ Run  │ Every  │ Same- │ Yes   │
│ 5 │ ce                             │ comparat │ cit   │ all  │ refere │ fold  │       │
│   │                                │ or       │ train │ comp │ nce-ID │ refer │       │
│   │                                │ referenc │ /test │ arat │ set is │ ence  │       │
│   │                                │ e        │ ID    │ ors  │ subset │ leaka │       │
│   │                                │ contains │ and   │      │ of     │ ge    │       │
│   │                                │ same-fol │ scaff │      │ outer  │       │       │
│   │                                │ d test   │ old   │      │ train  │       │       │
│   │                                │ molecule │ maps  │      │ IDs    │       │       │
│   │                                │ s        │       │      │        │       │       │
├───┼────────────────────────────────┼──────────┼───────┼──────┼────────┼───────┼───────┤
│ 3 │ test_conformal_groups_are_oute │ Proper/c │ Group │ Buil │ Union  │ Confo │ Yes   │
│ 6 │ r_training_and_disjoint        │ alibrati │ ed    │ d    │ equals │ rmal  │       │
│   │                                │ on       │ outer │ spli │ outer  │ train │       │
│   │                                │ groups   │ fold  │ t    │ traini │ /test │       │
│   │                                │ are      │ fixtu │      │ ng     │ conta │       │
│   │                                │ disjoint │ re    │      │ IDs;   │ minat │       │
│   │                                │ and      │       │      │ inters │ ion   │       │
│   │                                │ train-on │       │      │ ection │       │       │
│   │                                │ ly       │       │      │ empty; │       │       │
│   │                                │          │       │      │ no     │       │       │
│   │                                │          │       │      │ scaffo │       │       │
│   │                                │          │       │      │ ld     │       │       │
│   │                                │          │       │      │ overla │       │       │
│   │                                │          │       │      │ p      │       │       │
└───┴────────────────────────────────┴──────────┴───────┴──────┴────────┴───────┴───────┘

E. Prediction/uncertainty freeze boundary

┌───┬─────────────────────────────┬────────┬───────┬─────┬────────┬────────────┬────────┐
│ T │ TEST NAME                   │ INVARI │ MINIM │ ACT │ EXPECT │ WHAT BUG   │ PRE-EX │
│ E │                             │ ANT    │ AL    │ ION │ ED     │ IT CATCHES │ ECUTIO │
│ S │                             │        │ SYNTH │     │ ASSERT │            │ N      │
│ T │                             │        │ ETIC  │     │ ION    │            │        │
│ I │                             │        │ FIXTU │     │        │            │        │
│ D │                             │        │ RE    │     │        │            │        │
├───┼─────────────────────────────┼────────┼───────┼─────┼────────┼────────────┼────────┤
│ 3 │ test_prediction_freeze_prec │ Freeze │ Outco │ Run │ Event  │ Premature  │ Runner │
│ 7 │ edes_outcome_evaluation     │ event  │ me    │ syn │ order  │ outcome    │ -requi │
│   │                             │ preced │ senti │ the │ is     │ access     │ red    │
│   │                             │ es     │ nel   │ tic │ freeze │            │        │
│   │                             │ first  │ and   │ run │ <      │            │        │
│   │                             │ y_test │ stage │ ner │ evalua │            │        │
│   │                             │ access │ event │     │ te;    │            │        │
│   │                             │        │ log   │     │ sentin │            │        │
│   │                             │        │       │     │ el is  │            │        │
│   │                             │        │       │     │ untouc │            │        │
│   │                             │        │       │     │ hed    │            │        │
│   │                             │        │       │     │ before │            │        │
│   │                             │        │       │     │ freeze │            │        │
├───┼─────────────────────────────┼────────┼───────┼─────┼────────┼────────────┼────────┤
│ 3 │ test_prediction_freeze_hash │ Freeze │ Deter │ Com │ Manife │ Unverifiab │ Runner │
│ 8 │ _recorded                   │ artifa │ minis │ ple │ st     │ le         │ -requi │
│   │                             │ ct     │ tic   │ te  │ contai │ upstream   │ red    │
│   │                             │ hash   │ predi │ fre │ ns     │ artifact   │        │
│   │                             │ is     │ ction │ eze │ matchi │            │        │
│   │                             │ record │ table │ sta │ ng     │            │        │
│   │                             │ ed     │       │ ge  │ SHA-25 │            │        │
│   │                             │        │       │     │ 6      │            │        │
├───┼─────────────────────────────┼────────┼───────┼─────┼────────┼────────────┼────────┤
│ 3 │ test_downstream_changes_can │ Evalua │ Freez │ Run │ Freeze │ Metrics    │ Runner │
│ 9 │ not_mutate_freeze           │ tion   │ e     │ eva │ bytes/ │ mutate     │ -requi │
│   │                             │ is     │ table │ lua │ hash   │ prediction │ red    │
│   │                             │ downst │ plus  │ tio │ remain │ s/uncertai │        │
│   │                             │ ream-o │ alter │ n   │ unchan │ nty        │        │
│   │                             │ nly    │ nate  │ twi │ ged    │            │        │
│   │                             │        │ outco │ ce  │        │            │        │
│   │                             │        │ me    │     │        │            │        │
│   │                             │        │ array │     │        │            │        │
│   │                             │        │ s     │     │        │            │        │
├───┼─────────────────────────────┼────────┼───────┼─────┼────────┼────────────┼────────┤
│ 4 │ test_repeated_evaluation_re │ Same   │ Seale │ Reo │ Upstre │ Recompute  │ Runner │
│ 0 │ produces_upstream_hash      │ freeze │ d     │ pen │ am     │ drift      │ -requi │
│   │                             │ artifa │ synth │ eva │ hash   │            │ red    │
│   │                             │ ct     │ etic  │ lua │ is     │            │        │
│   │                             │ reprod │ freez │ tio │ identi │            │        │
│   │                             │ uces   │ e     │ n   │ cal    │            │        │
│   │                             │ upstre │ file  │ twi │        │            │        │
│   │                             │ am     │       │ ce  │        │            │        │
│   │                             │ state  │       │     │        │            │        │
├───┼─────────────────────────────┼────────┼───────┼─────┼────────┼────────────┼────────┤
│ 4 │ test_prediction_freeze_over │ Freeze │ Exist │ Att │ Write  │ Silent     │ Runner │
│ 1 │ write_rejected              │ artifa │ ing   │ emp │ fails  │ upstream   │ -requi │
│   │                             │ ct     │ seale │ t   │ closed │ replacemen │ red    │
│   │                             │ immuta │ d     │ ove │ ;      │ t          │        │
│   │                             │ ble    │ freez │ rwr │ origin │            │        │
│   │                             │        │ e     │ ite │ al     │            │        │
│   │                             │        │ file  │     │ bytes/ │            │        │
│   │                             │        │       │     │ hash   │            │        │
│   │                             │        │       │     │ unchan │            │        │
│   │                             │        │       │     │ ged    │            │        │
└───┴─────────────────────────────┴────────┴───────┴─────┴────────┴────────────┴────────┘

Required frozen record fields for tests 37–41:

activity_id
outer_fold
rf_prediction
qrf_q10
qrf_q90
qrf_width
tanimoto_unfamiliarity
physchem_knn5_distance
neff_inverse
local_label_sd
tree_sd
uncertainty method/rank/tie metadata

F. Within-fold retention

┌───┬────────────────────────────┬────────┬───────┬──────┬─────────┬───────────┬────────┐
│ T │ TEST NAME                  │ INVARI │ MINIM │ ACTI │ EXPECTE │ WHAT BUG  │ PRE-EX │
│ E │                            │ ANT    │ AL    │ ON   │ D       │ IT        │ ECUTIO │
│ S │                            │        │ SYNTH │      │ ASSERTI │ CATCHES   │ N      │
│ T │                            │        │ ETIC  │      │ ON      │           │        │
│ I │                            │        │ FIXTU │      │         │           │        │
│ D │                            │        │ RE    │      │         │           │        │
├───┼────────────────────────────┼────────┼───────┼──────┼─────────┼───────────┼────────┤
│ 4 │ test_ranking_is_per_outer_ │ Each   │ Two   │ Buil │ Per-fol │ Global    │ Yes    │
│ 2 │ fold                       │ fold   │ folds │ d    │ d ranks │ ranking   │        │
│   │                            │ is     │ with  │ rete │ match   │           │        │
│   │                            │ ranked │ unequ │ ntio │ indepen │           │        │
│   │                            │ indepe │ al    │ n    │ dent    │           │        │
│   │                            │ ndentl │ uncer │ mask │ select_ │           │        │
│   │                            │ y      │ taint │ s    │ retaine │           │        │
│   │                            │        │ y     │      │ d()     │           │        │
│   │                            │        │ scale │      │ calls   │           │        │
│   │                            │        │ s     │      │         │           │        │
├───┼────────────────────────────┼────────┼───────┼──────┼─────────┼───────────┼────────┤
│ 4 │ test_global_pooling_change │ Global │ Fold  │ Comp │ Runner  │ Global    │ Yes    │
│ 3 │ s_fixture_and_is_rejected  │ poolin │ 1     │ are  │ retains │ uncertain │        │
│   │                            │ g is   │ [.1,. │ runn │ two     │ ty        │        │
│   │                            │ prohib │ 2,.3, │ er   │ from    │ pooling   │        │
│   │                            │ ited   │ .4];  │ IDs  │ each    │           │        │
│   │                            │        │ fold  │ with │ fold,   │           │        │
│   │                            │        │ 2     │ glob │ not two │           │        │
│   │                            │        │ [10,2 │ al-s │ globall │           │        │
│   │                            │        │ 0,30, │ ort  │ y       │           │        │
│   │                            │        │ 40];  │ IDs  │ smalles │           │        │
│   │                            │        │ kappa │      │ t       │           │        │
│   │                            │        │ .5    │      │         │           │        │
├───┼────────────────────────────┼────────┼───────┼──────┼─────────┼───────────┼────────┤
│ 4 │ test_all_frozen_coverages_ │ Count  │ Unequ │ Eval │ Every   │ Floor/rou │ Yes    │
│ 4 │ use_ceil_per_fold          │ is     │ al    │ uate │ fold    │ nd/global │        │
│   │                            │ ceil(k │ folds │ all  │ count   │ count     │        │
│   │                            │ appa*n │ sizes │ six  │ equals  │           │        │
│   │                            │ _f)    │ 3, 4, │ cove │ exact   │           │        │
│   │                            │        │ 7     │ rage │ ceil    │           │        │
│   │                            │        │       │ s    │ rule    │           │        │
├───┼────────────────────────────┼────────┼───────┼──────┼─────────┼───────────┼────────┤
│ 4 │ test_lowest_uncertainty_re │ Lowest │ One   │ Sele │ Expecte │ Reversed  │ Yes    │
│ 5 │ tained                     │ uncert │ fold  │ ct   │ d       │ or        │        │
│   │                            │ ainty  │ with  │ at   │ lowest  │ descendin │        │
│   │                            │ wins   │ uniqu │ .5   │ half    │ g         │        │
│   │                            │        │ e     │      │ retaine │ selection │        │
│   │                            │        │ uncer │      │ d       │           │        │
│   │                            │        │ taint │      │         │           │        │
│   │                            │        │ y     │      │         │           │        │
│   │                            │        │ value │      │         │           │        │
│   │                            │        │ s     │      │         │           │        │
├───┼────────────────────────────┼────────┼───────┼──────┼─────────┼───────────┼────────┤
│ 4 │ test_activity_id_tie_hash_ │ Ties   │ Equal │ Shuf │ Same    │ Input-ord │ Yes    │
│ 6 │ is_deterministic           │ use    │ uncer │ fle  │ IDs     │ er-depend │        │
│   │                            │ SHA-25 │ taint │ inpu │ retaine │ ent ties  │        │
│   │                            │ 6      │ ies   │ t    │ d;      │           │        │
│   │                            │ activi │ and   │ and  │ known   │           │        │
│   │                            │ ty ID  │ known │ rank │ hash    │           │        │
│   │                            │ salt   │ IDs   │ repe │ orderin │           │        │
│   │                            │        │       │ ated │ g       │           │        │
│   │                            │        │       │ ly   │         │           │        │
├───┼────────────────────────────┼────────┼───────┼──────┼─────────┼───────────┼────────┤
│ 4 │ test_retention_frozen_befo │ Metric │ Outco │ Run  │ Retenti │ Outcome-g │ Runner │
│ 7 │ re_metrics                 │ s      │ me    │ sele │ on      │ uided     │ -requi │
│   │                            │ cannot │ senti │ ctio │ event   │ retention │ red    │
│   │                            │ alter  │ nel   │ n    │ precede │           │        │
│   │                            │ masks  │ and   │ then │ s all   │           │        │
│   │                            │        │ event │ metr │ outcome │           │        │
│   │                            │        │ log   │ ic   │ access; │           │        │
│   │                            │        │       │ stag │ mask    │           │        │
│   │                            │        │       │ e    │ unchang │           │        │
│   │                            │        │       │      │ ed      │           │        │
└───┴────────────────────────────┴────────┴───────┴──────┴─────────┴───────────┴────────┘

G. Random deferral

┌───┬─────────────────────────────┬───────────┬────────┬─────┬────────┬─────────┬───────┐
│ T │ TEST NAME                   │ INVARIANT │ MINIMA │ ACT │ EXPECT │ WHAT    │ PRE-E │
│ E │                             │           │ L      │ ION │ ED     │ BUG IT  │ XECUT │
│ S │                             │           │ SYNTHE │     │ ASSERT │ CATCHES │ ION   │
│ T │                             │           │ TIC    │     │ ION    │         │       │
│ I │                             │           │ FIXTUR │     │        │         │       │
│ D │                             │           │ E      │     │        │         │       │
├───┼─────────────────────────────┼───────────┼────────┼─────┼────────┼─────────┼───────┤
│ 4 │ test_random_production_draw │ Frozen    │ Inspec │ Sta │ Count  │ Silent  │ Yes   │
│ 8 │ _count_is_10000             │ count is  │ t      │ rt  │ equals │ draw-co │       │
│   │                             │ C.N_RANDO │ runner │ ran │ 10,000 │ unt     │       │
│   │                             │ M_DEFERRA │ config │ dom │ ;      │ change  │       │
│   │                             │ LS        │ /defau │ eng │ altere │         │       │
│   │                             │           │ lt     │ ine │ d      │         │       │
│   │                             │           │        │     │ count  │         │       │
│   │                             │           │        │     │ reject │         │       │
│   │                             │           │        │     │ ed in  │         │       │
│   │                             │           │        │     │ produc │         │       │
│   │                             │           │        │     │ tion   │         │       │
│   │                             │           │        │     │ mode   │         │       │
├───┼─────────────────────────────┼───────────┼────────┼─────┼────────┼─────────┼───────┤
│ 4 │ test_random_counts_match_qr │ Random    │ Unequa │ Gen │ Every  │ Unmatch │ Yes   │
│ 9 │ f_per_fold                  │ count     │ l      │ era │ draw   │ ed      │       │
│   │                             │ equals    │ folds, │ te  │ matche │ baselin │       │
│   │                             │ QRF count │ kappa  │ dra │ s QRF  │ e       │       │
│   │                             │ per fold  │ .8     │ ws  │ per-fo │         │       │
│   │                             │           │        │     │ ld     │         │       │
│   │                             │           │        │     │ retain │         │       │
│   │                             │           │        │     │ ed     │         │       │
│   │                             │           │        │     │ counts │         │       │
├───┼─────────────────────────────┼───────────┼────────┼─────┼────────┼─────────┼───────┤
│ 5 │ test_random_seed_is_2026092 │ Frozen    │ Fixed  │ Gen │ Stream │ Seed    │ Yes   │
│ 0 │ 3                           │ seed is   │ fold   │ era │ s      │ drift   │       │
│   │                             │ used      │ IDs    │ te  │ match  │         │       │
│   │                             │           │        │ exp │ seed   │         │       │
│   │                             │           │        │ ect │ 202609 │         │       │
│   │                             │           │        │ ed  │ 23     │         │       │
│   │                             │           │        │ str │        │         │       │
│   │                             │           │        │ eam │        │         │       │
│   │                             │           │        │ and │        │         │       │
│   │                             │           │        │ run │        │         │       │
│   │                             │           │        │ ner │        │         │       │
│   │                             │           │        │ str │        │         │       │
│   │                             │           │        │ eam │        │         │       │
├───┼─────────────────────────────┼───────────┼────────┼─────┼────────┼─────────┼───────┤
│ 5 │ test_random_selection_does_ │ Random    │ Outcom │ Gen │ Sentin │ Outcome │ Yes   │
│ 1 │ not_receive_outcomes        │ IDs       │ e      │ era │ el is  │ -guided │       │
│   │                             │ depend    │ sentin │ te  │ not    │ random  │       │
│   │                             │ only on   │ el     │ IDs │ access │ selecti │       │
│   │                             │ IDs/count │        │     │ ed;    │ on      │       │
│   │                             │ s/seed    │        │     │ IDs    │         │       │
│   │                             │           │        │     │ unchan │         │       │
│   │                             │           │        │     │ ged    │         │       │
│   │                             │           │        │     │ under  │         │       │
│   │                             │           │        │     │ altere │         │       │
│   │                             │           │        │     │ d      │         │       │
│   │                             │           │        │     │ labels │         │       │
├───┼─────────────────────────────┼───────────┼────────┼─────┼────────┼─────────┼───────┤
│ 5 │ test_random_draw_stream_rep │ Same      │ Fixed  │ Run │ Ordere │ Nondete │ Yes   │
│ 2 │ roducible                   │ input/see │ fold   │ twi │ d draw │ rminist │       │
│   │                             │ d gives   │ IDs    │ ce  │ stream │ ic      │       │
│   │                             │ same      │        │     │ s      │ baselin │       │
│   │                             │ draws     │        │     │ identi │ e       │       │
│   │                             │           │        │     │ cal    │         │       │
└───┴─────────────────────────────┴───────────┴────────┴─────┴────────┴─────────┴───────┘

H. Outcome-dependent evaluation after freeze

┌───┬──────────────────────────┬──────────┬───────────┬───────┬────────┬───────┬────────┐
│ T │ TEST NAME                │ INVARIAN │ MINIMAL   │ ACTIO │ EXPECT │ WHAT  │ PRE-EX │
│ E │                          │ T        │ SYNTHETIC │ N     │ ED     │ BUG   │ ECUTIO │
│ S │                          │          │ FIXTURE   │       │ ASSERT │ IT    │ N      │
│ T │                          │          │           │       │ ION    │ CATCH │        │
│ I │                          │          │           │       │        │ ES    │        │
│ D │                          │          │           │       │        │       │        │
├───┼──────────────────────────┼──────────┼───────────┼───────┼────────┼───────┼────────┤
│ 5 │ test_rmse_requires_froze │ RMSE     │ Runner    │ Call  │ Fails  │ Prema │ Runner │
│ 3 │ n_predictions            │ cannot   │ state     │ RMSE  │ closed │ ture  │ -requi │
│   │                          │ run      │ PREDICTIO │ stage │        │ metri │ red    │
│   │                          │ before   │ NS_NOT_FR │       │        │ c     │        │
│   │                          │ freeze   │ OZEN      │       │        │ evalu │        │
│   │                          │          │           │       │        │ ation │        │
├───┼──────────────────────────┼──────────┼───────────┼───────┼────────┼───────┼────────┤
│ 5 │ test_mae_requires_frozen │ MAE      │ Same      │ Call  │ Fails  │ Prema │ Runner │
│ 4 │ _predictions             │ cannot   │           │ MAE   │ closed │ ture  │ -requi │
│   │                          │ run      │           │ stage │        │ metri │ red    │
│   │                          │ before   │           │       │        │ c     │        │
│   │                          │ freeze   │           │       │        │ evalu │        │
│   │                          │          │           │       │        │ ation │        │
├───┼──────────────────────────┼──────────┼───────────┼───────┼────────┼───────┼────────┤
│ 5 │ test_rel_benefit_require │ Primary  │ Missing   │ Call  │ Fails  │ Prima │ Runner │
│ 5 │ s_frozen_inputs          │ estimand │ freeze    │ estim │ closed │ ry    │ -requi │
│   │                          │ requires │ marker    │ and   │        │ resul │ red    │
│   │                          │ frozen   │           │ stage │        │ t     │        │
│   │                          │ QRF/rand │           │       │        │ befor │        │
│   │                          │ om       │           │       │        │ e     │        │
│   │                          │ metrics  │           │       │        │ freez │        │
│   │                          │          │           │       │        │ e     │        │
├───┼──────────────────────────┼──────────┼───────────┼───────┼────────┼───────┼────────┤
│ 5 │ test_deferred_enrichment │ Enrichme │ Missing   │ Call  │ Fails  │ Early │ Runner │
│ 6 │ _requires_freeze         │ nt uses  │ freeze    │ enric │ closed │ error │ -requi │
│   │                          │ frozen   │ marker    │ hment │        │ strat │ red    │
│   │                          │ predicti │           │ stage │        │ ifica │        │
│   │                          │ ons/rete │           │       │        │ tion  │        │
│   │                          │ ntion    │           │       │        │       │        │
├───┼──────────────────────────┼──────────┼───────────┼───────┼────────┼───────┼────────┤
│ 5 │ test_error_discriminatio │ Error    │ Missing   │ Call  │ Fails  │ Error │ Runner │
│ 7 │ n_requires_freeze        │ labels   │ freeze    │ discr │ closed │ -deri │ -requi │
│   │                          │ are      │ marker    │ imina │        │ ved   │ red    │
│   │                          │ downstre │           │ tion  │        │ compa │        │
│   │                          │ am-only  │           │ stage │        │ rator │        │
│   │                          │          │           │       │        │ const │        │
│   │                          │          │           │       │        │ ructi │        │
│   │                          │          │           │       │        │ on    │        │
├───┼──────────────────────────┼──────────┼───────────┼───────┼────────┼───────┼────────┤
│ 5 │ test_outcome_diagnostics │ Downstre │ Frozen    │ Run   │ Upstre │ Feedb │ Runner │
│ 8 │ _cannot_mutate_upstream  │ am       │ artifact  │ diagn │ am     │ ack   │ -requi │
│   │                          │ outcomes │ and       │ ostic │ bytes/ │ from  │ red    │
│   │                          │ are      │ altered   │ s     │ hash/c │ diagn │        │
│   │                          │ read-onl │ outcomes  │       │ onfig  │ ostic │        │
│   │                          │ y        │           │       │ remain │ s     │        │
│   │                          │ relative │           │       │ unchan │       │        │
│   │                          │ to       │           │       │ ged    │       │        │
│   │                          │ freeze   │           │       │        │       │        │
└───┴──────────────────────────┴──────────┴───────────┴───────┴────────┴───────┴────────┘

I. Primary estimand

┌───┬───────────────────────────┬───────┬──────────┬─────────┬───────┬─────────┬────────┐
│ T │ TEST NAME                 │ INVAR │ MINIMAL  │ ACTION  │ EXPEC │ WHAT    │ PRE-EX │
│ E │                           │ IANT  │ SYNTHETI │         │ TED   │ BUG IT  │ ECUTIO │
│ S │                           │       │ C        │         │ ASSER │ CATCHES │ N      │
│ T │                           │       │ FIXTURE  │         │ TION  │         │        │
│ I │                           │       │          │         │       │         │        │
│ D │                           │       │          │         │       │         │        │
├───┼───────────────────────────┼───────┼──────────┼─────────┼───────┼─────────┼────────┤
│ 5 │ test_rel_benefit_formula_ │ Formu │ random=. │ Compute │ Resul │ Formula │ Yes    │
│ 9 │ exact                     │ la is │ 8,       │ estiman │ t     │ /sign   │        │
│   │                           │ (rand │ qrf=.6   │ d       │ equal │ error   │        │
│   │                           │ om -  │          │         │ s .25 │         │        │
│   │                           │ qrf)  │          │         │       │         │        │
│   │                           │ /     │          │         │       │         │        │
│   │                           │ rando │          │         │       │         │        │
│   │                           │ m     │          │         │       │         │        │
├───┼───────────────────────────┼───────┼──────────┼─────────┼───────┼─────────┼────────┤
│ 6 │ test_qrf80_rmse_uses_pool │ QRF80 │ Two      │ Compute │ Resul │ Fold    │ Yes    │
│ 0 │ ed_per_fold_retention     │ RMSE  │ folds    │ QRF80   │ t     │ averagi │        │
│   │                           │ pools │ with     │         │ equal │ ng or   │        │
│   │                           │ selec │ known    │         │ s     │ global  │        │
│   │                           │ ted   │ predicti │         │ RMSE  │ selecti │        │
│   │                           │ rows  │ ons/outc │         │ over  │ on      │        │
│   │                           │ after │ omes     │         │ union │         │        │
│   │                           │ fold- │          │         │ of    │         │        │
│   │                           │ local │          │         │ fold- │         │        │
│   │                           │ selec │          │         │ local │         │        │
│   │                           │ tion  │          │         │ retai │         │        │
│   │                           │       │          │         │ ned   │         │        │
│   │                           │       │          │         │ IDs   │         │        │
├───┼───────────────────────────┼───────┼──────────┼─────────┼───────┼─────────┼────────┤
│ 6 │ test_random80_uses_matche │ Basel │ Fixed    │ Compute │ Resul │ Analyti │ Yes    │
│ 1 │ d_random_procedure        │ ine   │ syntheti │ baselin │ t     │ c/unmat │        │
│   │                           │ equal │ c draw   │ e       │ equal │ ched    │        │
│   │                           │ s     │ stream   │         │ s     │ random  │        │
│   │                           │ mean  │          │         │ mean  │ baselin │        │
│   │                           │ of    │          │         │ draw  │ e       │        │
│   │                           │ presc │          │         │ RMSE  │         │        │
│   │                           │ ribed │          │         │       │         │        │
│   │                           │ draws │          │         │       │         │        │
├───┼───────────────────────────┼───────┼──────────┼─────────┼───────┼─────────┼────────┤
│ 6 │ test_aurc_cannot_replace_ │ Prima │ Syntheti │ Seriali │ Prima │ AURC    │ Runner │
│ 2 │ primary_estimand          │ ry    │ c result │ ze/clas │ ry    │ promote │ -requi │
│   │                           │ resul │ bundle   │ sify    │ decis │ d to    │ red    │
│   │                           │ t key │ with     │ result  │ ion   │ primary │        │
│   │                           │ is    │ altered  │         │ uses  │         │        │
│   │                           │ REL_B │ AURC     │         │ REL_B │         │        │
│   │                           │ ENEFI │          │         │ ENEFI │         │        │
│   │                           │ T_80  │          │         │ T_80  │         │        │
│   │                           │       │          │         │ only  │         │        │
└───┴───────────────────────────┴───────┴──────────┴─────────┴───────┴─────────┴────────┘

J. Coverage curve

┌───┬──────────────────────────┬──────┬───────────┬─────────┬────────┬─────────┬────────┐
│ T │ TEST NAME                │ INVA │ MINIMAL   │ ACTION  │ EXPECT │ WHAT    │ PRE-EX │
│ E │                          │ RIAN │ SYNTHETIC │         │ ED     │ BUG IT  │ ECUTIO │
│ S │                          │ T    │ FIXTURE   │         │ ASSERT │ CATCHES │ N      │
│ T │                          │      │           │         │ ION    │         │        │
│ I │                          │      │           │         │        │         │        │
│ D │                          │      │           │         │        │         │        │
├───┼──────────────────────────┼──────┼───────────┼─────────┼────────┼─────────┼────────┤
│ 6 │ test_all_six_coverages_e │ Grid │ Fixed     │ Run     │ Result │ Missing │ Runner │
│ 3 │ valuated                 │ is   │ uncertain │ curve   │ s      │ coverag │ -requi │
│   │                          │ exac │ ty/predic │ stage   │ contai │ e point │ red    │
│   │                          │ tly  │ tion      │         │ n      │         │        │
│   │                          │ six  │ fixture   │         │ 1,.9,. │         │        │
│   │                          │ froz │           │         │ 8,.7,. │         │        │
│   │                          │ en   │           │         │ 6,.5   │         │        │
│   │                          │ valu │           │         │        │         │        │
│   │                          │ es   │           │         │        │         │        │
├───┼──────────────────────────┼──────┼───────────┼─────────┼────────┼─────────┼────────┤
│ 6 │ test_no_posthoc_coverage │ No   │ Attempt   │ Run     │ Extra  │ Post-ho │ Runner │
│ 4 │ _added                   │ cove │ .85/.95   │ seriali │ covera │ c       │ -requi │
│   │                          │ rage │ result    │ zation  │ ge     │ thresho │ red    │
│   │                          │ outs │           │         │ reject │ ld      │        │
│   │                          │ ide  │           │         │ ed or  │ additio │        │
│   │                          │ froz │           │         │ marked │ n       │        │
│   │                          │ en   │           │         │ nonpro │         │        │
│   │                          │ grid │           │         │ tocol  │         │        │
│   │                          │ is   │           │         │        │         │        │
│   │                          │ prom │           │         │        │         │        │
│   │                          │ oted │           │         │        │         │        │
├───┼──────────────────────────┼──────┼───────────┼─────────┼────────┼─────────┼────────┤
│ 6 │ test_rmse_mae_persisted_ │ Both │ Fixed     │ Run     │ Six    │ Incompl │ Runner │
│ 5 │ for_each_coverage        │ metr │ outcomes/ │ curve   │ RMSE   │ ete     │ -requi │
│   │                          │ ics  │ predictio │         │ and    │ curve   │ red    │
│   │                          │ exis │ ns        │         │ six    │         │        │
│   │                          │ t at │           │         │ MAE    │         │        │
│   │                          │ ever │           │         │ record │         │        │
│   │                          │ y    │           │         │ s per  │         │        │
│   │                          │ kapp │           │         │ method │         │        │
│   │                          │ a    │           │         │        │         │        │
├───┼──────────────────────────┼──────┼───────────┼─────────┼────────┼─────────┼────────┤
│ 6 │ test_retained_deferred_c │ Coun │ Unequal   │ Run     │ Retain │ Missing │ Runner │
│ 6 │ ounts_persisted          │ ts   │ synthetic │ curve   │ ed +   │ /incorr │ -requi │
│   │                          │ are  │ folds     │         │ deferr │ ect     │ red    │
│   │                          │ reco │           │         │ ed     │ counts  │        │
│   │                          │ rded │           │         │ equals │         │        │
│   │                          │ per  │           │         │ fold   │         │        │
│   │                          │ fold │           │         │ size   │         │        │
│   │                          │ and  │           │         │ at     │         │        │
│   │                          │ pool │           │         │ each   │         │        │
│   │                          │ ed   │           │         │ kappa  │         │        │
├───┼──────────────────────────┼──────┼───────────┼─────────┼────────┼─────────┼────────┤
│ 6 │ test_naurc_uses_frozen_r │ nAUR │ Known     │ Compute │ Correc │ Wrong   │ Yes    │
│ 7 │ ange_and_is_secondary    │ C    │ curve     │ /serial │ t      │ range   │        │
│   │                          │ inte │ values    │ ize     │ nAURC; │ or role │        │
│   │                          │ grat │           │         │ no     │         │        │
│   │                          │ es   │           │         │ primar │         │        │
│   │                          │ .5   │           │         │ y-stat │         │        │
│   │                          │ to   │           │         │ e      │         │        │
│   │                          │ 1.0  │           │         │ substi │         │        │
│   │                          │ only │           │         │ tution │         │        │
└───┴──────────────────────────┴──────┴───────────┴─────────┴────────┴─────────┴────────┘

K. Scaffold-clustered bootstrap

┌───┬────────────────────────┬────────┬───────────┬──────┬────────┬────────────┬────────┐
│ T │ TEST NAME              │ INVARI │ MINIMAL   │ ACTI │ EXPECT │ WHAT BUG   │ PRE-EX │
│ E │                        │ ANT    │ SYNTHETIC │ ON   │ ED     │ IT CATCHES │ ECUTIO │
│ S │                        │        │ FIXTURE   │      │ ASSERT │            │ N      │
│ T │                        │        │           │      │ ION    │            │        │
│ I │                        │        │           │      │        │            │        │
│ D │                        │        │           │      │        │            │        │
├───┼────────────────────────┼────────┼───────────┼──────┼────────┼────────────┼────────┤
│ 6 │ test_bootstrap_unit_is │ Whole  │ Multi-row │ Gene │ Every  │ Molecule-l │ Yes    │
│ 8 │ _scaffold              │ scaffo │ scaffold  │ rate │ select │ evel       │        │
│   │                        │ ld     │ groups    │ draw │ ed     │ resampling │        │
│   │                        │ groups │           │ s    │ scaffo │            │        │
│   │                        │ are    │           │      │ ld     │            │        │
│   │                        │ sample │           │      │ contri │            │        │
│   │                        │ d      │           │      │ butes  │            │        │
│   │                        │        │           │      │ all    │            │        │
│   │                        │        │           │      │ rows   │            │        │
├───┼────────────────────────┼────────┼───────────┼──────┼────────┼────────────┼────────┤
│ 6 │ test_bootstrap_is_fold │ Sampli │ Two folds │ Gene │ Fold   │ Cross-fold │ Yes    │
│ 9 │ _stratified            │ ng     │ with      │ rate │ member │ resampling │        │
│   │                        │ occurs │ distinct  │ draw │ ship   │            │        │
│   │                        │ indepe │ scaffold  │ s    │ and    │            │        │
│   │                        │ ndentl │ names     │      │ per-fo │            │        │
│   │                        │ y      │           │      │ ld     │            │        │
│   │                        │ within │           │      │ group  │            │        │
│   │                        │ each   │           │      │ counts │            │        │
│   │                        │ fold   │           │      │ preser │            │        │
│   │                        │        │           │      │ ved    │            │        │
├───┼────────────────────────┼────────┼───────────┼──────┼────────┼────────────┼────────┤
│ 7 │ test_bootstrap_draws_a │ Both   │ Instrumen │ Eval │ Draw   │ Unpaired   │ Yes    │
│ 0 │ re_paired              │ method │ ted       │ uate │ IDs    │ CI         │        │
│   │                        │ s use  │ QRF/rando │ boot │ and    │ comparison │        │
│   │                        │ identi │ m         │ stra │ select │            │        │
│   │                        │ cal    │ evaluator │ p    │ ed     │            │        │
│   │                        │ draw   │ s         │      │ indice │            │        │
│   │                        │        │           │      │ s      │            │        │
│   │                        │        │           │      │ identi │            │        │
│   │                        │        │           │      │ cal    │            │        │
├───┼────────────────────────┼────────┼───────────┼──────┼────────┼────────────┼────────┤
│ 7 │ test_bootstrap_product │ Frozen │ Inspect   │ Init │ B      │ Silent     │ Yes    │
│ 1 │ ion_count_is_10000     │ B is   │ productio │ iali │ equals │ replicate  │        │
│   │                        │ 10,000 │ n config  │ ze   │ 10,000 │ reduction  │        │
│   │                        │        │           │ boot │ ;      │            │        │
│   │                        │        │           │ stra │ altere │            │        │
│   │                        │        │           │ p    │ d B    │            │        │
│   │                        │        │           │      │ reject │            │        │
│   │                        │        │           │      │ ed     │            │        │
├───┼────────────────────────┼────────┼───────────┼──────┼────────┼────────────┼────────┤
│ 7 │ test_bootstrap_seed_is │ Frozen │ Fixed     │ Gene │ Stream │ Seed drift │ Yes    │
│ 2 │ _20260923              │ seed   │ fold/scaf │ rate │ matche │            │        │
│   │                        │ is     │ fold      │ stre │ s      │            │        │
│   │                        │ used   │ fixture   │ am   │ fixed  │            │        │
│   │                        │        │           │      │ expect │            │        │
│   │                        │        │           │      │ ed     │            │        │
│   │                        │        │           │      │ stream │            │        │
├───┼────────────────────────┼────────┼───────────┼──────┼────────┼────────────┼────────┤
│ 7 │ test_bootstrap_percent │ 95%    │ Small     │ Comp │ Identi │ CI         │ Yes    │
│ 3 │ ile_ci_reproducible    │ percen │ fixed     │ ute  │ cal    │ method/non │        │
│   │                        │ tile   │ bootstrap │ CI   │ [Q.025 │ determinis │        │
│   │                        │ CI     │ -statisti │ twic │ ,Q.975 │ m drift    │        │
│   │                        │ determ │ c vector  │ e    │ ]      │            │        │
│   │                        │ inisti │           │      │ values │            │        │
│   │                        │ c      │           │      │        │            │        │
├───┼────────────────────────┼────────┼───────────┼──────┼────────┼────────────┼────────┤
│ 7 │ test_bootstrap_never_s │ Same   │ Scaffold  │ Insp │ No     │ Compound-l │ Yes    │
│ 4 │ plits_scaffold         │ scaffo │ groups    │ ect  │ indepe │ evel       │        │
│   │                        │ ld     │ with 2–3  │ each │ ndentl │ sampling   │        │
│   │                        │ rows   │ rows      │ draw │ y      │            │        │
│   │                        │ share  │           │      │ select │            │        │
│   │                        │ multip │           │      │ ed     │            │        │
│   │                        │ licity │           │      │ subset │            │        │
│   │                        │        │           │      │ of a   │            │        │
│   │                        │        │           │      │ scaffo │            │        │
│   │                        │        │           │      │ ld     │            │        │
└───┴────────────────────────┴────────┴───────────┴──────┴────────┴────────────┴────────┘

L. Three-state primary interpretation

┌───┬───────────────────────────┬────────┬──────┬────┬─────────────────┬────────┬───────┐
│ T │ TEST NAME                 │ INVARI │ MINI │ AC │ EXPECTED        │ WHAT   │ PRE-E │
│ E │                           │ ANT    │ MAL  │ TI │ ASSERTION       │ BUG IT │ XECUT │
│ S │                           │        │ SYNT │ ON │                 │ CATCHE │ ION   │
│ T │                           │        │ HETI │    │                 │ S      │       │
│ I │                           │        │ C    │    │                 │        │       │
│ D │                           │        │ FIXT │    │                 │        │       │
│   │                           │        │ URE  │    │                 │        │       │
├───┼───────────────────────────┼────────┼──────┼────┼─────────────────┼────────┼───────┤
│ 7 │ test_supported_signal_req │ Signal │ Boun │ Cl │ Only qualifying │ Over-p │ Yes   │
│ 5 │ uires_point_and_lower_bou │ iff    │ dary │ as │ cases yield     │ ermiss │       │
│   │ nd                        │ point  │ case │ si │ SUPPORTED_OPERA │ ive    │       │
│   │                           │ ≥ .10  │ s    │ fy │ TIONAL_SIGNAL   │ signal │       │
│   │                           │ and    │ arou │    │                 │        │       │
│   │                           │ lower  │ nd   │    │                 │        │       │
│   │                           │ CI > 0 │ both │    │                 │        │       │
│   │                           │        │ cond │    │                 │        │       │
│   │                           │        │ itio │    │                 │        │       │
│   │                           │        │ ns   │    │                 │        │       │
├───┼───────────────────────────┼────────┼──────┼────┼─────────────────┼────────┼───────┤
│ 7 │ test_below_threshold_requ │ Below- │ Uppe │ Cl │ Only <.10       │ Wrong  │ Yes   │
│ 6 │ ires_upper_ci_below_010   │ thresh │ r CI │ as │ yields          │ inclus │       │
│   │                           │ old    │ .099 │ si │ EVIDENCE_BELOW_ │ ive    │       │
│   │                           │ iff    │ ,    │ fy │ PRACTICAL_THRES │ bounda │       │
│   │                           │ upper  │ .10, │    │ HOLD            │ ry     │       │
│   │                           │ CI <   │ .101 │    │                 │        │       │
│   │                           │ .10    │      │    │                 │        │       │
├───┼───────────────────────────┼────────┼──────┼────┼─────────────────┼────────┼───────┤
│ 7 │ test_all_other_cases_inco │ Every  │ CI   │ Cl │ Result is       │ Forced │ Yes   │
│ 7 │ nclusive                  │ remain │ cros │ as │ INCONCLUSIVE    │ binary │       │
│   │                           │ ing    │ sing │ si │                 │ conclu │       │
│   │                           │ case   │ 0/.1 │ fy │                 │ sion   │       │
│   │                           │ is     │ 0    │    │                 │        │       │
│   │                           │ inconc │ and  │    │                 │        │       │
│   │                           │ lusive │ poin │    │                 │        │       │
│   │                           │        │ t/CI │    │                 │        │       │
│   │                           │        │ comb │    │                 │        │       │
│   │                           │        │ inat │    │                 │        │       │
│   │                           │        │ ions │    │                 │        │       │
├───┼───────────────────────────┼────────┼──────┼────┼─────────────────┼────────┼───────┤
│ 7 │ test_p_value_cannot_overr │ No     │ Same │ Cl │ Classification  │ Reintr │ Yes   │
│ 8 │ ide_state                 │ p-valu │ esti │ as │ unchanged       │ oduced │       │
│   │                           │ e      │ mate │ si │                 │ p-valu │       │
│   │                           │ partic │ /CI  │ fy │                 │ e rule │       │
│   │                           │ ipates │ with │    │                 │        │       │
│   │                           │        │ vary │    │                 │        │       │
│   │                           │        │ ing  │    │                 │        │       │
│   │                           │        │ p-va │    │                 │        │       │
│   │                           │        │ lues │    │                 │        │       │
└───┴───────────────────────────┴────────┴──────┴────┴─────────────────┴────────┴───────┘

M. Secondary conformal branch

┌───┬────────────────────────────┬─────────┬──────┬────────┬──────────┬────────┬────────┐
│ T │ TEST NAME                  │ INVARIA │ MINI │ ACTION │ EXPECTED │ WHAT   │ PRE-EX │
│ E │                            │ NT      │ MAL  │        │ ASSERTIO │ BUG IT │ ECUTIO │
│ S │                            │         │ SYNT │        │ N        │ CATCHE │ N      │
│ T │                            │         │ HETI │        │          │ S      │        │
│ I │                            │         │ C    │        │          │        │        │
│ D │                            │         │ FIXT │        │          │        │        │
│   │                            │         │ URE  │        │          │        │        │
├───┼────────────────────────────┼─────────┼──────┼────────┼──────────┼────────┼────────┤
│ 7 │ test_conformal_split_uses_ │ Proper/ │ Fold │ Build  │ IDs      │ Test   │ Yes    │
│ 9 │ outer_training_only        │ calibra │ ed   │ split  │ subset   │ rows   │        │
│   │                            │ tion    │ grou │        │ of outer │ in     │        │
│   │                            │ rows    │ ped  │        │ training │ confor │        │
│   │                            │ exclude │ fixt │        │          │ mal    │        │
│   │                            │ outer   │ ure  │        │          │ split  │        │
│   │                            │ test    │      │        │          │        │        │
├───┼────────────────────────────┼─────────┼──────┼────────┼──────────┼────────┼────────┤
│ 8 │ test_conformal_split_is_sc │ Scaffol │ Mult │ Build  │ No       │ Group  │ Yes    │
│ 0 │ affold_grouped             │ d is    │ i-ro │ split  │ scaffold │ leakag │        │
│   │                            │ indivis │ w    │        │ appears  │ e      │        │
│   │                            │ ible    │ scaf │        │ in both  │        │        │
│   │                            │         │ fold │        │ proper/c │        │        │
│   │                            │         │ grou │        │ alibrati │        │        │
│   │                            │         │ ps   │        │ on       │        │        │
├───┼────────────────────────────┼─────────┼──────┼────────┼──────────┼────────┼────────┤
│ 8 │ test_conformal_qrf_fits_on │ QRF     │ Spy  │ Run    │ Fit IDs  │ Calibr │ Runner │
│ 1 │ _proper_training_only      │ trainin │ RF   │ confor │ equal    │ ation/ │ -requi │
│   │                            │ g       │ fit  │ mal    │ proper-t │ test   │ red    │
│   │                            │ exclude │ inpu │ branch │ rain IDs │ used   │        │
│   │                            │ s       │ ts   │        │          │ for    │        │
│   │                            │ calibra │      │        │          │ fittin │        │
│   │                            │ tion/te │      │        │          │ g      │        │
│   │                            │ st      │      │        │          │        │        │
├───┼────────────────────────────┼─────────┼──────┼────────┼──────────┼────────┼────────┤
│ 8 │ test_nonconformity_uses_ca │ Scores  │ Outc │ Comput │ Only     │ Wrong  │ Yes    │
│ 2 │ libration_y_only           │ use     │ ome  │ e      │ calibrat │ outcom │        │
│   │                            │ calibra │ sent │ scores │ ion      │ e      │        │
│   │                            │ tion    │ inel │        │ sentinel │ partit │        │
│   │                            │ outcome │ s    │        │ accessed │ ion    │        │
│   │                            │ s       │ for  │        │          │        │        │
│   │                            │         │ prop │        │          │        │        │
│   │                            │         │ er/t │        │          │        │        │
│   │                            │         │ est  │        │          │        │        │
├───┼────────────────────────────┼─────────┼──────┼────────┼──────────┼────────┼────────┤
│ 8 │ test_test_y_used_only_for_ │ Outer-t │ Even │ Run    │ Test-y   │ Test   │ Runner │
│ 3 │ final_coverage             │ est     │ t    │ branch │ access   │ labels │ -requi │
│   │                            │ outcome │ log  │        │ occurs   │ calibr │ red    │
│   │                            │ s enter │ and  │        │ after    │ ate    │        │
│   │                            │ only    │ test │        │ correcti │ interv │        │
│   │                            │ final   │ outc │        │ on/inter │ als    │        │
│   │                            │ evaluat │ ome  │        │ val      │        │        │
│   │                            │ ion     │ sent │        │ freeze   │        │        │
│   │                            │         │ inel │        │          │        │        │
├───┼────────────────────────────┼─────────┼──────┼────────┼──────────┼────────┼────────┤
│ 8 │ test_constant_conformal_co │ CQR     │ Know │ Apply  │ QRF and  │ CQR    │ Yes    │
│ 4 │ rrection_preserves_rank    │ width   │ n    │ correc │ CQR      │ become │        │
│   │                            │ adds    │ QRF  │ tion/r │ order    │ s      │        │
│   │                            │ fold-co │ widt │ ank    │ identica │ altern │        │
│   │                            │ nstant  │ hs   │        │ l        │ ate    │        │
│   │                            │ 2*qhat  │ and  │        │          │ ranker │        │
│   │                            │         │ corr │        │          │        │        │
│   │                            │         │ ecti │        │          │        │        │
│   │                            │         │ on   │        │          │        │        │
├───┼────────────────────────────┼─────────┼──────┼────────┼──────────┼────────┼────────┤
│ 8 │ test_conformal_cannot_repl │ Primary │ Synt │ Run    │ Primary  │ Confor │ Runner │
│ 5 │ ace_primary_rank           │ retenti │ heti │ primar │ masks    │ mal    │ -requi │
│   │                            │ on      │ c    │ y and  │ use QRF  │ promot │ red    │
│   │                            │ source  │ QRF/ │ confor │ width;   │ ed to  │        │
│   │                            │ remains │ CQR  │ mal    │ conforma │ primar │        │
│   │                            │ QRF80   │ orde │ branch │ l is     │ y      │        │
│   │                            │         │ r    │ es     │ calibrat │        │        │
│   │                            │         │ fixt │        │ ion-only │        │        │
│   │                            │         │ ure  │        │          │        │        │
└───┴────────────────────────────┴─────────┴──────┴────────┴──────────┴────────┴────────┘

N. Sensitivity isolation

┌───┬─────────────────────────────┬────────┬──────┬─────┬─────────────┬────────┬────────┐
│ T │ TEST NAME                   │ INVARI │ MINI │ ACT │ EXPECTED    │ WHAT   │ PRE-EX │
│ E │                             │ ANT    │ MAL  │ ION │ ASSERTION   │ BUG IT │ ECUTIO │
│ S │                             │        │ SYNT │     │             │ CATCHE │ N      │
│ T │                             │        │ HETI │     │             │ S      │        │
│ I │                             │        │ C    │     │             │        │        │
│ D │                             │        │ FIXT │     │             │        │        │
│   │                             │        │ URE  │     │             │        │        │
├───┼─────────────────────────────┼────────┼──────┼─────┼─────────────┼────────┼────────┤
│ 8 │ test_primary_freezes_before │ Primar │ Even │ Run │ primary_fre │ Sensit │ Runner │
│ 6 │ _sensitivity                │ y      │ t    │ pip │ eze <       │ ivity  │ -requi │
│   │                             │ artifa │ log  │ eli │ sensitivity │ affect │ red    │
│   │                             │ ct     │ with │ ne  │ _start      │ s      │        │
│   │                             │ exists │ sens │     │             │ primar │        │
│   │                             │ before │ itiv │     │             │ y path │        │
│   │                             │ sensit │ ity  │     │             │        │        │
│   │                             │ ivity  │ hook │     │             │        │        │
│   │                             │ stage  │      │     │             │        │        │
├───┼─────────────────────────────┼────────┼──────┼─────┼─────────────┼────────┼────────┤
│ 8 │ test_n731_cannot_mutate_pri │ N731   │ Fixt │ Run │ Primary     │ Sensit │ Runner │
│ 7 │ mary_predictions            │ uses   │ ure  │ pri │ predictions │ ivity  │ -requi │
│   │                             │ separa │ with │ mar │ /hash       │ refits │ red    │
│   │                             │ te     │ 13   │ y   │ unchanged   │ /mutat │        │
│   │                             │ result │ boun │ the │             │ es     │        │
│   │                             │ namesp │ dary │ n   │             │ primar │        │
│   │                             │ ace    │ rows │ N73 │             │ y      │        │
│   │                             │        │      │ 1   │             │        │        │
├───┼─────────────────────────────┼────────┼──────┼─────┼─────────────┼────────┼────────┤
│ 8 │ test_ge25_cannot_mutate_pri │ Diagno │ Fixt │ Run │ Primary     │ Diagno │ Runner │
│ 8 │ mary_predictions            │ stic   │ ure  │ pri │ artifacts   │ stic   │ -requi │
│   │                             │ subgro │ cros │ mar │ unchanged   │ filter │ red    │
│   │                             │ up is  │ sing │ y   │             │ feeds  │        │
│   │                             │ downst │ 25   │ the │             │ back   │        │
│   │                             │ ream-o │ thre │ n   │             │        │        │
│   │                             │ nly    │ shol │ dia │             │        │        │
│   │                             │        │ d    │ gno │             │        │        │
│   │                             │        │      │ sti │             │        │        │
│   │                             │        │      │ c   │             │        │        │
├───┼─────────────────────────────┼────────┼──────┼─────┼─────────────┼────────┼────────┤
│ 8 │ test_sensitivity_does_not_c │ Primar │ Full │ Run │ Primary     │ Subset │ Runner │
│ 9 │ hange_primary_split_or_mode │ y      │ and  │ bot │ split/model │ -drive │ -requi │
│   │ l                           │ split/ │ sens │ h   │ hashes      │ n      │ red    │
│   │                             │ model  │ itiv │     │ identical   │ primar │        │
│   │                             │ inputs │ ity  │     │             │ y      │        │
│   │                             │ stay   │ subs │     │             │ fold/m │        │
│   │                             │ N744-f │ ets  │     │             │ odel   │        │
│   │                             │ rozen  │      │     │             │        │        │
├───┼─────────────────────────────┼────────┼──────┼─────┼─────────────┼────────┼────────┤
│ 9 │ test_ge25_is_labeled_diagno │ CLint> │ Diag │ Ser │ Explicit    │ Misrep │ Runner │
│ 0 │ stic_only                   │ =25    │ nost │ ial │ diagnostic/ │ resent │ -requi │
│   │                             │ cannot │ ic   │ ize │ outcome-def │ ing    │ red    │
│   │                             │ be     │ outp │ res │ ined label; │ sensit │        │
│   │                             │ deploy │ ut   │ ult │ no triage   │ ivity  │        │
│   │                             │ ment   │ sche │     │ policy      │        │        │
│   │                             │ policy │ ma   │     │ field       │        │        │
└───┴─────────────────────────────┴────────┴──────┴─────┴─────────────┴────────┴────────┘

O. Result serialization and provenance

┌───┬──────────────────────────┬─────────────┬─────────┬─────┬──────────┬───────┬───────┐
│ T │ TEST NAME                │ INVARIANT   │ MINIMAL │ ACT │ EXPECTED │ WHAT  │ PRE-E │
│ E │                          │             │ SYNTHET │ ION │ ASSERTIO │ BUG   │ XECUT │
│ S │                          │             │ IC      │     │ N        │ IT    │ ION   │
│ T │                          │             │ FIXTURE │     │          │ CATCH │       │
│ I │                          │             │         │     │          │ ES    │       │
│ D │                          │             │         │     │          │       │       │
├───┼──────────────────────────┼─────────────┼─────────┼─────┼──────────┼───────┼───────┤
│ 9 │ test_prediction_freeze_s │ Same record │ Fixed   │ Ser │ Bytes/sc │ Nonde │ Runne │
│ 1 │ chema_and_hash_determini │ table gives │ ordered │ ial │ hema/has │ termi │ r-req │
│   │ stic                     │ same        │ records │ ize │ h        │ nisti │ uired │
│   │                          │ schema/hash │         │ twi │ identica │ c     │       │
│   │                          │             │         │ ce  │ l        │ upstr │       │
│   │                          │             │         │     │          │ eam   │       │
│   │                          │             │         │     │          │ artif │       │
│   │                          │             │         │     │          │ act   │       │
├───┼──────────────────────────┼─────────────┼─────────┼─────┼──────────┼───────┼───────┤
│ 9 │ test_outcome_results_sep │ Outcome-der │ Tempora │ Ser │ Distinct │ Mixin │ Runne │
│ 2 │ arate_from_prediction_fr │ ived files  │ ry      │ ial │ paths/ar │ g     │ r-req │
│   │ eeze                     │ are         │ result  │ ize │ tifacts/ │ label │ uired │
│   │                          │ separate    │ tree    │ fre │ hashes   │ s     │       │
│   │                          │             │         │ eze │          │ into  │       │
│   │                          │             │         │ and │          │ upstr │       │
│   │                          │             │         │ met │          │ eam   │       │
│   │                          │             │         │ ric │          │ artif │       │
│   │                          │             │         │ s   │          │ act   │       │
├───┼──────────────────────────┼─────────────┼─────────┼─────┼──────────┼───────┼───────┤
│ 9 │ test_scientific_results_ │ Preflight   │ Existin │ Att │ Write    │ Destr │ Runne │
│ 3 │ cannot_overwrite_preflig │ files       │ g       │ emp │ rejected │ uctio │ r-req │
│   │ ht                       │ immutable   │ manifes │ t   │          │ n of  │ uired │
│   │                          │             │ t/split │ res │          │ froze │       │
│   │                          │             │ /matrix │ ult │          │ n     │       │
│   │                          │             │ files   │ wri │          │ input │       │
│   │                          │             │         │ te  │          │ s     │       │
│   │                          │             │         │ to  │          │       │       │
│   │                          │             │         │ tho │          │       │       │
│   │                          │             │         │ se  │          │       │       │
│   │                          │             │         │ pat │          │       │       │
│   │                          │             │         │ hs  │          │       │       │
├───┼──────────────────────────┼─────────────┼─────────┼─────┼──────────┼───────┼───────┤
│ 9 │ test_result_records_all_ │ Results     │ Synthet │ Ser │ Required │ Untra │ Runne │
│ 4 │ frozen_hashes            │ carry       │ ic      │ ial │ hashes   │ ceabl │ r-req │
│   │                          │ SAP/manifes │ provena │ ize │ present  │ e     │ uired │
│   │                          │ t/commit/en │ nce     │ res │ and      │ scien │       │
│   │                          │ vironment   │ object  │ ult │ match    │ tific │       │
│   │                          │ hashes      │         │     │          │ outpu │       │
│   │                          │             │         │     │          │ t     │       │
├───┼──────────────────────────┼─────────────┼─────────┼─────┼──────────┼───────┼───────┤
│ 9 │ test_partial_run_not_mar │ Incomplete  │ Inject  │ Ins │ No       │ Parti │ Runne │
│ 5 │ ked_complete             │ run cannot  │ fold    │ pec │ COMPLETE │ al    │ r-req │
│   │                          │ seal        │ failure │ t   │ D state  │ resul │ uired │
│   │                          │             │         │ sta │ or final │ t     │       │
│   │                          │             │         │ te/ │ result   │ masqu │       │
│   │                          │             │         │ out │          │ eradi │       │
│   │                          │             │         │ put │          │ ng as │       │
│   │                          │             │         │     │          │ compl │       │
│   │                          │             │         │     │          │ ete   │       │
├───┼──────────────────────────┼─────────────┼─────────┼─────┼──────────┼───────┼───────┤
│ 9 │ test_failed_fold_blocks_ │ Any fold    │ Fail    │ Run │ Final    │ Missi │ Runne │
│ 6 │ final_sealing            │ failure     │ fold 3  │ run │ seal     │ ng    │ r-req │
│   │                          │ aborts      │ of 5    │ ner │ absent;  │ fold  │ uired │
│   │                          │ final seal  │         │     │ abort    │ silen │       │
│   │                          │             │         │     │ recorded │ tly   │       │
│   │                          │             │         │     │          │ omitt │       │
│   │                          │             │         │     │          │ ed    │       │
└───┴──────────────────────────┴─────────────┴─────────┴─────┴──────────┴───────┴───────┘

P. Single-run and sealed execution

┌───┬─────────────────────────┬────────────┬──────┬──────┬────────────┬───────┬─────────┐
│ T │ TEST NAME               │ INVARIANT  │ MINI │ ACTI │ EXPECTED   │ WHAT  │ PRE-EXE │
│ E │                         │            │ MAL  │ ON   │ ASSERTION  │ BUG   │ CUTION  │
│ S │                         │            │ SYNT │      │            │ IT    │         │
│ T │                         │            │ HETI │      │            │ CATCH │         │
│ I │                         │            │ C    │      │            │ ES    │         │
│ D │                         │            │ FIXT │      │            │       │         │
│   │                         │            │ URE  │      │            │       │         │
├───┼─────────────────────────┼────────────┼──────┼──────┼────────────┼───────┼─────────┤
│ 9 │ test_completed_run_gets │ Completed  │ Temp │ Comp │ Run ID     │ Untra │ Runner- │
│ 7 │ _immutable_run_id       │ run has    │ orar │ lete │ exists in  │ ceabl │ require │
│   │                         │ unique     │ y    │ synt │ manifest   │ e     │ d       │
│   │                         │ immutable  │ run  │ heti │ and path   │ execu │         │
│   │                         │ ID         │ dire │ c    │            │ tion  │         │
│   │                         │            │ ctor │ run  │            │       │         │
│   │                         │            │ y    │      │            │       │         │
├───┼─────────────────────────┼────────────┼──────┼──────┼────────────┼───────┼─────────┤
│ 9 │ test_completed_run_cann │ Sealed     │ Exis │ Exec │ Second     │ Silen │ Runner- │
│ 8 │ ot_be_overwritten       │ outputs    │ ting │ ute  │ execution  │ t     │ require │
│   │                         │ are        │ seal │ same │ fails;     │ overw │ d       │
│   │                         │ immutable  │ ed   │ run  │ bytes      │ rite  │         │
│   │                         │            │ run  │ ID   │ unchanged  │       │         │
│   │                         │            │      │ agai │            │       │         │
│   │                         │            │      │ n    │            │       │         │
├───┼─────────────────────────┼────────────┼──────┼──────┼────────────┼───────┼─────────┤
│ 9 │ test_rerun_requires_new │ Reruns use │ Exis │ Requ │ New run ID │ Mutat │ Runner- │
│ 9 │ _provenance_record      │ new        │ ting │ est  │ required;  │ ion   │ require │
│   │                         │ ID/output  │ seal │ reru │ original   │ of    │ d       │
│   │                         │ path       │ ed   │ n    │ untouched  │ first │         │
│   │                         │            │ run  │      │            │ run   │         │
├───┼─────────────────────────┼────────────┼──────┼──────┼────────────┼───────┼─────────┤
│ 1 │ test_execution_ledger_i │ Ledger     │ Synt │ Insp │ Start,     │ Incom │ Runner- │
│ 0 │ s_complete              │ records    │ heti │ ect  │ completion │ plete │ require │
│ 0 │                         │ lifecycle/ │ c    │ ledg │ /abort,    │ audit │ d       │
│   │                         │ provenance │ succ │ er   │ commit,    │ trail │         │
│   │                         │            │ ess  │      │ manifest,  │       │         │
│   │                         │            │ and  │      │ environmen │       │         │
│   │                         │            │ abor │      │ t,         │       │         │
│   │                         │            │ t    │      │ artifact   │       │         │
│   │                         │            │ runs │      │ hashes all │       │         │
│   │                         │            │      │      │ present    │       │         │
└───┴─────────────────────────┴────────────┴──────┴──────┴────────────┴───────┴─────────┘

Q. Negative controls and adversarial leakage tests

These deliberately introduce a leakage-prone implementation and verify that the legitimate runner’s invariants detect or prevent it.

┌───┬────────────────────────────┬───────┬──────────┬──────┬──────────┬─────────┬───────┐
│ T │ TEST NAME                  │ INVAR │ MINIMAL  │ ACTI │ EXPECTED │ WHAT    │ PRE-E │
│ E │                            │ IANT  │ SYNTHETI │ ON   │ ASSERTIO │ BUG IT  │ XECUT │
│ S │                            │       │ C        │      │ N        │ CATCHES │ ION   │
│ T │                            │       │ FIXTURE  │      │          │         │       │
│ I │                            │       │          │      │          │         │       │
│ D │                            │       │          │      │          │         │       │
├───┼────────────────────────────┼───────┼──────────┼──────┼──────────┼─────────┼───────┤
│ Q │ test_test_y_cannot_change_ │ Test  │ Training │ Run  │ Scaler   │ Encodin │ Yes   │
│ 1 │ descriptor_scaling         │ label │ descript │ desc │ paramete │ g test  │       │
│   │                            │ s     │ ors      │ ript │ rs and   │ y into  │       │
│   │                            │ canno │ [[0],[1] │ or   │ distance │ scaling │       │
│   │                            │ t     │ ,[2]];   │ stag │ s        │         │       │
│   │                            │ affec │ test     │ e    │ identica │         │       │
│   │                            │ t     │ descript │ twic │ l; a     │         │       │
│   │                            │ descr │ or [10]; │ e    │ leaking  │         │       │
│   │                            │ iptor │ two      │      │ spy      │         │       │
│   │                            │ dista │ y_test   │      │ fails    │         │       │
│   │                            │ nces  │ vectors, │      │          │         │       │
│   │                            │       │ one      │      │          │         │       │
│   │                            │       │ extreme  │      │          │         │       │
├───┼────────────────────────────┼───────┼──────────┼──────┼──────────┼─────────┼───────┤
│ Q │ test_test_compound_cannot_ │ Refer │ Query is │ Run  │ Score    │ Includi │ Yes   │
│ 2 │ improve_tanimoto           │ ence  │ identica │ Tani │ remains  │ ng test │       │
│   │                            │ set   │ l to a   │ moto │ training │ compoun │       │
│   │                            │ is    │ test     │ stag │ -referen │ ds in   │       │
│   │                            │ outer │ fingerpr │ e    │ ce       │ referen │       │
│   │                            │ train │ int but  │      │ score,   │ ce pool │       │
│   │                            │ ing   │ not to   │      │ not zero │         │       │
│   │                            │ only  │ any      │      │          │         │       │
│   │                            │       │ training │      │          │         │       │
│   │                            │       │ fingerpr │      │          │         │       │
│   │                            │       │ int      │      │          │         │       │
├───┼────────────────────────────┼───────┼──────────┼──────┼──────────┼─────────┼───────┤
│ Q │ test_test_y_cannot_change_ │ Local │ Fixed    │ Run  │ Same     │ Test y  │ Yes   │
│ 3 │ local_sd                   │ heter │ weights/ │ loca │ value    │ used in │       │
│   │                            │ ogene │ training │ l SD │ both     │ local   │       │
│   │                            │ ity   │ labels;  │ stag │ runs;    │ heterog │       │
│   │                            │ uses  │ test     │ e    │ implemen │ eneity  │       │
│   │                            │ y_tra │ labels   │      │ tation   │         │       │
│   │                            │ in    │ [0,0] vs │      │ using    │         │       │
│   │                            │ only  │ [1000,10 │      │ test     │         │       │
│   │                            │       │ 00]      │      │ labels   │         │       │
│   │                            │       │          │      │ changes  │         │       │
│   │                            │       │          │      │ and      │         │       │
│   │                            │       │          │      │ fails    │         │       │
├───┼────────────────────────────┼───────┼──────────┼──────┼──────────┼─────────┼───────┤
│ Q │ test_test_y_cannot_change_ │ QRF   │ Fixed    │ Comp │ Q10/Q90/ │ Test    │ Yes   │
│ 4 │ qrf_width                  │ quant │ RF/weigh │ ute  │ width    │ outcome │       │
│   │                            │ iles  │ ts/train │ widt │ identica │ s used  │       │
│   │                            │ use   │ ing      │ hs   │ l        │ in QRF  │       │
│   │                            │ train │ labels;  │ twic │          │ uncerta │       │
│   │                            │ ing   │ two      │ e    │          │ inty    │       │
│   │                            │ outco │ test-lab │      │          │         │       │
│   │                            │ mes   │ el       │      │          │         │       │
│   │                            │ only  │ vectors  │      │          │         │       │
├───┼────────────────────────────┼───────┼──────────┼──────┼──────────┼─────────┼───────┤
│ Q │ test_test_y_cannot_change_ │ Reten │ Two      │ Buil │ Retained │ Error-g │ Yes   │
│ 5 │ retained_ids               │ tion  │ folds    │ d    │ IDs      │ uided   │       │
│   │                            │ uses  │ with     │ mask │ identica │ retenti │       │
│   │                            │ uncer │ tied/une │ s    │ l        │ on or   │       │
│   │                            │ taint │ qual     │ twic │          │ global  │       │
│   │                            │ y,    │ uncertai │ e    │          │ pooling │       │
│   │                            │ IDs,  │ nty      │      │          │         │       │
│   │                            │ fold, │ values;  │      │          │         │       │
│   │                            │ kappa │ two      │      │          │         │       │
│   │                            │ only  │ outcome  │      │          │         │       │
│   │                            │       │ arrays   │      │          │         │       │
├───┼────────────────────────────┼───────┼──────────┼──────┼──────────┼─────────┼───────┤
│ Q │ test_test_y_cannot_change_ │ Boots │ Scaffold │ Gene │ Draw     │ Outcome │ Yes   │
│ 6 │ bootstrap_draws            │ trap  │ /fold    │ rate │ sequence │ -depend │       │
│   │                            │ selec │ table    │ draw │ identica │ ent     │       │
│   │                            │ tion  │ plus two │ s    │ l        │ bootstr │       │
│   │                            │ is    │ outcome  │ twic │          │ ap      │       │
│   │                            │ outco │ arrays   │ e    │          │ samplin │       │
│   │                            │ me-bl │          │      │          │ g       │       │
│   │                            │ ind   │          │      │          │         │       │
└───┴────────────────────────────┴───────┴──────────┴──────┴──────────┴─────────┴───────┘

MUST-PASS BEFORE GATE 11 CAN CLOSE

The following categories must pass before Gate 11 can be considered closed:

1. Artifact and authorization gates: tests 1–7.
2. Fold integrity and OOF provenance: tests 8–13.
3. All pre-freeze outcome-blindness tests: tests 14–29.
4. Training-only reference boundaries: tests 30–36.
5. Prediction-freeze lifecycle: tests 37–41.
6. Within-fold retention: tests 42–47.
7. Random-deferral invariants: tests 48–52.
8. Outcome-stage ordering and nonfeedback: tests 53–58.
9. Primary estimand and coverage correctness: tests 59–67.
10. Scaffold bootstrap correctness: tests 68–74.
11. Three-state interpretation: tests 75–78.
12. Conformal isolation: tests 79–85.
13. Sensitivity nonmutation: tests 86–90.
14. Serialization, partial-run, and sealing behavior: tests 91–100.
15. At least three negative controls, including Q1–Q3; all Q tests are recommended.

A passing preflight-only suite is insufficient for Gate 11 unless the future runner exposes and enforces the prediction/uncertainty freeze boundary.

NICE-TO-HAVE HARDENING

• Property-based tests over random fold sizes, scaffold multiplicities, and coverage values.
• Mutation tests that deliberately replace  ceil  with  floor , remove scaffold grouping, or pool uncertainty globally.
• File-permission/read-only tests for sealed artifacts.
• Crash-recovery tests at every fold boundary.
• Cross-process locking tests for duplicate run IDs.
• Independent implementation of SHA-256 assignment and retention vectors.
• Schema-version migration tests.
• Deterministic serialization tests across Windows and Linux line endings.
• Memory/resource tests for 500-tree forests on the target hardware.
• Explicit tests that no v2 module is imported by the v3A runner.
• Tests that all scientific-result paths remain separate from  splits/ ,  manifests/ , and  state/  preflight paths.

REDUNDANT WITH EXISTING 119 PREFLIGHT TESTS

The current 119-test preflight suite already substantially covers:

• frozen ECFP4 representation and matrix shape/binary constraints;
• known scaffold SHA-256 tie vector;
• all-ID coverage and no duplicate IDs;
• scaffold leakage;
• input-row-order invariance;
• outcome-column invariance for fold construction;
• adversarial greedy scaffold allocation;
• frozen RF parameter constants;
• bootstrap QRF prediction reconstruction and weight-sum invariants;
• bootstrap-disabled rejection;
•  max_samples != None  rejection;
• unfitted RF rejection;
• weighted-fit/unattested-fit rejection;
• duplicate and zero-weight weighted quantiles;
• QRF width equals weighted Q90−Q10;
• within-fold retention counts;
• all six frozen coverage levels;
• activity-ID tie-break known vector;
• random-retention determinism and per-fold counts;
• scaffold bootstrap grouping/stratification/determinism;
• conformal group splitting;
• invalid calibration fractions;
• negative conformal correction rejection;
• artifact hash substitution, empty hash, missing-artifact, and tamper rejection;
• current pre-execution state and fail-closed execution guard.

The acceptance tests above should extend—not duplicate—the 119 tests by testing orchestration order, immutable freeze artifacts, outcome-access sentinels, nonmutation, result sealing, and single-run lifecycle behavior.

REQUIRES FUTURE RUNNER TO EXIST

The following cannot be fully tested against the current primitives alone:

• 11–13: complete per-fold model orchestration and OOF provenance;
• 37–41: prediction/uncertainty freeze lifecycle and immutable artifact;
• 47: retention-before-evaluation ordering;
• 53–58: stateful outcome-dependent evaluation boundary;
• 60–62: end-to-end primary estimand orchestration and role enforcement;
• 63–66: persisted complete coverage curve;
• 81, 83, 85: conformal model/evaluation orchestration;
• 86–90: sensitivity sequencing and nonmutation;
• 91–100: scientific result serialization, partial-run handling, sealing, run IDs, and execution ledger;
• Q5 if it must observe runner-level rather than primitive-level retention behavior.

No test in this specification requires real  CHEMBL3301370  outcomes or scientific v3A execution. The future runner must first pass the synthetic acceptance suite, then remain blocked by the existing execution-state/audit controls until the separately authorized scientific phase.

V3A_GATE11_ACCEPTANCE_TEST_SPEC_DESIGNED_NO_EDITS
```
