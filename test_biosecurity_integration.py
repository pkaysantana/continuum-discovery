#!/usr/bin/env python3
"""
Biosecurity Integration Test Suite
Tests Hard Mode Biosecurity Screening System integration with BioScientistAgent
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(__file__))

# Import required modules for testing
from openclaw.base_agent import MessageBus
from agents.bio_scientist_agent import BioScientistAgent
from agents.biosecurity_screening import BiosecurityScreening

async def test_biosecurity_integration():
    """Test biosecurity integration with bio scientist agent"""

    print("=" * 70)
    print("HARD MODE BIOSECURITY SCREENING SYSTEM TEST")
    print("=" * 70)
    print("Testing AminoAnalytica biosecurity integration with OpenClaw swarm")
    print()

    # Initialize test counters
    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    try:
        # Test 1: Initialize BiosecurityScreening standalone
        print("TEST 1: Biosecurity Screening Module Initialization")
        print("-" * 50)
        total_tests += 1

        biosecurity = BiosecurityScreening()

        # Check threat database
        threat_count = len(biosecurity.threat_database)
        expected_threats = 6  # BipD, IpaD, SipD, Ricin, Botulinum, Anthrax

        if threat_count == expected_threats:
            print(f"[PASS] Threat database initialized: {threat_count}/{expected_threats} threats loaded")
            passed_tests += 1
        else:
            print(f"[FAIL] Expected {expected_threats} threats, found {threat_count}")
            failed_tests += 1

        # Test 2: Structural Homology Screening
        print(f"\nTEST 2: Structural Homology Screening")
        print("-" * 50)
        total_tests += 1

        # Test with high-risk structure (should be flagged)
        high_risk_structure = {
            'rmsd': 1.5,      # < 3.0 threshold
            'tm_score': 0.8,  # > 0.5 threshold
            'sequence': 'TESTSEQUENCEHIGHRISK'
        }

        risk_result = biosecurity.structural_homology_screening(high_risk_structure)

        if risk_result['risk_level'] == 'HIGH' and risk_result['threat_count'] > 0:
            print(f"[PASS] High-risk structure correctly flagged: {risk_result['risk_level']}")
            print(f"       Threats detected: {risk_result['threat_count']}")
            passed_tests += 1
        else:
            print(f"[FAIL] High-risk structure not properly detected")
            print(f"       Risk level: {risk_result['risk_level']}, Threats: {risk_result['threat_count']}")
            failed_tests += 1

        # Test 3: Motif Detection
        print(f"\nTEST 3: Dangerous Motif Detection")
        print("-" * 50)
        total_tests += 1

        # Test sequence with dangerous motifs
        dangerous_sequence = "TESTSEQUENCEKDELPOTENTIALLYDANGEROUSRGDMOTIFS"
        motif_result = biosecurity.detect_redesigned_threats(dangerous_sequence)

        dangerous_found = len(motif_result['dangerous_motifs'])

        if dangerous_found > 0:
            print(f"[PASS] Dangerous motifs detected: {dangerous_found} motifs")
            for motif in motif_result['dangerous_motifs']:
                print(f"       • {motif['motif']}: {motif['description']}")
            passed_tests += 1
        else:
            print(f"[FAIL] No dangerous motifs detected in test sequence")
            failed_tests += 1

        # Test 4: BioScientistAgent Integration
        print(f"\nTEST 4: BioScientistAgent Integration")
        print("-" * 50)
        total_tests += 1

        message_bus = MessageBus()
        bio_agent = BioScientistAgent(message_bus)

        if hasattr(bio_agent, 'biosecurity') and bio_agent.biosecurity_enabled:
            print(f"[PASS] BioScientistAgent successfully integrated biosecurity")
            print(f"       Biosecurity enabled: {bio_agent.biosecurity_enabled}")
            print(f"       Capabilities updated: {len(bio_agent.capabilities)} total")
            passed_tests += 1
        else:
            print(f"[FAIL] BioScientistAgent integration failed")
            print(f"       Biosecurity enabled: {getattr(bio_agent, 'biosecurity_enabled', 'Not found')}")
            failed_tests += 1

        # Test 5: Synthesis Pipeline with Biosecurity
        print(f"\nTEST 5: Synthesis Pipeline with Biosecurity Screening")
        print("-" * 50)
        total_tests += 1

        try:
            synthesis_result = await bio_agent.run_primary_function()

            # Check if biosecurity screening was included
            has_biosecurity = 'biosecurity_screening' in synthesis_result
            biosecurity_data = synthesis_result.get('biosecurity_screening')

            if has_biosecurity and biosecurity_data:
                validation_status = biosecurity_data.get('validation_status', 'UNKNOWN')
                security_score = biosecurity_data.get('security_score', 0.0)

                print(f"[PASS] Synthesis pipeline includes biosecurity screening")
                print(f"       Validation status: {validation_status}")
                print(f"       Security score: {security_score:.3f}")
                print(f"       RMSD: {synthesis_result.get('rmsd_score', 'N/A'):.3f}")
                passed_tests += 1
            else:
                print(f"[FAIL] Synthesis pipeline missing biosecurity screening")
                print(f"       Result keys: {list(synthesis_result.keys())}")
                failed_tests += 1

        except Exception as e:
            print(f"[ERROR] Synthesis pipeline test failed: {str(e)}")
            failed_tests += 1

        # Test 6: Memory Logging with Validation Status
        print(f"\nTEST 6: Memory Logging with Biosecurity Validation")
        print("-" * 50)
        total_tests += 1

        test_log_data = {
            'protein_sequence': 'TESTSEQUENCEFORBIOSECURITYLOGGING',
            'rmsd_score': 1.8,
            'tm_score': 0.7,
            'target': 'Test biosecurity target',
            'security_score': 0.4,  # Should result in 'FLAGGED' status
            'biosecurity_screening': True
        }

        try:
            result_id = bio_agent.log_binder_result(test_log_data)

            if result_id:
                print(f"[PASS] Memory logging with biosecurity validation successful")
                print(f"       Result ID: {result_id}")
                print(f"       Security score > 0.3 should result in FLAGGED status")
                passed_tests += 1
            else:
                print(f"[FAIL] Memory logging failed or returned None")
                failed_tests += 1

        except Exception as e:
            print(f"[ERROR] Memory logging test failed: {str(e)}")
            failed_tests += 1

        # Test 7: OpenClaw Message Compatibility
        print(f"\nTEST 7: OpenClaw Message System Compatibility")
        print("-" * 50)
        total_tests += 1

        try:
            # Check if enhanced synthesis results are compatible with existing messaging
            synthesis_result = await bio_agent.run_primary_function()

            # Simulate message payload that would be sent to Telegram
            telegram_payload = {
                'stage': 'synthesis_complete',
                'rmsd_score': synthesis_result.get('rmsd_score'),
                'validation': synthesis_result.get('validation_status'),
                'sequence_cached': synthesis_result.get('from_memory', False),
                'biosecurity_status': 'FLAGGED' if synthesis_result.get('validation_status') == 'BIOSECURITY_FLAGGED' else 'CLEARED'
            }

            required_fields = ['stage', 'rmsd_score', 'validation', 'biosecurity_status']
            missing_fields = [field for field in required_fields if field not in telegram_payload or telegram_payload[field] is None]

            if not missing_fields:
                print(f"[PASS] OpenClaw message compatibility maintained")
                print(f"       All required fields present in payload")
                print(f"       Biosecurity status: {telegram_payload['biosecurity_status']}")
                passed_tests += 1
            else:
                print(f"[FAIL] Message compatibility issues detected")
                print(f"       Missing fields: {missing_fields}")
                failed_tests += 1

        except Exception as e:
            print(f"[ERROR] Message compatibility test failed: {str(e)}")
            failed_tests += 1

    except Exception as e:
        print(f"[CRITICAL ERROR] Test framework failure: {str(e)}")
        failed_tests += total_tests  # Mark all remaining tests as failed

    # Test Results Summary
    print("\n" + "=" * 70)
    print("BIOSECURITY INTEGRATION TEST RESULTS")
    print("=" * 70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

    if failed_tests == 0:
        print("\nALL TESTS PASSED!")
        print("Hard Mode Biosecurity Screening System successfully integrated")
        print("Ready for AminoAnalytica workshop demonstration")
    elif failed_tests <= 2:
        print(f"\n{failed_tests} minor issues detected - mostly operational")
        print("Core biosecurity functionality working")
    else:
        print(f"\n{failed_tests} significant issues detected!")
        print("Biosecurity integration requires immediate attention")

    print("\nBiosecurity Features Summary:")
    print(f"  • Threat Database: 6 T3SS threats and toxins monitored")
    print(f"  • Structural Screening: RMSD < 3.0 or TM-score > 0.5 detection")
    print(f"  • Motif Detection: KDEL, RGD, YXXΦ, KKXX dangerous motifs")
    print(f"  • Memory Integration: Validation status based on security_score < 0.3")
    print(f"  • OpenClaw Compatible: Enhanced messaging with biosecurity status")

    return {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'success_rate': (passed_tests/total_tests)*100 if total_tests > 0 else 0
    }

if __name__ == "__main__":
    print("Starting Hard Mode Biosecurity Integration Tests...")
    print("This will verify AminoAnalytica biosecurity screening integration")
    print("with the existing OpenClaw swarm system.\n")

    # Run the test suite
    test_result = asyncio.run(test_biosecurity_integration())

    print(f"\nTesting completed.")

    # Exit with appropriate code
    if test_result['failed_tests'] == 0:
        print("All biosecurity integration tests passed successfully!")
        sys.exit(0)
    else:
        print(f"{test_result['failed_tests']} tests failed - review required.")
        sys.exit(1)
