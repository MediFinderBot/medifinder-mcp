"""
MCP resources for the MedifinderMCP Server.
"""
import logging
import json
import pandas as pd
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP, Context

from app.db import queries
from app.models.medicines import Medicine

logger = logging.getLogger(__name__)

def register_resources(mcp: FastMCP):
    """Register MCP resources with the server.
    
    Args:
        mcp (FastMCP): The MCP server
    """
    logger.info("Registering MCP resources...")
    
    # Register all resources with the MCP server
    # Resource URI patterns
    mcp.resource("medicine://{id}")(get_medicine_resource)
    mcp.resource("stock://{name}")(get_medicine_stock_resource)
    mcp.resource("locations://{diresa}")(get_locations_resource)
    mcp.resource("statistics://stock")(get_stock_statistics_resource)
    mcp.resource("statistics://regions")(get_regions_statistics_resource)
    
    logger.info("MCP resources registered")


@mcp.resource("medicine://{id}")
def get_medicine_resource(id: str) -> str:
    """Get medicine details by ID.
    
    Args:
        id: Medicine ID
        
    Returns:
        JSON string with medicine details
    """
    logger.info(f"Fetching medicine resource for ID {id}")
    
    try:
        medicine_id = int(id)
    except ValueError:
        return json.dumps({"error": f"Invalid medicine ID: {id}"})
    
    medicine = queries.get_medicine_by_id(medicine_id)
    
    if not medicine:
        return json.dumps({"error": f"Medicine with ID {id} not found"})
    
    return json.dumps(medicine.to_dict(), indent=2)


@mcp.resource("stock://{name}")
def get_medicine_stock_resource(name: str) -> str:
    """Get stock information for a medicine by name.
    
    Args:
        name: Medicine name
        
    Returns:
        JSON string with stock information
    """
    logger.info(f"Fetching stock information for medicine name '{name}'")
    
    medicines = queries.search_medicines_by_name(name, limit=10)
    
    if not medicines:
        return json.dumps({"error": f"No medicines found matching '{name}'"})
    
    results = []
    for medicine in medicines:
        # Calculate months of supply
        months_of_supply = 0
        if medicine.cpma and medicine.cpma > 0:
            months_of_supply = medicine.stk / medicine.cpma
        
        result = medicine.to_dict()
        result["months_of_supply"] = round(months_of_supply, 2)
        results.append(result)
    
    return json.dumps({
        "query": name,
        "count": len(results),
        "results": results
    }, indent=2)


@mcp.resource("locations://{diresa}")
def get_locations_resource(diresa: str) -> str:
    """Get locations for a specific DIRESA (health region).
    
    Args:
        diresa: DIRESA name
        
    Returns:
        JSON string with location information
    """
    logger.info(f"Fetching locations for DIRESA '{diresa}'")
    
    with queries.db_session() as session:
        # Get unique locations in this DIRESA
        query = """
            SELECT DISTINCT 
                nombre_ejecutora, 
                categoria,
                reportante,
                tipo_reportante
            FROM medicines
            WHERE diresa = :diresa
            ORDER BY nombre_ejecutora
        """
        
        locations = session.execute(query, {"diresa": diresa}).fetchall()
        
        if not locations:
            return json.dumps({"error": f"No locations found for DIRESA '{diresa}'"})
        
        # Format the locations
        formatted_locations = []
        for loc in locations:
            formatted_locations.append({
                "nombre_ejecutora": loc.nombre_ejecutora,
                "categoria": loc.categoria,
                "reportante": loc.reportante,
                "tipo_reportante": loc.tipo_reportante
            })
        
        return json.dumps({
            "diresa": diresa,
            "count": len(formatted_locations),
            "locations": formatted_locations
        }, indent=2)


@mcp.resource("statistics://stock")
def get_stock_statistics_resource() -> str:
    """Get overall stock statistics.
    
    Returns:
        JSON string with stock statistics
    """
    logger.info("Fetching overall stock statistics")
    
    # Get medicine statistics
    stats = queries.get_medicine_statistics()
    
    return json.dumps(stats, indent=2)


@mcp.resource("statistics://regions")
def get_regions_statistics_resource() -> str:
    """Get regional statistics.
    
    Returns:
        JSON string with regional statistics
    """
    logger.info("Fetching regional statistics")
    
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
    
    return json.dumps({
        "count": len(formatted_stats),
        "regions": formatted_stats
    }, indent=2)