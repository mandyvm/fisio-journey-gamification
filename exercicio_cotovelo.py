import cv2
import mediapipe as mp
import numpy as np
import socket
from utils.calculos import calcular_angulo

# Configuração da Rede (UDP)
UDP_IP = "127.0.0.1" 
UDP_PORT = 5052
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

# Configuração do MediaPipe
mp_desenho = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
cap = cv2.VideoCapture(0)

contador = 0 
estagio = None

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        imagem = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagem.flags.writeable = False 
        resultados = pose.process(imagem)
        imagem.flags.writeable = True
        imagem = cv2.cvtColor(imagem, cv2.COLOR_RGB2BGR)
        
        try:
            landmarks = resultados.pose_landmarks.landmark
            ombro = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            cotovelo = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            punho = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            
            angulo = calcular_angulo(ombro, cotovelo, punho)
            
            # Transmissão UDP para a Unity
            mensagem = str(round(angulo, 2))
            sock.sendto(mensagem.encode(), (UDP_IP, UDP_PORT))
            
            cv2.putText(imagem, str(int(angulo)), tuple(np.multiply(cotovelo, [640, 480]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            
            if angulo > 160: estagio = "desce"
            if angulo < 30 and estagio == 'desce':
                estagio = "sobe"
                contador += 1
                       
        except:
            pass 
        
        # Interface Visual
        cv2.rectangle(imagem, (0,0), (225,73), (245,117,16), -1)
        cv2.putText(imagem, 'REPETICOES', (15,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(imagem, str(contador), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(imagem, 'ESTAGIO', (130,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(imagem, str(estagio), (125,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        mp_desenho.draw_landmarks(imagem, resultados.pose_landmarks, mp_pose.POSE_CONNECTIONS, mp_desenho.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), mp_desenho.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))               
        
        cv2.imshow('FisioPlay - Cotovelo', imagem)
        if cv2.waitKey(10) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()