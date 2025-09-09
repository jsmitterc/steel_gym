#!/usr/bin/env python3
"""
Bulk Profile Manager Script
Reads names from CSV and updates all profile active/inactive status via API
"""

import sys
from profile_manager_class import ProfileManager

# Configuration
CSV_FILE = "active_sample.csv"


def main():
    # Create manager instance
    manager = ProfileManager()
    
    # Check if API key is available
    if not manager.api_key:
        print("Error: FACE_RECOGNITION_API_KEY environment variable not set")
        print("Make sure you have a .env file with your API key")
        sys.exit(1)
    
    # Run the bulk sync
    try:
        manager.sync_profiles_from_csv(CSV_FILE)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()