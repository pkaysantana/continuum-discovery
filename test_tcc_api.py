#!/usr/bin/env python3
"""
TCC Enterprise Dashboard API Test Suite
Comprehensive testing for all FastAPI endpoints with mock agent outputs
"""

import sys
import os
import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

# Import the FastAPI app and models
from api.dashboard_app import (
    app,
    AminoAnalyticaMetrics,
    BioDockMetrics,
    FlockMetrics,
    AnimocaMetrics,
    ClawHumanMetrics,
    EnvironmentalMetrics,
    DashboardSummary,
    agent_instances,
    AGENTS_AVAILABLE
)

# Test client for FastAPI
client = TestClient(app)

class TestTCCAPICompliance:
    """
    TCC Track API Compliance Test Suite
    Tests all endpoints for 100% compliance with the 6-track integration requirements
    """

    def setup_method(self):
        """Setup for each test method"""
        self.test_timestamp = datetime.now(timezone.utc).isoformat()

    def test_health_check_endpoint(self):
        """Test 1: API health check returns correct status and structure"""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()

        # Verify required fields
        assert "status" in data
        assert "service" in data
        assert "agents_loaded" in data
        assert "timestamp" in data

        # Verify values
        assert data["status"] == "healthy"
        assert data["service"] == "TCC Enterprise Dashboard API"
        assert isinstance(data["agents_loaded"], int)
        assert data["agents_loaded"] >= 0

    def test_dashboard_home_endpoint(self):
        """Test 2: Main dashboard serves HTML correctly"""
        response = client.get("/")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_aminoanalytica_metrics_endpoint(self):
        """Test 3: AminoAnalytica metrics endpoint returns correct structure"""
        response = client.get("/api/agents/aminoanalytica")

        assert response.status_code == 200
        data = response.json()

        # Verify all required AminoAnalytica fields
        required_fields = [
            "iptm_score", "interface_pae", "hotspot_coverage_percent",
            "synthesis_status", "target_pdb", "validation_status", "last_synthesis"
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Verify data types and ranges
        assert isinstance(data["iptm_score"], float)
        assert 0.0 <= data["iptm_score"] <= 1.0
        assert isinstance(data["interface_pae"], float)
        assert data["interface_pae"] >= 0.0
        assert isinstance(data["hotspot_coverage_percent"], float)
        assert 0.0 <= data["hotspot_coverage_percent"] <= 100.0
        assert isinstance(data["synthesis_status"], str)
        assert isinstance(data["target_pdb"], str)
        assert isinstance(data["validation_status"], str)

    def test_biodock_metrics_endpoint(self):
        """Test 4: BioDock medical metrics endpoint returns correct structure"""
        response = client.get("/api/agents/biodock")

        assert response.status_code == 200
        data = response.json()

        # Verify all required BioDock fields
        required_fields = [
            "tissue_damage_reduction", "biomarker_confidence", "pathology_analysis_count",
            "diagnostic_accuracy", "treatment_recommendations", "last_analysis"
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Verify data types and ranges
        assert isinstance(data["tissue_damage_reduction"], float)
        assert 0.0 <= data["tissue_damage_reduction"] <= 100.0
        assert isinstance(data["biomarker_confidence"], float)
        assert 0.0 <= data["biomarker_confidence"] <= 1.0
        assert isinstance(data["pathology_analysis_count"], int)
        assert data["pathology_analysis_count"] >= 0
        assert isinstance(data["diagnostic_accuracy"], float)
        assert 0.0 <= data["diagnostic_accuracy"] <= 1.0
        assert isinstance(data["treatment_recommendations"], int)
        assert data["treatment_recommendations"] >= 0

    def test_flock_metrics_endpoint(self):
        """Test 5: FLock SDG metrics endpoint returns correct structure"""
        response = client.get("/api/agents/flock")

        assert response.status_code == 200
        data = response.json()

        # Verify all required FLock fields
        required_fields = [
            "telegram_alerts_sent", "sdg3_health_alerts", "community_impact_score",
            "stakeholder_coordination", "response_time_avg", "alert_success_rate"
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Verify data types and ranges
        assert isinstance(data["telegram_alerts_sent"], int)
        assert data["telegram_alerts_sent"] >= 0
        assert isinstance(data["sdg3_health_alerts"], int)
        assert data["sdg3_health_alerts"] >= 0
        assert isinstance(data["community_impact_score"], float)
        assert 0.0 <= data["community_impact_score"] <= 1.0
        assert isinstance(data["stakeholder_coordination"], int)
        assert data["stakeholder_coordination"] >= 0
        assert isinstance(data["response_time_avg"], float)
        assert data["response_time_avg"] >= 0.0
        assert isinstance(data["alert_success_rate"], float)
        assert 0.0 <= data["alert_success_rate"] <= 1.0

    def test_animoca_metrics_endpoint(self):
        """Test 6: Animoca blockchain/revenue metrics endpoint returns correct structure"""
        response = client.get("/api/agents/animoca")

        assert response.status_code == 200
        data = response.json()

        # Verify all required Animoca fields
        required_fields = [
            "stripe_revenue_total", "token_rewards_distributed", "agent_wallets_created",
            "transaction_simulations", "blockchain_participation_score", "revenue_growth_rate"
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Verify data types and ranges
        assert isinstance(data["stripe_revenue_total"], float)
        assert data["stripe_revenue_total"] >= 0.0
        assert isinstance(data["token_rewards_distributed"], float)
        assert data["token_rewards_distributed"] >= 0.0
        assert isinstance(data["agent_wallets_created"], int)
        assert data["agent_wallets_created"] >= 0
        assert isinstance(data["transaction_simulations"], int)
        assert data["transaction_simulations"] >= 0
        assert isinstance(data["blockchain_participation_score"], float)
        assert 0.0 <= data["blockchain_participation_score"] <= 1.0
        assert isinstance(data["revenue_growth_rate"], float)

    def test_claw_human_metrics_endpoint(self):
        """Test 7: Claw for Human safety metrics endpoint returns correct structure"""
        response = client.get("/api/agents/claw-human")

        assert response.status_code == 200
        data = response.json()

        # Verify all required Claw for Human fields
        required_fields = [
            "safety_interventions", "content_filtered", "child_interactions",
            "safety_score", "family_notifications", "educational_engagements"
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Verify data types and ranges
        assert isinstance(data["safety_interventions"], int)
        assert data["safety_interventions"] >= 0
        assert isinstance(data["content_filtered"], int)
        assert data["content_filtered"] >= 0
        assert isinstance(data["child_interactions"], int)
        assert data["child_interactions"] >= 0
        assert isinstance(data["safety_score"], float)
        assert 0.0 <= data["safety_score"] <= 1.0
        assert isinstance(data["family_notifications"], int)
        assert data["family_notifications"] >= 0
        assert isinstance(data["educational_engagements"], int)
        assert data["educational_engagements"] >= 0

    def test_environmental_metrics_endpoint(self):
        """Test 8: Environmental monitoring metrics endpoint returns correct structure"""
        response = client.get("/api/agents/environmental")

        assert response.status_code == 200
        data = response.json()

        # Verify all required Environmental fields
        required_fields = [
            "water_coverage_percent", "threat_level", "flood_alerts_sent",
            "emergency_responses", "satellite_data_points", "risk_assessment_score"
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Verify data types and ranges
        assert isinstance(data["water_coverage_percent"], float)
        assert data["water_coverage_percent"] >= 0.0
        assert isinstance(data["threat_level"], str)
        assert data["threat_level"] in ["LOW", "MEDIUM", "HIGH"]
        assert isinstance(data["flood_alerts_sent"], int)
        assert data["flood_alerts_sent"] >= 0
        assert isinstance(data["emergency_responses"], int)
        assert data["emergency_responses"] >= 0
        assert isinstance(data["satellite_data_points"], int)
        assert data["satellite_data_points"] >= 0
        assert isinstance(data["risk_assessment_score"], float)
        assert 0.0 <= data["risk_assessment_score"] <= 1.0

    def test_dashboard_summary_endpoint(self):
        """Test 9: Complete dashboard summary endpoint returns correct structure"""
        response = client.get("/api/dashboard/summary")

        assert response.status_code == 200
        data = response.json()

        # Verify all required top-level fields
        required_fields = [
            "aminoanalytica", "biodock", "flock", "animoca",
            "claw_human", "environmental", "system_status",
            "total_agents", "uptime_hours", "timestamp"
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Verify nested structures contain all their required fields
        assert isinstance(data["aminoanalytica"], dict)
        assert isinstance(data["biodock"], dict)
        assert isinstance(data["flock"], dict)
        assert isinstance(data["animoca"], dict)
        assert isinstance(data["claw_human"], dict)
        assert isinstance(data["environmental"], dict)

        # Verify system-level metrics
        assert isinstance(data["system_status"], str)
        assert data["system_status"] in ["operational", "partial"]
        assert isinstance(data["total_agents"], int)
        assert data["total_agents"] >= 0
        assert isinstance(data["uptime_hours"], float)
        assert data["uptime_hours"] >= 0.0

    def test_agent_status_endpoint(self):
        """Test 10: Agent status endpoint returns correct structure"""
        response = client.get("/api/agents/status")

        assert response.status_code == 200
        data = response.json()

        # Verify required status fields
        required_fields = ["total_agents", "agents_available", "agents", "timestamp"]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Verify data types
        assert isinstance(data["total_agents"], int)
        assert isinstance(data["agents_available"], bool)
        assert isinstance(data["agents"], dict)
        assert isinstance(data["timestamp"], str)

    @patch('api.dashboard_app.agent_instances')
    def test_aminoanalytica_with_real_agent(self, mock_agent_instances):
        """Test 11: AminoAnalytica endpoint with mocked real agent"""
        # Setup mock agent
        mock_agent = AsyncMock()
        mock_agent.run_primary_function.return_value = {
            'iptm_score': 0.85,
            'interface_pae': 3.2,
            'hotspot_coverage_percent': 78.5,
            'status': 'completed',
            'target_pdb': '2IBX',
            'validation_status': 'SUCCESS'
        }
        mock_agent_instances.__getitem__ = Mock(return_value=mock_agent)
        mock_agent_instances.__contains__ = Mock(return_value=True)

        response = client.get("/api/agents/aminoanalytica")

        assert response.status_code == 200
        data = response.json()
        assert data["iptm_score"] == 0.85
        assert data["interface_pae"] == 3.2
        assert data["target_pdb"] == "2IBX"

    @patch('api.dashboard_app.agent_instances')
    def test_biodock_with_real_agent(self, mock_agent_instances):
        """Test 12: BioDock endpoint with mocked real agent"""
        # Setup mock agent
        mock_agent = Mock()
        mock_agent.get_medical_status.return_value = {
            'tissue_damage_reduction': 67.3,
            'biomarker_confidence': 0.89,
            'analysis_count': 245,
            'diagnostic_accuracy': 0.94,
            'recommendations': 38
        }
        mock_agent_instances.__getitem__ = Mock(return_value=mock_agent)
        mock_agent_instances.__contains__ = Mock(return_value=True)

        response = client.get("/api/agents/biodock")

        assert response.status_code == 200
        data = response.json()
        assert data["tissue_damage_reduction"] == 67.3
        assert data["biomarker_confidence"] == 0.89
        assert data["pathology_analysis_count"] == 245

    @patch('api.dashboard_app.agent_instances')
    def test_flock_with_real_agent(self, mock_agent_instances):
        """Test 13: FLock endpoint with mocked real agent"""
        # Setup mock agent
        mock_agent = Mock()
        mock_agent.get_coordination_status.return_value = {
            'alerts_sent': 312,
            'sdg3_alerts': 89,
            'impact_score': 0.82,
            'stakeholders': 24,
            'response_time': 4.7,
            'success_rate': 0.91
        }
        mock_agent_instances.__getitem__ = Mock(return_value=mock_agent)
        mock_agent_instances.__contains__ = Mock(return_value=True)

        response = client.get("/api/agents/flock")

        assert response.status_code == 200
        data = response.json()
        assert data["telegram_alerts_sent"] == 312
        assert data["sdg3_health_alerts"] == 89
        assert data["community_impact_score"] == 0.82

    def test_pydantic_model_validation(self):
        """Test 14: Verify all Pydantic models validate correctly"""
        # Test AminoAnalyticaMetrics validation
        amino_data = {
            "iptm_score": 0.75,
            "interface_pae": 4.1,
            "hotspot_coverage_percent": 82.3,
            "synthesis_status": "completed",
            "target_pdb": "2IBX",
            "validation_status": "SUCCESS",
            "last_synthesis": self.test_timestamp
        }
        amino_model = AminoAnalyticaMetrics(**amino_data)
        assert amino_model.iptm_score == 0.75

        # Test BioDockMetrics validation
        biodock_data = {
            "tissue_damage_reduction": 55.7,
            "biomarker_confidence": 0.88,
            "pathology_analysis_count": 180,
            "diagnostic_accuracy": 0.93,
            "treatment_recommendations": 42,
            "last_analysis": self.test_timestamp
        }
        biodock_model = BioDockMetrics(**biodock_data)
        assert biodock_model.biomarker_confidence == 0.88

    def test_error_handling_robustness(self):
        """Test 15: Verify error handling for various edge cases"""
        # Test endpoints still work when agents throw exceptions
        with patch('api.dashboard_app.agent_instances') as mock_instances:
            # Mock agent that raises exception
            mock_agent = Mock()
            mock_agent.run_primary_function.side_effect = Exception("Test error")
            mock_instances.__getitem__ = Mock(return_value=mock_agent)
            mock_instances.__contains__ = Mock(return_value=True)

            # Should gracefully handle error and return mock data
            response = client.get("/api/agents/aminoanalytica")

            # Should either return 500 with error or fall back to mock data
            assert response.status_code in [200, 500]

            if response.status_code == 200:
                data = response.json()
                assert "iptm_score" in data
            else:
                assert "error" in response.json()["detail"]

def run_tcc_api_tests():
    """
    Execute the complete TCC API test suite
    Returns: (passed_tests, total_tests, compliance_percentage)
    """
    print("[TCC API] Starting comprehensive API compliance test suite...")

    # Run pytest with verbose output
    import subprocess
    result = subprocess.run([
        'python', '-m', 'pytest', 'test_tcc_api.py', '-v', '--tb=short'
    ], capture_output=True, text=True, cwd='.')

    # Parse results
    output = result.stdout + result.stderr
    print(output)

    # Count test results
    lines = output.split('\n')
    passed_count = 0
    failed_count = 0
    total_count = 0

    for line in lines:
        if '::test_' in line:
            total_count += 1
            if 'PASSED' in line:
                passed_count += 1
            elif 'FAILED' in line:
                failed_count += 1

    if total_count == 0:
        # Fallback: run tests directly
        import pytest
        pytest_result = pytest.main(['-v', 'test_tcc_api.py'])

        # For direct pytest execution, assume all tests if no failures
        total_count = 15  # We have 15 tests defined
        passed_count = total_count if pytest_result == 0 else 0

    compliance_percentage = (passed_count / total_count * 100) if total_count > 0 else 0

    print(f"\n[TCC API] Test Results:")
    print(f"  - Passed: {passed_count}/{total_count}")
    print(f"  - Failed: {failed_count}")
    print(f"  - Compliance: {compliance_percentage:.1f}%")

    if compliance_percentage == 100.0:
        print("[TCC API] [PASS] 100% API compliance achieved! Enterprise dashboard ready for production.")
    else:
        print(f"[TCC API] [FAIL] {compliance_percentage:.1f}% compliance. Review failed tests above.")

    return passed_count, total_count, compliance_percentage

if __name__ == "__main__":
    run_tcc_api_tests()
