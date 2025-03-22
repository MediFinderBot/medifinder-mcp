"""
MCP resources for the MedifinderMCP Server.
"""
import logging
import json
from typing import Dict, Any
from sqlalchemy import func

from mcp.server.fastmcp import FastMCP, Context

from app.db import queries
from app.db.connection import db_session
from app.models.region import Region
from app.models.medical_center import MedicalCenter
from app.models.product_type import ProductType
from app.models.product import Product
from app.models.inventory import Inventory

logger = logging.getLogger(__name__)

def register_resources(mcp: FastMCP):
    """Register MCP resources with the server.
    
    Args:
        mcp (FastMCP): The MCP server
    """
    logger.info("Registering MCP resources...")
    
    # Register all resources with the MCP server
    # Resource URI patterns
    mcp.resource("product://{id}")(get_product_resource)
    mcp.resource("stock://{name}")(get_product_stock_resource)
    mcp.resource("locations://{region}")(get_locations_resource)
    mcp.resource("statistics://stock")(get_stock_statistics_resource)
    mcp.resource("statistics://regions")(get_regions_statistics_resource)
    
    logger.info("MCP resources registered")


def get_product_resource(id: str) -> str:
    """Get product details by ID.
    
    Args:
        id: Product ID
        
    Returns:
        JSON string with product details
    """
    logger.info(f"Fetching product resource for ID {id}")
    
    try:
        product_id = int(id)
    except ValueError:
        return json.dumps({"error": f"Invalid product ID: {id}"})
    
    product = queries.get_medicine_by_id(product_id)
    
    if not product:
        return json.dumps({"error": f"Product with ID {id} not found"})
    
    # Get inventory information for this product
    with db_session() as session:
        inventories = session.query(Inventory).filter(
            Inventory.product_id == product_id
        ).all()
        
        inventory_data = [inv.to_dict() for inv in inventories]
    
    result = product.to_dict()
    result["inventories"] = inventory_data
    
    return json.dumps(result, indent=2)


def get_product_stock_resource(name: str) -> str:
    """Get stock information for a product by name.
    
    Args:
        name: Product name
        
    Returns:
        JSON string with stock information
    """
    logger.info(f"Fetching stock information for product name '{name}'")
    
    products = queries.search_medicines_by_name(name, limit=10)
    
    if not products:
        return json.dumps({"error": f"No products found matching '{name}'"})
    
    results = []
    for product in products:
        # Get inventory information for this product
        with db_session() as session:
            inventories = session.query(Inventory).filter(
                Inventory.product_id == product.product_id
            ).all()
            
            inventory_data = [inv.to_dict() for inv in inventories]
            
            # Calculate total stock across all locations
            total_stock = sum(inv.current_stock for inv in inventories if inv.current_stock)
            
            # Calculate average monthly consumption
            avg_consumption = sum(inv.avg_monthly_consumption for inv in inventories if inv.avg_monthly_consumption) / len(inventories) if inventories else 0
            
            # Calculate months of supply
            months_of_supply = round(total_stock / avg_consumption, 2) if avg_consumption > 0 else 0
        
        result = product.to_dict()
        result["total_stock"] = total_stock
        result["avg_monthly_consumption"] = round(avg_consumption, 2)
        result["months_of_supply"] = months_of_supply
        result["inventory_count"] = len(inventory_data)
        result["inventory_summary"] = [
            {
                "center_id": inv["center_id"], 
                "center_name": inv["center_name"],
                "current_stock": inv["current_stock"],
                "status_indicator": inv["status_indicator"]
            } for inv in inventory_data[:5]  # Just show first 5 for summary
        ]
        results.append(result)
    
    return json.dumps({
        "query": name,
        "count": len(results),
        "results": results
    }, indent=2)


def get_locations_resource(region: str) -> str:
    """Get locations for a specific region.
    
    Args:
        region: Region name
        
    Returns:
        JSON string with location information
    """
    logger.info(f"Fetching locations for region '{region}'")
    
    with db_session() as session:
        # Get the region
        db_region = session.query(Region).filter(
            Region.name.ilike(f"%{region}%")
        ).first()
        
        if not db_region:
            return json.dumps({"error": f"No region found matching '{region}'"})
        
        # Get medical centers in this region
        centers = session.query(MedicalCenter).filter(
            MedicalCenter.region_id == db_region.region_id
        ).order_by(MedicalCenter.name).all()
        
        if not centers:
            return json.dumps({"error": f"No medical centers found in region '{region}'"})
        
        # Format the centers
        formatted_centers = [center.to_dict() for center in centers]
        
        return json.dumps({
            "region": db_region.to_dict(),
            "count": len(formatted_centers),
            "centers": formatted_centers
        }, indent=2)


def get_stock_statistics_resource() -> str:
    """Get overall stock statistics.
    
    Returns:
        JSON string with stock statistics
    """
    logger.info("Fetching overall stock statistics")
    
    # Get medicine statistics
    stats = queries.get_medicine_statistics()
    
    return json.dumps(stats, indent=2)


def get_regions_statistics_resource() -> str:
    """Get regional statistics.
    
    Returns:
        JSON string with regional statistics
    """
    logger.info("Fetching regional statistics")
    
    # Get regional statistics
    regional_stats = queries.get_stock_status_by_region()
    
    return json.dumps({
        "count": len(regional_stats),
        "regions": regional_stats
    }, indent=2)