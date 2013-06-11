from rule import Rule
import csv

DEFAULT_DISCRETE_INTERVALS = 100


class Classifier(object):
    """
    Clase principal del clasificador.
    """

    def __init__(self, source, discrete_intervals=DEFAULT_DISCRETE_INTERVALS):
        """
        Inicializa el clasificador. Toma como fuente un archivo csv y puede
        recibir como parametro opcional la cantidad de intervalos para discretizar
        los valores de los features.
        """
        super(Classifier, self).__init__()
        self.source = source
        self.discrete_intervals = discrete_intervals
        self.features, self.data, self.result_types = self._read_source()
        self.len_data = len(self.data)

        # Las reglas se guardan en una Lista.
        # La idea es tener una regla por cada resultado posible.
        # Una regla devuelve un valor binario, SI es result_type o NO lo es.
        self.rules = []
        for result_type in self.result_types:
            self.rules.append(Rule(self.features, self.discrete_intervals, result_type))

    def train():
        pass

    def rule_fitness(self, rule):
        """
        Si una cancion es del tipo que se prueba la regla, y la regla devuelve
        positiva entonces se suma 1
        Si una cancion NO es del tipo que se prueba en la regla y la regla
        devuelve negativa entonces se suma 1
        en el resto de los casos no se suma.
        """
        # guarda los resultados positivos.
        positive_results = 0
        result_type = rule.result_type

        for song_data in self.data:
            song_is_type = rule.is_type(song_data['values'])

            if result_type == song_data['result_type'] and song_is_type:
                positive_results += 1
            elif result_type != song_data['result_type'] and not song_is_type:
                positive_results += 1

        # devuelve el fitness como los resultados positivos / la cantidad de datos de prueba
        return positive_results / self.len_data


    def _read_source():
        """
        Lee de la fuente de entrenamiento (csv) tres listas.
        features: lista de los nombres de los features.
        data: lista de dict (Maps) compuestos de:
            'values': lista ordenada (mismo orden que features) de los valores
            'result_type': tipo de resultado de esos valores.
        result_types: lista de los posibles tipos de valores de los resultados
        """
        return [], [], []
