# The MIT License (MIT)
#
# Copyright (c) 2017 Tony DiCola for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_lsm9ds1`
====================================================

CircuitPython module for the LSM9DS1 accelerometer, magnetometer, gyroscope.
Based on the driver from:
  https://github.com/adafruit/Adafruit_LSM9DS1

See examples/simpletest.py for a demo of the usage.

* Author(s): Tony DiCola
"""
import time

import adafruit_bus_device.i2c_device as i2c_device
import adafruit_bus_device.spi_device as spi_device


# Internal constants and register values:
_LSM9DS1_ADDRESS_ACCELGYRO       = const(0x6B)
_LSM9DS1_ADDRESS_MAG             = const(0x1E)
_LSM9DS1_XG_ID                   = const(0b01101000)
_LSM9DS1_MAG_ID                  = const(0b00111101)
_LSM9DS1_ACCEL_MG_LSB_2G         = 0.061
_LSM9DS1_ACCEL_MG_LSB_4G         = 0.122
_LSM9DS1_ACCEL_MG_LSB_8G         = 0.244
_LSM9DS1_ACCEL_MG_LSB_16G        = 0.732
_LSM9DS1_MAG_MGAUSS_4GAUSS       = 0.14
_LSM9DS1_MAG_MGAUSS_8GAUSS       = 0.29
_LSM9DS1_MAG_MGAUSS_12GAUSS      = 0.43
_LSM9DS1_MAG_MGAUSS_16GAUSS      = 0.58
_LSM9DS1_GYRO_DPS_DIGIT_245DPS   = 0.00875
_LSM9DS1_GYRO_DPS_DIGIT_500DPS   = 0.01750
_LSM9DS1_GYRO_DPS_DIGIT_2000DPS  = 0.07000
_LSM9DS1_TEMP_LSB_DEGREE_CELSIUS = 8 # 1°C = 8, 25° = 200, etc.
_LSM9DS1_REGISTER_WHO_AM_I_XG    = const(0x0F)
_LSM9DS1_REGISTER_CTRL_REG1_G    = const(0x10)
_LSM9DS1_REGISTER_CTRL_REG2_G    = const(0x11)
_LSM9DS1_REGISTER_CTRL_REG3_G    = const(0x12)
_LSM9DS1_REGISTER_TEMP_OUT_L     = const(0x15)
_LSM9DS1_REGISTER_TEMP_OUT_H     = const(0x16)
_LSM9DS1_REGISTER_STATUS_REG     = const(0x17)
_LSM9DS1_REGISTER_OUT_X_L_G      = const(0x18)
_LSM9DS1_REGISTER_OUT_X_H_G      = const(0x19)
_LSM9DS1_REGISTER_OUT_Y_L_G      = const(0x1A)
_LSM9DS1_REGISTER_OUT_Y_H_G      = const(0x1B)
_LSM9DS1_REGISTER_OUT_Z_L_G      = const(0x1C)
_LSM9DS1_REGISTER_OUT_Z_H_G      = const(0x1D)
_LSM9DS1_REGISTER_CTRL_REG4      = const(0x1E)
_LSM9DS1_REGISTER_CTRL_REG5_XL   = const(0x1F)
_LSM9DS1_REGISTER_CTRL_REG6_XL   = const(0x20)
_LSM9DS1_REGISTER_CTRL_REG7_XL   = const(0x21)
_LSM9DS1_REGISTER_CTRL_REG8      = const(0x22)
_LSM9DS1_REGISTER_CTRL_REG9      = const(0x23)
_LSM9DS1_REGISTER_CTRL_REG10     = const(0x24)
_LSM9DS1_REGISTER_OUT_X_L_XL     = const(0x28)
_LSM9DS1_REGISTER_OUT_X_H_XL     = const(0x29)
_LSM9DS1_REGISTER_OUT_Y_L_XL     = const(0x2A)
_LSM9DS1_REGISTER_OUT_Y_H_XL     = const(0x2B)
_LSM9DS1_REGISTER_OUT_Z_L_XL     = const(0x2C)
_LSM9DS1_REGISTER_OUT_Z_H_XL     = const(0x2D)
_LSM9DS1_REGISTER_WHO_AM_I_M     = const(0x0F)
_LSM9DS1_REGISTER_CTRL_REG1_M    = const(0x20)
_LSM9DS1_REGISTER_CTRL_REG2_M    = const(0x21)
_LSM9DS1_REGISTER_CTRL_REG3_M    = const(0x22)
_LSM9DS1_REGISTER_CTRL_REG4_M    = const(0x23)
_LSM9DS1_REGISTER_CTRL_REG5_M    = const(0x24)
_LSM9DS1_REGISTER_STATUS_REG_M   = const(0x27)
_LSM9DS1_REGISTER_OUT_X_L_M      = const(0x28)
_LSM9DS1_REGISTER_OUT_X_H_M      = const(0x29)
_LSM9DS1_REGISTER_OUT_Y_L_M      = const(0x2A)
_LSM9DS1_REGISTER_OUT_Y_H_M      = const(0x2B)
_LSM9DS1_REGISTER_OUT_Z_L_M      = const(0x2C)
_LSM9DS1_REGISTER_OUT_Z_H_M      = const(0x2D)
_LSM9DS1_REGISTER_CFG_M          = const(0x30)
_LSM9DS1_REGISTER_INT_SRC_M      = const(0x31)
_MAGTYPE                         = True
_XGTYPE                          = False
_SENSORS_GRAVITY_STANDARD        = 9.80665

# User facing constants/module globals.
ACCELRANGE_2G                = (0b00 << 3)
ACCELRANGE_16G               = (0b01 << 3)
ACCELRANGE_4G                = (0b10 << 3)
ACCELRANGE_8G                = (0b11 << 3)
MAGGAIN_4GAUSS               = (0b00 << 5)  # +/- 4 gauss
MAGGAIN_8GAUSS               = (0b01 << 5)  # +/- 8 gauss
MAGGAIN_12GAUSS              = (0b10 << 5)  # +/- 12 gauss
MAGGAIN_16GAUSS              = (0b11 << 5)  # +/- 16 gauss
GYROSCALE_245DPS             = (0b00 << 4)  # +/- 245 degrees/s rotation
GYROSCALE_500DPS             = (0b01 << 4)  # +/- 500 degrees/s rotation
GYROSCALE_2000DPS            = (0b11 << 4)  # +/- 2000 degrees/s rotation

class LSM9DS1:

    # Class-level buffer for reading and writing data with the sensor.
    # This reduces memory allocations but means the code is not re-entrant or
    # thread safe!
    _BUFFER = bytearray(6)

    def __init__(self):
        # soft reset & reboot accel/gyro
        self._write_u8(_XGTYPE, _LSM9DS1_REGISTER_CTRL_REG8, 0x05)
        # soft reset & reboot magnetometer
        self._write_u8(_MAGTYPE, _LSM9DS1_REGISTER_CTRL_REG2_M, 0x0C)
        time.sleep(0.01)
        # Check ID registers.
        if self._read_u8(_XGTYPE, _LSM9DS1_REGISTER_WHO_AM_I_XG) != _LSM9DS1_XG_ID or \
           self._read_u8(_MAGTYPE, _LSM9DS1_REGISTER_WHO_AM_I_M) != _LSM9DS1_MAG_ID:
            raise RuntimeError('Could not find LSM9DS1, check wiring!')
        # enable gyro continuous
        self._write_u8(_XGTYPE, _LSM9DS1_REGISTER_CTRL_REG1_G, 0xC0) # on XYZ
        # Enable the accelerometer continous
        self._write_u8(_XGTYPE, _LSM9DS1_REGISTER_CTRL_REG5_XL, 0x38)
        self._write_u8(_XGTYPE, _LSM9DS1_REGISTER_CTRL_REG6_XL, 0xC0)
        # enable mag continuous
        self._write_u8(_MAGTYPE, _LSM9DS1_REGISTER_CTRL_REG3_M, 0x00)
        # Set default ranges for the various sensors
        self.accel_range = ACCELRANGE_2G
        self.mag_gain = MAGGAIN_4GAUSS
        self.gyro_scale = GYROSCALE_245DPS

    @property
    def accel_range(self):
        """Get and set the accelerometer range.  Must be a value of:
          - ACCELRANGE_2G
          - ACCELRANGE_4G
          - ACCELRANGE_8G
          - ACCELRANGE_16G
        """
        reg = self._read_u8(_XGTYPE, LSM9DS1_REGISTER_CTRL_REG6_XL)
        return (reg & 0b00011000) & 0xFF

    @accel_range.setter
    def accel_range(self, val):
        assert val in (ACCELRANGE_2G, ACCELRANGE_4G, ACCELRANGE_8G,
                       ACCELRANGE_16G)
        reg = self._read_u8(_XGTYPE, LSM9DS1_REGISTER_CTRL_REG6_XL)
        reg = (reg & ~(0b00011000)) & 0xFF
        reg |= val
        self._write_u8(_XGTYPE, _LSM9DS1_REGISTER_CTRL_REG6_XL, reg)
        if val == _LSM9DS1_ACCELRANGE_2G:
            self._accel_mg_lsb = _LSM9DS1_ACCEL_MG_LSB_2G
        elif val == _LSM9DS1_ACCELRANGE_4G:
            self._accel_mg_lsb = _LSM9DS1_ACCEL_MG_LSB_4G
        elif val == _LSM9DS1_ACCELRANGE_8G:
            self._accel_mg_lsb = _LSM9DS1_ACCEL_MG_LSB_8G
        elif val == _LSM9DS1_ACCELRANGE_16G:
            self._accel_mg_lsb = _LSM9DS1_ACCEL_MG_LSB_16G

    @property
    def mag_gain(self):
        """Get and set the magnetometer gain.  Must be a value of:
          - MAGGAIN_4GAUSS
          - MAGGAIN_8GAUSS
          - MAGGAIN_12GAUSS
          - MAGGAIN_16GAUSS
        """
        reg = self._read_u8(_MAGTYPE, _LSM9DS1_REGISTER_CTRL_REG2_M)
        return (reg & 0b01100000) & 0xFF

    @mag_gain.setter
    def mag_gain(self, val):
        assert val in (MAGGAIN_4GAUSS, MAGGAIN_8GAUSS, MAGGAIN_12GAUSS,
                       MAGGAIN_16GAUSS)
        reg = self._read_u8(_MAGTYPE, _LSM9DS1_REGISTER_CTRL_REG2_M)
        reg = (reg & ~(0b01100000)) & 0xFF
        reg |= val
        self._write_u8(_MAGTYPE, _LSM9DS1_REGISTER_CTRL_REG2_M, reg)
        if val == _LSM9DS1_MAGGAIN_4GAUSS:
            self._mag_mgauss_lsb = _LSM9DS1_MAG_MGAUSS_4GAUSS
        elif val == _LSM9DS1_MAGGAIN_8GAUSS:
            self._mag_mgauss_lsb = _LSM9DS1_MAG_MGAUSS_8GAUSS
        elif val == _LSM9DS1_MAGGAIN_12GAUSS:
            self._mag_mgauss_lsb = _LSM9DS1_MAG_MGAUSS_12GAUSS
        elif val == _LSM9DS1_MAGGAIN_16GAUSS:
            self._mag_mgauss_lsb = _LSM9DS1_MAG_MGAUSS_16GAUSS

    @property
    def gyro_scale(self):
        """Get and set the gyroscope scale.  Must be a value of:
          - GYROSCALE_245DPS
          - GYROSCALE_500DPS
          - GYROSCALE_2000DPS
        """
        reg = self._read_u8(_XGTYPE, _LSM9DS1_REGISTER_CTRL_REG1_G)
        return (reg & 0b00110000) & 0xFF

    @gyro_scale.setter
    def gyro_scale(self, val):
        assert val in (GYROSCALE_245DPS, GYROSCALE_500DPS, GYROSCALE_2000DPS)
        reg = self._read_u8(_XGTYPE, _LSM9DS1_REGISTER_CTRL_REG1_G)
        reg = (reg & ~(0b00110000)) & 0xFF
        reg |= val
        self._write_u8(_XGTYPE, _LSM9DS1_REGISTER_CTRL_REG1_G, reg)
        if val == _LSM9DS1_GYROSCALE_245DPS:
            self._gyro_dps_digit = _LSM9DS1_GYRO_DPS_DIGIT_245DPS
        elif val == _LSM9DS1_GYROSCALE_500DPS:
            self._gyro_dps_digit = _LSM9DS1_GYRO_DPS_DIGIT_500DPS
        elif val == _LSM9DS1_GYROSCALE_2000DPS:
            self._gyro_dps_digit = _LSM9DS1_GYRO_DPS_DIGIT_2000DPS

    def read_accel_raw(self):
        """Read the raw accelerometer sensor values and return it as a
        3-tuple of X, Y, Z axis values that are 16-bit unsigned values.  If you
        want the acceleration in nice units you probably want to use the
        accelerometer property!
        """
        # Read the accelerometer
        self._read_bytes(_XGTYPE, 0x80 | LSM9DS1_REGISTER_OUT_X_L_XL, 6,
                         self._BUFFER)
        xlo = self._BUFFER[0];
        xhi = self._BUFFER[1];
        ylo = self._BUFFER[2];
        yhi = self._BUFFER[3];
        zlo = self._BUFFER[4];
        zhi = self._BUFFER[5];
        # Shift values to create properly formed integer (low byte first)
        raw_x = ((xhi << 8) | xlo) & 0xFFFF
        raw_y = ((yhi << 8) | ylo) & 0xFFFF
        raw_z = ((zhi << 8) | zlo) & 0xFFFF
        return (raw_x, raw_y, raw_z)

    @property
    def accelerometer(self):
        """Get the accelerometer X, Y, Z axis values as a 3-tuple of
        m/s^2 values.
        """
        raw = self.read_accel_raw()
        return map(lambda x: x * self._accel_mg_lsb / 1000.0 * _SENSORS_GRAVITY_STANDARD,
                   raw)

    def read_mag_raw(self):
        """Read the raw magnetometer sensor values and return it as a
        3-tuple of X, Y, Z axis values that are 16-bit unsigned values.  If you
        want the magnetometer in nice units you probably want to use the
        magnetometer property!
        """
        # Read the magnetometer
        self._read_bytes(_MAGTYPE, 0x80 | _LSM9DS1_REGISTER_OUT_X_L_M, 6,
                         self._BUFFER)
        xlo = self._BUFFER[0];
        xhi = self._BUFFER[1];
        ylo = self._BUFFER[2];
        yhi = self._BUFFER[3];
        zlo = self._BUFFER[4];
        zhi = self._BUFFER[5];
        # Shift values to create properly formed integer (low byte first)
        raw_x = ((xhi << 8) | xlo) & 0xFFFF
        raw_y = ((yhi << 8) | ylo) & 0xFFFF
        raw_z = ((zhi << 8) | zlo) & 0xFFFF
        return (raw_x, raw_y, raw_z)

    @property
    def magnetometer(self):
        """Get the magnetometer X, Y, Z axis values as a 3-tuple of
        gauss values.
        """
        raw = self.read_mag_raw()
        return map(lambda x: x * self._mag_mgauss_lsb / 1000.0, raw)

    def read_gyro_raw(self):
        """Read the raw gyroscope sensor values and return it as a
        3-tuple of X, Y, Z axis values that are 16-bit unsigned values.  If you
        want the gyroscope in nice units you probably want to use the
        gyroscope property!
        """
        # Read the gyroscope
        self._read_bytes(_XGTYPE, 0x80 | _LSM9DS1_REGISTER_OUT_X_L_G, 6,
                         self._BUFFER)
        xlo = self._BUFFER[0];
        xhi = self._BUFFER[1];
        ylo = self._BUFFER[2];
        yhi = self._BUFFER[3];
        zlo = self._BUFFER[4];
        zhi = self._BUFFER[5];
        # Shift values to create properly formed integer (low byte first)
        raw_x = ((xhi << 8) | xlo) & 0xFFFF
        raw_y = ((yhi << 8) | ylo) & 0xFFFF
        raw_z = ((zhi << 8) | zlo) & 0xFFFF
        return (raw_x, raw_y, raw_z)

    @property
    def gyroscope(self):
        """Get the gyroscope X, Y, Z axis values as a 3-tuple of
        radians/second values.
        """
        raw = self.read_mag_raw()
        return map(lambda x: x * self._gyro_dps_digit, raw)

    def read_temp_raw(self):
        """Read the raw temperature sensor value and return it as a 16-bit
        unsigned value.  If you want the temperature in nice units you probably
        want to use the temperature property!
        """
        # Read temp sensor
        self._read_bytes(_XGTYPE, 0x80 | LSM9DS1_REGISTER_TEMP_OUT_L, 2,
                         self._BUFFER)
        temp = (self._BUFFER[1] << 8) | self._BUFFER[0]
        return temp

    @property
    def temperature(self):
        """Get the temperature of the sensor in degrees Celsius."""
        # This is just a guess since the starting point (21C here) isn't documented :(
        temp = self.read_temp_raw()
        temp = 21.0 + temp/8
        return temp

    def _read_u8(self, sensor_type, address):
        # Read an 8-bit unsigned value from the specified 8-bit address.
        # The sensor_type boolean should be _MAGTYPE when talking to the
        # magnetometer, or _XGTYPE when talking to the accel or gyro.
        # MUST be implemented by subclasses!
        raise NotImplementedError()

    def _read_bytes(self, sensor_type, address, count, buffer):
        # Read a count number of bytes into buffer from the provided 8-bit
        # register address.  The sensor_type boolean should be _MAGTYPE when
        # talking to the magnetometer, or _XGTYPE when talking to the accel or
        # gyro.  MUST be implemented by subclasses!
        raise NotImplementedError()

    def _write_u8(self, sensor_type, address, val):
        # Write an 8-bit unsigned value to the specified 8-bit address.
        # The sensor_type boolean should be _MAGTYPE when talking to the
        # magnetometer, or _XGTYPE when talking to the accel or gyro.
        # MUST be implemented by subclasses!
        raise NotImplementedError()


class LSM9DS1_I2C(LSM9DS1):

    def __init__(self, i2c):
        self._mag_device = i2c_device.I2CDevice(i2c, _LSM9DS1_ADDRESS_MAG)
        self._xg_device  = i2c_device.I2CDevice(i2c, _LSM9DS1_ADDRESS_ACCELGYRO)
        super().__init__()

    def _read_u8(self, sensor_type, address):
        if sensor_type == _MAGTYPE:
            device = self._mag_device
        else:
            device = self._xg_device
        with device:
            self._BUFFER[0] = address & 0xFF
            device.write(self._BUFFER, end=1)
            device.readinto(self._BUFFER, end=1)
        return self._BUFFER[0]

    def _read_bytes(self, sensor_type, address, count, buffer):
        if sensor_type == _MAGTYPE:
            device = self._mag_device
        else:
            device = self._xg_device
        with device:
            self._BUFFER[0] = address & 0xFF
            device.write(self._BUFFER, end=1)
            device.readinto(self._BUFFER, end=count)

    def _write_u8(self, sensor_type, address, val):
        if sensor_type == _MAGTYPE:
            device = self._mag_device
        else:
            device = self._xg_device
        with device:
            self._BUFFER[0] = address & 0xFF
            self._BUFFER[1] = val & 0xFF
            device.write(self._BUFFER, end=2)


class LSM9DS1_SPI(LSM9DS1):

    def __init__(self, spi, xgcs, mcs):
        self._mag_device = spi_device.I2CDevice(spi, mcs)
        self._xg_device  = spi_device.I2CDevice(spi, xgcs)
        super().__init__()

    def _read_u8(self, sensor_type, address):
        if sensor_type == _MAGTYPE:
            device = self._mag_device
        else:
            device = self._xg_device
        with device:
            device.configure(baudrate=200000, phase=0, polarity=0)
            self._BUFFER[0] = (address | 0x80) & 0xFF
            device.write(self._BUFFER, end=1)
            device.readinto(self._BUFFER, end=1)
        return self._BUFFER[0]

    def _read_bytes(self, sensor_type, address, count, buffer):
        if sensor_type == _MAGTYPE:
            device = self._mag_device
        else:
            device = self._xg_device
        with device:
            device.configure(baudrate=200000, phase=0, polarity=0)
            self._BUFFER[0] = (address | 0x80) & 0xFF
            device.write(self._BUFFER, end=1)
            device.readinto(self._BUFFER, end=count)

    def _write_u8(self, sensor_type, address, val):
        if sensor_type == _MAGTYPE:
            device = self._mag_device
        else:
            device = self._xg_device
        with device:
            device.configure(baudrate=200000, phase=0, polarity=0)
            self._BUFFER[0] = (address & 0x7F) & 0xFF
            self._BUFFER[1] = val & 0xFF
            device.write(self._BUFFER, end=2)