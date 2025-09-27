"""
Chat Handler for Stock Recommendation System

This module handles OpenAI chat completions with function calling for stock queries.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from backend.openai_functions import get_function_schemas, process_openai_function_call

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockChatHandler:
    """
    Handles chat interactions with OpenAI for stock recommendations and queries.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the chat handler.

        Args:
            api_key: OpenAI API key (if None, reads from environment)
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.function_schemas = get_function_schemas()
        self.conversation_history = []

    def get_stock_recommendation(self, user_query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Get stock recommendations based on user query using OpenAI function calling.

        Args:
            user_query: User's natural language query
            context: Optional context about user preferences

        Returns:
            Dict containing response and any function call results
        """
        try:
            # Build system message
            system_message = self._build_system_message(context)

            # Add user query to conversation
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_query}
            ]

            # Add conversation history
            messages.extend(self.conversation_history[-6:])  # Keep last 6 messages for context

            # Make OpenAI API call with function calling
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                functions=self.function_schemas,
                function_call="auto",
                temperature=0.7,
                max_tokens=1500
            )

            message = response.choices[0].message
            result = {
                "response": message.content,
                "function_calls": [],
                "recommendations": []
            }

            # Handle function calls
            if message.function_call:
                function_result = process_openai_function_call({
                    "name": message.function_call.name,
                    "arguments": message.function_call.arguments
                })

                result["function_calls"].append({
                    "function": message.function_call.name,
                    "arguments": message.function_call.arguments,
                    "result": json.loads(function_result)
                })

                # Follow up with function result
                follow_up_messages = messages + [
                    {"role": "assistant", "content": message.content, "function_call": message.function_call},
                    {"role": "function", "name": message.function_call.name, "content": function_result}
                ]

                follow_up_response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=follow_up_messages,
                    temperature=0.7,
                    max_tokens=1500
                )

                result["response"] = follow_up_response.choices[0].message.content

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_query})
            self.conversation_history.append({"role": "assistant", "content": result["response"]})

            return result

        except Exception as e:
            logger.error(f"Error in get_stock_recommendation: {str(e)}")
            return {
                "error": str(e),
                "response": "I'm sorry, I encountered an error while processing your request. Please try again."
            }

    def _build_system_message(self, context: Optional[str] = None) -> str:
        """
        Build system message for OpenAI chat.

        Args:
            context: Optional user context

        Returns:
            System message string
        """
        base_message = """
You are a helpful stock recommendation assistant. You have access to a comprehensive database of stocks with financial metrics, ratings, and performance data.

Your capabilities include:
- Finding top-rated stocks (stars range 0-4)
- Filtering stocks by industry or sector
- Providing detailed stock analysis
- Comparing multiple stocks
- Advanced stock screening with multiple criteria
- Industry overviews and market insights

Available data includes:
- Star ratings (0-4 scale)
- Global evaluation (very negative to very positive)
- Financial metrics (P/E ratio, ROE, market cap, etc.)
- Performance data (YTD, 4-week performance)
- Valuation ratings (undervalued, overvalued, etc.)
- Industry and sector classifications
- Dividend information

When helping users:
1. Use function calls to retrieve specific stock data
2. Provide clear, actionable recommendations
3. Explain the reasoning behind recommendations
4. Consider user's risk tolerance and investment goals
5. Be educational - explain financial terms when needed
6. Always mention that this is for informational purposes only

Be conversational and helpful, but always remind users to do their own research and consult financial advisors for investment decisions.
"""

        if context:
            base_message += f"\n\nUser Context: {context}"

        return base_message

    def get_industry_recommendations(self, industry: str, user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get recommendations for a specific industry.

        Args:
            industry: Industry name
            user_preferences: User preference dictionary

        Returns:
            Dict containing industry recommendations
        """
        query = f"Show me the best stocks in the {industry} industry"
        if user_preferences:
            if user_preferences.get("risk_tolerance") == "low":
                query += " with low risk and stable performance"
            elif user_preferences.get("focus") == "growth":
                query += " with high growth potential"
            elif user_preferences.get("focus") == "dividend":
                query += " with good dividend yields"

        return self.get_stock_recommendation(query)

    def compare_stocks(self, stock_list: List[str]) -> Dict[str, Any]:
        """
        Compare multiple stocks.

        Args:
            stock_list: List of stock tickers or ISINs

        Returns:
            Dict containing stock comparison
        """
        query = f"Compare these stocks for me: {', '.join(stock_list)}. Show me their key differences and which might be better investments."
        return self.get_stock_recommendation(query)

    def screen_stocks(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Screen stocks based on specific criteria.

        Args:
            criteria: Screening criteria dictionary

        Returns:
            Dict containing screened stocks
        """
        criteria_desc = []
        if criteria.get("min_stars"):
            criteria_desc.append(f"at least {criteria['min_stars']} stars")
        if criteria.get("industry"):
            criteria_desc.append(f"in {criteria['industry']} industry")
        if criteria.get("min_ytd_performance"):
            criteria_desc.append(f"with YTD performance above {criteria['min_ytd_performance']*100}%")

        query = f"Find stocks with {', '.join(criteria_desc) if criteria_desc else 'good fundamentals'}"
        return self.get_stock_recommendation(query)

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

# Example usage functions
def example_chat_session():
    """Example of how to use the StockChatHandler."""
    handler = StockChatHandler()

    # Example queries
    queries = [
        "Show me the top 5 highest-rated stocks",
        "What are the best technology stocks right now?",
        "Find undervalued stocks with good growth potential",
        "Compare AAPL and MSFT for me",
        "Give me an overview of the healthcare industry"
    ]

    for query in queries:
        print(f"\n--- User Query: {query} ---")
        result = handler.get_stock_recommendation(query)
        print(f"Response: {result['response']}")
        if result.get('function_calls'):
            print(f"Function calls made: {len(result['function_calls'])}")

if __name__ == "__main__":
    # Test the chat handler
    print("Testing Stock Chat Handler...")

    # Note: Requires OPENAI_API_KEY environment variable
    if os.getenv("OPENAI_API_KEY"):
        example_chat_session()
    else:
        print("OPENAI_API_KEY not set. Skipping chat tests.")

        # Test function schemas
        handler = StockChatHandler()
        print(f"Loaded {len(handler.function_schemas)} function schemas")
        for schema in handler.function_schemas[:3]:
            print(f"- {schema['name']}: {schema['description']}")