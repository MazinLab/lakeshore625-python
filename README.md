# lakeshore625-python
Python interface for communicating with lakeshore 625 superconducting power supply

## Installation ##  

```
git clone https://github.com/MazinLab/lakeshore625-python
python3 -m venv lakeshore625-env  
source lakeshore625-env/bin/activate    
cd lakeshore625-python  
pip install -e .    
```

## Safety
**Note, if your lakeshore 625 is configured in ramp mode, executing ``--set-current`` will start the ramp. Do not set this to a value until you are ready to start ramping. This is a large power supply, be aware of open circuits and shocks**  


## Basic Structure
The lakeshore625 is a power supply for controlling a superconducting magnet, ramping current up and down according to preset user parameters.  

This repository consists of:  
1) ``pyproject.toml`` which handles all necessary imports
2) ``power_controller.py`` which handles all direct serial commands with the lakeshore 625. This file includes several methods with functionality that can be called upon through CLI in main.py. For example ``set_ramp_rate`` is called upon as ``--set-ramp-rate`` as defined in ``main.py``. All methods contain direct serial commands as defined in the lakeshore 625 manual. It does not include every serial command available  
3) ``main.py`` initializes the CLI. It calls upon methods defined in ``power_controller.py``.
4) ``logging.py`` records the parameters of the lakeshore 625, best run during a ramp up or ramp down to monitor voltages and current


## Usage Examples   
To execute a basic ramp up then ramp down, we would execute the following steps:

### 1. Check Max Limits   
Before running anything, we want to ensure quench detection is on (``lakeshore 625 --enable-quench``).  

We also want to set our max limits/quench detection limits. Note, these are different than the compliance voltage and target current. Compliance voltage is the voltage as which the ramp will stop if it exceeds and target current is the current the ramp is attempting to reach. The maximum voltage and maximum currents, when reached, will trigger a quench detection and everything will shut off. The maximum voltage, current, and rate should be higher than the compliance voltage, target current, and ramp rate or else the ramp will be interrupted.  

We can set maximum limits by running ``lakeshore625 --set-max-limits CURRENT VOLTAGE RATE``  

### 2. Set compliance voltage and ramp rate   
YOu can set your compliance voltage with `` lakeshore625 --set-compliance-voltage VOLTAGE`` and set the rate with ``lakeshore625 --set-rate RATE``. Voltage is in volts and rate is in A/s.  

### 3. Start logging  
Run ``logging.py`` to log the lakeshore 625 parameters through the cycle. It will create a new .csv file stored in the ramps/ folder. 

### 3. When ready, set target current   
Execute `` lakeshore625 --set-current CURRENT``.   
The lakeshore 625 should immediately start ramping to that current at the rate you specified. It will automatically stop when it reaches that current, or if it reaches your quench detection limit. 

Note, to "ramp down" simply set the target current to 0 and it will begin ramping down.   



Nikki Zivkov 2/19/26


