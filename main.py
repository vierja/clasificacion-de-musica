# -*- coding: utf-8 -*-
import argparse
import itertools
import plotly
from classifier import Classifier


def main():
    parser = argparse.ArgumentParser(description='Clasificador de musica.\nToma los datos de entrenamiento de un archivo y utiliza algoritmos evolutivos para crear y mejorar las reglas de clasificación.')
    parser.add_argument('-d', '--data', help='Archivo donde se encuentra la información fuente para el clasificador.')
    parser.add_argument('-o', '--output', help='Archivo donde guardar las reglas si es que se quiere persistir.')
    parser.add_argument('-i', '--input', help='Archivo de reglas persistidas para cargar.')
    args = vars(parser.parse_args())

    #test_combinations(args)

    #return
    options = [
        [100, 10, 0.9, 4, 10000],  # discrete_intervals, size_rule_generation, req_min_fitness, gen_select, limit_generations
        [1000, 10, 0.9, 4, 10000],
        [100, 20, 0.9, 4, 10000],
        [100, 5, 0.9, 2, 10000],
        [100, 10, 0.9, 2, 10000],
        [100, 10, 0.9, 6, 10000],
        [200, 50, 0.9, 10, 10000]
    ]

    for num, options in enumerate(options):
        print "Option num:", num, ", val:", options
        classifier = Classifier(args['data'], discrete_intervals=options[0], size_rule_generation=options[1], filter_list=["skewness", "spectral_rolloff", "energy", "sv", "spread", "centroid", "obsi", "kurtosis"])
        final_fitness = classifier.train(req_min_fitness=options[2], gen_select=options[3], limit_generations=options[4])
        print "Testing"
        classifier.test()
        # classifier.guess_genre([7.53659769442,1389.49121537,0.0166588959174,0.355062895642,1480.75635175,769.172547276,3.47303203307,69.8220939453])
        print "Training ended\nFinal fitness:", final_fitness


def test_combinations(args):
    py = plotly.plotly(username='vierja', key='uzkqabvlzm', verbose=False)
    options = [100, 20, 0.9, 4, 10000]
    features = ["skewness", "spectral_rolloff", "energy", "sv", "spread", "centroid", "zcr", "obsi", "kurtosis"]
    electronic_y = []
    classical_y = []
    categories = []

    for i in range(2, len(features) + 1):
        combinations = [list(comb) for comb in itertools.combinations(features, i)]
        for comb in combinations:
            comb_name = ', '.join(comb)
            classifier = Classifier(args['data'], discrete_intervals=options[0], size_rule_generation=options[1], filter_list=comb)
            top_fitness = classifier.train(req_min_fitness=options[2], gen_select=options[3], limit_generations=options[4])
            print "Training ended\nFinal fitness:", top_fitness
            electronic_y.append(top_fitness['electronic'])
            classical_y.append(top_fitness['classical'])
            categories.append(comb_name)

            if len(categories) > 20:
                electronic = {
                    "name": "Electronic",
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
