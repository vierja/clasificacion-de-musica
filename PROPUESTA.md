# Clasificación de Música
 
> Javier Rey

> María Noel Quiñones

> Facultad de Ingeniería, Universidad de la República

> Montevideo, Uruguay

> {javirey, manoqui23}@gmail.com


 
## I.   DESCRIPCIÓN DEL PROBLEMA
El proyecto consiste en la formulación y entrenamiento de una función de clasificación de sonidos (en específico música) utilizando algoritmos evolutivos.

A partir de un conjunto de datos conocidos, sus respectivas propiedades y su clasificación conocida de antemano, se desea crear y entrenar una función de clasificación que pueda clasificar con un alto porcentaje de éxito los sonidos.

## II. JUSTIFICACIÓN DE USAR AE’S

La clasificación de música es un problema de clasificación muy complejo, ya que cada canción tiene muchas dimensiones.

En estos casos suele usarse métodos de aprendizaje automático para tratar de darle estructura al gran número de dimensiones. Específicamente dentro del área de aprendizaje automático existe lo que se llaman Learning Classifying Systems (LCS) [1] [2]. Los LCS trabajan dentro del esquema de reinforcement learning, dentro del cual la soluciones con comportamiento deseado son fomentadas. Esto se realiza utilizando AEs.

Los AEs sirven como método para darle sentido a los datos o dimensiones de lo que se quiere clasificar sin saber nada de estos.

## III.  ESTRATEGIA DE RESOLUCIÓN

Se va a desarrollar un LCS,  del tipo Pittsburgh [3] donde se tiene una población de sets de reglas separadas de largo variable, y el algoritmo evolutivo se encarga de encontrar el set óptimo de reglas para la clasificación.

### A.  Propiedades del sonido a tener en cuenta

El conjunto de propiedades a tomar en cuenta para la clasificación es el SLL feature vector [4], comúnmente utilizado en proyectos relacionados. Este consiste en las siguientes propiedades:
- root-meansquare (RMS) level
- spectral centroid
- bandwidth
- zero-crossing rate
- spectral roll-off frequency
- band energy ratio
- delta spectrum magnitude
- pitch
- pitch strength

Para esto se va a utilizar la librería LibXtrack [5].

### B.  Clasificaciones posibles

Para la clasificación se van a tomar en cuenta distintos géneros de música (Pop, Rock, Clasica, Electronica, etc). Se quiere llegar a un clasificador, que dada una canción, devuelva a qué géneros pertenece.

### C.  Representación de la solución

Al trabajar sobre un problema con atributos con valor real, se necesita un algoritmo de discretización para manejar las posibles soluciones.

La solución se representa como un set de reglas usando Adaptative Discretization Intervals (ADI) [6][7]. Cada regla consiste de dos partes, una condición y una decisión.

Cada condición es un predicado Conjunctive Normal Form (CNF) definido como:

((A1 = V11 ˅ … ˅ A1 = V1m ) ˄…˄ (An= V2n ˅ … ˅ An = Vbm ))

Donde Ai es el atributo i del problema (por ejemplo bandwidth) y Vij el valor j que puede tomar el atributo i.

Este predicado, en problemas discretos, se puede representar de forma binaria de la sigueinte manera. Si tenemos dos atributos que pueden tomar los valores {1,2,3}, una regla del tipo “si el atributo 1 tiene valor 1 o 2 y el atributo 2 tiene valor 3 entonces es de clase 1” se representa como 110|001|1.

Al trabajar con valores reales, se separan los posibles valores de los atributos en micro-intervalos.  

Para cada regla del set, se tiene una condición por cada atributo posible. Este se encuentra dividido en micro-intervalos con un estado asignado. Si el estado del micro-intervalo es 1, entonces si el valor del atributo cae en el micro-intervalo, la condición se cumple. Si el estado es 0, entonces no.
 
Figura 1. Representación de un Set de reglas.

### D.  Función de fitness

La función de fitness para cada regla del conjunto de reglas está dada por el % de clasificaciones correctas sobre el conjunto de datos de entrenamiento.

### E.  Operadores

Los operadores que utilizaremos es el cruzamiento y la mutación (dentro de este el split y merge).

En el cruzamiento los puntos de corte del operador de cruzamiento sólo se llevará a cabo en los límites del atributo, no entre los intervalos. Esta restricción se lleva a cabo con el fin de mantener la corrección semántica de las reglas.

En la mutación, cuando se separa un intervalo, se selecciona un punto al azar de los micro-intervalos para hacer el corte.

Luego cuando se fusiona dos intervalos, el estado resultante (1 o 0) del intervalo se toma del que tiene más micro-intervalos. Si los dos tienen la misma cantidad de micro-intervalos, el valor del estado se elige al azar.
 
Figura 2. Operadores Split y Merge.

## IV. PROPUESTA DE EVALUACIÓN EXPERIMENTAL

### A.  Datos sobre los cuales trabajar

Para tener entrenar un clasificador de forma eficiente se necesitan datos ya clasificados, y variados.

La Universidad de Columbia tiene un programa llamado Million Song Dataset [8] en el cual ofrecen más de 200 GB de música contemporánea ya clasificada. Para este proyecto vamos a utilizar un subset de estos datos de 1.8 GB el cual consiste en 10.000 canciones.

Este set lo vamos a dividir en dos partes, una parte para entrenar al clasificador, y la otra para validarlo. 

### B.  Implementación

La idea es desarrollar el clasificador en el lenguaje de programación Python para poder prototipar de manera rápida y poder identificar e iterar sobre problemas rápidamente.


## REFERENCIAS

- [1] http://en.wikipedia.org/wiki/Learning_classifier_system.
- [2] Dr. J. Bacardit, Dr. N. Krasnogor, “Introduction to Learning Classifier Systems”.
- [3] Jaume Bacardit, Josep Maria Garrell R. Nicole, “Evolving Multiple Discretizations with Adaptive Intervals for a Pittsburgh Rule-Based Learning Classiﬁer System”.
- [4] Martin F. McKinney, Jeroen Breebart, “Feature Audio and  Music Clasiffication”, Philips Research Laboratories.
- [5] https://github.com/jamiebullock/LibXtract.
- [6] Jaume Bacardit, Josep Maria Garrell, ”Evolving Multiple Discretizations with Adaptive Intervals for a Pittsburgh Rule-Based Learning  Classiﬁer System”, Intelligent Systems Research Group.
- [7] Jaume Bacardit, Josep Maria Garrell, Analysis and improvements of the Adaptive Discretization Intervals knowledge representation.
- [8] http://labrosa.ee.columbia.edu/millionsong/

 

