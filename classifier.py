from rule import Rule

DEFAULT_DISCRETE_INTERVALS = 100


class Classifier(object):
    """
    Clase principal del clasificador.
    """

    def __init__(self, source, discrete_intervals=DEFAULT_DISCRETE_INTERVALS, size_rule_generation=10):
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
        self.size_rule_generation = size_rule_generation
        self.len_rules = len(self.result_types)

        # Cada regla tiene `size_rule_generation` reglas inicialmente creadas
        # al azar.
        # La idea es evolucionar sobre este conjunto de reglas para cada tipo
        # de reglas.
        # Una regla devuelve un valor binario, SI es result_type o NO lo es.

        self.rules = {}
        for result_type in self.result_types:
            self.rules[result_type] = []

            # Para cada tipo de regla creo `size_rule_generation` reglas al
            # azar y evaluo de forma prematura con los datos que tienen.
            for i in range(self.size_rule_generation):
                rule = Rule(self.features, self.discrete_intervals, result_type)
                rule_dict = {'rule': rule, 'fitness': self._rule_fitness(rule)}
                self.rules[result_type].append(rule_dict)

    def train(min_fitness=0.9, gen_select=4):
        """
        Realiza el entrenamiento de las reglas, mutandolas usando tecnicas de
        algoritmos evolutivos hasta que el fitness total de el conjunto de las
        reglas alcance el minimo deseado.
        Devuelve el fitness alcanzado.
        """
        total_fitness = 0
        generation = 0
        fitness_sum = 0

        # itero hasta tener un fitness total mayor al especificado.
        while total_fitness > min_fitness:
            max_fitness_list = []
            for list_of_rules in self.rules:
                # devuelve una nueva lista
                list_of_rules = self._select_rules(list_of_rules, gen_select)
                list_of_rules = self._crossover(list_of_rules)
                # modifica la lista
                self._mutate(list_of_rules)
                max_fitness = self._evaluate_fitness(list_of_rules)
                max_fitness_list.append(max_fitness)

            # El total_fitness se puede calcular como el minimo fitness de
            # todas las reglas.
            total_fitness = min(max_fitness_list)

        return total_fitness

    def _rule_fitness(self, rule):
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

        # devuelve el fitness como
        # los resultados positivos / la cantidad de datos de prueba
        return positive_results / self.len_data

    def _select_rules(self, list_of_rules, num_select):
        """
        Toma como parametro una lista de reglas con su respectivo fitness
        Elige `num_select` reglas de `list_of_rules` usando determinada
        tecnica.

        Puede ser:
            Roulette wheel selection
            Rank selection
            Tournament selection

        TODO: A DEFINIRSE
        """
        return list_of_rules

    def _crossover(self, list_of_rules):
        """
        Crea cruces entre las reglas en la lista `list_of_rules`.

        TODO: A DEFINIRSE.
            - Parametros
            - Eleccion
            - Forma de cruzamiento
        """
        return list_of_rules

    def _mutate(self, list_of_rules):
        """
        Muta algunas reglas de las reglas en la lista `list_of_rules`.

        TODO: A DEFINIRSE.
            - Parametros
            - Como elegir
            - Tipo de mutacion
        """
        # No devuelve, modifica directamente la lista.
        pass

    def _evaluate_fitness(self, list_of_rules):
        """
        Para cada regla en la lista de reglas `list_of_rules` recalcula el
        fitness.
        Devuelve el maximo valor de fitness obtenido.
        """
        max_fitness = 0
        for rule in list_of_rules:
            rule['fitness'] = self._rule_fitness(rule['rule'])
            if rule['fitness'] > max_fitness:
                max_fitness = rule['fitness']

        return max_fitness

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
