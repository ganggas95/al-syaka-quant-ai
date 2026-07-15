"""Al-Syaka MT5 Bridge — Connector, Order Manager, Auto Trading, Safety."""

__version__ = "0.1.0"

from .connector import MT5Connector, MT5SimulationConnector
from .models import OrderRequest, OrderResult, AccountInfo
from .order_manager import OrderManager
from .auto_trader import AutoTradingEngine
from .safety import SafetySystem

__all__ = [
    "MT5Connector", "MT5SimulationConnector",
    "OrderRequest", "OrderResult", "AccountInfo",
    "OrderManager",
    "AutoTradingEngine",
    "SafetySystem",
]
