#!/usr/bin/env python3
"""
Animoca Cognitive Intelligence Layer
Enhanced cognitive engine with advanced reasoning and persistent memory
"""

import sys
import os
import asyncio
import json
import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import math

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.cognitive_backbone import ContinuumCognitiveAgent, CognitiveMemory, MockEthoswarmAgent
from anyway_integration.traceloop_config import workflow, task

class EnhancedCognitiveMemory(CognitiveMemory):
    """Enhanced memory system with importance weighting and decay"""

    def __init__(self, agent_id: str, capacity: int = 10000):
        super().__init__(agent_id)
        self.capacity = capacity
        self.importance_weights = {}
        self.access_patterns = {}
        self.memory_graph = {}  # For associative connections

    async def store_experience(self, experience: Dict[str, Any]) -> str:
        """Store experience with enhanced importance scoring"""
        memory_id = await super().store_experience(experience)

        # Calculate importance score using multiple factors
        importance_score = await self._calculate_importance_score(experience)
        self.importance_weights[memory_id] = importance_score

        # Track access patterns
        self.access_patterns[memory_id] = {
            'creation_time': datetime.utcnow(),
            'last_access': datetime.utcnow(),
            'access_count': 0,
            'relevance_decay': 1.0
        }

        # Create associative links
        await self._create_associative_links(memory_id, experience)

        # Manage capacity
        await self._manage_memory_capacity()

        return memory_id

    async def retrieve_relevant(self, query: str, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Enhanced retrieval with importance weighting and recency"""
        # Get basic relevant memories
        basic_memories = await super().retrieve_relevant(query, similarity_threshold)

        # Enhance with importance and recency scoring
        scored_memories = []
        current_time = datetime.utcnow()

        for memory in basic_memories:
            memory_id = memory.get('memory_id')
            if not memory_id:
                # Generate memory_id if missing
                memory_id = hashlib.sha256(str(memory).encode()).hexdigest()[:16]

            # Calculate enhanced relevance score
            importance = self.importance_weights.get(memory_id, 0.5)

            # Time decay factor
            if memory_id in self.access_patterns:
                creation_time = self.access_patterns[memory_id]['creation_time']
                time_diff = (current_time - creation_time).total_seconds() / 3600  # hours
                recency_score = math.exp(-time_diff / 168)  # 7-day half-life
            else:
                recency_score = 0.5

            # Access frequency factor
            access_count = self.access_patterns.get(memory_id, {}).get('access_count', 0)
            frequency_score = min(1.0, access_count / 10)  # Cap at 10 accesses

            # Composite relevance score
            composite_score = (importance * 0.5) + (recency_score * 0.3) + (frequency_score * 0.2)

            memory['enhanced_relevance_score'] = composite_score
            memory['memory_id'] = memory_id
            scored_memories.append(memory)

            # Update access pattern
            if memory_id in self.access_patterns:
                self.access_patterns[memory_id]['access_count'] += 1
                self.access_patterns[memory_id]['last_access'] = current_time

        # Sort by enhanced relevance and return top results
        scored_memories.sort(key=lambda x: x['enhanced_relevance_score'], reverse=True)
        return scored_memories[:15]  # Return top 15 most relevant

    async def _calculate_importance_score(self, experience: Dict[str, Any]) -> float:
        """Calculate importance score based on multiple factors"""
        score = 0.5  # Base score

        # Factor 1: Explicit importance from experience
        explicit_importance = experience.get('importance', 0.5)
        score += explicit_importance * 0.3

        # Factor 2: Emotional/urgency indicators
        context = experience.get('context', {})
        if context.get('urgency') == 'high':
            score += 0.2
        if context.get('emergency', False):
            score += 0.3

        # Factor 3: Domain expertise relevance
        if 'domain' in experience and experience['domain']:
            score += 0.1

        # Factor 4: Outcome success
        outcome = experience.get('outcome', {})
        if outcome.get('status') == 'success':
            score += 0.15
        elif outcome.get('status') == 'failure':
            score += 0.1  # Failures are also important to learn from

        # Factor 5: Collaboration indicators
        if 'collaboration' in experience:
            score += 0.1

        # Factor 6: Learning outcome quality
        learning = experience.get('learning', {})
        if learning.get('confidence_adjustment', 0) > 0:
            score += 0.1

        # Normalize to [0, 1] range
        return min(1.0, max(0.0, score))

    async def _create_associative_links(self, memory_id: str, experience: Dict[str, Any]):
        """Create associative links between related memories"""
        if memory_id not in self.memory_graph:
            self.memory_graph[memory_id] = {'links': [], 'strength': {}}

        # Find related memories based on keywords and concepts
        keywords = self._extract_keywords(experience)

        for existing_id, existing_memory in self.memory_store.items():
            if existing_id == memory_id:
                continue

            existing_keywords = self._extract_keywords(existing_memory['experience'])
            common_keywords = set(keywords) & set(existing_keywords)

            if len(common_keywords) >= 2:  # At least 2 common keywords
                link_strength = len(common_keywords) / max(len(keywords), len(existing_keywords))

                # Create bidirectional links
                self.memory_graph[memory_id]['links'].append(existing_id)
                self.memory_graph[memory_id]['strength'][existing_id] = link_strength

                if existing_id not in self.memory_graph:
                    self.memory_graph[existing_id] = {'links': [], 'strength': {}}
                self.memory_graph[existing_id]['links'].append(memory_id)
                self.memory_graph[existing_id]['strength'][memory_id] = link_strength

    async def _manage_memory_capacity(self):
        """Manage memory capacity by removing least important memories"""
        if len(self.memory_store) <= self.capacity:
            return

        # Calculate removal scores (inverse of importance + age)
        removal_candidates = []
        current_time = datetime.utcnow()

        for memory_id in self.memory_store:
            importance = self.importance_weights.get(memory_id, 0.5)
            creation_time = self.access_patterns.get(memory_id, {}).get('creation_time', current_time)
            age_hours = (current_time - creation_time).total_seconds() / 3600

            # Lower score = more likely to be removed
            removal_score = importance - (age_hours / 1000)  # Age penalty
            removal_candidates.append((memory_id, removal_score))

        # Sort by removal score and remove lowest scoring memories
        removal_candidates.sort(key=lambda x: x[1])

        memories_to_remove = int(len(self.memory_store) - self.capacity * 0.9)  # Remove to 90% capacity

        for i in range(memories_to_remove):
            memory_id, _ = removal_candidates[i]
            self._remove_memory(memory_id)

    def _remove_memory(self, memory_id: str):
        """Remove a memory and its associations"""
        if memory_id in self.memory_store:
            del self.memory_store[memory_id]
        if memory_id in self.importance_weights:
            del self.importance_weights[memory_id]
        if memory_id in self.access_patterns:
            del self.access_patterns[memory_id]
        if memory_id in self.memory_graph:
            # Remove bidirectional links
            for linked_id in self.memory_graph[memory_id]['links']:
                if linked_id in self.memory_graph:
                    self.memory_graph[linked_id]['links'] = [
                        lid for lid in self.memory_graph[linked_id]['links'] if lid != memory_id
                    ]
                    if memory_id in self.memory_graph[linked_id]['strength']:
                        del self.memory_graph[linked_id]['strength'][memory_id]
            del self.memory_graph[memory_id]

class EnhancedEthoswarmAgent(MockEthoswarmAgent):
    """Enhanced Ethoswarm agent with advanced reasoning capabilities"""

    def __init__(self, agent_config: Dict[str, Any]):
        super().__init__(agent_config)
        self.reasoning_confidence_threshold = 0.8
        self.pattern_recognition_buffer = []
        self.strategic_memory = {}

    async def reason(self, perception: Dict[str, Any], memories: List[Dict], goals: List[str]) -> Dict[str, Any]:
        """Enhanced reasoning with pattern recognition and confidence scoring"""

        # Step 1: Context analysis
        context_analysis = await self._analyze_context(perception, memories)

        # Step 2: Pattern recognition
        patterns = await self._recognize_patterns(perception, memories)

        # Step 3: Goal alignment assessment
        goal_alignment = await self._assess_goal_alignment(perception, goals)

        # Step 4: Evidence-based reasoning
        evidence_chain = await self._build_evidence_chain(context_analysis, patterns, memories)

        # Step 5: Confidence calculation
        confidence = await self._calculate_reasoning_confidence(evidence_chain, patterns, goal_alignment)

        # Step 6: Generate reasoning conclusion
        conclusion = await self._generate_conclusion(evidence_chain, patterns, goal_alignment, confidence)

        reasoning_result = {
            'reasoning_type': 'enhanced_analytical',
            'confidence': confidence,
            'conclusion': conclusion['summary'],
            'reasoning_chain': evidence_chain,
            'patterns_recognized': patterns,
            'goal_alignment_score': goal_alignment['overall_score'],
            'context_analysis': context_analysis,
            'decision_factors': conclusion['factors'],
            'timestamp': datetime.utcnow().isoformat()
        }

        self.reasoning_history.append(reasoning_result)

        # Store strategic insights
        if confidence >= self.reasoning_confidence_threshold:
            await self._store_strategic_insight(reasoning_result)

        return reasoning_result

    async def _analyze_context(self, perception: Dict[str, Any], memories: List[Dict]) -> Dict[str, Any]:
        """Analyze contextual factors"""
        context = perception.get('context', {})

        # Analyze urgency and importance
        urgency_indicators = ['urgent', 'critical', 'emergency', 'immediate']
        urgency_score = sum(1 for indicator in urgency_indicators
                          if indicator in str(context).lower()) / len(urgency_indicators)

        # Analyze domain relevance
        content = perception.get('processed_content', '')
        domain_relevance = 0.5  # Default

        if any(term in content.lower() for term in ['biotech', 'therapeutic', 'protein']):
            domain_relevance += 0.3
        if any(term in content.lower() for term in ['collaboration', 'multi-agent', 'swarm']):
            domain_relevance += 0.2

        return {
            'urgency_score': min(1.0, urgency_score),
            'domain_relevance': min(1.0, domain_relevance),
            'complexity_level': len(str(perception)) / 1000,  # Text length as complexity proxy
            'memory_relevance': len(memories) / 10  # Number of relevant memories
        }

    async def _recognize_patterns(self, perception: Dict[str, Any], memories: List[Dict]) -> List[Dict[str, Any]]:
        """Recognize patterns across perceptions and memories"""
        patterns = []

        # Add current perception to pattern buffer
        self.pattern_recognition_buffer.append({
            'perception': perception,
            'timestamp': datetime.utcnow(),
            'processed': False
        })

        # Keep only recent items in buffer
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.pattern_recognition_buffer = [
            item for item in self.pattern_recognition_buffer
            if item['timestamp'] > cutoff_time
        ]

        # Pattern 1: Recurring themes
        if len(self.pattern_recognition_buffer) >= 3:
            recent_contents = [item['perception'].get('processed_content', '')
                            for item in self.pattern_recognition_buffer[-5:]]

            # Simple keyword frequency analysis
            word_freq = {}
            for content in recent_contents:
                words = content.lower().split()
                for word in words:
                    if len(word) > 3:  # Skip short words
                        word_freq[word] = word_freq.get(word, 0) + 1

            recurring_themes = {word: freq for word, freq in word_freq.items() if freq >= 2}
            if recurring_themes:
                patterns.append({
                    'type': 'recurring_themes',
                    'themes': recurring_themes,
                    'confidence': min(1.0, len(recurring_themes) / 5),
                    'description': f"Detected {len(recurring_themes)} recurring themes"
                })

        # Pattern 2: Success/failure patterns from memories
        if memories:
            outcomes = [memory.get('experience', {}).get('outcome', {}).get('status')
                       for memory in memories if 'experience' in memory]
            success_rate = outcomes.count('success') / len(outcomes) if outcomes else 0.5

            patterns.append({
                'type': 'outcome_pattern',
                'success_rate': success_rate,
                'confidence': min(1.0, len(outcomes) / 5),
                'description': f"Historical success rate: {success_rate:.2f}"
            })

        return patterns

    async def _assess_goal_alignment(self, perception: Dict[str, Any], goals: List[str]) -> Dict[str, Any]:
        """Assess how well the perception aligns with current goals"""
        if not goals:
            return {'overall_score': 0.5, 'alignment_details': {}}

        content = perception.get('processed_content', '').lower()
        alignment_scores = {}

        for goal in goals:
            goal_lower = goal.lower()

            # Simple keyword matching
            goal_words = goal_lower.split('_')
            matches = sum(1 for word in goal_words if word in content)
            alignment_scores[goal] = matches / len(goal_words)

        overall_score = sum(alignment_scores.values()) / len(alignment_scores)

        return {
            'overall_score': overall_score,
            'alignment_details': alignment_scores,
            'best_aligned_goal': max(alignment_scores, key=alignment_scores.get) if alignment_scores else None
        }

    async def _build_evidence_chain(self, context_analysis: Dict[str, Any],
                                  patterns: List[Dict[str, Any]], memories: List[Dict]) -> List[str]:
        """Build evidence chain for reasoning"""
        evidence_chain = []

        # Evidence from context
        if context_analysis['urgency_score'] > 0.7:
            evidence_chain.append("High urgency detected - immediate action may be required")
        if context_analysis['domain_relevance'] > 0.8:
            evidence_chain.append("Strong domain relevance - leveraging specialized knowledge")

        # Evidence from patterns
        for pattern in patterns:
            if pattern['confidence'] > 0.7:
                evidence_chain.append(f"Pattern detected: {pattern['description']}")

        # Evidence from memories
        if memories:
            high_relevance_memories = [m for m in memories if m.get('enhanced_relevance_score', 0) > 0.8]
            if high_relevance_memories:
                evidence_chain.append(f"Found {len(high_relevance_memories)} highly relevant past experiences")

        # Logical reasoning steps
        evidence_chain.append("Analyzing available evidence and applying domain expertise")
        evidence_chain.append("Considering potential outcomes and risk factors")
        evidence_chain.append("Synthesizing multi-factor analysis for decision recommendation")

        return evidence_chain

    async def _calculate_reasoning_confidence(self, evidence_chain: List[str],
                                           patterns: List[Dict[str, Any]],
                                           goal_alignment: Dict[str, Any]) -> float:
        """Calculate confidence in reasoning conclusion"""
        confidence_factors = []

        # Evidence quality factor
        evidence_quality = min(1.0, len(evidence_chain) / 5)
        confidence_factors.append(evidence_quality * 0.3)

        # Pattern recognition factor
        pattern_confidence = sum(p['confidence'] for p in patterns) / len(patterns) if patterns else 0.5
        confidence_factors.append(pattern_confidence * 0.3)

        # Goal alignment factor
        confidence_factors.append(goal_alignment['overall_score'] * 0.2)

        # Consistency factor (simplified)
        consistency_factor = 0.8  # Assume high consistency for enhanced reasoning
        confidence_factors.append(consistency_factor * 0.2)

        return sum(confidence_factors)

    async def _generate_conclusion(self, evidence_chain: List[str], patterns: List[Dict[str, Any]],
                                 goal_alignment: Dict[str, Any], confidence: float) -> Dict[str, Any]:
        """Generate reasoning conclusion"""

        # Generate summary based on confidence level
        if confidence >= 0.9:
            summary = "High-confidence analysis completed with strong evidence and clear patterns"
        elif confidence >= 0.7:
            summary = "Solid analysis with good evidence support and identifiable patterns"
        elif confidence >= 0.5:
            summary = "Moderate confidence analysis - some uncertainty remains"
        else:
            summary = "Low confidence analysis - limited evidence or conflicting patterns"

        # Key decision factors
        factors = []
        if evidence_chain:
            factors.append(f"Evidence chain: {len(evidence_chain)} factors analyzed")
        if patterns:
            factors.append(f"Pattern analysis: {len(patterns)} patterns identified")
        if goal_alignment['overall_score'] > 0.6:
            factors.append(f"Strong goal alignment: {goal_alignment['overall_score']:.2f}")

        return {
            'summary': summary,
            'factors': factors,
            'confidence_level': 'high' if confidence >= 0.8 else 'medium' if confidence >= 0.6 else 'low'
        }

    async def _store_strategic_insight(self, reasoning_result: Dict[str, Any]):
        """Store high-confidence reasoning as strategic insight"""
        insight_id = str(uuid.uuid4())

        self.strategic_memory[insight_id] = {
            'reasoning_summary': reasoning_result['conclusion'],
            'confidence': reasoning_result['confidence'],
            'patterns': reasoning_result['patterns_recognized'],
            'decision_factors': reasoning_result['decision_factors'],
            'timestamp': reasoning_result['timestamp'],
            'application_count': 0
        }

        # Limit strategic memory size
        if len(self.strategic_memory) > 50:
            # Remove oldest insight
            oldest_key = min(self.strategic_memory.keys(),
                           key=lambda k: self.strategic_memory[k]['timestamp'])
            del self.strategic_memory[oldest_key]

class CognitivePlatformEngine(ContinuumCognitiveAgent):
    """Enhanced cognitive platform engine extending ContinuumCognitiveAgent"""

    def __init__(self, agent_config: Dict[str, Any]):
        # Initialize with enhanced components
        agent_config['name'] = agent_config.get('name', 'CognitivePlatformEngine')
        agent_config['domain'] = agent_config.get('domain', 'cognitive_intelligence')

        super().__init__(agent_config)

        # Replace with enhanced components
        self.memory = EnhancedCognitiveMemory(self.identity.id)
        self.cognitive_engine = EnhancedEthoswarmAgent(agent_config)

        # Enhanced capabilities
        self.enhanced_capabilities = [
            'advanced_reasoning',
            'pattern_recognition',
            'strategic_planning',
            'meta_cognition',
            'associative_memory',
            'confidence_assessment',
            'evidence_chain_building',
            'multi_factor_analysis'
        ]

        print(f"[COGNITIVE_ENGINE] Enhanced platform initialized: {self.identity.name}")
        print(f"[COGNITIVE_ENGINE] Enhanced capabilities: {len(self.enhanced_capabilities)}")

    @workflow(name="enhanced_cognitive_processing")
    async def think(self, stimulus: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced thinking with advanced cognitive processing"""

        print(f"[COGNITIVE_ENGINE] Enhanced thinking initiated: {stimulus.get('type', 'unknown')}")

        # Enhanced cognitive processing pipeline
        result = await super().think_and_act(stimulus)

        # Add cognitive enhancement metrics
        enhancement_metrics = {
            'cognitive_complexity_score': await self._assess_cognitive_complexity(stimulus, result),
            'reasoning_depth_level': self._calculate_reasoning_depth(result.get('reasoning_trace', {})),
            'pattern_recognition_score': self._calculate_pattern_score(result.get('reasoning_trace', {})),
            'meta_cognitive_awareness': await self._assess_meta_cognitive_awareness(result)
        }

        result['enhancement_metrics'] = enhancement_metrics
        result['cognitive_engine_version'] = 'enhanced_v1.0'

        return result

    @task(name="enhanced_memory_storage")
    async def remember(self, experience: Dict[str, Any]) -> str:
        """Enhanced memory storage with importance scoring"""
        print(f"[COGNITIVE_ENGINE] Storing enhanced memory: {experience.get('type', 'unknown')}")

        # Use enhanced memory system
        memory_id = await self.memory.store_experience(experience)

        print(f"[COGNITIVE_ENGINE] Memory stored with ID: {memory_id[:8]}...")
        return memory_id

    @task(name="enhanced_reasoning")
    async def reason(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced reasoning with confidence scoring"""
        if context is None:
            context = {}

        print(f"[COGNITIVE_ENGINE] Enhanced reasoning: {query[:50]}...")

        # Retrieve relevant memories
        relevant_memories = await self.memory.retrieve_relevant(query)

        # Create reasoning stimulus
        reasoning_stimulus = {
            'type': 'reasoning_query',
            'content': query,
            'context': context,
            'importance': 0.8
        }

        # Use enhanced reasoning
        perception = await self.cognitive_engine.perceive(reasoning_stimulus)
        reasoning_result = await self.cognitive_engine.reason(
            perception=perception,
            memories=relevant_memories,
            goals=self.identity.current_goals
        )

        return {
            'query': query,
            'reasoning_result': reasoning_result,
            'relevant_memories_count': len(relevant_memories),
            'confidence': reasoning_result.get('confidence', 0.5),
            'reasoning_type': reasoning_result.get('reasoning_type', 'standard'),
            'timestamp': datetime.utcnow().isoformat()
        }

    async def _assess_cognitive_complexity(self, stimulus: Dict[str, Any], result: Dict[str, Any]) -> float:
        """Assess cognitive complexity of the processing"""
        complexity_factors = []

        # Input complexity
        input_complexity = len(str(stimulus)) / 1000
        complexity_factors.append(min(1.0, input_complexity))

        # Reasoning chain length
        reasoning_trace = result.get('reasoning_trace', {})
        chain_length = len(reasoning_trace.get('reasoning_chain', []))
        complexity_factors.append(min(1.0, chain_length / 10))

        # Memory interaction
        memory_usage = len(str(result.get('reasoning_trace', {}))) / 2000
        complexity_factors.append(min(1.0, memory_usage))

        return sum(complexity_factors) / len(complexity_factors)

    def _calculate_reasoning_depth(self, reasoning_trace: Dict[str, Any]) -> int:
        """Calculate depth of reasoning process"""
        depth_indicators = [
            len(reasoning_trace.get('reasoning_chain', [])),
            len(reasoning_trace.get('patterns_recognized', [])),
            len(reasoning_trace.get('decision_factors', []))
        ]

        return sum(depth_indicators)

    def _calculate_pattern_score(self, reasoning_trace: Dict[str, Any]) -> float:
        """Calculate pattern recognition effectiveness"""
        patterns = reasoning_trace.get('patterns_recognized', [])
        if not patterns:
            return 0.0

        pattern_confidences = [p.get('confidence', 0.5) for p in patterns]
        return sum(pattern_confidences) / len(pattern_confidences)

    async def _assess_meta_cognitive_awareness(self, result: Dict[str, Any]) -> float:
        """Assess meta-cognitive awareness level"""
        awareness_indicators = []

        reasoning_trace = result.get('reasoning_trace', {})

        # Confidence assessment quality
        confidence = reasoning_trace.get('confidence', 0.5)
        confidence_quality = 1.0 - abs(0.8 - confidence)  # Optimal confidence around 0.8
        awareness_indicators.append(confidence_quality)

        # Self-reflection in reasoning
        if 'uncertainty' in str(reasoning_trace).lower():
            awareness_indicators.append(0.8)
        else:
            awareness_indicators.append(0.4)

        # Process monitoring
        if len(reasoning_trace.get('reasoning_chain', [])) > 3:
            awareness_indicators.append(0.9)
        else:
            awareness_indicators.append(0.5)

        return sum(awareness_indicators) / len(awareness_indicators)

# Demo function for testing
async def demo_cognitive_engine():
    """Demonstrate enhanced cognitive engine"""

    print("\n" + "="*70)
    print("ANIMOCA COGNITIVE INTELLIGENCE LAYER DEMO")
    print("="*70)

    # Initialize enhanced cognitive engine
    config = {
        'name': 'AnimocaCognitiveEngine',
        'domain': 'cognitive_intelligence',
        'personality': {'analytical': 0.9, 'innovative': 0.85, 'reflective': 0.8},
        'ethics': ['transparency', 'beneficence', 'cognitive_honesty'],
        'goals': ['enhanced_reasoning', 'pattern_recognition', 'strategic_insights'],
        'capabilities': ['advanced_reasoning', 'pattern_recognition', 'strategic_planning']
    }

    engine = CognitivePlatformEngine(config)

    # Test 1: Enhanced thinking
    print("\n[DEMO] Test 1: Enhanced Cognitive Processing")
    stimulus = {
        'type': 'complex_problem',
        'content': 'Multi-agent biodefense coordination with blockchain integration',
        'context': {
            'urgency': 'high',
            'domain': 'biotech',
            'complexity': 'multi_factor',
            'stakeholders': ['researchers', 'commercial', 'security']
        },
        'importance': 0.9
    }

    result = await engine.think(stimulus)

    print(f"[DEMO] Cognitive complexity: {result['enhancement_metrics']['cognitive_complexity_score']:.3f}")
    print(f"[DEMO] Reasoning depth: {result['enhancement_metrics']['reasoning_depth_level']}")
    print(f"[DEMO] Pattern score: {result['enhancement_metrics']['pattern_recognition_score']:.3f}")
    print(f"[DEMO] Meta-cognitive awareness: {result['enhancement_metrics']['meta_cognitive_awareness']:.3f}")

    # Test 2: Enhanced memory
    print(f"\n[DEMO] Test 2: Enhanced Memory Storage")
    experience = {
        'type': 'strategic_insight',
        'content': 'Blockchain-cognitive integration requires trust modeling',
        'domain': 'cognitive_intelligence',
        'importance': 0.85,
        'outcome': {'status': 'success'},
        'context': {'innovation': True, 'multi_domain': True}
    }

    memory_id = await engine.remember(experience)
    print(f"[DEMO] Memory stored with enhanced scoring: {memory_id}")

    # Test 3: Enhanced reasoning
    print(f"\n[DEMO] Test 3: Enhanced Reasoning")
    reasoning_result = await engine.reason(
        "How can cognitive agents optimize blockchain revenue integration?",
        {'domain': 'blockchain', 'priority': 'commercial'}
    )

    print(f"[DEMO] Reasoning confidence: {reasoning_result['confidence']:.3f}")
    print(f"[DEMO] Reasoning type: {reasoning_result['reasoning_result']['reasoning_type']}")
    print(f"[DEMO] Relevant memories: {reasoning_result['relevant_memories_count']}")

    print(f"\n[DEMO] Cognitive engine demonstration completed!")
    print("="*70)

    return engine

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_cognitive_engine())
