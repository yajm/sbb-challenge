import json
from typing import List, Tuple, Set, Dict
from collections import defaultdict
import heapq
from datetime import datetime

class SwissCantonRegionalPathFinder:
    def __init__(self, comprehensive_file: str):
        """Initialize with comprehensive connection times from JSON file."""
        with open(comprehensive_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.cantons = sorted(list(self.data.keys()))
        self.canton_to_id = {canton: i for i, canton in enumerate(self.cantons)}
        
        # Define regions - Solothurn is now only in west
        self.west_cantons = {
            "Geneva", "Vaud", "Valais", "Fribourg", "Neuchâtel", 
            "Jura", "Basel-Stadt", "Basel-Landschaft", "Solothurn", "Bern"
        }
        
        self.east_cantons = {
            "Zurich", "Aargau", "Lucerne", "Uri", "Schwyz", 
            "Obwalden", "Nidwalden", "Glarus", "Zug", "St. Gallen",
            "Appenzell Innerrhoden", "Appenzell Ausserrhoden", 
            "Thurgau", "Schaffhausen", "Graubünden", "Ticino"
        }
        
        # Define possible split points
        self.split_points = ["Olten", "Zofingen", "Aarau"]
        
        # Build the graph
        self.connections = {}  # (from_station, to_station) -> minutes
        self.station_to_canton = {}  # station -> canton
        self.canton_to_stations = defaultdict(set)  # canton -> set of stations
        
        self._build_graph()
        
    def _build_graph(self):
        """Build connection graph and station mappings."""
        for from_canton in self.data:
            for to_canton in self.data[from_canton]:
                conn_data = self.data[from_canton][to_canton]
                if 'connections' in conn_data:
                    for conn in conn_data['connections']:
                        from_st = conn['from_station']
                        to_st = conn['to_station']
                        minutes = conn['minutes']
                        
                        self.connections[(from_st, to_st)] = minutes
                        self.station_to_canton[from_st] = from_canton
                        self.station_to_canton[to_st] = to_canton
                        self.canton_to_stations[from_canton].add(from_st)
                        self.canton_to_stations[to_canton].add(to_st)
        
        # Build adjacency list
        self.neighbors = defaultdict(list)
        for (from_st, to_st), minutes in self.connections.items():
            self.neighbors[from_st].append((to_st, minutes))
        
        print(f"Built graph with {len(self.canton_to_stations)} cantons")
        print(f"Total stations: {len(self.station_to_canton)}")
        print(f"Total connections: {len(self.connections)}")
        
        # Verify split points exist
        for sp in self.split_points:
            if sp not in self.station_to_canton:
                print(f"WARNING: {sp} not found in stations!")
            else:
                print(f"{sp} is in canton: {self.station_to_canton[sp]}")
    
    def find_top_k_paths(self, region: Set[str], start_station: str, k: int = 3) -> List[Dict]:
        """
        Find top K shortest paths visiting all cantons in a specific region.
        Simply collects all complete solutions found during search.
        """
        # Create mask for region cantons
        region_canton_ids = {self.canton_to_id[c] for c in region if c in self.canton_to_id}
        region_mask = sum(1 << i for i in region_canton_ids)
        
        # Priority queue: (priority, time, station, mask, path)
        pq = []
        
        # Best time to reach each state
        best_time = {}
        
        # Store ALL complete solutions found
        complete_solutions = []
        
        # Initialize with start station
        if start_station not in self.station_to_canton:
            print(f"Error: {start_station} not found in station list")
            return []
        
        start_canton = self.station_to_canton[start_station]
        canton_id = self.canton_to_id[start_canton]
        mask = 1 << canton_id if start_canton in region else 0
        state = (start_station, mask)
        best_time[state] = 0
        priority = -bin(mask).count('1') * 10000 + 0
        heapq.heappush(pq, (priority, 0, start_station, mask, [start_station]))
        
        while pq:
            priority, current_time, current_station, current_mask, path = heapq.heappop(pq)
            
            # Skip if we've found a better path to this state
            state = (current_station, current_mask)
            if state in best_time and best_time[state] < current_time:
                continue
            
            # Check if we've visited all cantons in the region
            if (current_mask & region_mask) == region_mask:
                # Add this complete solution
                complete_solutions.append({
                    'stations': path,
                    'cantons': [self.station_to_canton[st] for st in path],
                    'time': current_time,
                    'end_station': current_station
                })
                continue
            
            # Explore neighbors
            for next_station, travel_time in self.neighbors[current_station]:
                next_canton = self.station_to_canton[next_station]
                next_canton_id = self.canton_to_id[next_canton]
                
                # Only set bit if canton is in our target region
                if next_canton in region:
                    next_mask = current_mask | (1 << next_canton_id)
                else:
                    next_mask = current_mask
                
                next_time = current_time + travel_time
                next_state = (next_station, next_mask)
                
                if next_state not in best_time or best_time[next_state] > next_time:
                    best_time[next_state] = next_time
                    next_cantons_visited = bin(next_mask & region_mask).count('1')
                    next_priority = -next_cantons_visited * 10000 + next_time
                    heapq.heappush(pq, (next_priority, next_time, next_station, 
                                       next_mask, path + [next_station]))
        
        # Sort by time
        complete_solutions.sort(key=lambda x: x['time'])
        
        # Group by end station and keep only the best time for each
        best_by_end = {}
        for sol in complete_solutions:
            end = sol['end_station']
            if end not in best_by_end or sol['time'] < best_by_end[end]['time']:
                best_by_end[end] = sol
        
        # Get top K unique end stations
        unique_solutions = sorted(best_by_end.values(), key=lambda x: x['time'])
        
        return unique_solutions[:k]
    
    def find_all_combinations(self):
        """Find all combinations of split points with top 3 east and west solutions."""
        print("Finding all combinations of Swiss canton tours")
        print("="*80)
        print(f"West region ({len(self.west_cantons)} cantons): {', '.join(sorted(self.west_cantons))}")
        print(f"East region ({len(self.east_cantons)} cantons): {', '.join(sorted(self.east_cantons))}")
        print(f"Split points: {', '.join(self.split_points)}")
        print(f"Finding top 3 solutions for each region at each split point")
        
        all_combinations = []
        
        # For each split point
        for split_point in self.split_points:
            print(f"\n{'='*60}")
            print(f"Processing split point: {split_point}")
            print(f"{'='*60}")
            
            # Find top 3 west solutions
            print(f"Finding top 3 west solutions from {split_point}...")
            west_solutions = self.find_top_k_paths(self.west_cantons, split_point, k=3)
            print(f"Found {len(west_solutions)} west solutions")
            for i, sol in enumerate(west_solutions):
                print(f"  West #{i+1}: {sol['time']} min, ends at {sol['end_station']}")
            
            # Find top 3 east solutions
            print(f"Finding top 3 east solutions from {split_point}...")
            east_solutions = self.find_top_k_paths(self.east_cantons, split_point, k=3)
            print(f"Found {len(east_solutions)} east solutions")
            for i, sol in enumerate(east_solutions):
                print(f"  East #{i+1}: {sol['time']} min, ends at {sol['end_station']}")
            
            # Create all combinations
            for i, west in enumerate(west_solutions):
                for j, east in enumerate(east_solutions):
                    # Skip duplicate split point in combined path
                    combined_stations = west['stations'] + east['stations'][1:]
                    combined_time = west['time'] + east['time']
                    
                    combination = {
                        'split_point': split_point,
                        'west_rank': i + 1,
                        'east_rank': j + 1,
                        'west_time': west['time'],
                        'east_time': east['time'],
                        'total_time': combined_time,
                        'west_end': west['end_station'],
                        'east_end': east['end_station'],
                        'west_path': west['stations'],
                        'east_path': east['stations'],
                        'combined_path': combined_stations
                    }
                    
                    all_combinations.append(combination)
        
        # Sort by total time
        all_combinations.sort(key=lambda x: x['total_time'])
        
        # Add ranking
        for i, combo in enumerate(all_combinations):
            combo['rank'] = i + 1
        
        # Print ranking
        print(f"\n{'='*80}")
        print("TOP 27 ROUTE COMBINATIONS RANKING")
        print(f"{'='*80}")
        print(f"{'Rank':>4} | {'Split Point':^12} | {'West End':^20} | {'East End':^20} | "
              f"{'West':>8} | {'East':>8} | {'Total':>8}")
        print("-" * 100)
        
        for combo in all_combinations:
            total_h = combo['total_time'] // 60
            total_m = combo['total_time'] % 60
            print(f"{combo['rank']:>4} | {combo['split_point']:^12} | "
                  f"{combo['west_end'][:20]:^20} | {combo['east_end'][:20]:^20} | "
                  f"{combo['west_time']:>8} | {combo['east_time']:>8} | "
                  f"{combo['total_time']:>6} ({total_h}h{total_m:02d})")
        
        # Save to JSON
        output = {
            'metadata': {
                'total_combinations': len(all_combinations),
                'split_points': self.split_points,
                'west_cantons': sorted(list(self.west_cantons)),
                'east_cantons': sorted(list(self.east_cantons)),
                'timestamp': datetime.now().isoformat()
            },
            'rankings': all_combinations
        }
        
        with open('top_27_canton_routes.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*80}")
        print(f"Saved all {len(all_combinations)} route combinations to 'top_27_canton_routes.json'")
        
        # Print summary statistics
        if all_combinations:
            print(f"\nSUMMARY STATISTICS:")
            print(f"Best overall time: {all_combinations[0]['total_time']} minutes "
                  f"({all_combinations[0]['total_time']//60}h {all_combinations[0]['total_time']%60}min)")
            print(f"  Split: {all_combinations[0]['split_point']}, "
                  f"West ends at: {all_combinations[0]['west_end']}, "
                  f"East ends at: {all_combinations[0]['east_end']}")
            
            print(f"Worst overall time: {all_combinations[-1]['total_time']} minutes "
                  f"({all_combinations[-1]['total_time']//60}h {all_combinations[-1]['total_time']%60}min)")
            
            # Best for each split point
            print(f"\nBest time for each split point:")
            for sp in self.split_points:
                sp_combos = [c for c in all_combinations if c['split_point'] == sp]
                if sp_combos:
                    best = min(sp_combos, key=lambda x: x['total_time'])
                    print(f"  {sp}: {best['total_time']} minutes (Rank #{best['rank']})")

def main():
    print("Swiss Canton Path Finder - Top 27 Route Combinations")
    print("Finding best 3 west × best 3 east × 3 split points = 27 total routes")
    print("=" * 80)
    
    finder = SwissCantonRegionalPathFinder('output_step2/swiss_canton_connection_times.json')
    finder.find_all_combinations()

if __name__ == "__main__":
    main()