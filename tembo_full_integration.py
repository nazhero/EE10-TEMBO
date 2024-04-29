#Import modules
import cv2
import numpy as np
import math
import time
import RPi.GPIO as GPIO

# Define GPIO pins for controls
in1 = 38
in2 = 36
in3 = 37
in4 = 35
enA = 40
enB = 33

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
l_pulse = GPIO.PWM(enA, 400)
r_pulse = GPIO.PWM(enB, 400)
r_pulse.start(40)
l_pulse.start(40)

# Start video stream
cap = cv2.VideoCapture(0)
cap.set(3, 320)
cap.set(4, 100)

# Function to move forward
def forward(speed):
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.HIGH)
    r_pulse.ChangeDutyCycle(speed)
    l_pulse.ChangeDutyCycle(speed)

 # Function to move backwards
def reverse(speed):
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.HIGH)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
    r_pulse.ChangeDutyCycle(speed)
    l_pulse.ChangeDutyCycle(speed)
    
# Function to turn left
def turn_left(speed):
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
    r_pulse.ChangeDutyCycle(speed)
    l_pulse.ChangeDutyCycle(speed)
    
# Function to turn right
def turn_right(speed):
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.HIGH)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.HIGH)
    r_pulse.ChangeDutyCycle(speed)
    l_pulse.ChangeDutyCycle(speed)
    
# Function to stop
def stop():
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.LOW)
    r_pulse.ChangeDutyCycle(40)
    l_pulse.ChangeDutyCycle(40)

def image_processing(img):
    # Image Processing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    edge = cv2.Canny(blur, 40, 170)
    
    return gray, blur, hsv, edge

def detect_line(img, hsv):
    # Black Mask
    lower_black = np.uint8([0,0,0])
    upper_black = np.uint8([70,70,60])
    mask_black = cv2.inRange(img, lower_black, upper_black)
    # Yellow Mask
    lower_yellow = np.uint8([20,100,100])
    upper_yellow = np.uint8([40,255,255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    # Red Mask
    lower_red = np.uint8([160,50,70])
    upper_red = np.uint8([180,255,255])
    mask_red = cv2.inRange(hsv, lower_red, upper_red)
    # Blue Mask
    lower_blue = np.uint8([100,75,2])
    upper_blue = np.uint8([100,255,255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    # Green Mask
    lower_green = np.uint8([48,170,60])
    upper_green = np.uint8([90,255,255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    
    def process_contours(mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= 100]
        
        return filtered_contours

    # Process each mask
    y_contours = process_contours(mask_yellow)
    b_contours = process_contours(mask_blue)
    k_contours = process_contours(mask_black)
    
    if len(y_contours) > 0:
        cnt = max(y_contours, key = cv2.contourArea)
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            print("cX: "+str(cX)+"cY:"+str(cY))
            if cX >= 180:
                print("Turn Right")
                turn_right(40)
            if cX < 180 and cX > 90:
                print("Stable")
                forward(40)
            if cX <= 90:
                print("Turn Left")
                turn_left(40)
            cv2.circle(img, (cX, cY), 5, (255, 0, 255), -1)
            cv2.putText(img, "yellow", (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (185, 218, 255), 2)
        cv2.drawContours(img, y_contours, -1, (255, 0, 0), 1)
                                                                                                                                                                                                                   
    elif len(b_contours) > 0:
        cnt = max(b_contours, key = cv2.contourArea)
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            print("cX: "+str(cX)+"cY:"+str(cY))
            if cX >= 200:
                print("Turn Right")
                turn_right(40)
            if cX < 200 and cX > 100:
                print("Stable")
                forward(30)
            if cX <= 100:
                print("Turn Left")
                turn_left(40)
            cv2.circle(img, (cX, cY), 5, (255, 0, 255), -1)
            cv2.putText(img, "blue", (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (185, 218, 255), 2)
        cv2.drawContours(img, b_contours, -1, (255, 0, 0), 1)
    
    elif len(k_contours) > 0:
        cnt = max(k_contours, key = cv2.contourArea)
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            print("cX: "+str(cX)+"cY:"+str(cY))
            if cX >= 180:
                print("Turn Right")
                turn_right(40)
            if cX < 180 and cX > 90:
                print("Stable")
                forward(30)
            if cX <= 90:
                print("Turn Left")
                turn_left(40)
            cv2.circle(img, (cX, cY), 5, (255, 255, 255), -1)
            cv2.putText(img, "black", (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (185, 218, 255), 2)
        cv2.drawContours(img, k_contours, -1, (0, 255, 0), 1)
    else:
        print("No Line Detected")
        reverse(40)
        time.sleep(0.3)
        turn_left(50)
        time.sleep(0.1)
    return img, mask_black, mask_yellow, mask_blue,

def detect_shapes(img):
    
    #Find contours in the edged image
    contours, _ = cv2.findContours(edge.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    #Loop over our contours
    for cnt in contours:
        #Calculate the area of the contour
        area = cv2.contourArea(cnt)
        
        # Only proceed if the area meets the minimum threshold
        if area >= 2000:
            # Approximate the contour
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
            
            shape_name = "Unknown"
            
            if len(approx) == 3:
                shape_name = "Triangle"
                print("Triangle")
            elif len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspectRatio = float(w)/h
                if aspectRatio >= 0.95 and aspectRatio <= 1.05:
                    shape_name = "Square"
                    print("Square")
                else:
                    shape_name = "Rectangle"
                    print("Rectangle")
            elif len(approx) == 5:
                shape_name = "Pentagon"
                print("Pentagon")
            elif len(approx) == 6:
                shape_name = "Hexagon"
                print("Hexagon")
            elif len(approx) == 7:
                base = max(approx, key = lambda p: ((cX - p[0][0])**2 + (cY - p[0][1])**2)**0.5)
                tip = min(approx, key = lambda p: ((cX - p[0][0])**2 + (cY - p[0][1])**2)**0.5)
                shape_name = "Possible Arrow"
                dX = base[0][0] - tip[0][0]
                dY = base[0][1] - tip[0][1]
                if abs(dX) > abs(dY):
                    if dX > 0:
                        shape_name = "Left Arrow"
                        print("Left Arrow")
                    else:
                        shape_name = "Right Arrow"
                        print("Right Arrow")
                else:
                    if dY > 0:
                        shape_name = "Down Arrow"
                        print("Down Arrow")
                    else:
                        shape_name = "Up Arrow"
                        print("Up Arrow")
            else:
                perimeter = cv2.arcLength(cnt, True)
                radius = perimeter/(2*math.pi)
                circle_area = math.pi * (radius ** 2)
                area_ratio = area/circle_area if circle_area > 0 else 0
                if 0.85 <= area_ratio <= 1.1:
                    shape_name = "Circle"
                    print("Circle")
                elif 0.55 <= area_ratio <= 0.65:
                    shape_name = "Partial circle"
                    print("Partial circle")
            
            # Drawing the shape name and contour
            cv2.drawContours(img, [cnt], -1, (0, 255, 0), 2)
            cv2.putText(img, shape_name, (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (185, 218, 255), 2)

    return img

def display_interface(frame_line, frame_contour, edge, mask_black, mask_yellow, mask_blue):
    edge_3ch = cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)
    mask_black_3ch = cv2.cvtColor(mask_black, cv2.COLOR_GRAY2BGR)
    mask_yellow_3ch = cv2.cvtColor(mask_yellow, cv2.COLOR_GRAY2BGR)
    mask_blue_3ch = cv2.cvtColor(mask_blue, cv2.COLOR_GRAY2BGR)
    h1_combined = np.hstack([frame_line, frame_contour, edge_3ch])
    h2_combined = np.hstack([mask_black_3ch, mask_yellow_3ch, mask_blue_3ch])
    all_combined = np.vstack([h1_combined, h2_combined])
    cv2.imshow("Line | Contour | Gray | HSV | Edge | Masks (K, Y, R, B, G)", all_combined)
                         
while True:
    ret, frame_line = cap.read()
    _, frame_contour = cap.read()
    if not ret:
        break
    
    gray, blur, hsv, edge = image_processing(frame_line)
    frame_line, mask_black, mask_yellow, mask_blue = detect_line(frame_line, hsv)
    frame_contour = detect_shapes(frame_contour)
    display_interface(frame_line, frame_contour, edge, mask_black, mask_yellow, mask_blue)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
# Release the capture and destroy all windows when done
cap.release()
cv2.destroyAllWindows()
stop() 
