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
    
    # Continue with rest of the input structure creation...
    # (truncated for brevity - this would include all the complex graph construction logic)
    
    return full_input_dict

# Create the input dictionary with reduced parameters
input_dict = create_slinklpy_input('sample_routes.csv', vehicle_capacity=5, time_horizon=10)

# Save the output to a JSON file
with open('slinklpy_input.json', 'w') as f:
    json.dump(input_dict, f, indent=2)  # indent=2 makes the JSON file nicely formatted

print(f"Input dictionary saved to 'slinklpy_input.json'")
