import RPi.GPIO as GPIO
import time

# Define GPIO pins for controls
in1 = 38
in2 = 36
in3 = 37
in4 = 35
enA = 40
enB = 33
tachoL = 29
tachoR = 31

# Set GPIO mode and warnings
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Set up motor pins
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
GPIO.setup(enA, GPIO.OUT)
GPIO.setup(enB, GPIO.OUT)
l_speed = 40
r_speed = 40
r_pulse = GPIO.PWM(enA, 1500)
l_pulse = GPIO.PWM(enB, 1500)
r_pulse.start(r_speed)
l_pulse.start(l_speed)

# Set up encoder pins and variables
GPIO.setup(tachoL, GPIO.IN)
GPIO.setup(tachoR, GPIO.IN)
tachoL_counter = 0
tachoR_counter = 0
total_distance = 0
disk_diameter = 0.0255
pulses_per_revolution = 20
prev_time = time.time()

#Function to handle tachometer interrupts
def tacho_callback(channel):
    global tachoL_counter, tachoR_counter
    if channel == tachoL:
        tachoL_counter += 1
    elif channel == tachoR:
        tachoR_counter += 1

# Add event detection for tachometer pulses
GPIO.add_event_detect(tachoL, GPIO.RISING, callback=tacho_callback)
GPIO.add_event_detect(tachoR, GPIO.RISING, callback=tacho_callback)

#Function to calculate the speed and distance travelled
def calculate_speed_distance():
    global tachoL_counter, tachoR_counter, prev_time, total_distance
    
    current_time = time.time()
    time_diff = current_time - prev_time
    
    if time_diff >= 0.001:  # Calculate speed every 0.01 second
        # Calculate speed
        speedL = tachoL_counter / time_diff  # Speed for tachometer 1 (in pulses per second)
        speedR = tachoR_counter / time_diff  # Speed for tachometer 2 (in pulses per second)
        round_speedL=round(speedL,4)
        round_speedR=round(speedR,4)
        print("Left speed:", round_speedL * (disk_diameter * 3.14) / pulses_per_revolution, "m/s")
        print("Right speed:", round_speedR * (disk_diameter * 3.14) / pulses_per_revolution, "m/s")
        
        # Calculate distance traveled
        distanceL = (tachoL_counter / pulses_per_revolution) * (disk_diameter * 3.14)  # Distance for tachometer 1 (in m)
        distanceR = (tachoR_counter / pulses_per_revolution) * (disk_diameter * 3.14)  # Distance for tachometer 2 (in m)
        total_distance +=1.339/2*(distanceL + distanceR)  # Average distance of both wheels
        round_total_distance=round(total_distance,4)
        print("Total distance traveled:", round_total_distance, "m")
        
        # Reset counters and update time
        tachoL_counter = 0
        tachoR_counter = 0
        prev_time = current_time

#Function to set speed
def set_speed(speed_percent):
    if speed_percent < 0 or speed_percent > 100:
        raise ValueError("Speed percentage should be between 0 and 100")
    r_pulse.ChangeDutyCycle(speed_percent)
    l_pulse.ChangeDutyCycle(speed_percent)

# Function to move forward
def forward():
    print("Forward, here we go!")
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)

# Function to move backwards
def reverse():
    print("Reverse")
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.HIGH)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.HIGH)

# Function to turn left
def turn_left():
    print("Left")
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.HIGH)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
    r_pulse.ChangeDutyCycle(100)
    l_pulse.ChangeDutyCycle(100)
    
# Function to turn right
def turn_right():
    print("Right")
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.HIGH)
    r_pulse.ChangeDutyCycle(100)
    l_pulse.ChangeDutyCycle(100)
    
# Function to stop
def stop():
    print("Stop!")
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.LOW)
    r_pulse.ChangeDutyCycle(100)
    l_pulse.ChangeDutyCycle(100)


# Main working environment
try:
    while True:
        action = input("Enter your command:")
        if action == "w":
            forward()
        elif action == "a":
            turn_left()
        elif action == "s":
            reverse()
        elif action == "d":
            turn_right()
        elif action == "q":
            stop()
        elif action == "x":
            calculate_speed_distance()
        elif action == "0":
            set_speed(40)
        elif action == "1":
            set_speed(60)
        elif action == "2":
            set_speed(80)
        elif action == "3":
            set_speed(100)
        elif action == "45d":
            turn_right()
            time.sleep(0.27)
            stop()
        elif action == "60d":
            turn_right()
            time.sleep(0.35)
            stop()
        elif action == "90d":
            turn_left()
            time.sleep(0.51)
            stop()
     
except KeyboardInterrupt:
    pass

finally:
    GPIO.output(enA, GPIO.LOW)
    GPIO.output(enB, GPIO.LOW)
    GPIO.cleanup()  # Clean up GPIO pins
