"""
CSV Data Processing Functions for Stock Recommendation System

This module provides pandas-based functions that can be called via OpenAI function calling
to analyze and filter stock data from CSV files.
"""

import pandas as pd
import os
import logging
from typing import Dict, List, Optional, Any, Union
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define dataset path based on notebook structure
DATASET_PATH = os.getenv("DATASET_PATH")
CSV_FILE = "2025-09-23_data_EN.csv"

def load_stock_data() -> pd.DataFrame:
    """
    Load stock data from CSV file with proper encoding and error handling.

    Returns:
        pd.DataFrame: Loaded stock data
    """
    try:
        df = pd.read_csv(
            DATASET_PATH + CSV_FILE,
            sep=";",
            encoding="iso-8859-1"
        )
        logger.info(f"Successfully loaded {len(df)} stocks from CSV")
        return df
    except FileNotFoundError:
        logger.error(f"CSV file not found at {DATASET_PATH + CSV_FILE}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading CSV data: {str(e)}")
        return pd.DataFrame()

def get_top_stocks_by_stars(min_stars: int = 2, limit: int = 10) -> Dict[str, Any]:
    """
    Get top stocks filtered by minimum star rating.

    Args:
        min_stars: Minimum star rating (0-4)
        limit: Maximum number of stocks to return

    Returns:
        Dict containing list of top stocks and metadata
    """
    try:
        df = load_stock_data()
        if df.empty:
            return {"error": "No data available", "stocks": []}

        # Filter by minimum stars and sort
        filtered_df = df[df['Stars'] >= min_stars].copy()
        top_stocks = filtered_df.nlargest(limit, 'Stars')

        stocks_list = []
        for _, row in top_stocks.iterrows():
            stock_info = {
                'ticker': row['Ticker'],
                'isin': row['ISIN'],
                'name': row['Name'],
                'stars': row['Stars'],
                'sector': row['Sector'],
                'industry': row['Industry'],
                'price': row['Price'],
                'market_cap_bn': row['Martket Capitalization (in $bn)'],
                'global_evaluation': row['Global Evaluation'],
                'ytd_performance': row['Year to date performance'],
                'valuation_rating': row['Valuation rating']
            }
            stocks_list.append(stock_info)

        return {
            "stocks": stocks_list,
            "total_found": len(filtered_df),
            "returned": len(stocks_list),
            "filter_criteria": f"Stars >= {min_stars}"
        }

    except Exception as e:
        logger.error(f"Error in get_top_stocks_by_stars: {str(e)}")
        return {"error": str(e), "stocks": []}

def filter_stocks_by_industry(industry_name: str, sort_by: str = "Stars", limit: int = 10) -> Dict[str, Any]:
    """
    Filter stocks by specific industry.

    Args:
        industry_name: Name of the industry to filter by
        sort_by: Column to sort by (Stars, Global Evaluation, Year to date performance)
        limit: Maximum number of stocks to return

    Returns:
        Dict containing filtered stocks and metadata
    """
    try:
        df = load_stock_data()
        if df.empty:
            return {"error": "No data available", "stocks": []}

        # Filter by industry (case insensitive)
        filtered_df = df[df['Industry'].str.contains(industry_name, case=False, na=False)].copy()

        if filtered_df.empty:
            available_industries = df['Industry'].unique().tolist()
            return {
                "error": f"No stocks found for industry: {industry_name}",
                "available_industries": available_industries,
                "stocks": []
            }

        # Sort by specified column
        if sort_by == "Stars":
            sorted_df = filtered_df.nlargest(limit, 'Stars')
        elif sort_by == "Global Evaluation":
            # Convert text ratings to numeric for sorting
            eval_order = ['very negative', 'negative', 'slightly negative', 'neutral', 'slightly positive', 'positive', 'very positive']
            filtered_df['eval_rank'] = filtered_df['Global Evaluation'].map(lambda x: eval_order.index(x) if x in eval_order else 3)
            sorted_df = filtered_df.nlargest(limit, 'eval_rank')
        else:  # Year to date performance
            sorted_df = filtered_df.nlargest(limit, 'Year to date performance')

        stocks_list = []
        for _, row in sorted_df.iterrows():
            stock_info = {
                'ticker': row['Ticker'],
                'isin': row['ISIN'],
                'name': row['Name'],
                'industry': row['Industry'],
                'sector': row['Sector'],
                'stars': row['Stars'],
                'price': row['Price'],
                'global_evaluation': row['Global Evaluation'],
                'industry_global_evaluation': row['Industry Global Evaluation'],
                'ytd_performance': row['Year to date performance'],
                'valuation_rating': row['Valuation rating'],
                'market_cap_bn': row['Martket Capitalization (in $bn)']
            }
            stocks_list.append(stock_info)

        return {
            "stocks": stocks_list,
            "industry": industry_name,
            "total_in_industry": len(filtered_df),
            "returned": len(stocks_list),
            "sorted_by": sort_by
        }

    except Exception as e:
        logger.error(f"Error in filter_stocks_by_industry: {str(e)}")
        return {"error": str(e), "stocks": []}

def filter_stocks_by_sector(sector_name: str, sort_by: str = "Global Evaluation", limit: int = 10) -> Dict[str, Any]:
    """
    Filter stocks by specific sector.

    Args:
        sector_name: Name of the sector to filter by
        sort_by: Column to sort by
        limit: Maximum number of stocks to return

    Returns:
        Dict containing filtered stocks and metadata
    """
    try:
        df = load_stock_data()
        if df.empty:
            return {"error": "No data available", "stocks": []}

        # Filter by sector (case insensitive)
        filtered_df = df[df['Sector'].str.contains(sector_name, case=False, na=False)].copy()

        if filtered_df.empty:
            available_sectors = df['Sector'].unique().tolist()
            return {
                "error": f"No stocks found for sector: {sector_name}",
                "available_sectors": available_sectors,
                "stocks": []
            }

        # Sort by specified column
        if sort_by == "Stars":
            sorted_df = filtered_df.nlargest(limit, 'Stars')
        elif sort_by == "Global Evaluation":
            eval_order = ['very negative', 'negative', 'slightly negative', 'neutral', 'slightly positive', 'positive', 'very positive']
            filtered_df['eval_rank'] = filtered_df['Global Evaluation'].map(lambda x: eval_order.index(x) if x in eval_order else 3)
            sorted_df = filtered_df.nlargest(limit, 'eval_rank')
        else:  # Year to date performance
            sorted_df = filtered_df.nlargest(limit, 'Year to date performance')

        stocks_list = []
        for _, row in sorted_df.iterrows():
            stock_info = {
                'ticker': row['Ticker'],
                'isin': row['ISIN'],
                'name': row['Name'],
                'sector': row['Sector'],
                'industry': row['Industry'],
                'stars': row['Stars'],
                'price': row['Price'],
                'global_evaluation': row['Global Evaluation'],
                'ytd_performance': row['Year to date performance'],
                'valuation_rating': row['Valuation rating'],
                'market_cap_bn': row['Martket Capitalization (in $bn)']
            }
            stocks_list.append(stock_info)

        return {
            "stocks": stocks_list,
            "sector": sector_name,
            "total_in_sector": len(filtered_df),
            "returned": len(stocks_list),
            "sorted_by": sort_by
        }

    except Exception as e:
        logger.error(f"Error in filter_stocks_by_sector: {str(e)}")
        return {"error": str(e), "stocks": []}

def get_stock_details(ticker_or_isin: str) -> Dict[str, Any]:
    """
    Get detailed information for a specific stock by ticker or ISIN.

    Args:
        ticker_or_isin: Stock ticker symbol or ISIN

    Returns:
        Dict containing detailed stock information
    """
    try:
        df = load_stock_data()
        if df.empty:
            return {"error": "No data available"}

        # Search by ticker or ISIN
        stock_row = df[(df['Ticker'] == ticker_or_isin) | (df['ISIN'] == ticker_or_isin)]

        if stock_row.empty:
            return {"error": f"Stock not found: {ticker_or_isin}"}

        row = stock_row.iloc[0]

        stock_details = {
            'identifiers': {
                'ticker': row['Ticker'],
                'isin': row['ISIN'],
                'name': row['Name'],
                'sector': row['Sector'],
                'industry': row['Industry'],
                'market': row['Market'],
                'currency': row['Currency']
            },
            'price_performance': {
                'current_price': row['Price'],
                'target_price': row['Target Price'],
                'ytd_performance': row['Year to date performance'],
                'four_weeks_performance': row['4 weeks performance'],
                'reference_index': row['Reference index']
            },
            'valuation_metrics': {
                'long_term_pe': row['Long Term PE'],
                'book_value_price': row['Book Value / Price'],
                'valuation_rating': row['Valuation rating'],
                'market_cap_bn': row['Martket Capitalization (in $bn)']
            },
            'financial_metrics': {
                'return_on_equity': row['Return On equity'],
                'ebit': row['Earnings Before Interest & Taxes'],
                'equity_on_assets': row['Equity on Assets'],
                'current_ratio': row['Current Ratio'] if pd.notna(row['Current Ratio']) else None,
                'long_term_debt': row['Long Term Debt'],
                'total_revenue_mio': row['Total Revenue (in Mio)'],
                'net_income_mio': row['Net Income (in Mio)'],
                'revenues_on_assets': row['Revenues on Assets'],
                'cash_flow_on_revenues': row['Cash Flow on Revenues'] if pd.notna(row['Cash Flow on Revenues']) else None
            },
            'growth_trends': {
                'long_term_growth': row['Long Term Growth'],
                'earnings_revision_trend': row['Earnings revision trend'],
                'technical_trend': row['Technical trend'],
                'sensitivity': row['Sensitivity']
            },
            'ratings': {
                'stars': row['Stars'],
                'global_evaluation': row['Global Evaluation'],
                'industry_global_evaluation': row['Industry Global Evaluation']
            },
            'dividend_info': {
                'expected_dividend': row['Expected dividend']
            }
        }

        return stock_details

    except Exception as e:
        logger.error(f"Error in get_stock_details: {str(e)}")
        return {"error": str(e)}

def compare_stocks_performance(stock_list: List[str]) -> Dict[str, Any]:
    """
    Compare performance metrics of multiple stocks.

    Args:
        stock_list: List of ticker symbols or ISINs

    Returns:
        Dict containing comparison data
    """
    try:
        df = load_stock_data()
        if df.empty:
            return {"error": "No data available"}

        comparison_data = []
        not_found = []

        for stock_id in stock_list:
            stock_row = df[(df['Ticker'] == stock_id) | (df['ISIN'] == stock_id)]

            if stock_row.empty:
                not_found.append(stock_id)
            else:
                row = stock_row.iloc[0]
                stock_comparison = {
                    'ticker': row['Ticker'],
                    'name': row['Name'],
                    'stars': row['Stars'],
                    'price': row['Price'],
                    'market_cap_bn': row['Martket Capitalization (in $bn)'],
                    'ytd_performance': row['Year to date performance'],
                    'four_weeks_performance': row['4 weeks performance'],
                    'long_term_pe': row['Long Term PE'],
                    'return_on_equity': row['Return On equity'],
                    'long_term_growth': row['Long Term Growth'],
                    'global_evaluation': row['Global Evaluation'],
                    'valuation_rating': row['Valuation rating'],
                    'expected_dividend': row['Expected dividend']
                }
                comparison_data.append(stock_comparison)

        return {
            "comparison": comparison_data,
            "not_found": not_found,
            "compared_count": len(comparison_data)
        }

    except Exception as e:
        logger.error(f"Error in compare_stocks_performance: {str(e)}")
        return {"error": str(e)}

def get_industry_overview(industry_name: str) -> Dict[str, Any]:
    """
    Get overview statistics for a specific industry.

    Args:
        industry_name: Name of the industry

    Returns:
        Dict containing industry overview statistics
    """
    try:
        df = load_stock_data()
        if df.empty:
            return {"error": "No data available"}

        # Filter by industry
        industry_df = df[df['Industry'].str.contains(industry_name, case=False, na=False)].copy()

        if industry_df.empty:
            return {"error": f"No stocks found for industry: {industry_name}"}

        overview = {
            'industry_name': industry_name,
            'total_stocks': len(industry_df),
            'average_stars': industry_df['Stars'].mean(),
            'average_ytd_performance': industry_df['Year to date performance'].mean(),
            'average_market_cap_bn': industry_df['Martket Capitalization (in $bn)'].mean(),
            'average_pe_ratio': industry_df['Long Term PE'].mean(),
            'average_expected_dividend': industry_df['Expected dividend'].mean(),
            'top_performers': industry_df.nlargest(3, 'Stars')[['Ticker', 'Name', 'Stars']].to_dict('records'),
            'evaluation_distribution': industry_df['Global Evaluation'].value_counts().to_dict(),
            'valuation_distribution': industry_df['Valuation rating'].value_counts().to_dict()
        }

        return overview

    except Exception as e:
        logger.error(f"Error in get_industry_overview: {str(e)}")
        return {"error": str(e)}

def search_stocks_by_criteria(criteria_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search stocks based on multiple criteria.

    Args:
        criteria_dict: Dictionary containing search criteria
            Possible keys: min_stars, max_stars, min_ytd_performance, max_pe_ratio,
            valuation_rating, global_evaluation, sector, industry, limit

    Returns:
        Dict containing matching stocks
    """
    try:
        df = load_stock_data()
        if df.empty:
            return {"error": "No data available", "stocks": []}

        filtered_df = df.copy()
        applied_filters = []

        # Apply filters based on criteria
        if 'min_stars' in criteria_dict:
            filtered_df = filtered_df[filtered_df['Stars'] >= criteria_dict['min_stars']]
            applied_filters.append(f"Stars >= {criteria_dict['min_stars']}")

        if 'max_stars' in criteria_dict:
            filtered_df = filtered_df[filtered_df['Stars'] <= criteria_dict['max_stars']]
            applied_filters.append(f"Stars <= {criteria_dict['max_stars']}")

        if 'min_ytd_performance' in criteria_dict:
            filtered_df = filtered_df[filtered_df['Year to date performance'] >= criteria_dict['min_ytd_performance']]
            applied_filters.append(f"YTD Performance >= {criteria_dict['min_ytd_performance']}")

        if 'max_pe_ratio' in criteria_dict:
            filtered_df = filtered_df[filtered_df['Long Term PE'] <= criteria_dict['max_pe_ratio']]
            applied_filters.append(f"PE Ratio <= {criteria_dict['max_pe_ratio']}")

        if 'valuation_rating' in criteria_dict:
            filtered_df = filtered_df[filtered_df['Valuation rating'].str.contains(criteria_dict['valuation_rating'], case=False, na=False)]
            applied_filters.append(f"Valuation Rating: {criteria_dict['valuation_rating']}")

        if 'global_evaluation' in criteria_dict:
            filtered_df = filtered_df[filtered_df['Global Evaluation'].str.contains(criteria_dict['global_evaluation'], case=False, na=False)]
            applied_filters.append(f"Global Evaluation: {criteria_dict['global_evaluation']}")

        if 'sector' in criteria_dict:
            filtered_df = filtered_df[filtered_df['Sector'].str.contains(criteria_dict['sector'], case=False, na=False)]
            applied_filters.append(f"Sector: {criteria_dict['sector']}")

        if 'industry' in criteria_dict:
            filtered_df = filtered_df[filtered_df['Industry'].str.contains(criteria_dict['industry'], case=False, na=False)]
            applied_filters.append(f"Industry: {criteria_dict['industry']}")

        # Limit results
        limit = criteria_dict.get('limit', 20)
        result_df = filtered_df.nlargest(limit, 'Stars')

        stocks_list = []
        for _, row in result_df.iterrows():
            stock_info = {
                'ticker': row['Ticker'],
                'isin': row['ISIN'],
                'name': row['Name'],
                'stars': row['Stars'],
                'sector': row['Sector'],
                'industry': row['Industry'],
                'price': row['Price'],
                'global_evaluation': row['Global Evaluation'],
                'ytd_performance': row['Year to date performance'],
                'valuation_rating': row['Valuation rating'],
                'market_cap_bn': row['Martket Capitalization (in $bn)']
            }
            stocks_list.append(stock_info)

        return {
            "stocks": stocks_list,
            "total_matches": len(filtered_df),
            "returned": len(stocks_list),
            "applied_filters": applied_filters
        }

    except Exception as e:
        logger.error(f"Error in search_stocks_by_criteria: {str(e)}")
        return {"error": str(e), "stocks": []}

# Utility functions
def get_available_industries() -> List[str]:
    """Get list of all available industries."""
    try:
        df = load_stock_data()
        return df['Industry'].unique().tolist() if not df.empty else []
    except:
        return []

def get_available_sectors() -> List[str]:
    """Get list of all available sectors."""
    try:
        df = load_stock_data()
        return df['Sector'].unique().tolist() if not df.empty else []
    except:
        return []

if __name__ == "__main__":
    # Test the functions
    print("Testing CSV Data Processing Functions...")

    # Test top stocks
    top_stocks = get_top_stocks_by_stars(min_stars=3, limit=5)
    print(f"Top 5 stocks with 3+ stars: {len(top_stocks['stocks'])} found")

    # Test industry filter
    tech_stocks = filter_stocks_by_industry("Technology", limit=3)
    print(f"Technology stocks: {len(tech_stocks['stocks'])} found")

    # Test stock details
    if tech_stocks['stocks']:
        first_tech_stock = tech_stocks['stocks'][0]['ticker']
        details = get_stock_details(first_tech_stock)
        print(f"Details for {first_tech_stock}: {details.get('identifiers', {}).get('name', 'Unknown')}")