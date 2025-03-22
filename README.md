# MedifinderMCP Server

An MCP (Model Context Protocol) server for medicine inventory queries.

## Overview

The MedifinderMCP Server provides tools and resources for querying a medicine inventory database. It exposes functionality through the Model Context Protocol, allowing AI assistants and other clients to:

- Search for medicines by name or location
- Check medicine availability at different healthcare facilities
- Get stock information for specific medicines
- View statistics on medicine availability by region
- Analyze stock status across the healthcare system

## Project Structure

```
medifinder-mcp/
├── app/
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py    # Database connection handling
│   │   └── queries.py       # SQL queries
│   ├── models/
│   │   ├── __init__.py
│   │   └── medicines.py     # Data models
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py        # MCP server setup
│   │   ├── tools.py         # Tool implementations
│   │   ├── resources.py     # Resource implementations
│   │   └── prompts.py       # Prompt templates
│   └── utils/
│       ├── __init__.py
│       └── helpers.py       # Helper functions
├── main.py                  # Application entry point
├── requirements.txt         # Dependencies
└── README.md                # Documentation
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/medifinder-mcp.git
   cd medifinder-mcp
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables by creating a `.env` file:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=medifinder
   DB_USER=medifinder
   DB_PASSWORD=your_password
   DEBUG=True
   ENV=development
   ```

## Usage

### Running the Server

To start the MCP server:

```
python main.py
```

### Integration with Claude

The MCP server can be installed in Claude Desktop using the MCP CLI:

```
mcp install main.py
```

### Development Mode

For testing and debugging:

```
mcp dev main.py
```

## MCP Capabilities

### Tools

- `search_medicines`: Search for medicines by name or location
- `get_medicine_locations`: Find locations where a medicine is available
- `get_medicine_stock`: Get stock information for a specific medicine
- `get_regional_statistics`: Get medicine statistics by region
- `get_medicine_status`: Get overall medicine statistics

### Resources

- `medicine://{id}`: Get medicine details by ID
- `stock://{name}`: Get stock information for a medicine by name
- `locations://{diresa}`: Get locations for a specific health region
- `statistics://stock`: Get overall stock statistics
- `statistics://regions`: Get regional statistics

### Prompts

- `medicine_search_prompt`: Template for searching medicines by name
- `medicine_availability_prompt`: Template for checking medicine availability
- `medicine_statistics_prompt`: Template for analyzing medicine statistics
- `regional_availability_prompt`: Template for analyzing regional medicine availability

## License

[MIT License](LICENSE)

## Contributors

- Your Name - Initial work