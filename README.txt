Entrenamiento y prueba de clasificacion
=======================================

Para probar clasificador se necesita tener instalado:
    - numpy
    - plotly

Es recomendable correrlo con PyPy en vez de Python.
Para correrlo teniendo un archivo de entranamiento 'train.csv' se debe hacer:

    pypy main.py -d train.csv

Si se quiere modificar las variables del algoritmo evolutivo se debe realizar
dentro del programa 'main.py'


Generacion de archivos de entrenamiento
=======================================

Para generar archivos de entrenamiento se debe de tener instalado Yaafe
y correr 'extract_features.py' de la siguiente manera:

    python extract_features.py -i songs/ -o train.csv

donde 'songs/' es el directorio donde se encuentran las canciones y 'train.csv' 
el output (y entrada para el clasificador).

