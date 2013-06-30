# -*- coding: utf-8 -*-
import random

ROULETTE_WHEEL_SELECTION = 1
RANK_SELECTION = 2
TOURNAMENT_SELECTION = 3


def roulette_wheel_selection(list_of_rules, num_select):
    """
    Seleccion de reglas utilizando tecnica de roulette wheel selection.
    Se elige un numero entre 0 y la suma de todos los fitness combinados
    y se elige la regla tal que el numero 'caiga' de esta.

    0       0.6   0.9          1.9     2.4            sum_fitness
    | ------ | --- | ---------- | ----- | ----------------|
        r1     r2        r3         r4           r5
    pick = 1.3
                        ^
                        |
                       pick
    selected_rule = r3

    La seleccion se repite hasta tener `num_select` reglas.
    Cada regla se le agrega 0.2 de fitness para poder ser seleccionada
    aunque falle.
    """
    sum_fitness = 0
    for rule in list_of_rules:
        sum_fitness += rule['fitness'][0] + 0.05

    # El algoritmo no esta optimizado. Se podria calcular directamente
    # en el rango que cae.
    # Tambien actualmente permite que se elija dos veces la misma regla
    # no se si esto esta permitido.
    selected_rules = []
    picks = []
    while len(selected_rules) < num_select:
        pick = random.uniform(0, sum_fitness)
        picks.append(pick)
        current = 0
        for rule in list_of_rules:
            current += rule['fitness'][0] + 0.05
            if current > pick:
                selected_rules.append(rule)
                break

    # print "list_of_rules", [rule['fitness'] for rule in list_of_rules]
    # print "sum_fitness", sum_fitness
    # print "picks", picks
    # print "selected_rules:", [rule['fitness'] for rule in selected_rules]
    return selected_rules


def rank_selection(list_of_rules, num_select):
    """
    Seleccion de reglas utilizando tecnica de rank selection.
    Se ordenan las reglas segun su valor de fitness
    y se seleccionan las mejores 'num_select'.
    """
    selected_rules = []
    # Ordeno primero las reglas por su valor de fitness
    order_rules = sorted(list_of_rules, key=lambda rule: rule['fitness'], reverse=True)
    # Selecciono las mejores 'num_select'
    selected_rules = order_rules[:num_select]

    return selected_rules


# Para el tournament selection se necesitan 2 parametros. Cambiar luego _select_rules en classifier.py
def tournament_selection(list_of_rules, num_rules, num_select):
    """
    Seleccion de reglas utilizando tecnica de tournament selection.
    Se eligen 'num_rules' reglas y se seleccionan las mejores 'num_select'.
    """
    selected_rules = []
    for i in range(num_rules):
        # Selecciono aleatoriamente una regla dentro de la lista de reglas
        index = random.randint(0, len(list_of_rules)-1)

        # Si la regla ya esta seleccionada entonces sigo buscando otra
        while list_of_rules(index) in selected_rules:
            index = random.randint(0, len(list_of_rules)-1)

        # Agrego la regla seleccionada
        selected_rules.append(list_of_rules(index))

    # Ordeno las reglas y selecciono las mejores 'num_select'
    rank_selection(selected_rules, num_select)
