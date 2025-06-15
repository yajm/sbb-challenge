#!/usr/bin/env python3
"""
SBB Route Time Calculator
Calculates actual train times for all 54 routes (27 paths in both directions)
"""

import requests
import json
from datetime import datetime, timedelta
import time
import pandas as pd
from typing import Dict, List, Tuple
import re

class SBBRouteCalculator:
    def __init__(self, data_file: str):
        """Initialize with route data from JSON file"""
        with open(data_file, 'r') as f:
            self.data = json.load(f)
        
        self.api_url = "https://transport.opendata.ch/v1/connections"
        self.date = "2025-06-17"  # Tuesday
        self.start_time = "04:00"
        self.results = []
        
    def fix_combined_path(self, ranking: Dict) -> List[str]:
        """Correctly combine west_path (inverted) with east_path at split point"""
        west_path = ranking['west_path'].copy()
        east_path = ranking['east_path'].copy()
        split_point = ranking['split_point']
        
        # Reverse the west path
        west_path_reversed = west_path[::-1]
        
        # Remove duplicate split point
        if west_path_reversed[-1] == split_point and east_path[0] == split_point:
            combined = west_path_reversed[:-1] + east_path
        else:
            combined = west_path_reversed + east_path
            
        return combined
    
    def parse_datetime(self, datetime_str: str) -> datetime:
        """Parse datetime string from SBB API with proper timezone handling"""
        # Handle different timezone formats
        if datetime_str.endswith('Z'):
            # UTC time
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        else:
            # Check if timezone offset needs colon insertion (e.g., +0200 -> +02:00)
            # Pattern matches timestamps ending with +/-HHMM
            pattern = r'([+-]\d{2})(\d{2})$'
            match = re.search(pattern, datetime_str)
            if match:
                # Insert colon between hours and minutes in timezone offset
                datetime_str = re.sub(pattern, r'\1:\2', datetime_str)
            
            try:
                return datetime.fromisoformat(datetime_str)
            except ValueError:
                # Fallback: try parsing without timezone info
                # This removes everything after and including the last + or -
                datetime_str_no_tz = re.sub(r'[+-]\d{2}:?\d{2}$', '', datetime_str)
                return datetime.fromisoformat(datetime_str_no_tz)
    
    def get_connection_time(self, from_station: str, to_station: str, 
                          start_time: str = None) -> Dict:
        """Query SBB API for connection time between two stations"""
        if start_time is None:
            start_time = self.start_time
            
        params = {
            'from': from_station,
            'to': to_station,
            'limit': 16,
            'time': start_time,
            'date': self.date
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['connections'] and len(data['connections']) > 0:
                conn = data['connections'][0]
                departure = conn['from']['departure']
                arrival = conn['to']['arrival']
                
                # Parse times using the fixed parser
                dep_time = self.parse_datetime(departure)
                arr_time = self.parse_datetime(arrival)
                
                # Calculate duration in minutes
                duration = int((arr_time - dep_time).total_seconds() / 60)
                
                return {
                    'departure': dep_time.strftime('%H:%M'),
                    'arrival': arr_time.strftime('%H:%M'),
                    'duration': duration,
                    'success': True
                }
            else:
                return {'success': False, 'error': 'No connections found'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def calculate_route_time(self, stations: List[str], route_name: str, 
                           direction: str) -> Dict:
        """Calculate total time for a route through multiple stations"""
        print(f"\nProcessing {route_name} ({direction})...")
        print(f"Route: {stations[0]} → {stations[-1]} ({len(stations)} stations)")
        
        results = {
            'route_name': route_name,
            'direction': direction,
            'stations': stations,
            'segments': [],
            'total_duration': 0,
            'start_time': self.start_time,
            'end_time': None,
            'success': True
        }
        
        current_time = self.start_time
        
        for i in range(len(stations) - 1):
            from_station = stations[i]
            to_station = stations[i + 1]

            if i == 0 and from_station == "S. Vittore, Zona industriale" and to_station == "Bellinzona":
                results['start_time'] = "04:37"
                results['total_duration'] = 30
                current_time = "05:07"
                results['segments'].append({
                    'from': "S. Vittore, Zona industriale",
                    'to': "Bellinzona",
                    'departure':  "04:37",
                    'arrival': "05:07",
                    'duration': 30
                })
                continue
        
            conn = self.get_connection_time(from_station, to_station, current_time)     

            if conn['success']:
                if i==0:
                    results['start_time'] = conn['departure']

                results['segments'].append({
                    'from': from_station,
                    'to': to_station,
                    'departure': conn['departure'],
                    'arrival': conn['arrival'],
                    'duration': conn['duration']
                })
                
                # Update current time to arrival time (0 min transfer)
                current_time = conn['arrival']
                results['total_duration'] += conn['duration']
                
                print(f"  {from_station} → {to_station}: "
                      f"{conn['departure']}-{conn['arrival']} ({conn['duration']}min)")
            else:
                results['success'] = False
                results['error'] = f"Failed at {from_station} → {to_station}: {conn.get('error', 'Unknown error')}"
                print(f"  ERROR: {results['error']}")
                break
        
        if results['success'] and results['segments']:
            results['end_time'] = results['segments'][-1]['arrival']
            
            # Calculate actual total duration from start to end time
            start_dt = datetime.strptime(f"{self.date} {results['start_time']}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{self.date} {results['end_time']}", "%Y-%m-%d %H:%M")
            
            # Handle case where arrival is after midnight
            if end_dt < start_dt:
                end_dt += timedelta(days=1)
            
            results['total_duration'] = int((end_dt - start_dt).total_seconds() / 60)
            
            print(f"  Total time: {results['total_duration']//60} hours {results['total_duration']%60} minutes "
                f"({results['start_time']} → {results['end_time']})")
        
        return results
    
    def process_all_routes(self):
        """Process all 54 routes (27 paths × 2 directions)"""
        # Sort by original total_time to start with shortest
        sorted_rankings = sorted(self.data['rankings'], 
                               key=lambda x: x['total_time'])
        
        for idx, ranking in enumerate(sorted_rankings):
            # Fix the combined path
            fixed_path = self.fix_combined_path(ranking)
            
            # Process forward direction
            route_name = f"Route_{ranking['rank']}_Split_{ranking['split_point']}"
            
            # Forward direction
            forward_result = self.calculate_route_time(
                fixed_path, 
                f"{route_name}_Forward",
                "forward"
            )
            forward_result['original_rank'] = ranking['rank']
            forward_result['split_point'] = ranking['split_point']
            forward_result['original_time'] = ranking['total_time']
            self.results.append(forward_result)
            
            # Save intermediate results
            self.save_results(f"sbb_routes_progress_{idx+1}.json")
            
            # Reverse direction
            reverse_result = self.calculate_route_time(
                fixed_path[::-1],
                f"{route_name}_Reverse",
                "reverse"
            )
            reverse_result['original_rank'] = ranking['rank']
            reverse_result['split_point'] = ranking['split_point']
            reverse_result['original_time'] = ranking['total_time']
            self.results.append(reverse_result)
            
            # Save intermediate results
            self.save_results(f"sbb_routes_progress_{idx+1}.json")
            
            # Print summary table every 5 routes
            if (idx + 1) % 5 == 0:
                self.print_summary_table()
    
    def save_results(self, filename: str):
        """Save results to JSON file"""
        output = {
            'metadata': {
                'date': self.date,
                'start_time': self.start_time,
                'total_routes_processed': len(self.results),
                'timestamp': datetime.now().isoformat()
            },
            'routes': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to {filename}")
    
    def print_summary_table(self):
        """Print summary table of results"""
        if not self.results:
            return
            
        # Create summary data
        summary_data = []
        for result in self.results:
            if result['success']:
                summary_data.append({
                    'Route': result['route_name'],
                    'Split': result['split_point'],
                    'Direction': result['direction'],
                    'Start': result['stations'][0],
                    'End': result['stations'][-1],
                    'Stations': len(result['stations']),
                    'Original Time': result['original_time'],
                    'Actual Time': result['total_duration'],
                    'Difference': result['total_duration'] - result['original_time'],
                    'Start Time': result['start_time'],
                    'End Time': result['end_time']
                })
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            print("\n" + "="*100)
            print("ROUTE SUMMARY TABLE")
            print("="*100)
            print(df.to_string(index=False))
            print("="*100)
            
            # Statistics
            print(f"\nTotal routes processed: {len(self.results)}")
            print(f"Successful: {len(summary_data)}")
            print(f"Failed: {len(self.results) - len(summary_data)}")
            
            if summary_data:
                avg_diff = df['Difference'].mean()
                print(f"Average time difference: {avg_diff:.1f} minutes")
                print(f"Shortest actual route: {df['Actual Time'].min()} minutes")
                print(f"Longest actual route: {df['Actual Time'].max()} minutes")


def main():
    # Load route data
    calculator = SBBRouteCalculator('output_step3/top_27_canton_routes.json')
    
    print("SBB Route Time Calculator")
    print(f"Date: {calculator.date} (Tuesday)")
    print(f"Start time: {calculator.start_time}")
    print(f"Total routes to process: 54 (27 paths × 2 directions)")
    print("-" * 50)
    
    # Process all routes
    calculator.process_all_routes()
    
    # Save final results
    calculator.save_results('sbb_routes_final.json')
    
    # Print final summary
    calculator.print_summary_table()
    
    print("\nProcessing complete!")


if __name__ == "__main__":
    main()