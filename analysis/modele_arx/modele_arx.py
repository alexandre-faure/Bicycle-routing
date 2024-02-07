'''
Ce module contient les fonctions qui permettent de tester et de paramétrer un modèle ARX
'''

import numpy as np
from scipy.optimize import minimize
from code_thomas import thomas
import json
from os import listdir
import matplotlib.pyplot as plt

#Ajout trace de référence
track_ref = 'data/JSON/originals_mm_full_truncated/02_juil._08h06_-_08h23_0.json'


#récupération des traces 
donnees=[]
for track in listdir('data/JSON/originals_mm_full_truncated/'):
    donnees.append('data/JSON/originals_mm_full_truncated/'+ track)

# Construction des données à partir du modèle
def arx_model(y_obs,u , a1, a2, a3, b0, b1, e):
    ''' ENTREE : y_obs (matrice des observations des vitesses),
                u (matrices des entrées externes), 
                a1, a2, a3, b0, b1, e (paramètres du modèle)
    
    SORTIE : vecteur des vitesses prédite par le modèle
    '''
    y_pred = np.zeros_like(y_obs)
    for i in range(3, len(y_obs)):
        y_pred[i] = a1*y_pred[i-1] + a2*y_pred[i-2] + a3*y_pred[i-3] + b0*u[i] + b1*u[i-1] + np.random.normal(0, e)
    return y_pred[3:]  # On ignore les trois premières valeurs pour correspondre aux retards dans le modèle




# Définition de la fonction à minimiser (moindres carrés)
def arx_least_squares(params, Yobs, U):
    '''ENTREE : params (paramètres initiaux du modèle), Yobs(matrices des vitesses observées), U (matrice des entrées externes)
    SORTIE : valeur de la fonction des moindres carré pour les paramètres en entrée et les observations'''
    a1, a2, a3, b0, b1, e = params
    n = len(U)
    J_total = 0
    for i in range(n) :
        y_pred = arx_model(Yobs[i],U[i], a1, a2, a3, b0, b1, e)
        residuals = y_pred - Yobs[i][3:]
        J=0
        for r in residuals:
           J += r*r
        J_total += J
    return J_total


def methode_ls(tracks) :
    """Realise la methode des moindres carre pour la liste de trace en entrée
    
    renvoie un dictionnaire avec la valeur des paramètres, les observations, la pentes et l'altitude.
    """
    
    y_obs =[]
    u=[]
    alt=[]

    for track in tracks :
        #Recuperation de la trace
        with open(file=track) as f:
            data = json.load(f)
        
        # Génération de données pour la parametrisation
        u.append(list(thomas(t=data)['slope'])) # Pente de la route (entrée)
        alt.append(list(thomas(t=data)['altitude']))
        y_obs.append(list(thomas(t=data)['speed']))
    
    
    initial_params = [0,0,0,0,0,0]  # Vous pouvez ajuster les valeurs initiales selon votre cas

    # Minimisation des moindres carrés
    optimized_params = minimize(arx_least_squares, initial_params, args=(y_obs,u)).x

    # Obtention des paramètres estimés
    res = {}
    res['observation']= y_obs
    res['pente']=u
    res['altitude']= alt
    res['parametres']= optimized_params
    
    #Affichage des résultats
    return res
    




def test_model(params, track):
    
    '''fonction qui fait un test avec les paramètere ajusté d'un modele (params) sur une trace (track) donnée
    
    la fonction affiche la vitesse calculée, la vitesse observée, la pente et l'altitude'''
    
    #Genaration de donnees pour tester le modele
    with open(file=track) as f:
            data = json.load(f)
            
    u = list(thomas(t=data)['slope']) # Pente de la route (entrée)
    alt = list(thomas(t=data)['altitude'])
    y_obs =list(thomas(t=data)['speed'])
    
    
    a1_est, a2_est, a3_est, b0_est, b1_est, e_est = params
    predicted_speed = arx_model(y_obs, u , a1_est, a2_est, a3_est, b0_est, b1_est, e_est)
    time_steps = np.arange(len(predicted_speed))

    plt.figure(figsize=(10, 6))
    plt.subplot(2, 2, 1)
    plt.plot(time_steps, predicted_speed, label='Vitesse prédite')
    plt.xlabel('Temps')
    plt.ylabel('Vitesse')
    plt.legend()
    

    plt.subplot(2, 2, 2)
    plt.plot(time_steps, y_obs[3:] , label='Vitesse observee')
    plt.xlabel('Temps')
    plt.ylabel('Vitesse')
    plt.legend()

    plt.subplot(2, 2, 3)
    plt.plot(time_steps, u[3:], label='Pente')
    plt.xlabel('Temps')
    plt.ylabel('Pente')
    plt.legend()
        
    plt.subplot(2, 2, 4)
    plt.plot(time_steps, alt[3:], label='Altitude')
    plt.xlabel('Temps')
    plt.ylabel('Altitude')
    plt.legend()

    plt.tight_layout()
    plt.show()
 








def etude_param():
    '''fonction  qui étudie les paramètres pour plusieurs simulations'''
    
    A1, A2, A3, B0, B1, E = [],[],[],[],[],[]
    for track in donnees[:20] : 
        res = methode_ls([track])['parametres']
        A1.append(res[0])
        A2.append(res[1])
        A3.append(res[2])
        B0.append(res[3])
        B1.append(res[4])
        E.append(res[5])
    plt.figure(figsize=(10, 6))
    plt.subplot(3, 2, 1)
    plt.plot(A1, label='A1')
    plt.legend()

    plt.subplot(3, 2, 2)
    plt.plot(A2, label='A2')
    plt.legend()

    plt.subplot(3, 2, 3)
    plt.plot(A3, label='A3')
    plt.legend()

    plt.subplot(3, 2, 4)
    plt.plot(B0, label='B0')
    plt.legend()

    plt.subplot(3, 2, 5)
    plt.plot(B1, label='B1')
    plt.legend()

    plt.subplot(3, 2, 6)
    plt.plot(E, label='E')
    plt.legend()

    plt.show()
    
    a1 = np.mean(A1)
    a2 = np.mean(A2)
    a3 = np.mean(A3)
    b0 = np.mean(B0)
    b1 = np.mean(B1)
    e = np.mean(E)

