# Preguntas frecuentes sobre Python

Documento base del agente de nivel 1. Cubre Python básico e intermedio.
Cada pregunta es un encabezado de nivel 2 (`##`) seguido de su respuesta.

## ¿Qué es Python?
Python es un lenguaje de programación interpretado, de alto nivel y de propósito
general. Destaca por su sintaxis legible, su tipado dinámico y su gran ecosistema
de librerías. Se usa en desarrollo web, ciencia de datos, automatización,
scripting e inteligencia artificial.

## ¿Cómo imprimo algo por pantalla en Python?
Con la función `print()`. Por ejemplo: `print("Hola, mundo")`. Acepta varios
argumentos separados por comas y los une con un espacio: `print("a", "b")` imprime
`a b`.

## ¿Cómo declaro una variable?
Basta con asignar un valor con `=`, sin declarar el tipo: `x = 10` o
`nombre = "Ana"`. Python infiere el tipo automáticamente (tipado dinámico).

## ¿Cuáles son los tipos de datos básicos en Python?
Los principales son: `int` (enteros), `float` (decimales), `str` (cadenas de
texto), `bool` (`True`/`False`) y `None` (ausencia de valor). Los contenedores
más comunes son `list`, `tuple`, `dict` y `set`.

## ¿Qué diferencia hay entre una lista y una tupla?
Una lista (`list`) es mutable: puedes añadir, quitar o cambiar elementos. Una
tupla (`tuple`) es inmutable: una vez creada no se puede modificar. Las listas se
escriben con corchetes `[1, 2, 3]` y las tuplas con paréntesis `(1, 2, 3)`.

## ¿Cómo creo una lista y añado elementos?
Se crea con corchetes: `numeros = [1, 2, 3]`. Para añadir al final se usa
`.append(valor)`, para insertar en una posición `.insert(indice, valor)` y para
extender con otra lista `.extend(otra_lista)`.

## ¿Cómo accedo a elementos de una lista por índice?
Los índices empiezan en 0: `lista[0]` es el primer elemento. Los índices
negativos cuentan desde el final: `lista[-1]` es el último. Acceder a un índice
fuera de rango lanza `IndexError`.

## ¿Qué es el slicing (rebanado) de listas?
Permite obtener una sublista con la sintaxis `lista[inicio:fin:paso]`. Por
ejemplo `lista[1:4]` toma del índice 1 al 3, `lista[::2]` toma uno de cada dos y
`lista[::-1]` invierte la lista.

## ¿Qué es un diccionario y cómo se usa?
Un diccionario (`dict`) almacena pares clave-valor: `persona = {"nombre": "Ana", "edad": 30}`.
Se accede con `persona["nombre"]`. Para evitar errores si la clave no existe se
usa `persona.get("nombre", valor_por_defecto)`.

## ¿Cómo recorro un diccionario?
Con un bucle `for`. `for clave in d:` recorre las claves; `for valor in d.values():`
los valores; y `for clave, valor in d.items():` ambos a la vez.

## ¿Qué es un conjunto (set) en Python?
Un `set` es una colección no ordenada de elementos únicos: `s = {1, 2, 3}`. No
admite duplicados y es ideal para eliminar repetidos de una lista con `set(lista)`
o para operaciones de conjuntos (unión `|`, intersección `&`, diferencia `-`).

## ¿Cómo escribo una condición if/elif/else?
```python
if edad >= 18:
    print("Mayor de edad")
elif edad >= 13:
    print("Adolescente")
else:
    print("Niño")
```
La indentación (normalmente 4 espacios) delimita el bloque.

## ¿Cómo funciona un bucle for?
Recorre los elementos de un iterable: `for elemento in lista:`. Para iterar sobre
un rango de números se usa `range`: `for i in range(5):` recorre del 0 al 4.

## ¿Cómo funciona un bucle while?
Repite el bloque mientras la condición sea verdadera:
```python
i = 0
while i < 5:
    print(i)
    i += 1
```
Hay que asegurarse de que la condición acabe siendo falsa para evitar bucles
infinitos.

## ¿Para qué sirven break y continue?
`break` sale inmediatamente del bucle. `continue` salta a la siguiente iteración
sin ejecutar el resto del bloque. Ambos se usan dentro de `for` y `while`.

## ¿Qué hace la función range()?
Genera una secuencia de números. `range(5)` produce 0,1,2,3,4; `range(2, 8)`
produce de 2 a 7; y `range(0, 10, 2)` produce 0,2,4,6,8 (con paso 2).

## ¿Cómo defino una función?
Con la palabra clave `def`:
```python
def saludar(nombre):
    return f"Hola, {nombre}"
```
Se llama con `saludar("Ana")`. El valor se devuelve con `return`.

## ¿Qué son los argumentos por defecto en una función?
Son valores que toma un parámetro si no se le pasa uno: `def saludar(nombre="amigo"):`.
Así `saludar()` devuelve "Hola, amigo" y `saludar("Ana")` devuelve "Hola, Ana".

## ¿Qué son *args y **kwargs?
`*args` recoge un número variable de argumentos posicionales en una tupla.
`**kwargs` recoge argumentos con nombre en un diccionario. Permiten funciones
flexibles: `def f(*args, **kwargs):`.

## ¿Qué es una f-string?
Es una forma cómoda de formatear cadenas usando el prefijo `f` y llaves:
`f"Hola {nombre}, tienes {edad} años"`. Las expresiones dentro de `{}` se evalúan
en el momento.

## ¿Cómo concateno cadenas de texto?
Con el operador `+`: `"Hola " + "mundo"`. Para unir una lista de cadenas se usa
`" ".join(lista)`. Para insertar valores es preferible usar f-strings.

## ¿Cómo convierto entre tipos (casting)?
Con las funciones constructoras: `int("42")` convierte texto a entero,
`str(42)` entero a texto, `float("3.14")` texto a decimal y `list("abc")` a una
lista de caracteres.

## ¿Qué métodos útiles tienen las cadenas de texto?
Algunos comunes: `.upper()`, `.lower()`, `.strip()` (quita espacios), `.split()`
(divide en lista), `.replace(viejo, nuevo)`, `.startswith()`, `.endswith()` y
`.find()`.

## ¿Qué es una list comprehension (lista por comprensión)?
Es una forma concisa de crear listas: `[x * 2 for x in range(5)]` produce
`[0, 2, 4, 6, 8]`. Admite condiciones: `[x for x in numeros if x % 2 == 0]` filtra
los pares.

## ¿Cómo manejo errores con try/except?
```python
try:
    resultado = 10 / 0
except ZeroDivisionError:
    print("No se puede dividir por cero")
```
Puedes capturar varias excepciones y usar `finally` para código que siempre se
ejecuta.

## ¿Qué es una excepción y cómo la lanzo manualmente?
Una excepción señala un error en tiempo de ejecución. Se lanza con `raise`:
`raise ValueError("dato no válido")`. Se pueden definir excepciones propias
heredando de `Exception`.

## ¿Cómo leo un archivo de texto?
Con `open` dentro de un bloque `with`, que cierra el fichero automáticamente:
```python
with open("datos.txt", "r", encoding="utf-8") as f:
    contenido = f.read()
```

## ¿Cómo escribo en un archivo?
Abriéndolo en modo escritura `"w"` (sobrescribe) o `"a"` (añade al final):
```python
with open("salida.txt", "w", encoding="utf-8") as f:
    f.write("una línea\n")
```

## ¿Qué es un módulo y cómo lo importo?
Un módulo es un fichero `.py` con código reutilizable. Se importa con `import math`
y se usa con `math.sqrt(9)`. También `from math import sqrt` para importar solo lo
necesario.

## ¿Qué es pip?
Es el gestor de paquetes de Python. Instala librerías del Python Package Index
(PyPI) con `pip install nombre_paquete`. Para listar lo instalado: `pip list`.

## ¿Qué es un entorno virtual y por qué usarlo?
Es un Python aislado por proyecto, para que las dependencias de un proyecto no
afecten a otros. Se crea con `python -m venv .venv` y se activa antes de instalar
paquetes. Aísla versiones y evita conflictos.

## ¿Qué es requirements.txt?
Es un fichero que lista las dependencias del proyecto, una por línea, con su
versión. Se instala todo con `pip install -r requirements.txt` y se genera con
`pip freeze > requirements.txt`.

## ¿Cuál es la diferencia entre == e is?
`==` compara si dos valores son iguales. `is` compara si dos variables apuntan al
mismo objeto en memoria. Para comparar con `None` se usa siempre `is`:
`if x is None:`.

## ¿Qué significa que None sea un valor?
`None` representa la ausencia de valor. Es lo que devuelve una función sin
`return` explícito. Se comprueba con `if variable is None:`.

## ¿Cómo compruebo el tipo de una variable?
Con `type(x)` para obtener el tipo, o con `isinstance(x, int)` para comprobar si
es de un tipo concreto (preferible, porque respeta la herencia).

## ¿Qué hace la función len()?
Devuelve el número de elementos de una secuencia o contenedor: `len("hola")` es 4,
`len([1, 2, 3])` es 3 y `len({"a": 1})` es 1.

## ¿Cómo ordeno una lista?
`lista.sort()` la ordena en el sitio (modifica la lista). `sorted(lista)` devuelve
una nueva lista ordenada sin tocar la original. Ambas aceptan `reverse=True` y un
parámetro `key`.

## ¿Qué hacen las funciones enumerate() y zip()?
`enumerate(lista)` devuelve pares (índice, valor) al recorrer: útil en bucles.
`zip(a, b)` empareja elementos de varios iterables: `zip([1,2],[3,4])` da
`(1,3),(2,4)`.

## ¿Qué es una clase en Python?
Es una plantilla para crear objetos que agrupan datos (atributos) y comportamiento
(métodos):
```python
class Perro:
    def __init__(self, nombre):
        self.nombre = nombre
    def ladrar(self):
        return f"{self.nombre} dice guau"
```

## ¿Qué es el método __init__?
Es el constructor de la clase: se ejecuta al crear un objeto y sirve para
inicializar sus atributos. El primer parámetro siempre es `self`, que representa la
instancia.

## ¿Qué es self en una clase?
`self` es la referencia a la instancia actual del objeto. Permite acceder a sus
atributos y métodos desde dentro de la clase. Es el primer parámetro de los métodos
de instancia.

## ¿Qué es la herencia entre clases?
Permite que una clase (hija) reutilice y extienda otra (padre):
`class Gato(Animal):`. La hija hereda atributos y métodos del padre y puede añadir
los suyos o sobrescribirlos.

## ¿Cómo escribo un comentario en Python?
Una línea que empieza por `#` es un comentario y se ignora al ejecutar. Para texto
de varias líneas se suelen usar comillas triples `""" ... """`, habituales como
docstrings.

## ¿Qué es un docstring?
Es una cadena de documentación al principio de un módulo, función o clase, escrita
con comillas triples. Describe qué hace el objeto y se accede con `help()` o el
atributo `.__doc__`.

## ¿Para qué sirve if __name__ == "__main__"?
Permite que un bloque de código se ejecute solo cuando el fichero se corre
directamente, y no cuando se importa como módulo. Es el patrón habitual para el
punto de entrada de un script.

## ¿Cómo genero números aleatorios?
Con el módulo `random`: `random.randint(1, 6)` da un entero entre 1 y 6,
`random.choice(lista)` elige un elemento al azar y `random.random()` da un decimal
entre 0 y 1.

## ¿Cómo trabajo con fechas y horas?
Con el módulo `datetime`: `datetime.now()` da la fecha y hora actual,
`datetime(2025, 1, 1)` crea una fecha concreta y `.strftime("%d/%m/%Y")` la
formatea como texto.

## ¿Qué es la indentación y por qué importa en Python?
La indentación (sangría) define los bloques de código en lugar de llaves. Es
obligatoria y debe ser consistente (lo habitual son 4 espacios). Una indentación
incorrecta provoca `IndentationError`.

## ¿Qué es PEP 8?
Es la guía de estilo oficial de Python: recomienda 4 espacios de indentación,
nombres en `snake_case` para funciones y variables, líneas de hasta 79 caracteres
y otras convenciones para escribir código legible.

## ¿Cómo depuro código en Python?
Lo más sencillo es añadir `print()` para inspeccionar valores. Para algo más
potente está el depurador `pdb` (`import pdb; pdb.set_trace()`) o el depurador
integrado del editor, que permite poner puntos de interrupción.
