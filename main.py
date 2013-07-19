# -*- coding: utf-8 -*-
import argparse
import itertools
import plotly
import selection
from classifier import Classifier
import sys
import time


def main():
    parser = argparse.ArgumentParser(description='Clasificador de musica.\nToma los datos de entrenamiento de un archivo y utiliza algoritmos evolutivos para crear y mejorar las reglas de clasificación.')
    parser.add_argument('-d', '--data', help='Archivo donde se encuentra la información fuente para el clasificador.')
    args = vars(parser.parse_args())

    """
    Los valores default son:
        tamaño discretizacion - 100
        poblacion de generacion - 10
        min fitness para terminar - 0.9
        numero a seleccionar - 4
        porcentaje de mutacion - 0.05
        maximo de generaciones - 10000
        tipo de seleccion - ROULETTE_WHEEL_SELECTION
    """
    defaults = [100, 10, 0.9, 4, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION]

    classifier = Classifier(args['data'], discrete_intervals=defaults[0], size_rule_generation=defaults[1], filter_list=["skewness", "spectral_rolloff", "energy", "sv", "spread", "centroid", "obsi", "kurtosis"], log_results=False)
    start = time.clock()
    best_results = classifier.train(req_min_fitness=defaults[2], gen_select=defaults[3], mutation_prob=defaults[4], limit_generations=defaults[5])
    duration = (time.clock() - start)*1000
    print "Duration\t", duration
    print "Training endend."
    print "Best results:", best_results
    print "Testing:"
    classifier.test()
    print "Testing ended."


def test(args):
    test_performance(args, 5)
    return
    #return
    options = [
        [100, 10, 0.9, 4, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION],  # discrete_intervals, size_rule_generation, req_min_fitness, gen_select, limit_generations
        [1000, 10, 0.9, 4, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION],
        [100, 20, 0.9, 4, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION],
        [100, 5, 0.9, 2, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION],
        [100, 10, 0.9, 2, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION],
        [100, 10, 0.9, 6, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION],
        [200, 50, 0.9, 10, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION],
        [300, 10, 0.9, 4, 0.1, 10000, selection.ROULETTE_WHEEL_SELECTION],
        [500, 15, 0.9, 2, 0.005, 10000, selection.ROULETTE_WHEEL_SELECTION],
        [50, 20, 0.9, 4, 0.1, 10000, selection.ROULETTE_WHEEL_SELECTION]
    ]

    #prueba Tamaño de población
    options = [
        [100, 5, 0.9, 2, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION],
        [100, 10, 0.9, 2, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION],
        [100, 15, 0.9, 2, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION],
        [100, 20, 0.9, 2, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION],
        [100, 30, 0.9, 2, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION],
        [100, 50, 0.9, 2, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION]
    ]

    #prueba Proceso de seleccion
    options = [
        [100, 10, 0.9, 2, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION],
        [100, 10, 0.9, 2, 0.05, 10000, selection.RANK_SELECTION],
        [100, 10, 0.9, 2, 0.05, 10000, selection.TOURNAMENT_SELECTION]
    ]

    options = [
        [100, 10, 0.9, 2, 0.05, 10000, selection.ROULETTE_WHEEL_SELECTION],
    ]

    average_multiple_runs(30, options, args)

    test_combinations(args)

    for num, option in enumerate(options):
        print "Option num:", num, ", val:", option
        classifier = Classifier(args['data'], discrete_intervals=option[0], size_rule_generation=option[1], filter_list=["skewness", "spectral_rolloff", "energy", "sv", "spread", "centroid", "obsi", "kurtosis"], log_results=True)
        best_results = classifier.train(req_min_fitness=option[2], gen_select=option[3], mutation_prob=option[4], limit_generations=option[5])
        print "Testing"
        classifier.test()
        # classifier.guess_genre([7.53659769442,1389.49121537,0.0166588959174,0.355062895642,1480.75635175,769.172547276,3.47303203307,69.8220939453])
        print "Training ended\nFinal fitness:", best_results


def average_multiple_runs(num_runs, options, args):
    for num, option in enumerate(options):
        print "Running", num_runs, "iterations with options:", option
        list_best_results = []
        list_test_results = []
        list_correct_results = []
        for i in range(num_runs):
            print "Running #" + str(i + 1)
            classifier = Classifier(args['data'], discrete_intervals=option[0], size_rule_generation=option[1], filter_list=["skewness", "spectral_rolloff", "energy", "sv", "spread", "centroid", "obsi", "kurtosis"], log_results=False)
            best_results = classifier.train(req_min_fitness=option[2], gen_select=option[3], mutation_prob=option[4], limit_generations=option[5], selection_type=option[6])
            test_results, correct_results = classifier.test()
            list_best_results.append(best_results)
            list_test_results.append(test_results)
            list_correct_results.append(correct_results)
        print "Results for option: ", option
        print "run\ttype\tgen\tfitness"
        for i, results in enumerate(list_best_results):
            for rule, result in results.items():
                print str(i + 1) + "\t" + rule[:7] + "\t" + str(result["generation"]) + "\t" + str(result["fitness"])

        print "run\ttype\tavg correct rules"
        for i, results in enumerate(list_test_results):
            for avg_map in results:
                print str(i + 1) + "\t" + avg_map.keys()[0][:7] + "\t" + str(avg_map[avg_map.keys()[0]])

        print "run\ttype\tavg correct results"
        for i, results in enumerate(list_correct_results):
            for avg_map in results:
                print str(i + 1) + "\t" + avg_map.keys()[0][:7] + "\t" + str(avg_map[avg_map.keys()[0]])


def test_performance(args, num_runs):
    #Features:
    features = ["skewness", "spectral_rolloff", "energy", "sv", "spread", "centroid", "zcr", "obsi", "kurtosis"]
    option = [100, 10, 0.9, 2, 0.05, 1000, selection.ROULETTE_WHEEL_SELECTION]
    for i in range(1, len(features) + 1):
        print "Num of features:", i
        for num_run in range(num_runs):
            classifier = Classifier(args['data'], discrete_intervals=option[0], size_rule_generation=option[1], filter_list=features[:i], log_results=False)
            start = time.clock()
            classifier.train(req_min_fitness=option[2], gen_select=option[3], mutation_prob=option[4], limit_generations=option[5], selection_type=option[6])
            duration = (time.clock() - start)*1000
            print num_run, "\t", duration


def test_combinations(args, graph=False):
    py = plotly.plotly(username='vierja', key='uzkqabvlzm', verbose=False)
    options = [100, 10, 0.9, 4, 0.05, 10000]
    features = ["skewness", "spectral_rolloff", "energy", "sv", "spread", "centroid", "zcr", "obsi", "kurtosis"]
    electronic_y = []
    classical_y = []
    categories = []

    print '\t'.join([feature[:2] for feature in features] + ["meta", "acou", "regg", "elec", "class"])

    for i in range(1, len(features) + 1):
        combinations = [list(comb) for comb in itertools.combinations(features, i)]
        for comb in combinations:
            comb_name = ', '.join(comb)
            classifier = Classifier(args['data'], discrete_intervals=options[0], size_rule_generation=options[1], filter_list=comb)
            top_fitness = classifier.train(req_min_fitness=options[2], gen_select=options[3], mutation_prob=options[4], limit_generations=options[5])
            for feature in features:
                if feature in comb:
                    sys.stdout.write("X\t")
                else:
                    sys.stdout.write("\t")
            sys.stdout.write(str(top_fitness['metal']["fitness"])[:4] + "\t")
            sys.stdout.write(str(top_fitness['acoustic']["fitness"])[:4] + "\t")
            sys.stdout.write(str(top_fitness['reggae']["fitness"])[:4] + "\t")
            sys.stdout.write(str(top_fitness['electronic']["fitness"])[:4] + "\t")
            sys.stdout.write(str(top_fitness['classical']["fitness"])[:4] + "\n")

            if graph:
                print "Training ended\nFinal fitness:", top_fitness
                electronic_y.append(top_fitness['metal'])
                classical_y.append(top_fitness['classical'])
                categories.append(comb_name)

                if len(categories) > 20:
                    electronic = {
                        "name": "Metal",
                        "x": categories,
                        "y": electronic_y,
                        "type": "bar"
                    }

                    classical = {
                        "name": "Classical",
                        "x": categories,
                        "y": classical_y,
                        "type": "bar"
                    }

                    layout = {
                        "barmode": "group",
                        'xaxis': {'type': 'combination'},
                        'catagories': categories
                    }
                    response = py.plot([electronic, classical], layout=layout)
                    print response['url']
                    electronic_y = []
                    classical_y = []
                    categories = []


if __name__ == '__main__':
    main()
