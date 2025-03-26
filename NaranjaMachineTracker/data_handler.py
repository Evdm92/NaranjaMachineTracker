import os
import json
import datetime

class DataHandler:
    """
    Handles data storage and retrieval for the machine utilization application.
    Uses a simple JSON file-based storage system.
    """
    
    def __init__(self, data_dir="data"):
        """
        Initialize the data handler.
        
        Args:
            data_dir (str): Directory to store data files
        """
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def save_data(self, timestamp, data):
        """
        Save machine utilization data for a specific timestamp.
        
        Args:
            timestamp (str): Timestamp identifier (format: "YYYY-MM-DD_HH")
            data (dict): Data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create filename from timestamp
            filename = os.path.join(self.data_dir, f"{timestamp}.json")
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def load_data(self, timestamp):
        """
        Load machine utilization data for a specific timestamp.
        
        Args:
            timestamp (str): Timestamp identifier (format: "YYYY-MM-DD_HH")
            
        Returns:
            dict: The loaded data or None if not found
        """
        try:
            filename = os.path.join(self.data_dir, f"{timestamp}.json")
            
            if not os.path.exists(filename):
                return None
            
            with open(filename, 'r') as f:
                data = json.load(f)
            
            return data
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def load_daily_data(self, date_str):
        """
        Load all machine utilization data for a specific date.
        
        Args:
            date_str (str): Date string (format: "YYYY-MM-DD")
            
        Returns:
            list: List of data entries for the day
        """
        try:
            daily_data = []
            
            # Check all possible hours (0-23)
            for hour in range(24):
                timestamp = f"{date_str}_{hour}"
                data = self.load_data(timestamp)
                
                if data:
                    daily_data.append(data)
            
            return daily_data
        except Exception as e:
            print(f"Error loading daily data: {e}")
            return []
    
    def load_date_range_data(self, start_date_str, end_date_str):
        """
        Load all machine utilization data for a range of dates.
        
        Args:
            start_date_str (str): Start date string (format: "YYYY-MM-DD")
            end_date_str (str): End date string (format: "YYYY-MM-DD")
            
        Returns:
            list: List of data entries for the date range
        """
        try:
            # Convert date strings to datetime objects
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            # Initialize result list
            range_data = []
            
            # Iterate through dates
            current_date = start_date
            while current_date <= end_date:
                daily_data = self.load_daily_data(str(current_date))
                range_data.extend(daily_data)
                
                # Move to next day
                current_date += datetime.timedelta(days=1)
            
            return range_data
        except Exception as e:
            print(f"Error loading date range data: {e}")
            return []
    
    def list_available_dates(self):
        """
        List all dates for which data is available.
        
        Returns:
            list: List of dates with available data
        """
        try:
            # Get all data files
            files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
            
            # Extract dates
            dates = set()
            for file in files:
                # Remove extension and extract date part
                date_str = file.replace('.json', '').split('_')[0]
                dates.add(date_str)
            
            return sorted(list(dates))
        except Exception as e:
            print(f"Error listing available dates: {e}")
            return []
