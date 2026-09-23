# TDC hepatocyte species audit

```json
{
  "INFERRED": {
    "claim_status": "REPRODUCED",
    "decision_rule": "REPRODUCED requires both rat-only and human-only structure matches with exactly matching numeric source labels. PARTIALLY_REPRODUCED requires label-specific matches to both species without both exclusive structural witnesses; otherwise NOT_REPRODUCED. Censored matches identify numeric boundaries only.",
    "strict_duplicate_pair_rule": "Exactly two TDC rows with different numeric labels: one has exactly one strict structure/value-matching rat record and no human value match; the other has exactly one strict structure/value-matching human record and no rat value match. Numeric agreement uses exact Decimal equality."
  },
  "OBSERVED": {
    "duplicate_label_groups": {
      "different": 193
    },
    "duplicate_trace_groups": {
      "distinct_labels_match_rat_and_human": 187,
      "no_strict_structural_match_to_either_assay": 6
    },
    "numeric_label_match_row_counts": {
      "both": 31,
      "human_only": 370,
      "rat_only": 796,
      "unresolved": 16
    },
    "row_counts": {
      "ambiguous_unparseable": 0,
      "both": 405,
      "human_only": 183,
      "neither": 16,
      "rat_only": 609
    },
    "secondary_id_duplicate_trace_groups": {
      "distinct_labels_match_rat_and_human": 190,
      "partial_or_unresolved": 3
    },
    "secondary_id_numeric_label_match_row_counts": {
      "both": 31,
      "human_only": 373,
      "rat_only": 801,
      "unresolved": 8
    },
    "unique_valid_structure_counts": {
      "ambiguous_unparseable": 0,
      "both": 218,
      "human_only": 183,
      "neither": 10,
      "rat_only": 609
    }
  },
  "UNRESOLVED": "Historical lineage cannot be proven by equality alone. A shared structure/label can map to both species; retain ambiguity. Species uses ChEMBL assay organism/taxonomy, never target magnitude. Secondary exact molecule-ID plus numeric-value matching is explicitly separate and never upgrades the strict structural matches."
}
```

INFERRED: Identity rule: RDKit 2025.03.6 sanitized isomeric canonical SMILES; stereochemistry, isotopes, charge and all disconnected fragments retained. No parent selection, desalting, neutralization, tautomer normalization or stereo removal. RDKit ordinary explicit-H handling applies. Equality is string equality of valid keys; missing/invalid structures never match. Identity is representation-specific, not proof of sample identity.

OBSERVED: Row evidence is in `../data/interim/TDC_HEPATOCYTE_SPECIES_ROWS.csv`; repeated-structure evidence is in `../data/interim/TDC_HEPATOCYTE_DUPLICATE_LABELS.json`. Numeric matching retains source censor relations and does not assign species from label magnitude.
