import numpy as np

def calcular_angulo(a, b, c):
    """ Calcula o ângulo em graus entre três pontos (x, y) """
    a = np.array(a) # Primeiro ponto
    b = np.array(b) # Ponto médio
    c = np.array(c) # Ponto final
    
    radianos = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angulo = np.abs(radianos * 180.0 / np.pi)
    
    if angulo > 180.0:
        angulo = 360 - angulo
        
    return angulo

def calcular_angulo_joelho(ponto_quadril, ponto_joelho, ponto_tornozelo):
    """ Calcula o ângulo de flexão do joelho """
    a = np.array(ponto_quadril)   
    b = np.array(ponto_joelho)    
    c = np.array(ponto_tornozelo) 
    
    radianos = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angulo = np.abs(radianos * 180.0 / np.pi)
    
    if angulo > 180.0:
        angulo = 360 - angulo
        
    return angulo