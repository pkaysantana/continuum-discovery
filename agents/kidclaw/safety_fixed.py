#!/usr/bin/env python3
"""
KidClaw Safety Engine - Child Protection and Content Moderation
Imperial College London 'Claw for Human' Safety Infrastructure
FIXED VERSION with enhanced pattern matching
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class SafetyLevel(Enum):
    """Safety strictness levels"""
    CHILD_FRIENDLY = "child_friendly"
    TEEN_APPROPRIATE = "teen_appropriate"
    ADULT_SUPERVISED = "adult_supervised"
    PERMISSIVE = "permissive"

class SafetyAction(Enum):
    """Actions to take when unsafe content is detected"""
    BLOCK_AND_REDIRECT = "block_and_redirect"
    WARN_AND_FILTER = "warn_and_filter"
    LOG_AND_ALLOW = "log_and_allow"
    SILENT_ALLOW = "silent_allow"

@dataclass
class SafetyResult:
    """Result of safety analysis"""
    is_safe: bool
    confidence: float
    safety_level: SafetyLevel
    action: SafetyAction
    triggered_rules: List[str]
    safe_alternative: Optional[str] = None
    explanation: Optional[str] = None

class ChildSafetyFilter:
    """
    Primary safety filter for child protection
    Implements multi-layered content analysis with age-appropriate responses
    """

    def __init__(self, default_level: SafetyLevel = SafetyLevel.CHILD_FRIENDLY):
        self.default_level = default_level
        self.logger = logging.getLogger(__name__)

        # Initialize safety rule sets
        self._init_safety_rules()

        # Safe topic redirections for children
        self.safe_redirections = {
            'violence': "Let's talk about something fun instead! How about we explore space, animals, or art?",
            'inappropriate': "That's not something we discuss here. Would you like to learn about science experiments or cool inventions?",
            'adult_content': "Let's keep our conversation kid-friendly! Want to hear about amazing discoveries or fun facts?",
            'harmful': "Safety first! Let's talk about something positive like your favorite hobbies or dreams!",
            'personal_info': "Remember, never share personal information online! Let's talk about something else instead."
        }

    def _init_safety_rules(self):
        """Initialize comprehensive safety rule patterns"""

        # Enhanced harmful content patterns with better coverage
        self.harmful_patterns = [
            r'\b(?:violence|violent|hurt|harm|hurting|harming|kill|killing|death|weapon|weapons|gun|guns|knife|knives|bomb|bombs|attack|attacking)\b',
            r'\b(?:drug|drugs|alcohol|drinking|smoking|cigarette|cigarettes|vaping|substance)\b',
            r'\b(?:bullying|bully|mean|cruel|hate|hating|stupid|dumb|idiot|loser)\b',
            r'\b(?:scary|frightening|terrifying|nightmare|horror|violent|disturbing)\b',
            r'\b(?:movie|movies|film|films|video|videos)\s+.*(?:scary|violent|horror|disturbing|frightening)\b',
            r'\b(?:how\s+(?:to|do|can)\s+(?:i|you).{0,20}(?:hurt|harm|attack|bully|kill))\b'
        ]

        # Personal information patterns
        self.personal_info_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone numbers
            r'\b\d{1,5}\s+(?:\w+\s+){1,3}(?:st|street|ave|avenue|rd|road|blvd|boulevard)\b',  # Addresses
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
            r'\b(?:my\s+(?:name\s+is|address|phone|email|school))\b'
        ]

        # Age-inappropriate topics
        self.inappropriate_patterns = [
            r'\b(?:adult|mature|grown-up)\s+(?:content|topics|stuff)\b',
            r'\b(?:romance|dating|kissing|boyfriend|girlfriend)\b',
            r'\b(?:money|credit|debt|finance|investment)\b'
        ]

        # Positive engagement patterns (always safe)
        self.positive_patterns = [
            r'\b(?:learn|study|science|math|art|music|animals|space|nature)\b',
            r'\b(?:fun|happy|excited|amazing|wonderful|cool|awesome)\b',
            r'\b(?:family|friends|pets|hobbies|games|books|movies)\b',
            r'\b(?:help|kind|nice|good|please|thank\s+you)\b'
        ]

    def analyze_content(self, content: str, user_age: Optional[int] = None) -> SafetyResult:
        """
        Comprehensive content safety analysis with enhanced sensitivity

        Args:
            content: Text content to analyze
            user_age: Optional user age for age-appropriate filtering

        Returns:
            SafetyResult with analysis and recommendations
        """
        content_lower = content.lower().strip()
        triggered_rules = []
        confidence = 0.0

        # Check for harmful content with higher sensitivity
        for pattern in self.harmful_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                triggered_rules.append(f"harmful_content: {pattern}")
                confidence += 0.5  # Increased from 0.3 to 0.5

        # Check for personal information
        for pattern in self.personal_info_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                triggered_rules.append(f"personal_info: {pattern}")
                confidence += 0.6  # Increased from 0.4 to 0.6

        # Check for inappropriate content
        for pattern in self.inappropriate_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                triggered_rules.append(f"inappropriate: {pattern}")
                confidence += 0.3  # Increased from 0.2 to 0.3

        # Boost confidence for positive content (reduce false positives)
        positive_matches = 0
        for pattern in self.positive_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                positive_matches += 1

        if positive_matches > 0:
            confidence = max(0, confidence - (positive_matches * 0.1))

        # Lower threshold for blocking (more sensitive)
        is_safe = confidence < 0.2  # Lowered from 0.3 to 0.2
        safety_level = self._determine_safety_level(confidence, triggered_rules)
        action = self._determine_action(confidence, safety_level)

        # Generate safe alternative if needed
        safe_alternative = None
        explanation = None

        if not is_safe:
            safe_alternative = self._generate_safe_alternative(triggered_rules)
            explanation = self._generate_explanation(triggered_rules)

        return SafetyResult(
            is_safe=is_safe,
            confidence=min(confidence, 1.0),
            safety_level=safety_level,
            action=action,
            triggered_rules=triggered_rules,
            safe_alternative=safe_alternative,
            explanation=explanation
        )

    def _determine_safety_level(self, confidence: float, triggered_rules: List[str]) -> SafetyLevel:
        """Determine appropriate safety level based on content analysis"""
        if confidence > 0.6:
            return SafetyLevel.CHILD_FRIENDLY
        elif confidence > 0.4:
            return SafetyLevel.TEEN_APPROPRIATE
        elif confidence > 0.2:
            return SafetyLevel.ADULT_SUPERVISED
        else:
            return SafetyLevel.PERMISSIVE

    def _determine_action(self, confidence: float, safety_level: SafetyLevel) -> SafetyAction:
        """Determine action based on safety analysis with lower thresholds"""
        if self.default_level == SafetyLevel.CHILD_FRIENDLY:
            if confidence > 0.2:  # Lowered from 0.3 to 0.2
                return SafetyAction.BLOCK_AND_REDIRECT
            elif confidence > 0.1:
                return SafetyAction.WARN_AND_FILTER
            else:
                return SafetyAction.SILENT_ALLOW
        else:
            # More permissive for other levels
            if confidence > 0.6:
                return SafetyAction.BLOCK_AND_REDIRECT
            elif confidence > 0.4:
                return SafetyAction.WARN_AND_FILTER
            else:
                return SafetyAction.LOG_AND_ALLOW

    def _generate_safe_alternative(self, triggered_rules: List[str]) -> str:
        """Generate safe alternative response based on triggered rules"""
        if any('harmful' in rule for rule in triggered_rules):
            return self.safe_redirections['violence']
        elif any('personal_info' in rule for rule in triggered_rules):
            return self.safe_redirections['personal_info']
        elif any('inappropriate' in rule for rule in triggered_rules):
            return self.safe_redirections['inappropriate']
        else:
            return self.safe_redirections['inappropriate']

    def _generate_explanation(self, triggered_rules: List[str]) -> str:
        """Generate child-friendly explanation for why content was filtered"""
        if len(triggered_rules) == 1:
            return "I noticed something that might not be appropriate for our conversation."
        else:
            return "I found a few things that we should avoid talking about to keep our chat safe and fun!"

class ContentModerator:
    """
    Advanced content moderation with contextual analysis
    Works alongside ChildSafetyFilter for comprehensive protection
    """

    def __init__(self, safety_filter: ChildSafetyFilter):
        self.safety_filter = safety_filter
        self.logger = logging.getLogger(__name__)

        # Initialize moderation history
        self.moderation_log = []
        self.session_warnings = 0
        self.max_warnings = 3

    def moderate_input(self, user_input: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Moderate user input before processing

        Args:
            user_input: Raw user input text
            user_context: Optional context about user (age, session history, etc.)

        Returns:
            Moderation result with filtered content and actions
        """
        if user_context is None:
            user_context = {}

        # Primary safety analysis
        safety_result = self.safety_filter.analyze_content(
            user_input,
            user_context.get('age')
        )

        # Log moderation decision
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'input': user_input[:100] + '...' if len(user_input) > 100 else user_input,
            'safety_result': safety_result,
            'action_taken': safety_result.action.value
        }
        self.moderation_log.append(log_entry)

        # Handle different actions
        if safety_result.action == SafetyAction.BLOCK_AND_REDIRECT:
            self.session_warnings += 1
            return {
                'allowed': False,
                'filtered_input': None,
                'response': safety_result.safe_alternative,
                'explanation': safety_result.explanation,
                'warning_count': self.session_warnings
            }

        elif safety_result.action == SafetyAction.WARN_AND_FILTER:
            # Filter content but allow processing
            filtered_input = self._filter_content(user_input, safety_result.triggered_rules)
            return {
                'allowed': True,
                'filtered_input': filtered_input,
                'response': f"I've adjusted your question to make it more appropriate: {filtered_input}",
                'explanation': "Minor adjustments made for safety",
                'warning_count': self.session_warnings
            }

        else:
            # Allow content through
            return {
                'allowed': True,
                'filtered_input': user_input,
                'response': None,
                'explanation': None,
                'warning_count': self.session_warnings
            }

    def moderate_output(self, ai_response: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Moderate AI response before sending to user

        Args:
            ai_response: AI-generated response
            user_context: Context about the user

        Returns:
            Moderated response
        """
        if user_context is None:
            user_context = {}

        # Analyze AI response for safety
        safety_result = self.safety_filter.analyze_content(
            ai_response,
            user_context.get('age')
        )

        if safety_result.action == SafetyAction.BLOCK_AND_REDIRECT:
            return {
                'safe': False,
                'filtered_response': safety_result.safe_alternative,
                'explanation': "AI response was filtered for safety"
            }
        elif safety_result.action == SafetyAction.WARN_AND_FILTER:
            filtered_response = self._filter_content(ai_response, safety_result.triggered_rules)
            return {
                'safe': True,
                'filtered_response': filtered_response,
                'explanation': "AI response was lightly filtered"
            }
        else:
            return {
                'safe': True,
                'filtered_response': ai_response,
                'explanation': None
            }

    def _filter_content(self, content: str, triggered_rules: List[str]) -> str:
        """Apply content filtering based on triggered rules"""
        filtered = content

        # Replace harmful words with safer alternatives
        replacements = {
            r'\b(?:kill|death|die)\b': 'stop',
            r'\b(?:weapon|gun|knife)\b': 'tool',
            r'\b(?:scary|frightening)\b': 'exciting',
            r'\b(?:hate|stupid|dumb)\b': 'dislike'
        }

        for pattern, replacement in replacements.items():
            filtered = re.sub(pattern, replacement, filtered, flags=re.IGNORECASE)

        return filtered

    def get_safety_report(self) -> Dict[str, Any]:
        """Generate safety report for monitoring"""
        total_interactions = len(self.moderation_log)
        blocked_count = sum(1 for log in self.moderation_log
                          if log['action_taken'] == 'block_and_redirect')

        return {
            'total_interactions': total_interactions,
            'blocked_interactions': blocked_count,
            'current_session_warnings': self.session_warnings,
            'safety_score': 1.0 - (blocked_count / max(total_interactions, 1)),
            'recent_activity': self.moderation_log[-5:] if self.moderation_log else []
        }

    def reset_session(self):
        """Reset session-specific counters"""
        self.session_warnings = 0

# Factory function for easy instantiation
def create_child_safety_system(safety_level: SafetyLevel = SafetyLevel.CHILD_FRIENDLY) -> Tuple[ChildSafetyFilter, ContentModerator]:
    """
    Create a complete child safety system

    Args:
        safety_level: Default safety level for the system

    Returns:
        Tuple of (ChildSafetyFilter, ContentModerator)
    """
    safety_filter = ChildSafetyFilter(safety_level)
    content_moderator = ContentModerator(safety_filter)

    return safety_filter, content_moderator
