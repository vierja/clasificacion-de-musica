# -*- coding: utf-8 -*-
import itertools
import selection
import random
import csv
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
        self.best_rules = {}

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

        self._print_rules()

    def train(self, min_fitness=0.9, gen_select=4):
        """
        Realiza el entrenamiento de las reglas, mutandolas usando tecnicas de
        algoritmos evolutivos hasta que el fitness total de el conjunto de las
        reglas alcance el minimo deseado.
        Devuelve el fitness alcanzado.
        """
        total_fitness = 0
        generation = 0
        best_rules = {}

        # itero hasta tener un fitness total mayor al especificado.
        while min_fitness > total_fitness:
            max_fitness_list = []
            generation += 1

            print "Generation", generation

            for rule_name, list_of_rules in self.rules.items():
                # devuelve una nueva lista
                list_of_rules = self._select_rules(list_of_rules, gen_select)
                list_of_rules = self._crossover(list_of_rules)
                # modifica la lista
                self._mutate(list_of_rules)
                max_fitness, best_rule = self._evaluate_fitness(list_of_rules)
                # Se guarda el max_fitness para comparar rapidamente.
                max_fitness_list.append(max_fitness)
                # Guardo la mejor regla en caso de que quiera tenerla.
                best_rules[rule_name] = {'rule': best_rule, 'fitness': max_fitness}

            # El total_fitness se puede calcular como el minimo fitness de
            # todas las reglas.
            total_fitness = min(max_fitness_list)

        self.best_rules = best_rules

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

            # si la regla es del tipo de la cancion y la evaluacion da positiva
            if result_type == song_data['result_type'] and song_is_type:
                positive_results += 1
            # si la regla no es del tipo de la cancion y la evaluacion da negativa
            elif result_type != song_data['result_type'] and not song_is_type:
                positive_results += 1

        # devuelve el fitness como
        # los resultados positivos / la cantidad de datos de prueba
        return positive_results / self.len_data

    def _select_rules(self, list_of_rules, num_select, type=selection.ROULETTE_WHEEL_SELECTION):
        """
        Toma como parametro una lista de reglas con su respectivo fitness
        Elige `num_select` reglas de `list_of_rules` usando determinada
        tecnica.

        Puede ser:
            Roulette wheel selection
            TODO: Rank selection
            TODO: Tournament selection
        """

        if type == selection.ROULETTE_WHEEL_SELECTION:
            return selection.roulette_wheel_selection(list_of_rules, num_select)

        return list_of_rules

    def _crossover(self, list_of_rules):
        """
        Crea cruces entre las reglas en la lista `list_of_rules`.

        TODO: A DEFINIRSE.
            - Parametros
            - Eleccion
            - Forma de cruzamiento
        """
        """
        Implementacion α. Suponiendo que se obtienen 4 reglas, y se quieren
        10 en total se crean hijos a partir de las combinaciones de 4 tomadas
        de a dos (6) y se lo suma a los padres para un total de 10.
        """
        print "len(list_of_rules)", len(list_of_rules)
        combinations = [x for x in itertools.combinations(list_of_rules, 2)]
        # assert len(combinations) == 2 TODO: porque puse esto?!?!!
        # Uso itertools.combinations para crear sets de combinaciones de las reglas.
        for rule1, rule2 in combinations:
            new_rule = Rule.crossover(rule1['rule'], rule2['rule'])
            rule_map = {'fitness': 0, 'rule': new_rule}
            list_of_rules.append(rule_map)

        return list_of_rules

    def _mutate(self, list_of_rules, mutation_probability=0.05):
        """
        Muta algunas reglas de las reglas en la lista `list_of_rules`.

        Recibe una `mutation_probability` que por default es 5%.
        Para cada regla se hace una mutacion con el 5% de probabilidad.
        """
        for rule_map in list_of_rules:
            # random.random() devuelve un numero de 0 a 1.
            if random.random() < mutation_probability:
                rule_map['rule'].mutate()

    def _evaluate_fitness(self, list_of_rules):
        """
        Para cada regla en la lista de reglas `list_of_rules` recalcula el
        fitness.
        Devuelve el maximo valor de fitness obtenido.
        """
        max_fitness = 0
        max_fitness_rule = None
        print "_evaluate_fitness: se evaluan", len(list_of_rules), "reglas."
        for rule in list_of_rules:
            print "Se evalua regla de tipo:", rule['rule'].result_type
            rule['fitness'] = self._rule_fitness(rule['rule'])
            if rule['fitness'] > max_fitness:
                max_fitness = rule['fitness']
                max_fitness_rule = rule['rule']

        return max_fitness, max_fitness_rule

    def _read_source(self):
        """
        Lee de la fuente de entrenamiento (csv) tres listas.
            - features: lista de los nombres de los features.
            - data: lista de dict (Maps) compuestos de:
                'values': lista ordenada (mismo orden que features) de los valores
                'result_type': tipo de resultado de esos valores.
                'song': nombre de la cancion
            - result_types: lista de los posibles tipos de valores de los resultados
        """
        features = []
        data = []
        with open(self.source, 'r') as source:
            reader = csv.DictReader(source)
            header = reader.fieldnames
            for value in header:
                if value != 'song' and value != 'genre':
                    features.append(value)

            # para cada linea del csv creo un map de 'result_type', 'song' y 'values'
            for source_line in reader:
                # creo los values en el MISMO orden que los features
                values = []
                for feature in features:
                    values.append(float(source_line[feature]))
                song_data = {
                    'result_type': source_line['genre'],
                    'song': source_line['song'],
                    'values': values
                }
                data.append(song_data)

        """
        Con la data creada primero obtengo la lista 'result_types'
        Como quiero una lista sin repetidos (ya que para cada uno
        se tiene una regla), se quitan los repetidos pasandolo a set
        y de nuevo a lista.
        """
        result_types = []
        for value in data:
            result_types.append(value['result_type'])
        result_types = list(set(result_types))

        """
        Tenemos que desnormalizar los valores, los vamos a setear desde 0 a 1.
        para esto tenemos que conseguir el minimo y maximo de cada variable.
        """
        for i, feature in enumerate(features):
            max_val = None
            min_val = None

            # Para cada feature buscamos todos los datos.
            for song_data in data:
                value = song_data['values'][i]
                if max_val is None:
                    max_val = value
                else:
                    max_val = max(value, max_val)

                if min_val is None:
                    min_val = value
                else:
                    min_val = min(value, min_val)

            max_min_diff = max_val - min_val
            """
                              x - xMin
            normalize(x) = --------------
                             xMax - Xmin

            Para cada valor del feature actual actualizamos el value para que
            quede entre 0 y 1.
            Esto genera que el maximo valor sea 1 y el minimo sea 0.
            """
            for song_data in data:
                song_data['values'][i] = (song_data['values'][i] - min_val) / max_min_diff

        return features, data, result_types

    def load_rules(self, source):
        """
        Carga las reglas desde un archivo.
        Sirve para poder persistir un entrenamiento a medio camino
        y poder seguir ejecutando el train.
        """
    def save_rules(self, output):
        """
        Guarda las reglas en un archivo
        """
        pass

    def _print_rules(self):
        for rule_type, rule_list in self.rules.items():
            print "Rule type:", rule_type
            for i, rule_dict in enumerate(rule_list):
                print "#", i, ". Rule fitness:", rule_dict['fitness']
                rule_dict['rule'].print_rule()
