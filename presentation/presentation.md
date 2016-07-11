`Pytest` desde las trincheras
=============================

Pau Ruŀlan Ferragut

pau@rullan.cat + prullan@apsl.net

CreantBits «Estiu 2016» - 15/7/2016

Note: EuroPython 2016 - Bilbao 19/7/2016



Cómo usar pytest para cosas que no nos vienen a la cabeza usar un framework de
testing.



Recreación de batallitas con Pytest

![pytest](logos/pytest.png)



Trabajo en APSL como sysadmin

(lo que en _cool_ hoy en día llaman `SRE` o

_ingeniero de fiabilidad_)



![Shameless plug](memes/shameless_plug.png)


En APSL siempre buscamos talento así que…

![apsl](logos/apsl.svg)


puedes venir a disfrutar de los infitos días de sol de Mallorca

![sunny](memes/its_always_sunny_in_mallorca.jpg)


Py.test como gestor de tests unitarios



Paso más allá, utilidades de QA y sysadmin



# Caso 0: `filechecker`


Confirmar que un conjunto de ficheros sigue una nomenclatura de _código-numérico_nombre.extensión_

```
000_carga-verano-2016.sql
```


En lugar de hacer un script escribiremos tests con `py.test`.


El sistema de `assert` en `py.test` es muy _pythonico_ y nos permite alejarnos de escribir cosas como:

```python
self.assertEquals(x, y)
```

para poner:

```python
assert x % 2 == 0, "Expected even, found odd value"
```


De primeras el no tener `assertAlmostEqual` y toda la pandilla puede parecer un inconveniente pero el código será mucho más legible

```python
assertAlmostEqual(a, b)
```

```python
assert round(a-b, 7) == 0 	 
```


Además, sabe analizar los tipos primitivos de Python: compará diccionarios, listas y tuplas.

```python
def test_eq_dict(self):
>       assert {'a': 0, 'b': 1, 'c': 0} == {'a': 0, 'b': 2, 'd': 0}
E         Omitting 1 identical items, use -v to show
E         Differing items:
E         {'b': 1} != {'b': 2}
E         Left contains more items:
E         {'c': 0}
E         Right contains more items:
E         {'d': 0}
E         Use -v to get the f
```


Para estudiar los errores podemos solicitar más información de backtrace:

```bash
py.test --tb=long
```


O atacar directamente a los tests problemáticos:

```bash
py.test --exit-first
```

```bash
py.test --failed-first
```

```bash
py.test --last-failed
```


Podemos añadir un parámetro al `py.test` para indicar de qué directorio coger los ficheros.


Incorporamos en la misma batería de tests ejemplos y gestionamos los casos que SABEMOS que tienen que fallar con `xfail`.
Note: http://pytest.org/latest/skipping.html#skipping


`xfail`, como la mayoría de plugins o atributos de `py.test`, lo podemos indicar como decorador de la función o en el cuerpo.

```Python
@pytest.mark.xfail("Won't work!", strict=True)
def f(x):
  pass
```

```Python
def f(x):
  if x > 1:
    pytest.mark.xfail(strict=True)
```



Podemos mirar que estén en `utf-8`.

Aquí empieza a brillar el hecho que usemos Python para probar cosas: nada de usar `bash` y `file`.


Mejor usar magia.

```python
with magic.Magic(flags=magic.MAGIC_MIME_ENCODING) as m:
    try:
        encoding = m.id_filename(checkfile)
    except magic.MagicError:
        assert False, "Could not decode file"
assert encoding == "utf-8"
```


Además, verificar que no contiene saltos de línia Mac también será un plis.

```python
with open(checkfile) as f:
    assert "\r" not in f.read()
```


Ahora queremos poner un lazo bonito sobre nuestros tests. Si no nos gusta el pintado por defecto `pip install pytest-colordots`

```
$ py.test
test_files.py .x...
```

```
$ py.test -v
test_files.py::test_utf8[./000_1234_any-extension.xXx] PASSED
test_files.py::test_utf8[./010_0000_empty.tab] xfail
test_files.py::test_macos_eol[./000_1234_any-extension.xXx] PASSED
test_files.py::test_macos_eol[./010_0000_empty.tab] PASSED
test_files.py::test_filenames_extensions[./000_1234_any-extension.xXx] PASSED
test_files.py::test_filenames_extensions[./010_0000_empty.tab] PASSED
```
Note: https://pypi.python.org/pypi/pytest-colordots



O más bonito todavía, con `sugar`

```
$ py.test -v
f_utf8[./000_1234_any-extension.xXx] ✓                   4% ▍         
f_utf8[./010_0000_empty.tab] x                           7% ▊     
[...]
f_filenames_extensions[./000_1234_any-extension.xXx] ✓  70% ███████▏  
f_filenames_extensions[./645_0000_invalid-code.sql] x  100% ██████████

Results (0.15s):
      17 passed
      10 xfailed
```
Note: https://github.com/Frozenball/pytest-sugar



# Caso 1: calidad mínima de código


Un truco para forzar a nuestros programadores a seguir un estilo de código es que EL PROPIO CÓDIGO sea un test.
Note:
https://pypi.python.org/pypi/pytest-flake8
https://github.com/carsongee/pytest-pylint


```
pip install pytest-flake8
```

```
# content of setup.cfg
[pytest]
flake8-max-line-length = 99
```


```
$ py.test -v --flake8
― FLAKE8-check ―
conftest.py:4:1: F401 'glob' imported but unused
conftest.py:10:1: E302 expected 2 blank lines, found 1
conftest.py:17:1: E302 expected 2 blank lines, found 1
conftest.py:20:5: E265 block comment should start with '# '
conftest.pyFLAKE8-check ⨯   3% ▍         

― FLAKE8-check ―
test_files.py:42:1: E302 expected 2 blank lines, found 1
test_files.py:90:1: E302 expected 2 blank lines, found 0
test_files.py:112:12: E127 continuation line…
test_files.pyFLAKE8-check ⨯
```


# Caso 2: generador configuraciones kubernetes


Verificador de yaml para un deploy kubernetes



http://pytest.org/latest/fixture.html#fixture

Los fixtures pytest son mucho más flexibles y potentes que los típicos de xUnit. Tienen nombres explícitos y basta usarlos como parámetros en las funciones para utilizarlos.

Así, los fixtures se comportan como un un _inyector de dependencias_ y son los propios tests que consumen el resultado.

Los fixtures pueden incluír finalizadores (código _teardown_) no solamente para ampliar la depuración sinó para mejorar el uso de recursos (p.ej: cerrar conexiones de bbdd).

```
request.addfinalizer(fin)
```

Vamos a renderizar el template en un fichero temporal por que queremos verificarlo a nivel de yaml. Para ello, usaremos el fixture `tmpfile`


Además, como los fixtures son funciones normales y corrientes, pueden llamar a otros fixtures.



Con los fixtures `py.test` tenemos un potentísimo sistema de inyección de dependencias.


Note: http://pytest.org/latest/tmpdir.html#tmpdir-handling
Note: tmpdir per crear els fitxers yaml del k8s


# Caso 3: `mariano20`


Mariano era un jefe que tuve al que le encantaba hacer de nagios humano.

![mariano](memes/mariano.jpg)


Para hacer que su família pudiera disfrutar de él lo robotizamos e hicimos el «Mariano 2.0» o `mariano20`

![mariano-robot](memes/mariano-robot.jpg)


En realidad es un scraping dinámico que lee de un fichero de configuración las páginas que tienen que existir.



Sincronización de las secciones principales de una web.



Podemos especificar en un yaml qué menús esperamos encontrar. Generaremos un fallo en caso que no sean exactamente esos.



Parametrizamos el test para poder mirar a todos nuestros países.



Y lo ponemos en paralelo: `xdist`
Note: https://pypi.python.org/pypi/pytest-xdist

```
pip install pytest-xdist
```

e indicamos el número de procesos a crear (o auto):

```
py.test -n auto
```


¿Qué queremos averiguar qué tests son los más lentos?

```
py.test --durations=5
```


Algunas veces tenemos problemas de red; don't panic! Tenemos `flaky` para los tests _poco fiables_.



Los tests se pueden filtrar.

La manera más fácil es identificandolo:

```
py.test modulo.clase::funcion
```

pero también lo podemos hacer filtrando con strings:

```
py.test -k "cart and logged"
```


Separaremos los distintos tests en agrupaciones el `pytest.mark`. Esto nos permite filtrar por ejemplo según línia de negocio.
Note: http://pytest.org/latest/example/markers.html

```python
@pytest.mark.premium
```

```
py.test --markers
py.test -m premium
```




Usaremos la salida XML del `jUnit` para guardar el estado.


Lo metemos en un job periódico de jenkins y listos.



![thats-all](memes/that-s-all-folks.jpg)


![no-questions](memes/no-questions.png)


TODO:

1. behaviour driven development amb bdd rollo cucumber
pytest cucumber behaviour driven development
https://github.com/pytest-dev/pytest-bdd
2. quickcheck
https://pypi.python.org/pypi/pytest-quickcheck
