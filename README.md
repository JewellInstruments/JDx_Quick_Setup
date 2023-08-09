# JDx_Quick_Setup
A Python + Qt app for connecting to, communicating with, and streaming from JDx sensors. This app will work on macOS, Linux, and Windows 10.

# Useage
## Prerequisits
+ Make sure you have Python >3.6 and pip isntalled.
+ Make sure you have device connected to serial port and appropriate serial drivers installed.
## Install and Setup
+ Clone the app to your local machine.
+ Navigate into the app directory. 
+ Create a local venv in the with "python -m venv venv" (creates a virtual enviroment in ~/venv)
+ Activate the eviroment using "source venv/Scripts/activate" (linux and macOS) or venv\Scripts\activate (Windows)
+ Install modules using "pip install -r requirements.txt"
+ Run "python main.py" to start the app.
## Running the App
Upon starting the app, select the serial port and the baud rate the sensor has.
Click the connect button and turn power to the unit on. The splash message should appear.
