# Swiss Train Challenge 🚂🇨🇭

A computational approach to finding the shortest train route through all 26 Swiss cantons using public transportation data from the SBB (Swiss Federal Railways) API.

## 📋 Overview

This project tackles the Swiss Train Challenge - finding the optimal route to visit all 26 Swiss cantons using public transportation in the shortest possible time. The solution uses a multi-step approach combining graph algorithms, dynamic programming, and real-time SBB schedule data.

**Current Best Route**: 12 hours 35 minutes (755 minutes)

## 🎯 Challenge Description

The Swiss Train Challenge requires:

- Visiting all 26 Swiss cantons
- Using only public transportation (trains, buses, trams)
- Finding the shortest total travel time
- Starting and ending at any station

## 📂 Project Structure

```
├── step1_define_stations.py     # Define canton data and stations
├── step2_find_shortest_times.py # Query SBB API for connection times
├── step3_find_shortest_route.py # Find optimal routes using algorithms
├── step4_actual_times.py        # Calculate real-world timetable times
├── output_step2/
│   └── swiss_canton_connection_times.json
├── output_step3/
│   └── top_27_canton_routes.json
├── visualization_of_shortest_route.html
└── README.md
```

## 🔧 Implementation Steps

### Step 1: Define Canton Data (`step1_define_stations.py`)

- Maps out all 26 Swiss cantons and their neighbors
- Defines key train stations for each canton
- Creates the graph structure for route finding

**Key Data Structures**:

- `neighbors`: Dictionary mapping each canton to its neighboring cantons
- `swiss_canton_stations`: List of representative stations per canton

### Step 2: Find Connection Times (`step2_find_shortest_times.py`)

- Queries the SBB OpenData Transport API for all station-to-station connections
- Builds a comprehensive database of travel times between neighboring cantons
- Processes ~768 unique connections
- Saves results to JSON for offline analysis

**API Used**: `http://transport.opendata.ch/v1/connections`

### Step 3: Find Optimal Routes (`step3_find_shortest_route.py`)

- Implements a sophisticated path-finding algorithm
- Splits Switzerland into two regions (East/West) for optimization
- Uses dynamic programming with bitmask states to track visited cantons
- Identifies 3 optimal split points: Olten, Zofingen, Aarau
- Generates top 27 route combinations (3 split points × 3 west routes × 3 east routes)

**Algorithm Features**:

- Priority queue-based search with canton coverage heuristic
- State representation: (station, visited_cantons_bitmask)
- Finds multiple solutions with different end stations

### Step 4: Calculate Actual Times (`step4_actual_times.py`)

- Converts theoretical routes to real-world timetables
- Queries SBB API for actual departure/arrival times
- Handles timezone conversions and overnight journeys
- Processes all 54 variations (27 routes × 2 directions)

## 🏆 Results

### Best Route Found

- **Total Time**: 12 hours 35 minutes (755 minutes)
- **Split Point**: Olten
- **Route Type**: West region ending at St-Maurice, East region ending at S. Vittore, Zona industriale

### Top 3 Routes

1. **Olten Split**: 755 minutes (West → St-Maurice, East → S. Vittore)
2. **Aarau Split**: 755 minutes (West → St-Maurice, East → S. Vittore)
3. **Zofingen Split**: 762 minutes (West → St-Maurice, East → S. Vittore)

### Route Visualization

See `visualization_of_shortest_route.html` for an interactive map of the optimal route.

## ⚠️ Known Issues

### 1. Appenzell Bus Connections

- **Problem**: Cannot find BUS B226 connections between Appenzell Innerrhoden and Appenzell Ausserrhoden
- **Impact**: May affect route optimization in Eastern Switzerland
- **Status**: Using alternative station connections

### 2. Basel Connection Issue

- **Problem**: Liestal to Basel SBB connection occasionally fails in API queries
- **Workaround**: Route uses alternative connections when necessary

### 3. Early Morning Departures

- **Issue**: Some remote stations (e.g., S. Vittore, Zona industriale) have limited early morning connections
- **Solution**: Algorithm adjusts start times based on first available departure

## 🛠️ Technical Details

### Dependencies

```python
- requests          # API calls
- pandas           # Data analysis
- json             # Data storage
- heapq            # Priority queue
- datetime         # Time calculations
```

### API Rate Limiting

- The SBB API allows up to 16 connections per query
- Processing all routes requires ~800 API calls
- Estimated processing time: 6-7 minutes for initial data collection

### Canton Regions

**West Region (10 cantons)**:
Basel-Stadt, Basel-Landschaft, Bern, Fribourg, Geneva, Jura, Neuchâtel, Solothurn, Valais, Vaud

**East Region (16 cantons)**:
Aargau, Appenzell Ausserrhoden, Appenzell Innerrhoden, Glarus, Graubünden, Lucerne, Nidwalden, Obwalden, Schaffhausen, Schwyz, St. Gallen, Thurgau, Ticino, Uri, Zug, Zurich

## 📊 Performance Comparison

Current leader board: [Swiss Train Challenge 2025](https://modellbahn.mahrer.net/ontour/2025_03_15_swisstrainchallenge/)

Our computational approach finds routes competitive with manual planning while exploring a much larger solution space.

## 🚀 Usage

1. **Data Collection**:

   ```bash
   python step1_define_stations.py
   python step2_find_shortest_times.py
   ```

2. **Route Finding**:

   ```bash
   python step3_find_shortest_route.py
   ```

3. **Timetable Verification**:
   ```bash
   python step4_actual_times.py
   ```

## 📈 Future Improvements

1. **Dynamic Station Selection**: Automatically identify optimal stations per canton
2. **Multi-modal Optimization**: Better integration of bus connections
3. **Time-of-Day Optimization**: Account for rush hours and service frequency
4. **Parallel Processing**: Speed up API queries with concurrent requests
5. **Machine Learning**: Predict connection times without API calls

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional station data for better coverage
- Alternative routing algorithms
- Visualization enhancements
- Real-time route tracking

## 📜 License

This project is for educational and research purposes. Please respect the SBB OpenData API terms of service.

## 🙏 Acknowledgments

- SBB OpenData for providing the transport API
- The Swiss Train Challenge community
- All contributors to Swiss public transportation data

---

_Last updated: June 2025_
