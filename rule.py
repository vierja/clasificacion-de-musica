# -*- coding: utf-8 -*-
import random
import numpy as np

"""
Esta implementacion de Rule inicial tiene la limitacion que la discretizacion
que se realiza para los intervalores de los posibles valores de los features
es de largo fijo.

Supuestamente en los papers investigados la discretizacion es un elemento mas
que puede evolucionar con el algoritmo.

Al no tener bien claro como implementar esto, se piensa realizar en primer
lugar una implementacion de largo fijo para luego poder, con una version que
funcione, mejorarla.
"""


class Rule(object):
    """Regla de clasificacion individual."""

    def __init__(self, features, discrete_intervals, result_type, parent1=None, parent2=None):
        """
        Crea la regla.
        `features` es la lista de nombre de features que pertenecen a la regla.
        `discrete_intervals` es la cantidad de intervalos para cada valor de
        cada feature de la regla.
        Los valores de los features deben de estar normalizados entre 0 y 1
        para facilmente calcular su posicion.
        `result_type` es el tipo de objeto que la regla prueba.
        """
        super(Rule, self).__init__()
        self.features = features
        self.discrete_intervals = discrete_intervals
        self.features_lists = []
        self.result_type = result_type

        if parent1 is None or parent2 is None:
            # La regla se representa como un map de listas
            # Donde cada valor del map principal representa un feature
            # Y la lista de ese feature representan los intervalos discretos.

            # En principio las listas van a tener largo fijo (discrete_intervals)
            # pero luego el largo (o minima unidad de discretizacion) va a poder
            # evolucionar con el algoritmo.

            # Enumeramos las reglas para tener claro
            for feature in self.features:
                self.features_lists.append(self._init_random_interval())
        else:
            # Si se pasan padres a la regla entonces se crea una
            # regla crossover a partir de estos.
            pass

    @classmethod
    def crossover(cls, parent1, parent2):
        return cls(parent1.features, parent1.discrete_intervals, parent1.result_type, parent1=parent1, parent2=parent2)

    def _init_random_interval(self):
        """
        Devulve una lista de largo `discrete_intervals` con valores True o False.
        La idea es crear un intervalo que parezca una regla valida.
        En primer lugar para facilitar el trabajo inicial se va a realizar una
        regla con una secuencia seguida de True y el resto False.

        Ejemplo:
        discrete_intervals = 5
        0 --- 0.25 --- 0.50 --- 0.75 --- 1
           F        T        F        F

        value = 0.63

        quiero obtener 0.50 = 0.63 - X
        X = 0.63 % 0.25

        value - float(float(value) % (float(1)/(discrete_intervals - 1)))

        con 0.50 obtener el numero de intevalo
        X * 0.25 = 0.50, X = 0.50 / 0.25


        """
        feature_list = np.array([False] * self.discrete_intervals, dtype=np.bool)

        # La secuencia de largo True no deberia de ser mas larga que la mitad
        # de la secuencia total.
        true_length = random.randrange(1, self.discrete_intervals/2)

        # Booleano que determina si se debe tomar la posicion como indice de
        # inicio o final de la secuencia de True's
        beginning_position = random.choice([True, False])
        # Posicion (ya sea de inicio o final, depende de beginning_position)
        position = random.randrange(0, self.discrete_intervals)

        if beginning_position:
            for i in range(position, min(true_length, self.discrete_intervals)):
                feature_list[i] = True
        else:
            for i in range(max(0, position - true_length), position + true_length):
                feature_list[i] = True

        return feature_list

    def is_type(self, values):
        """
        Devuelve True o False dependiendo si los valores se encuentran dentro
        de las reglas especificadas.
        Los values deben estar normalizados de 0 a 1.
        """
        interval = (1.0/(self.discrete_intervals - 1))

        for pos, value in enumerate(values):
            if value != 1:
                # Obtengo el valor minimo de el intervalo al que pertenece.
                min_val = value - value % interval
                # Calculo la posicion de el intervalo.
                value_pos = int(min_val / interval)
            else:
                # Si el valor == 1 entonces la posicion es la ultima.
                value_pos = -1

            # si nos encontramos con un valor False, devolvemos False.
            if not self.features_lists[pos][value_pos]:
                return False

        # Si no retorne False hasta entonces entonces es True.
        return True

    def mutate(self):
        """		
        En la mutacion, cuando se separa un intervalo, se selecciona un punto al azar de los micro-intervalos para hacer el corte. (split)
        Luego cuando se fusiona dos intervalos, el estado resultante (1 o 0) del intervalo se toma del que tiene m�s micro-intervalos. 
        Si los dos tienen la misma cantidad de micro-intervalos, el valor del estado se elige al azar. (mutate)
        SACADO DEL INFORME. VER IMAGEN QUE PUSIMOS COMO EXPLICACION.

        DUDAS:   
		    - Aca pasamos la regla, el feature al cual le vamos a hacer el mutate se elige aleatoriamente?
            - No me queda claro la representacion de los mini-intervalos.
        """

        # Elijo aleatoriamente el feature al cual le voy a aplicar la mutacion
        feature = random.randint(0, len(features)-1)

        # Elijo aleatoriamente intervalo que voy a mutar
        position = random.randint(0, self.discrete_intervals-1) # DUDA: por que vos usas el randrange si la posicion tiene que ser un entero?

        # Si el valor que voy a mutar es True entonces lo cambio a False
        if self.feature_list[feature][position]:
	        self.feature_list[feature][position] = False
        else: # Si el valor que voy a mutar es False entonces lo cambio a True
	        self.feature_list[feature][position] = True
