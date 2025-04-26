# backend/app/services/bus_filtering.py
import math
from typing import List, Dict, Any, Optional # Import Optional

def filter_and_paginate_buses(
    full_bus_list: List[Dict[str, Any]],
    page: int = 1,
    limit: int = 10,
    lines: Optional[List[str]] = None # Optional line filter
) -> Dict[str, Any]:
    """
    Filters a list of buses by line (optional) and applies pagination.

    Args:
        full_bus_list: The complete list of bus data dictionaries.
        page: The desired page number (1-indexed).
        limit: The number of items per page.
        line: The specific bus line to filter by (optional).

    Returns:
        A dictionary containing pagination metadata and the filtered/paginated list of buses.
    """

    # 1. Filter by line if provided
    if lines: # Check if the list is provided and not empty
        # Convert filter lines to a set of strings for efficient 'in' check
        # Handles potential non-string items in the input list
        line_filter_set = {str(line) for line in lines if line}
        if line_filter_set: # Proceed only if the set is not empty after conversion
            filtered_list = [
                bus for bus in full_bus_list
                if isinstance(bus, dict) and str(bus.get("linha")) in line_filter_set
            ]
        else:
             # If input list was empty or contained only falsy values
             filtered_list = full_bus_list
    else:
        # No line filter applied, use the full list
        filtered_list = full_bus_list

    # 2. Apply Pagination to the filtered list
    total_items = len(filtered_list)
    limit = max(1, limit) # Ensure limit is at least 1
    page = max(1, page)   # Ensure page is at least 1
    offset = (page - 1) * limit
    total_pages = math.ceil(total_items / limit) if limit > 0 else 0

    # Ensure page number is within valid range
    if page > total_pages and total_pages > 0:
        # Optional: Redirect to last page? Or keep it simple and return empty list?
        # Let's return empty list if page is out of bounds
         paginated_items = []
         # Or adjust page to last page: page = total_pages; offset = (page - 1) * limit
    else:
         paginated_items = filtered_list[offset : offset + limit]


    # 3. Return structured data
    return {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit,
        "items": paginated_items
    }