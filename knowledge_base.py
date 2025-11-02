"""
Base de Conocimiento para el sistema de licencias.
Contiene reglas y hechos relacionados con trámites de licencias.
"""

LICENCIAS = {
    'reglas': [
        {
            'cabeza': ('debe_pagar', 'P', 'T', 'C'),
            'cuerpo': [('solicita_tramite', 'P', 'T'), ('costo_tramite', 'T', 'C')]
        },
        {
            'cabeza': ('solicita_tramite', 'P', 'T'),
            'cuerpo': [('es_ciudadano', 'P'), ('necesita_tramite', 'P', 'T')]
        }
    ],
    'hechos': [
        ('es_ciudadano', 'ana'),
        ('es_ciudadano', 'juan'),
        ('es_ciudadano', 'maria'),
        ('necesita_tramite', 'ana', 'reposicion'),
        ('necesita_tramite', 'juan', 'expedicion'),
        ('necesita_tramite', 'maria', 'revalidacion'),
        ('necesita_tramite', 'ana', 'nacimiento'),
        ('costo_tramite', 'reposicion', 823.72),
        ('costo_tramite', 'expedicion', 1077.80),
        ('costo_tramite', 'revalidacion', 956.67),
        ('costo_tramite', 'nacimiento', 476.00)
    ]
}