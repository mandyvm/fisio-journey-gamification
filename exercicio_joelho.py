import cv2
import mediapipe as mp
import numpy as np
import os
from utils.calculos import calcular_angulo_joelho

PASTA_DESTINO = "evidencias_tcc_com_landmarks"
if not os.path.exists(PASTA_DESTINO):
    os.makedirs(PASTA_DESTINO)

mp_desenho = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
cap = cv2.VideoCapture(0)

contador = 0 
estagio = "NEUTRO" 
total_prints = 0
tirou_repouso = False
tirou_extensao = False
ultimo_contador = 0

print(f"--- INICIANDO CAPTURA PARA TCC ---")

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        imagem = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagem.flags.writeable = False
        resultados = pose.process(imagem)
        imagem.flags.writeable = True
        imagem = cv2.cvtColor(imagem, cv2.COLOR_RGB2BGR)
        
        salvar_agora = False
        nome_arquivo = ""
        
        try:
            landmarks = resultados.pose_landmarks.landmark
            quadril = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            joelho = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            tornozelo = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            
            angulo = calcular_angulo_joelho(quadril, joelho, tornozelo)
            
            if angulo < 100:
                estagio = "DESCE"
                if not tirou_repouso:
                    salvar_agora, nome_arquivo, tirou_repouso = True, "1_Posicao_Inicial_DESCE", True
            
            if angulo > 150 and estagio == "DESCE":
                estagio = "SOBE"
                contador += 1
                if not tirou_extensao:
                    salvar_agora, nome_arquivo, tirou_extensao = True, "2_Extensao_Maxima_SOBE", True
            
            if contador > ultimo_contador and total_prints < 4 and not salvar_agora:
                salvar_agora, nome_arquivo, ultimo_contador = True, f"3_Repeticao_{contador}_Completa", contador

        except:
            pass
        
        mp_desenho.draw_landmarks(imagem, resultados.pose_landmarks, mp_pose.POSE_CONNECTIONS, mp_desenho.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), mp_desenho.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))
        cv2.rectangle(imagem, (0,0), (225,73), (245,117,16), -1)
        cv2.putText(imagem, 'REPS', (15,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(imagem, str(contador), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(imagem, 'ESTAGIO', (130,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(imagem, estagio, (100,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        
        if 'joelho' in locals():
            cv2.putText(imagem, str(int(angulo)), tuple(np.multiply(joelho, [640, 480]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        if salvar_agora and total_prints < 4:
            cv2.imwrite(f"{PASTA_DESTINO}/{nome_arquivo}.png", imagem)
            print(f"📸 PRINT SALVO: {nome_arquivo}")
            total_prints += 1
            if total_prints >= 4: print("--- 4 PRINTS REALIZADOS. PODE FECHAR ---")
        
        cv2.imshow('FisioPlay - Joelho (Coleta)', imagem)
        if cv2.waitKey(10) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()