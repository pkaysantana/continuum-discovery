"""v3A.1-RC frozen constants. Canonical spec: docs/V3A_UNCERTAINTY_ASSAY_TRIAGE_SAP_3A1_RC.md.

Nothing here may be tuned. Changing any value invalidates the pre-execution manifest.
"""
import enum
import hashlib
from types import MappingProxyType

from sklearn.ensemble import RandomForestRegressor

PROTOCOL_VERSION = "v3A.1-RC"
STATE_PREEXECUTION = "PREEXECUTION_IMPLEMENTED_NOT_RUN"
STATE_FROZEN = "FROZEN_READY_FOR_EXECUTION"

MASTER_SEED = 20260923
N_FOLDS = 5
COHORT_N = 744
N_INTERIOR = 731
N_BOUNDARY_LOW = 13
N_BOUNDARY_HIGH = 0
N_LEFT_CENSORED = 274
N_RIGHT_CENSORED = 84
N_TOTAL_ASSAY_ROWS = 1102
CLINT_LOW, CLINT_HIGH = 3.0, 150.0

# SAP §8.2 step 3: SHA-256 of  scaffold_key + "_V3A_20260923"
SPLIT_TIE_SUFFIX = "_V3A_20260923"
# SAP §9.3: SHA-256 of  activity_id + "_V3A_TIE_20260923"
RETENTION_TIE_SUFFIX = "_V3A_TIE_20260923"
# Conformal proper-train / calibration scaffold split (task §14; SAP §13.2 "deterministic hash")
CQR_SPLIT_SALT_SUFFIX = "_V3A_CQR_20260923"

COVERAGE_LEVELS = (1.00, 0.90, 0.80, 0.70, 0.60, 0.50)
PRIMARY_COVERAGE = 0.80
CONFORMAL_LEVELS = (0.80, 0.90, 0.95)
N_RANDOM_DEFERRALS = 10_000
N_BOOTSTRAP = 10_000
QRF_LOW_Q, QRF_HIGH_Q = 0.10, 0.90
PRACTICAL_THRESHOLD = 0.10

WEIGHT_SUM_TOL = 1e-12
WEIGHT_MEAN_TOL = 1e-6

DESCRIPTOR_PANEL = (
    "MolWt", "MolLogP", "MolMR", "TPSA", "NumHDonors", "NumHAcceptors",
    "NumRotatableBonds", "RingCount", "NumAromaticRings", "NumAliphaticRings",
    "FractionCSP3", "HeavyAtomCount",
)
PHYSCHEM_KNN = 5

UNCERTAINTY_METHOD_IDS = MappingProxyType({
    "primary": "QRF80_WIDTH",
    "secondary": ("ECFP4_TANIMOTO_FAMILIARITY", "PHYSCHEM_KNN5_FAMILIARITY",
                  "NEFF_INVERSE", "LOCAL_LABEL_SD", "TREE_SD"),
})


class Representation(str, enum.Enum):
    """The only representation permitted in v3A. Routing is by enum identity, never by substring."""
    ECFP4_2048_R2_BINARY_NOCHIRAL = "ECFP4_2048_R2_BINARY_NOCHIRAL"


REPRESENTATION = Representation.ECFP4_2048_R2_BINARY_NOCHIRAL
MORGAN_SPEC = MappingProxyType(
    {"radius": 2, "nBits": 2048, "binary": True, "useChirality": False}
)

FROZEN_RF_PARAMS = MappingProxyType({
    "n_estimators": 500,
    "criterion": "squared_error",
    "max_features": "sqrt",
    "min_samples_split": 2,
    "min_samples_leaf": 2,
    "max_depth": None,
    "bootstrap": True,
    "random_state": MASTER_SEED,
})


def make_frozen_rf() -> RandomForestRegressor:
    """The single factory for the v3A point model. Returns an UNFITTED estimator."""
    return RandomForestRegressor(**dict(FROZEN_RF_PARAMS))


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def split_tiebreak_hash(scaffold_key: str) -> str:
    return sha256_hex(scaffold_key + SPLIT_TIE_SUFFIX)


def retention_tiebreak_hash(activity_id) -> str:
    return sha256_hex(str(activity_id) + RETENTION_TIE_SUFFIX)
