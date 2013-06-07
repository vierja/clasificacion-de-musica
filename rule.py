import random


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
    def __init__(self, features, discrete_intervals, result_type):
        super(Rule, self).__init__()
        self.features = features
        self.discrete_intervals = discrete_intervals
        self.feature_map = {}
        self.result_type = result_type

        for feature in self.features:
            # Los intervalos para cada feature se representan como una lista
            # de tamaño fijo (RANGO_VALOR / DISCRETE_INTERVALS)
            # Los otros valores posibles son True o False.
            # La idea es usar None para cuando no importa.
            self.feature_map[feature] = [None] * self.discrete_intervals

    def _init_random_interval(self):
        """
        Devulve una lista de largo `discrete_intervals` con valores True o False.
        La idea es crear un intervalo que parezca una regla valida.
        En primer lugar para facilitar el trabajo inicial se va a realizar una
        regla con una secuencia seguida de True y el resto False.
        """
        feature_list = [False] * self.discrete_intervals

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
