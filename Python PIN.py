import cv2, numpy as np, mediapipe as mp, subprocess, requests, time
import webbrowser

# The Correct Pin Password
CORRECT_PIN = "12345"
input_pin = ""
pin_state = [0]*5

# Virtual Buttons
buttons = {
    '1':(50,150),'2':(130,150),'3':(210,150),
    '4':(50,230),'5':(130,230),'6':(210,230),
    '7':(50,310),'8':(130,310),'9':(210,310),
    'DEL':(50,390),'0':(130,390),'ENT':(210,390)
}

# Mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
FINGER_TIP = mp_hands.HandLandmark.INDEX_FINGER_TIP

hover = False

# IP ESP32 LED
LED_IP = "http://192.168.137.150"
LED_NAMES = ["thumb","index","middle","ring","pinky"]

def led_pin_on(i):
    try: requests.get(f"{LED_IP}/led/{LED_NAMES[i]}/on", timeout=0.2)
    except: pass

def led_pin_off(i):
    try: requests.get(f"{LED_IP}/led/{LED_NAMES[i]}/off", timeout=0.2)
    except: pass

def blink_leds(color: str, times=3, delay=0.2):
    path = "/on" if color == "green" else "/on"
    off_path = "/off"
    for _ in range(times):
        for i in range(5):
            try:
                req_path = f"{LED_IP}/led/{LED_NAMES[i]}{path if color == 'green' else '/on'}"
                requests.get(req_path, timeout=0.2)
            except: pass
        time.sleep(delay)
        for i in range(5):
            try:
                requests.get(f"{LED_IP}/led/{LED_NAMES[i]}/off", timeout=0.2)
            except: pass
        time.sleep(delay)

def handle_click(key):
    global input_pin, pin_state
    if key == "DEL":
        input_pin = ""
        pin_state = [0]*5
        for i in range(5): led_pin_off(i)

    elif key == "ENT":
        if input_pin == CORRECT_PIN:
            pin_state = [2]*5
            blink_leds("green", 3)
            webbrowser.open("https://www.youtube.com/watch?v=cJz6Oqm4UoY&list=RDcJz6Oqm4UoY&start_radio=1&ab_channel=CarlRendar")
            webbrowser.open("https://www.youtube.com/watch?v=2mnBRZNAA_0&ab_channel=ArchivedHDR")
        else:
            pin_state = [3]*5
            blink_leds("red", 3)
        input_pin = ""
        pin_state = [0]*5
        for i in range(5): led_pin_off(i)

    elif key.isdigit() and len(input_pin) < 5:
        input_pin += key
        idx = len(input_pin)-1
        pin_state[idx] = 1
        led_pin_on(idx)


def draw_ui(frame):
    # PIN underline & number
    for i in range(5):
        col=(200,200,200)
        if pin_state[i]==1: col=(0,0,255)
        elif pin_state[i]==2: col=(0,255,0)
        elif pin_state[i]==3: col=(0,0,255)
        xs=70+i*70
        cv2.line(frame,(xs,80),(xs+40,80),col,5)
        if i<len(input_pin):
            cv2.putText(frame,input_pin[i],(xs+5,70),cv2.FONT_HERSHEY_SIMPLEX,1,col,2)
    # Virtual Button
    for k,(x,y) in buttons.items():
        cv2.rectangle(frame,(x,y),(x+60,y+60),(50,50,50),-1)
        cv2.putText(frame,k,(x+10,y+40),cv2.FONT_HERSHEY_SIMPLEX,1.2,(255,255,255),2)

cap = cv2.VideoCapture("http://192.168.1.6:4747/video")
if not cap.isOpened(): raise Exception("Failed To Open Camera")

print("▶ Gesture PIN active")
while True:
    ret,frame = cap.read()
    if not ret: break
    frame=cv2.flip(frame,1)
    h,w,_=frame.shape
    rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    res=hands.process(rgb)
    draw_ui(frame)

    if res.multi_hand_landmarks:
        lm=res.multi_hand_landmarks[0].landmark[FINGER_TIP]
        cx,cy=int(lm.x*w),int(lm.y*h)
        cv2.circle(frame,(cx,cy),10,(0,0,255),-1)
        for k,(x,y) in buttons.items():
            if x<cx<x+60 and y<cy<y+60:
                if not hover:
                    hover=True; handle_click(k)
                break
        else: hover=False

    cv2.imshow("Gesture PIN Input", cv2.resize(frame, (1080, 720)))
    if cv2.waitKey(5)&0xFF==27: break

cap.release()
cv2.destroyAllWindows()
