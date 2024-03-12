import sys
import os
import datetime

import serial
import serial.tools.list_ports

from PyQt5 import QtWidgets, uic, QtCore

import pyqtgraph
import pyqtgraph.exporters

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


def send_serial_data(connection: serial.Serial, packet: str) -> None:
    """send serial data to device.

    Args:
        connection (serial.Serial): open serial connection
        packet (str): data to send over connection.
    """
    connection.write(packet.encode())


def read_serial_data(connection: serial.Serial) -> str:
    """read serial data from connection.

    Args:
        connection (serial.Serial): open serial connection

    Returns:
        str: data returned from open serial connection
    """
    return connection.readline().decode("utf-8")


class JDx_Configuration_Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(JDx_Configuration_Window, self).__init__()

        # get the path to the ui file
        ui_file = "JDx_configuration.ui"

        # load the ui file
        uic.loadUi(ui_file, self)

        self.base = os.path.expanduser("~")

        # MENU BAR ACTIONS
        ############################################################################

        self.actAbout = self.findChild(QtWidgets.QAction, "actionAbout")
        self.actAbout.triggered.connect(self.about_page)

        self.actExit = self.findChild(QtWidgets.QAction, "actionExit")
        self.actExit.triggered.connect(self.exit)

        self.actionDownload_Settings = self.findChild(
            QtWidgets.QAction, "actionDownload_Settings"
        )
        self.actionDownload_Settings.triggered.connect(self.dump_settings)

        self.actionSave = self.findChild(QtWidgets.QAction, "actionSave")
        self.actionSave.triggered.connect(self.dump_settings)

        ############################################################################

        # BUTTONS
        ############################################################################

        self.connect_pb = self.findChild(QtWidgets.QPushButton, "connect_pb")
        self.connect_pb.clicked.connect(self.connect_to_sensor)

        self.send_pb = self.findChild(QtWidgets.QPushButton, "send_pb")
        self.send_pb.clicked.connect(self.send_command)

        self.exit_pb = self.findChild(QtWidgets.QPushButton, "exit_pb")
        self.exit_pb.clicked.connect(self.exit)

        self.dump_lut_pb = self.findChild(QtWidgets.QPushButton, "dump_lut_pb")
        self.dump_lut_pb.clicked.connect(self.update_plot)

        self.dump_settings_pb = self.findChild(
            QtWidgets.QPushButton, "dump_settings_pb"
        )
        self.dump_settings_pb.clicked.connect(self.dump_settings)

        self.export_pb = self.findChild(QtWidgets.QPushButton, "export_pb")
        self.export_pb.clicked.connect(self.export_plots)

        ############################################################################

        # LINE EDITS
        ############################################################################

        self.command_le = self.findChild(QtWidgets.QLineEdit, "command_le")

        self.model_le = self.findChild(QtWidgets.QLineEdit, "model_le")
        self.mfg_date_le = self.findChild(QtWidgets.QLineEdit, "mfg_date_le")
        self.serial_no_le = self.findChild(QtWidgets.QLineEdit, "serial_no_le")
        self.fw_version_le = self.findChild(QtWidgets.QLineEdit, "fw_version_le")
        self.bandwidth_le = self.findChild(QtWidgets.QLineEdit, "bandwidth_le")

        self.maf_le = self.findChild(QtWidgets.QLineEdit, "maf_le")
        self.maf_length_le = self.findChild(QtWidgets.QLineEdit, "maf_length_le")
        self.status_le = self.findChild(QtWidgets.QLineEdit, "status_le")
        self.decimation_le = self.findChild(QtWidgets.QLineEdit, "decimation_le")

        self.g_vector_le = self.findChild(QtWidgets.QLineEdit, "g_vector_le")
        self.temp_sensor_gain_le = self.findChild(
            QtWidgets.QLineEdit, "temp_sensor_gain_le"
        )
        self.temp_sensor_offset_le = self.findChild(
            QtWidgets.QLineEdit, "temp_sensor_offset_le"
        )
        self.odr_le = self.findChild(QtWidgets.QLineEdit, "odr_le")

        self.streaming_status_le = self.findChild(
            QtWidgets.QLineEdit, "streaming_status_le"
        )
        self.test_mode_le = self.findChild(QtWidgets.QLineEdit, "test_mode_le")
        self.relative_offset_le = self.findChild(
            QtWidgets.QLineEdit, "relative_offset_le"
        )

        self.O_x_le = self.findChild(QtWidgets.QLineEdit, "O_x_le")
        self.O_y_le = self.findChild(QtWidgets.QLineEdit, "O_y_le")
        self.O_z_le = self.findChild(QtWidgets.QLineEdit, "O_z_le")

        self.c_xx_le = self.findChild(QtWidgets.QLineEdit, "c_xx_le")
        self.c_xy_le = self.findChild(QtWidgets.QLineEdit, "c_xy_le")
        self.c_xz_le = self.findChild(QtWidgets.QLineEdit, "c_xz_le")

        self.c_yx_le = self.findChild(QtWidgets.QLineEdit, "c_yx_le")
        self.c_yy_le = self.findChild(QtWidgets.QLineEdit, "c_yy_le")
        self.c_yz_le = self.findChild(QtWidgets.QLineEdit, "c_yz_le")

        self.c_zx_le = self.findChild(QtWidgets.QLineEdit, "c_zx_le")
        self.c_zy_le = self.findChild(QtWidgets.QLineEdit, "c_zy_le")
        self.c_zz_le = self.findChild(QtWidgets.QLineEdit, "c_zz_le")

        self.x_cal_temp_1 = self.findChild(QtWidgets.QLineEdit, "x_cal_temp_1")
        self.x_cal_temp_2 = self.findChild(QtWidgets.QLineEdit, "x_cal_temp_2")
        self.x_cal_temp_3 = self.findChild(QtWidgets.QLineEdit, "x_cal_temp_3")

        self.y_cal_temp_1 = self.findChild(QtWidgets.QLineEdit, "y_cal_temp_1")
        self.y_cal_temp_2 = self.findChild(QtWidgets.QLineEdit, "y_cal_temp_2")
        self.y_cal_temp_3 = self.findChild(QtWidgets.QLineEdit, "y_cal_temp_3")

        self.log_filepath_le = self.findChild(QtWidgets.QLineEdit, "log_filepath_le")

        date_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filepath = os.path.join(self.base, f"JDx_log_{date_time}.txt")
        self.log_filepath_le.setText(filepath)

        ############################################################################

        # TEXT EDITS
        ############################################################################

        self.message_te = self.findChild(QtWidgets.QTextEdit, "message_te")

        ############################################################################

        # COMBO BOXES
        ############################################################################

        self.port_cb = self.findChild(QtWidgets.QComboBox, "port_cb")
        ports = [port.name for port in serial.tools.list_ports.comports()]
        self.port_cb.addItems(ports)

        self.baud_cb = self.findChild(QtWidgets.QComboBox, "baud_cb")

        self.parity_cb = self.findChild(QtWidgets.QComboBox, "parity_cb")

        ############################################################################

        ############################################################################

        # create the plotting widget.
        angle_limit_low = -95
        angle_limit_high = 95

        self.diff_plot = self.findChild(QtWidgets.QWidget, "diff_plot_pw")
        self.diff_plot.setTitle(
            "Deviation from Nominal vs ADC Counts", color="w", size="18pt"
        )
        styles = {"color": "white", "font-size": "18px"}
        self.diff_plot.setLabel("left", "Deviation (counts) (x1000)", **styles)
        self.diff_plot.setLabel("bottom", "ADC Counts (x1000)", **styles)
        # self.diff_plot.addLegend()
        self.diff_plot.showGrid(x=True, y=True)
        self.diff_plot.setXRange(-300, 300)

        self.plot = self.findChild(QtWidgets.QWidget, "lut_plot_pw")
        self.plot.setTitle("Angle vs ADC Counts", color="w", size="18pt")
        styles = {"color": "white", "font-size": "18px"}
        self.plot.setLabel("left", "Angle (arc-deg)", **styles)
        self.plot.setLabel("bottom", "ADC Counts (x1000)", **styles)
        self.plot.addLegend()
        self.plot.showGrid(x=True, y=True)
        self.plot.setYRange(angle_limit_low, angle_limit_high)
        self.plot.setXRange(-300, 300)
        # seed the plot data prior to starting.
        N = 1
        self.counts_x_temp_1 = list(range(N))
        self.lut_x_temp_1 = list(range(N))
        self.diff_x_temp_1 = list(range(N))

        self.counts_y_temp_1 = list(range(N))
        self.lut_y_temp_1 = list(range(N))
        self.diff_y_temp_1 = list(range(N))
        pen_x_temp_1 = pyqtgraph.mkPen(color=(29, 212, 8))
        pen_y_temp_1 = pyqtgraph.mkPen(color=(207, 203, 4))

        self.counts_x_temp_2 = list(range(N))
        self.lut_x_temp_2 = list(range(N))
        self.diff_x_temp_2 = list(range(N))
        self.counts_y_temp_2 = list(range(N))
        self.lut_y_temp_2 = list(range(N))
        self.diff_y_temp_2 = list(range(N))

        pen_x_temp_2 = pyqtgraph.mkPen(color=(237, 79, 74))
        pen_y_temp_2 = pyqtgraph.mkPen(color=(54, 235, 232))

        self.counts_x_temp_3 = list(range(N))
        self.lut_x_temp_3 = list(range(N))
        self.diff_x_temp_3 = list(range(N))
        self.counts_y_temp_3 = list(range(N))
        self.lut_y_temp_3 = list(range(N))
        self.diff_y_temp_3 = list(range(N))
        pen_x_temp_3 = pyqtgraph.mkPen(color=(240, 113, 238))
        pen_y_temp_3 = pyqtgraph.mkPen(color=(108, 101, 240))

        # Get a line reference
        self.line_x_temp_1 = self.plot.plot(
            self.counts_x_temp_1,
            self.lut_x_temp_1,
            name="X Data Temp 1",
            pen=pen_x_temp_1,
            symbol="+",
            symbolSize=5,
            symbolBrush="b",
        )
        self.line_y_temp_1 = self.plot.plot(
            self.counts_y_temp_1,
            self.lut_y_temp_1,
            name="Y Data Temp 1",
            pen=pen_y_temp_1,
            symbol="+",
            symbolSize=5,
            symbolBrush="b",
        )

        self.line_x_temp_2 = self.plot.plot(
            self.counts_x_temp_2,
            self.lut_x_temp_2,
            name="X Data Temp 2",
            pen=pen_x_temp_2,
            symbol="+",
            symbolSize=5,
            symbolBrush="b",
        )
        self.line_y_temp_2 = self.plot.plot(
            self.counts_y_temp_2,
            self.lut_y_temp_2,
            name="Y Data Temp 1",
            pen=pen_y_temp_2,
            symbol="+",
            symbolSize=5,
            symbolBrush="b",
        )

        self.line_x_temp_3 = self.plot.plot(
            self.counts_x_temp_3,
            self.lut_x_temp_3,
            name="X Data Temp 3",
            pen=pen_x_temp_3,
            symbol="+",
            symbolSize=5,
            symbolBrush="b",
        )
        self.line_y_temp_3 = self.plot.plot(
            self.counts_y_temp_3,
            self.lut_y_temp_3,
            name="Y Data Temp 3",
            pen=pen_y_temp_3,
            symbol="+",
            symbolSize=5,
            symbolBrush="b",
        )

        self.line_x_diff_1 = self.diff_plot.plot(
            self.counts_x_temp_1,
            self.diff_x_temp_1,
            name="Deviation X Data Temp 1",
            pen=pen_x_temp_1,
            symbol="+",
            symbolSize=5,
            symbolBrush="b",
        )
        self.line_y_diff_1 = self.diff_plot.plot(
            self.counts_y_temp_1,
            self.diff_y_temp_1,
            name="Deviation Y Data Temp 1",
            pen=pen_y_temp_1,
            symbol="+",
            symbolSize=5,
            symbolBrush="b",
        )

        self.line_x_diff_2 = self.diff_plot.plot(
            self.counts_x_temp_2,
            self.diff_x_temp_2,
            name="Deviation X Data Temp 2",
            pen=pen_x_temp_2,
            symbol="+",
            symbolSize=5,
            symbolBrush="b",
        )
        self.line_y_diff_2 = self.diff_plot.plot(
            self.counts_y_temp_2,
            self.diff_y_temp_2,
            name="Deviation Y Data Temp 2",
            pen=pen_y_temp_2,
            symbol="+",
            symbolSize=5,
            symbolBrush="b",
        )

        self.line_x_diff_3 = self.diff_plot.plot(
            self.counts_x_temp_3,
            self.diff_x_temp_3,
            name="Deviation X Data Temp 3",
            pen=pen_x_temp_3,
            symbol="+",
            symbolSize=5,
            symbolBrush="b",
        )
        self.line_y_diff_3 = self.diff_plot.plot(
            self.counts_y_temp_3,
            self.diff_y_temp_3,
            name="Deviation Y Data Temp 3",
            pen=pen_y_temp_3,
            symbol="+",
            symbolSize=5,
            symbolBrush="b",
        )

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)

        self.deviations_x_temp_1 = []
        self.deviations_y_temp_1 = []
        self.deviations_x_temp_2 = []
        self.deviations_y_temp_2 = []
        self.deviations_x_temp_3 = []
        self.deviations_y_temp_3 = []

        self.connected_to_sensor = False

        self.show()

    def about_page(self):
        """open the about page."""
        self.about = about_window.About_Window()
        self.about.show()

    def dump_settings(self):
        """
        Summary: this method sends some query commands to the JDx sensor and loads the results into the respective line edits.
        """

        self.message_te.append("Dumping settings from the sensor.")

        data = self.query_and_log_response(";000,q,q\r\n")
        data = data.split(",")

        self.model_le.setText(data[4])
        self.mfg_date_le.setText(data[10].split("=")[1])
        self.serial_no_le.setText(data[5])
        self.fw_version_le.setText(data[6].split(" ")[1])
        self.decimation_le.setText(data[21].split("=")[1])
        streaming_status = "On" if int(data[14].split("=")[1]) == 1 else "Off"
        test_mode_status = "On" if int(data[15].split("=")[1]) == 1 else "Off"
        self.streaming_status_le.setText(streaming_status)
        self.test_mode_le.setText(test_mode_status)
        self.relative_offset_le.setText(data[17].split("=")[1])

        self.temp_sensor_gain_le.setText(data[18].split("=")[1])
        self.temp_sensor_offset_le.setText(data[19].split("=")[1])
        self.odr_le.setText(data[20].split("=")[1])

        data = self.query_and_log_response(";000,q,gf\r\n")
        data = data.split(",")
        self.g_vector_le.setText(data[3].split(":")[1].replace(" ", ""))

        data = self.query_and_log_response(";000,q,be\r\n")
        data = data.split(",")
        self.maf_le.setText(data[4])
        data = self.query_and_log_response(";000,q,bl\r\n")
        data = data.split(",")
        self.maf_length_le.setText(data[3])
        data = self.query_and_log_response(";000,q,b\r\n")
        data = data.split(",")
        self.bandwidth_le.setText(data[5])

        data = self.query_and_log_response(";000,q,gf\r\n")
        data = data.split(",")
        self.g_vector_le.setText(data[3].split(":")[1].replace(" ", ""))

        # get the orthorenormalization matrix
        for i in range(3):
            data = self.query_and_log_response(
                f";000,q,ma{i}\r\n"
            )  # get orthonormalization matrix
            # parse the data string.
            data = data.replace(" ", "").split(":")[1].split(",")
            if i == 0:
                self.c_xx_le.setText(f"{float(data[0]):.5f}")
                self.c_yx_le.setText(f"{float(data[1]):.5f}")
                self.c_zx_le.setText(f"{float(data[2]):.5f}")
            elif i == 1:
                self.c_xy_le.setText(f"{float(data[0]):.5f}")
                self.c_yy_le.setText(f"{float(data[1]):.5f}")
                self.c_zy_le.setText(f"{float(data[2]):.5f}")
            else:
                self.c_xz_le.setText(f"{float(data[0]):.5f}")
                self.c_yz_le.setText(f"{float(data[1]):.5f}")
                self.c_zz_le.setText(f"{float(data[2]):.5f}")

        data = self.query_and_log_response(";000,q,mb\r\n")
        data = data.replace(" ", "").split(":")[1].split(",")

        self.O_x_le.setText(f"{float(data[0]):.5f}")
        self.O_y_le.setText(f"{float(data[1]):.5f}")
        self.O_z_le.setText(f"{float(data[2]):.5f}")

    def query_and_log_response(self, arg: str) -> str:
        """send ascii data to sensor through serial port and read/log to file the response.

        Args:
            arg (str): string to be sent to sensor.

        Returns:
            str: response from the sensor.
        """
        # query the basic stuff
        send_serial_data(self.sensor, arg)
        result = read_serial_data(self.sensor).replace("+", "")
        with open(self.log_filepath_le.text(), "a") as file:
            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"{date_time} - {result}")

        return result

    def get_cal_temps(self, data: str) -> None:
        """parse the data string and get the temps at which the sensor was calibrated. These values come from the
        LUT output.


        Args:
            data (str): line from the LUT output stream.
        """
        if "Axis Temperatures" in data:
            if "X Axis" in data:
                data = data.split(",")
                temp_1 = data[1].split(":")[1].replace(" ", "")
                temp_2 = data[2]
                temp_3 = data[3]
                self.x_cal_temp_1.setText(temp_1)
                self.x_cal_temp_2.setText(temp_2)
                self.x_cal_temp_3.setText(temp_3)
            elif "Y Axis" in data:
                data = data.split(",")
                temp_1 = data[1].split(":")[1].replace(" ", "")
                temp_2 = data[2]
                temp_3 = data[3]
                self.y_cal_temp_1.setText(temp_1)
                self.y_cal_temp_2.setText(temp_2)
                self.y_cal_temp_3.setText(temp_3)

    def get_lut_from_sensor(self):
        """
        get the LUT from the sensor. The data will hammer the serial port until the "success,end of LUT" massage appears.
        """
        self.counts_x_temp_1 = []
        self.lut_x_temp_1 = []
        self.counts_y_temp_1 = []
        self.lut_y_temp_1 = []

        self.counts_x_temp_2 = []
        self.lut_x_temp_2 = []
        self.counts_y_temp_2 = []
        self.lut_y_temp_2 = []

        self.counts_x_temp_3 = []
        self.lut_x_temp_3 = []
        self.counts_y_temp_3 = []
        self.lut_y_temp_3 = []

        N = 0.001  # scaling for the ADC counts to a more friendly scale.

        # self.timer.start()
        send_serial_data(self.sensor, ";000,?\r\n")  # get the lut.
        while True:
            data = read_serial_data(self.sensor).replace("+", "")
            with open(self.log_filepath_le.text(), "a") as file:
                date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"{date_time} - {data}")

            if "057,?,success,end of LUT" in data or "Z Axis" in data:
                break
            self.get_cal_temps(data)

            data = data.split(",")

            if data[2] == "0":  # temp index
                if data[1] == "X":  # axis index
                    self.counts_x_temp_1.append(N * float(data[4]))
                    self.lut_x_temp_1.append(float(data[5]))
                elif data[1] == "Y":
                    self.counts_y_temp_1.append(N * float(data[4]))
                    self.lut_y_temp_1.append(float(data[5]))
            elif data[2] == "1":
                if data[1] == "X":
                    self.counts_x_temp_2.append(N * float(data[4]))
                    self.lut_x_temp_2.append(float(data[5]))
                elif data[1] == "Y":
                    self.counts_y_temp_2.append(N * float(data[4]))
                    self.lut_y_temp_2.append(float(data[5]))

            elif data[2] == "2":
                if data[1] == "X":
                    self.counts_x_temp_3.append(N * float(data[4]))
                    self.lut_x_temp_3.append(float(data[5]))
                elif data[1] == "Y":
                    self.counts_y_temp_3.append(N * float(data[4]))
                    self.lut_y_temp_3.append(float(data[5]))

    def get_deviations(self):
        """
        Compute and plot the deviations for all the LUT points from room temp.
        """
        self.nominal_x = self.counts_x_temp_2
        self.nominal_y = self.counts_y_temp_2
        for i in range(len(self.counts_x_temp_1)):
            self.deviations_x_temp_1.append(self.nominal_x[i] - self.counts_x_temp_1[i])
            self.deviations_y_temp_1.append(self.nominal_y[i] - self.counts_y_temp_1[i])

            self.deviations_x_temp_2.append(self.nominal_x[i] - self.counts_x_temp_2[i])
            self.deviations_y_temp_2.append(self.nominal_y[i] - self.counts_y_temp_2[i])

            self.deviations_x_temp_3.append(self.nominal_x[i] - self.counts_x_temp_3[i])
            self.deviations_y_temp_3.append(self.nominal_y[i] - self.counts_y_temp_3[i])

    def update_plot(self):
        """
        update each plot with data and lines.
        """

        self.message_te.append(
            "Downloading LUT from sensor, this will take a few minutes."
        )

        self.get_lut_from_sensor()

        self.get_deviations()

        self.line_x_diff_1.setData(self.counts_x_temp_1, self.deviations_x_temp_1)
        self.line_y_diff_1.setData(self.counts_y_temp_1, self.deviations_y_temp_1)

        self.line_x_diff_2.setData(self.counts_x_temp_2, self.deviations_x_temp_2)
        self.line_y_diff_2.setData(self.counts_y_temp_2, self.deviations_y_temp_2)

        self.line_x_diff_3.setData(self.counts_x_temp_3, self.deviations_x_temp_3)
        self.line_y_diff_3.setData(self.counts_y_temp_3, self.deviations_y_temp_3)

        self.line_x_temp_1.setData(self.counts_x_temp_1, self.lut_x_temp_1)
        self.line_y_temp_1.setData(self.counts_y_temp_1, self.lut_y_temp_1)

        self.line_x_temp_2.setData(self.counts_x_temp_2, self.lut_x_temp_2)
        self.line_y_temp_2.setData(self.counts_y_temp_2, self.lut_y_temp_2)

        self.line_x_temp_3.setData(self.counts_x_temp_3, self.lut_x_temp_3)
        self.line_y_temp_3.setData(self.counts_x_temp_3, self.lut_y_temp_3)

    def connect_to_sensor(self):
        """
        Open a serial connection to a JDx.
        """

        port = self.port_cb.currentText()
        baud = int(self.baud_cb.currentText())
        parity = self.parity_cb.currentText()

        if port == "Port":
            self.message_te.append("Please select a port")
        else:
            try:
                self.sensor = open_serial_connection(port, baud, parity=parity)
            except FileNotFoundError:
                self.message_te.append("Check the port")

            self.message_te.append("Connected!")
            self.connected_to_sensor = True

    def send_command(self):
        """
        Send ascii data to sensor and read response.
        """
        if self.connected_to_sensor is True:
            data = self.command_le.text()
            send_serial_data(self.sensor, f"{data}\r\n")
            data = read_serial_data(self.sensor)
            self.message_te.append(data)
        else:
            self.message_te.append("Not connected to the sensor.")

    def export_plots(self):
        """
        save plots to png files based on the serial number of the sensor.
        """

        exporter_diff = pyqtgraph.exporters.ImageExporter(self.diff_plot.plotItem)
        deviation_plot_file = os.path.join(
            self.base, f"{self.serial_no_le.text()}_Deviations_plot.png"
        )
        exporter_diff.export(deviation_plot_file)

        exporter = pyqtgraph.exporters.ImageExporter(self.plot.plotItem)
        # save to file
        lut_plot_file = os.path.join(
            self.base, f"{self.serial_no_le.text()}_LUT_plot.png"
        )
        exporter.export(lut_plot_file)

        self.message_te.append(f"Finished exporting plots to {self.base}.")

    def exit(self):
        """
        Close the app.
        """
        self.close()
        return


def jdx_display_window_window():
    """open the window and start the app."""
    app = QtWidgets.QApplication(sys.argv)
    window = JDx_Configuration_Window()  # noqa: F841
    app.exec_()


if __name__ == "__main__":
    jdx_display_window_window()
