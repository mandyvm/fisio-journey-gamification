import cv2
import mediapipe as mp
import socket

# --- Configuração da Rede (UDP) ---
UDP_IP = "127.0.0.1" 
UDP_PORT = 5052
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

# --- Configuração do MediaPipe ---
mp_desenho = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
cap = cv2.VideoCapture(0)

print("Iniciando captura de corpo inteiro (Mocap) para a Unity...")
print("Pressione 'q' na janela do vídeo para sair.")

# model_complexity=1 garante um bom equilíbrio entre velocidade e precisão no 3D
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=1) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        # Converte a imagem para o MediaPipe ler
        imagem = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagem.flags.writeable = False 
        resultados = pose.process(imagem)
        imagem.flags.writeable = True
        imagem = cv2.cvtColor(imagem, cv2.COLOR_RGB2BGR)
        
        # Se encontrou o corpo do paciente
        if resultados.pose_world_landmarks:
            # Atenção: Estamos usando WORLD landmarks (Coordenadas 3D reais)
            landmarks = resultados.pose_world_landmarks.landmark
            
            # Vamos empacotar os 33 pontos do corpo em uma única mensagem de texto!
            lista_dados = []
            for lm in landmarks:
                # O MediaPipe tem o eixo Y invertido em relação à Unity. 
                # Colocamos um sinal de menos (-) no Y para consertar isso direto na origem.
                # Formato final de cada ponto: X,Y,Z
                lista_dados.append(f"{lm.x},{-lm.y},{lm.z}")
            
            # Junta todos os 33 pontos separando-os por um " | " (pipe)
            # A mensagem final vai ficar enorme, tipo: "x,y,z|x,y,z|x,y,z..."
            mensagem = "|".join(lista_dados)
            
            # Envia o pacotão 3D pela rede para a Unity!
            sock.sendto(mensagem.encode(), (UDP_IP, UDP_PORT))
            
            # --- Interface Visual ---
            # Desenha o esqueleto 2D na tela do vídeo para o paciente ver que está sendo rastreado
            mp_desenho.draw_landmarks(
                imagem, 
                resultados.pose_landmarks, 
                mp_pose.POSE_CONNECTIONS, 
                mp_desenho.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                mp_desenho.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
            )               
        
        # Mostra a tela
        cv2.imshow('FisioPlay - Captura Mocap', imagem)
        
        if cv2.waitKey(10) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()