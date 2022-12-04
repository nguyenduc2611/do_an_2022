import cv2
import RPi.GPIO as GPIO
import time 
import imutils

import numpy as np
import requests
import json
import pytesseract
from PIL import Image
rel = 0
rel1 = 0
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(12,GPIO.OUT)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.remove_event_detect(22)
GPIO.remove_event_detect(23)
print('current value of pin', 22, 'is', GPIO.input(22))
print('current value of pin', 23, 'is', GPIO.input(23))

def cap_picture(id_servo):
    
	global rel
	global rel1
	cap.release()

	img = cv2.imread('anh_ngon.jpg',cv2.IMREAD_COLOR)


	img = cv2.resize(img, (620,480) )

	img = cv2.rotate(img, cv2.ROTATE_180)

	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to grey scale

	gray = cv2.bilateralFilter(gray, 11, 17, 17) #Blur to reduce noise

	edged = cv2.Canny(gray, 30, 200) #Perform Edge detection


	# find contours in the edged image, keep only the largest

	# ones, and initialize our screen contour

	cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	cnts = imutils.grab_contours(cnts)

	cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]

	screenCnt = None


	# loop over our contours

	for c in cnts:

 	# approximate the contour

 		peri = cv2.arcLength(c, True)

 		approx = cv2.approxPolyDP(c, 0.018 * peri, True)

 

 	# if our approximated contour has four points, then

 	# we can assume that we have found our screen

 		if len(approx) == 4:

  			screenCnt = approx

  			break


 


	if screenCnt is None:

 		detected = 0

 		print ("No contour detected")
 		cv2.destroyAllWindows()

	else:

 		detected = 1
 		if id_servo == 0:
 			rel1 = 1
 		else:
 			rel = 1


	if detected == 1:

 		cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)


	# Masking the part other than the number plate

	if detected == 1:
		mask = np.zeros(gray.shape,np.uint8)

		new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)

		new_image = cv2.bitwise_and(img,img,mask=mask)


	# Now crop

		(x, y) = np.where(mask == 255)

		(topx, topy) = (np.min(x), np.min(y))

		(bottomx, bottomy) = (np.max(x), np.max(y))

		Cropped = gray[topx:bottomx+1, topy:bottomy+1]


 


	#Read the number plate

		text = pytesseract.image_to_string(Cropped, config='--psm 11')

		print("Detected Number is:",text)
		print(" "+text)
		if(len(text) > 6):
			index_end = text.find('.', 0, len(text))
			
			if index_end > 0:
				palte = text[index_end-3]+text[index_end-2]+text[index_end-1]+text[index_end+1]+text[index_end+2]
				get_response = requests.get(url='http://103.226.250.98:8080/api/requests?licensePlates='+palte+'&restaurantId=1234')
				data = get_response.json()
				print(palte+'hello')
				print((data['status']))
				print(rel)
				print(" "+text)
				if data['status'] == 'OK':
					if(id_servo == 1):
						servo = GPIO.PWM(17, 50)
					else:
						servo = GPIO.PWM(12, 50)
				
					servo.start(0)
					time.sleep(1)
				
					servo.ChangeDutyCycle(6)
					time.sleep(1)
					if(id_servo == 1):
						servo.ChangeDutyCycle(3)
					else:
						servo.ChangeDutyCycle(2)
					time.sleep(10)
					servo.ChangeDutyCycle(6)
					time.sleep(1)
			#duty = 2
			#while duty <= 17:
				#servo.ChangeDutyCycle(duty)
				#time.sleep(1)
				#duty = duty + 1
					servo.stop()
			cv2.destroyAllWindows()

		cv2.destroyAllWindows()
	
while True:
	ir1 = GPIO.input(22)
	ir2 = GPIO.input(23)
	count1 = 0
	count = 0
	if ir1 == 1:
		
		print('current value of pin', 22, 'is', GPIO.input(22))
		cap = cv2.VideoCapture(0)
		if not cap.isOpened():
			print("Unable ")
		ret, frame = cap.read()
		cv2.imwrite('anh_ngon.jpg', frame)
		cap_picture(0)
		
	if ir2 == 1:
		print('current value of pin', 23, 'is', GPIO.input(23))
		cap = cv2.VideoCapture(2)
		if not cap.isOpened():
			print("Unable ")
		ret, frame = cap.read()
		cv2.imwrite('anh_ngon.jpg', frame)
		cap_picture(1)
	


