# Frozen-source data audit

OBSERVED: Acquisition and forensic characterisation only. No modelling or scientific preprocessing was executed.

## Counts

| Source | Rows | Unique IDs | Unique raw SMILES | Unique RDKit structures | Missing / invalid | Duplicate groups / excess rows |
|---|---:|---:|---:|---:|---:|---:|
| OBSERVED: CHEMBL3301370 | 1102 | 1102 | 1102 | 1102 | 0 / 0 | 0 / 0 |
| OBSERVED: CHEMBL3301371 | 837 | 837 | 837 | 837 | 0 / 0 | 0 / 0 |
| OBSERVED: CHEMBL3301372 | 408 | 408 | 408 | 408 | 0 / 0 | 0 / 0 |
| OBSERVED: Clearance_Microsome_AZ | 1102 | 1102 | 1102 | 1102 | 0 / 0 | 0 / 0 |
| OBSERVED: Clearance_Hepatocyte_AZ | 1213 | 1020 | 1020 | 1020 | 0 / 0 | 193 / 193 |
| OBSERVED: Biogen | 3521 | 3521 | 3521 | 3521 | 0 / 0 | 0 / 0 |

EXPECTED_FROM_MEMO: Task-supplied expected assay counts are 1102 (3301370), 837 (3301371), 408 (3301372). The memo freezes selection but contains no numeric counts.

## ChEMBL relations

| Assay | < | > | = | Anything else |
|---|---:|---:|---:|---:|
| OBSERVED: CHEMBL3301370 | 274 | 84 | 0 | 744 |
| OBSERVED: CHEMBL3301371 | 115 | 127 | 0 | 595 |
| OBSERVED: CHEMBL3301372 | 104 | 15 | 0 | 289 |

OBSERVED: CHEMBL3301370 censored/other reported boundaries: `{"<": [{"count": 274, "reported_value": "3.0"}], ">": [{"count": 84, "reported_value": "150.0"}], "UNKNOWN": [{"count": 10, "reported_value": "10.0"}, {"count": 1, "reported_value": "10.23"}, {"count": 1, "reported_value": "10.47"}, {"count": 2, "reported_value": "10.5"}, {"count": 1, "reported_value": "10.67"}, {"count": 1, "reported_value": "10.72"}, {"count": 2, "reported_value": "10.96"}, {"count": 1, "reported_value": "100.0"}, {"count": 1, "reported_value": "101.0"}, {"count": 1, "reported_value": "102.0"}, {"count": 2, "reported_value": "103.0"}, {"count": 2, "reported_value": "104.0"}, {"count": 1, "reported_value": "104.5"}, {"count": 4, "reported_value": "104.71"}, {"count": 1, "reported_value": "105.0"}, {"count": 1, "reported_value": "107.0"}, {"count": 1, "reported_value": "107.15"}, {"count": 17, "reported_value": "11.0"}, {"count": 5, "reported_value": "11.22"}, {"count": 3, "reported_value": "11.48"}, {"count": 1, "reported_value": "11.75"}, {"count": 1, "reported_value": "111.0"}, {"count": 2, "reported_value": "112.0"}, {"count": 4, "reported_value": "112.2"}, {"count": 2, "reported_value": "114.82"}, {"count": 2, "reported_value": "116.0"}, {"count": 2, "reported_value": "117.49"}, {"count": 1, "reported_value": "119.0"}, {"count": 13, "reported_value": "12.0"}, {"count": 1, "reported_value": "12.02"}, {"count": 2, "reported_value": "12.3"}, {"count": 1, "reported_value": "12.5"}, {"count": 2, "reported_value": "12.59"}, {"count": 1, "reported_value": "12.88"}, {"count": 2, "reported_value": "120.0"}, {"count": 1, "reported_value": "120.23"}, {"count": 2, "reported_value": "123.03"}, {"count": 1, "reported_value": "124.0"}, {"count": 2, "reported_value": "125.89"}, {"count": 1, "reported_value": "126.0"}, {"count": 1, "reported_value": "127.0"}, {"count": 1, "reported_value": "127.7"}, {"count": 1, "reported_value": "128.82"}, {"count": 1, "reported_value": "129.0"}, {"count": 10, "reported_value": "13.0"}, {"count": 2, "reported_value": "13.49"}, {"count": 2, "reported_value": "13.5"}, {"count": 3, "reported_value": "13.8"}, {"count": 2, "reported_value": "131.83"}, {"count": 1, "reported_value": "134.0"}, {"count": 1, "reported_value": "137.0"}, {"count": 2, "reported_value": "138.04"}, {"count": 12, "reported_value": "14.0"}, {"count": 4, "reported_value": "14.13"}, {"count": 4, "reported_value": "14.45"}, {"count": 2, "reported_value": "14.79"}, {"count": 1, "reported_value": "140.0"}, {"count": 1, "reported_value": "141.0"}, {"count": 1, "reported_value": "144.54"}, {"count": 1, "reported_value": "145.0"}, {"count": 2, "reported_value": "146.0"}, {"count": 8, "reported_value": "15.0"}, {"count": 3, "reported_value": "15.14"}, {"count": 1, "reported_value": "15.49"}, {"count": 1, "reported_value": "15.67"}, {"count": 3, "reported_value": "15.85"}, {"count": 7, "reported_value": "16.0"}, {"count": 1, "reported_value": "16.6"}, {"count": 4, "reported_value": "17.0"}, {"count": 1, "reported_value": "17.03"}, {"count": 1, "reported_value": "17.25"}, {"count": 1, "reported_value": "17.33"}, {"count": 2, "reported_value": "17.38"}, {"count": 2, "reported_value": "17.5"}, {"count": 6, "reported_value": "17.78"}, {"count": 5, "reported_value": "18.0"}, {"count": 1, "reported_value": "18.2"}, {"count": 1, "reported_value": "18.33"}, {"count": 1, "reported_value": "18.5"}, {"count": 1, "reported_value": "18.62"}, {"count": 5, "reported_value": "19.0"}, {"count": 1, "reported_value": "19.05"}, {"count": 1, "reported_value": "19.25"}, {"count": 2, "reported_value": "19.5"}, {"count": 3, "reported_value": "19.95"}, {"count": 5, "reported_value": "20.0"}, {"count": 5, "reported_value": "20.42"}, {"count": 1, "reported_value": "20.5"}, {"count": 1, "reported_value": "20.89"}, {"count": 8, "reported_value": "21.0"}, {"count": 5, "reported_value": "21.38"}, {"count": 1, "reported_value": "21.5"}, {"count": 2, "reported_value": "21.88"}, {"count": 5, "reported_value": "22.0"}, {"count": 3, "reported_value": "23.0"}, {"count": 1, "reported_value": "23.44"}, {"count": 3, "reported_value": "23.5"}, {"count": 1, "reported_value": "23.6"}, {"count": 4, "reported_value": "24.0"}, {"count": 4, "reported_value": "24.55"}, {"count": 5, "reported_value": "25.0"}, {"count": 2, "reported_value": "25.12"}, {"count": 4, "reported_value": "26.0"}, {"count": 2, "reported_value": "26.33"}, {"count": 7, "reported_value": "27.0"}, {"count": 2, "reported_value": "27.5"}, {"count": 4, "reported_value": "27.54"}, {"count": 5, "reported_value": "28.0"}, {"count": 1, "reported_value": "28.18"}, {"count": 1, "reported_value": "28.67"}, {"count": 2, "reported_value": "29.0"}, {"count": 2, "reported_value": "29.51"}, {"count": 13, "reported_value": "3.0"}, {"count": 1, "reported_value": "3.02"}, {"count": 1, "reported_value": "3.31"}, {"count": 1, "reported_value": "3.6"}, {"count": 1, "reported_value": "3.9"}, {"count": 2, "reported_value": "3.98"}, {"count": 4, "reported_value": "30.0"}, {"count": 1, "reported_value": "30.13"}, {"count": 2, "reported_value": "30.2"}, {"count": 1, "reported_value": "30.33"}, {"count": 3, "reported_value": "30.5"}, {"count": 2, "reported_value": "30.9"}, {"count": 4, "reported_value": "31.0"}, {"count": 1, "reported_value": "31.62"}, {"count": 1, "reported_value": "32.0"}, {"count": 2, "reported_value": "32.36"}, {"count": 7, "reported_value": "33.0"}, {"count": 2, "reported_value": "33.11"}, {"count": 2, "reported_value": "33.88"}, {"count": 2, "reported_value": "34.0"}, {"count": 3, "reported_value": "34.67"}, {"count": 11, "reported_value": "35.0"}, {"count": 1, "reported_value": "35.48"}, {"count": 4, "reported_value": "36.0"}, {"count": 1, "reported_value": "36.31"}, {"count": 3, "reported_value": "37.0"}, {"count": 2, "reported_value": "37.15"}, {"count": 4, "reported_value": "38.0"}, {"count": 1, "reported_value": "38.02"}, {"count": 2, "reported_value": "38.9"}, {"count": 1, "reported_value": "39.0"}, {"count": 1, "reported_value": "39.25"}, {"count": 1, "reported_value": "39.81"}, {"count": 1, "reported_value": "39.83"}, {"count": 22, "reported_value": "4.0"}, {"count": 1, "reported_value": "4.07"}, {"count": 3, "reported_value": "4.17"}, {"count": 1, "reported_value": "4.2"}, {"count": 1, "reported_value": "4.47"}, {"count": 1, "reported_value": "4.57"}, {"count": 1, "reported_value": "4.7"}, {"count": 1, "reported_value": "4.79"}, {"count": 1, "reported_value": "4.9"}, {"count": 1, "reported_value": "40.0"}, {"count": 1, "reported_value": "40.4"}, {"count": 1, "reported_value": "40.5"}, {"count": 1, "reported_value": "40.74"}, {"count": 5, "reported_value": "41.0"}, {"count": 2, "reported_value": "41.69"}, {"count": 5, "reported_value": "42.0"}, {"count": 2, "reported_value": "42.66"}, {"count": 2, "reported_value": "43.0"}, {"count": 1, "reported_value": "43.5"}, {"count": 2, "reported_value": "43.65"}, {"count": 2, "reported_value": "44.0"}, {"count": 1, "reported_value": "44.67"}, {"count": 4, "reported_value": "45.0"}, {"count": 1, "reported_value": "45.71"}, {"count": 2, "reported_value": "46.0"}, {"count": 2, "reported_value": "46.77"}, {"count": 1, "reported_value": "47.0"}, {"count": 2, "reported_value": "48.0"}, {"count": 1, "reported_value": "48.67"}, {"count": 2, "reported_value": "48.98"}, {"count": 2, "reported_value": "49.0"}, {"count": 22, "reported_value": "5.0"}, {"count": 2, "reported_value": "5.13"}, {"count": 3, "reported_value": "5.25"}, {"count": 2, "reported_value": "5.37"}, {"count": 5, "reported_value": "5.5"}, {"count": 1, "reported_value": "5.6"}, {"count": 3, "reported_value": "5.75"}, {"count": 2, "reported_value": "50.0"}, {"count": 2, "reported_value": "50.12"}, {"count": 1, "reported_value": "50.5"}, {"count": 1, "reported_value": "51.0"}, {"count": 3, "reported_value": "51.29"}, {"count": 1, "reported_value": "52.48"}, {"count": 2, "reported_value": "53.0"}, {"count": 1, "reported_value": "53.7"}, {"count": 1, "reported_value": "54.0"}, {"count": 1, "reported_value": "54.5"}, {"count": 2, "reported_value": "54.95"}, {"count": 4, "reported_value": "56.0"}, {"count": 2, "reported_value": "56.23"}, {"count": 1, "reported_value": "57.54"}, {"count": 2, "reported_value": "58.0"}, {"count": 1, "reported_value": "58.5"}, {"count": 3, "reported_value": "59.0"}, {"count": 23, "reported_value": "6.0"}, {"count": 1, "reported_value": "6.03"}, {"count": 2, "reported_value": "6.17"}, {"count": 1, "reported_value": "6.18"}, {"count": 4, "reported_value": "6.31"}, {"count": 1, "reported_value": "6.33"}, {"count": 1, "reported_value": "6.46"}, {"count": 1, "reported_value": "6.5"}, {"count": 1, "reported_value": "6.61"}, {"count": 1, "reported_value": "6.67"}, {"count": 1, "reported_value": "6.76"}, {"count": 3, "reported_value": "6.92"}, {"count": 2, "reported_value": "60.0"}, {"count": 3, "reported_value": "60.26"}, {"count": 1, "reported_value": "61.0"}, {"count": 1, "reported_value": "61.66"}, {"count": 3, "reported_value": "62.0"}, {"count": 2, "reported_value": "63.0"}, {"count": 1, "reported_value": "63.1"}, {"count": 2, "reported_value": "64.0"}, {"count": 1, "reported_value": "64.57"}, {"count": 7, "reported_value": "66.0"}, {"count": 3, "reported_value": "66.07"}, {"count": 1, "reported_value": "66.5"}, {"count": 2, "reported_value": "67.61"}, {"count": 2, "reported_value": "68.0"}, {"count": 1, "reported_value": "69.0"}, {"count": 19, "reported_value": "7.0"}, {"count": 1, "reported_value": "7.08"}, {"count": 1, "reported_value": "7.24"}, {"count": 3, "reported_value": "7.41"}, {"count": 3, "reported_value": "7.5"}, {"count": 2, "reported_value": "7.59"}, {"count": 2, "reported_value": "7.76"}, {"count": 2, "reported_value": "7.94"}, {"count": 1, "reported_value": "70.0"}, {"count": 2, "reported_value": "70.79"}, {"count": 1, "reported_value": "71.0"}, {"count": 1, "reported_value": "71.25"}, {"count": 3, "reported_value": "72.0"}, {"count": 1, "reported_value": "73.0"}, {"count": 2, "reported_value": "74.0"}, {"count": 4, "reported_value": "75.0"}, {"count": 1, "reported_value": "75.86"}, {"count": 1, "reported_value": "76.0"}, {"count": 1, "reported_value": "77.62"}, {"count": 2, "reported_value": "79.0"}, {"count": 2, "reported_value": "79.43"}, {"count": 1, "reported_value": "79.5"}, {"count": 13, "reported_value": "8.0"}, {"count": 1, "reported_value": "8.13"}, {"count": 1, "reported_value": "8.28"}, {"count": 2, "reported_value": "8.32"}, {"count": 1, "reported_value": "8.33"}, {"count": 3, "reported_value": "8.5"}, {"count": 1, "reported_value": "8.51"}, {"count": 1, "reported_value": "8.67"}, {"count": 2, "reported_value": "8.71"}, {"count": 1, "reported_value": "8.86"}, {"count": 2, "reported_value": "8.91"}, {"count": 1, "reported_value": "81.0"}, {"count": 2, "reported_value": "82.0"}, {"count": 1, "reported_value": "83.0"}, {"count": 1, "reported_value": "83.18"}, {"count": 1, "reported_value": "83.83"}, {"count": 2, "reported_value": "85.0"}, {"count": 1, "reported_value": "85.11"}, {"count": 2, "reported_value": "86.0"}, {"count": 2, "reported_value": "87.1"}, {"count": 1, "reported_value": "88.0"}, {"count": 1, "reported_value": "89.0"}, {"count": 1, "reported_value": "89.13"}, {"count": 16, "reported_value": "9.0"}, {"count": 2, "reported_value": "9.12"}, {"count": 1, "reported_value": "9.33"}, {"count": 1, "reported_value": "9.5"}, {"count": 1, "reported_value": "9.55"}, {"count": 3, "reported_value": "9.77"}, {"count": 1, "reported_value": "93.33"}, {"count": 2, "reported_value": "94.0"}, {"count": 3, "reported_value": "95.5"}, {"count": 1, "reported_value": "96.0"}, {"count": 2, "reported_value": "97.72"}, {"count": 2, "reported_value": "99.0"}]}`.

OBSERVED: CHEMBL3301371 censored/other reported boundaries: `{"<": [{"count": 115, "reported_value": "3.0"}], ">": [{"count": 127, "reported_value": "150.0"}], "UNKNOWN": [{"count": 8, "reported_value": "10.0"}, {"count": 1, "reported_value": "10.2"}, {"count": 3, "reported_value": "10.23"}, {"count": 3, "reported_value": "10.47"}, {"count": 1, "reported_value": "10.63"}, {"count": 1, "reported_value": "10.72"}, {"count": 1, "reported_value": "10.8"}, {"count": 1, "reported_value": "10.96"}, {"count": 1, "reported_value": "100.0"}, {"count": 1, "reported_value": "101.0"}, {"count": 2, "reported_value": "102.33"}, {"count": 1, "reported_value": "103.2"}, {"count": 3, "reported_value": "104.71"}, {"count": 1, "reported_value": "105.0"}, {"count": 2, "reported_value": "107.0"}, {"count": 3, "reported_value": "107.15"}, {"count": 3, "reported_value": "108.0"}, {"count": 2, "reported_value": "109.65"}, {"count": 3, "reported_value": "11.0"}, {"count": 3, "reported_value": "11.48"}, {"count": 1, "reported_value": "11.75"}, {"count": 1, "reported_value": "110.0"}, {"count": 1, "reported_value": "111.0"}, {"count": 1, "reported_value": "112.2"}, {"count": 1, "reported_value": "113.0"}, {"count": 1, "reported_value": "114.0"}, {"count": 1, "reported_value": "114.82"}, {"count": 3, "reported_value": "117.49"}, {"count": 1, "reported_value": "118.0"}, {"count": 1, "reported_value": "119.0"}, {"count": 8, "reported_value": "12.0"}, {"count": 4, "reported_value": "12.02"}, {"count": 1, "reported_value": "12.15"}, {"count": 5, "reported_value": "12.3"}, {"count": 1, "reported_value": "12.5"}, {"count": 2, "reported_value": "12.59"}, {"count": 1, "reported_value": "12.73"}, {"count": 4, "reported_value": "12.88"}, {"count": 2, "reported_value": "120.23"}, {"count": 1, "reported_value": "121.0"}, {"count": 3, "reported_value": "123.03"}, {"count": 1, "reported_value": "125.89"}, {"count": 1, "reported_value": "128.0"}, {"count": 2, "reported_value": "128.82"}, {"count": 1, "reported_value": "129.0"}, {"count": 5, "reported_value": "13.0"}, {"count": 3, "reported_value": "13.18"}, {"count": 3, "reported_value": "13.49"}, {"count": 1, "reported_value": "13.78"}, {"count": 2, "reported_value": "13.8"}, {"count": 2, "reported_value": "130.0"}, {"count": 2, "reported_value": "135.0"}, {"count": 1, "reported_value": "136.0"}, {"count": 1, "reported_value": "137.0"}, {"count": 4, "reported_value": "138.04"}, {"count": 1, "reported_value": "139.0"}, {"count": 3, "reported_value": "14.0"}, {"count": 2, "reported_value": "14.13"}, {"count": 1, "reported_value": "14.24"}, {"count": 1, "reported_value": "14.3"}, {"count": 2, "reported_value": "14.45"}, {"count": 2, "reported_value": "14.79"}, {"count": 1, "reported_value": "140.0"}, {"count": 1, "reported_value": "141.0"}, {"count": 1, "reported_value": "141.25"}, {"count": 1, "reported_value": "142.0"}, {"count": 2, "reported_value": "144.0"}, {"count": 3, "reported_value": "144.54"}, {"count": 3, "reported_value": "147.91"}, {"count": 1, "reported_value": "149.0"}, {"count": 5, "reported_value": "15.0"}, {"count": 1, "reported_value": "15.14"}, {"count": 1, "reported_value": "15.3"}, {"count": 1, "reported_value": "15.85"}, {"count": 4, "reported_value": "16.0"}, {"count": 2, "reported_value": "16.22"}, {"count": 1, "reported_value": "16.25"}, {"count": 3, "reported_value": "16.6"}, {"count": 3, "reported_value": "16.98"}, {"count": 4, "reported_value": "17.0"}, {"count": 1, "reported_value": "17.16"}, {"count": 1, "reported_value": "17.32"}, {"count": 4, "reported_value": "17.38"}, {"count": 3, "reported_value": "18.0"}, {"count": 2, "reported_value": "18.2"}, {"count": 1, "reported_value": "18.62"}, {"count": 1, "reported_value": "18.84"}, {"count": 1, "reported_value": "18.89"}, {"count": 4, "reported_value": "19.0"}, {"count": 3, "reported_value": "19.05"}, {"count": 1, "reported_value": "19.44"}, {"count": 3, "reported_value": "19.5"}, {"count": 1, "reported_value": "19.6"}, {"count": 5, "reported_value": "19.95"}, {"count": 5, "reported_value": "20.0"}, {"count": 3, "reported_value": "20.42"}, {"count": 2, "reported_value": "20.89"}, {"count": 4, "reported_value": "21.0"}, {"count": 1, "reported_value": "21.3"}, {"count": 1, "reported_value": "21.38"}, {"count": 1, "reported_value": "21.47"}, {"count": 3, "reported_value": "21.88"}, {"count": 2, "reported_value": "22.0"}, {"count": 1, "reported_value": "22.39"}, {"count": 1, "reported_value": "22.77"}, {"count": 1, "reported_value": "22.91"}, {"count": 2, "reported_value": "23.0"}, {"count": 2, "reported_value": "23.44"}, {"count": 5, "reported_value": "23.99"}, {"count": 1, "reported_value": "24.0"}, {"count": 2, "reported_value": "24.55"}, {"count": 1, "reported_value": "25.0"}, {"count": 2, "reported_value": "25.12"}, {"count": 1, "reported_value": "25.33"}, {"count": 3, "reported_value": "25.7"}, {"count": 3, "reported_value": "26.0"}, {"count": 1, "reported_value": "26.3"}, {"count": 5, "reported_value": "26.92"}, {"count": 1, "reported_value": "26.98"}, {"count": 3, "reported_value": "27.0"}, {"count": 1, "reported_value": "27.54"}, {"count": 4, "reported_value": "28.0"}, {"count": 3, "reported_value": "28.18"}, {"count": 6, "reported_value": "29.0"}, {"count": 3, "reported_value": "29.51"}, {"count": 2, "reported_value": "3.0"}, {"count": 1, "reported_value": "3.09"}, {"count": 1, "reported_value": "3.16"}, {"count": 1, "reported_value": "3.24"}, {"count": 1, "reported_value": "3.31"}, {"count": 3, "reported_value": "3.39"}, {"count": 1, "reported_value": "3.63"}, {"count": 1, "reported_value": "3.8"}, {"count": 1, "reported_value": "3.87"}, {"count": 1, "reported_value": "30.0"}, {"count": 2, "reported_value": "30.2"}, {"count": 1, "reported_value": "30.51"}, {"count": 1, "reported_value": "30.72"}, {"count": 2, "reported_value": "30.9"}, {"count": 3, "reported_value": "31.0"}, {"count": 2, "reported_value": "31.62"}, {"count": 1, "reported_value": "32.36"}, {"count": 2, "reported_value": "33.0"}, {"count": 1, "reported_value": "33.11"}, {"count": 2, "reported_value": "33.88"}, {"count": 1, "reported_value": "34.0"}, {"count": 1, "reported_value": "34.5"}, {"count": 1, "reported_value": "35.0"}, {"count": 5, "reported_value": "35.48"}, {"count": 1, "reported_value": "36.08"}, {"count": 3, "reported_value": "36.31"}, {"count": 1, "reported_value": "37.0"}, {"count": 3, "reported_value": "38.0"}, {"count": 2, "reported_value": "38.02"}, {"count": 1, "reported_value": "38.9"}, {"count": 2, "reported_value": "39.0"}, {"count": 2, "reported_value": "39.81"}, {"count": 7, "reported_value": "4.0"}, {"count": 2, "reported_value": "4.17"}, {"count": 1, "reported_value": "4.24"}, {"count": 1, "reported_value": "4.37"}, {"count": 1, "reported_value": "4.68"}, {"count": 3, "reported_value": "4.79"}, {"count": 1, "reported_value": "40.0"}, {"count": 3, "reported_value": "40.74"}, {"count": 1, "reported_value": "41.0"}, {"count": 1, "reported_value": "41.35"}, {"count": 1, "reported_value": "41.41"}, {"count": 2, "reported_value": "42.0"}, {"count": 5, "reported_value": "42.66"}, {"count": 3, "reported_value": "43.0"}, {"count": 1, "reported_value": "43.36"}, {"count": 1, "reported_value": "43.43"}, {"count": 1, "reported_value": "43.65"}, {"count": 3, "reported_value": "44.67"}, {"count": 2, "reported_value": "45.71"}, {"count": 3, "reported_value": "46.0"}, {"count": 1, "reported_value": "46.28"}, {"count": 1, "reported_value": "46.77"}, {"count": 1, "reported_value": "47.0"}, {"count": 1, "reported_value": "47.91"}, {"count": 1, "reported_value": "48.44"}, {"count": 1, "reported_value": "48.98"}, {"count": 7, "reported_value": "5.0"}, {"count": 2, "reported_value": "5.01"}, {"count": 4, "reported_value": "5.13"}, {"count": 2, "reported_value": "5.25"}, {"count": 1, "reported_value": "5.29"}, {"count": 1, "reported_value": "5.37"}, {"count": 2, "reported_value": "5.5"}, {"count": 1, "reported_value": "5.75"}, {"count": 1, "reported_value": "5.79"}, {"count": 1, "reported_value": "50.0"}, {"count": 3, "reported_value": "50.12"}, {"count": 1, "reported_value": "50.96"}, {"count": 2, "reported_value": "51.0"}, {"count": 2, "reported_value": "51.29"}, {"count": 2, "reported_value": "52.0"}, {"count": 5, "reported_value": "52.48"}, {"count": 2, "reported_value": "53.0"}, {"count": 3, "reported_value": "53.7"}, {"count": 1, "reported_value": "54.0"}, {"count": 3, "reported_value": "54.95"}, {"count": 1, "reported_value": "55.0"}, {"count": 2, "reported_value": "56.0"}, {"count": 2, "reported_value": "56.23"}, {"count": 1, "reported_value": "57.0"}, {"count": 1, "reported_value": "57.54"}, {"count": 1, "reported_value": "58.0"}, {"count": 1, "reported_value": "58.88"}, {"count": 1, "reported_value": "59.0"}, {"count": 1, "reported_value": "59.87"}, {"count": 8, "reported_value": "6.0"}, {"count": 3, "reported_value": "6.17"}, {"count": 3, "reported_value": "6.31"}, {"count": 2, "reported_value": "6.61"}, {"count": 2, "reported_value": "6.76"}, {"count": 2, "reported_value": "6.92"}, {"count": 2, "reported_value": "60.0"}, {"count": 2, "reported_value": "61.0"}, {"count": 2, "reported_value": "61.66"}, {"count": 2, "reported_value": "63.1"}, {"count": 3, "reported_value": "64.0"}, {"count": 1, "reported_value": "64.34"}, {"count": 4, "reported_value": "64.57"}, {"count": 2, "reported_value": "65.0"}, {"count": 3, "reported_value": "66.0"}, {"count": 2, "reported_value": "66.07"}, {"count": 1, "reported_value": "67.0"}, {"count": 1, "reported_value": "67.61"}, {"count": 1, "reported_value": "69.0"}, {"count": 6, "reported_value": "69.18"}, {"count": 6, "reported_value": "7.0"}, {"count": 1, "reported_value": "7.08"}, {"count": 1, "reported_value": "7.11"}, {"count": 1, "reported_value": "7.2"}, {"count": 1, "reported_value": "7.24"}, {"count": 1, "reported_value": "7.33"}, {"count": 1, "reported_value": "7.48"}, {"count": 1, "reported_value": "7.59"}, {"count": 2, "reported_value": "7.94"}, {"count": 1, "reported_value": "70.0"}, {"count": 3, "reported_value": "70.79"}, {"count": 1, "reported_value": "71.99"}, {"count": 6, "reported_value": "72.44"}, {"count": 1, "reported_value": "73.0"}, {"count": 1, "reported_value": "74.0"}, {"count": 4, "reported_value": "74.13"}, {"count": 1, "reported_value": "75.0"}, {"count": 2, "reported_value": "75.86"}, {"count": 1, "reported_value": "75.93"}, {"count": 1, "reported_value": "76.0"}, {"count": 2, "reported_value": "77.0"}, {"count": 1, "reported_value": "78.0"}, {"count": 1, "reported_value": "79.43"}, {"count": 1, "reported_value": "79.99"}, {"count": 9, "reported_value": "8.0"}, {"count": 2, "reported_value": "8.13"}, {"count": 2, "reported_value": "8.51"}, {"count": 2, "reported_value": "8.71"}, {"count": 1, "reported_value": "8.91"}, {"count": 1, "reported_value": "80.0"}, {"count": 2, "reported_value": "81.0"}, {"count": 1, "reported_value": "82.0"}, {"count": 2, "reported_value": "83.18"}, {"count": 1, "reported_value": "84.0"}, {"count": 3, "reported_value": "85.0"}, {"count": 1, "reported_value": "85.11"}, {"count": 1, "reported_value": "87.0"}, {"count": 4, "reported_value": "87.1"}, {"count": 1, "reported_value": "88.0"}, {"count": 4, "reported_value": "89.13"}, {"count": 5, "reported_value": "9.0"}, {"count": 1, "reported_value": "9.01"}, {"count": 2, "reported_value": "9.12"}, {"count": 1, "reported_value": "9.33"}, {"count": 2, "reported_value": "9.55"}, {"count": 4, "reported_value": "9.77"}, {"count": 1, "reported_value": "9.8"}, {"count": 1, "reported_value": "9.88"}, {"count": 1, "reported_value": "9.9"}, {"count": 1, "reported_value": "9.95"}, {"count": 5, "reported_value": "91.0"}, {"count": 3, "reported_value": "91.2"}, {"count": 1, "reported_value": "93.03"}, {"count": 1, "reported_value": "93.33"}, {"count": 1, "reported_value": "95.5"}, {"count": 1, "reported_value": "97.72"}, {"count": 1, "reported_value": "98.0"}, {"count": 1, "reported_value": "99.0"}]}`.

OBSERVED: CHEMBL3301372 censored/other reported boundaries: `{"<": [{"count": 104, "reported_value": "3.0"}], ">": [{"count": 15, "reported_value": "150.0"}], "UNKNOWN": [{"count": 3, "reported_value": "10.0"}, {"count": 2, "reported_value": "10.23"}, {"count": 2, "reported_value": "10.47"}, {"count": 5, "reported_value": "10.72"}, {"count": 2, "reported_value": "10.96"}, {"count": 1, "reported_value": "102.33"}, {"count": 1, "reported_value": "11.48"}, {"count": 2, "reported_value": "12.02"}, {"count": 2, "reported_value": "12.3"}, {"count": 2, "reported_value": "12.59"}, {"count": 2, "reported_value": "12.88"}, {"count": 1, "reported_value": "123.03"}, {"count": 1, "reported_value": "125.0"}, {"count": 1, "reported_value": "125.89"}, {"count": 1, "reported_value": "128.82"}, {"count": 2, "reported_value": "13.18"}, {"count": 3, "reported_value": "13.49"}, {"count": 1, "reported_value": "13.5"}, {"count": 5, "reported_value": "13.8"}, {"count": 1, "reported_value": "134.9"}, {"count": 1, "reported_value": "14.0"}, {"count": 3, "reported_value": "14.45"}, {"count": 1, "reported_value": "14.5"}, {"count": 1, "reported_value": "14.78"}, {"count": 3, "reported_value": "14.79"}, {"count": 2, "reported_value": "15.14"}, {"count": 6, "reported_value": "15.49"}, {"count": 1, "reported_value": "16.0"}, {"count": 2, "reported_value": "16.22"}, {"count": 2, "reported_value": "16.6"}, {"count": 1, "reported_value": "16.98"}, {"count": 4, "reported_value": "17.38"}, {"count": 3, "reported_value": "17.78"}, {"count": 3, "reported_value": "18.2"}, {"count": 2, "reported_value": "18.62"}, {"count": 3, "reported_value": "19.05"}, {"count": 1, "reported_value": "19.45"}, {"count": 2, "reported_value": "19.5"}, {"count": 1, "reported_value": "19.91"}, {"count": 2, "reported_value": "19.95"}, {"count": 1, "reported_value": "20.0"}, {"count": 1, "reported_value": "20.05"}, {"count": 1, "reported_value": "20.42"}, {"count": 2, "reported_value": "21.38"}, {"count": 1, "reported_value": "21.88"}, {"count": 1, "reported_value": "21.9"}, {"count": 2, "reported_value": "22.39"}, {"count": 1, "reported_value": "22.91"}, {"count": 1, "reported_value": "23.2"}, {"count": 1, "reported_value": "23.22"}, {"count": 1, "reported_value": "23.44"}, {"count": 1, "reported_value": "23.99"}, {"count": 3, "reported_value": "24.55"}, {"count": 3, "reported_value": "25.12"}, {"count": 2, "reported_value": "25.7"}, {"count": 1, "reported_value": "25.92"}, {"count": 2, "reported_value": "26.3"}, {"count": 1, "reported_value": "26.41"}, {"count": 2, "reported_value": "26.92"}, {"count": 1, "reported_value": "27.3"}, {"count": 3, "reported_value": "27.54"}, {"count": 2, "reported_value": "28.18"}, {"count": 1, "reported_value": "28.84"}, {"count": 2, "reported_value": "29.51"}, {"count": 1, "reported_value": "3.2"}, {"count": 1, "reported_value": "3.24"}, {"count": 1, "reported_value": "3.3"}, {"count": 3, "reported_value": "3.31"}, {"count": 1, "reported_value": "3.39"}, {"count": 1, "reported_value": "3.4"}, {"count": 1, "reported_value": "3.46"}, {"count": 2, "reported_value": "3.47"}, {"count": 1, "reported_value": "3.55"}, {"count": 3, "reported_value": "3.72"}, {"count": 1, "reported_value": "3.8"}, {"count": 1, "reported_value": "3.81"}, {"count": 1, "reported_value": "3.89"}, {"count": 1, "reported_value": "3.91"}, {"count": 3, "reported_value": "3.98"}, {"count": 1, "reported_value": "30.12"}, {"count": 2, "reported_value": "30.2"}, {"count": 2, "reported_value": "30.9"}, {"count": 1, "reported_value": "32.0"}, {"count": 3, "reported_value": "32.36"}, {"count": 1, "reported_value": "33.88"}, {"count": 2, "reported_value": "34.67"}, {"count": 2, "reported_value": "35.48"}, {"count": 1, "reported_value": "36.31"}, {"count": 1, "reported_value": "37.0"}, {"count": 3, "reported_value": "38.02"}, {"count": 3, "reported_value": "38.9"}, {"count": 2, "reported_value": "39.81"}, {"count": 1, "reported_value": "4.04"}, {"count": 1, "reported_value": "4.17"}, {"count": 2, "reported_value": "4.27"}, {"count": 1, "reported_value": "4.46"}, {"count": 2, "reported_value": "4.47"}, {"count": 3, "reported_value": "4.57"}, {"count": 2, "reported_value": "4.68"}, {"count": 1, "reported_value": "4.7"}, {"count": 1, "reported_value": "4.76"}, {"count": 3, "reported_value": "4.79"}, {"count": 1, "reported_value": "4.88"}, {"count": 2, "reported_value": "4.9"}, {"count": 1, "reported_value": "4.92"}, {"count": 1, "reported_value": "40.0"}, {"count": 1, "reported_value": "40.74"}, {"count": 1, "reported_value": "41.69"}, {"count": 1, "reported_value": "42.5"}, {"count": 2, "reported_value": "42.66"}, {"count": 1, "reported_value": "43.65"}, {"count": 1, "reported_value": "44.0"}, {"count": 1, "reported_value": "45.71"}, {"count": 1, "reported_value": "46.77"}, {"count": 1, "reported_value": "5.01"}, {"count": 1, "reported_value": "5.05"}, {"count": 1, "reported_value": "5.13"}, {"count": 1, "reported_value": "5.16"}, {"count": 1, "reported_value": "5.17"}, {"count": 3, "reported_value": "5.25"}, {"count": 2, "reported_value": "5.37"}, {"count": 1, "reported_value": "5.5"}, {"count": 2, "reported_value": "5.62"}, {"count": 3, "reported_value": "5.75"}, {"count": 1, "reported_value": "5.88"}, {"count": 2, "reported_value": "50.12"}, {"count": 2, "reported_value": "51.29"}, {"count": 1, "reported_value": "52.48"}, {"count": 4, "reported_value": "54.95"}, {"count": 1, "reported_value": "56.23"}, {"count": 1, "reported_value": "57.11"}, {"count": 3, "reported_value": "6.0"}, {"count": 2, "reported_value": "6.17"}, {"count": 3, "reported_value": "6.31"}, {"count": 2, "reported_value": "6.46"}, {"count": 2, "reported_value": "6.61"}, {"count": 2, "reported_value": "6.76"}, {"count": 2, "reported_value": "6.92"}, {"count": 1, "reported_value": "6.99"}, {"count": 2, "reported_value": "60.26"}, {"count": 1, "reported_value": "61.66"}, {"count": 1, "reported_value": "64.0"}, {"count": 1, "reported_value": "64.57"}, {"count": 1, "reported_value": "66.07"}, {"count": 1, "reported_value": "67.61"}, {"count": 1, "reported_value": "7.0"}, {"count": 2, "reported_value": "7.08"}, {"count": 1, "reported_value": "7.24"}, {"count": 2, "reported_value": "7.41"}, {"count": 3, "reported_value": "7.59"}, {"count": 3, "reported_value": "7.76"}, {"count": 1, "reported_value": "7.9"}, {"count": 2, "reported_value": "7.94"}, {"count": 1, "reported_value": "74.13"}, {"count": 1, "reported_value": "77.62"}, {"count": 1, "reported_value": "8.13"}, {"count": 3, "reported_value": "8.51"}, {"count": 1, "reported_value": "8.7"}, {"count": 2, "reported_value": "8.71"}, {"count": 1, "reported_value": "8.91"}, {"count": 1, "reported_value": "83.18"}, {"count": 2, "reported_value": "87.1"}, {"count": 4, "reported_value": "9.12"}, {"count": 2, "reported_value": "9.33"}, {"count": 1, "reported_value": "9.5"}, {"count": 2, "reported_value": "9.77"}, {"count": 2, "reported_value": "95.5"}]}`.

## TDC target audit

OBSERVED: Raw columns are ID, X, Y; Drug_ID in the requested audit means ID, raw SMILES means X. Both tables were downloaded directly using the verified PyTDC 1.1.15 source registry. PyTDC itself was not installed or invoked.

### Clearance_Microsome_AZ

OBSERVED:
```json
{
  "total_rows": 1102,
  "numeric_rows": 1102,
  "missing_rows": 0,
  "unparseable_rows": 0,
  "exactly_3": 287,
  "exactly_150": 84,
  "inequality_strings": 0,
  "top_value_frequencies": [
    {
      "value": "3.0",
      "count": 287
    },
    {
      "value": "150.0",
      "count": 84
    },
    {
      "value": "6.0",
      "count": 23
    },
    {
      "value": "4.0",
      "count": 22
    },
    {
      "value": "5.0",
      "count": 22
    },
    {
      "value": "7.0",
      "count": 19
    },
    {
      "value": "11.0",
      "count": 17
    },
    {
      "value": "9.0",
      "count": 16
    },
    {
      "value": "8.0",
      "count": 13
    },
    {
      "value": "12.0",
      "count": 13
    }
  ],
  "min": 3.0,
  "q05": 3.0,
  "q25": 3.0,
  "median": 12.735,
  "q75": 42.66,
  "q95": 150.0,
  "max": 150.0,
  "iqr": 39.66,
  "mad": 9.735
}
```

### Clearance_Hepatocyte_AZ

OBSERVED:
```json
{
  "total_rows": 1213,
  "numeric_rows": 1213,
  "missing_rows": 0,
  "unparseable_rows": 0,
  "exactly_3": 195,
  "exactly_150": 137,
  "inequality_strings": 0,
  "top_value_frequencies": [
    {
      "value": "3.0",
      "count": 195
    },
    {
      "value": "150.0",
      "count": 137
    },
    {
      "value": "10.0",
      "count": 11
    },
    {
      "value": "6.0",
      "count": 10
    },
    {
      "value": "8.0",
      "count": 9
    },
    {
      "value": "12.0",
      "count": 8
    },
    {
      "value": "17.38",
      "count": 8
    },
    {
      "value": "4.0",
      "count": 7
    },
    {
      "value": "5.0",
      "count": 7
    },
    {
      "value": "7.0",
      "count": 7
    }
  ],
  "min": 3.0,
  "q05": 3.0,
  "q25": 6.0,
  "median": 19.0,
  "q75": 64.0,
  "q95": 150.0,
  "max": 150.0,
  "iqr": 58.0,
  "mad": 16.0
}
```

## Species and microsome reconciliation

# TDC hepatocyte summary

```json
{
  "INFERRED": {
    "claim_status": "REPRODUCED",
    "decision_rule": "REPRODUCED requires both rat-only and human-only structure matches with exactly matching numeric source labels. PARTIALLY_REPRODUCED requires label-specific matches to both species without both exclusive structural witnesses; otherwise NOT_REPRODUCED. Censored matches identify numeric boundaries only."
  },
  "OBSERVED": {
    "duplicate_label_groups": {
      "different": 193
    },
    "duplicate_trace_groups": {
      "distinct_labels_match_rat_and_human": 187,
      "partial_or_unresolved": 6
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
    "unique_valid_structure_counts": {
      "ambiguous_unparseable": 0,
      "both": 218,
      "human_only": 183,
      "neither": 10,
      "rat_only": 609
    }
  },
  "UNRESOLVED": "Historical lineage cannot be proven by equality alone. A shared structure/label can map to both species; retain ambiguity. Species uses ChEMBL assay organism/taxonomy, never target magnitude."
}
```

# TDC microsome summary

```json
{
  "INFERRED": "mL/min/g and microL/min/mg are dimensionally and numerically equivalent (unit conversion in numerator and denominator cancels). Exact numeric matches require no target transformation; retained boundary numbers without inequality strings indicate censor information is absent from the TDC table. This is not physiological scaling.",
  "OBSERVED": {
    "chembl_only_structures": 5,
    "chembl_original_units": {
      "microL/min/mg": 1102
    },
    "chembl_standard_units": {
      "mL.min-1.g-1": 1102
    },
    "chembl_unmatched_rows": 5,
    "original_to_standard_numeric_equal_rows": 1102,
    "qualifier_reconciliation_candidate_pairs": {
      "<": {
        "candidate_pairs": 274,
        "numeric_equal_pairs": 274,
        "tdc_inequality_present_pairs": 0
      },
      ">": {
        "candidate_pairs": 84,
        "numeric_equal_pairs": 84,
        "tdc_inequality_present_pairs": 0
      },
      "None": {
        "candidate_pairs": 739,
        "numeric_equal_pairs": 739,
        "tdc_inequality_present_pairs": 0
      }
    },
    "structure_overlap": 1097,
    "tdc_only_structures": 5,
    "tdc_raw_unit_column": null,
    "tdc_rows_structure_matched_without_numeric_match": 0,
    "tdc_rows_with_exact_numeric_match": 1097,
    "tdc_rows_with_multiple_candidates": 0,
    "tdc_unmatched_rows": 5
  },
  "UNRESOLVED": "The TDC table has no units or censoring field. Numeric agreement supports, but cannot independently establish, source lineage or unit annotation. No claim about undocumented historical processing is made."
}
```

## Paired human cohort

# Membership summary

```json
{
  "INFERRED": "This establishes membership only under two identity definitions. It does not establish matched experimental conditions or independent biological replicates.",
  "OBSERVED": {
    "canonical_structure_overlap_n": 187,
    "id_overlap_n": 187,
    "id_structure_disagreement_or_ambiguity": [],
    "shared_ids": [
      "CHEMBL1017",
      "CHEMBL1020",
      "CHEMBL103667",
      "CHEMBL1071",
      "CHEMBL108",
      "CHEMBL1088752",
      "CHEMBL1089518",
      "CHEMBL1091137",
      "CHEMBL11",
      "CHEMBL112",
      "CHEMBL114",
      "CHEMBL1144",
      "CHEMBL1164729",
      "CHEMBL1194325",
      "CHEMBL12",
      "CHEMBL1201753",
      "CHEMBL1204759",
      "CHEMBL1213118",
      "CHEMBL1232461",
      "CHEMBL1256967",
      "CHEMBL12610",
      "CHEMBL1276308",
      "CHEMBL1346",
      "CHEMBL1355736",
      "CHEMBL1363",
      "CHEMBL1371",
      "CHEMBL139",
      "CHEMBL1405150",
      "CHEMBL141157",
      "CHEMBL1427959",
      "CHEMBL1463345",
      "CHEMBL1464",
      "CHEMBL1483",
      "CHEMBL1513",
      "CHEMBL1575409",
      "CHEMBL1614705",
      "CHEMBL1645392",
      "CHEMBL1688458",
      "CHEMBL1689109",
      "CHEMBL1689110",
      "CHEMBL1689111",
      "CHEMBL1689117",
      "CHEMBL1689119",
      "CHEMBL1689126",
      "CHEMBL1689127",
      "CHEMBL1689128",
      "CHEMBL1689133",
      "CHEMBL1689135",
      "CHEMBL1689137",
      "CHEMBL17157",
      "CHEMBL1734492",
      "CHEMBL1761322",
      "CHEMBL1773254",
      "CHEMBL1778628",
      "CHEMBL1778639",
      "CHEMBL1778644",
      "CHEMBL1779512",
      "CHEMBL1790041",
      "CHEMBL1800526",
      "CHEMBL1800528",
      "CHEMBL1800659",
      "CHEMBL1807820",
      "CHEMBL1807821",
      "CHEMBL1807823",
      "CHEMBL1807827",
      "CHEMBL1807829",
      "CHEMBL1829174",
      "CHEMBL1829763",
      "CHEMBL1834184",
      "CHEMBL1835918",
      "CHEMBL1852508",
      "CHEMBL1874317",
      "CHEMBL1900528",
      "CHEMBL1916271",
      "CHEMBL1916272",
      "CHEMBL1916282",
      "CHEMBL1916288",
      "CHEMBL1916289",
      "CHEMBL1917443",
      "CHEMBL1917450",
      "CHEMBL1917456",
      "CHEMBL1917458",
      "CHEMBL1917459",
      "CHEMBL192",
      "CHEMBL1929039",
      "CHEMBL193",
      "CHEMBL1934426",
      "CHEMBL1938400",
      "CHEMBL1939560",
      "CHEMBL1944691",
      "CHEMBL1945033",
      "CHEMBL1947157",
      "CHEMBL1951575",
      "CHEMBL196707",
      "CHEMBL2017291",
      "CHEMBL2018964",
      "CHEMBL2018969",
      "CHEMBL20210",
      "CHEMBL203059",
      "CHEMBL2036958",
      "CHEMBL205078",
      "CHEMBL2057371",
      "CHEMBL2057372",
      "CHEMBL2058529",
      "CHEMBL2062774",
      "CHEMBL2070950",
      "CHEMBL2137199",
      "CHEMBL2141746",
      "CHEMBL2147032",
      "CHEMBL2147033",
      "CHEMBL2147475",
      "CHEMBL2158771",
      "CHEMBL2158785",
      "CHEMBL2158792",
      "CHEMBL2158793",
      "CHEMBL2158826",
      "CHEMBL2158839",
      "CHEMBL217899",
      "CHEMBL2181753",
      "CHEMBL2181926",
      "CHEMBL2181927",
      "CHEMBL2207669",
      "CHEMBL2216859",
      "CHEMBL2216870",
      "CHEMBL23",
      "CHEMBL2326623",
      "CHEMBL2326624",
      "CHEMBL232846",
      "CHEMBL2349318",
      "CHEMBL235789",
      "CHEMBL2364624",
      "CHEMBL256668",
      "CHEMBL257025",
      "CHEMBL271012",
      "CHEMBL272705",
      "CHEMBL35",
      "CHEMBL360227",
      "CHEMBL361546",
      "CHEMBL361812",
      "CHEMBL370492",
      "CHEMBL380732",
      "CHEMBL380947",
      "CHEMBL38380",
      "CHEMBL402501",
      "CHEMBL402728",
      "CHEMBL402986",
      "CHEMBL403225",
      "CHEMBL403313",
      "CHEMBL408",
      "CHEMBL42",
      "CHEMBL423",
      "CHEMBL451",
      "CHEMBL457",
      "CHEMBL46",
      "CHEMBL46740",
      "CHEMBL472",
      "CHEMBL49",
      "CHEMBL5",
      "CHEMBL551170",
      "CHEMBL551813",
      "CHEMBL552512",
      "CHEMBL553",
      "CHEMBL560219",
      "CHEMBL560423",
      "CHEMBL560993",
      "CHEMBL565755",
      "CHEMBL570015",
      "CHEMBL578194",
      "CHEMBL580",
      "CHEMBL583042",
      "CHEMBL589973",
      "CHEMBL62136",
      "CHEMBL682",
      "CHEMBL6966",
      "CHEMBL71",
      "CHEMBL72",
      "CHEMBL723",
      "CHEMBL782",
      "CHEMBL787",
      "CHEMBL82663",
      "CHEMBL833",
      "CHEMBL841",
      "CHEMBL894",
      "CHEMBL945",
      "CHEMBL95",
      "CHEMBL956",
      "CHEMBL957"
    ],
    "shared_structures_with_multiple_rows_or_ids": 0,
    "shared_structures_without_shared_id": 0
  },
  "UNRESOLVED": "Any repeated activities remain unresolved replicates; no aggregation or label selection occurs. No clearance ratio, difference, scaling, correlation or model is calculated."
}
```

## Biogen

OBSERVED: 3521 rows; exact non-null HLM N = 3087; column `LOG HLM_CLint (mL/min/kg)`. See BIOGEN_AUDIT.md for independent descriptive results; no numerical cross-dataset comparison is made.

## Chemical-space audit

INFERRED: RDKit 2025.03.6 sanitized isomeric canonical SMILES; stereochemistry, isotopes, charge and all disconnected fragments retained. No parent selection, desalting, neutralization, tautomer normalization or stereo removal. RDKit ordinary explicit-H handling applies. Equality is string equality of valid keys; missing/invalid structures never match. Identity is representation-specific, not proof of sample identity.

INFERRED: Descriptors use RDKit MolWt (g/mol), Wildman-Crippen MolLogP, CalcTPSA (A^2), Lipinski NumHDonors/NumHAcceptors, strict CalcNumRotatableBonds, CalcFractionCSP3. Every valid source row is characterised, including duplicates and rows with missing targets. No outliers are removed.

| Source / property | Numeric N | Min | Q05 | Q25 | Median | Q75 | Q95 | Max | IQR | MAD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| OBSERVED: CHEMBL3301370 / molecular_weight | 1102 | 133.154 | 241.291 | 340.335 | 414.549 | 478.622 | 569.66 | 1065.7 | 138.288 | 67.044 |
| OBSERVED: CHEMBL3301370 / clogp | 1102 | -1.9714 | 1.39099 | 2.81585 | 3.64341 | 4.53905 | 5.64899 | 10.3425 | 1.7232 | 0.85982 |
| OBSERVED: CHEMBL3301370 / tpsa | 1102 | 3.24 | 38.3325 | 57.9025 | 79.54 | 96.4125 | 124.276 | 300.89 | 38.51 | 17.995 |
| OBSERVED: CHEMBL3301370 / hbd | 1102 | 0 | 0 | 1 | 1 | 2 | 4 | 11 | 1 | 1 |
| OBSERVED: CHEMBL3301370 / hba | 1102 | 1 | 2 | 4 | 5 | 6 | 8 | 14 | 2 | 1 |
| OBSERVED: CHEMBL3301370 / rotatable_bonds | 1102 | 0 | 2 | 4 | 6 | 8 | 11.95 | 23 | 4 | 2 |
| OBSERVED: CHEMBL3301370 / fraction_csp3 | 1102 | 0 | 0 | 0.1875 | 0.315789 | 0.43442 | 0.6 | 0.888889 | 0.24692 | 0.118993 |
| OBSERVED: CHEMBL3301371 / molecular_weight | 837 | 147.177 | 239.66 | 343.423 | 415.862 | 475.004 | 578.185 | 1160.43 | 131.581 | 64.732 |
| OBSERVED: CHEMBL3301371 / clogp | 837 | -7.8314 | 1.03734 | 2.64662 | 3.5376 | 4.41952 | 5.91242 | 10.3425 | 1.7729 | 0.88487 |
| OBSERVED: CHEMBL3301371 / tpsa | 837 | 3.24 | 35.128 | 60.45 | 82.59 | 101.79 | 132.2 | 490.66 | 41.34 | 20.23 |
| OBSERVED: CHEMBL3301371 / hbd | 837 | 0 | 0 | 1 | 2 | 2 | 5 | 18 | 1 | 1 |
| OBSERVED: CHEMBL3301371 / hba | 837 | 1 | 2 | 4 | 5 | 7 | 9 | 18 | 3 | 1 |
| OBSERVED: CHEMBL3301371 / rotatable_bonds | 837 | 0 | 2 | 4 | 6 | 8 | 12 | 28 | 4 | 2 |
| OBSERVED: CHEMBL3301371 / fraction_csp3 | 837 | 0 | 0.0549708 | 0.208333 | 0.315789 | 0.434783 | 0.622868 | 0.846154 | 0.226449 | 0.115789 |
| OBSERVED: CHEMBL3301372 / molecular_weight | 408 | 30.07 | 217.613 | 325.622 | 397.476 | 469.905 | 549.027 | 914.187 | 144.283 | 72.415 |
| OBSERVED: CHEMBL3301372 / clogp | 408 | -1.8644 | 0.91544 | 2.47 | 3.37795 | 4.34332 | 5.69199 | 8.948 | 1.87332 | 0.92795 |
| OBSERVED: CHEMBL3301372 / tpsa | 408 | 0 | 34.6 | 55.71 | 79.515 | 98.585 | 130.746 | 235.97 | 42.875 | 21.945 |
| OBSERVED: CHEMBL3301372 / hbd | 408 | 0 | 0 | 1 | 1 | 2 | 4 | 6 | 1 | 1 |
| OBSERVED: CHEMBL3301372 / hba | 408 | 0 | 2 | 3 | 5 | 7 | 9 | 14 | 4 | 2 |
| OBSERVED: CHEMBL3301372 / rotatable_bonds | 408 | 0 | 1 | 3 | 5 | 7 | 11 | 16 | 4 | 2 |
| OBSERVED: CHEMBL3301372 / fraction_csp3 | 408 | 0 | 0.0601103 | 0.181818 | 0.30602 | 0.428571 | 0.644588 | 1 | 0.246753 | 0.123377 |
| OBSERVED: Clearance_Microsome_AZ / molecular_weight | 1102 | 133.154 | 241.291 | 340.335 | 414.549 | 478.622 | 569.66 | 1065.7 | 138.288 | 67.044 |
| OBSERVED: Clearance_Microsome_AZ / clogp | 1102 | -1.9714 | 1.39099 | 2.81958 | 3.64341 | 4.53905 | 5.64899 | 10.3425 | 1.71948 | 0.85886 |
| OBSERVED: Clearance_Microsome_AZ / tpsa | 1102 | 3.24 | 38.3325 | 57.9025 | 79.46 | 96.33 | 124.276 | 300.89 | 38.4275 | 17.945 |
| OBSERVED: Clearance_Microsome_AZ / hbd | 1102 | 0 | 0 | 1 | 1 | 2 | 4 | 11 | 1 | 1 |
| OBSERVED: Clearance_Microsome_AZ / hba | 1102 | 1 | 2 | 4 | 5 | 6 | 8 | 14 | 2 | 1 |
| OBSERVED: Clearance_Microsome_AZ / rotatable_bonds | 1102 | 0 | 2 | 4 | 6 | 8 | 11.95 | 23 | 4 | 2 |
| OBSERVED: Clearance_Microsome_AZ / fraction_csp3 | 1102 | 0 | 0 | 0.1875 | 0.315789 | 0.43442 | 0.6 | 0.888889 | 0.24692 | 0.118993 |
| OBSERVED: Clearance_Hepatocyte_AZ / molecular_weight | 1213 | 30.07 | 232.543 | 336.432 | 410.4 | 472.387 | 566.887 | 1160.43 | 135.955 | 67.183 |
| OBSERVED: Clearance_Hepatocyte_AZ / clogp | 1213 | -7.8314 | 1.0349 | 2.6037 | 3.4871 | 4.38702 | 5.83048 | 10.3425 | 1.78332 | 0.8891 |
| OBSERVED: Clearance_Hepatocyte_AZ / tpsa | 1213 | 0 | 33.42 | 57.78 | 80.91 | 99.88 | 129.144 | 490.66 | 42.1 | 21.31 |
| OBSERVED: Clearance_Hepatocyte_AZ / hbd | 1213 | 0 | 0 | 1 | 2 | 2 | 4 | 18 | 1 | 1 |
| OBSERVED: Clearance_Hepatocyte_AZ / hba | 1213 | 0 | 2 | 4 | 5 | 7 | 9 | 18 | 3 | 1 |
| OBSERVED: Clearance_Hepatocyte_AZ / rotatable_bonds | 1213 | 0 | 1 | 4 | 6 | 7 | 12 | 28 | 3 | 2 |
| OBSERVED: Clearance_Hepatocyte_AZ / fraction_csp3 | 1213 | 0 | 0.0555556 | 0.2 | 0.3125 | 0.433333 | 0.641143 | 1 | 0.233333 | 0.120192 |
| OBSERVED: Biogen / molecular_weight | 3521 | 150.145 | 219.288 | 268.32 | 313.792 | 364.489 | 461.949 | 1097.4 | 96.169 | 47.581 |
| OBSERVED: Biogen / clogp | 3521 | -1.98 | 0.97814 | 2.0532 | 2.7828 | 3.5326 | 4.7748 | 9.0141 | 1.4794 | 0.7388 |
| OBSERVED: Biogen / tpsa | 3521 | 3.24 | 38.33 | 49.33 | 60.15 | 74.44 | 103.78 | 258.52 | 25.11 | 12.32 |
| OBSERVED: Biogen / hbd | 3521 | 0 | 0 | 1 | 1 | 1 | 3 | 8 | 0 | 0 |
| OBSERVED: Biogen / hba | 3521 | 1 | 2 | 3 | 4 | 5 | 7 | 16 | 2 | 1 |
| OBSERVED: Biogen / rotatable_bonds | 3521 | 0 | 2 | 3 | 4 | 5 | 7 | 35 | 2 | 1 |
| OBSERVED: Biogen / fraction_csp3 | 3521 | 0 | 0.0625 | 0.2 | 0.333333 | 0.466667 | 0.7 | 1 | 0.266667 | 0.133333 |

## Uncertainty and provenance

UNRESOLVED: ChEMBL live API release may differ from historical TDC release; no historical ChEMBL release asserted.

UNRESOLVED: Rat assay strain metadata contains CD1, BC, CD1, NMRI, SCID, or Nd. Species classification follows explicit assay organism Rattus norvegicus/taxonomy 10116 and description; the strain annotation requires source-level review.

UNRESOLVED: Identity matching does not resolve unspecified stereochemistry, tautomer differences or sample provenance.

UNRESOLVED: TDC has numeric targets without native unit/censor fields; absent qualifiers are not evidence of exact uncensored measurements.

OBSERVED: Full machine-readable results are DATA_AUDIT.json. All six complete enriched row tables, structure anomalies and duplicate groups are under data/interim. Raw files and receipt hashes are in manifests/source_manifest.json and PROVENANCE_TABLE.csv. Execution logs include failures with actual errors.

INFERRED: Native ChEMBL source numeric boundary distributions are descriptive, not estimates of uncensored clearance. Raw TDC and Biogen numeric labels do not encode absent censor metadata. Missing metadata remains unknown.

OBSERVED: Acquisition initially failed only while generating the manifest because the ChEMBL status activities field is an integer. All raw downloads were retained; a list-type check fixed manifest generation and acquisition was rerun using the same bytes. No failed computation was replaced by a mock result.
