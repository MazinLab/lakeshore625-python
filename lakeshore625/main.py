#!/usr/bin/env python3
"""
Main interface for Lakeshore625 Superconducting Magnet Power Supply
"""

import argparse
import serial
from .power_controller import PowerController

def main():
    parser = argparse.ArgumentParser(
        description="Lakeshore 625 Superconducting Magnet Power Supply Controller",
        epilog="""

Serial Settings:
  Default: 9600 baud, 8-bit data, odd parity, 1 stop bit
  Port: /dev/ttyUSB0 (use --port to change)
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Device information
    parser.add_argument("--info", action="store_true", help="Get device information (*IDN?, BAUD?)")
    
    # Serial communication settings
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial port (default: /dev/ttyUSB0)")
    parser.add_argument("--get-baud", action="store_true", help="Get current baud rate setting (BAUD?)")
    
    # Ramp Control Commands
    parser.add_argument("--get-field", action="store_true", help="Get current magnetic field reading (RDGF?)")
    parser.add_argument("--get-current", action="store_true", help="Get current current reading (RDGI?)")
    parser.add_argument("--get-voltage", action="store_true", help="Get currentvoltage reading (RDGV?)")
    parser.add_argument("--set-current", type=float, help="Set target current in Amps (SETI)")
    parser.add_argument("--get-compliance-voltage", action="store_true", help="Get compliance voltage limit (SETV?)")
    parser.add_argument("--set-compliance-voltage", type=float, help="Set compliance voltage limit in V (SETV)")
    parser.add_argument("--get-rate", action="store_true", help="Get ramp rate (RATE?)")
    parser.add_argument("--set-rate", type=float, help="Set ramp rate in A/s (RATE)")
    parser.add_argument("--start-ramp", action="store_true", help="Start ramp (RAMP)")
    parser.add_argument("--stop-ramp", action="store_true", help="Stop ramp (STOP)")


    # Safety/Quench commands
    parser.add_argument("--get-max-limits", action="store_true", help="Get all max limits (LIMIT?)")
    parser.add_argument("--set-max-limits", nargs=3, type=float, metavar=('CURRENT', 'VOLTAGE', 'RATE'), help="Set max limits: current(0-60.1A), voltage(0.1-5.0V), rate(0.0001-99.999A/s) (LIMIT)")
    parser.add_argument("--quench-status", action="store_true", help="Get quench detection status (QNCH?)")
    parser.add_argument("--enable-quench", action="store_true", help="Enable quench detection (QNCH 1)")
    parser.add_argument("--disable-quench", action="store_true", help="Disable quench detection (QNCH 0)")

    # Raw serial command
    parser.add_argument("--raw-command", type=str, help="Send raw command to device")
    
    args = parser.parse_args()

    try:
        power_controller = PowerController(port=args.port)

        # Raw command execution
        if args.raw_command:
            print(f"Command: {args.raw_command}")
            response = power_controller.send_command(args.raw_command)
            print(f"Response: {response}")
            return

        # Device information
        if args.info:
            print("Device Information:")
            print("Command: *IDN?")
            identification = power_controller.get_identification()
            print("Command: BAUD?")
            baud_rate = power_controller.get_baud_rate()
            print(f"  ID: {identification}")
            print(f"  Baud Rate Code: {baud_rate} (0=9600, 1=19200, 2=38400, 3=57600)")
            print()

        # Baud rate operations
        if args.get_baud:
            print("Command: BAUD?")
            baud_code = power_controller.get_baud_rate()
            baud_map = {"0": "9600", "1": "19200", "2": "38400", "3": "57600"}
            baud_str = baud_map.get(baud_code, f"Unknown ({baud_code})")
            print(f"Current baud rate: {baud_str} baud (code: {baud_code})")

        # Power control operations
        if args.get_field:
            print("Command: RDGF?")
            field = power_controller.get_field()
            print(f"Magnetic field: {field} T")

        if args.get_current:
            print("Command: RDGI?")
            current = power_controller.get_current()
            print(f"Current: {current} A")

        if args.get_voltage:
            print("Command: RDGV?")
            voltage = power_controller.get_voltage()
            print(f"Voltage: {voltage} V")

        if args.get_compliance_voltage:
            print("Command: SETV?")
            compliance_voltage = power_controller.get_compliance_voltage()
            print(f"Compliance voltage limit: {compliance_voltage} V")

        if args.set_compliance_voltage is not None:
            print(f"Command: SETV {args.set_compliance_voltage}")
            response = power_controller.set_compliance_voltage(args.set_compliance_voltage)
            print(f"Set compliance voltage limit to {args.set_compliance_voltage} V")
            if response:
                print(f"Response: {response}")

        if args.set_current is not None:
            print(f"Command: SETI {args.set_current}")
            response = power_controller.set_current(args.set_current)
            print(f"Set current to {args.set_current} A")
            if response:
                print(f"Response: {response}")

        if args.get_rate:
            print("Command: RATE?")
            rate = power_controller.get_ramp_rate()
            print(f"Ramp rate: {rate} A/s")

        if args.set_rate is not None:
            print(f"Command: RATE {args.set_rate}")
            response = power_controller.set_ramp_rate(args.set_rate)
            print(f"Set ramp rate to {args.set_rate} A/s")
            if response:
                print(f"Response: {response}")

        if args.start_ramp:
            print("Command: RAMP")
            response = power_controller.start_ramp()
            print("Started current ramp")
            if response:
                print(f"Response: {response}")
            print("Tip: Run 'python3 logging.py' in a separate terminal to log ramp data")

        if args.stop_ramp:
            print("Command: STOP")
            response = power_controller.stop_ramp()
            print("Stopped current ramp")
            if response:
                print(f"Response: {response}")

        if args.quench_status:
            print("Command: QNCH?")
            quench = power_controller.get_quench_detect()
            print(f"Quench detection: {quench}")
            if quench and quench != "NO_RESPONSE":
                try:
                    parts = quench.split(',')
                    if len(parts) >= 2:
                        status = parts[0].strip()
                        step_limit = parts[1].strip()
                        if status == "1":
                            print("Quench Detection: ON")
                        elif status == "0":
                            print("Quench Detection: OFF")
                        print(f"Step Limit: {step_limit} A/s")
                except:
                    pass

        if args.enable_quench:
            print("Command: QNCH 1")
            response = power_controller.set_quench_detect(True)
            print("Enabled quench detection")
            if response:
                print(f"Response: {response}")

        if args.disable_quench:
            print("Command: QNCH 0")
            response = power_controller.set_quench_detect(False)
            print("Disabled quench detection")
            if response:
                print(f"Response: {response}")

        if args.get_max_limits:
            print("Command: LIMIT?")
            limits = power_controller.get_limits()
            if limits and limits != "NO_RESPONSE":
                try:
                    current_limit, voltage_limit, rate_limit = limits.split(',')
                    print(f"Current limit: {current_limit.strip()} A")
                    print(f"Voltage limit: {voltage_limit.strip()} V")
                    print(f"Rate limit: {rate_limit.strip()} A/s")
                except ValueError:
                    print(f"Limits: {limits}")
            else:
                print("No response from device")

        if args.set_max_limits:
            current_limit, voltage_limit, rate_limit = args.set_max_limits
            print(f"Command: LIMIT {current_limit}, {voltage_limit}, {rate_limit}")
            try:
                response = power_controller.set_limits(current_limit, voltage_limit, rate_limit)
                print(f"Set limits to: Current={current_limit}A, Voltage={voltage_limit}V, Rate={rate_limit}A/s")
                if response:
                    print(f"Response: {response}")
            except ValueError as e:
                print(f"Error: {e}")



    # Handle serial connection issues
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
        print(f"Make sure the Lakeshore 625 is connected to {args.port} and the port is correct.")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            power_controller.close()
        except:
            pass

if __name__ == "__main__":
    main()