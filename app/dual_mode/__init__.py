"""
Dual-mode offline-online system package.

This package provides components for managing dual-mode functionality:
- ModeStateManager: Core mode state management
- CreditManager: Automaton credit management
- OfflineModeHandler: Manual trading features without LLM
- OnlineModeHandler: AI-powered trading features (to be implemented)
- SessionManager: Online session management (to be implemented)
- AIAgentManager: Isolated AI agent management (to be implemented)

Feature: dual-mode-offline-online
"""

from .mode_state_manager import (
    ModeStateManager,
    UserModeState,
    ModeTransition,
    TransitionResult
)

from .credit_manager import (
    CreditManager,
    CreditResult,
    CreditTransaction,
    ValidationResult
)

from .offline_mode_handler import (
    OfflineModeHandler,
    AnalysisResult,
    SignalResult
)

__all__ = [
    'ModeStateManager',
    'UserModeState',
    'ModeTransition',
    'TransitionResult',
    'CreditManager',
    'CreditResult',
    'CreditTransaction',
    'ValidationResult',
    'OfflineModeHandler',
    'AnalysisResult',
    'SignalResult'
]
