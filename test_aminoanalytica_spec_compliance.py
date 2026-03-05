#!/usr/bin/env python3
"""
AminoAnalytica Workshop Spec Compliance Test Suite
Spec-Driven Development Validation for bio_scientist_agent.py
"""

import sys
import os
import asyncio
import inspect
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(__file__))

# Import specifications
from specs.aminoanalytica_workshop_specs import (
    AminoAnalyticaWorkshopSpecs,
    PipelineStage,
    MetricType,
    WorkshopTarget,
    PipelineSpec,
    CapabilitySpec
)

# Import implementation
from openclaw.base_agent import MessageBus
from agents.bio_scientist_agent import BioScientistAgent

class SpecComplianceValidator:
    """Validates implementation against AminoAnalytica workshop specifications"""

    def __init__(self):
        self.specs = AminoAnalyticaWorkshopSpecs()
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0

    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log individual test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1

        status = "PASS" if passed else "FAIL"
        self.test_results.append({
            'test': test_name,
            'status': status,
            'details': details
        })
        print(f"[{status}] {test_name}: {details}")

    async def validate_workshop_target_spec(self, agent: BioScientistAgent) -> bool:
        """SPEC VALIDATION: Workshop target configuration"""
        print("\n=== SPEC VALIDATION: Workshop Target ===")

        target_spec = self.specs.get_workshop_target_spec()

        # Test 1: Agent has workshop targets configured
        has_workshop_targets = hasattr(agent, 'workshop_targets')
        self.log_test(
            "Workshop Targets Configured",
            has_workshop_targets,
            f"workshop_targets attribute: {'present' if has_workshop_targets else 'missing'}"
        )

        if not has_workshop_targets:
            return False

        # Test 2: 7K43 target exists
        has_7k43 = '7K43' in agent.workshop_targets
        self.log_test(
            "7K43 Target Exists",
            has_7k43,
            f"7K43 in workshop_targets: {has_7k43}"
        )

        if not has_7k43:
            return False

        target = agent.workshop_targets['7K43']

        # Test 3: PDB ID matches spec
        pdb_matches = target['pdb_id'] == target_spec.pdb_id
        self.log_test(
            "PDB ID Specification",
            pdb_matches,
            f"Expected: {target_spec.pdb_id}, Got: {target['pdb_id']}"
        )

        # Test 4: Chain matches spec
        chain_matches = target['chain'] == target_spec.chain
        self.log_test(
            "Chain Specification",
            chain_matches,
            f"Expected: {target_spec.chain}, Got: {target['chain']}"
        )

        # Test 5: Hotspots match spec
        hotspots_match = target['hotspots'] == target_spec.hotspots
        self.log_test(
            "Hotspot Specification",
            hotspots_match,
            f"Expected: {target_spec.hotspots}, Got: {target['hotspots']}"
        )

        # Test 6: Description matches spec
        desc_matches = target['description'] == target_spec.description
        self.log_test(
            "Description Specification",
            desc_matches,
            f"Expected: {target_spec.description}, Got: {target['description']}"
        )

        return all([has_workshop_targets, has_7k43, pdb_matches, chain_matches, hotspots_match, desc_matches])

    async def validate_capability_spec(self, agent: BioScientistAgent) -> bool:
        """SPEC VALIDATION: Agent capabilities"""
        print("\n=== SPEC VALIDATION: Agent Capabilities ===")

        capability_spec = self.specs.get_capability_spec()

        # Test 1: Has capabilities attribute
        has_capabilities = hasattr(agent, 'capabilities')
        self.log_test(
            "Capabilities Attribute",
            has_capabilities,
            f"capabilities attribute: {'present' if has_capabilities else 'missing'}"
        )

        if not has_capabilities:
            return False

        # Test 2: Core capabilities present
        core_missing = []
        for cap in capability_spec.core_capabilities:
            if cap not in agent.capabilities:
                core_missing.append(cap)

        core_complete = len(core_missing) == 0
        self.log_test(
            "Core Capabilities Complete",
            core_complete,
            f"Missing: {core_missing if core_missing else 'None'}"
        )

        # Test 3: AminoAnalytica capabilities present
        aa_missing = []
        for cap in capability_spec.aminoanalytica_capabilities:
            if cap not in agent.capabilities:
                aa_missing.append(cap)

        aa_complete = len(aa_missing) == 0
        self.log_test(
            "AminoAnalytica Capabilities Complete",
            aa_complete,
            f"Missing: {aa_missing if aa_missing else 'None'}"
        )

        # Test 4: Integration capabilities present
        integration_missing = []
        for cap in capability_spec.integration_capabilities:
            if cap not in agent.capabilities:
                integration_missing.append(cap)

        integration_complete = len(integration_missing) == 0
        self.log_test(
            "Integration Capabilities Complete",
            integration_complete,
            f"Missing: {integration_missing if integration_missing else 'None'}"
        )

        return all([has_capabilities, core_complete, aa_complete, integration_complete])

    async def validate_pipeline_spec(self, agent: BioScientistAgent) -> bool:
        """SPEC VALIDATION: Pipeline implementation"""
        print("\n=== SPEC VALIDATION: Pipeline Implementation ===")

        # Test 1: AminoAnalytica pipeline enabled
        pipeline_enabled = getattr(agent, 'pipeline_enabled', False)
        self.log_test(
            "Pipeline Enabled",
            pipeline_enabled,
            f"pipeline_enabled: {pipeline_enabled}"
        )

        # Test 2: AminoAnalytica instance present
        has_pipeline = hasattr(agent, 'aminoanalytica') and agent.aminoanalytica is not None
        self.log_test(
            "Pipeline Instance Present",
            has_pipeline,
            f"aminoanalytica instance: {'present' if has_pipeline else 'missing'}"
        )

        # Test 3: Pipeline has run_complete_pipeline method
        if has_pipeline:
            has_complete_method = hasattr(agent.aminoanalytica, 'run_complete_pipeline')
            self.log_test(
                "Complete Pipeline Method",
                has_complete_method,
                f"run_complete_pipeline method: {'present' if has_complete_method else 'missing'}"
            )
        else:
            has_complete_method = False
            self.log_test(
                "Complete Pipeline Method",
                False,
                "Cannot test - pipeline instance missing"
            )

        return all([pipeline_enabled, has_pipeline, has_complete_method])

    async def validate_method_signatures(self, agent: BioScientistAgent) -> bool:
        """SPEC VALIDATION: Required method signatures"""
        print("\n=== SPEC VALIDATION: Method Signatures ===")

        method_specs = self.specs.get_method_signature_specs()

        # Test 1: run_primary_function exists and is async
        has_primary = hasattr(agent, 'run_primary_function')
        primary_async = False
        if has_primary:
            primary_async = inspect.iscoroutinefunction(agent.run_primary_function)

        self.log_test(
            "run_primary_function Signature",
            has_primary and primary_async,
            f"Present: {has_primary}, Async: {primary_async}"
        )

        # Test 2: _run_aminoanalytica_pipeline exists and is async
        has_aa_pipeline = hasattr(agent, '_run_aminoanalytica_pipeline')
        aa_pipeline_async = False
        if has_aa_pipeline:
            aa_pipeline_async = inspect.iscoroutinefunction(agent._run_aminoanalytica_pipeline)

        self.log_test(
            "_run_aminoanalytica_pipeline Signature",
            has_aa_pipeline and aa_pipeline_async,
            f"Present: {has_aa_pipeline}, Async: {aa_pipeline_async}"
        )

        # Test 3: log_binder_result_enhanced exists
        has_enhanced_log = hasattr(agent, 'log_binder_result_enhanced')
        self.log_test(
            "log_binder_result_enhanced Signature",
            has_enhanced_log,
            f"Present: {has_enhanced_log}"
        )

        return all([has_primary and primary_async, has_aa_pipeline and aa_pipeline_async, has_enhanced_log])

    async def validate_integration_spec(self, agent: BioScientistAgent) -> bool:
        """SPEC VALIDATION: OpenClaw integration"""
        print("\n=== SPEC VALIDATION: Integration Requirements ===")

        integration_spec = self.specs.get_integration_spec()

        # Test 1: Biosecurity integration
        biosecurity_enabled = getattr(agent, 'biosecurity_enabled', False)
        has_biosecurity = hasattr(agent, 'biosecurity') and agent.biosecurity is not None

        self.log_test(
            "Biosecurity Integration",
            biosecurity_enabled and has_biosecurity,
            f"Enabled: {biosecurity_enabled}, Instance: {has_biosecurity}"
        )

        # Test 2: Memory integration
        memory_active = getattr(agent, 'memory_active', False)
        has_memory = hasattr(agent, 'memory') and agent.memory is not None

        self.log_test(
            "Memory Integration",
            memory_active and has_memory,
            f"Active: {memory_active}, Instance: {has_memory}"
        )

        # Test 3: Message handling methods
        required_handlers = ['handle_flood_threat_detected', 'handle_synthesis_request', 'handle_emergency_stop']
        missing_handlers = []

        for handler in required_handlers:
            if not hasattr(agent, handler):
                missing_handlers.append(handler)

        handlers_complete = len(missing_handlers) == 0
        self.log_test(
            "Message Handlers Complete",
            handlers_complete,
            f"Missing: {missing_handlers if missing_handlers else 'None'}"
        )

        return all([biosecurity_enabled and has_biosecurity, memory_active and has_memory, handlers_complete])

    async def validate_output_spec(self, agent: BioScientistAgent) -> bool:
        """SPEC VALIDATION: Output format compliance"""
        print("\n=== SPEC VALIDATION: Output Format ===")

        scoring_spec = self.specs.get_scoring_spec()
        required_metrics = list(scoring_spec['primary_metrics'].keys())

        try:
            # Run a synthesis to test output format
            print("[TEST] Running synthesis for output validation...")
            synthesis_result = await agent.run_primary_function()

            # Test 1: Status field present
            has_status = 'status' in synthesis_result
            self.log_test(
                "Output Status Field",
                has_status,
                f"status field: {'present' if has_status else 'missing'}"
            )

            # Test 2: Required metrics present
            missing_metrics = []
            for metric in required_metrics:
                if metric not in synthesis_result:
                    missing_metrics.append(metric)

            metrics_complete = len(missing_metrics) == 0
            self.log_test(
                "Required Metrics Present",
                metrics_complete,
                f"Missing: {missing_metrics if missing_metrics else 'None'}"
            )

            # Test 3: Method field indicates AminoAnalytica
            method_field = synthesis_result.get('method', '')
            aminoanalytica_method = 'aminoanalytica' in method_field.lower()
            self.log_test(
                "AminoAnalytica Method Indicated",
                aminoanalytica_method,
                f"method: '{method_field}'"
            )

            # Test 4: Metric types and ranges
            metrics_valid = True
            metric_details = []

            for metric in required_metrics:
                if metric in synthesis_result:
                    value = synthesis_result[metric]
                    spec = scoring_spec['primary_metrics'][metric]

                    if isinstance(value, (int, float)):
                        min_val, max_val = spec['range']
                        in_range = min_val <= value <= max_val
                        metric_details.append(f"{metric}: {value} ({'valid' if in_range else 'invalid range'})")
                        if not in_range:
                            metrics_valid = False
                    else:
                        metric_details.append(f"{metric}: {type(value)} (invalid type)")
                        metrics_valid = False

            self.log_test(
                "Metric Types and Ranges Valid",
                metrics_valid,
                f"Details: {'; '.join(metric_details)}"
            )

            return all([has_status, metrics_complete, aminoanalytica_method, metrics_valid])

        except Exception as e:
            self.log_test(
                "Output Format Validation",
                False,
                f"Synthesis failed: {str(e)}"
            )
            return False

    async def run_complete_validation(self) -> Dict[str, Any]:
        """Run complete spec-driven validation suite"""
        print("=" * 80)
        print("AMINOANALYTICA WORKSHOP SPEC COMPLIANCE VALIDATION")
        print("=" * 80)
        print(f"Testing implementation against formal specifications")
        print(f"Timestamp: {datetime.now().isoformat()}")

        # Initialize agent
        message_bus = MessageBus()
        agent = BioScientistAgent(message_bus)

        # Run all validation tests
        validation_results = {}

        validation_results['workshop_target'] = await self.validate_workshop_target_spec(agent)
        validation_results['capabilities'] = await self.validate_capability_spec(agent)
        validation_results['pipeline'] = await self.validate_pipeline_spec(agent)
        validation_results['method_signatures'] = await self.validate_method_signatures(agent)
        validation_results['integration'] = await self.validate_integration_spec(agent)
        validation_results['output_format'] = await self.validate_output_spec(agent)

        # Calculate overall compliance
        total_sections = len(validation_results)
        passed_sections = sum(1 for result in validation_results.values() if result)
        overall_compliance = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0

        print("\n" + "=" * 80)
        print("SPEC COMPLIANCE VALIDATION RESULTS")
        print("=" * 80)
        print(f"Individual Tests: {self.passed_tests}/{self.total_tests} ({overall_compliance:.1f}%)")
        print(f"Specification Sections: {passed_sections}/{total_sections}")

        print("\nSection Results:")
        for section, passed in validation_results.items():
            status = "COMPLIANT" if passed else "NON-COMPLIANT"
            print(f"  {section.replace('_', ' ').title()}: {status}")

        all_compliant = all(validation_results.values())
        final_status = "FULLY SPEC COMPLIANT" if all_compliant else "SPEC COMPLIANCE ISSUES"
        print(f"\nOVERALL STATUS: {final_status}")

        if not all_compliant:
            print("\nFailed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test']}: {result['details']}")

        return {
            'overall_compliant': all_compliant,
            'compliance_percentage': overall_compliance,
            'section_results': validation_results,
            'test_details': self.test_results,
            'passed_tests': self.passed_tests,
            'total_tests': self.total_tests
        }

async def main():
    """Run spec compliance validation"""
    validator = SpecComplianceValidator()
    results = await validator.run_complete_validation()

    # Return appropriate exit code
    exit_code = 0 if results['overall_compliant'] else 1
    print(f"\nValidation completed with exit code: {exit_code}")
    return exit_code

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
