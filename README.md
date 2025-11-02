# LegalMente(equipo de leyes) - Resolución SLD en Python

Este proyecto implementa un motor de inferencia basado en **Resolución SLD (Selective Linear Definite-clause resolution)** en Python. El objetivo es simular el razonamiento de un sistema experto capaz de responder consultas sobre una base de conocimiento definida mediante cláusulas de Horn.

## Descripción del Proyecto

El script `sld_practice.py` toma un programa lógico (una lista de hechos y reglas) y una consulta (query), y utiliza el algoritmo de Resolución SLD para encontrar todas las sustituciones de variables que satisfacen dicha consulta. Además, para facilitar la comprensión del proceso, el script imprime la ruta de derivación detallada paso a paso, mostrando cómo el sistema llega a una conclusión.

El proyecto utiliza una pequeña sección de la base de conocimientos del sistema experto "LegalMente", enfocado en trámites vehiculares en Ensenada.

## Estructura del Repositorio

* `sld_practice.py`: El script principal que contiene el motor de Resolución SLD.
* `base_conocimiento.txt`: Un archivo de texto que describe los hechos y reglas utilizados en la demostración.
* `README.md`: Este archivo.

## Base de Conocimiento Utilizada

Para la demostración, hemos seleccionado un subconjunto de reglas y hechos relacionados con la **expedición de la licencia de conducir**.

### Hechos:

Representan conocimiento fundamental y verdadero en nuestro sistema.

* Ana es ciudadana
* Juan es ciudadano
* Maria es ciudadana
* Ana necesita reposicionar su tarjeta de circulación
* Maria necesita revalidar su licencia de conducir
* Juan necesita expedir su licencia de conducir
* Expedir la licencia de conducir tiene un precio $1077.80
* La revalidacion de la tarjeta de conducir tiene un precio $956.57
* La reposicion de la licencia de conducir tiene un precio de $823.72


### Reglas (Cláusulas de Horn):

Permiten al sistema inferir nuevo conocimiento a partir de los hechos.

1. **Expedición de licencia de conducir:**
- Si el ciudadano no cuenta con licencia de conducir y desea conducir, entonces debe tramitar la expedición de una nueva licencia en la Secretaría de Hacienda de Ensenada.
- Si el ciudadano quiere expedir su licencia de conducir, entonces debe llevar identificación oficial, comprobante de domicilio y certificado médico.
- Si quieres realizar el trámite, entonces debes pagar y tiene un costo de $1,077.80 MXN. por 3 años
- Si quieres realizar el trámite, entonces debes pagar y tiene un costo de $1,437.07 MXN. por 5 años.
 

2. **Revalidación licencia de conducir:**
- Si el ciudadano quiere revalidar su licencia de conducir, entonces debe llevar la licencia anterior.
- Si la licencia de conducir está vencida, entonces el ciudadano debe tramitar la revalidación de la licencia en la Secretaría de Hacienda de Ensenada.
Si quieres realizar el trámite, entonces debes pagar tiene un costo de $956.67 MXN. por 3 años
Si quieres realizar el trámite, entonces debes pagar tiene un costo de $1,275.57 MXN. por 5 años

3. **Reposición de licencia de conducir:** 
- Si el ciudadano perdió su licencia o requiere una reposición, entonces debe tramitar la reposición de licencia en la Secretaría de Hacienda de Ensenada.
- Si un ciudadano solicita la reposición de su licencia, entonces debe presentar una denuncia o reporte de extravío junto con una identificación oficial vigente.
- Si quieres reposicionar tu licencia de conducir, debes pagar $823.72 MXN.



## ¿Cómo Ejecutar el Script?

1.  Asegúrate de tener Python 3 instalado.
2.  Coloca los archivos `sld_practice.py` y `knowledge_base.py` en el mismo directorio.
3.  Abre una terminal en ese directorio y ejecuta el siguiente comando:

```bash
python sld_practice.py
