import sys
import os
import datetime

import pymodbus
from pymodbus.client import ModbusSerialClient

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
    return serial.Serial(port, baud, parity=parity, timeout=5)

def open_modbus_connection(met: str = 'rtu', pt: str = '9', baud: int = 19200, to:int = 5):
    client = ModbusSerialClient(method=met, port=pt, baudrate=baud, timeout=to)
    client.connect()
    return client

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

def read_modbus_packet(client):
    result = client.read_holding_registers(address=0x00, count=10, unit=1)

    # Check if the read was successful
    if not result.isError():
        # Access the registers
        registers = result.registers
        print(f"Registers: {registers}")
    else:
        print("Error reading registers")
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
            self.sensor = open_modbus_connection()
        else:
            self.sensor = open_serial_connection(port, baud, parity=parity)

        self.message_te.append("Connected!")
        self.connected_to_sensor = True

    def send_command(self):
        if self.connected_to_sensor is True:
            if self.STREAM_DATA is True:
                self.message_te.append(
                    "Cannot send command while app is streaming data. Please turn streaming off before sending commands."
                )
            else:
                data = self.command_le.text()
                if self.modbus_ch_bo.isChecked():
                    send_modbus_packet(self.sensor)
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
