"""
MCP tools for the MedifinderMCP Server.
"""
import logging
import json
from typing import Dict, List, Optional, Any

from mcp.server.fastmcp import FastMCP, Context

from app.db import queries
from app.config import MAX_SEARCH_RESULTS

logger = logging.getLogger(__name__)

def register_tools(mcp: FastMCP):
    """Register MCP tools with the server.
    
    Args:
        mcp (FastMCP): The MCP server
    """
    logger.info("Registering MCP tools...")
    
    # Register all tools with the MCP server
    mcp.tool()(search_medicines)
    mcp.tool()(get_medicine_locations)
    mcp.tool()(get_medicine_stock)
    mcp.tool()(get_regional_statistics)
    mcp.tool()(get_medicine_status)
    
    logger.info("MCP tools registered")


@mcp.tool()
def search_medicines(
    query: str, 
    search_type: str = "name", 
    location: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = MAX_SEARCH_RESULTS
) -> Dict[str, Any]:
    """Search for medicines in the database.
    
    Args:
        query: The search query
        search_type: Type of search ('name' or 'location')
        location: Location to search in (DIRESA)
        category: Category of medical facility
        limit: Maximum number of results to return
        
    Returns:
        Dictionary with search results
    """
    logger.info(f"Searching for medicines with query '{query}', type: {search_type}")
    
    results = []
    
    if search_type.lower() == "name":
        medicines = queries.search_medicines_by_name(query, limit=limit)
        
        # Convert SQLAlchemy objects to dictionaries
        results = [medicine.to_dict() for medicine in medicines]
    
    elif search_type.lower() == "location":
        if not location:
            return {"error": "Location parameter is required for location search"}
            
        medicines = queries.search_medicines_by_location(
            location, 
            categoria=category, 
            limit=limit
        )
        
        # Convert SQLAlchemy objects to dictionaries
        results = [medicine.to_dict() for medicine in medicines]
    
    else:
        return {"error": f"Invalid search type: {search_type}"}
    
    return {
        "query": query,
        "search_type": search_type,
        "count": len(results),
        "results": results
    }


@mcp.tool()
def get_medicine_locations(medicine_name: str, min_stock: int = 1) -> Dict[str, Any]:
    """Get locations where a medicine is available.
    
    Args:
        medicine_name: The name of the medicine to search for
        min_stock: Minimum stock required to consider available
        
    Returns:
        Dictionary with available locations
    """
    logger.info(f"Finding locations for medicine '{medicine_name}' with min stock {min_stock}")
    
    locations = queries.get_available_medicine_locations(medicine_name, min_stock)
    
    # Format the locations
    formatted_locations = []
    for loc in locations:
        formatted_locations.append({
            "diresa": loc.diresa,
            "categoria": loc.categoria,
            "nombre_ejecutora": loc.nombre_ejecutora,
            "reportante": loc.reportante,
            "stock": loc.stk
        })
    
    return {
        "medicine_name": medicine_name,
        "min_stock": min_stock,
        "count": len(formatted_locations),
        "locations": formatted_locations
    }


@mcp.tool()
def get_medicine_stock(medicine_id: int) -> Dict[str, Any]:
    """Get stock information for a specific medicine.
    
    Args:
        medicine_id: The ID of the medicine
        
    Returns:
        Dictionary with medicine stock information
    """
    logger.info(f"Getting stock information for medicine ID {medicine_id}")
    
    medicine = queries.get_medicine_by_id(medicine_id)
    
    if not medicine:
        return {"error": f"Medicine with ID {medicine_id} not found"}
    
    # Calculate months of supply
    months_of_supply = 0
    if medicine.cpma and medicine.cpma > 0:
        months_of_supply = medicine.stk / medicine.cpma
    
    result = medicine.to_dict()
    result["months_of_supply"] = round(months_of_supply, 2)
    
    return result


@mcp.tool()
def get_regional_statistics() -> Dict[str, Any]:
    """Get medicine statistics by region.
    
    Returns:
        Dictionary with regional statistics
    """
    logger.info("Getting regional statistics")
    
    # Get regional statistics
    regional_stats = queries.get_stock_status_by_region()
    
    # Format the results
    formatted_stats = []
    for stat in regional_stats:
        # Convert SQLAlchemy Row to dictionary
        stat_dict = dict(stat)
        
        # Calculate availability percentage
        if stat_dict["total_medicines"] > 0:
            availability = (stat_dict["available_medicines"] / stat_dict["total_medicines"]) * 100
        else:
            availability = 0
            
        stat_dict["availability_percentage"] = round(availability, 2)
        formatted_stats.append(stat_dict)
    
    return {
        "count": len(formatted_stats),
        "regions": formatted_stats
    }


@mcp.tool()
def get_medicine_status() -> Dict[str, Any]:
    """Get overall medicine statistics.
    
    Returns:
        Dictionary with medicine statistics
    """
    logger.info("Getting overall medicine statistics")
    
    # Get medicine statistics
    stats = queries.get_medicine_statistics()
    
    return stats