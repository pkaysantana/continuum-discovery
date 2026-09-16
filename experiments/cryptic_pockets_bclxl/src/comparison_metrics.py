"""Common candidate evaluator, exercised only with synthetic candidates so far."""
import math


def candidate_metrics(candidate_center, reference_center, predicted, reference):
    if len(candidate_center) != 3 or len(reference_center) != 3:
        raise ValueError('Centers must be three-dimensional')
    if not all(math.isfinite(v) for v in (*candidate_center, *reference_center)):
        raise ValueError('Centers must be finite; no fallback center')
    p, r = set(predicted), set(reference)
    if not r:
        raise ValueError('Empty reference invalidates evaluation')
    intersection = len(p & r)
    distance = math.dist(candidate_center, reference_center)
    return {'centroid_distance_angstrom': distance, 'recovered': distance <= 4.0,
            'intersection_count': intersection, 'reference_site_recall': intersection / len(r),
            'predicted_site_precision': intersection / len(p) if p else 0.0,
            'jaccard': intersection / len(p | r)}
