# Simple demo of the LSM9DS1 accelerometer, magnetometer, gyroscope.
# Will print the acceleration, magnetometer, and gyroscope values every second.
import time
import board
import busio
import adafruit_lsm9ds1
import threading

def get_time():
	return int(round(time.time() * 10000))

waiting_time = 0.003

# I2C connection:
i2c = busio.I2C(board.SCL, board.SDA)

sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c, 0x1C, 0x6A)
# set mag to 1000hz sampling
sensor.set_property_mag(adafruit_lsm9ds1._LSM9DS1_REGISTER_CTRL_REG1_M, 0b10)
# Main loop will read the magnetometer
# values every second and print them out.
while True:
	t = threading.Thread(target=time.sleep, args=(waiting_time-0.001,))
	t.start()

	# Read magnetometer.
	mag_x, mag_y, mag_z = sensor.magnetic

	t.join()

	# Print values.
	print(
		"{0:10d} Magnetometer (gauss): ({1:0.3f},{2:0.3f},{3:0.3f})".format(get_time(),mag_x, mag_y, mag_z)
	)