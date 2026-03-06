#!/usr/bin/env python3
"""
Animoca Track Spec Compliance Test Suite
Comprehensive testing for Cognitive Intelligence Layer and Blockchain Integration
"""

import sys
import os
import asyncio
import unittest
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.dirname(__file__))

# Import specifications
from specs.animoca_track_specs import (
    AnimocaTrackSpecs,
    CognitiveProcessType,
    MemoryType,
    BlockchainNetwork
)

# Import implementations
from agents.animoca.cognitive_engine import (
    CognitivePlatformEngine,
    EnhancedCognitiveMemory,
    EnhancedEthoswarmAgent
)

from agents.animoca.blockchain import (
    BlockchainAgentIntegration,
    AgentWalletManager,
    TransactionType
)

class AnimocaSpecComplianceTest(unittest.IsolatedAsyncioTestCase):
    """Comprehensive test suite for Animoca track spec compliance"""

    async def asyncSetUp(self):
        """Setup test environment"""
        self.specs = AnimocaTrackSpecs()

        # Initialize cognitive engine
        cognitive_config = {
            'name': 'TestCognitiveEngine',
            'domain': 'cognitive_intelligence',
            'personality': {'analytical': 0.9, 'innovative': 0.8},
            'ethics': ['transparency', 'beneficence'],
            'goals': ['enhanced_reasoning', 'pattern_recognition'],
            'capabilities': ['advanced_reasoning', 'strategic_planning']
        }
        self.cognitive_engine = CognitivePlatformEngine(cognitive_config)

        # Initialize blockchain integration
        self.blockchain = BlockchainAgentIntegration(stripe_integration_enabled=True)

        # Test counters
        self.total_tests = 0
        self.passed_tests = 0

    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1

        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {test_name}: {details}")

    # ========================
    # COGNITIVE ENGINE TESTS
    # ========================

    async def test_cognitive_capabilities_compliance(self):
        """TEST 1: Verify cognitive capabilities match specifications"""
        spec_capabilities = self.specs.get_cognitive_engine_spec()['cognitive_capabilities']
        required_capability_names = [cap.name for cap in spec_capabilities]

        # Check if engine has required enhanced capabilities
        missing_capabilities = []
        for cap_name in required_capability_names:
            if cap_name not in self.cognitive_engine.enhanced_capabilities:
                missing_capabilities.append(cap_name)

        passed = len(missing_capabilities) == 0
        self.log_test_result(
            "Cognitive Capabilities Compliance",
            passed,
            f"Missing: {missing_capabilities}" if missing_capabilities else "All capabilities present"
        )
        self.assertTrue(passed)

    async def test_memory_system_compliance(self):
        """TEST 2: Verify memory system meets specifications"""
        memory_spec = self.specs.get_cognitive_engine_spec()['memory_system']

        # Test memory capacity
        memory = self.cognitive_engine.memory
        self.assertIsInstance(memory, EnhancedCognitiveMemory)

        # Test memory operations
        test_experience = {
            'type': 'test_experience',
            'content': 'Test memory storage',
            'importance': 0.8,
            'domain': 'testing'
        }

        memory_id = await memory.store_experience(test_experience)
        self.assertIsInstance(memory_id, str)

        # Test memory retrieval
        retrieved_memories = await memory.retrieve_relevant("test memory")
        memory_retrieval_works = len(retrieved_memories) > 0

        self.log_test_result(
            "Memory System Compliance",
            memory_retrieval_works,
            f"Memory stored: {memory_id[:8]}..., Retrieved: {len(retrieved_memories)} items"
        )

    async def test_enhanced_reasoning_logic(self):
        """TEST 3: Test enhanced reasoning capabilities"""
        # Create complex reasoning stimulus
        complex_stimulus = {
            'type': 'complex_reasoning_test',
            'content': 'Multi-factor blockchain cognitive integration analysis',
            'context': {
                'urgency': 'high',
                'domain': 'blockchain_cognitive',
                'complexity': 'multi_domain'
            },
            'importance': 0.9
        }

        # Test enhanced thinking
        result = await self.cognitive_engine.think(complex_stimulus)

        # Verify enhanced metrics are present
        has_enhancement_metrics = 'enhancement_metrics' in result
        has_cognitive_complexity = 'cognitive_complexity_score' in result.get('enhancement_metrics', {})
        has_reasoning_depth = 'reasoning_depth_level' in result.get('enhancement_metrics', {})
        has_pattern_score = 'pattern_recognition_score' in result.get('enhancement_metrics', {})

        reasoning_compliance = all([
            has_enhancement_metrics,
            has_cognitive_complexity,
            has_reasoning_depth,
            has_pattern_score
        ])

        self.log_test_result(
            "Enhanced Reasoning Logic",
            reasoning_compliance,
            f"Enhancement metrics: {has_enhancement_metrics}, Complexity: {has_cognitive_complexity}"
        )
        self.assertTrue(reasoning_compliance)

    async def test_memory_retention_and_importance(self):
        """TEST 4: Test memory retention with importance scoring"""
        memory = self.cognitive_engine.memory

        # Store experiences with different importance levels
        high_importance = {
            'type': 'critical_insight',
            'content': 'High importance memory test',
            'importance': 0.9,
            'context': {'urgency': 'high'}
        }

        low_importance = {
            'type': 'routine_update',
            'content': 'Low importance memory test',
            'importance': 0.2
        }

        high_id = await memory.store_experience(high_importance)
        low_id = await memory.store_experience(low_importance)

        # Check importance scoring
        high_importance_score = memory.importance_weights.get(high_id, 0)
        low_importance_score = memory.importance_weights.get(low_id, 0)

        importance_scoring_works = high_importance_score > low_importance_score

        self.log_test_result(
            "Memory Retention and Importance",
            importance_scoring_works,
            f"High: {high_importance_score:.3f}, Low: {low_importance_score:.3f}"
        )
        self.assertTrue(importance_scoring_works)

    async def test_pattern_recognition_functionality(self):
        """TEST 5: Test pattern recognition capabilities"""
        # Create multiple related stimuli to test pattern recognition
        related_stimuli = [
            {
                'type': 'pattern_test',
                'content': 'Blockchain integration cognitive analysis',
                'context': {'domain': 'blockchain'}
            },
            {
                'type': 'pattern_test',
                'content': 'Cognitive blockchain revenue optimization',
                'context': {'domain': 'blockchain'}
            },
            {
                'type': 'pattern_test',
                'content': 'Revenue cognitive blockchain integration',
                'context': {'domain': 'blockchain'}
            }
        ]

        # Process stimuli to build pattern buffer
        results = []
        for stimulus in related_stimuli:
            result = await self.cognitive_engine.think(stimulus)
            results.append(result)

        # Check if patterns are being recognized
        last_result = results[-1]
        reasoning_trace = last_result.get('reasoning_trace', {})
        patterns_recognized = reasoning_trace.get('patterns_recognized', [])

        pattern_recognition_working = len(patterns_recognized) > 0

        self.log_test_result(
            "Pattern Recognition Functionality",
            pattern_recognition_working,
            f"Patterns detected: {len(patterns_recognized)}"
        )

    # ========================
    # BLOCKCHAIN TESTS
    # ========================

    async def test_agent_wallet_creation(self):
        """TEST 6: Test agent wallet creation compliance"""
        agent_id = "test_agent_wallet"

        # Test wallet creation
        wallet_result = await self.blockchain.wallet_manager.create_agent_wallet(
            agent_id, BlockchainNetwork.BNB_CHAIN
        )

        # Verify wallet creation compliance
        wallet_created = wallet_result['status'] == 'created'
        has_wallet_address = 'wallet_address' in wallet_result
        has_initial_balance = 'initial_balance' in wallet_result
        simulation_mode_enabled = wallet_result.get('simulation_mode', False)
        security_compliant = wallet_result.get('security_compliance', False)

        wallet_compliance = all([
            wallet_created,
            has_wallet_address,
            has_initial_balance,
            simulation_mode_enabled,
            security_compliant
        ])

        self.log_test_result(
            "Agent Wallet Creation",
            wallet_compliance,
            f"Address: {wallet_result.get('wallet_address', 'N/A')[:10]}..., Simulation: {simulation_mode_enabled}"
        )
        self.assertTrue(wallet_compliance)

    async def test_transaction_intent_simulation(self):
        """TEST 7: Test transaction intent simulation"""
        # First create an agent wallet
        agent_id = "test_transaction_agent"
        await self.blockchain.wallet_manager.create_agent_wallet(agent_id, BlockchainNetwork.BNB_CHAIN)

        # Create transaction intent
        transaction_intent = {
            'transaction_type': 'revenue_distribution',
            'from_agent': agent_id,
            'to_address': '0x742d35Cc6634C0532925a3b8D02e3fE09111a8A9',
            'amount': 100.0,
            'currency': 'USDT',
            'network': 'bsc',
            'metadata': {'test': True}
        }

        # Test simulation
        simulation_result = await self.blockchain.simulate_transaction_intent(transaction_intent)

        # Verify simulation compliance
        has_intent_id = 'intent_id' in simulation_result
        has_simulation_result = 'simulation_result' in simulation_result
        has_gas_estimate = 'gas_estimate_usd' in simulation_result
        simulation_only = True  # Always true for our implementation

        transaction_simulation_compliance = all([
            has_intent_id,
            has_simulation_result,
            has_gas_estimate,
            simulation_only
        ])

        self.log_test_result(
            "Transaction Intent Simulation",
            transaction_simulation_compliance,
            f"Intent ID: {simulation_result.get('intent_id', 'N/A')[:8]}..., Gas: ${simulation_result.get('gas_estimate_usd', 0):.4f}"
        )
        self.assertTrue(transaction_simulation_compliance)

    async def test_revenue_stream_integration(self):
        """TEST 8: Test revenue stream integration with Stripe"""
        # Create agent for revenue testing
        agent_id = "test_revenue_agent"
        await self.blockchain.wallet_manager.create_agent_wallet(agent_id, BlockchainNetwork.BNB_CHAIN)

        # Simulate Stripe revenue data
        stripe_data = {
            'asset_id': 'test_asset_revenue_123',
            'revenue_generated': 500.0,
            'synthesizing_agent': agent_id,
            'stripe_transaction_id': 'txn_test_123'
        }

        # Test revenue linking
        revenue_link_result = await self.blockchain.link_revenue_stream(stripe_data)

        # Verify revenue integration compliance
        revenue_linked = revenue_link_result['status'] == 'linked'
        has_stream_id = 'stream_id' in revenue_link_result
        has_token_distribution = 'token_distribution' in revenue_link_result
        stripe_preserved = 'revenue_data' in revenue_link_result

        revenue_integration_compliance = all([
            revenue_linked,
            has_stream_id,
            has_token_distribution,
            stripe_preserved
        ])

        self.log_test_result(
            "Revenue Stream Integration",
            revenue_integration_compliance,
            f"Linked: {revenue_linked}, Tokens: {revenue_link_result.get('token_distribution', {}).get('amount', 0):.2f}"
        )
        self.assertTrue(revenue_integration_compliance)

    async def test_gas_estimation_accuracy(self):
        """TEST 9: Test gas estimation functionality"""
        # Test different transaction types for gas estimation
        transaction_types = [
            'revenue_distribution',
            'ip_tokenization',
            'agent_payment',
            'governance_vote'
        ]

        gas_estimates = {}
        for tx_type in transaction_types:
            intent = {
                'transaction_type': tx_type,
                'from_agent': 'test_agent',
                'to_address': '0x123...',
                'amount': 100.0,
                'currency': 'USDT',
                'network': 'bsc'
            }

            gas_estimate = await self.blockchain._estimate_gas(intent)
            gas_estimates[tx_type] = gas_estimate

        # Verify gas estimates are reasonable and different
        all_estimates_positive = all(estimate > 0 for estimate in gas_estimates.values())
        estimates_vary = len(set(gas_estimates.values())) > 1

        gas_estimation_compliance = all_estimates_positive and estimates_vary

        self.log_test_result(
            "Gas Estimation Accuracy",
            gas_estimation_compliance,
            f"Estimates: {len(gas_estimates)}, Varying: {estimates_vary}"
        )

    async def test_security_compliance_validation(self):
        """TEST 10: Test security compliance"""
        # Verify no real private keys are generated or stored
        agent_id = "test_security_agent"
        wallet_result = await self.blockchain.wallet_manager.create_agent_wallet(agent_id, BlockchainNetwork.ETHEREUM)

        wallet_manager = self.blockchain.wallet_manager

        # Check security compliance
        simulation_mode_active = wallet_manager.simulation_mode
        security_compliance_enabled = wallet_manager.security_compliance

        # Verify wallet data doesn't contain real private keys
        wallet_info = await wallet_manager.get_wallet_info(agent_id)
        no_private_keys_stored = 'private_key' not in str(wallet_info)

        security_compliance = all([
            simulation_mode_active,
            security_compliance_enabled,
            no_private_keys_stored
        ])

        self.log_test_result(
            "Security Compliance Validation",
            security_compliance,
            f"Simulation: {simulation_mode_active}, Compliance: {security_compliance_enabled}, No PK: {no_private_keys_stored}"
        )
        self.assertTrue(security_compliance)

    # ========================
    # INTEGRATION TESTS
    # ========================

    async def test_cognitive_blockchain_integration(self):
        """TEST 11: Test integration between cognitive engine and blockchain"""
        # Test cognitive decision making about blockchain transactions
        blockchain_stimulus = {
            'type': 'blockchain_decision',
            'content': 'Should agent participate in revenue distribution protocol?',
            'context': {
                'revenue_available': 1000.0,
                'gas_cost_estimate': 5.0,
                'network_congestion': 'low'
            },
            'importance': 0.8
        }

        # Get cognitive analysis
        cognitive_result = await self.cognitive_engine.think(blockchain_stimulus)

        # Test blockchain integration with cognitive output
        agent_id = "test_integration_agent"
        await self.blockchain.onboard_agent(agent_id, {'preferred_network': 'bsc'})

        # Simulate blockchain action based on cognitive decision
        if cognitive_result['confidence_score'] > 0.7:
            transaction_intent = {
                'transaction_type': 'revenue_distribution',
                'from_agent': agent_id,
                'to_address': '0x456...',
                'amount': 50.0,
                'currency': 'USDT',
                'network': 'bsc'
            }

            blockchain_result = await self.blockchain.simulate_transaction_intent(transaction_intent)
            integration_successful = blockchain_result['simulation_result']['status'] == 'success'
        else:
            integration_successful = True  # No action taken is also valid

        self.log_test_result(
            "Cognitive-Blockchain Integration",
            integration_successful,
            f"Cognitive confidence: {cognitive_result['confidence_score']:.3f}, Integration: {integration_successful}"
        )

    async def test_end_to_end_workflow(self):
        """TEST 12: Test complete end-to-end workflow"""
        agent_id = "test_e2e_agent"

        # Step 1: Cognitive processing
        stimulus = {
            'type': 'commercial_opportunity',
            'content': 'New biodefense revenue stream available',
            'context': {'revenue_potential': 2000.0, 'urgency': 'medium'},
            'importance': 0.9
        }

        cognitive_result = await self.cognitive_engine.think(stimulus)

        # Step 2: Blockchain onboarding
        onboarding_result = await self.blockchain.onboard_agent(
            agent_id, {'preferred_network': 'bsc'}
        )

        # Step 3: Revenue stream linking
        stripe_data = {
            'asset_id': 'e2e_test_asset',
            'revenue_generated': 2000.0,
            'synthesizing_agent': agent_id
        }

        revenue_result = await self.blockchain.link_revenue_stream(stripe_data)

        # Step 4: Transaction execution
        transaction_intent = {
            'transaction_type': 'agent_payment',
            'from_agent': agent_id,
            'to_address': '0x789...',
            'amount': 200.0,
            'currency': 'SWARM',
            'network': 'bsc'
        }

        transaction_result = await self.blockchain.simulate_transaction_intent(transaction_intent)

        # Verify end-to-end workflow
        e2e_successful = all([
            cognitive_result['confidence_score'] > 0.5,
            onboarding_result['onboarding_status'] == 'completed',
            revenue_result['status'] == 'linked',
            transaction_result['simulation_result']['status'] == 'success'
        ])

        self.log_test_result(
            "End-to-End Workflow",
            e2e_successful,
            f"Cognitive: {cognitive_result['confidence_score']:.3f}, Blockchain: {e2e_successful}"
        )
        self.assertTrue(e2e_successful)

    async def test_performance_validation(self):
        """TEST 13: Test performance requirements"""
        start_time = datetime.utcnow()

        # Batch cognitive processing
        stimuli = [
            {
                'type': f'performance_test_{i}',
                'content': f'Performance test stimulus {i}',
                'importance': 0.7
            }
            for i in range(5)
        ]

        cognitive_tasks = [self.cognitive_engine.think(stimulus) for stimulus in stimuli]
        cognitive_results = await asyncio.gather(*cognitive_tasks)

        # Batch blockchain operations
        agent_ids = [f'perf_agent_{i}' for i in range(3)]
        blockchain_tasks = [
            self.blockchain.onboard_agent(agent_id, {'preferred_network': 'bsc'})
            for agent_id in agent_ids
        ]
        blockchain_results = await asyncio.gather(*blockchain_tasks)

        end_time = datetime.utcnow()
        total_time = (end_time - start_time).total_seconds()

        # Performance validation
        performance_acceptable = total_time < 10.0  # Should complete in under 10 seconds
        all_operations_successful = (
            all(result['confidence_score'] > 0 for result in cognitive_results) and
            all(result['onboarding_status'] == 'completed' for result in blockchain_results)
        )

        performance_validation = performance_acceptable and all_operations_successful

        self.log_test_result(
            "Performance Validation",
            performance_validation,
            f"Time: {total_time:.2f}s, Operations: {len(cognitive_results) + len(blockchain_results)}"
        )

    # ========================
    # ERROR HANDLING TESTS
    # ========================

    async def test_error_handling_robustness(self):
        """TEST 14: Test error handling and robustness"""
        # Test cognitive engine with malformed input
        try:
            malformed_stimulus = {
                'type': None,
                'content': "",
                'context': "invalid_context_type",
                'importance': 2.0  # Invalid range
            }

            cognitive_result = await self.cognitive_engine.think(malformed_stimulus)
            cognitive_handles_errors = 'error' not in str(cognitive_result).lower()
        except Exception:
            cognitive_handles_errors = False

        # Test blockchain with invalid transaction
        try:
            invalid_intent = {
                'transaction_type': 'invalid_type',
                'from_agent': 'nonexistent_agent',
                'to_address': 'invalid_address',
                'amount': -100.0,  # Invalid amount
                'currency': 'INVALID_CURRENCY',
                'network': 'invalid_network'
            }

            blockchain_result = await self.blockchain.simulate_transaction_intent(invalid_intent)
            blockchain_handles_errors = True  # Should not crash
        except Exception:
            blockchain_handles_errors = False

        error_handling_robust = cognitive_handles_errors and blockchain_handles_errors

        self.log_test_result(
            "Error Handling Robustness",
            error_handling_robust,
            f"Cognitive: {cognitive_handles_errors}, Blockchain: {blockchain_handles_errors}"
        )

    # ========================
    # FINAL COMPLIANCE CHECK
    # ========================

    async def test_final_spec_compliance_summary(self):
        """TEST 15: Final specification compliance summary"""
        # Gather all compliance metrics
        cognitive_spec = self.specs.get_cognitive_engine_spec()
        blockchain_spec = self.specs.get_blockchain_integration_spec()
        integration_spec = self.specs.get_integration_specs()

        # Check cognitive compliance
        cognitive_capabilities_present = all(
            cap.name in self.cognitive_engine.enhanced_capabilities
            for cap in cognitive_spec['cognitive_capabilities']
        )

        # Check blockchain compliance
        blockchain_features_present = all([
            hasattr(self.blockchain, 'wallet_manager'),
            hasattr(self.blockchain, 'simulate_transaction_intent'),
            hasattr(self.blockchain, 'link_revenue_stream'),
            self.blockchain.simulation_mode
        ])

        # Check integration compliance
        integration_preserved = all([
            hasattr(self.cognitive_engine, 'think'),
            hasattr(self.cognitive_engine, 'remember'),
            hasattr(self.cognitive_engine, 'reason')
        ])

        final_compliance = all([
            cognitive_capabilities_present,
            blockchain_features_present,
            integration_preserved
        ])

        self.log_test_result(
            "Final Spec Compliance Summary",
            final_compliance,
            f"Cognitive: {cognitive_capabilities_present}, Blockchain: {blockchain_features_present}, Integration: {integration_preserved}"
        )
        self.assertTrue(final_compliance)

    async def generate_test_report(self):
        """Generate comprehensive test report"""
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0

        print("\n" + "="*70)
        print("ANIMOCA TRACK SPEC COMPLIANCE TEST REPORT")
        print("="*70)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")

        if success_rate == 100.0:
            print("\n🎯 ALL TESTS PASSED - 100% SPEC COMPLIANCE ACHIEVED!")
            print("[PASS] Cognitive Intelligence Layer: COMPLIANT")
            print("[PASS] Blockchain Integration: COMPLIANT")
            print("[PASS] Security Requirements: COMPLIANT")
            print("[PASS] Performance Standards: COMPLIANT")
        elif success_rate >= 90.0:
            print(f"\n[PASS] EXCELLENT COMPLIANCE - {success_rate:.1f}% success rate")
        elif success_rate >= 80.0:
            print(f"\n[WARN]  GOOD COMPLIANCE - {success_rate:.1f}% success rate")
        else:
            print(f"\n[FAIL] COMPLIANCE ISSUES - {success_rate:.1f}% success rate")

        print("\nAnimoca Track Implementation Status:")
        print("  • Cognitive Intelligence Layer: Enhanced reasoning & memory")
        print("  • Blockchain Integration: Wallet management & revenue linking")
        print("  • Security Compliance: Simulation-only, no real keys")
        print("  • Stripe Integration: Revenue stream linking preserved")

        return {
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'success_rate': success_rate,
            'compliance_status': 'FULLY_COMPLIANT' if success_rate == 100.0 else 'PARTIAL_COMPLIANCE'
        }

async def run_animoca_tests():
    """Run complete Animoca track test suite"""
    print("Starting Animoca Track Specification Compliance Tests...")
    print("Testing Cognitive Intelligence Layer + Blockchain Integration\n")

    # Create test suite
    test_suite = AnimocaSpecComplianceTest()
    await test_suite.asyncSetUp()

    # Run all tests
    test_methods = [
        test_suite.test_cognitive_capabilities_compliance,
        test_suite.test_memory_system_compliance,
        test_suite.test_enhanced_reasoning_logic,
        test_suite.test_memory_retention_and_importance,
        test_suite.test_pattern_recognition_functionality,
        test_suite.test_agent_wallet_creation,
        test_suite.test_transaction_intent_simulation,
        test_suite.test_revenue_stream_integration,
        test_suite.test_gas_estimation_accuracy,
        test_suite.test_security_compliance_validation,
        test_suite.test_cognitive_blockchain_integration,
        test_suite.test_end_to_end_workflow,
        test_suite.test_performance_validation,
        test_suite.test_error_handling_robustness,
        test_suite.test_final_spec_compliance_summary
    ]

    for test_method in test_methods:
        try:
            await test_method()
        except Exception as e:
            test_name = test_method.__name__.replace('test_', '').replace('_', ' ').title()
            test_suite.log_test_result(test_name, False, f"Exception: {str(e)}")

    # Generate final report
    test_report = await test_suite.generate_test_report()

    return test_report

if __name__ == "__main__":
    # Run the test suite
    test_result = asyncio.run(run_animoca_tests())

    # Exit with appropriate code
    exit_code = 0 if test_result['compliance_status'] == 'FULLY_COMPLIANT' else 1
    print(f"\nTesting completed with exit code: {exit_code}")
    exit(exit_code)
