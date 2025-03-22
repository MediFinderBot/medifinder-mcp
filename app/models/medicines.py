"""
Medicine model for the MedifinderMCP Server.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.db.connection import Base

class Medicine(Base):
    """Medicine model representing a row in the medicines table."""
    __tablename__ = 'medicines'
    
    id = Column(Integer, primary_key=True)
    nombre_ejecutora = Column(String, nullable=False)
    diresa = Column(String, nullable=False)
    categoria = Column(String)
    codpre = Column(String)
    reportante = Column(String)
    tipsum = Column(String)
    codmed = Column(String)
    nombre_prod = Column(String, nullable=False)
    tipo_prod = Column(String)
    stk = Column(Integer)
    cpma = Column(Float)
    consumo_acum_4m = Column(Integer)
    med = Column(Float)
    fechareporte = Column(DateTime)
    estado = Column(String)
    institucion = Column(String)
    tipo_reportante = Column(String)
    consumo_ult_mes = Column(Integer)
    stk_ult_mes = Column(Integer)
    indicador = Column(String)
    cpma_hace_12_meses_a = Column(Float)
    cpma_hace_24_meses_a = Column(Float)
    cpma_hace_36_meses_a = Column(Float)
    consumo_acum_12m = Column(Integer)
    
    # Metadata fields
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        """String representation of the medicine."""
        return f"<Medicine(id={self.id}, nombre_prod='{self.nombre_prod}')>"
    
    def to_dict(self):
        """Convert the medicine to a dictionary.
        
        Returns:
            dict: Dictionary representation of the medicine
        """
        return {
            "id": self.id,
            "nombre_ejecutora": self.nombre_ejecutora,
            "diresa": self.diresa,
            "categoria": self.categoria,
            "reportante": self.reportante,
            "nombre_prod": self.nombre_prod,
            "tipo_prod": self.tipo_prod,
            "stk": self.stk,
            "cpma": self.cpma,
            "consumo_acum_4m": self.consumo_acum_4m,
            "med": self.med,
            "fechareporte": self.fechareporte.isoformat() if self.fechareporte else None,
            "estado": self.estado,
            "institucion": self.institucion,
            "tipo_reportante": self.tipo_reportante,
            "consumo_ult_mes": self.consumo_ult_mes,
            "stk_ult_mes": self.stk_ult_mes,
            "indicador": self.indicador
        }