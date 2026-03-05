#!/usr/bin/env python3
"""
AminoAnalytica Workshop Specifications
Spec-Driven Development Requirements for bio_scientist_agent.py
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class PipelineStage(Enum):
    """Required pipeline stages"""
    RFDIFFUSION = "rfdiffusion_backbone_generation"
    PROTEINMPNN = "proteinmpnn_sequence_design"
    BOLTZ2 = "boltz2_complex_validation"
    PESTO = "pesto_binding_validation"

class MetricType(Enum):
    """Required confidence metrics"""
    IPTM = "iptm_score"
    INTERFACE_PAE = "interface_pae"
    HOTSPOT_COVERAGE = "hotspot_coverage_percent"

@dataclass
class WorkshopTarget:
    """Workshop target specification"""
    pdb_id: str
    chain: str
    description: str
    hotspots: List[int]
    target_type: str

@dataclass
class PipelineSpec:
    """Complete pipeline specification"""
    stages: List[PipelineStage]
    required_metrics: List[MetricType]
    default_target: WorkshopTarget

@dataclass
class CapabilitySpec:
    """Required agent capabilities"""
    core_capabilities: List[str]
    aminoanalytica_capabilities: List[str]
    integration_capabilities: List[str]

class AminoAnalyticaWorkshopSpecs:
    """
    Complete AminoAnalytica Workshop Specifications
    Based on workshop requirements for generative protein design
    """

    @staticmethod
    def get_workshop_target_spec() -> WorkshopTarget:
        """SPEC: Workshop default target - PDB 7K43"""
        return WorkshopTarget(
            pdb_id="7K43",
            chain="A",
            description="SARS-CoV-2 Spike RBD - ACE2 Complex",
            hotspots=[417, 453, 455, 489, 500, 501, 505],
            target_type="workshop_default"
        )

    @staticmethod
    def get_pipeline_spec() -> PipelineSpec:
        """SPEC: Complete generative pipeline requirements"""
        return PipelineSpec(
            stages=[
                PipelineStage.RFDIFFUSION,
                PipelineStage.PROTEINMPNN,
                PipelineStage.BOLTZ2,
                PipelineStage.PESTO
            ],
            required_metrics=[
                MetricType.IPTM,
                MetricType.INTERFACE_PAE,
                MetricType.HOTSPOT_COVERAGE
            ],
            default_target=AminoAnalyticaWorkshopSpecs.get_workshop_target_spec()
        )

    @staticmethod
    def get_capability_spec() -> CapabilitySpec:
        """SPEC: Required agent capabilities"""
        return CapabilitySpec(
            core_capabilities=[
                "protein_synthesis",
                "proteinmpnn_generation",
                "esmfold_validation",
                "unibase_memory_management",
                "cross_pathogen_analysis",
                "rmsd_scoring"
            ],
            aminoanalytica_capabilities=[
                "rfdiffusion_backbone",
                "proteinmpnn_sequence",
                "boltz2_validation",
                "pesto_binding",
                "hotspot_targeting",
                "iptm_pae_scoring"
            ],
            integration_capabilities=[
                "biosecurity_screening",
                "threat_detection",
                "motif_analysis"
            ]
        )

    @staticmethod
    def get_scoring_spec() -> Dict[str, Any]:
        """SPEC: Workshop confidence scoring requirements"""
        return {
            "primary_metrics": {
                "iptm_score": {
                    "type": "float",
                    "range": [0.0, 1.0],
                    "high_confidence_threshold": 0.7,
                    "description": "Interface predicted Template Modeling score"
                },
                "interface_pae": {
                    "type": "float",
                    "range": [0.0, 30.0],
                    "high_confidence_threshold": 5.0,
                    "description": "Interface Predicted Aligned Error in Angstroms"
                },
                "hotspot_coverage_percent": {
                    "type": "float",
                    "range": [0.0, 100.0],
                    "minimum_threshold": 50.0,
                    "description": "Percentage of target hotspots contacted"
                }
            },
            "validation_rules": {
                "high_confidence": "iptm_score >= 0.7 AND interface_pae <= 5.0",
                "acceptable": "iptm_score >= 0.5 AND hotspot_coverage_percent >= 50.0",
                "failed": "iptm_score < 0.5 OR interface_pae > 10.0"
            }
        }

    @staticmethod
    def get_integration_spec() -> Dict[str, Any]:
        """SPEC: OpenClaw integration requirements"""
        return {
            "message_compatibility": {
                "required_message_types": [
                    "synthesis_request",
                    "flood_threat_detected",
                    "emergency_stop",
                    "memory_query"
                ],
                "output_message_types": [
                    "synthesis_progress",
                    "countermeasure_ready",
                    "synthesis_results"
                ]
            },
            "biosecurity_integration": {
                "screening_enabled": True,
                "threat_database_size": 6,
                "screening_methods": [
                    "structural_homology_screening",
                    "dangerous_motif_detection"
                ]
            },
            "memory_integration": {
                "unibase_enabled": True,
                "enhanced_logging": True,
                "metrics_included": ["iptm_score", "interface_pae", "hotspot_coverage"]
            }
        }

    @staticmethod
    def get_method_signature_specs() -> Dict[str, Any]:
        """SPEC: Required method signatures for compliance"""
        return {
            "run_primary_function": {
                "async": True,
                "returns": "Dict[str, Any]",
                "required_fields": [
                    "status", "iptm_score", "interface_pae",
                    "hotspot_coverage_percent", "method"
                ]
            },
            "_run_aminoanalytica_pipeline": {
                "async": True,
                "workflow_decorated": True,
                "returns": "Dict[str, Any]",
                "integrates_biosecurity": True
            },
            "log_binder_result_enhanced": {
                "parameters": ["log_data: Dict[str, Any]"],
                "returns": "str",
                "aminoanalytica_aware": True
            }
        }
