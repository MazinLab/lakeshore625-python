#!/usr/bin/env python3
"""
Power controller module for Lakeshore625 Superconducting Magnet Power Supply
Handles all serial comms with lakeshore625
"""

import serial
import time

class PowerController:
    
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        """
        Initialize the PowerController
        
        Args:
            port: Serial port path (default: /dev/ttyUSB0)  
            baudrate: Serial baud rate (default: 9600)
        """
        # Use Lakeshore 625 serial settings: 9600 baud, 7-bit data, odd parity, 1 stop bit
        self.ser = serial.Serial(
            port=port, 
            baudrate=baudrate, 
            bytesize=7,  # 7 data bits for Lakeshore 625
            parity='O',  # Odd parity
            stopbits=1, 
            timeout=2
        )
    
    def send_command(self, command):
        """
        Send a command to the device and return the response
        
        Args:
            command (str): Command to send
            
        Returns:
            str: Device response or None if error
        """
        try:
            # Clear any leftover data
            self.ser.reset_input_buffer()
            
            # Send command with CR+LF terminator (required by Lakeshore 625)
            self.ser.write((command + '\r\n').encode('ascii'))
            time.sleep(0.2)
            
            # Read response
            response = self.ser.readline().decode('ascii', errors='ignore').strip()
            return response
            
        except Exception as e:
            print(f"Communication error: {e}")
            return None

    def get_quench_detect(self):
        """
        Get quench detection status using QNCH? command
        
        Returns:
            str: Quench detection status
        """
        response = self.send_command("QNCH?")
        if response is None or response == "":
            return "NO_RESPONSE"
        return response

    def set_quench_detect(self, enable):
        """
        Set quench detection on/off using QNCH command
        
        Args:
            enable (bool): True to enable, False to disable
        """
        command = f"QNCH {1 if enable else 0}"
        return self.send_command(command)

    def set_quench_step_limit(self, step_limit):
        """
        Set quench detection step limit using QNCH command
        
        Args:
            step_limit (float): Step limit in A/s
        """
        command = f"QNCH 1,{step_limit}"
        return self.send_command(command)

    def get_ramp_rate(self):
        """
        Get current ramp rate using RATE? command
        
        Returns:
            str: Current ramp rate in A/s
        """
        response = self.send_command("RATE?")
        if response is None or response == "":
            return "NO_RESPONSE"
        return response

    def set_ramp_rate(self, rate):
        """
        Set ramp rate using RATE command
        
        Args:
            rate (float): Ramp rate in A/s
        """
        command = f"RATE {rate}"
        return self.send_command(command)

    def get_field(self):
        """
        Get magnetic field reading using RDGF? command
        
        Returns:
            str: Field in Tesla
        """
        response = self.send_command("RDGF?")
        if response is None or response == "":
            return "NO_RESPONSE"
        return response

    def get_voltage(self):
        """
        Get voltage reading using RDGV? command
        
        Returns:
            str: Voltage in V
        """
        response = self.send_command("RDGV?")
        if response is None or response == "":
            return "NO_RESPONSE"
        return response

    def get_current(self):
        """
        Get current reading using RDGI? command
        
        Returns:
            str: Current in A
        """
        response = self.send_command("RDGI?")
        if response is None or response == "":
            return "NO_RESPONSE"
        return response

    def set_current(self, current):
        """
        Set target current using SETI command
        
        Args:
            current (float): Target current in A
        """
        command = f"SETI {current}"
        return self.send_command(command)

    def get_limits(self):
        """
        Get all max limits using LIMIT? command
        
        Returns:
            str: Current limit, voltage limit, rate limit (comma-separated)
        """
        response = self.send_command("LIMIT?")
        if response is None or response == "":
            return "NO_RESPONSE"
        return response

    def get_compliance_voltage(self):
        """
        Get compliance voltage limit using SETV? command
        
        Returns:
            str: Current compliance voltage limit in V
        """
        response = self.send_command("SETV?")
        if response is None or response == "":
            return "NO_RESPONSE"
        return response

    def set_compliance_voltage(self, voltage):
        """
        Set compliance voltage limit using SETV command
        
        Args:
            voltage (float): Compliance voltage limit in V (0.1-5.0V)
        """
        if not (0.1 <= voltage <= 5.0):
            raise ValueError(f"Compliance voltage must be between 0.1 and 5.0 V, got {voltage}")
        command = f"SETV {voltage}"
        return self.send_command(command)

    def set_limits(self, current_limit, voltage_limit, rate_limit):
        """
        Set all limits using LIMIT command
        
        Args:
            current_limit (float): Maximum current limit in A (0-60.1000)
            voltage_limit (float): Maximum voltage limit in V (0.1000-5.0000)
            rate_limit (float): Maximum ramp rate limit in A/s (0.0001-99.999)
        """
        # Validate ranges according to manual specifications
        if not (0 <= current_limit <= 60.1000):
            raise ValueError(f"Current limit must be between 0 and 60.1000 A, got {current_limit}")
        if not (0.1000 <= voltage_limit <= 5.0000):
            raise ValueError(f"Voltage limit must be between 0.1000 and 5.0000 V, got {voltage_limit}")
        if not (0.0001 <= rate_limit <= 99.999):
            raise ValueError(f"Rate limit must be between 0.0001 and 99.999 A/s, got {rate_limit}")
            
        command = f"LIMIT {current_limit}, {voltage_limit}, {rate_limit}"
        return self.send_command(command)

    def start_ramp(self):
        """
        Start current ramp using RAMP command
        """
        return self.send_command("RAMP")

    def stop_ramp(self):
        """
        Stop/pause current ramp using STOP command
        """
        return self.send_command("STOP")

    def get_identification(self):
        """
        Get device identification using *IDN? command
        
        Returns:
            str: Device identification string
            str: "NO_RESPONSE" if communication error
        """
        response = self.send_command("*IDN?")
        if response is None or response == "":
            return "NO_RESPONSE"
        return response

    def get_baud_rate(self):
        """
        Get current baud rate setting using BAUD? command
        
        Returns:
            str: Baud rate code (0=9600, 1=19200, 2=38400, 3=57600)
            str: "NO_RESPONSE" if communication error
        """
        response = self.send_command("BAUD?")
        if response is None or response == "":
            return "NO_RESPONSE"
        return response

    def close(self):
        """
        Close the serial connection
        """
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()