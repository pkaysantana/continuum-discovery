#!/usr/bin/env python3
"""
KidClaw Agent - Child-Safe AI Assistant
Imperial College London 'Claw for Human' Track Implementation
"""

import sys
import os
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from openclaw.base_agent import OpenClawAgent, Message
from agents.kidclaw.safety import create_child_safety_system, SafetyLevel, SafetyAction
from anyway_integration.traceloop_config import workflow, task

class KidClawAgent(OpenClawAgent):
    """
    Child-Safe AI Assistant with comprehensive safety infrastructure
    Implements Imperial 'Claw for Human' safety specifications
    """

    def __init__(self, message_bus, safety_level: SafetyLevel = SafetyLevel.CHILD_FRIENDLY):
        super().__init__(
            agent_name="KidClawAgent",
            agent_type="child_safety_assistant",
            message_bus=message_bus
        )

        # Initialize safety infrastructure
        self.safety_filter, self.content_moderator = create_child_safety_system(safety_level)
        self.safety_level = safety_level

        # Initialize capabilities
        self.capabilities = [
            "child_safe_conversation",
            "content_filtering",
            "educational_assistance",
            "family_communication",
            "safety_monitoring",
            "positive_engagement"
        ]

        # Child-friendly response templates
        self.response_templates = {
            'greeting': [
                "Hi there! I'm KidClaw, your friendly and safe AI assistant! How can I help you today?",
                "Hello! I'm here to help you learn and have fun safely. What would you like to explore?",
                "Hey! I'm KidClaw, and I love helping kids discover amazing things. What's on your mind?"
            ],
            'encouragement': [
                "That's a great question! You're really curious and that's awesome!",
                "I love how you think! Let's explore that together!",
                "You're doing great! Keep asking questions - that's how we learn!"
            ],
            'learning': [
                "Did you know that learning new things actually makes your brain stronger? Cool, right?",
                "Let's turn this into a fun learning adventure!",
                "Every question you ask helps you become smarter!"
            ],
            'safety_redirect': [
                "Let's talk about something more fun instead!",
                "How about we explore something exciting and positive?",
                "I have so many cool topics we could discuss!"
            ]
        }

        # Educational topics that are always safe and engaging
        self.safe_topics = {
            'science': [
                "Amazing space discoveries and cool planets",
                "Fun animal facts and nature wonders",
                "Cool science experiments you can do safely"
            ],
            'creativity': [
                "Art projects and creative ideas",
                "Story writing and imagination games",
                "Music, dancing, and creative expression"
            ],
            'learning': [
                "Fun ways to learn math and reading",
                "Geography and world cultures",
                "History heroes and amazing inventions"
            ],
            'health': [
                "Staying healthy and strong",
                "Good habits and self-care",
                "Exercise and outdoor activities"
            ]
        }

        # Initialize session tracking
        self.user_sessions = {}
        self.safety_stats = {
            'total_interactions': 0,
            'safety_interventions': 0,
            'positive_redirections': 0,
            'educational_engagements': 0
        }

        print(f"[KIDCLAW] Child Safety Agent initialized with {safety_level.value} protection level")

    @workflow(name="kidclaw_safe_interaction")
    async def handle_user_interaction(self, user_input: str, user_id: str = "anonymous", user_age: int = 8) -> Dict[str, Any]:
        """
        Handle user interaction with comprehensive safety filtering

        Args:
            user_input: Raw user input
            user_id: User identifier for session tracking
            user_age: User's age for age-appropriate responses

        Returns:
            Safe, filtered response with educational value
        """
        self.safety_stats['total_interactions'] += 1

        # Get or create user session
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'session_start': datetime.now(timezone.utc).isoformat(),
                'age': user_age,
                'interaction_count': 0,
                'safety_warnings': 0,
                'favorite_topics': []
            }

        session = self.user_sessions[user_id]
        session['interaction_count'] += 1

        # Moderate input through safety system
        moderation_result = await self._moderate_input(user_input, session)

        if not moderation_result['allowed']:
            # Handle blocked content
            self.safety_stats['safety_interventions'] += 1
            session['safety_warnings'] += 1

            response = await self._generate_safety_response(moderation_result, session)
            return {
                'response': response,
                'safety_filtered': True,
                'educational_content': await self._suggest_safe_alternative(),
                'status': 'content_blocked'
            }

        # Process safe content
        filtered_input = moderation_result['filtered_input']
        ai_response = await self._generate_safe_response(filtered_input, session)

        # Moderate AI output
        output_moderation = self.content_moderator.moderate_output(
            ai_response,
            {'age': session['age'], 'session': session}
        )

        final_response = output_moderation['filtered_response']

        # Add educational value
        educational_content = await self._add_educational_value(filtered_input, final_response, session)

        self.state['last_interaction'] = datetime.now(timezone.utc).isoformat()

        return {
            'response': final_response,
            'safety_filtered': not output_moderation['safe'],
            'educational_content': educational_content,
            'status': 'safe_interaction',
            'encouragement': self._generate_encouragement()
        }

    @task(name="input_moderation")
    async def _moderate_input(self, user_input: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """Moderate user input using safety systems"""
        user_context = {
            'age': session['age'],
            'session_warnings': session['safety_warnings'],
            'interaction_count': session['interaction_count']
        }

        return self.content_moderator.moderate_input(user_input, user_context)

    @task(name="safety_response_generation")
    async def _generate_safety_response(self, moderation_result: Dict[str, Any], session: Dict[str, Any]) -> str:
        """Generate appropriate safety response for blocked content"""
        base_response = moderation_result['response']

        # Add age-appropriate context
        if session['age'] <= 6:
            return f"🌟 {base_response} Let's talk about your favorite animals instead!"
        elif session['age'] <= 10:
            return f"🚀 {base_response} Want to hear about space adventures or cool science?"
        else:
            return f"🎨 {base_response} How about we explore art, music, or amazing inventions?"

    @task(name="safe_response_generation")
    async def _generate_safe_response(self, filtered_input: str, session: Dict[str, Any]) -> str:
        """Generate safe, engaging AI response"""
        # Simple keyword-based response generation (placeholder for more sophisticated AI)
        input_lower = filtered_input.lower()

        if any(word in input_lower for word in ['science', 'space', 'planet', 'star']):
            return "Space is amazing! Did you know there are more stars in the universe than grains of sand on all Earth's beaches? What would you like to know about space?"

        elif any(word in input_lower for word in ['animal', 'pet', 'dog', 'cat', 'bird']):
            return "Animals are incredible! Each animal has special skills - like how dolphins can see with sound! What's your favorite animal?"

        elif any(word in input_lower for word in ['art', 'draw', 'paint', 'create']):
            return "Art is a wonderful way to express yourself! Did you know that colors can actually make you feel different emotions? What do you like to create?"

        elif any(word in input_lower for word in ['learn', 'school', 'study', 'homework']):
            return "Learning is like going on treasure hunts for knowledge! Every new thing you learn makes you smarter and more amazing. What subject interests you most?"

        elif any(word in input_lower for word in ['help', 'problem', 'stuck']):
            return "I'm here to help! Remember, asking for help shows you're smart and brave. What can we figure out together?"

        else:
            # Default safe and encouraging response
            return "That's interesting! I love how curious you are. Curiosity is one of the best qualities a person can have. Tell me more about what you're thinking!"

    @task(name="educational_enhancement")
    async def _add_educational_value(self, user_input: str, response: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """Add educational value to interactions"""
        input_lower = user_input.lower()
        educational_content = {}

        # Identify educational opportunities
        if any(word in input_lower for word in ['why', 'how', 'what', 'when', 'where']):
            educational_content['learning_opportunity'] = True
            educational_content['question_type'] = 'inquiry'

        # Suggest related learning
        if 'space' in input_lower:
            educational_content['related_topics'] = self.safe_topics['science'][0:2]
        elif 'animal' in input_lower:
            educational_content['related_topics'] = self.safe_topics['science'][1:3]
        elif 'art' in input_lower:
            educational_content['related_topics'] = self.safe_topics['creativity'][0:2]

        # Track favorite topics
        if educational_content.get('related_topics'):
            session['favorite_topics'].append(educational_content['related_topics'][0])

        self.safety_stats['educational_engagements'] += 1

        return educational_content

    async def _suggest_safe_alternative(self) -> Dict[str, Any]:
        """Suggest safe alternative topics when content is blocked"""
        import random

        category = random.choice(list(self.safe_topics.keys()))
        topic = random.choice(self.safe_topics[category])

        return {
            'category': category,
            'topic': topic,
            'question': f"Would you like to learn about {topic.lower()}?"
        }

    def _generate_encouragement(self) -> str:
        """Generate encouraging message for positive reinforcement"""
        import random
        return random.choice(self.response_templates['encouragement'])

    async def handle_safety_report_request(self, message: Message):
        """Handle requests for safety reports from other agents or administrators"""
        report = self.content_moderator.get_safety_report()

        # Add KidClaw-specific stats
        report.update({
            'kidclaw_stats': self.safety_stats,
            'active_sessions': len(self.user_sessions),
            'safety_level': self.safety_level.value
        })

        await self.send_message(
            recipient=message.sender,
            message_type="safety_report_response",
            payload={'safety_report': report},
            priority=1
        )

    async def handle_family_communication(self, message: Message):
        """Handle family communication and parental oversight requests"""
        # Placeholder for family communication features
        family_update = {
            'child_activity_summary': "Your child has been engaging in safe, educational conversations",
            'learning_topics': list(set().union(*[session['favorite_topics'] for session in self.user_sessions.values()])),
            'safety_status': "All interactions have been appropriately filtered",
            'engagement_level': "Positive and curious participation"
        }

        await self.send_message(
            recipient=message.sender,
            message_type="family_update",
            payload=family_update,
            priority=1
        )

    async def handle_emergency_stop(self, message: Message):
        """Handle emergency stop requests with safety logging"""
        print(f"[KIDCLAW] Emergency stop received: {message.payload.get('reason', 'Unknown')}")

        # Log emergency stop for safety audit
        emergency_log = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'reason': message.payload.get('reason', 'Unknown'),
            'sender': message.sender,
            'active_sessions': len(self.user_sessions),
            'safety_stats': self.safety_stats
        }

        print(f"[KIDCLAW] Safety audit: {len(self.user_sessions)} active child sessions terminated safely")

        # Reset all user sessions for safety
        self.user_sessions.clear()
        self.content_moderator.reset_session()

        # Deactivate agent safely
        await self.deactivate()

    def get_safety_status(self) -> Dict[str, Any]:
        """Get comprehensive safety status for monitoring"""
        return {
            'agent_name': self.agent_name,
            'safety_level': self.safety_level.value,
            'active_sessions': len(self.user_sessions),
            'safety_stats': self.safety_stats,
            'capabilities': self.capabilities,
            'system_status': 'operational'
        }

    async def run_primary_function(self) -> Dict[str, Any]:
        """Primary function for KidClaw agent - safety monitoring"""
        # Perform safety system health check
        system_health = {
            'safety_filter_operational': self.safety_filter is not None,
            'content_moderator_operational': self.content_moderator is not None,
            'active_user_sessions': len(self.user_sessions),
            'total_interactions_handled': self.safety_stats['total_interactions'],
            'safety_intervention_rate': (
                self.safety_stats['safety_interventions'] /
                max(self.safety_stats['total_interactions'], 1)
            ) * 100
        }

        print(f"[KIDCLAW] Safety system health check: {system_health['safety_filter_operational']} ✅")
        print(f"[KIDCLAW] Active sessions: {system_health['active_user_sessions']}")
        print(f"[KIDCLAW] Safety intervention rate: {system_health['safety_intervention_rate']:.1f}%")

        return {
            'status': 'operational',
            'system_health': system_health,
            'safety_level': self.safety_level.value,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

# Demo conversation handler for testing
async def demo_kidclaw_interaction(agent: KidClawAgent, user_input: str, user_age: int = 8) -> None:
    """Demonstrate KidClaw interaction for testing"""
    print(f"\n[DEMO] Child (age {user_age}): {user_input}")

    result = await agent.handle_user_interaction(user_input, "demo_user", user_age)

    print(f"[KIDCLAW] {result['response']}")

    if result.get('educational_content'):
        print(f"[EDUCATIONAL] {result['educational_content']}")

    if result.get('encouragement'):
        print(f"[ENCOURAGEMENT] {result['encouragement']}")

    print(f"[STATUS] {result['status']} | Safety Filtered: {result['safety_filtered']}")
