"""
MCP tools for the MedifinderMCP Server.
"""
import logging
import json
import os
from typing import Dict, List, Optional, Any

from mcp.server.fastmcp import FastMCP, Context

from app.db import queries
from app.models.product import Product
from app.models.inventory import Inventory
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
    mcp.tool()(diagnose_database)
    mcp.tool()(troubleshoot_connection)
    mcp.tool()(create_database_schema)
    
    logger.info("MCP tools registered")


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
    
    try:
        results = []
        
        if search_type.lower() == "name":
            # This now returns dictionaries, not model instances
            results = queries.search_medicines_by_name(query, limit=limit)
        
        elif search_type.lower() == "location":
            if not location:
                return {"error": "Location parameter is required for location search"}
                
            products_with_inventory = queries.search_medicines_by_location(
                location, 
                categoria=category, 
                limit=limit
            )
            
            # These are already dictionaries
            results = products_with_inventory
        
        else:
            return {"error": f"Invalid search type: {search_type}"}
        
        return {
            "query": query,
            "search_type": search_type,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error in search_medicines: {str(e)}")
        return {
            "error": f"Database error: {str(e)}",
            "query": query,
            "search_type": search_type,
            "count": 0,
            "results": []
        }


def get_medicine_locations(medicine_name: str, min_stock: int = 1) -> Dict[str, Any]:
    """Get locations where a medicine is available.
    
    Args:
        medicine_name: The name of the medicine to search for
        min_stock: Minimum stock required to consider available
        
    Returns:
        Dictionary with available locations
    """
    logger.info(f"Finding locations for medicine '{medicine_name}' with min stock {min_stock}")
    
    try:
        # Now returns a list of dictionaries
        locations = queries.get_available_medicine_locations(medicine_name, min_stock)
        
        return {
            "medicine_name": medicine_name,
            "min_stock": min_stock,
            "count": len(locations),
            "locations": locations
        }
    except Exception as e:
        logger.error(f"Error in get_medicine_locations: {str(e)}")
        return {
            "error": f"Database error: {str(e)}",
            "medicine_name": medicine_name,
            "min_stock": min_stock,
            "count": 0,
            "locations": []
        }


def get_medicine_stock(medicine_id: int) -> Dict[str, Any]:
    """Get stock information for a specific medicine.
    
    Args:
        medicine_id: The ID of the medicine
        
    Returns:
        Dictionary with medicine stock information
    """
    logger.info(f"Getting stock information for medicine ID {medicine_id}")
    
    try:
        product = queries.get_medicine_by_id(medicine_id)
        
        if not product:
            return {"error": f"Medicine with ID {medicine_id} not found"}
        
        # Get inventory information for this product
        with queries.db_session() as session:
            inventory_list = session.query(Inventory).filter(
                Inventory.product_id == medicine_id
            ).all()
            
            inventory_data = [inv.to_dict() for inv in inventory_list]
            
            # Calculate total stock across all locations
            total_stock = sum(inv.current_stock for inv in inventory_list if inv.current_stock)
            
            # Calculate average monthly consumption
            avg_consumption = sum(inv.avg_monthly_consumption for inv in inventory_list if inv.avg_monthly_consumption) / len(inventory_list) if inventory_list else 0
            
            # Calculate months of supply
            months_of_supply = round(total_stock / avg_consumption, 2) if avg_consumption > 0 else 0
        
        result = product.to_dict()
        result["total_stock"] = total_stock
        result["avg_monthly_consumption"] = round(avg_consumption, 2)
        result["months_of_supply"] = months_of_supply
        result["inventory_locations"] = len(inventory_data)
        result["inventory"] = inventory_data
        
        return result
    except Exception as e:
        logger.error(f"Error in get_medicine_stock: {str(e)}")
        return {
            "error": f"Database error: {str(e)}",
            "medicine_id": medicine_id
        }


def get_regional_statistics() -> Dict[str, Any]:
    """Get medicine statistics by region.
    
    Returns:
        Dictionary with regional statistics
    """
    logger.info("Getting regional statistics")
    
    try:
        # Get regional statistics
        regional_stats = queries.get_stock_status_by_region()
        
        # Format the results (already in the right format)
        
        return {
            "count": len(regional_stats),
            "regions": regional_stats
        }
    except Exception as e:
        logger.error(f"Error in get_regional_statistics: {str(e)}")
        return {
            "error": f"Database error: {str(e)}",
            "count": 0,
            "regions": []
        }


def get_medicine_status() -> Dict[str, Any]:
    """Get overall medicine statistics.
    
    Returns:
        Dictionary with medicine statistics
    """
    logger.info("Getting overall medicine statistics")
    
    try:
        # Get medicine statistics
        stats = queries.get_medicine_statistics()
        
        return stats
    except Exception as e:
        logger.error(f"Error in get_medicine_status: {str(e)}")
        return {
            "error": f"Database error: {str(e)}"
        }

def create_database_schema() -> Dict[str, Any]:
    """Tool to create all database tables based on the SQLAlchemy models.
    
    Returns:
        Dictionary with results of table creation
    """
    logger.info("Creating database schema")
    
    result = {
        "action": "create_schema",
        "tables_created": [],
        "errors": [],
        "status": "unknown"
    }
    
    try:
        # Import the create_all function and Base from connection
        from app.db.connection import Base, engine
        from app.models.region import Region
        from app.models.medical_center import MedicalCenter
        from app.models.product_type import ProductType
        from app.models.product import Product
        from app.models.inventory import Inventory
        from app.models.user import User
        from app.models.search_history import SearchHistory
        
        # Get existing tables before creation
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        # Get tables after creation
        inspector = inspect(engine)
        new_tables = set(inspector.get_table_names())
        
        # Determine which tables were created
        created_tables = new_tables - existing_tables
        result["tables_created"] = list(created_tables)
        result["tables_already_existed"] = list(existing_tables)
        
        # Test that we can create a sample record
        if "region" in new_tables and "region" not in existing_tables:
            try:
                from app.db.connection import db_session
                with db_session() as session:
                    # Create a test region
                    test_region = Region(name="Test Region", code="TEST")
                    session.add(test_region)
                    session.commit()
                    
                    # Verify it was created
                    count = session.query(Region).count()
                    result["test_record_created"] = True
                    result["record_count"] = count
            except Exception as test_e:
                result["test_record_error"] = str(test_e)
        
        if created_tables:
            result["status"] = "success"
            result["message"] = f"Successfully created {len(created_tables)} tables: {', '.join(created_tables)}"
        else:
            result["status"] = "no_change"
            result["message"] = "No new tables were created. Schema might already exist."
        
    except Exception as e:
        logger.error(f"Error creating database schema: {e}")
        result["status"] = "error"
        result["errors"].append(str(e))
        result["message"] = f"Failed to create database schema: {str(e)}"
    
    return result

def diagnose_database() -> Dict[str, Any]:
    """Diagnostic tool to check database connection and content.
    
    Returns:
        Dictionary with diagnostic information
    """
    logger.info("Running database diagnostics")
    
    try:
        # Import the engine directly
        from app.db.connection import engine, db_session
        
        results = {
            "connection": "Unknown",
            "connection_url": str(engine.url).replace(os.environ.get("DB_PASSWORD", ""), "****"),
            "tables": {},
            "sample_data": {},
            "errors": []
        }
        
        # Test database connection
        with engine.connect() as conn:
            results["connection"] = "Connected"
            
            # Get database metadata
            from sqlalchemy import inspect, MetaData
            inspector = inspect(engine)
            
            # List all tables in the database
            tables = inspector.get_table_names()
            results["tables_found"] = tables
            
            if not tables:
                results["errors"].append("No tables found in the database")
        
        # Check if our model tables exist in the database
        expected_tables = ["region", "medical_center", "product_type", "product", "inventory"]
        for table_name in expected_tables:
            results["tables"][table_name] = table_name in tables
        
        # Try to query each table if it exists
        with db_session() as session:
            if "region" in tables:
                # Import models here to avoid circular imports
                from app.models.region import Region
                count = session.query(Region).count()
                results["tables"]["region_count"] = count
                if count > 0:
                    results["sample_data"]["region"] = session.query(Region).first().to_dict()
            
            if "product" in tables:
                from app.models.product import Product
                count = session.query(Product).count()
                results["tables"]["product_count"] = count
                if count > 0:
                    results["sample_data"]["product"] = session.query(Product).first().to_dict()
                    
            if "inventory" in tables:
                from app.models.inventory import Inventory
                count = session.query(Inventory).count()
                results["tables"]["inventory_count"] = count
                if count > 0:
                    results["sample_data"]["inventory"] = session.query(Inventory).first().to_dict()
        
        results["connection_successful"] = True
        
    except Exception as e:
        logger.error(f"Diagnostic error: {e}")
        results = {
            "connection": "Error",
            "connection_successful": False,
            "error": f"Database error: {str(e)}",
            "suggestion": "Check your database connection settings in .env file and make sure the database exists."
        }
    
    return results

def troubleshoot_connection() -> Dict[str, Any]:
    """Tool to troubleshoot database connection issues.
    
    Returns:
        Dictionary with troubleshooting information
    """
    logger.info("Troubleshooting database connection")
    
    result = {
        "environment": {},
        "connection_test": {},
        "table_check": {},
        "recommendations": []
    }
    
    try:
        # Check environment variables
        from app.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DATABASE_URL
        
        # Add environment info (masking password)
        result["environment"] = {
            "DB_HOST": DB_HOST,
            "DB_PORT": DB_PORT,
            "DB_NAME": DB_NAME,
            "DB_USER": DB_USER,
            "DB_PASSWORD": "****" if DB_PASSWORD else "Not set",
            "DATABASE_URL": DATABASE_URL.replace(DB_PASSWORD, "****") if DB_PASSWORD else DATABASE_URL
        }
        
        # Test basic connection
        from app.db.connection import engine
        
        try:
            with engine.connect() as conn:
                result["connection_test"]["basic_connection"] = "Success"
                
                # Try a simple query
                from sqlalchemy import text
                try:
                    version = conn.execute(text("SELECT version()")).scalar()
                    result["connection_test"]["version"] = version
                except Exception as query_e:
                    result["connection_test"]["version_error"] = str(query_e)
                    # Try a simpler query
                    try:
                        test = conn.execute(text("SELECT 1")).scalar()
                        result["connection_test"]["simple_query"] = "Success" if test == 1 else "Failed"
                    except Exception as simple_e:
                        result["connection_test"]["simple_query_error"] = str(simple_e)
                
                # Check if tables exist
                from sqlalchemy import inspect
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                result["table_check"]["tables_found"] = tables
                
                # Check our expected tables
                expected_tables = ["region", "medical_center", "product_type", "product", "inventory"]
                for table in expected_tables:
                    result["table_check"][f"{table}_exists"] = table in tables
                    
                    # If table exists, check columns
                    if table in tables:
                        try:
                            columns = [col["name"] for col in inspector.get_columns(table)]
                            result["table_check"][f"{table}_columns"] = columns
                        except Exception as col_e:
                            result["table_check"][f"{table}_columns_error"] = str(col_e)
                
                # Add recommendations based on findings
                if not tables:
                    result["recommendations"].append("No tables found in the database. You may need to create the database schema.")
                    result["recommendations"].append("Run the init_db function to create all tables.")
                else:
                    missing_tables = [table for table in expected_tables if table not in tables]
                    if missing_tables:
                        result["recommendations"].append(f"Missing expected tables: {', '.join(missing_tables)}. Check if your database schema matches the application models.")
                        result["recommendations"].append("Run the init_db function to create all missing tables.")
        
        except Exception as conn_e:
            result["connection_test"]["error"] = str(conn_e)
            result["recommendations"].append(f"Connection error: {str(conn_e)}. Check your database credentials and ensure the database server is running.")
            result["recommendations"].append(f"Verify PostgreSQL is running on port {DB_PORT} and that the database '{DB_NAME}' exists.")
    
    except Exception as e:
        result["error"] = str(e)
        result["recommendations"].append(f"Configuration error: {str(e)}. Check your environment variables and .env file.")
    
    # Add general recommendations
    if not result.get("recommendations"):
        result["recommendations"].append("Database connection successful, but tables may be empty. Check if you have imported data into the database.")
        result["recommendations"].append("Make sure you have run the data ingestion process to populate the tables.")
    
    return result