#!/usr/bin/env python3
"""
Telegram Interface: FLock.io SDG 3 Multi-Channel Integration
Provides Telegram alerts for UN SDG 3 (Good Health and Well-being)
"""

import sys
import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from openclaw.base_agent import OpenClawAgent, Message

try:
    import telegram
    from telegram import Bot
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("[TELEGRAM] python-telegram-bot not available - using simulation mode")

class TelegramInterface(OpenClawAgent):
    """
    FLock.io SDG 3 Telegram Interface for multi-channel swarm communication
    Sends real-time health alerts for flood-pathogen threats
    """

    def __init__(self, message_bus, bot_token: str = None):
        super().__init__(
            agent_name="TelegramInterface",
            agent_type="communication_channel",
            message_bus=message_bus
        )

        # Initialize capabilities
        self.capabilities = [
            "telegram_notifications",
            "sdg3_health_alerts",
            "flock_api_integration",
            "multi_channel_communication",
            "emergency_broadcasting",
            "swarm_status_updates"
        ]

        # Telegram configuration
        self.bot_token = bot_token or "DEMO_BOT_TOKEN"
        self.chat_ids = []  # User chat IDs for broadcasting
        self.bot_active = TELEGRAM_AVAILABLE and bot_token

        if self.bot_active:
            try:
                self.bot = Bot(token=self.bot_token)
                self.state['telegram_status'] = 'connected'
            except Exception as e:
                self.bot_active = False
                self.state['telegram_status'] = f'error: {e}'
        else:
            self.state['telegram_status'] = 'simulation_mode'

        # Message history for demo
        self.message_history = []
        self.alert_count = 0

    async def run_primary_function(self) -> Dict[str, Any]:
        """
        Primary function: Monitor and relay swarm communications
        """
        status_report = {
            'interface_timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'operational',
            'telegram_active': self.bot_active,
            'chat_subscribers': len(self.chat_ids),
            'alerts_sent': self.alert_count,
            'message_history_count': len(self.message_history)
        }

        print(f"[TELEGRAM] Interface status: {len(self.chat_ids)} subscribers, {self.alert_count} alerts sent")
        return status_report

    async def handle_sdg3_health_alert(self, message: Message):
        """
        Handle SDG 3 (Good Health and Well-being) alerts from EarthWatcherAgent
        """
        alert_data = message.payload
        severity = alert_data.get('severity', 'UNKNOWN')
        region = alert_data.get('region', 'Unknown Region')
        water_coverage = alert_data.get('water_coverage', 0.0)

        # Construct FLock SDG 3 alert message
        alert_text = f"[EARTH] SDG 3 Alert: High-risk flood detected in {region}. "\
                    f"Water coverage: {water_coverage:.1f}%. "\
                    f"BioScientistAgent is spinning up open-source countermeasures via FLock API..."

        telegram_message = {
            'type': 'sdg3_health_alert',
            'severity': severity,
            'message': alert_text,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'sdg_target': '3.3 - Combat infectious diseases',
            'flock_integration': True
        }

        await self._send_telegram_message(telegram_message)

        print(f"[TELEGRAM] SDG 3 Alert sent: {severity} severity flood detected")

    async def handle_synthesis_progress(self, message: Message):
        """
        Handle synthesis progress updates from BioScientistAgent
        """
        progress_data = message.payload
        stage = progress_data.get('stage', 'unknown')
        rmsd_score = progress_data.get('rmsd_score', 0.0)
        validation = progress_data.get('validation', 'UNKNOWN')

        if stage == 'synthesis_complete':
            progress_text = f"[SYNTH] FLock Synthesis Update: Countermeasure generated! "\
                           f"RMSD: {rmsd_score:.3f}A ({validation}). "\
                           f"Open-source validation complete via multi-agent collaboration."

            telegram_message = {
                'type': 'synthesis_progress',
                'message': progress_text,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'rmsd_score': rmsd_score,
                'validation_status': validation
            }

            await self._send_telegram_message(telegram_message)

        print(f"[TELEGRAM] Synthesis progress: {stage} - RMSD {rmsd_score:.3f}A")

    async def handle_asset_commercialized(self, message: Message):
        """
        Handle commercialization updates from BiotechExecutiveAgent
        """
        asset_data = message.payload
        asset_id = asset_data.get('asset_id', 'unknown')
        final_price = asset_data.get('final_price', 0.0)
        token_symbol = asset_data.get('token_symbol', 'UNKNOWN')

        commercial_text = f"[MONEY] Swarm Commercialization: Asset {asset_id[:8]} ready! "\
                         f"Dynamic price: ${final_price:.2f}. "\
                         f"IP token {token_symbol} launched on BNB Chain via multi-agent coordination."

        telegram_message = {
            'type': 'asset_commercialized',
            'message': commercial_text,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'asset_id': asset_id,
            'final_price': final_price,
            'token_symbol': token_symbol
        }

        await self._send_telegram_message(telegram_message)

        print(f"[TELEGRAM] Commercial update: {asset_id[:8]} at ${final_price:.2f}")

    async def handle_pricing_update(self, message: Message):
        """
        Handle dynamic pricing updates
        """
        pricing_data = message.payload
        threat_level = pricing_data.get('threat_level', 'UNKNOWN')
        multiplier = pricing_data.get('pricing_multiplier', 1.0)
        water_coverage = pricing_data.get('water_coverage', 0.0)

        pricing_text = f"[PRICE] Dynamic Pricing Update: {threat_level} threat level detected "\
                      f"({water_coverage:.1f}% flood coverage). "\
                      f"Pricing multiplier: {multiplier:.1f}x for emergency response optimization."

        telegram_message = {
            'type': 'pricing_update',
            'message': pricing_text,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'threat_level': threat_level,
            'pricing_multiplier': multiplier
        }

        await self._send_telegram_message(telegram_message)

        print(f"[TELEGRAM] Pricing update: {threat_level} -> {multiplier:.1f}x multiplier")

    async def _send_telegram_message(self, telegram_message: Dict[str, Any]):
        """
        Send message via Telegram bot or simulate for demo
        """
        self.message_history.append(telegram_message)
        self.alert_count += 1

        message_text = telegram_message['message']

        if self.bot_active and self.chat_ids:
            try:
                # Send to all subscribers
                for chat_id in self.chat_ids:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message_text,
                        parse_mode='Markdown'
                    )

                print(f"[TELEGRAM] Message sent to {len(self.chat_ids)} subscribers")

            except Exception as e:
                print(f"[TELEGRAM] Send error: {e}")
                self.state['telegram_status'] = f'send_error: {e}'
        else:
            # Simulation mode - display message
            print(f"[TELEGRAM] SIMULATION - Would send to Telegram:")
            print(f"[TELEGRAM] {message_text}")

    async def handle_swarm_status_request(self, message: Message):
        """
        Handle swarm status requests via Telegram
        """
        status_text = f"[SWARM] OpenClaw Multi-Agent Swarm Status:\n"\
                     f"* EarthWatcherAgent: Monitoring satellite data\n"\
                     f"* BioScientistAgent: Protein synthesis ready\n"\
                     f"* BiotechExecutiveAgent: Commercial operations active\n"\
                     f"* Alerts sent: {self.alert_count}\n"\
                     f"* FLock SDG 3 integration: [OK] Active"

        status_message = {
            'type': 'swarm_status',
            'message': status_text,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'alert_count': self.alert_count
        }

        await self._send_telegram_message(status_message)

    async def handle_emergency_stop(self, message: Message):
        """Handle emergency stop from swarm coordinator"""
        print(f"[TELEGRAM] Emergency stop received: {message.payload.get('reason')}")

        # Send final status message
        final_text = f"[STOP] Multi-Agent Swarm Shutdown: Emergency stop initiated. "\
                    f"Total alerts sent: {self.alert_count}. "\
                    f"FLock SDG 3 session complete."

        final_message = {
            'type': 'emergency_stop',
            'message': final_text,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'final_alert_count': self.alert_count
        }

        await self._send_telegram_message(final_message)
        await self.deactivate()

    async def add_subscriber(self, chat_id: str):
        """Add a Telegram chat subscriber"""
        if chat_id not in self.chat_ids:
            self.chat_ids.append(chat_id)
            print(f"[TELEGRAM] Added subscriber: {chat_id}")

    def get_interface_status(self) -> Dict[str, Any]:
        """Get detailed interface status"""
        return {
            'agent_name': self.agent_name,
            'telegram_active': self.bot_active,
            'telegram_status': self.state.get('telegram_status'),
            'subscribers': len(self.chat_ids),
            'alerts_sent': self.alert_count,
            'message_history_count': len(self.message_history),
            'capabilities': self.capabilities,
            'flock_sdg3_ready': True
        }

    async def run_continuous_monitoring(self):
        """
        Monitor for communication requests
        """
        print(f"[TELEGRAM] Starting FLock SDG 3 interface monitoring...")

        while self.is_active:
            try:
                # Periodic status check
                await self.run_primary_function()
                await asyncio.sleep(180)  # Check every 3 minutes

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[TELEGRAM] Interface monitoring error: {e}")
                await asyncio.sleep(30)

        print(f"[TELEGRAM] Interface monitoring stopped")