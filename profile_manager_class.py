#!/usr/bin/env python3
"""
ProfileManager Class
Handles all face recognition API profile operations
"""

import csv
import requests
import json
from typing import List, Dict, Set, Optional
from dotenv import load_dotenv
import os

load_dotenv()

class ProfileManager:
    def __init__(self, api_key: str = None, base_url: str = None):

        self.api_key = api_key or os.getenv("FACE_RECOGNITION_API_KEY")
        self.base_url = base_url or "http://localhost:3000/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
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
    
    def find_profile_by_name(self, name: str) -> Optional[Dict]:
        """Find a profile by name (case insensitive)"""
        profiles = self.get_all_profiles()
        
        for profile in profiles:
            if profile['name'].lower() == name.lower():
                return profile
        
        return None
    
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
    
    def update_single_profile_by_name(self, name: str, active: bool) -> bool:
        """Update a single profile's status by name"""
        print(f"Looking for profile: {name}")
        
        # Get all profiles first
        all_profiles = self.get_all_profiles()
        if not all_profiles:
            print("Error: Could not fetch profiles from API")
            return False
        
        # Find the specific profile by name
        profile = None
        for p in all_profiles:
            if p['name'].lower() == name.lower():
                profile = p
                break
        
        if not profile:
            print(f"Error: Profile '{name}' not found")
            print("\nAvailable profiles:")
            for p in all_profiles:
                print(f"  - {p['name']}")
            return False
        
        profile_id = profile['id']
        profile_name = profile['name']
        current_status = profile['active']
        
        print(f"Found profile: {profile_name}")
        print(f"Current status: {'Active' if current_status else 'Inactive'}")
        print(f"Target status: {'Active' if active else 'Inactive'}")
        
        if current_status == active:
            print(f"Profile is already {'active' if active else 'inactive'}. No changes needed.")
            return True
        
        success = self.update_profile_status(profile_id, active)
        
        if success:
            action = "activated" if active else "deactivated"
            print(f"✓ Successfully {action} profile '{profile_name}'")
            return True
        else:
            print(f"✗ Failed to update profile '{profile_name}'")
            return False
    
    def read_active_names_csv(self, csv_file: str) -> Set[str]:
        """Read names from CSV file"""
        active_names = set()
        
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                lines = file.readlines()
                
                if not lines:
                    print(f"Error: CSV file '{csv_file}' is empty")
                    return set()
                
                delimiters = [',', ';', '\t', '|']
                reader = None
                
                for delimiter in delimiters:
                    try:
                        first_line = lines[0].strip()
                        if delimiter in first_line:
                            reader = csv.reader(lines, delimiter=delimiter)
                            break
                    except:
                        continue
                
                if reader is None:
                    print(f"No CSV delimiter found, treating each line as a name")
                    for line in lines:
                        name = line.strip()
                        if name and not name.lower().startswith('name'):
                            active_names.add(name.lower())
                else:
                    first_row = True
                    for row in reader:
                        if row:
                            if first_row and len(row) > 0 and row[0].lower() in ['name', 'names', 'profile', 'person']:
                                first_row = False
                                continue
                            first_row = False
                            
                            name = row[0].strip()
                            if name:
                                active_names.add(name.lower())
                
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
    
    def sync_profiles_from_csv(self, csv_file: str):
        """Sync all profile statuses based on CSV file"""
        print("=== Profile Status Sync ===")
        
        active_names = self.read_active_names_csv(csv_file)
        if not active_names:
            print("No names found in CSV file. Exiting.")
            return
        
        profiles = self.get_all_profiles()
        if not profiles:
            print("No profiles found in account. Exiting.")
            return
        
        print(f"Found {len(profiles)} profiles in account")
        
        stats = {
            'activated': 0,
            'deactivated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for profile in profiles:
            profile_id = profile['id']
            profile_name = profile['name']
            current_status = profile['active']
            
            should_be_active = profile_name.lower() in active_names
            
            print(f"\nProcessing: {profile_name}")
            print(f"  Current status: {'Active' if current_status else 'Inactive'}")
            print(f"  Should be: {'Active' if should_be_active else 'Inactive'}")
            
            if current_status == should_be_active:
                print(f"  ✓ Already in correct state - skipping")
                stats['skipped'] += 1
                continue
            
            success = self.update_profile_status(profile_id, should_be_active)
            
            if success:
                action = "activated" if should_be_active else "deactivated"
                print(f"  ✓ Successfully {action}")
                stats[action] += 1
            else:
                print(f"  ✗ Failed to update")
                stats['errors'] += 1
        
        print(f"\n=== Summary ===")
        print(f"Profiles activated: {stats['activated']}")
        print(f"Profiles deactivated: {stats['deactivated']}")
        print(f"Profiles skipped (already correct): {stats['skipped']}")
        print(f"Errors: {stats['errors']}")
        print(f"Total processed: {len(profiles)}")