#Import modules
import time
import cv2
import math
import numpy as np

def detect_shapes(img):
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edge = cv2.Canny(blur, 40, 170)
    
    #Find contours in the edged image
    contours, _ = cv2.findContours(edge.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    #Loop over our contours
    for cnt in contours:
        #Calculate the area of the contour
        area = cv2.contourArea(cnt)
        
        # Only proceed if the area meets the minimum threshold
        if 100 <= area <= 25000:
            # Approximate the contour
            epsilon = 0.01 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
            
            shape_name = "Unknown"
            
            # Basic shape detection
            if len(approx) == 3:
                shape_name = "Triangle"
            elif len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspectRatio = float(w)/h
                if aspectRatio >= 0.95 and aspectRatio <= 1.05:
                    shape_name = "Square"
                else:
                    shape_name = "Rectangle"
            elif len(approx) == 5:
                shape_name = "Pentagon"
            elif len(approx) == 6:
                shape_name = "Hexagon"
            else:
                perimeter = cv2.arcLength(cnt, True)
                radius = perimeter/(2*math.pi)
                circle_area = math.pi * (radius ** 2)
                area_ratio = area/circle_area if circle_area > 0 else 0
            
                if 0.85 <= area_ratio <= 1.1:
                    shape_name = "Circle"
               
            # Drawing the shape name and contour
            cv2.drawContours(img, [cnt], -1, (0, 255, 0), 2)
            cv2.putText(img, shape_name, (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    return img, gray, blur, edge

def display(frame, gray, blur, edge):
    gray_3ch = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    blur_3ch = cv2.cvtColor(blur, cv2.COLOR_GRAY2BGR)
    edge_3ch = cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)
    combined = np.hstack([frame, gray_3ch, blur_3ch, edge_3ch])
    cv2.imshow('Original | Grayscale | Blurred | Edge', combined)
    
# Start capturing video from the webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    #Resize the frame
    frame_resized = cv2.resize(frame, (384,288))
    
    new_frame, gray, blur, edge = detect_shapes(frame_resized)
    display(new_frame, gray, blur, edge)
    
    if cv2.waitKey(1) & 0xFF == ord('p'):
        break
    
# Release the capture and destroy all windows when done
cap.release()
cv2.destroyAllWindows()
