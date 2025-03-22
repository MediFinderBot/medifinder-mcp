"""
Database queries for the MedifinderMCP Server.
"""
import logging
from sqlalchemy import func, or_

from app.db.connection import db_session
from app.models.region import Region
from app.models.medical_center import MedicalCenter
from app.models.product_type import ProductType
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.user import User
from app.models.search_history import SearchHistory
from app.config import MAX_SEARCH_RESULTS

logger = logging.getLogger(__name__)

def search_medicines_by_name(name, limit=MAX_SEARCH_RESULTS):
    """Search for medicines by name using LIKE matching.
    
    Args:
        name (str): The medicine name to search for
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of matching medicines
    """
    with db_session() as session:
        search_term = f"%{name}%"
        query = session.query(Product).filter(
            Product.name.ilike(search_term)
        ).limit(limit)
        
        # Fetch all results within this session and convert to dictionaries
        results = [product.to_dict() for product in query.all()]
        return results

def search_medicines_by_location(diresa, categoria=None, limit=MAX_SEARCH_RESULTS):
    """Search for medicines by location.
    
    Args:
        diresa (str): The DIRESA (health region)
        categoria (str, optional): The facility category
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of matching medicines with inventory
    """
    with db_session() as session:
        # Join Product, Inventory, MedicalCenter, and Region
        query = session.query(Product, Inventory).join(
            Inventory, Product.product_id == Inventory.product_id
        ).join(
            MedicalCenter, Inventory.center_id == MedicalCenter.center_id
        ).join(
            Region, MedicalCenter.region_id == Region.region_id
        ).filter(
            Region.name.ilike(f"%{diresa}%")
        )
        
        if categoria:
            query = query.filter(MedicalCenter.category.ilike(f"%{categoria}%"))
            
        query = query.limit(limit)
        
        # Process results
        results = []
        for product, inventory in query.all():
            product_dict = product.to_dict()
            product_dict["inventory"] = inventory.to_dict()
            results.append(product_dict)
            
        return results

def get_medicine_by_id(medicine_id):
    """Get a medicine by its ID.
    
    Args:
        medicine_id (int): The medicine ID
        
    Returns:
        Product: The product object or None if not found
    """
    with db_session() as session:
        return session.query(Product).filter(Product.product_id == medicine_id).first()

def get_available_medicine_locations(medicine_name, min_stock=1):
    """Get locations where a medicine is available with stock.
    
    Args:
        medicine_name (str): The medicine name
        min_stock (int): Minimum stock required to consider available
        
    Returns:
        list: List of dictionaries with location information
    """
    with db_session() as session:
        search_term = f"%{medicine_name}%"
        
        query = session.query(
            Region.name.label('region'),
            MedicalCenter.category,
            MedicalCenter.name.label('center_name'),
            MedicalCenter.reporter_name,
            Inventory.current_stock.label('stock')
        ).select_from(Product).join(
            Inventory, Product.product_id == Inventory.product_id
        ).join(
            MedicalCenter, Inventory.center_id == MedicalCenter.center_id
        ).join(
            Region, MedicalCenter.region_id == Region.region_id
        ).filter(
            Product.name.ilike(search_term),
            Inventory.current_stock >= min_stock
        ).order_by(Inventory.current_stock.desc())
        
        # Convert results to dictionaries immediately
        results = []
        for row in query.all():
            results.append({
                "region": row.region,
                "category": row.category,
                "center_name": row.center_name,
                "reporter_name": row.reporter_name,
                "stock": row.stock
            })
        
        return results

def get_stock_status_by_region():
    """Get aggregate stock status by region.
    
    Returns:
        list: List of regions with their stock status
    """
    with db_session() as session:
        regions = session.query(Region).all()
        results = []
        
        for region in regions:
            # Count total products in inventory for this region
            total_count = session.query(func.count(Inventory.inventory_id)).join(
                MedicalCenter, Inventory.center_id == MedicalCenter.center_id
            ).filter(
                MedicalCenter.region_id == region.region_id
            ).scalar()
            
            # Count available products (stock > 0)
            available_count = session.query(func.count(Inventory.inventory_id)).join(
                MedicalCenter, Inventory.center_id == MedicalCenter.center_id
            ).filter(
                MedicalCenter.region_id == region.region_id,
                Inventory.current_stock > 0
            ).scalar()
            
            # Count by indicator
            overstock = session.query(func.count(Inventory.inventory_id)).join(
                MedicalCenter, Inventory.center_id == MedicalCenter.center_id
            ).filter(
                MedicalCenter.region_id == region.region_id,
                Inventory.status_indicator == 'Sobrestock'
            ).scalar()
            
            understock = session.query(func.count(Inventory.inventory_id)).join(
                MedicalCenter, Inventory.center_id == MedicalCenter.center_id
            ).filter(
                MedicalCenter.region_id == region.region_id,
                Inventory.status_indicator == 'Substock'
            ).scalar()
            
            normalstock = session.query(func.count(Inventory.inventory_id)).join(
                MedicalCenter, Inventory.center_id == MedicalCenter.center_id
            ).filter(
                MedicalCenter.region_id == region.region_id,
                Inventory.status_indicator == 'Normostock'
            ).scalar()
            
            outofstock = session.query(func.count(Inventory.inventory_id)).join(
                MedicalCenter, Inventory.center_id == MedicalCenter.center_id
            ).filter(
                MedicalCenter.region_id == region.region_id,
                Inventory.status_indicator == 'Desabastecido'
            ).scalar()
            
            results.append({
                "region": region.name,
                "total_medicines": total_count,
                "available_medicines": available_count,
                "overstock": overstock,
                "understock": understock,
                "normalstock": normalstock,
                "outofstock": outofstock
            })
        
        return results

def get_medicine_statistics():
    """Get overall medicine statistics.
    
    Returns:
        dict: Statistics about medicines in the database
    """
    with db_session() as session:
        total_count = session.query(func.count(Inventory.inventory_id)).scalar()
        available_count = session.query(func.count(Inventory.inventory_id)).filter(
            Inventory.current_stock > 0
        ).scalar()
        
        overstock_count = session.query(func.count(Inventory.inventory_id)).filter(
            Inventory.status_indicator == 'Sobrestock'
        ).scalar()
        
        understock_count = session.query(func.count(Inventory.inventory_id)).filter(
            Inventory.status_indicator == 'Substock'
        ).scalar()
        
        outofstock_count = session.query(func.count(Inventory.inventory_id)).filter(
            Inventory.status_indicator == 'Desabastecido'
        ).scalar()
        
        normalstock_count = session.query(func.count(Inventory.inventory_id)).filter(
            Inventory.status_indicator == 'Normostock'
        ).scalar()
        
        # Count unique products
        unique_products = session.query(func.count(func.distinct(Product.product_id))).scalar()
        
        # Count unique medical centers
        unique_centers = session.query(func.count(func.distinct(MedicalCenter.center_id))).scalar()
        
        # Count unique regions
        unique_regions = session.query(func.count(func.distinct(Region.region_id))).scalar()
        
        return {
            "total_inventory_records": total_count,
            "available_inventory": available_count,
            "overstock": overstock_count,
            "understock": understock_count,
            "normalstock": normalstock_count,
            "outofstock": outofstock_count,
            "unique_products": unique_products,
            "unique_medical_centers": unique_centers,
            "unique_regions": unique_regions,
            "availability_rate": round(available_count / total_count * 100, 2) if total_count > 0 else 0
        }

def diagnose_database():
    """Get diagnostic information about the database.
    
    Returns:
        dict: Diagnostic information about database tables and content
    """
    from app.db.connection import engine
    
    with db_session() as session:
        result = {
            "tables": {},
            "sample_data": {},
            "connection_url": str(engine.url).replace(":password@", ":******@"),
        }
        
        # Count records in each table
        try:
            result["tables"]["regions"] = session.query(func.count(Region.region_id)).scalar()
        except Exception as e:
            result["tables"]["regions"] = f"Error: {str(e)}"
            
        try:
            result["tables"]["medical_centers"] = session.query(func.count(MedicalCenter.center_id)).scalar()
        except Exception as e:
            result["tables"]["medical_centers"] = f"Error: {str(e)}"
            
        try:
            result["tables"]["product_types"] = session.query(func.count(ProductType.type_id)).scalar()
        except Exception as e:
            result["tables"]["product_types"] = f"Error: {str(e)}"
            
        try:
            result["tables"]["products"] = session.query(func.count(Product.product_id)).scalar()
        except Exception as e:
            result["tables"]["products"] = f"Error: {str(e)}"
            
        try:
            result["tables"]["inventory"] = session.query(func.count(Inventory.inventory_id)).scalar()
        except Exception as e:
            result["tables"]["inventory"] = f"Error: {str(e)}"
        
        # Get sample data if available
        if result["tables"]["products"] and not isinstance(result["tables"]["products"], str) and result["tables"]["products"] > 0:
            try:
                sample_product = session.query(Product).first()
                result["sample_data"]["product"] = sample_product.to_dict() if sample_product else None
            except Exception as e:
                result["sample_data"]["product"] = f"Error: {str(e)}"
            
        if result["tables"]["regions"] and not isinstance(result["tables"]["regions"], str) and result["tables"]["regions"] > 0:
            try:
                sample_region = session.query(Region).first()
                result["sample_data"]["region"] = sample_region.to_dict() if sample_region else None
            except Exception as e:
                result["sample_data"]["region"] = f"Error: {str(e)}"
            
        if result["tables"]["inventory"] and not isinstance(result["tables"]["inventory"], str) and result["tables"]["inventory"] > 0:
            try:
                sample_inventory = session.query(Inventory).first()
                result["sample_data"]["inventory"] = sample_inventory.to_dict() if sample_inventory else None
            except Exception as e:
                result["sample_data"]["inventory"] = f"Error: {str(e)}"
        
        # Also try a simple raw SQL query to check if database is actually accessible
        try:
            from sqlalchemy import text
            result["raw_sql_test"] = bool(session.execute(text("SELECT 1")).scalar())
        except Exception as e:
            result["raw_sql_test"] = f"Error: {str(e)}"
        
        return result