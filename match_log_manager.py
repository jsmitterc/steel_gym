#!/usr/bin/env python3
"""
Match Log Manager Class
Handles fetching match logs from the face recognition API and exporting to CSV
"""

import csv
import requests
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import urllib.parse

load_dotenv()

class MatchLogManager:
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv("FACE_RECOGNITION_API_KEY")
        self.base_url = base_url or "http://localhost:3000/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_match_logs(self, 
                      limit: int = 100, 
                      offset: int = 0,
                      start_date: str = None,
                      end_date: str = None,
                      profile_id: str = None,
                      device_id: str = None) -> List[Dict]:
        """Fetch match logs from the API with optional filters"""
        try:
            params = {
                'limit': limit,
                'offset': offset
            }
            
            # Add optional filters
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date
            if profile_id:
                params['profile_id'] = profile_id
            if device_id:
                params['device_id'] = device_id
            
            # Build URL with query parameters
            url = f"{self.base_url}/match-logs"
            if params:
                url += "?" + urllib.parse.urlencode(params)
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching match logs: {response.status_code}")
                print(f"Response: {response.text}")
                return []
        
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching match logs: {e}")
            return []
    
    def get_all_match_logs(self,
                          start_date: str = None,
                          end_date: str = None,
                          profile_id: str = None,
                          device_id: str = None) -> List[Dict]:
        """Fetch all match logs by paginating through the API"""
        all_logs = []
        offset = 0
        limit = 100
        
        print("Fetching match logs...")
        
        while True:
            logs = self.get_match_logs(
                limit=limit, 
                offset=offset,
                start_date=start_date,
                end_date=end_date,
                profile_id=profile_id,
                device_id=device_id
            )
            
            if not logs:
                break
            
            all_logs.extend(logs)
            print(f"Fetched {len(logs)} logs (total: {len(all_logs)})")
            
            # If we got fewer logs than the limit, we've reached the end
            if len(logs) < limit:
                break
            
            offset += limit
        
        print(f"Total match logs fetched: {len(all_logs)}")
        return all_logs
    
    def flatten_match_log(self, log: Dict) -> Dict:
        """Flatten nested match log data for CSV export"""
        flattened = {
            'id': log.get('id'),
            'profile_id': log.get('profile_id'),
            'profile_name': log.get('profile_name'),
            'confidence': log.get('confidence'),
            'device_id': log.get('device_id'),
            'device_name': log.get('device_name'),
            'device_location': log.get('device_location'),
            'matched_at': log.get('matched_at'),
            'created_at': log.get('created_at'),
        }
        
        return flattened
    
    def export_to_csv(self, 
                     filename: str,
                     start_date: str = None,
                     end_date: str = None,
                     profile_id: str = None,
                     device_id: str = None) -> bool:
        """Export match logs to CSV file"""
        try:
            # Fetch all match logs
            logs = self.get_all_match_logs(
                start_date=start_date,
                end_date=end_date,
                profile_id=profile_id,
                device_id=device_id
            )
            
            if not logs:
                print("No match logs found to export.")
                return False
            
            # Flatten the data for CSV
            flattened_logs = [self.flatten_match_log(log) for log in logs]
            
            # Get CSV headers from the first log
            headers = list(flattened_logs[0].keys())
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(flattened_logs)
            
            print(f"Successfully exported {len(logs)} match logs to '{filename}'")
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def get_date_range_logs(self, days_back: int = 30) -> List[Dict]:
        """Get match logs for the last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        start_date_str = start_date.isoformat()
        end_date_str = end_date.isoformat()
        
        return self.get_all_match_logs(
            start_date=start_date_str,
            end_date=end_date_str
        )
    
    def export_recent_logs(self, filename: str, days_back: int = 30) -> bool:
        """Export recent match logs (last N days) to CSV"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        start_date_str = start_date.isoformat()
        end_date_str = end_date.isoformat()
        
        print(f"Exporting match logs from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        return self.export_to_csv(
            filename=filename,
            start_date=start_date_str,
            end_date=end_date_str
        )
    
    def get_logs_summary(self) -> Dict:
        """Get a summary of match logs"""
        try:
            # Get a small sample to check if API is working
            logs = self.get_match_logs(limit=10)
            
            if not logs:
                return {
                    'total_accessible': 0,
                    'sample_logs': [],
                    'api_working': False
                }
            
            # Get recent logs for summary
            recent_logs = self.get_date_range_logs(days_back=7)
            
            return {
                'total_recent_week': len(recent_logs),
                'sample_logs': logs[:5],  # First 5 logs as sample
                'api_working': True
            }
            
        except Exception as e:
            print(f"Error getting logs summary: {e}")
            return {
                'total_accessible': 0,
                'sample_logs': [],
                'api_working': False,
                'error': str(e)
            }