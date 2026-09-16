# Biogen HLM audit

```json
{
  "INFERRED": "Repeated exact values at distribution boundaries are pile-ups consistent with reporting/assay limits; they alone do not prove censoring. Undefined stereochemistry means RDKit-detectable potential stereo elements without specified configuration, not demonstrated sample composition.",
  "OBSERVED": {
    "exact_hlm_column": "LOG HLM_CLint (mL/min/kg)",
    "missing_hlm_n": 434,
    "non_null_hlm_n": 3087,
    "structure_and_target_audit": {
      "chemical_space": {
        "clogp": {
          "exactly_150": 0,
          "exactly_3": 0,
          "inequality_strings": 0,
          "iqr": 1.4794000000000023,
          "mad": 0.7388000000000008,
          "max": 9.0141,
          "median": 2.782800000000001,
          "min": -1.9800000000000006,
          "missing_rows": 0,
          "numeric_rows": 3521,
          "q05": 0.9781399999999999,
          "q25": 2.0532,
          "q75": 3.532600000000002,
          "q95": 4.7748000000000035,
          "top_value_frequencies": [
            {
              "count": 3,
              "value": "2.127"
            },
            {
              "count": 3,
              "value": "2.34412"
            },
            {
              "count": 3,
              "value": "4.068500000000003"
            },
            {
              "count": 2,
              "value": "0.0427199999999997"
            },
            {
              "count": 2,
              "value": "0.1988999999999993"
            },
            {
              "count": 2,
              "value": "0.91212"
            },
            {
              "count": 2,
              "value": "1.0446999999999993"
            },
            {
              "count": 2,
              "value": "1.4462"
            },
            {
              "count": 2,
              "value": "1.61432"
            },
            {
              "count": 2,
              "value": "1.6822"
            }
          ],
          "total_rows": 3521,
          "unparseable_rows": 0
        },
        "fraction_csp3": {
          "exactly_150": 0,
          "exactly_3": 0,
          "inequality_strings": 0,
          "iqr": 0.26666666666666666,
          "mad": 0.1333333333333333,
          "max": 1.0,
          "median": 0.3333333333333333,
          "min": 0.0,
          "missing_rows": 0,
          "numeric_rows": 3521,
          "q05": 0.0625,
          "q25": 0.2,
          "q75": 0.4666666666666667,
          "q95": 0.7,
          "top_value_frequencies": [
            {
              "count": 145,
              "value": "0.5"
            },
            {
              "count": 132,
              "value": "0.3333333333333333"
            },
            {
              "count": 97,
              "value": "0.25"
            },
            {
              "count": 84,
              "value": "0.0"
            },
            {
              "count": 75,
              "value": "0.2"
            },
            {
              "count": 75,
              "value": "0.4"
            },
            {
              "count": 68,
              "value": "0.2857142857142857"
            },
            {
              "count": 65,
              "value": "0.42857142857142855"
            },
            {
              "count": 57,
              "value": "0.2727272727272727"
            },
            {
              "count": 54,
              "value": "0.3"
            }
          ],
          "total_rows": 3521,
          "unparseable_rows": 0
        },
        "hba": {
          "exactly_150": 0,
          "exactly_3": 688,
          "inequality_strings": 0,
          "iqr": 2.0,
          "mad": 1.0,
          "max": 16.0,
          "median": 4.0,
          "min": 1.0,
          "missing_rows": 0,
          "numeric_rows": 3521,
          "q05": 2.0,
          "q25": 3.0,
          "q75": 5.0,
          "q95": 7.0,
          "top_value_frequencies": [
            {
              "count": 982,
              "value": "4"
            },
            {
              "count": 756,
              "value": "5"
            },
            {
              "count": 688,
              "value": "3"
            },
            {
              "count": 443,
              "value": "6"
            },
            {
              "count": 260,
              "value": "2"
            },
            {
              "count": 240,
              "value": "7"
            },
            {
              "count": 88,
              "value": "8"
            },
            {
              "count": 31,
              "value": "9"
            },
            {
              "count": 19,
              "value": "10"
            },
            {
              "count": 6,
              "value": "1"
            }
          ],
          "total_rows": 3521,
          "unparseable_rows": 0
        },
        "hbd": {
          "exactly_150": 0,
          "exactly_3": 133,
          "inequality_strings": 0,
          "iqr": 0.0,
          "mad": 0.0,
          "max": 8.0,
          "median": 1.0,
          "min": 0.0,
          "missing_rows": 0,
          "numeric_rows": 3521,
          "q05": 0.0,
          "q25": 1.0,
          "q75": 1.0,
          "q95": 3.0,
          "top_value_frequencies": [
            {
              "count": 2014,
              "value": "1"
            },
            {
              "count": 848,
              "value": "0"
            },
            {
              "count": 482,
              "value": "2"
            },
            {
              "count": 133,
              "value": "3"
            },
            {
              "count": 31,
              "value": "4"
            },
            {
              "count": 9,
              "value": "5"
            },
            {
              "count": 2,
              "value": "6"
            },
            {
              "count": 1,
              "value": "7"
            },
            {
              "count": 1,
              "value": "8"
            }
          ],
          "total_rows": 3521,
          "unparseable_rows": 0
        },
        "molecular_weight": {
          "exactly_150": 0,
          "exactly_3": 0,
          "inequality_strings": 0,
          "iqr": 96.16900000000015,
          "mad": 47.580999999999904,
          "max": 1097.3979999999992,
          "median": 313.79200000000014,
          "min": 150.145,
          "missing_rows": 0,
          "numeric_rows": 3521,
          "q05": 219.28799999999998,
          "q25": 268.32,
          "q75": 364.48900000000015,
          "q95": 461.94900000000024,
          "top_value_frequencies": [
            {
              "count": 6,
              "value": "258.32099999999997"
            },
            {
              "count": 5,
              "value": "202.213"
            },
            {
              "count": 5,
              "value": "203.245"
            },
            {
              "count": 5,
              "value": "259.30899999999997"
            },
            {
              "count": 5,
              "value": "262.353"
            },
            {
              "count": 4,
              "value": "214.268"
            },
            {
              "count": 4,
              "value": "228.295"
            },
            {
              "count": 4,
              "value": "257.33699999999993"
            },
            {
              "count": 4,
              "value": "287.36299999999994"
            },
            {
              "count": 4,
              "value": "296.33000000000004"
            }
          ],
          "total_rows": 3521,
          "unparseable_rows": 0
        },
        "rotatable_bonds": {
          "exactly_150": 0,
          "exactly_3": 796,
          "inequality_strings": 0,
          "iqr": 2.0,
          "mad": 1.0,
          "max": 35.0,
          "median": 4.0,
          "min": 0.0,
          "missing_rows": 0,
          "numeric_rows": 3521,
          "q05": 2.0,
          "q25": 3.0,
          "q75": 5.0,
          "q95": 7.0,
          "top_value_frequencies": [
            {
              "count": 1021,
              "value": "4"
            },
            {
              "count": 796,
              "value": "3"
            },
            {
              "count": 464,
              "value": "2"
            },
            {
              "count": 458,
              "value": "5"
            },
            {
              "count": 312,
              "value": "6"
            },
            {
              "count": 164,
              "value": "7"
            },
            {
              "count": 122,
              "value": "1"
            },
            {
              "count": 79,
              "value": "8"
            },
            {
              "count": 42,
              "value": "9"
            },
            {
              "count": 30,
              "value": "0"
            }
          ],
          "total_rows": 3521,
          "unparseable_rows": 0
        },
        "tpsa": {
          "exactly_150": 0,
          "exactly_3": 0,
          "inequality_strings": 0,
          "iqr": 25.109999999999992,
          "mad": 12.32,
          "max": 258.5199999999999,
          "median": 60.15,
          "min": 3.24,
          "missing_rows": 0,
          "numeric_rows": 3521,
          "q05": 38.33,
          "q25": 49.330000000000005,
          "q75": 74.44,
          "q95": 103.78000000000002,
          "top_value_frequencies": [
            {
              "count": 67,
              "value": "41.99"
            },
            {
              "count": 35,
              "value": "45.230000000000004"
            },
            {
              "count": 34,
              "value": "46.92"
            },
            {
              "count": 34,
              "value": "59.81"
            },
            {
              "count": 28,
              "value": "49.410000000000004"
            },
            {
              "count": 26,
              "value": "40.620000000000005"
            },
            {
              "count": 25,
              "value": "54.88"
            },
            {
              "count": 23,
              "value": "58.120000000000005"
            },
            {
              "count": 22,
              "value": "50.7"
            },
            {
              "count": 22,
              "value": "51.22"
            }
          ],
          "total_rows": 3521,
          "unparseable_rows": 0
        }
      },
      "dummy_atom_rows": 0,
      "duplicated_structure_groups": 0,
      "excess_duplicate_rows": 0,
      "invalid_structure_rows": 0,
      "missing_identifiers": 0,
      "missing_structure_rows": 0,
      "molecules_with_undefined_stereo": 223,
      "multicomponent_rows": 4,
      "row_count": 3521,
      "rows_in_duplicate_groups": 0,
      "target_distribution": {
        "exactly_150": 0,
        "exactly_3": 0,
        "inequality_strings": 0,
        "iqr": 1.1274287875,
        "mad": 0.529625944,
        "max": 3.372714293,
        "median": 1.205312653,
        "min": 0.675686709,
        "missing_rows": 434,
        "numeric_rows": 3087,
        "q05": 0.675686709,
        "q25": 0.675686709,
        "q75": 1.8031154965,
        "q95": 2.4395045188999993,
        "top_value_frequencies": [
          {
            "count": 958,
            "value": "0.675686709"
          },
          {
            "count": 6,
            "value": "0.881384657"
          },
          {
            "count": 2,
            "value": "0.80140371"
          },
          {
            "count": 2,
            "value": "0.82445127"
          },
          {
            "count": 2,
            "value": "0.837651558"
          },
          {
            "count": 2,
            "value": "0.845903839"
          },
          {
            "count": 2,
            "value": "0.870462432"
          },
          {
            "count": 2,
            "value": "0.880813592"
          },
          {
            "count": 2,
            "value": "1.005952287"
          },
          {
            "count": 2,
            "value": "1.006893708"
          }
        ],
        "total_rows": 3521,
        "unparseable_rows": 0
      },
      "unique_identifiers": 3521,
      "unique_raw_smiles": 3521,
      "unique_valid_structures": 3521,
      "valid_structure_rows": 3521
    },
    "total_rows": 3521,
    "unique_internal_ids": 3521,
    "upstream_readme": "data/raw/biogen/README.md explicitly describes experimental log(properties)."
  },
  "UNRESOLVED": "CSV supplies no per-row HLM censor relation. Log base and derivation of bodyweight-normalized source labels are not established by the downloaded CSV/README. No log/inverse-log, scaling or numerical comparison with AstraZeneca has been performed."
}
```
