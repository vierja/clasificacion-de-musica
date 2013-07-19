# -*- coding: utf-8 -*-
from __future__ import division
import itertools
import selection
import random
import csv
from rule import Rule
import plotly
import sys

DEFAULT_DISCRETE_INTERVALS = 100


class Classifier(object):
    """
    Clase principal del clasificador.
    """

    def __init__(self, source, discrete_intervals=DEFAULT_DISCRETE_INTERVALS, size_rule_generation=20, filter_list=[], log_results=False):
        """
        Inicializa el clasificador. Toma como fuente un archivo csv y puede
        recibir como parametro opcional la cantidad de intervalos para discretizar
        los valores de los features.
        """
        super(Classifier, self).__init__()
        self.source = source
        self.discrete_intervals = discrete_intervals
        self.features, self.train_data, self.test_data, self.result_types = self._read_source(filter_list)
        self.len_features = len(self.features)
        if log_results:
            print "Se tienen", self.len_features, "features distintos."
        self.len_data = len(self.train_data)
        self.size_rule_generation = size_rule_generation
        self.len_rules = len(self.result_types)
        self.best_rules = {}
        self.py = plotly.plotly(username='vierja', key='uzkqabvlzm', verbose=False)
        self.log_results = log_results

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

    def train(self, req_min_fitness=6, gen_select=2, selection_type=selection.TOURNAMENT_SELECTION, mutation_prob=0.05, limit_generations=10000):
        """
        Realiza el entrenamiento de las reglas, mutandolas usando tecnicas de
        algoritmos evolutivos hasta que el fitness total de el conjunto de las
        reglas alcance el minimo deseado.
        Devuelve el fitness alcanzado.
        """
        total_fitness = 0
        generation = 0
        total_best = dict((rule_name, {'rule': None, 'fitness': -1}) for rule_name, _ in self.rules.items())
        list_max_fitness = dict((rule_name, []) for rule_name, _ in self.rules.items())
        list_min_fitness = dict((rule_name, []) for rule_name, _ in self.rules.items())
        list_avg_fitness = dict((rule_name, []) for rule_name, _ in self.rules.items())

        # itero hasta tener un fitness total mayor al especificado.
        while req_min_fitness > total_fitness and generation < limit_generations:
            max_fitness_list = []
            generation += 1

            for rule_name, list_of_rules in self.rules.items():
                # devuelve una nueva lista
                list_of_rules = self._select_rules(list_of_rules, gen_select, type=selection_type)
                list_of_rules = self._crossover(list_of_rules)
                assert len(list_of_rules) == self.size_rule_generation
                # modifica la lista
                self._mutate(list_of_rules, mutation_probability=mutation_prob)
                max_fitness, best_rule, min_fitness, worst_rule = self._evaluate_fitness(list_of_rules)
                if max_fitness[0] > total_best[rule_name]['fitness']:
                    total_best[rule_name] = {'rule': best_rule, 'fitness': max_fitness[0], 'generation': generation}
                # Se guarda el max_fitness para comparar rapidamente.
                if generation % 5000 == -1 and self.log_results:
                    print "Best", rule_name, "rule of generation", generation, ", fitness:", max_fitness, ". Rule:"
                    best_rule.print_rule()
                    print "All", len(list_of_rules), "rules for ", rule_name, " of generation", generation
                    self._print_list_of_rules(list_of_rules)
                    print "End generation", generation
                    print "*************************"
                max_fitness_list.append(max_fitness[0])
                if generation % (limit_generations / 1000) == 0:
                    # if max_fitness[0] < 0.4:
                    #     print list_of_rules
                    list_max_fitness[rule_name].append([generation, max_fitness[0]])
                    list_min_fitness[rule_name].append([generation, min_fitness[0]])
                    list_avg_fitness[rule_name].append([generation, self._average_fitness(list_of_rules)])

            # El total_fitness se puede calcular como el minimo fitness de
            # todas las reglas.
            total_fitness = min(max_fitness_list)

        self.best_rules = total_best

        if self.log_results:
            print "\nTotal best:", total_best
            trace_list = []
            for type_rule, list_fitness in list_max_fitness.items():
                unziped = zip(*list_fitness)
                generation_list = list(unziped[0])
                max_fitness_list = list(unziped[1])
                min_fitness_list = list(zip(*list_min_fitness[type_rule])[1])
                avg_fitness_list = list(zip(*list_avg_fitness[type_rule])[1])

                trace = {
                    'name': "Max " + type_rule,
                    'x': generation_list,
                    'y': max_fitness_list,
                    'type': 'scatter',
                    'mode': 'markers'
                }
                trace_list.append(trace)
                continue
                trace = {
                    'x': generation_list,
                    'y': min_fitness_list,
                    'type': 'scatter',
                    'mode': 'lines'
                }
                trace_list.append(trace)
                trace = {
                    'x': generation_list,
                    'y': avg_fitness_list,
                    'type': 'scatter',
                    'mode': 'lines'
                }
                trace_list.append(trace)

            try:
                response = self.py.plot(trace_list)
                print "Performance graph:", response['url']
            except Exception, e:
                print "Connection error: ", e
                print "Could not generate graph."

        return total_best

    def _rule_fitness(self, rule):
        """
        La regla devuelve la cantidad de resultados positivos y la cantidad de
        resultados negativos.
        Los resultados positivos son la cantidad de sub-reglas que devuelven
        True dentro de la regla.
        Los resultados negativos son la cantidad de sub-reglas que devuelven
        False dentro de la regla.
        Las sub-reglas son los intervalos de features dentro de cada regla.
        La cantidad de resultados positivos mas la cantidad de resultados
        negativos debe de ser igual al total de features.
        """
        # guarda los resultados positivos.
        correct_results = 0
        incorrect_results = 0
        result_type = rule.result_type

        for song_data in self.train_data:
            # es True si la regla es del tipo de dato que se prueba
            is_type_rule = result_type == song_data['result_type']
            positive_values, negative_values = rule.is_type(song_data['values'], is_type_rule)

            if is_type_rule:
                # si la regla es del tipo de la cancion y la evaluacion da positiva
                correct_results += positive_values
                incorrect_results += negative_values
            else:
                # si la regla NO es del tipo de la cancion y la evaluacion da negativa
                correct_results += negative_values
                incorrect_results += positive_values

        # (a + b + c + d) / (len_data * num_features) == (a/num_features + b/num_features + c/num_features + d/num_features) / len_data
        # entonces para optimizar divido por num_features despues.
        rule_fitness = 0
        if correct_results >= incorrect_results:
            rule_fitness = (correct_results - incorrect_results) / (self.len_data * self.len_features)

        # Para probar
        #rule_fitness = correct_results / (self.len_data * self.len_features)

        return rule_fitness, incorrect_results / (self.len_data * self.len_features)

    def _select_rules(self, list_of_rules, num_select, type=selection.ROULETTE_WHEEL_SELECTION):
        """
        Toma como parametro una lista de reglas con su respectivo fitness
        Elige `num_select` reglas de `list_of_rules` usando determinada
        tecnica.

        Puede ser:
            Roulette wheel selection (default)
            Rank selection
            Tournament selection
        """
        # por las dudas
        assert list_of_rules >= num_select

        if type == selection.ROULETTE_WHEEL_SELECTION:
            return selection.roulette_wheel_selection(list_of_rules, num_select)
        elif type == selection.RANK_SELECTION:
            return selection.rank_selection(list_of_rules, num_select)
        elif type == selection.TOURNAMENT_SELECTION:
            return selection.tournament_selection(list_of_rules, num_select)
        # else devuelvo los primeros num_select
        return list_of_rules[:num_select]

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
        if len(list_of_rules) > 1:
            combinations = [x for x in itertools.combinations(list_of_rules, 2)]
            # Uso itertools.combinations para crear sets de combinaciones de las reglas.
            while len(list_of_rules) < self.size_rule_generation:
                for rule1, rule2 in combinations:
                    new_rule = Rule.crossover(rule1['rule'], rule2['rule'])
                    rule_map = {'fitness': (0, 0), 'rule': new_rule}
                    list_of_rules.append(rule_map)
        else:
            print "Invalid number of rules to crossover (" + str(len(list_of_rules)) + ")."
            exit(0)

        return list_of_rules[:self.size_rule_generation]

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
        max_fitness_val = -1
        max_fitness_rule = None
        max_fitness = None
        min_fitness_val = 999999
        min_fitness_rule = None
        min_fitness = None
        for rule in list_of_rules:
            rule['fitness'] = self._rule_fitness(rule['rule'])
            if rule['fitness'][0] > max_fitness_val:
                max_fitness_val = rule['fitness'][0]
                max_fitness = rule['fitness']
                max_fitness_rule = rule['rule']
            if rule['fitness'][0] < min_fitness_val:
                min_fitness_val = rule['fitness'][0]
                min_fitness = rule['fitness']
                min_fitness_rule = rule['rule']

        return max_fitness, max_fitness_rule, min_fitness, min_fitness_rule

    def _read_source(self, filter_list):
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
                if value != 'song' and value != 'genre' and value in filter_list:
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
        self.normalization_vector = []
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
            self.normalization_vector.append([max_min_diff, min_val])
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

        train_data = []
        test_data = []

        counter = 0
        for song_data in data:
            if counter % 4 == 0:
                test_data.append(song_data)
            else:
                train_data.append(song_data)
            counter += 1

        return features, train_data, test_data, result_types

    def test(self):
        results_by_type = dict((type, dict((type, 0) for type in self.result_types)) for type in self.result_types)
        num_results_by_type = dict((type, 0) for type in self.result_types)
        results_by_type_positive_negative = dict((type, {"correct": 0, "incorrect": 0}) for type in self.result_types)
        results_by_correct_value_score = dict((type, []) for type in self.result_types)
        for song_data in self.test_data:
            num_results_by_type[song_data['result_type']] += 1
            if self.log_results:
                print "Se evalua cancion de tipo:", song_data['result_type'], ", cancion:", song_data['song']
            guessed_genre, value_correct = self.guess_genre(song_data['values'], song_data['result_type'])
            results_by_correct_value_score[song_data['result_type']].append(value_correct)
            if guessed_genre == song_data['result_type']:
                results_by_type[song_data['result_type']][guessed_genre] += 1
                results_by_type_positive_negative[song_data['result_type']]["correct"] += 1
                if self.log_results:
                    print "CORRECT!"
            else:
                results_by_type[song_data['result_type']][guessed_genre] += 1
                results_by_type_positive_negative[song_data['result_type']]["incorrect"] += 1
                if self.log_results:
                    print "Incorrect."

        graph_list = []

        if self.log_results:
            result_type_list = [result_type for result_type, _ in results_by_type.items()]

            for result_type, result_test in results_by_type.items():
                res_map = {
                    "name": result_type,
                    "x": result_type_list,
                    "y": [results_by_type[each_type][result_type] for each_type in result_type_list],
                    "type": "bar"
                }
                graph_list.append(res_map)

            layout = {
                "barmode": "group",
                'xaxis': {'type': 'combination'},
                'categories': result_type_list
            }
            try:
                response = self.py.plot(graph_list, layout=layout)
                print response['url']
            except Exception, e:
                print "Connection error: ", e
                print "Could not generate graph."

            correct = {
                "name": "Correct",
                "x": result_type_list,
                "y": [result["correct"] for res_type, result in results_by_type_positive_negative.items()],
                "type": "bar"
            }

            incorrect = {
                "name": "Incorrect",
                "x": result_type_list,
                "y": [result["incorrect"] for res_type, result in results_by_type_positive_negative.items()],
                "type": "bar"
            }
            layout = {
                "barmode": "group",
                'xaxis': {'type': 'combination'},
                'categories': result_type_list
            }
            try:
                response = self.py.plot([correct, incorrect], layout=layout)
                print response['url']
            except Exception, e:
                print "Connection error: ", e
                print "Could not generate graph."

            for result_type, correct_value_score in results_by_correct_value_score.items():
                print "Average correct value score for", result_type, " = ", reduce(lambda x, y: x + y, correct_value_score) / len(correct_value_score)

        avg_correct_rules = [{result_type: reduce(lambda x, y: x + y, correct_value_score) / len(correct_value_score)} for result_type, correct_value_score in results_by_correct_value_score.items()]
        correct_results = [{res_type: result["correct"] / num_results_by_type[res_type]} for res_type, result in results_by_type_positive_negative.items()]
        return avg_correct_rules, correct_results

    def guess_genre(self, data, data_type, normalize=False):
        if normalize:
            # Primero tengo que normalizar los datos
            for i, [max_min_diff, min_val] in enumerate(self.normalization_vector):
                data[i] = (data[i] - min_val) / max_min_diff

        rules_result = {}
        for result_type, rule in self.best_rules.items():
            positive_values, negative_values = rule['rule'].is_type(data)
            rules_result[result_type] = positive_values / self.len_features

        if self.log_results:
            print "  Scoring por genre: "
        import operator
        sorted_scores = sorted(rules_result.iteritems(), key=operator.itemgetter(1), reverse=True)
        #print sorted_scores
        correct_value_score = 0
        for result_type, score in sorted_scores:
            if data_type == result_type:
                correct_value_score = score
            if self.log_results:
                print "   -", result_type, ":", score
        return sorted_scores[0][0], correct_value_score

    def load_rules(self, source):
        """
        Carga las reglas desde un archivo.
        Sirve para poder persistir un entrenamiento a medio camino
        y poder seguir ejecutando el train.
        """
        pass

    def save_rules(self, output):
        """
        Guarda las reglas en un archivo
        """
        pass

    def _print_best_rules(self, best_rules):
        for rule_type, rule_dict in best_rules.items():
            print "Best rule: rule type:", rule_dict['rule'].result_type, ", rule fitness:", rule_dict['fitness']
            rule_dict['rule'].print_rule()

    def _print_list_of_rules(self, list_of_rules):
        for i, rule_dict in enumerate(list_of_rules):
            print "#", i, ". Rule type:", rule_dict['rule'].result_type, ", rule fitness:", rule_dict['fitness']
            rule_dict['rule'].print_rule()

    def _print_rules(self):
        for rule_type, rule_list in self.rules.items():
            print "Rule type:", rule_type
            for i, rule_dict in enumerate(rule_list):
                print "#", i, ". Rule type:", rule_type, ", rule fitness:", rule_dict['fitness']
                rule_dict['rule'].print_rule()

    def _average_fitness(self, list_of_rules):
        total = 0
        for rule_dict in list_of_rules:
            total += rule_dict['fitness'][0]
        return total / len(list_of_rules)
