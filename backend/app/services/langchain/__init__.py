"""
LangChain service module for TravelPal.

This module provides LangChain-based services for natural language processing
and conversation handling in the TravelPal application.
"""

from .agent import TravelAgent, travel_agent

__all__ = ["TravelAgent", "travel_agent"]
