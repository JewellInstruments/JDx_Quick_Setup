# JDx_Quick_Setup
## Apps
This repo has two apps useful for connecting, streaming, visualizing, and debugging your JDx. These apps have been tested on Windows 10, MacOS, and linux (Debian).
### JDX Streaming
JDx_stream.py is a Python app for connecting to, communicating with, and streaming from JDx sensors.
### JDX Display
JDx_display.py is a Python app built on the Qt5 framework to help the user visualize the JDx output using a graphical display and interact with the JDx sensor.
### JDX Configuration
JDx_configuration.py is a Python app built on the Qt5 framework to help the user visualize the JDx settings and allows the user to send commands to the sensor.



# Usage
## Prerequisite
+ Make sure you have Python >3.6 and pip installed.
+ Make sure you have device connected to serial port and appropriate serial drivers installed.

## Install and Setup
+ Clone the app to your local machine.
+ Navigate into the app directory. 
+ Create a local venv in the directory with "python -m venv .venv" (creates a virtual environment in /.venv)
+ Activate the environment using "source .venv/Scripts/activate" (linux) or .venv\Scripts\activate (aWindows)
+ Install modules using "pip install -r requirements.txt"
+ Run "python jdx_stream.py" to start the app.

## Running the Apps

### JDX Streaming
The app will scan for the JDI by issuing the ;000,q,q command (defaults to 19200 baud, Even parity, 1 stopbit, and 8 datab bytes). Once found, the app will issue the ;000,s,1 command and stream the output of the sensor to the terminal.

### JDX Display
To use this app with a JDx connected to the PC. use the dropdown menus to select the port, baud, and parity of the sensor. The connect button will open the serial connection to the JDx.
From there, one can send command by typing in the command box and pressing send. The output will display in the message prompt.
Streaming data can be toggled with the toggle data stream button. The stream data will be logged to a text file (and datetime stamped) to the path shown in the log file path.

### JDX Configuration
To use this app with a JDx connected to the PC. use the dropdown menus to select the port, baud, and parity of the sensor. The connect button will open the serial connection to the JDx.
From there, one can dump the Lookup Table (LUT) and the settings by using the buttons on the main window. Plots show the LUT or each axis and over each temperature. The configuration data
is also loaded into the window.
