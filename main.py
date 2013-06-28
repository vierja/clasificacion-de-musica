# -*- coding: utf-8 -*-
import argparse
from classifier import Classifier


def main():
    parser = argparse.ArgumentParser(description='Clasificador de musica.\nToma los datos de entrenamiento de un archivo y utiliza algoritmos evolutivos para crear y mejorar las reglas de clasificación.')
    parser.add_argument('-d', '--data', help='Archivo donde se encuentra la información fuente para el clasificador.')
    parser.add_argument('-o', '--output', help='Archivo donde guardar las reglas si es que se quiere persistir.')
    parser.add_argument('-i', '--input', help='Archivo de reglas persistidas para cargar.')
    args = vars(parser.parse_args())

    classifier = Classifier(args['data'])
    final_fitness = classifier.train()
    print "Training ended\nFinal fitness:", final_fitness

if __name__ == '__main__':
    main()
