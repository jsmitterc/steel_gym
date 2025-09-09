#!/usr/bin/env python3
"""
Single User Profile Updater Script
Updates a single user's profile active/inactive status via API using command line arguments
"""

import sys
import argparse
from profile_manager_class import ProfileManager


def main():
    parser = argparse.ArgumentParser(description='Update a single profile status in face recognition API')
    parser.add_argument('name', help='Name of the profile to update')
    parser.add_argument('status', choices=['active', 'inactive'], help='Status to set (active or inactive)')
    
    args = parser.parse_args()
    
    # Create manager instance
    manager = ProfileManager()
    
    # Check if API key is available
    if not manager.api_key:
        print("Error: FACE_RECOGNITION_API_KEY environment variable not set")
        print("Make sure you have a .env file with your API key")
        sys.exit(1)
    
    # Convert status string to boolean
    active = args.status == 'active'
    
    # Update the single profile
    try:
        success = manager.update_single_profile_by_name(args.name, active)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()