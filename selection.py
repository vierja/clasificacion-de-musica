import random

ROULETTE_WHEEL_SELECTION = 1


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
    """
    sum_fitness = 0
    for rule in list_of_rules:
        sum_fitness += rule['fitness']

    # El algoritmo no esta optimizado. Se podria calcular directamente
    # en el rango que cae.
    selected_rules = []
    while len(selected_rules) < num_select:
        pick = random.uniform(0, sum_fitness)
        current = 0
        for rule in list_of_rules:
            current += rule['fitness']
            if current > pick:
                selected_rules.append(rule)
                break

    return selected_rules
