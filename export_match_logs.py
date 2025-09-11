#!/usr/bin/env python3
"""
Export Match Logs Script
Exports match logs from face recognition API to CSV files
"""

import sys
import argparse
from datetime import datetime, timedelta
from match_log_manager import MatchLogManager
import time
def main():
    parser = argparse.ArgumentParser(description='Export match logs from face recognition API to CSV')
    parser.add_argument('-o', '--output', default='match_logs.csv', help='Output CSV filename (default: match_logs.csv)')
    parser.add_argument('-d', '--days', type=int, default=30, help='Number of days back to export (default: 30)')
    parser.add_argument('--start-date', help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end-date', help='End date in YYYY-MM-DD format')
    parser.add_argument('--profile-id', help='Filter by specific profile ID')
    parser.add_argument('--device-id', help='Filter by specific device ID')
    parser.add_argument('--summary', action='store_true', help='Show summary of available logs without exporting')
    parser.add_argument('--all', action='store_true', help='Export all available logs (ignores --days)')
    
    args = parser.parse_args()
    
    # Create manager instance
    manager = MatchLogManager()
    
    # Check if API key is available
    if not manager.api_key:
        print("Error: FACE_RECOGNITION_API_KEY environment variable not set")
        print("Make sure you have a .env file with your API key")
        sys.exit(1)
    
    try:
        # Show summary if requested
        if args.summary:
            print("Getting match logs summary...")
            summary = manager.get_logs_summary()
            
            if not summary['api_working']:
                print("❌ API is not working properly")
                if 'error' in summary:
                    print(f"Error: {summary['error']}")
                sys.exit(1)
            
            print("✅ API is working")
            print(f"📊 Recent logs (last 7 days): {summary['total_recent_week']}")
            
            if summary['sample_logs']:
                print("\n📋 Sample logs:")
                for i, log in enumerate(summary['sample_logs'], 1):
                    matched_at = log.get('matched_at', 'Unknown')
                    profile_name = log.get('profile_name', 'Unknown')
                    confidence = log.get('confidence', 0)
                    device_name = log.get('device_name', 'Unknown')
                    
                    print(f"  {i}. {matched_at} - {profile_name} ({confidence:.2%} confidence) - {device_name}")
            
            return
        
        # Determine export parameters
        if args.all:
            print("Exporting ALL available match logs...")
            success = manager.export_to_csv(
                filename=args.output,
                profile_id=args.profile_id,
                device_id=args.device_id
            )
        elif args.start_date or args.end_date:
            print(f"Exporting match logs from {args.start_date or 'beginning'} to {args.end_date or 'now'}...")
            
            # Convert dates to ISO format if provided
            start_date = None
            end_date = None
            
            if args.start_date:
                try:
                    start_date = datetime.strptime(args.start_date, '%Y-%m-%d').isoformat()
                except ValueError:
                    print("Error: start-date must be in YYYY-MM-DD format")
                    sys.exit(1)
            
            if args.end_date:
                try:
                    end_date = datetime.strptime(args.end_date, '%Y-%m-%d').isoformat()
                except ValueError:
                    print("Error: end-date must be in YYYY-MM-DD format")
                    sys.exit(1)
            
            success = manager.export_to_csv(
                filename=args.output,
                start_date=start_date,
                end_date=end_date,
                profile_id=args.profile_id,
                device_id=args.device_id
            )
        else:
            print(f"Exporting match logs from the last {args.days} days...")
            success = manager.export_recent_logs(
                filename=args.output,
                days_back=args.days
            )
        
        if success:
            print(f"✅ Match logs successfully exported to '{args.output}'")
            sys.exit(0)
        else:
            print("❌ Failed to export match logs")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        time.sleep(60)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        time.sleep(60)
        sys.exit(1)

if __name__ == "__main__":
    main()