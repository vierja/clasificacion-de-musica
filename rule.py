# -*- coding: utf-8 -*-
from __future__ import division
import random
try:
    import numpy as np
except ImportError:
    import numpypy as np
import sys

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

NEW_RANDOM = 1
INCREASE = 2
DECREASE = 3


class Rule(object):
    """
    Regla de clasificacion individual.
    """

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
        self.features_len = len(self.features)
        self.discrete_intervals = discrete_intervals
        self.features_lists = []
        self.result_type = result_type
        self.stats = [[0, 0] for i in self.features]  # Guarda la cantidad de exitos y errores en esta regla.

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
            for num_feature, feature in enumerate(self.features):
                if random.choice([True, False]):
                    self.features_lists.append(parent1.features_lists[num_feature])
                else:
                    self.features_lists.append(parent2.features_lists[num_feature])

    @classmethod
    def crossover(cls, parent1, parent2):
        return cls(parent1.features, parent1.discrete_intervals, parent1.result_type, parent1=parent1, parent2=parent2)

    def _init_random_interval(self, minimum_length=10):
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
        # y tiene un minimo de 'minimum_length' (default: 10)
        true_length = random.randint(minimum_length, self.discrete_intervals/2)

        # Booleano que determina si se debe tomar la posicion como indice de
        # inicio o final de la secuencia de True's
        beginning_position = random.choice([True, False])
        # Posicion (ya sea de inicio o final, depende de beginning_position)
        position = random.randint(0, self.discrete_intervals)

        if beginning_position:
            for i in range(position, min(position + true_length, self.discrete_intervals)):
                feature_list[i] = True
        else:
            for i in range(max(0, position - true_length), min(position, self.discrete_intervals)):
                feature_list[i] = True

        return feature_list

    def is_type(self, values, is_type=None):
        """
        Devuelve True o False dependiendo si los valores se encuentran dentro
        de las reglas especificadas.
        Los values deben estar normalizados de 0 a 1.
        """
        interval = (1.0/(self.discrete_intervals - 1))

        correct_values = 0
        incorrect_values = 0

        for pos, value in enumerate(values):
            if value != 1:
                # Obtengo el valor minimo de el intervalo al que pertenece.
                min_val = value - value % interval
                # Calculo la posicion de el intervalo.
                value_pos = int(min_val / interval)
            else:
                # Si el valor == 1 entonces la posicion es la ultima.
                value_pos = -1

            if self.features_lists[pos][value_pos]:
                correct_values += 1
                if is_type is not None: 
                    if is_type:
                        # Si la regla es positiva y es de tipo correcto
                        self.stats[pos][0] += 1
                    else:
                        # Si la regla es positiva y NO es de tipo correcto
                        self.stats[pos][1] += 1
            else:
                incorrect_values += 1
                if is_type is not None: 
                    if is_type:
                        # Si la regla es negativa y es de tipo correcto
                        self.stats[pos][1] += 1
                    else:
                        # Si la regla es negativa y NO es de tipo correcto.
                        self.stats[pos][0] += 1

        return abs(correct_values - incorrect_values), 0

    def mutate(self, action=NEW_RANDOM):
        """
        En la mutacion, cuando se separa un intervalo, se selecciona un punto al azar de los micro-intervalos para hacer el corte. (split)
        Luego cuando se fusiona dos intervalos, el estado resultante (1 o 0) del intervalo se toma del que tiene más micro-intervalos.
        Si los dos tienen la misma cantidad de micro-intervalos, el valor del estado se elige al azar. (mutate)
        SACADO DEL INFORME. VER IMAGEN QUE PUSIMOS COMO EXPLICACION.

        DUDAS:
            - Aca pasamos la regla, el feature al cual le vamos a hacer el mutate se elige aleatoriamente?
            - No me queda claro la representacion de los mini-intervalos.
        """

        """
        Se tienen 3 posibles acciones
        - NEW_RANDOM
            Se crea un nuevo interval random desde cero.
        - INCREASE
            Se incrementa el intervalo de determinado feature.
        - DECREASE
            Se decrementa el intervalo de determinado feature.
        """
        # NEW_RANDOM, INCREASE, DECREASE = 1, 2, 3

        mutated_features = []
        num_to_mutate = random.randint(1, self.features_len)
        while len(mutated_features) < num_to_mutate:
            feature_pos = random.randint(0, self.features_len - 1)
            if not feature_pos in mutated_features:
                mutated_features.append(feature_pos)

                # Elijo la accion a tomar.
                # action = random.choice([NEW_RANDOM, INCREASE, DECREASE])

                if action == NEW_RANDOM:
                    self.features_lists[feature_pos] = self._init_random_interval()

                elif action == INCREASE:
                    """
                    Para esta accion si un intervalo tiene dos partes entonces
                    se incrementa la primera parte del primero y la ultima
                    parte del ultimo.
                    Si alguno de los dos coinciden con el final entonces ese
                    no se incrementa.
                    """
                    # Elijo al azar cuanto se va a incrementar el intervalo.
                    increase_size = random.randint(1, 5)
                    # Listo las posiciones de True de la lista.
                    true_interval_positions = [i for i in range(self.discrete_intervals) if self.features_lists[feature_pos][i]]

                    if len(true_interval_positions) < 1:
                        continue
                    # Expando el intervalo de la primera parte.
                    if true_interval_positions[0] > 0:
                        for i in range(max(0, true_interval_positions[0] - increase_size), true_interval_positions[0]):
                            self.features_lists[feature_pos][i] = True
                    # Expando el intervalo de la ultima parte.
                    if true_interval_positions[-1] < self.discrete_intervals:
                        for i in range(true_interval_positions[-1] + 1, min(self.discrete_intervals - 1, true_interval_positions[-1] + increase_size)):
                            self.features_lists[feature_pos][i] = True

                elif action == DECREASE:
                    decrease_size = random.randint(1, 5)
                    true_interval_positions = [i for i in range(self.discrete_intervals) if self.features_lists[feature_pos][i]]
                    if len(true_interval_positions) < decrease_size * 2:
                        continue
                    # Disminuyo el intervalo de la primera parte
                    # print "true_interval_positions", true_interval_positions, "decrease_size", decrease_size
                    for i in range(true_interval_positions[0], true_interval_positions[0] + decrease_size):
                        self.features_lists[feature_pos][i] = False
                    # Disminuyo el intervalo de la segunda parte
                    for i in range(true_interval_positions[-1] - decrease_size + 1, true_interval_positions[0] - 1):
                        self.features_lists[feature_pos][i] = False

                # Luego de la mutacion resteo las estadisticas
                self.stats[feature_pos] = [0, 0]
        return

        # # Elijo aleatoriamente el feature al cual le voy a aplicar la mutacion
        # feature = random.randint(0, self.features_len - 1)

        # # Elijo aleatoriamente intervalo que voy a mutar
        # position = random.randint(0, self.discrete_intervals - 1)

        # # Si el valor que voy a mutar es True entonces lo cambio a False y si es False a True
        # self.features_lists[feature][position] = not self.features_lists[feature][position]

    def print_rule(self):
        print "Feature list size: ", self.features_len
        print "Counter:", self.stats
        for features_list in self.features_lists:
            self._print_features_list(features_list)

    def _print_features_list(self, features_list, pos=None):
        for i in range(self.discrete_intervals):
            if pos is not None and pos == i:
                sys.stdout.write('@')
            elif features_list[i]:
                sys.stdout.write('+')
            else:
                sys.stdout.write('-')
        print ""
