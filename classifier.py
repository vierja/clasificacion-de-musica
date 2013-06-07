from rule import Rule


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
        self.features, self.values, self.result_types = self._read_source()

        # Las reglas se guardan en una Lista.
        # La idea es tener una regla por cada resultado posible.
        # Una regla devuelve un valor binario, SI es result_type o NO lo es.
        self.rules = []
        for result_type in self.result_types:
            self.rules = Rule(self.features, self.discrete_intervals, result_type)

    def train():
        pass

    def _read_source():
        return [], [], []
