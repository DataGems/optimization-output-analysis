import csv
import math
import json

def create_slinklpy_input(csv_path, vehicle_capacity=5, time_horizon=10):
    """
    Create input structures for SlinkLPy algorithm based on CVRPTW data.
    
    Parameters:
    -----------
    csv_path : str
        Path to CSV file with customer data
    vehicle_capacity : int
        Capacity of the vehicle
    time_horizon : int
        Start of time horizon
        
    Returns:
    --------
    dict
        Dictionary with input structures for SlinkLPy
    """
    
    # Read customer data using standard csv module
    customers = []
    customer_data = {}

    with open(csv_path, 'r', encoding='utf-8-sig') as csvfile:  # utf-8-sig handles the BOM
        reader = csv.DictReader(csvfile)
        
        # Store the actual column names from the reader
        column_names = reader.fieldnames
        print(f"CSV columns: {column_names}")
        
        # Get the actual name of the customer column (remove BOM if present)
        cust_column = 'CUST_NUM'
        if '\ufeffCUST_NUM' in column_names:
            cust_column = '\ufeffCUST_NUM'
        
        for row in reader:
            if len(customers) == 0:
                print(f"First row: {dict(row)}")
            
            cust_num = row[cust_column]
            customers.append(cust_num)
            customer_data[cust_num] = {
                'x': float(row['XCOORD.']),
                'y': float(row['YCOORD.']),
                'demand': int(row['DEMAND']),
                'ready_time': int(row['READY_TIME']),
                'due_date': int(row['DUE_DATE']),
                'service_time': int(row['SERVICE_TIME'])
            }
    
    # Initialize the full input dictionary
    full_input_dict = {}
    
    # Define depot indices
    start_depot = "startDepot"  # α
    end_depot = "endDepot"      # ᾱ
    
    # Calculate Euclidean distance between two points
    def calculate_distance(u, v):
        if u == start_depot or u == end_depot:
            u_x, u_y = 3.5, 3.5  # Depot coordinates
        else:
            u_x, u_y = customer_data[u]['x'], customer_data[u]['y']
            
        if v == start_depot or v == end_depot:
            v_x, v_y = 3.5, 3.5  # Depot coordinates
        else:
            v_x, v_y = customer_data[v]['x'], customer_data[v]['y']
        
        return math.sqrt((u_x - v_x)**2 + (u_y - v_y)**2)
    
    # Calculate travel time (distance + service time)
    def calculate_travel_time(u, v):
        distance = calculate_distance(u, v)
        
        # Add service time of u (if u is a customer)
        if u != start_depot and u != end_depot:
            service_time = customer_data[u]['service_time']
            total_time = distance + service_time
        else:
            total_time = distance
        
        # Round up to nearest 0.1
        ceil_value = math.ceil(total_time * 10) / 10
        return round(ceil_value * 10) / 10
    
    # 1. allDelta - auxiliary variables for time and capacity
    all_delta = []
    for customer in customers:
        all_delta.append(f"delta_capRem_{customer}")
        all_delta.append(f"delta_timeRem_{customer}")
    full_input_dict['allDelta'] = all_delta
    
    # 2. allGraphNames - names of all graphs
    full_input_dict['allGraphNames'] = ['TimeGraph', 'CapGraph']
    
    # 3. h2SourceId - source node identifiers for each graph
    full_input_dict['h2SourceId'] = {
        'TimeGraph': f'node_timeGraph_cust={start_depot}_timeRem={time_horizon}',
        'CapGraph': f'node_capGraph_cust={start_depot}_capRem={vehicle_capacity}'
    }
    
    # 4. h2sinkid - sink node identifiers for each graph
    full_input_dict['h2sinkid'] = {
        'TimeGraph': f'node_timeGraph_cust={end_depot}_timeRem=0',
        'CapGraph': f'node_capGraph_cust={end_depot}_capRem=0'
    }
    
    # 5. Create list of all possible edges (u,v) for our problem
    edges = []
    locations = customers + [start_depot, end_depot]
    
    for u in locations:
        for v in locations:
            # Skip invalid edges:
            # - No self-loops
            # - No edges from end_depot
            # - No edges to start_depot
            # - No direct connections from start_depot to end_depot
            if (u != v and 
                u != end_depot and 
                v != start_depot and
                not (u == start_depot and v == end_depot)):
                edges.append((u, v))
    
    # 6. allActions - list of all action names
    all_actions = []
    
    # Add null action
    null_action = "nullAction"
    all_actions.append(null_action)
    
    # Add actions for direct connections
    for u, v in edges:
        action_name = f"LAArc_{u}_{v}"
        all_actions.append(action_name)
    
    full_input_dict['allActions'] = all_actions
    
    # 7. nullAction - string for null action
    full_input_dict['nullAction'] = null_action
    
    # 8. allNonNullAction - all actions except null
    all_non_null_action = all_actions.copy()
    all_non_null_action.remove(null_action)
    full_input_dict['allNonNullAction'] = all_non_null_action
    
    # 9. allPrimitiveVars - for each edge (u,v), create 'psi_u_v'
    all_primitive_vars = []
    for u, v in edges:
        all_primitive_vars.append(f"psi_{u}_{v}")
    
    full_input_dict['allPrimitiveVars'] = all_primitive_vars
    
    # 10. action2Cost - map each action to its cost
    action_2_cost = {}
    
    # Null action has zero cost
    action_2_cost[null_action] = 0
    
    # For direct connections, cost is travel time
    for u, v in edges:
        action_name = f"LAArc_{u}_{v}"
        action_2_cost[action_name] = calculate_travel_time(u, v)
    
    full_input_dict['action2Cost'] = action_2_cost
    
    return full_input_dict

def clean_for_json(obj):
    """Convert tuples to strings in the dictionary to make it JSON-serializable"""
    if isinstance(obj, dict):
        return {str(k): clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(e) for e in obj]
    elif isinstance(obj, tuple):
        return str(obj)
    else:
        return obj

if __name__ == "__main__":
    # Create the input dictionary with reduced parameters
    input_dict = create_slinklpy_input('sample_routes.csv', vehicle_capacity=5, time_horizon=10)

    # Save the output to a JSON file
    with open('slinklpy_input.json', 'w') as f:
        json.dump(input_dict, f, indent=2)  # indent=2 makes the JSON file nicely formatted

    print(f"Input dictionary saved to 'slinklpy_input.json'")

    # Create a clean version that's guaranteed to be JSON-serializable
    with open('slinklpy_input_clean.json', 'w') as f:
        cleaned_dict = clean_for_json(input_dict)
        json.dump(cleaned_dict, f, indent=2)  # indent=2 makes the JSON file nicely formatted

    print(f"Cleaned dictionary saved to 'slinklpy_input_clean.json'")
