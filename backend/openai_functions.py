"""
OpenAI Function Calling Integration for Stock Recommendation System

This module provides function schemas and dispatching for OpenAI function calling
to interact with CSV data processing functions.
"""

import json
from typing import Dict, Any, List
from backend.data_processor import (
    get_top_stocks_by_stars,
    filter_stocks_by_industry,
    filter_stocks_by_sector,
    get_stock_details,
    compare_stocks_performance,
    get_industry_overview,
    search_stocks_by_criteria,
    get_available_industries,
    get_available_sectors
)

# OpenAI Function Schemas
FUNCTION_SCHEMAS = [
    {
        "name": "get_top_stocks_by_stars",
        "description": "Get top-performing stocks filtered by minimum star rating. Stars range from 0-4.",
        "parameters": {
            "type": "object",
            "properties": {
                "min_stars": {
                    "type": "integer",
                    "description": "Minimum star rating (0-4)",
                    "minimum": 0,
                    "maximum": 4,
                    "default": 2
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of stocks to return",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10
                }
            },
            "required": []
        }
    },
    {
        "name": "filter_stocks_by_industry",
        "description": "Filter stocks by specific industry and sort by various criteria.",
        "parameters": {
            "type": "object",
            "properties": {
                "industry_name": {
                    "type": "string",
                    "description": "Name of the industry to filter by (e.g., 'Technology', 'Financial Services', 'Health Care')"
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["Stars", "Global Evaluation", "Year to date performance"],
                    "description": "Column to sort results by",
                    "default": "Stars"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of stocks to return",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10
                }
            },
            "required": ["industry_name"]
        }
    },
    {
        "name": "filter_stocks_by_sector",
        "description": "Filter stocks by specific sector and sort by various criteria.",
        "parameters": {
            "type": "object",
            "properties": {
                "sector_name": {
                    "type": "string",
                    "description": "Name of the sector to filter by (e.g., 'Speciality Finance', 'Technology', 'Basic Resources')"
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["Stars", "Global Evaluation", "Year to date performance"],
                    "description": "Column to sort results by",
                    "default": "Global Evaluation"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of stocks to return",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10
                }
            },
            "required": ["sector_name"]
        }
    },
    {
        "name": "get_stock_details",
        "description": "Get detailed information for a specific stock by ticker symbol or ISIN.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker_or_isin": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'AAPL', 'III') or ISIN code"
                }
            },
            "required": ["ticker_or_isin"]
        }
    },
    {
        "name": "compare_stocks_performance",
        "description": "Compare performance metrics of multiple stocks side by side.",
        "parameters": {
            "type": "object",
            "properties": {
                "stock_list": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of stock ticker symbols or ISINs to compare",
                    "minItems": 2,
                    "maxItems": 10
                }
            },
            "required": ["stock_list"]
        }
    },
    {
        "name": "get_industry_overview",
        "description": "Get statistical overview and insights for a specific industry including averages, top performers, and distributions.",
        "parameters": {
            "type": "object",
            "properties": {
                "industry_name": {
                    "type": "string",
                    "description": "Name of the industry to analyze"
                }
            },
            "required": ["industry_name"]
        }
    },
    {
        "name": "search_stocks_by_criteria",
        "description": "Search stocks using multiple filtering criteria for advanced stock screening.",
        "parameters": {
            "type": "object",
            "properties": {
                "criteria_dict": {
                    "type": "object",
                    "description": "Dictionary containing search criteria",
                    "properties": {
                        "min_stars": {
                            "type": "integer",
                            "description": "Minimum star rating (0-4)",
                            "minimum": 0,
                            "maximum": 4
                        },
                        "max_stars": {
                            "type": "integer",
                            "description": "Maximum star rating (0-4)",
                            "minimum": 0,
                            "maximum": 4
                        },
                        "min_ytd_performance": {
                            "type": "number",
                            "description": "Minimum year-to-date performance as decimal (e.g., 0.1 for 10%)"
                        },
                        "max_pe_ratio": {
                            "type": "number",
                            "description": "Maximum P/E ratio"
                        },
                        "valuation_rating": {
                            "type": "string",
                            "description": "Valuation rating filter (e.g., 'undervalued', 'overvalued')"
                        },
                        "global_evaluation": {
                            "type": "string",
                            "description": "Global evaluation filter (e.g., 'positive', 'negative', 'neutral')"
                        },
                        "sector": {
                            "type": "string",
                            "description": "Sector filter"
                        },
                        "industry": {
                            "type": "string",
                            "description": "Industry filter"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20
                        }
                    },
                    "additionalProperties": False
                }
            },
            "required": ["criteria_dict"]
        }
    },
    {
        "name": "get_available_industries",
        "description": "Get list of all available industries in the dataset for filtering purposes.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_available_sectors",
        "description": "Get list of all available sectors in the dataset for filtering purposes.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

# Function dispatcher
FUNCTION_MAP = {
    "get_top_stocks_by_stars": get_top_stocks_by_stars,
    "filter_stocks_by_industry": filter_stocks_by_industry,
    "filter_stocks_by_sector": filter_stocks_by_sector,
    "get_stock_details": get_stock_details,
    "compare_stocks_performance": compare_stocks_performance,
    "get_industry_overview": get_industry_overview,
    "search_stocks_by_criteria": search_stocks_by_criteria,
    "get_available_industries": lambda: {"industries": get_available_industries()},
    "get_available_sectors": lambda: {"sectors": get_available_sectors()}
}

def execute_function(function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a function call from OpenAI with the given arguments.

    Args:
        function_name: Name of the function to call
        arguments: Dictionary of function arguments

    Returns:
        Function result as dictionary
    """
    try:
        if function_name not in FUNCTION_MAP:
            return {
                "error": f"Function '{function_name}' not found",
                "available_functions": list(FUNCTION_MAP.keys())
            }

        function = FUNCTION_MAP[function_name]

        # Handle functions with no arguments
        if not arguments:
            if function_name in ["get_available_industries", "get_available_sectors"]:
                return function()
            else:
                return function()

        # Handle functions with single dictionary argument (search_stocks_by_criteria)
        if function_name == "search_stocks_by_criteria":
            return function(arguments.get("criteria_dict", {}))

        # Handle regular function calls
        return function(**arguments)

    except TypeError as e:
        return {
            "error": f"Invalid arguments for function '{function_name}': {str(e)}",
            "provided_arguments": arguments
        }
    except Exception as e:
        return {
            "error": f"Error executing function '{function_name}': {str(e)}",
            "provided_arguments": arguments
        }

def get_function_schemas() -> List[Dict[str, Any]]:
    """
    Get all function schemas for OpenAI function calling.

    Returns:
        List of function schemas
    """
    return FUNCTION_SCHEMAS

def process_openai_function_call(function_call: Dict[str, Any]) -> str:
    """
    Process a function call from OpenAI and return JSON result.

    Args:
        function_call: Function call object from OpenAI with 'name' and 'arguments'

    Returns:
        JSON string with function result
    """
    try:
        function_name = function_call.get("name")
        arguments_str = function_call.get("arguments", "{}")

        # Parse arguments if they're a string
        if isinstance(arguments_str, str):
            arguments = json.loads(arguments_str) if arguments_str else {}
        else:
            arguments = arguments_str

        result = execute_function(function_name, arguments)
        return json.dumps(result, indent=2, default=str)

    except json.JSONDecodeError as e:
        return json.dumps({
            "error": f"Invalid JSON in function arguments: {str(e)}",
            "raw_arguments": arguments_str
        })
    except Exception as e:
        return json.dumps({
            "error": f"Error processing function call: {str(e)}",
            "function_call": function_call
        })

# Example usage patterns for documentation
EXAMPLE_USAGE = {
    "get_top_stocks_by_stars": {
        "description": "Find high-rated stocks",
        "example_call": {"name": "get_top_stocks_by_stars", "arguments": '{"min_stars": 3, "limit": 5}'},
        "use_cases": ["Show me the best performing stocks", "What are the top-rated stocks?", "Find stocks with 4 stars"]
    },
    "filter_stocks_by_industry": {
        "description": "Focus on specific industry",
        "example_call": {"name": "filter_stocks_by_industry", "arguments": '{"industry_name": "Technology", "limit": 10}'},
        "use_cases": ["Show me technology stocks", "What are the best healthcare stocks?", "Find energy sector investments"]
    },
    "search_stocks_by_criteria": {
        "description": "Advanced stock screening",
        "example_call": {"name": "search_stocks_by_criteria", "arguments": '{"criteria_dict": {"min_stars": 3, "min_ytd_performance": 0.1, "sector": "Technology", "limit": 15}}'},
        "use_cases": ["Find undervalued tech stocks with good performance", "Screen for dividend stocks", "Look for growth stocks in specific sectors"]
    }
}

if __name__ == "__main__":
    # Test the OpenAI function integration
    print("Testing OpenAI Function Integration...")

    # Test function schema generation
    schemas = get_function_schemas()
    print(f"Generated {len(schemas)} function schemas")

    # Test function execution
    test_call = {
        "name": "get_top_stocks_by_stars",
        "arguments": '{"min_stars": 2, "limit": 3}'
    }

    result = process_openai_function_call(test_call)
    print("Test function call result:")
    print(result)