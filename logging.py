#!/usr/bin/env python3
"""
Ramp data logging for Lakeshore 625 Superconducting Magnet Power Supply
Continuously records ramp parameters every minute and saves to timestamped CSV
"""

import time
import csv
import os
import sys
from datetime import datetime

# Add the lakeshore625 module to the path
sys.path.append('/home/kids/lakeshore625-python')

from lakeshore625.power_controller import PowerController

class RampLogger:
    def __init__(self):
        # Initialize power controller
        self.power_controller = PowerController()
        # Data storage
        self.ramp_data = []
        # CSV file setup with automatic numbering
        self.start_date = datetime.now().strftime("%Y-%m-%d")
        # Create ramps directory if it doesn't exist
        os.makedirs("ramps", exist_ok=True)
        # Find next available filename
        self.csv_filename = self._get_next_csv_filename()
        # CSV headers
        self.headers = [
            "Timestamp",
            "Date",
            "Time",
            "Elapsed_Seconds",
            "Ramp_Rate_A_per_s",
            "Current_A",
            "Voltage_V", 
            "Field_T"
        ]
        self.column_widths = [28, 12, 12, 16, 18, 14, 14, 14]
        
    def _get_next_csv_filename(self):
        """Find the next available CSV filename with automatic numbering"""
        base_filename = f"ramps/{self.start_date}_ramp_log.csv"
        
        # If the base filename doesn't exist, use it
        if not os.path.exists(base_filename):
            return base_filename
        
        # Otherwise, find the next numbered version
        counter = 1
        while True:
            numbered_filename = f"ramps/{self.start_date}_ramp_log_{counter}.csv"
            if not os.path.exists(numbered_filename):
                return numbered_filename
            counter += 1
        
    def print_formatted_header(self):
        """Print nicely formatted header to terminal"""
        # Print header row
        header_line = ""
        for i, header in enumerate(self.headers):
            header_line += f"{header:<{self.column_widths[i]}}"
        print(header_line)
        
        # Print separator line
        separator_line = ""
        for width in self.column_widths:
            separator_line += "-" * width
        print(separator_line)
    
    def print_formatted_row(self, data_row):
        """Print nicely formatted data row to terminal"""
        formatted_line = ""
        for i, value in enumerate(data_row):
            # Special formatting for different columns
            if i == 3 and isinstance(value, float):
                # Elapsed seconds (1 decimal place)
                formatted_value = f"{value:.1f}"
            elif i in [4, 5, 6, 7] and isinstance(value, float):
                # Ramp rate, current, voltage, field (4 decimal places)
                formatted_value = f"{value:.4f}"
            elif isinstance(value, float):
                # Other numbers (2 decimal places)
                formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)
            formatted_line += f"{formatted_value:<{self.column_widths[i]}}"
        print(formatted_line)
        
    def get_ramp_data(self, start_time):
        """Get all required ramp data"""
        current_time = datetime.now()
        timestamp = current_time.isoformat()
        date_str = current_time.strftime("%Y-%m-%d")
        time_str = current_time.strftime("%H:%M:%S")
        elapsed = time.time() - start_time
        
        try:
            # Get ramp rate
            ramp_rate_str = self.power_controller.get_ramp_rate()
            try:
                ramp_rate = float(ramp_rate_str.replace('+', '')) if ramp_rate_str != "NO_RESPONSE" else None
            except:
                ramp_rate = None
                
            # Get current
            current_str = self.power_controller.get_current()
            try:
                current = float(current_str.replace('+', '')) if current_str != "NO_RESPONSE" else None
            except:
                current = None
                
            # Get voltage
            voltage_str = self.power_controller.get_voltage()
            try:
                voltage = float(voltage_str.replace('+', '')) if voltage_str != "NO_RESPONSE" else None
            except:
                voltage = None
                
            # Get field
            field_str = self.power_controller.get_field()
            try:
                field = float(field_str.replace('+', '').replace('E+00', '')) if field_str != "NO_RESPONSE" else None
            except:
                field = None
            
            return {
                "timestamp": timestamp,
                "date": date_str,
                "time": time_str,
                "elapsed": elapsed,
                "ramp_rate": ramp_rate,
                "current": current,
                "voltage": voltage,
                "field": field
            }
            
        except Exception as e:
            print(f"Error reading ramp data: {e}")
            return None
    
    def format_csv_row(self, data):
        """Format data dictionary as CSV row"""
        try:
            row = [
                data["timestamp"],
                data["date"],
                data["time"],
                data["elapsed"],
                data["ramp_rate"],
                data["current"],
                data["voltage"],
                data["field"]
            ]
            return row
        except Exception as e:
            print(f"Error formatting CSV row: {e}")
            return None
    
    def save_to_csv(self):
        """Save all recorded data to CSV file"""
        try:
            with open(self.csv_filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self.headers)
                writer.writerows(self.ramp_data)
        except Exception as e:
            print(f"Error saving CSV file: {e}")
    
    def create_formatted_csv(self):
        """Create CSV file with nicely formatted columns"""
        try:
            with open(self.csv_filename, 'w', newline='') as csvfile:
                # Write formatted header
                header_line = ""
                for i, header in enumerate(self.headers):
                    if i == len(self.headers) - 1:  # Last column
                        header_line += header
                    else:
                        header_line += f"{header:<{self.column_widths[i]}}"
                csvfile.write(header_line + "\n")
        except Exception as e:
            print(f"Error creating CSV file: {e}")
    
    def append_to_formatted_csv(self, data_row):
        """Append a formatted row to the CSV file"""
        try:
            with open(self.csv_filename, 'a', newline='') as csvfile:
                # Write formatted data row
                formatted_line = ""
                for i, value in enumerate(data_row):
                    # Special formatting for different columns
                    if i == 3 and isinstance(value, float):
                        # Elapsed seconds (1 decimal place)
                        formatted_value = f"{value:.1f}"
                    elif i in [4, 5, 6, 7] and isinstance(value, float):
                        # Ramp rate, current, voltage, field (4 decimal places)
                        formatted_value = f"{value:.4f}"
                    elif isinstance(value, float):
                        # Other numbers (2 decimal places)
                        formatted_value = f"{value:.2f}"
                    else:
                        formatted_value = str(value)
                    
                    if i == len(data_row) - 1:  # Last column
                        formatted_line += formatted_value
                    else:
                        formatted_line += f"{formatted_value:<{self.column_widths[i]}}"
                csvfile.write(formatted_line + "\n")
        except Exception as e:
            print(f"Error appending to CSV file: {e}")
    
    def run(self):
        """Main logging loop"""
        # Print startup information first
        print(f"Starting Lakeshore 625 ramp data logging...")
        print(f"Recording interval: 60 seconds")
        print(f"CSV file will be saved as: {self.csv_filename}")
        print(f"Press Ctrl+C to stop recording and save data")
        print("-" * 120)
        print()  # Empty line
        
        # Now print the formatted header
        self.print_formatted_header()
        
        # Create the CSV file immediately with formatted header
        self.create_formatted_csv()
        
        start_time = time.time()
        
        try:
            while True:
                # Get current readings
                data = self.get_ramp_data(start_time)
                
                if data:
                    # Format as CSV row
                    csv_row = self.format_csv_row(data)
                    
                    if csv_row:
                        # Store data
                        self.ramp_data.append(csv_row)
                        
                        # Print to terminal with nice formatting
                        self.print_formatted_row(csv_row)
                        
                        # Append to CSV file immediately
                        self.append_to_formatted_csv(csv_row)
                
                # Wait 60 seconds
                time.sleep(60)
                
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print(f"\n\nStopping ramp data logging.")
            print(f"Ramp log saved successfully!")
            print(f"Total readings recorded: {len(self.ramp_data)}")
            print(f"File location: {self.csv_filename}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            # Still save using the formatted method as backup
            self.save_to_csv()
        finally:
            # Close the power controller connection
            if hasattr(self, 'power_controller'):
                self.power_controller.close()

def main():
    """Main function"""
    logger = RampLogger()
    logger.run()

if __name__ == "__main__":
    main()