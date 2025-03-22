"""
Database queries for the MedifinderMCP Server.
"""
import logging
from sqlalchemy import text, func
from app.db.connection import db_session
from app.models.medicines import Medicine
from app.config import MAX_SEARCH_RESULTS, SEARCH_SIMILARITY_THRESHOLD

logger = logging.getLogger(__name__)

def search_medicines_by_name(name, limit=MAX_SEARCH_RESULTS):
    """Search for medicines by name using fuzzy matching.
    
    Args:
        name (str): The medicine name to search for
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of matching medicines
    """
    with db_session() as session:
        # Use PostgreSQL's trigram similarity for fuzzy matching
        query = session.query(Medicine).filter(
            func.similarity(Medicine.nombre_prod, name) > SEARCH_SIMILARITY_THRESHOLD
        ).order_by(
            func.similarity(Medicine.nombre_prod, name).desc()
        ).limit(limit)
        
        return query.all()

def search_medicines_by_location(diresa, categoria=None, limit=MAX_SEARCH_RESULTS):
    """Search for medicines by location.
    
    Args:
        diresa (str): The DIRESA (health region)
        categoria (str, optional): The facility category
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of matching medicines
    """
    with db_session() as session:
        query = session.query(Medicine).filter(Medicine.diresa == diresa)
        
        if categoria:
            query = query.filter(Medicine.categoria == categoria)
            
        return query.limit(limit).all()

def get_medicine_by_id(medicine_id):
    """Get a medicine by its ID.
    
    Args:
        medicine_id (int): The medicine ID
        
    Returns:
        Medicine: The medicine object or None if not found
    """
    with db_session() as session:
        return session.query(Medicine).filter(Medicine.id == medicine_id).first()

def get_available_medicine_locations(medicine_name, min_stock=1):
    """Get locations where a medicine is available with stock.
    
    Args:
        medicine_name (str): The medicine name
        min_stock (int): Minimum stock required to consider available
        
    Returns:
        list: List of locations with available stock
    """
    with db_session() as session:
        query = session.query(
            Medicine.diresa,
            Medicine.categoria,
            Medicine.nombre_ejecutora,
            Medicine.reportante,
            Medicine.stk
        ).filter(
            func.lower(Medicine.nombre_prod).contains(func.lower(medicine_name)),
            Medicine.stk >= min_stock
        ).order_by(Medicine.stk.desc())
        
        return query.all()

def get_stock_status_by_region():
    """Get aggregate stock status by region.
    
    Returns:
        list: List of regions with their stock status
    """
    with db_session() as session:
        query = text("""
            SELECT 
                diresa, 
                COUNT(*) as total_medicines,
                SUM(CASE WHEN stk > 0 THEN 1 ELSE 0 END) as available_medicines,
                SUM(CASE WHEN indicador = 'Sobrestock' THEN 1 ELSE 0 END) as overstock,
                SUM(CASE WHEN indicador = 'Substock' THEN 1 ELSE 0 END) as understock,
                SUM(CASE WHEN indicador = 'Normostock' THEN 1 ELSE 0 END) as normalstock,
                SUM(CASE WHEN indicador = 'Desabastecido' THEN 1 ELSE 0 END) as outofstock
            FROM medicines
            GROUP BY diresa
            ORDER BY diresa
        """)
        
        return session.execute(query).fetchall()

def get_medicine_statistics():
    """Get overall medicine statistics.
    
    Returns:
        dict: Statistics about medicines in the database
    """
    with db_session() as session:
        total_count = session.query(func.count(Medicine.id)).scalar()
        available_count = session.query(func.count(Medicine.id)).filter(Medicine.stk > 0).scalar()
        overstock_count = session.query(func.count(Medicine.id)).filter(Medicine.indicador == 'Sobrestock').scalar()
        understock_count = session.query(func.count(Medicine.id)).filter(Medicine.indicador == 'Substock').scalar()
        outofstock_count = session.query(func.count(Medicine.id)).filter(Medicine.indicador == 'Desabastecido').scalar()
        
        return {
            "total": total_count,
            "available": available_count,
            "overstock": overstock_count,
            "understock": understock_count,
            "outofstock": outofstock_count,
            "availability_rate": round(available_count / total_count * 100, 2) if total_count > 0 else 0
        }