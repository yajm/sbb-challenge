import requests
import json
from typing import Dict, Optional
from step1_define_stations import neighbors, swiss_canton_stations
from datetime import datetime


def duration_to_minutes(duration_str: str) -> int:
    """Convert duration string format '00d00:39:00' to minutes."""
    parts = duration_str.split(':')
    day_part = parts[0]
    d_index = day_part.find('d')
    days = int(day_part[:d_index])
    hours = int(day_part[d_index+1:])
    minutes = int(parts[1])
    return days * 24 * 60 + hours * 60 + minutes

def fetch_connection(from_station: str, to_station: str) -> Optional[int]:
    """Fetch the shortest connection time between two stations."""
    url = f"http://transport.opendata.ch/v1/connections"
    params = {
        'from': from_station,
        'to': to_station,
        'limit': 16,  # Maximum limit according to API docs
        'time': '08:00',  # Tuesday morning at 8:00
        'date': '2025-06-17'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('connections'):
            # Find the shortest duration
            shortest_minutes = float('inf')
            
            for conn in data['connections']:
                minutes = duration_to_minutes(conn['duration'])
                if minutes < shortest_minutes:
                    shortest_minutes = minutes
            
            return shortest_minutes if shortest_minutes != float('inf') else None
        
        return None
    except Exception as e:
        print(f"Error fetching {from_station} to {to_station}: {e}")
        return None

def create_comprehensive_connection_times() -> Dict[str, Dict[str, Dict[str, any]]]:
    """
    Create a comprehensive dictionary of connection times between all station 
    combinations of neighboring cantons.
    
    Structure:
    {
        "Canton1": {
            "Canton2": {
                "connections": [
                    {
                        "from_station": "Station1",
                        "to_station": "Station2", 
                        "minutes": 45
                    },
                    ...
                ],
                "shortest": {
                    "from_station": "Station1",
                    "to_station": "Station2",
                    "minutes": 45
                }
            }
        }
    }
    """
    connection_times = {}
    processed_pairs = set()
    
    # Calculate total number of connections to fetch
    total_connections = 0
    for canton, neighbor_list in neighbors.items():
        for neighbor in neighbor_list:
            pair_id = tuple(sorted([canton, neighbor]))
            if pair_id not in processed_pairs:
                from_stations = swiss_canton_stations.get(canton, [])
                to_stations = swiss_canton_stations.get(neighbor, [])
                total_connections += len(from_stations) * len(to_stations)
                processed_pairs.add(pair_id)
    
    processed_pairs.clear()
    connection_count = 0
    
    print(f"Total connections to fetch: {total_connections}")
    print(f"Estimated time: {total_connections * 0.5 / 60:.1f} minutes\n")
    
    start_time = datetime.now()
    
    for canton, neighbor_list in neighbors.items():
        if canton not in connection_times:
            connection_times[canton] = {}
        
        for neighbor in neighbor_list:
            # Create unique pair identifier
            pair_id = tuple(sorted([canton, neighbor]))
            
            # Skip if already processed
            if pair_id in processed_pairs:
                if neighbor in connection_times and canton in connection_times[neighbor]:
                    # Copy the data in reverse direction
                    connection_times[canton][neighbor] = {
                        "connections": [
                            {
                                "from_station": conn["to_station"],
                                "to_station": conn["from_station"],
                                "minutes": conn["minutes"]
                            }
                            for conn in connection_times[neighbor][canton]["connections"]
                        ],
                        "shortest": {
                            "from_station": connection_times[neighbor][canton]["shortest"]["to_station"],
                            "to_station": connection_times[neighbor][canton]["shortest"]["from_station"],
                            "minutes": connection_times[neighbor][canton]["shortest"]["minutes"]
                        } if connection_times[neighbor][canton].get("shortest") else None
                    }
                continue
            
            # Get all station combinations
            from_stations = swiss_canton_stations.get(canton, [])
            to_stations = swiss_canton_stations.get(neighbor, [])
            
            if not from_stations or not to_stations:
                print(f"Missing stations for canton: {canton if not from_stations else neighbor}")
                continue
            
            print(f"\n{canton} <-> {neighbor} ({len(from_stations)} x {len(to_stations)} = {len(from_stations) * len(to_stations)} connections)")
            
            connections = []
            shortest_connection = None
            shortest_time = float('inf')
            
            for from_station in from_stations:
                for to_station in to_stations:
                    connection_count += 1
                    progress = connection_count / total_connections * 100
                    
                    print(f"  [{connection_count}/{total_connections}] ({progress:.1f}%) {from_station} -> {to_station}", end="")
                    
                    # Fetch connection time
                    connection_time = fetch_connection(from_station, to_station)
                    
                    if connection_time is not None:
                        connections.append({
                            "from_station": from_station,
                            "to_station": to_station,
                            "minutes": connection_time
                        })
                        
                        # Track shortest connection
                        if connection_time < shortest_time:
                            shortest_time = connection_time
                            shortest_connection = {
                                "from_station": from_station,
                                "to_station": to_station,
                                "minutes": connection_time
                            }
                        
                        print(f" -> {connection_time} min ({connection_time // 60}h {connection_time % 60}min)")
                    else:
                        print(f" -> No connection found")
                    

            
            # Store the data
            if connections:
                connection_data = {
                    "connections": connections,
                    "shortest": shortest_connection
                }
                
                connection_times[canton][neighbor] = connection_data
                
                # Store reverse direction
                if neighbor not in connection_times:
                    connection_times[neighbor] = {}
                    
                connection_times[neighbor][canton] = {
                    "connections": [
                        {
                            "from_station": conn["to_station"],
                            "to_station": conn["from_station"],
                            "minutes": conn["minutes"]
                        }
                        for conn in connections
                    ],
                    "shortest": {
                        "from_station": shortest_connection["to_station"],
                        "to_station": shortest_connection["from_station"],
                        "minutes": shortest_connection["minutes"]
                    } if shortest_connection else None
                }
            
            processed_pairs.add(pair_id)
    
    elapsed_time = (datetime.now() - start_time).total_seconds() / 60
    print(f"\n\nCompleted in {elapsed_time:.1f} minutes")
    
    return connection_times

def save_summary_json(connection_times: Dict, filename: str = "swiss_canton_connection_times_summary.json"):
    """Save a simplified version with just the shortest connections."""
    summary = {}
    
    for canton, connections in connection_times.items():
        summary[canton] = {}
        for neighbor, data in connections.items():
            if data.get("shortest"):
                summary[canton][neighbor] = {
                    "minutes": data["shortest"]["minutes"],
                    "route": f"{data['shortest']['from_station']} -> {data['shortest']['to_station']}"
                }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"Summary saved to '{filename}'")

def main():
    print("Fetching comprehensive connection times between neighboring Swiss cantons...")
    print("This will fetch ALL possible station combinations between neighbors.\n")
    
    connection_times = create_comprehensive_connection_times()
    
    # Save full data
    with open('swiss_canton_connection_times_cheat.json', 'w', encoding='utf-8') as f:
        json.dump(connection_times, f, indent=2, ensure_ascii=False)
    
    print("\nFull data saved to 'swiss_canton_connection_times_comprehensive.json'")
    
    # Save summary version
    save_summary_json(connection_times)
    
    # Print summary
    print("\n\nSummary of shortest connection times:")
    for canton, connections in sorted(connection_times.items()):
        if connections:
            print(f"\n{canton}:")
            for neighbor, data in sorted(connections.items()):
                if data.get("shortest"):
                    shortest = data["shortest"]
                    hours = shortest["minutes"] // 60
                    minutes = shortest["minutes"] % 60
                    print(f"  -> {neighbor}: {hours}h {minutes}min via {shortest['from_station']} -> {shortest['to_station']}")

if __name__ == "__main__":
    main()