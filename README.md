# JDx_Quick_Setup
A Python app for connecting to, communicating with, and streaming from JDx sensors. This app will work on macOS, Linux, and Windows 10.

# Useage
## Prerequisits
+ Make sure you have Python >3.6 and pip isntalled.
+ Make sure you have device connected to serial port and appropriate serial drivers installed.
## Install and Setup
+ Clone the app to your local machine.
+ Navigate into the app directory. 
+ Create a local venv in the with "python -m venv .venv" (creates a virtual enviroment in ~/.venv)
+ Activate the eviroment using "source .venv/Scripts/activate" (linux) or .venv\Scripts\activate (Windows)
+ Install modules using "pip install -r requirements.txt"
+ Run "python jdx_stream.py" to start the app.
## Running the App
The app will scan for the JDI by issuing the ;000,q,q command (defaults to 19200 baud, Even parity, 1 stopbit, and 8 datab bytes). Once found, the app will issue the ;000,s,1 command and stream the output of the sensor to the terminal.
