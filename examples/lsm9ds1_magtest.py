# Simple demo of the LSM9DS1 accelerometer, magnetometer, gyroscope.
# Will print the acceleration, magnetometer, and gyroscope values every second.
import time
import board
import busio
import adafruit_lsm9ds1

# I2C connection:
i2c = busio.I2C(board.SCL, board.SDA)

sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c, 0x1C, 0x6A)
# set mag to 1000hz sampling
#sensor.set_property_mag(adafruit_lsm9ds1._LSM9DS1_REGISTER_CTRL_REG1_M, 0b10)
# Main loop will read the magnetometer
# values every second and print them out.
while True:
    # Read magnetometer.
    mag_x, mag_y, mag_z = sensor.magnetic
    # Print values.
    print(
        "Magnetometer (gauss): ({0:0.3f},{1:0.3f},{2:0.3f})".format(mag_x, mag_y, mag_z)
    )
    # Delay for a 1/1000 second.
    # time.sleep(0.001)
