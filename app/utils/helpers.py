"""
Helper functions for the MedifinderMCP Server.
"""
import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def sanitize_string(text: str) -> str:
    """Sanitize a string by removing special characters and extra whitespace.
    
    Args:
        text: The string to sanitize
        
    Returns:
        Sanitized string
    """
    if not text:
        return ""
        
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove any non-alphanumeric characters except spaces, parentheses, and common punctuation
    text = re.sub(r'[^\w\s\(\)\.\,\-\+\/]', '', text)
    
    return text


def format_stock_status(status: str) -> str:
    """Format stock status for consistent display.
    
    Args:
        status: The raw stock status
        
    Returns:
        Formatted stock status
    """
    if not status:
        return "Unknown"
        
    status_mapping = {
        'Sobrestock': 'Overstock',
        'Normostock': 'Normal Stock',
        'Substock': 'Understock',
        'Desabastecido': 'Out of Stock',
        'Sin_Consumo': 'No Consumption',
        'Sin_Rotación': 'No Rotation'
    }
    
    return status_mapping.get(status, status)


def calculate_months_supply(stock: int, consumption_rate: float) -> float:
    """Calculate months of supply based on stock and consumption rate.
    
    Args:
        stock: Current stock level
        consumption_rate: Average monthly consumption rate
        
    Returns:
        Months of supply (float)
    """
    if not stock or not consumption_rate or consumption_rate <= 0:
        return 0.0
        
    return stock / consumption_rate


def format_location_name(location: str) -> str:
    """Format location name for consistent display.
    
    Args:
        location: Raw location name
        
    Returns:
        Formatted location name
    """
    if not location:
        return ""
        
    # Replace underscores with spaces
    location = location.replace('_', ' ')
    
    # Handle common abbreviations
    location = re.sub(r'\bC\.S\.\s', 'Centro de Salud ', location)
    location = re.sub(r'\bP\.S\.\s', 'Puesto de Salud ', location)
    location = re.sub(r'\bHOSP\.\s', 'Hospital ', location)
    
    # Title case for readability
    location = location.title()
    
    return location


def get_stock_level_description(stock: int, indicator: str) -> str:
    """Get a human-readable description of the stock level.
    
    Args:
        stock: Current stock level
        indicator: Stock indicator
        
    Returns:
        Stock level description
    """
    if stock is None:
        return "Unknown stock level"
        
    if stock <= 0:
        return "Out of stock"
        
    status = format_stock_status(indicator)
    
    if status == "Overstock":
        return f"Well stocked ({stock} units, more than needed)"
    elif status == "Normal Stock":
        return f"Adequately stocked ({stock} units)"
    elif status == "Understock":
        return f"Low stock ({stock} units, below optimal level)"
    elif status == "Out of Stock":
        return f"Critically low stock ({stock} units)"
    else:
        return f"In stock ({stock} units)"