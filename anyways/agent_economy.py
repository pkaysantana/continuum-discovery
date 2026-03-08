#!/usr/bin/env python3
"""
Anyways Agent Economy
Credit optimization system for maximizing discovery efficiency
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import math

@dataclass
class CreditTransaction:
    """Record of a credit transaction"""
    timestamp: datetime
    operation: str  # 'rfdiffusion', 'proteinmpnn', 'boltz2', 'pesto'
    credits_spent: float
    batch_size: int
    results_quality: float  # 0-1 score based on outcomes
    credits_earned: float   # Credits earned from successful discoveries
    net_efficiency: float   # (credits_earned - credits_spent) / credits_spent

@dataclass
class OperationCost:
    """Cost structure for different operations"""
    base_cost: float
    per_item_cost: float
    bulk_discount: float  # Discount rate for larger batches
    quality_bonus: float  # Bonus multiplier for high-quality results

class AnyWaysAgentEconomy:
    """
    AI Agent Economy system for optimizing compute credit allocation
    """

    def __init__(self, initial_credits: float = 17.82, db_path: str = "anyways/economy.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)

        self.current_credits = initial_credits
        self.total_credits_earned = 0.0
        self.total_credits_spent = 0.0

        # Initialize cost structure
        self.operation_costs = {
            'rfdiffusion': OperationCost(0.10, 0.05, 0.02, 1.5),    # $0.10 base + $0.05/design
            'proteinmpnn': OperationCost(0.05, 0.02, 0.01, 1.3),    # $0.05 base + $0.02/sequence
            'boltz2': OperationCost(0.15, 0.08, 0.03, 2.0),         # $0.15 base + $0.08/structure
            'pesto': OperationCost(0.08, 0.03, 0.015, 1.8)          # $0.08 base + $0.03/analysis
        }

        # Credit earning rates for discoveries
        self.discovery_rewards = {
            'low_confidence': 0.50,    # ipTM 0.70-0.79, coverage 70-79%
            'medium_confidence': 1.00,  # ipTM 0.80-0.89, coverage 80-89%
            'high_confidence': 2.00,    # ipTM 0.90+, coverage 90%+
            'perfect_binder': 5.00      # ipTM 0.95+, coverage 100%, good binding
        }

        self.init_database()

    def init_database(self):
        """Initialize economy tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credit_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                credits_spent REAL NOT NULL,
                batch_size INTEGER NOT NULL,
                results_quality REAL NOT NULL,
                credits_earned REAL NOT NULL,
                net_efficiency REAL NOT NULL,
                operation_details TEXT  -- JSON
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_optimizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT NOT NULL,
                optimal_batch_size INTEGER NOT NULL,
                efficiency_score REAL NOT NULL,
                confidence_level REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discovery_rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequence_hash TEXT NOT NULL,
                reward_type TEXT NOT NULL,
                credits_earned REAL NOT NULL,
                iptm_score REAL,
                coverage_percent REAL,
                timestamp TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def calculate_operation_cost(self, operation: str, batch_size: int) -> float:
        """Calculate cost for an operation given batch size"""
        if operation not in self.operation_costs:
            return 0.5  # Default cost for unknown operations

        cost_structure = self.operation_costs[operation]
        base_cost = cost_structure.base_cost
        item_cost = cost_structure.per_item_cost * batch_size

        # Apply bulk discount
        if batch_size > 10:
            discount = min(cost_structure.bulk_discount * (batch_size - 10), 0.3)  # Max 30% discount
            total_cost = (base_cost + item_cost) * (1 - discount)
        else:
            total_cost = base_cost + item_cost

        return round(total_cost, 4)

    def optimize_batch_size(self, operation: str, remaining_credits: float) -> Tuple[int, float]:
        """
        Determine optimal batch size for maximum efficiency given remaining credits
        Returns (optimal_batch_size, expected_efficiency)
        """
        if operation not in self.operation_costs:
            return 1, 0.5

        # Get historical efficiency data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT batch_size, AVG(net_efficiency), COUNT(*)
            FROM credit_transactions
            WHERE operation = ? AND timestamp > date('now', '-7 days')
            GROUP BY batch_size
            ORDER BY AVG(net_efficiency) DESC
        """, (operation,))

        historical_data = cursor.fetchall()
        conn.close()

        # Find the batch size that maximizes efficiency within credit constraints
        best_batch_size = 1
        best_efficiency = 0.0

        for test_batch_size in range(1, 21):  # Test batch sizes 1-20
            cost = self.calculate_operation_cost(operation, test_batch_size)

            if cost > remaining_credits:
                break  # Can't afford this batch size

            # Estimate efficiency based on historical data or theoretical model
            estimated_efficiency = self.estimate_batch_efficiency(operation, test_batch_size, historical_data)

            if estimated_efficiency > best_efficiency:
                best_efficiency = estimated_efficiency
                best_batch_size = test_batch_size

        return best_batch_size, best_efficiency

    def estimate_batch_efficiency(self, operation: str, batch_size: int, historical_data: List[Tuple]) -> float:
        """Estimate efficiency for a given batch size"""
        # If we have historical data for this exact batch size, use it
        for hist_batch, hist_efficiency, hist_count in historical_data:
            if hist_batch == batch_size and hist_count >= 2:
                return hist_efficiency

        # Otherwise, use theoretical model
        # Efficiency generally increases with batch size due to bulk discounts
        # but may decrease due to quality degradation in very large batches

        base_efficiency = 0.3  # Base efficiency
        batch_bonus = min(batch_size * 0.05, 0.4)  # Up to 40% bonus for batching
        large_batch_penalty = max(0, (batch_size - 15) * 0.02)  # Penalty for very large batches

        estimated_efficiency = base_efficiency + batch_bonus - large_batch_penalty
        return max(0.1, estimated_efficiency)  # Minimum 10% efficiency

    def record_operation(self, operation: str, batch_size: int, results: List[Dict[str, Any]]) -> float:
        """
        Record the results of an operation and calculate credits earned
        Returns net credits earned (earned - spent)
        """
        cost = self.calculate_operation_cost(operation, batch_size)

        if cost > self.current_credits:
            print(f"[ECONOMY] WARNING: Operation cost ${cost:.4f} exceeds remaining credits ${self.current_credits:.4f}")
            return -cost

        # Calculate quality and earnings from results
        total_quality = 0.0
        credits_earned = 0.0

        for result in results:
            iptm = result.get('iptm_score', 0.0)
            coverage = result.get('hotspot_coverage_percent', 0.0)

            # Determine quality tier and reward
            if iptm >= 0.95 and coverage >= 100.0:
                reward_type = 'perfect_binder'
            elif iptm >= 0.90 and coverage >= 90.0:
                reward_type = 'high_confidence'
            elif iptm >= 0.80 and coverage >= 80.0:
                reward_type = 'medium_confidence'
            elif iptm >= 0.70 and coverage >= 70.0:
                reward_type = 'low_confidence'
            else:
                reward_type = None

            if reward_type:
                reward_credits = self.discovery_rewards[reward_type]
                credits_earned += reward_credits
                total_quality += 1.0

                # Record individual discovery reward
                self.record_discovery_reward(result.get('sequence_hash', 'unknown'),
                                           reward_type, reward_credits, iptm, coverage)

        # Calculate average quality
        avg_quality = total_quality / len(results) if results else 0.0

        # Apply quality bonus to earnings
        if avg_quality > 0:
            quality_bonus = self.operation_costs[operation].quality_bonus
            credits_earned *= (1 + (avg_quality * (quality_bonus - 1)))

        # Update credit balance
        self.current_credits -= cost
        self.current_credits += credits_earned
        self.total_credits_spent += cost
        self.total_credits_earned += credits_earned

        # Calculate efficiency
        net_efficiency = (credits_earned - cost) / cost if cost > 0 else 0.0

        # Record transaction
        transaction = CreditTransaction(
            timestamp=datetime.now(),
            operation=operation,
            credits_spent=cost,
            batch_size=batch_size,
            results_quality=avg_quality,
            credits_earned=credits_earned,
            net_efficiency=net_efficiency
        )

        self.record_transaction(transaction, results)

        print(f"[ECONOMY] {operation}: Spent ${cost:.4f}, Earned ${credits_earned:.4f}, Net: ${credits_earned-cost:.4f}")
        print(f"[ECONOMY] Remaining credits: ${self.current_credits:.4f}, Efficiency: {net_efficiency:.2f}")

        return credits_earned - cost

    def record_transaction(self, transaction: CreditTransaction, operation_details: List[Dict]):
        """Record transaction in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO credit_transactions
            (timestamp, operation, credits_spent, batch_size, results_quality,
             credits_earned, net_efficiency, operation_details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction.timestamp.isoformat(),
            transaction.operation,
            transaction.credits_spent,
            transaction.batch_size,
            transaction.results_quality,
            transaction.credits_earned,
            transaction.net_efficiency,
            json.dumps(operation_details, default=str)
        ))

        conn.commit()
        conn.close()

    def record_discovery_reward(self, sequence_hash: str, reward_type: str,
                              credits_earned: float, iptm_score: float, coverage_percent: float):
        """Record individual discovery reward"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO discovery_rewards
            (sequence_hash, reward_type, credits_earned, iptm_score, coverage_percent, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            sequence_hash,
            reward_type,
            credits_earned,
            iptm_score,
            coverage_percent,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    def get_economic_recommendations(self) -> Dict[str, Any]:
        """Get recommendations for optimal resource allocation"""
        recommendations = {}

        for operation in self.operation_costs.keys():
            optimal_batch, expected_efficiency = self.optimize_batch_size(operation, self.current_credits)
            estimated_cost = self.calculate_operation_cost(operation, optimal_batch)

            recommendations[operation] = {
                'optimal_batch_size': optimal_batch,
                'estimated_cost': estimated_cost,
                'expected_efficiency': expected_efficiency,
                'affordable_batches': int(self.current_credits / estimated_cost),
                'recommendation': self.get_operation_recommendation(operation, optimal_batch, expected_efficiency)
            }

        return recommendations

    def get_operation_recommendation(self, operation: str, batch_size: int, efficiency: float) -> str:
        """Generate human-readable recommendation for operation"""
        if efficiency > 1.0:
            return f"HIGHLY RECOMMENDED: Use batch size {batch_size} for {operation} (expected +{efficiency:.1f}x return)"
        elif efficiency > 0.5:
            return f"RECOMMENDED: Use batch size {batch_size} for {operation} (expected +{efficiency:.1f}x return)"
        elif efficiency > 0.0:
            return f"MARGINAL: Use batch size {batch_size} for {operation} (expected +{efficiency:.1f}x return)"
        else:
            return f"NOT RECOMMENDED: {operation} showing negative returns"

    def get_economy_stats(self) -> Dict[str, Any]:
        """Get comprehensive economy statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Transaction summary
        cursor.execute("""
            SELECT operation, COUNT(*), SUM(credits_spent), SUM(credits_earned), AVG(net_efficiency)
            FROM credit_transactions
            GROUP BY operation
        """)
        operation_stats = {}
        for operation, count, spent, earned, avg_eff in cursor.fetchall():
            operation_stats[operation] = {
                'operations_count': count,
                'total_spent': spent or 0,
                'total_earned': earned or 0,
                'average_efficiency': avg_eff or 0,
                'net_profit': (earned or 0) - (spent or 0)
            }

        # Discovery summary
        cursor.execute("""
            SELECT reward_type, COUNT(*), SUM(credits_earned), AVG(iptm_score), AVG(coverage_percent)
            FROM discovery_rewards
            GROUP BY reward_type
        """)
        discovery_stats = {}
        for reward_type, count, earned, avg_iptm, avg_coverage in cursor.fetchall():
            discovery_stats[reward_type] = {
                'count': count,
                'credits_earned': earned or 0,
                'avg_iptm': avg_iptm or 0,
                'avg_coverage': avg_coverage or 0
            }

        conn.close()

        return {
            'current_credits': self.current_credits,
            'total_spent': self.total_credits_spent,
            'total_earned': self.total_credits_earned,
            'net_profit': self.total_credits_earned - self.total_credits_spent,
            'overall_efficiency': self.total_credits_earned / self.total_credits_spent if self.total_credits_spent > 0 else 0,
            'operation_breakdown': operation_stats,
            'discovery_breakdown': discovery_stats,
            'recommendations': self.get_economic_recommendations()
        }

if __name__ == "__main__":
    # Test the agent economy
    economy = AnyWaysAgentEconomy(initial_credits=17.82)

    # Simulate some operations
    print("=== ANYWAYS AGENT ECONOMY TEST ===")
    print(f"Starting credits: ${economy.current_credits:.4f}")

    # Test batch optimization
    optimal_batch, efficiency = economy.optimize_batch_size('rfdiffusion', economy.current_credits)
    print(f"\nOptimal RFDiffusion batch: {optimal_batch} (efficiency: {efficiency:.3f})")

    # Simulate operation results
    mock_results = [
        {'iptm_score': 0.85, 'hotspot_coverage_percent': 88.9, 'sequence_hash': 'abc123'},
        {'iptm_score': 0.72, 'hotspot_coverage_percent': 75.2, 'sequence_hash': 'def456'},
        {'iptm_score': 0.91, 'hotspot_coverage_percent': 92.1, 'sequence_hash': 'ghi789'},
    ]

    net_credits = economy.record_operation('rfdiffusion', optimal_batch, mock_results)
    print(f"Net credits from operation: ${net_credits:.4f}")

    # Show economy stats
    stats = economy.get_economy_stats()
    print(f"\nEconomy Statistics:")
    print(f"Net Profit: ${stats['net_profit']:.4f}")
    print(f"Overall Efficiency: {stats['overall_efficiency']:.3f}")
    print(f"Remaining Credits: ${stats['current_credits']:.4f}")
