import sys
import os
import datetime

import pymodbus
from pymodbus.client import ModbusSerialClient
#from pymodbus.payload import BinaryPayloadDecoder
#from pymodbus.constants import Endian
import Modbus_master

import serial
from serial import tools as SerialTools
import serial.tools.list_ports

from PyQt5 import QtWidgets, uic, QtCore

import pyqtgraph

import about_window


def open_serial_connection(port: str, baud: int, parity: str) -> serial.Serial:
    """open serial port to JDx sensor.

    Args:
        port (str): physical serial port
        baud (int): baud rate that sensor has
        parity (str): parity of sensor

    Returns:
        serial.Serial: open serial port connection.
    """
    found = True
    return serial.Serial(port, baud, parity=parity, timeout=5), found

#def open_modbus_connection(port: str, device:str = 0, baud: int = 19200, parity:int = 'n', data_bit: int = 8, stop_bit:int = 1):
#    client = ModbusSerialClient(port=port, baudrate=baud, parity=parity, stopbits=stop_bit, timeout=2, bytesize=data_bit)
#    found = False
#    if client.connect() is True:
#        qq = client.read_holding_registers(address=0, count=46, device_id=1, no_response_expected=False)
#        result = client.read_holding_registers(address=100, count=10, device_id=int(device), no_response_expected=False)
#        print(f"qq response: {qq.registers}")
#        print(f"result response: {result.registers}")
#        #client.close()
#        print("modbus connection worked")
#        found = True
#    return client, found

def open_modbus_connection(port: str, device:int = 1, baud: int = 19200, parity:str = 'E', data_bit: int = 8, stop_bit:int = 1):
    #modbus_unit_connection = Modbus_master.ModbusMaster(port='COM9', baudrate=19200, timeout=1)# this hardcode works
    modbus_unit_connection = Modbus_master.ModbusMaster(port=port, baudrate=baud, timeout=stop_bit)
    found = False
    if modbus_unit_connection.connect():
        qq = modbus_unit_connection.read_holding_registers(slave_id=device, start_address=0, count=46) #start adress 0 and count 46 is the qq command
        stats = modbus_unit_connection.get_statistics()
        if stats['responses_received'] > 0:
            #print(f"the qq response is: {qq}")
            found = True
    return modbus_unit_connection, found

def send_serial_data(connection: serial.Serial, packet: str) -> None:
    """send serial data to device.

    Args:
        connection (serial.Serial): open serial connection
        packet (str): data to send over connection.
    """
    connection.write(packet.encode())

def send_modbus_packet(connection: serial.Serial):
        
    return

def read_serial_data(connection: serial.Serial) -> str:
    """read serial data from connection.

    Args:
        connection (serial.Serial): open serial connection

    Returns:
        str: data returned from open serial connection
    """
    return connection.readline().decode("utf-8")

def read_modbus_packet(connection: serial.Serial):
    #connection.write('01 03 00 00 00 2E C5 D6') #unicode
    unicode = '01 03 00 00 00 2E C5 D6' #qq
    unicode = '01 04 00 C8 00 0A FF FF' #read data registers
    bytes = unicode.encode('utf-8')
    connection.write(bytes)
    method_1 = connection.read() #bytes
    method_2 = connection.readline()
    method_3 = connection.read_all()
    print(f"method 1: {method_1}")
    print(f"method 2: {method_2}")
    print(f"method 3: {method_3}")
    return


class JDx_Display_Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(JDx_Display_Window, self).__init__()

        # get the path to the ui file
        ui_file = "JDx_display.ui"

        # load the ui file
        uic.loadUi(ui_file, self)

        # MENU BAR ACTIONS
        ############################################################################
        #
        self.actAbout = self.findChild(QtWidgets.QAction, "actionAbout")
        self.actAbout.triggered.connect(self.about_page)

        self.actExit = self.findChild(QtWidgets.QAction, "actionExit")
        self.actExit.triggered.connect(self.exit)

        self.actSave = self.findChild(QtWidgets.QAction, "actionSave")
        self.actAbout.triggered.connect(self.save_messages)

        self.actStream = self.findChild(QtWidgets.QAction, "actionLog_Data")
        self.actStream.triggered.connect(self.toggle_stream)

        ############################################################################

        # BUTTONS
        ############################################################################

        self.connect_pb = self.findChild(QtWidgets.QPushButton, "connect_pb")
        self.connect_pb.clicked.connect(self.connect_to_sensor)

        self.send_pb = self.findChild(QtWidgets.QPushButton, "send_pb")
        self.send_pb.clicked.connect(self.send_command)

        self.exit_pb = self.findChild(QtWidgets.QPushButton, "exit_pb")
        self.exit_pb.clicked.connect(self.exit)

        self.stream_pb = self.findChild(QtWidgets.QPushButton, "stream_pb")
        self.stream_pb.clicked.connect(self.toggle_stream)
        self.STREAM_DATA = False

        ############################################################################

        # LINE EDITS
        ############################################################################

        self.command_le = self.findChild(QtWidgets.QLineEdit, "command_le")
        self.x_output_le = self.findChild(QtWidgets.QLineEdit, "x_output_le")
        self.y_output_le = self.findChild(QtWidgets.QLineEdit, "y_output_le")
        self.t_output_le = self.findChild(QtWidgets.QLineEdit, "t_output_le")
        self.address_le = self.findChild(QtWidgets.QLineEdit, "address_le")
        self.log_filepath_le = self.findChild(QtWidgets.QLineEdit, "log_filepath_le")
        self.unit_id_le = self.findChild(QtWidgets.QLineEdit, "unit_id_le")

        date_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filepath = os.path.join(os.path.expanduser("~"), f"JDx_log_{date_time}.txt")
        self.log_filepath_le.setText(filepath)

        ############################################################################

        # TEXT EDITS
        ############################################################################

        self.message_te = self.findChild(QtWidgets.QTextEdit, "message_te")

        ############################################################################

        # COMBO BOXES
        ############################################################################

        self.port_cb = self.findChild(QtWidgets.QComboBox, "port_cb")
        ports = [port.name for port in SerialTools.list_ports.comports()]
        self.port_cb.addItems(ports)

        self.baud_cb = self.findChild(QtWidgets.QComboBox, "baud_cb")

        self.parity_cb = self.findChild(QtWidgets.QComboBox, "parity_cb")

        ############################################################################

        ############################################################################

        # CHECK BOXES
        ############################################################################

        self.modbus_ch_bo = self.findChild(QtWidgets.QCheckBox, "modbus_ch_bo")

        ############################################################################

        ############################################################################

        # create the plotting widget.
        angle_limit_low = -95
        angle_limit_high = 95
        self.plot = self.findChild(QtWidgets.QWidget, "widget")

        self.plot.setTitle("Angle vs Time", color="w", size="18pt")
        styles = {"color": "white", "font-size": "18px"}
        self.plot.setLabel("left", "Angle (arc-deg)", **styles)
        self.plot.setLabel("bottom", "Time (sec)", **styles)
        self.plot.addLegend()
        self.plot.showGrid(x=True, y=True)
        self.plot.setYRange(angle_limit_low, angle_limit_high)
        # seed the plot data prior to starting.
        self.time = list(range(10))
        self.angle_x = [0 for _ in range(10)]
        self.angle_y = [0 for _ in range(10)]

        pen_x = pyqtgraph.mkPen(color=(255, 0, 255))
        pen_y = pyqtgraph.mkPen(color=(0, 255, 0))

        # Get a line reference
        self.line_x = self.plot.plot(
            self.time,
            self.angle_x,
            name="X Data",
            pen=pen_x,
            symbol="+",
            symbolSize=5,
            symbolBrush="b",
        )
        self.line_y = self.plot.plot(
            self.time,
            self.angle_y,
            name="Y Data",
            pen=pen_y,
            symbol="+",
            symbolSize=5,
            symbolBrush="r",
        )

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)

        self.connected_to_sensor = False

        self.show()

    def save_messages(self):
        data = self.message_te.toPlainText()
        with open(self.log_filepath_le.text(), "a") as file:
            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"{date_time} - {data}")
        return

    def about_page(self):
        self.about = about_window.About_Window()
        self.about.show()

    def update_plot(self):
        if self.modbus_ch_bo.isChecked():
            send_modbus_packet(self.sensor)
        else:
            send_serial_data(self.sensor, ";000,v,v\r\n")

        if self.modbus_ch_bo.isChecked():
            data = read_modbus_packet(self.sensor)
            print(f"data = {data}")
        else:
            data = read_serial_data(self.sensor).replace("+", "")
        with open(self.log_filepath_le.text(), "a") as file:
            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"{date_time} - {data}")

        data = data.split(",")

        try:
            x_data = float(data[3])
            y_data = float(data[4])
            temp = float(data[5])
            addr = data[0]
        except Exception as e:
            self.message_te.append(e)
            x_data = 0
            y_data = 0
            temp = 0
            addr = 0

        self.x_output_le.setText(f"{x_data:.4f}")
        self.y_output_le.setText(f"{y_data:.4f}")
        self.t_output_le.setText(f"{temp:.4f}")
        self.address_le.setText(f"{addr}")

        self.time = self.time[1:]
        self.time.append(self.time[-1] + 1)
        self.angle_x = self.angle_x[1:]
        self.angle_x.append(x_data)
        self.angle_y = self.angle_y[1:]
        self.angle_y.append(y_data)
        self.line_x.setData(self.time, self.angle_x)
        self.line_y.setData(self.time, self.angle_y)

    def connect_to_sensor(self):
        port = self.port_cb.currentText()
        baud = int(self.baud_cb.currentText())
        parity = self.parity_cb.currentText()
        if self.modbus_ch_bo.isChecked():
            self.sensor, found = open_modbus_connection(port, int(self.unit_id_le.text()), baud, parity)
        else:
            self.sensor, found = open_serial_connection(port, baud, parity=parity)

        if found is True:
            self.message_te.append("Connected!")
            self.connected_to_sensor = True
        else:
            self.message_te.append("Failed to connect to unit!")

        

    def send_command(self):
        if self.connected_to_sensor is True:
            if self.STREAM_DATA is True:
                self.message_te.append(
                    "Cannot send command while app is streaming data. Please turn streaming off before sending commands."
                )
            else:
                data = self.command_le.text()
                if self.modbus_ch_bo.isChecked():
                    send_modbus_packet(self.sensor, data)
                else:
                    send_serial_data(self.sensor, f"{data}\r\n")
                if self.modbus_ch_bo.isChecked():
                    data = read_modbus_packet(self.sensor)
                else:
                    data = read_serial_data(self.sensor)
                self.message_te.append(data)
        else:
            self.message_te.append("Not connected to the sensor.")

    def toggle_stream(self):
        if self.connected_to_sensor is True:
            if self.STREAM_DATA is True:
                self.message_te.append("Turning off data stream")
                self.STREAM_DATA = False
                self.timer.stop()
            else:
                self.STREAM_DATA = True
                self.message_te.append("Turning on data stream")
                self.message_te.append(
                    f"Logging data stream to {self.log_filepath_le.text()}"
                )
                self.timer.start()

        else:
            self.message_te.append("Not connected to the sensor.")
        return

    def exit(self):
        self.close()
        return


def jdx_display_window_window():
    """open the window and start the app."""
    app = QtWidgets.QApplication(sys.argv)
    window = JDx_Display_Window()  # noqa: F841
    app.exec_()


if __name__ == "__main__":
    jdx_display_window_window()
