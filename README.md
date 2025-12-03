# LegalMente(equipo de leyes) - Resolución SLD en Python

Este proyecto implementa un motor de inferencia basado en **Resolución SLD (Selective Linear Definite-clause resolution)** en Python. El objetivo es simular el razonamiento de un sistema experto capaz de responder consultas sobre una base de conocimiento definida mediante cláusulas de Horn.

## Descripción del Proyecto

LegalMente es un sistema experto desarrollado en Python que proporciona información completa y actualizada sobre trámites gubernamentales en Ensenada, B.C. para octubre de 2025. La aplicación utiliza un motor de inferencia lógica basado en resolución SLD (encadenamiento hacia atrás) para ofrecer respuestas inteligentes sobre requisitos, costos, dependencias y condiciones de diversos trámites.

## Estructura del Repositorio

```bash
LegalMente/
├── main.py                 # Aplicación principal y interfaz de usuario
├── ui/
│   └── elementos.py        # Componentes UI reutilizables (tarjetas visuales)
├── logic/
│   └── sistema.py          # Lógica de negocio y backend
└── core/
    ├── motor_inferencia.py # Motor de inferencia SLD (encadenamiento hacia atrás)
    └── knowledge_base.py   # Base de conocimiento con hechos y reglas
```

## Base de Conocimiento Utilizada

### Reglas Lógicas

- Reglas de negocio: Validación de pagos, residencia, terceros
- Reglas "puente": Unificación de subtipos de trámites
- Reglas de inferencia: Derivación de información relacionada

### Hechos Específicos

- Catálogo de trámites: 15+ trámites válidos organizados por categorías
- Requisitos de residencia: Filtrado por residentes vs. foráneos
- Dependencias: Oficinas gubernamentales responsables
- Costos: Tarifas detalladas por concepto y vigencia
- Requisitos: Documentación necesaria para cada trámite
- Condiciones especiales: Vigencia, modalidades, restricciones

### Ejemplos de Trámites Incluidos

- Actas de nacimiento, matrimonio y defunción
- Licencias de conducir (expedición, revalidación, reposición)
- Trámites vehiculares (altas, bajas, cambio de propietario)
- Refrendo de tarjeta de circulación
- Constancia de antecedentes penales
- Pasaporte

## ¿Cómo Ejecutar el Script?

1.  Asegúrate de tener Python 3 instalado.
2.  Requiere la instalación de **flet**.
```bash
pip install flet
```
3.  Abre una terminal en ese directorio y ejecuta el siguiente comando:
```bash
python main.py
```
