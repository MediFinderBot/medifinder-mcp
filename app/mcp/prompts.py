"""
MCP prompts for the MedifinderMCP Server.
"""
import logging
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

logger = logging.getLogger(__name__)

def register_prompts(mcp: FastMCP):
    """Register MCP prompts with the server.
    
    Args:
        mcp (FastMCP): The MCP server
    """
    logger.info("Registering MCP prompts...")
    
    # Register all prompts with the MCP server
    mcp.prompt()(medicine_search_prompt)
    mcp.prompt()(medicine_availability_prompt)
    mcp.prompt()(medicine_statistics_prompt)
    mcp.prompt()(regional_availability_prompt)
    
    logger.info("MCP prompts registered")


def medicine_search_prompt(medicine_name: str) -> str:
    """Create a prompt for searching medicines by name.
    
    Args:
        medicine_name: The name of the medicine to search for
        
    Returns:
        Formatted prompt string
    """
    return f"""Please search for medicines that match the name "{medicine_name}" and provide a summary of the results.
    
Use the search_medicines tool with the following parameters:
- query: "{medicine_name}"
- search_type: "name"

For each medicine found, please include:
1. The full medicine name
2. The current stock level
3. The health facility name
4. The health region (DIRESA)
5. The stock status indicator

If multiple medicines are found, list them in order of closest name match first.
If no medicines are found, suggest alternative search terms."""


def medicine_availability_prompt(medicine_name: str, diresa: str = None) -> list[base.Message]:
    """Create a prompt for checking medicine availability.
    
    Args:
        medicine_name: The name of the medicine to check
        diresa: Optional DIRESA (health region) to filter by
        
    Returns:
        List of prompt messages
    """
    diresa_filter = f" in the {diresa} region" if diresa else ""
    
    return [
        base.UserMessage(f"I need to find where {medicine_name} is available{diresa_filter}."),
        base.AssistantMessage("I'll help you find where this medicine is available. Let me check the current stock levels."),
        base.UserMessage(f"""Please use the get_medicine_locations tool to find facilities with {medicine_name} in stock.
        
If specific locations are found:
1. List the facilities with their stock levels, sorted by highest stock first
2. Provide the facility category and region
3. Suggest when the patient should call ahead to confirm availability

If no locations are found with stock:
1. Check if the medicine name might be misspelled
2. Suggest checking for alternative generic versions
3. Recommend checking back later as inventory is updated regularly""")
    ]


def medicine_statistics_prompt() -> str:
    """Create a prompt for analyzing medicine statistics.
    
    Returns:
        Formatted prompt string
    """
    return """Please analyze the current medicine inventory statistics and provide a comprehensive summary.

Use the get_medicine_status tool to retrieve overall statistics, and then analyze the following aspects:

1. Overall availability: What percentage of medicines are currently in stock?
2. Stock status breakdown: What percentage of medicines are in overstock, normal stock, understock, or out of stock?
3. Potential issues: Are there critical medicines that are out of stock or in understock?
4. Trends: Are there any notable trends in medicine consumption or stock levels?

Please provide your analysis in a clear, structured format with sections for each aspect mentioned above. Include recommendations for inventory management if appropriate."""


def regional_availability_prompt(diresa: str = None) -> list[base.Message]:
    """Create a prompt for analyzing regional medicine availability.
    
    Args:
        diresa: Optional DIRESA (health region) to analyze
        
    Returns:
        List of prompt messages
    """
    if diresa:
        region_text = f"for the {diresa} region"
    else:
        region_text = "across all regions"
    
    return [
        base.UserMessage(f"Can you analyze medicine availability {region_text}?"),
        base.AssistantMessage("I'll analyze the medicine availability data for you."),
        base.UserMessage(f"""Please use the get_regional_statistics tool to retrieve regional statistics{'' if not diresa else ' and filter for the ' + diresa + ' region'}.

For your analysis, please:

1. Calculate and compare the overall availability percentages across regions
2. Identify regions with the highest and lowest availability rates
3. Analyze the distribution of overstock, normal stock, understock, and out of stock medications
4. Highlight any regions with critical shortages or unusual patterns
5. Provide a summary of key findings and potential areas of concern

Present the information in a clear, structured format that would be helpful for health administrators and planners.""")
    ]