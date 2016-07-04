`Pytest` desde las trincheras
=============================

Pau Ruŀlan Ferragut

pau@rullan.cat + prullan@apsl.net

CreantBits «Estiu 2016» - 15/7/2016

EuroPython 2016 - Bilbao 19/7/2016

[logo APSL]



Cómo usar pytest para cosas que no nos vienen a la cabeza usar un framework de
testing.




Recreación de batallitas con Pytest



Trabajo en APSL como sysadmin

(lo que en _cool_ hoy en día llaman `SRE`)




[shameless plug]


En APSL siempre buscamos talento así que si quieres disfrutar de los infitos días de sol de Mallorca estás invitado

[it's always sunny in Palma]

Py.test como gestor de tests unitarios



Paso más allá, utilidades de QA y sysadmin


Caso 0: `filechecker`


Confirmar que un conjunto de ficheros sigue una nomenclatura de `código-numérico_nombre.extensión`

Podemos añadir un parámetro al `py.test` para indicar de qué directorio coger los ficheros.


Podemos mirar que estén en `utf-8`.
Aquí empieza a brillar el hecho que usemos Python para probar cosas: nada de usar `bash` y `file`, mejor usar magia.

[kind of magic]


Además, verificar que no contiene saltos de línia Mac también será un plis.


Ahora lo hacemos bonito con `colors`

Caso 1: `mariano20`




Mariano era un jefe que tuve al que le encantaba hacer de nagios humano.



Para hacer que su família pudiera disfrutar de él lo robotizamos e hicimos el «Mariano 2.0» o `mariano20`.



En realidad es un scraping dinámico que lee de un fichero de configuración las páginas que tienen que existir.



Sincronización de las secciones principales de una web.



Podemos especificar en un yaml qué menús esperamos encontrar. Generaremos un fallo en caso que no sean exactamente esos.



Parametrizamos el test para poder mirar a todos nuestros países.



Y lo ponemos en paralelo: `xdist`



Algunas veces tenemos problemas de red; don't panic! Tenemos `flaky` para los tests _poco fiables_.



Usaremos la salida XML del `jUnit` para guardar el estado.


Lo metemos en un job periódico de jenkins y listos.



Si quisieramos ara podríamos escribirlo mediante `asyncio`

[because you can]


Caso 2: generador configuraciones kubernetes

Verificador de yaml para un deploy kubernetes



[that's all folks]

[ questions please]
