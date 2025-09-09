#!/usr/bin/env python3
"""
Profile Manager Script
Reads names from active.csv and updates profile active/inactive status via API
"""

import csv
import requests
import json
import sys
from typing import List, Dict, Set
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
# Configuration
API_BASE_URL = "https://face-recognition-app-nine.vercel.app/api/v1"  # Change to your deployed URL if needed
API_KEY = os.getenv("FACE_RECOGNITION_API_KEY")  # Replace with your actual API key
CSV_FILE = "active_sample.csv"

class ProfileManager:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_all_profiles(self) -> List[Dict]:
        """Fetch all profiles from the API"""
        try:
            response = requests.get(
                f"{self.base_url}/profiles",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching profiles: {response.status_code}")
                print(f"Response: {response.text}")
                return []
        
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching profiles: {e}")
            return []
    
    def update_profile_status(self, profile_id: str, active: bool) -> bool:
        """Update a profile's active status"""
        try:
            response = requests.patch(
                f"{self.base_url}/profiles/{profile_id}/toggle",
                headers=self.headers,
                json={"active": active}
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"Error updating profile {profile_id}: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        
        except requests.exceptions.RequestException as e:
            print(f"Network error updating profile {profile_id}: {e}")
            return False
    
    def read_active_names_csv(self, csv_file: str) -> Set[str]:
        """Read names from CSV file"""
        active_names = set()
        
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                # Read all lines first
                lines = file.readlines()
                
                if not lines:
                    print(f"Error: CSV file '{csv_file}' is empty")
                    return set()
                
                # Try different delimiters
                delimiters = [',', ';', '\t', '|']
                reader = None
                
                for delimiter in delimiters:
                    try:
                        # Reset to beginning and try this delimiter
                        first_line = lines[0].strip()
                        if delimiter in first_line:
                            # Create reader with this delimiter
                            reader = csv.reader(lines, delimiter=delimiter)
                            break
                    except:
                        continue
                
                # If no delimiter worked, treat each line as a single name
                if reader is None:
                    print(f"No CSV delimiter found, treating each line as a name")
                    for line in lines:
                        name = line.strip()
                        if name and not name.lower().startswith('name'):  # Skip header-like lines
                            active_names.add(name.lower())
                else:
                    # Process CSV with detected delimiter
                    first_row = True
                    for row in reader:
                        if row:  # Skip empty rows
                            # Check if first row looks like a header
                            if first_row and len(row) > 0 and row[0].lower() in ['name', 'names', 'profile', 'person']:
                                first_row = False
                                continue
                            first_row = False
                            
                            # Take first column and strip whitespace
                            name = row[0].strip()
                            if name:  # Skip empty names
                                active_names.add(name.lower())  # Case insensitive comparison
                
                print(f"Read {len(active_names)} names from {csv_file}")
                if len(active_names) > 0:
                    print(f"Sample names: {list(active_names)[:3]}{'...' if len(active_names) > 3 else ''}")
                return active_names
        
        except FileNotFoundError:
            print(f"Error: CSV file '{csv_file}' not found")
            return set()
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return set()
    
    def sync_profiles(self, csv_file: str):
        """Main function to sync profile statuses"""
        print("=== Profile Status Sync ===")
        
        # Read active names from CSV
        active_names = self.read_active_names_csv(csv_file)
        if not active_names:
            print("No names found in CSV file. Exiting.")
            return
        
        # Get all profiles from API
        profiles = self.get_all_profiles()
        if not profiles:
            print("No profiles found in account. Exiting.")
            return
        
        print(f"Found {len(profiles)} profiles in account")
        
        # Track statistics
        stats = {
            'activated': 0,
            'deactivated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Process each profile
        for profile in profiles:
            profile_id = profile['id']
            profile_name = profile['name']
            current_status = profile['active']
            
            # Check if this profile name is in our active list (case insensitive)
            should_be_active = profile_name.lower() in active_names
            
            print(f"\nProcessing: {profile_name}")
            print(f"  Current status: {'Active' if current_status else 'Inactive'}")
            print(f"  Should be: {'Active' if should_be_active else 'Inactive'}")
            
            # Skip if already in correct state
            if current_status == should_be_active:
                print(f"  ✓ Already in correct state - skipping")
                stats['skipped'] += 1
                continue
            
            # Update the profile
            success = self.update_profile_status(profile_id, should_be_active)
            
            if success:
                action = "activated" if should_be_active else "deactivated"
                print(f"  ✓ Successfully {action}")
                stats[action] += 1
            else:
                print(f"  ✗ Failed to update")
                stats['errors'] += 1
        
        # Print summary
        print(f"\n=== Summary ===")
        print(f"Profiles activated: {stats['activated']}")
        print(f"Profiles deactivated: {stats['deactivated']}")
        print(f"Profiles skipped (already correct): {stats['skipped']}")
        print(f"Errors: {stats['errors']}")
        print(f"Total processed: {len(profiles)}")


def main():
    # Check if API key is set
    if API_KEY == "YOUR_API_KEY":
        print("Error: Please set your API key in the script")
        print("Edit the script and replace 'YOUR_API_KEY_HERE' with your actual API key")
        sys.exit(1)
    
    # Create manager instance
    manager = ProfileManager(API_KEY, API_BASE_URL)
    
    # Run the sync
    try:
        manager.sync_profiles(CSV_FILE)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()