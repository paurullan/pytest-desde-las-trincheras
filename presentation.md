`Pytest` desde las trincheras
=============================

Pau Ruŀlan Ferragut

pau@rullan.cat + prullan@apsl.net

CreantBits «Estiu 2016» - 15/7/2016

Note: EuroPython 2016 - Bilbao 19/7/2016


Cómo usar pytest para cosas que no nos vienen a la cabeza al
usar un framework de testing.


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


Py.test como herramienta de QA o sysadmin

y no como gestor de tests unitarios.


# Caso 0: estándares de estilo


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


De esta manera eliminamos git.hooks y preprocesadores para convertir nuestras
reglas de estilo de código en tests.



Usaremos la salida XML del `jUnit` para guardar el estado.

```
py.test --junit-xml=path.xml
```


Así Jenkins _entiende_ que estamos pasando tests.
```
jenkins  JUnit Attachments Plugin
```
![jenkins_a](images/test-result.png)


![jenkins_b](images/test-result-trend.png)


# Caso 1: mini scraper


Crearemos un pequeño script que arranque Selenium y con `assert` confirmaremos
si una variable es verdadero.

```python
assert req.ok
assert items > 3
```


Los *fixtures pytest* son mucho más flexibles y potentes que los típicos de xUnit.

Tienen nombres explícitos y basta usarlos como parámetros en las funciones para utilizarlos.

```python
def test_file(tmpdir):
    pass
```


Así, los fixtures se comportan como un un _inyector de dependencias_ y son los propios tests que consumen el resultado.


Selenium es una maravilla y podemos

rápidamente integrarlo con `py.test`

```
pip install pytest-splinter
```


Explotaremos los fixtures que nos proporciona `splinter` para accedir al navegador
y hacer nuestro fixture de login

```python
# conftest.py
import pytest

@pytest.fixture
def login(browser):
    browser.visit('http://site-demo.apsl.net/')
    browser.fill('username', 'user')
    browser.fill('password', 'SUPERSECRET')
    browser.find_by_css('#submit-id-submit').click()
```


```python
def test_add_item(browser, login):
    browser.fill('slug', 'test')
    browser.find_by_css('input#submit').click()
    assert browser.find_by_css('tr td')[0] == 'test'

    with browser.get_iframe(0) as iframe:
        iframe.find_by_css('button').click()

    assert not browser.find_by_css('tr td')
```


Lo que si podemos hacer es usar `ipdb` cuando lo necesitemos:

```python
def test_add_item(browser, login):
    …
    import ipdb; ipdb.set_trace()
    …
```

```
py.test -s      #  shortcut for --capture=no.
```


# Caso 2: generador configuraciones kubernetes


Verificador de yaml para un deploy kubernetes.

En el propio código que gestiona los templates comprobaremos que los ficheros
generados son correctos.


Vamos a renderizar el template en un fichero temporal por que queremos
verificarlo a nivel de yaml.

Explotaremos cosas como la librería `sh`

```python
from sh import envtpl, yamllint
envtpl = envtpl.bake(keep_template=True)
```


Usaremos el fixture `tmpdir`.

```python
@pytest.yield_fixture
def tmpfile(tmpdir):
    yield tmpdir + "test.yaml"
```


```python
@pytest.mark.parametrize("app, component", \
                         itertools.product(APPS, COMPONENTS))
def test_yamls(app, component, tmpfile):
    infile = "apps/app-{component}.yaml.tpl".format(
        app=app, component=component
    )
    envtpl(infile, o=tmpfile, _env={…},  )
    yamllint(tmpfile)
```


```
$ py.test -v
collected 30 items
test_yamls.py::test_yamls[web-deployment] PASSED
test_yamls.py::test_yamls[web-hpa] PASSED
test_yamls.py::test_yamls[web-svc] PASSED
test_yamls.py::test_yamls[web-varnish-svc] PASSED

test_yamls.py::test_yamls[nginx-deployment] PASSED
…
```



# Caso 3: `mariano20`


Mariano era un jefe que tuve al que le encantaba hacer de nagios humano.

![mariano](memes/mariano.jpg)


Para ayudar a que su família pudiera disfrutar de él lo robotizamos e hicimos el «Mariano 2.0» o `mariano20`

![mariano-robot](memes/mariano-robot.jpg)


En realidad es un scraping que lee de un fichero de configuración las páginas que tienen que existir.

También verifica algunas redirecciones.


Podemos especificar en un yaml qué menús esperamos encontrar.
Generaremos un fallo en caso que no sean exactamente esos.

La web a monitorizar era multipaís: parametrizamos el test para poder mirar a todos
nuestros países.


```yaml
sites:
  ca:
    redirect: https://ca.wikipedia.org/wiki/Portada
    title: Viquipèdia
    today: mp-left

  de:
    redirect: https://de.wikipedia.org/wiki/Wikipedia:Hauptseite
    today: Artikel_des_Tages
    title: Wikipedia – Die freie Enzyklopädie
```


```
$ py.test -v mariano20.py
```


```python
import yaml

from collections import namedtuple
Site = namedtuple('Site', 'homepage redirect title today')
BASE_SITE = "https://{code}.wikipedia.org"

def load_sites():
    with open("sites.yaml") as f:
        params = yaml.load(f)
    for code, data in params['sites'].items():
        data['homepage'] = BASE_SITE.format(code=code)
        yield Site(**data)
```


```python
import pytest
import requests

@pytest.mark.parametrize("site", load_sites())
def test_site_redirect(site):
    r = requests.head(site.homepage, allow_redirects=True)
    assert r.ok
    assert len(r.history) == 1
    redirect, = r.history
    assert redirect.is_permanent_redirect
    assert r.url == site.redirect
```


```python
from bs4 import BeautifulSoup

@pytest.mark.parametrize("site", load_sites())
def test_home_today_article(site):
    r = requests.get(site.homepage)
    assert r.ok, "Could not load site"
    soup = BeautifulSoup(r.content, 'html.parser')
    assert site.title == soup.title.string
    assert soup.find(id=site.today)
```


```
$ py.test mariano20.py  -v
```


```
― test_home_today_article[de] ――
site = Site(title='Viquipèdia', today='Artikel_des_Tages',
  homepage='https://de.wikipedia.org',
  redirect='https://de.wikipedia.org/wiki/Wikipedia:Hauptseite')

    @pytest.mark.parametrize("site", load_sites())
    def test_home_today_article(site):
        r = requests.get(site.homepage)
        assert r.ok, "Could not load site"
        soup = BeautifulSoup(r.content, 'html.parser')
>       assert site.title == soup.title.string
E       assert 'Viquipèdia' == 'Wikipedia – Die freie Enzyklopädie'
E         - Viquipèdia
E         + Wikipedia – Die freie Enzyklopädie

mariano20.py:33: AssertionError
  mariano20.py ⨯    25% ██▌
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


El parámetro `--lf` nos ejecutará solamente
los tests que fallaron.

```
$ py.test mariano20.py --lf
run-last-failure: rerun last 2 failures
 mariano20.py ✓✓                              100% ██████████

Results (1.40s):
       2 passed
       6 deselected
 ```


En modo `-v` `py.test` indica qué casos estamos ejecutando para cada opción
del `parametrize`

```
 $ py.test -v mariano20.py

  mariano20.pytest_site_redirect[site0] ✓   12% █▍        
  mariano20.pytest_site_redirect[site1] ✓   25% ██▌       
  mariano20.pytest_site_redirect[site2] ✓   38% ███▊      
  mariano20.pytest_site_redirect[site3] ✓   50% █████     
```


El `parametrize` tiene una opción `ids` que nos permite hacer más claro
el listado de casos.

```python
Site = namedtuple('Site', 'homepage redirect title today code')
```

```
@pytest.mark.parametrize("site", load_sites(), ids=lambda s: s.code)
```


```
$ py.test mariano20.py  -v

 mariano20.pytest_site_redirect[de] ✓     12% █▍
 mariano20.pytest_site_redirect[en] ✓     25% ██▌
 mariano20.pytest_site_redirect[ca] ✓     38% ███▊
 mariano20.pytest_site_redirect[it] ✓     50% █████
 ```


Queremos probar el rendimiento de nuestro super nagios:

```
 $ time py.test mariano20.py
  mariano20.py ✓✓✓✓✓✓✓✓           100% ██████████

 Results (5.67s):
        8 passed

 real 0m6.085s
 user 0m1.348s
 sys  0m0.068s
 ```


Y lo ponemos en paralelo: `xdist`

```
pip install pytest-xdist
```

e indicamos el número de procesos a crear (o auto):

```
py.test -n auto
```
Note: https://pypi.python.org/pypi/pytest-xdist


```
$ time py.test mariano20.py  -n auto

 mariano20.py ✓✓✓✓✓✓✓✓      100% ██████████

Results (2.18s):
       8 passed

real 0m2.839s
user 0m4.208s
sys  0m0.316s
```


Cuidado con el xdist si generais dinámicamente los tests.

```
― ERROR collecting gw2 ―――――――――――――――――――――――――――――
Different tests were collected between gw3 and gw2.
The difference is:
--- gw3
+++ gw2

@@ -1,8 +1,8 @@
+mariano20.py::test_site_redirect[de]
-mariano20.py::test_site_redirect[en]
-mariano20.py::test_site_redirect[de]
-mariano20.py::test_site_redirect[ca]
```


El orden del parametrize debe de ser determinista

```python
for code, data in sorted(params['sites'].items()):
```



¿Qué queremos averiguar qué tests son los más lentos?

```
py.test --durations=8
```


```
== slowest 8 test durations ==
0.69s call     mariano20.py::test_home_today_article[it]
0.66s call     mariano20.py::test_home_today_article[ca]
0.66s call     mariano20.py::test_home_today_article[en]
0.61s call     mariano20.py::test_home_today_article[de]
0.49s call     mariano20.py::test_site_redirect[en]
0.47s call     mariano20.py::test_site_redirect[it]
0.45s call     mariano20.py::test_site_redirect[de]
0.45s call     mariano20.py::test_site_redirect[ca]

Results (2.10s):
       8 passed
```


Algunas veces tenemos problemas de red; don't panic!

Tenemos `flaky` para los tests _poco fiables_.

```
pip install flaky
```
```python
from flaky import flaky
@flaky(max_runs=3, min_passes=2)
def test_with_network_problems(self):
    r = requests.get(homepage, timeout=0.5)
    assert r.ok
```

Note: https://github.com/box/flaky


Los tests se pueden filtrar.

```
py.test modulo.clase::funcion
```

pero también lo podemos hacer filtrando con strings:

```
py.test -k "cart and logged"
```


Separaremos los distintos tests en agrupaciones el `pytest.mark`.

Esto nos permite filtrar por ejemplo según línia de negocio.

```python
@pytest.mark.users
```

```
py.test --markers
py.test -m users
```
Note: http://pytest.org/latest/example/markers.html


# Caso 4: `filechecker`


Confirmar que un conjunto de ficheros sigue una nomenclatura de _código-numérico_nombre.extensión_

```
000_carga-verano-2016.sql
```


En lugar de hacer un script escribiremos tests con `py.test`.


El sistema de `assert` en `py.test` es muy _pythonico_

```python
self.assertEquals(x, y)
```

```python
assert x == y
```


De primeras el no tener `assertAlmostEqual` y toda la pandilla puede parecer
un inconveniente

```python
self.assertAlmostEqual(a, b)
```

```python
assert round(a-b, 7) == 0 	 
```


Pero `py.test` sabe analizar los tipos primitivos de Python: compará
diccionarios, listas y tuplas.

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


Y gestiona excepciones y warnings:

```
def test_exceptions_and_warnings():
    with pytest.raises(AttributeError):
        raise AttributeError
    with pytest.warns(UserWarning):
        myobject.method_with_warnings()
    with pytest.deprecated_call():
        myobject.deprecated_method()
```


Mensajes de logging detallado

```python
assert x % 2 == 0, "Expected even, found odd value"
```


Podemos añadir un parámetro al `py.test` para indicar de qué directorio coger
los ficheros.

```python
# conftest.py
def pytest_addoption(parser):
    parser.addoption(
        "--chekfiles",
        default="./test-examples",
        help="set the dir to read the code"
    )
  ```

```
py.test --checkfiles=dir
```


Podemos integrar la recolección de ficheros con un parametrizador:

```python
# conftest.py
def pytest_generate_tests(metafunc):
    checkfiles = metafunc.config.option.checkfiles
    matches = []
    for root, dirnames, filenames in os.walk(checkfiles):
        for filename in fnmatch.filter(filenames, '*'):
            extension = os.path.splitext(filename)[1]
            if extension.lower() in IGNORED_EXTENSIONS:
                print("File ignore for extension: %s" % filename)
                continue
            print(filename)
            matches.append(os.path.join(root, filename))
    metafunc.parametrize("checkfile", matches)
```


Nuestra función de comprovación de extensión recibirá el parámetro `checkfile`

```python
def test_filenames_extensions(checkfile):
    extension = path.splitext(checkfile)[1].strip(".")
      assert extension in allowed_extensions, \
             "Extension %s not allowed" % (extension, )
  ```


Además, verificar que no contiene saltos de línia Mac también será un plis.

```python
def test_macos_eol(checkfile):
    with open(checkfile) as f:
        assert "\r" not in f.read()
```  


Finalmente podemos mirar que el fichero esté en `utf-8`.

Aquí empieza a brillar el hecho que usemos Python para probar
cosas: nada de usar `bash` y `file`.


Mejor usar magia.
```
pip install filemagic
```
```python
with magic.Magic(flags=magic.MAGIC_MIME_ENCODING) as m:
    try:
        encoding = m.id_filename(checkfile)
    except magic.MagicError:
        assert False, "Could not decode file"
assert encoding == "utf-8"
```


Incorporamos en la misma batería de tests ejemplos y gestionamos los casos que SABEMOS que tienen que fallar con `xfail`.
Note: http://pytest.org/latest/skipping.html#skipping


`xfail`, como la mayoría de plugins o atributos de `py.test`, lo podemos indicar como decorador de la función o en el cuerpo.

```python
@pytest.mark.xfail("Won't work!", strict=True)
def f(x):
  pass
```

```python
def test_macos_eol(checkfile):
    # fixture checking
    if path.basename(checkfile) in MACOS_EOL_FAIL_LIST:
        pytest.xfail("Expected to fail: \r in file")

    with open(checkfile) as f:
        assert "\r" not in f.read()
```


Para hacer bonitos nuestros tests: ¡colorines!

```
pip install pytest-colordots
```

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
pip install pytest-sugar
```

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


![thats-all](memes/that-s-all-folks.jpg)


![no-questions](memes/no-questions.png)
