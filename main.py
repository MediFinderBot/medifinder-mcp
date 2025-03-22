#!/usr/bin/env python3
"""
MedifinderMCP Server - Main Entry Point
A Model Context Protocol server for medicine inventory queries.
"""
import os
import logging

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Environment variables loaded from .env file")
except ImportError:
    print("python-dotenv package not found. Using environment variables from system.")
    # Continue without dotenv as environment variables are set in Claude config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("medifinder-mcp")

# Import the MCP server
from app.mcp.server import create_mcp_server

# Create the MCP server - expose at module level for MCP CLI discovery
mcp = create_mcp_server()

def main():
    """Main entry point for the application."""
    logger.info("Starting MedifinderMCP Server...")
    
    # Run the server
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        logger.info("Server shutdown complete.")

if __name__ == "__main__":
    main()