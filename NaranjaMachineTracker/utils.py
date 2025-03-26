def get_machine_type(machine_number):
    """
    Returns the type of machine based on its number.
    
    Args:
        machine_number (int): The machine number (9-20)
        
    Returns:
        str: The machine type (Speed Packer or Jumble Filler)
    """
    if 9 <= machine_number <= 14:
        return "Speed Packer"
    elif 15 <= machine_number <= 20:
        return "Jumble Filler"
    else:
        return "Unknown"

def get_machine_capacity(machine_number, carton_type):
    """
    Returns the hourly capacity of a machine based on its number and carton type.
    
    Args:
        machine_number (int): The machine number (9-20)
        carton_type (str): The type of carton being processed
        
    Returns:
        int: The machine's hourly capacity for the specified carton type
    """
    # Speed Packers 9-10
    if machine_number in [9, 10]:
        if carton_type == "A02D":
            return 300
        elif carton_type in ["A07D", "A11D", "E15D"]:
            return 300
        elif carton_type == "E10D":
            return 200
        elif carton_type == "A15C":
            return 216
    
    # Speed Packers 11-14
    elif 11 <= machine_number <= 14:
        if carton_type == "A02D":
            return 360
        elif carton_type in ["A07D", "A11D", "E15D"]:
            return 360
        elif carton_type == "E10D":
            return 240
        elif carton_type == "A15C":
            return 264
    
    # Jumble Fillers 15-20
    elif 15 <= machine_number <= 20:
        return 210
    
    # Default fallback
    return 0

def calculate_utilization(cartons_packed, capacity):
    """
    Calculates the utilization percentage of a machine.
    
    Args:
        cartons_packed (int): The number of cartons packed in an hour
        capacity (int): The machine's capacity per hour
        
    Returns:
        float: The utilization percentage (0-100)
    """
    if capacity > 0:
        utilization = (cartons_packed / capacity) * 100
        return min(utilization, 100)  # Cap at 100%
    return 0
