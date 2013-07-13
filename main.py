# -*- coding: utf-8 -*-
import argparse
from classifier import Classifier


def main():
    parser = argparse.ArgumentParser(description='Clasificador de musica.\nToma los datos de entrenamiento de un archivo y utiliza algoritmos evolutivos para crear y mejorar las reglas de clasificación.')
    parser.add_argument('-d', '--data', help='Archivo donde se encuentra la información fuente para el clasificador.')
    parser.add_argument('-o', '--output', help='Archivo donde guardar las reglas si es que se quiere persistir.')
    parser.add_argument('-i', '--input', help='Archivo de reglas persistidas para cargar.')
    args = vars(parser.parse_args())

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
        print "Option num:", num, ", val:" , options
        classifier = Classifier(args['data'], discrete_intervals=options[0], size_rule_generation=options[1])
        final_fitness = classifier.train(req_min_fitness=options[2], gen_select=options[3], limit_generations=options[4])
        print "Training ended\nFinal fitness:", final_fitness

if __name__ == '__main__':
    main()
