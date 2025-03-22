"""
Configuration module for the MedifinderMCP Server.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "medifinder")
DB_USER = os.getenv("DB_USER", "medifinder")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Application configuration
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ENV = os.getenv("ENV", "development")
SERVER_NAME = os.getenv("SERVER_NAME", "MedifinderMCP")
SERVER_VERSION = os.getenv("SERVER_VERSION", "1.0.0")

# MCP server configuration
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "MedifinderMCP")
MCP_SERVER_DESCRIPTION = os.getenv("MCP_SERVER_DESCRIPTION", 
                                   "MCP server for medicine inventory queries")

# Connection string for SQLAlchemy
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Search configuration
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "50"))
SEARCH_SIMILARITY_THRESHOLD = float(os.getenv("SEARCH_SIMILARITY_THRESHOLD", "0.3"))