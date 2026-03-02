#!/usr/bin/env python3
"""
OpenClaw Base Agent Framework
Foundation classes for multi-agent swarm communication
"""

import asyncio
import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Message:
    """Inter-agent communication message"""
    id: str
    sender: str
    recipient: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: str
    priority: int = 0  # 0=normal, 1=high, 2=critical

    @classmethod
    def create(cls, sender: str, recipient: str, message_type: str,
               payload: Dict[str, Any], priority: int = 0):
        """Create a new message with auto-generated ID and timestamp"""
        return cls(
            id=str(uuid.uuid4())[:8],
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.now(timezone.utc).isoformat(),
            priority=priority
        )

class MessageBus:
    """Central message bus for agent communication"""

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_history: List[Message] = []

    def subscribe(self, agent_name: str, handler: Callable):
        """Subscribe an agent to receive messages"""
        if agent_name not in self.subscribers:
            self.subscribers[agent_name] = []
        self.subscribers[agent_name].append(handler)
        logger.info(f"[BUS] {agent_name} subscribed to message bus")

    async def publish(self, message: Message):
        """Publish message to recipient agent"""
        self.message_history.append(message)

        logger.info(f"[BUS] Message {message.id}: {message.sender} -> {message.recipient}")
        logger.info(f"[BUS] Type: {message.message_type}, Priority: {message.priority}")

        # Deliver to recipient
        if message.recipient in self.subscribers:
            for handler in self.subscribers[message.recipient]:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"[BUS] Handler error for {message.recipient}: {e}")

        # Broadcast critical messages to all agents
        if message.priority >= 2:
            for agent_name, handlers in self.subscribers.items():
                if agent_name != message.sender:
                    for handler in handlers:
                        try:
                            await handler(message)
                        except Exception as e:
                            logger.error(f"[BUS] Broadcast error to {agent_name}: {e}")

class OpenClawAgent(ABC):
    """Base OpenClaw Agent for multi-agent swarm"""

    def __init__(self, agent_name: str, agent_type: str, message_bus: MessageBus):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.message_bus = message_bus
        self.is_active = False
        self.capabilities: List[str] = []
        self.state: Dict[str, Any] = {
            'status': 'initialized',
            'last_activity': None,
            'message_count': 0
        }

        # Subscribe to message bus
        message_bus.subscribe(agent_name, self.handle_message)

        logger.info(f"[AGENT] {agent_name} ({agent_type}) initialized")

    async def activate(self):
        """Activate the agent"""
        self.is_active = True
        self.state['status'] = 'active'
        self.state['last_activity'] = datetime.now(timezone.utc).isoformat()
        logger.info(f"[AGENT] {self.agent_name} activated")

        # Send activation notification
        await self.send_message(
            recipient="*",  # Broadcast
            message_type="agent_activated",
            payload={
                'agent_name': self.agent_name,
                'agent_type': self.agent_type,
                'capabilities': self.capabilities
            }
        )

    async def deactivate(self):
        """Deactivate the agent"""
        self.is_active = False
        self.state['status'] = 'inactive'
        logger.info(f"[AGENT] {self.agent_name} deactivated")

    async def send_message(self, recipient: str, message_type: str,
                          payload: Dict[str, Any], priority: int = 0):
        """Send message to another agent"""
        message = Message.create(
            sender=self.agent_name,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
            priority=priority
        )

        await self.message_bus.publish(message)

    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        if not self.is_active:
            return

        self.state['message_count'] += 1
        self.state['last_activity'] = datetime.now(timezone.utc).isoformat()

        logger.info(f"[AGENT] {self.agent_name} received {message.message_type} from {message.sender}")

        # Route to appropriate handler
        handler_method = f"handle_{message.message_type}"
        if hasattr(self, handler_method):
            handler = getattr(self, handler_method)
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"[AGENT] {self.agent_name} handler error: {e}")
        else:
            # Default handling
            await self.handle_unknown_message(message)

    async def handle_unknown_message(self, message: Message):
        """Handle unknown message types"""
        logger.warning(f"[AGENT] {self.agent_name} received unknown message type: {message.message_type}")

    @abstractmethod
    async def run_primary_function(self) -> Dict[str, Any]:
        """Primary agent function - must be implemented by subclasses"""
        pass

    @abstractmethod
    async def handle_emergency_stop(self, message: Message):
        """Handle emergency stop messages"""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'is_active': self.is_active,
            'capabilities': self.capabilities,
            'state': self.state.copy()
        }

class SwarmCoordinator:
    """Coordinates the multi-agent swarm"""

    def __init__(self):
        self.message_bus = MessageBus()
        self.agents: Dict[str, OpenClawAgent] = {}
        self.is_running = False

    def register_agent(self, agent: OpenClawAgent):
        """Register an agent with the swarm"""
        self.agents[agent.agent_name] = agent
        logger.info(f"[SWARM] Registered agent: {agent.agent_name}")

    async def start_swarm(self):
        """Start the entire swarm"""
        self.is_running = True
        logger.info(f"[SWARM] Starting {len(self.agents)} agents")

        # Activate all agents
        for agent in self.agents.values():
            await agent.activate()

        logger.info("[SWARM] All agents activated and ready")

    async def stop_swarm(self):
        """Stop the entire swarm"""
        self.is_running = False
        logger.info("[SWARM] Stopping swarm")

        # Send emergency stop to all agents
        for agent in self.agents.values():
            await agent.send_message(
                recipient="*",
                message_type="emergency_stop",
                payload={'reason': 'swarm_shutdown'},
                priority=2
            )
            await agent.deactivate()

    def get_swarm_status(self) -> Dict[str, Any]:
        """Get status of entire swarm"""
        return {
            'is_running': self.is_running,
            'agent_count': len(self.agents),
            'agents': {name: agent.get_status() for name, agent in self.agents.items()},
            'message_history_count': len(self.message_bus.message_history)
        }