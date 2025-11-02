"""
Base de Conocimiento (BC) para el sistema LegalMente.
Contiene todos los hechos y reglas lógicas sobre los 15 trámites
gubernamentales en Ensenada, B.C., para Octubre de 2025.

(Versión CORREGIDA: Los hechos 'subtipo_de' están en la
lista 'hechos', no en 'reglas')
"""

KB_LEGALMENTE = {
    'reglas': [
        # --- 1. Reglas Lógicas de Negocio ---

        # Regla 15: "Si el trámite tiene costo, entonces deberá ser pagado."
        {
            'cabeza': ('requiere_pago', 'Tramite'),
            'cuerpo': [('costo', 'Tramite', 'Descripcion', 'Monto')]
        },
        # Regla 1: "Si... no está disponible en línea, entonces debe asistir a Recaudación..."
        {
            'cabeza': ('lugar_de_pago_fisico', 'Tramite', 'Recaudacion de Rentas Ensenada'),
            'cuerpo': [('es_tramite_valido', 'Tramite'), 
                       ('pago_no_disponible_en_linea', 'Tramite')]
        },
        # Regla 6: Lógica de Residencia
        {
            'cabeza': ('es_apto_para_tramite', 'Persona', 'Tramite'),
            'cuerpo': [('no_requiere_residencia_local', 'Tramite')]
        },
        {
            'cabeza': ('es_apto_para_tramite', 'Persona', 'Tramite'),
            'cuerpo': [('requiere_residencia_local', 'Tramite'),
                       ('reside_en_ensenada', 'Persona')]
        },
        # Regla 13: Lógica de Gestores / Terceros
        {
            'cabeza': ('requiere_para_tercero', 'Tramite', 'carta_poder_firmada'),
            'cuerpo': [('permite_tercero', 'Tramite')]
        },
        {
            'cabeza': ('requiere_para_tercero', 'Tramite', 'identificacion_oficial_interesado'),
            'cuerpo': [('permite_tercero', 'Tramite')]
        },
        {
            'cabeza': ('requiere_para_tercero', 'Tramite', 'identificacion_oficial_gestor'),
            'cuerpo': [('permite_tercero', 'Tramite')]
        },

        # --- 2. Reglas "Puente" de Unificación de Subtipos ---
        # Estas reglas (diccionarios) SÍ pertenecen aquí.
        
        # Si preguntas por 'requiere' un trámite genérico, busca en sus subtipos.
        {
            'cabeza': ('requiere', 'TramiteGenerico', 'Requisito'),
            'cuerpo': [('subtipo_de', 'TramiteEspecifico', 'TramiteGenerico'),
                       ('requiere', 'TramiteEspecifico', 'Requisito')]
        },
        # Si preguntas por 'costo'
        {
            'cabeza': ('costo', 'TramiteGenerico', 'Desc', 'Monto'),
            'cuerpo': [('subtipo_de', 'TramiteEspecifico', 'TramiteGenerico'),
                       ('costo', 'TramiteEspecifico', 'Desc', 'Monto')]
        },
        # Si preguntas por 'dependencia'
        {
            'cabeza': ('dependencia', 'TramiteGenerico', 'Lugar'),
            'cuerpo': [('subtipo_de', 'TramiteEspecifico', 'TramiteGenerico'),
                       ('dependencia', 'TramiteEspecifico', 'Lugar')]
        },
        # Si preguntas por 'condicion'
        {
            'cabeza': ('condicion', 'TramiteGenerico', 'Detalle'),
            'cuerpo': [('subtipo_de', 'TramiteEspecifico', 'TramiteGenerico'),
                       ('condicion', 'TramiteEspecifico', 'Detalle')]
        }
    ],
    'hechos': [
        # --- HECHOS "PUENTE" (Corregido: ahora están en 'hechos') ---
        # Estos son HECHOS (tuplas) que definen la relación de subtipos.
        ('subtipo_de', 'acta_nacimiento_existente', 'acta_nacimiento'),
        ('subtipo_de', 'acta_nacimiento_recien_nacido', 'acta_nacimiento'),
        ('subtipo_de', 'acta_matrimonio_en_linea', 'acta_matrimonio'),
        ('subtipo_de', 'acta_matrimonio_presencial', 'acta_matrimonio'),
        ('subtipo_de', 'cambio_propietario_pf', 'cambio_propietario_vehiculo'), # Persona Física
        ('subtipo_de', 'cambio_propietario_pm', 'cambio_propietario_vehiculo'), # Persona Moral

        # --- Hechos: Catálogo de Trámites Válidos (Regla 4 y 14) ---
        ('es_tramite_valido', 'acta_nacimiento'),
        ('es_tramite_valido', 'expedicion_licencia'),
        ('es_tramite_valido', 'revalidacion_licencia'),
        ('es_tramite_valido', 'refrendo_tarjeta_circulacion'),
        ('es_tramite_valido', 'constancia_antecedentes_penales'),
        ('es_tramite_valido', 'reposicion_licencia'),
        ('es_tramite_valido', 'alta_vehiculo'),
        ('es_tramite_valido', 'baja_vehiculo'),
        ('es_tramite_valido', 'cambio_propietario_vehiculo'),
        ('es_tramite_valido', 'reposicion_tarjeta_circulacion'),
        ('es_tramite_valido', 'reposicion_placas_circulacion'),
        ('es_tramite_valido', 'permiso_traslado_vehicular'),
        ('es_tramite_valido', 'acta_matrimonio'),
        ('es_tramite_valido', 'acta_defuncion'),
        ('es_tramite_valido', 'pasaporte'),

        # --- Hechos: Requisitos de Residencia (Regla 6) ---
        ('requiere_residencia_local', 'expedicion_licencia'),
        ('requiere_residencia_local', 'revalidacion_licencia'),
        ('requiere_residencia_local', 'reposicion_licencia'),
        ('requiere_residencia_local', 'alta_vehiculo'),
        ('requiere_residencia_local', 'baja_vehiculo'),
        ('requiere_residencia_local', 'cambio_propietario_vehiculo'),
        ('requiere_residencia_local', 'refrendo_tarjeta_circulacion'),
        ('requiere_residencia_local', 'reposicion_tarjeta_circulacion'),
        ('requiere_residencia_local', 'reposicion_placas_circulacion'),
        ('requiere_residencia_local', 'permiso_traslado_vehicular'),
        ('requiere_residencia_local', 'acta_matrimonio'), # Condición: casarse en Ensenada

        ('no_requiere_residencia_local', 'acta_nacimiento'),
        ('no_requiere_residencia_local', 'constancia_antecedentes_penales'),
        ('no_requiere_residencia_local', 'acta_defuncion'),
        ('no_requiere_residencia_local', 'pasaporte'),

        # --- Hechos: Dependencias ---
        # (Se agrupan los subtipos para que las reglas puente funcionen)
        ('dependencia', 'acta_nacimiento_existente', 'Registro Civil Ensenada'),
        ('dependencia', 'acta_nacimiento_recien_nacido', 'Registro Civil Ensenada'),
        ('dependencia', 'acta_matrimonio_presencial', 'Registro Civil Ensenada'),
        ('dependencia', 'acta_matrimonio_en_linea', 'Portal Web Gobierno BC'),
        ('dependencia', 'acta_defuncion', 'Registro Civil Ensenada (Oficialia 01)'),
        
        ('dependencia', 'expedicion_licencia', 'Recaudacion de Rentas Ensenada'),
        ('dependencia', 'revalidacion_licencia', 'Recaudacion de Rentas Ensenada'),
        ('dependencia', 'reposicion_licencia', 'Recaudacion de Rentas Ensenada'),
        ('dependencia', 'refrendo_tarjeta_circulacion', 'Recaudacion de Rentas Ensenada'),
        ('dependencia', 'alta_vehiculo', 'Recaudacion de Rentas Ensenada'),
        ('dependencia', 'baja_vehiculo', 'Recaudacion de Rentas Ensenada'),
        ('dependencia', 'reposicion_tarjeta_circulacion', 'Recaudacion de Rentas Ensenada'),
        ('dependencia', 'permiso_traslado_vehicular', 'Recaudacion de Rentas Ensenada'),
        ('dependencia', 'cambio_propietario_vehiculo', 'Subrecaudacion Auxiliar de Rentas Ensenada'),
        
        ('dependencia', 'pasaporte', 'Oficina de Enlace SRE Ensenada'),
        ('dependencia', 'constancia_antecedentes_penales', 'Fiscalia General del Estado'),

        # --- Hechos: Costos (Regla 7 y 15) ---
        ('costo', 'expedicion_licencia', '3_años', 1077.80),
        ('costo', 'expedicion_licencia', '5_años', 1437.07),
        ('costo', 'revalidacion_licencia', '3_años', 956.67),
        ('costo', 'revalidacion_licencia', '5_años', 1275.57),
        ('costo', 'reposicion_licencia', 'estandar', 823.72),
        ('costo', 'refrendo_tarjeta_circulacion', 'auto_particular', 1148.34),
        ('costo', 'refrendo_tarjeta_circulacion', 'motocicleta', 1148.34),
        ('costo', 'refrendo_tarjeta_circulacion', 'demostracion', 2162.33),
        ('costo', 'refrendo_tarjeta_circulacion', 'remolque', 504.49),
        ('costo', 'constancia_antecedentes_penales', 'estandar', 272.91),
        ('costo', 'reposicion_tarjeta_circulacion', 'estandar', 384.62),
        ('costo', 'alta_vehiculo', 'tarjeta_circulacion_auto_particular', 1779.85),
        ('costo', 'alta_vehiculo', 'tarjeta_circulacion_motocicleta', 1779.85),
        ('costo', 'alta_vehiculo', 'tarjeta_circulacion_demostracion', 4253.14),
        ('costo', 'alta_vehiculo', 'tarjeta_circulacion_remolque', 1636.86),
        ('costo', 'alta_vehiculo', 'placas_auto_particular', 1874.63),
        ('costo', 'alta_vehiculo', 'placas_motocicleta', 376.19),
        ('costo', 'alta_vehiculo', 'placas_demostracion', 4228.96),
        ('costo', 'alta_vehiculo', 'placas_remolque', 1359.19),
        ('costo', 'alta_vehiculo', 'placas_discapacitado', 1874.63),
        ('costo', 'baja_vehiculo', 'estandar', 384.62),
        ('costo', 'permiso_traslado_vehicular', '15_dias', 1036.78),
        ('costo', 'pasaporte', '1_año (solo menores 3 años)', 885.00),
        ('costo', 'pasaporte', '3_años', 1730.00),
        ('costo', 'pasaporte', '6_años', 2350.00),
        ('costo', 'pasaporte', '10_años (no trabajadores agricolas)', 4120.00),
        ('costo', 'cambio_propietario_vehiculo', 'variable (depende_modelo_impuestos)', 0.00),
        ('costo', 'acta_nacimiento_existente', 'copia_certificada', 476.00),
        ('costo', 'acta_matrimonio_presencial', 'copia_certificada', 476.00),
        ('costo', 'acta_matrimonio_en_linea', 'copia_certificada', 476.00),
        ('costo', 'acta_defuncion', 'primera_acta', 244.00),
        ('costo', 'acta_defuncion', 'copia_consecutiva', 122.00),
        ('costo', 'reposicion_placas_circulacion', 'informacion_no_disponible', 0.00),
        
        ('moneda_de_pago', 'mxn'), # Hecho para Regla 7

        # --- Hechos: Requisitos (Regla 2, 12) ---
        ('requiere', 'expedicion_licencia', 'identificacion_oficial_vigente'),
        ('requiere', 'expedicion_licencia', 'comprobante_domicilio'),
        ('requiere', 'expedicion_licencia', 'certificado_medico'),
        ('requiere', 'revalidacion_licencia', 'presentar_licencia_anterior'),
        ('requiere', 'reposicion_licencia', 'denuncia_o_reporte_extravio'),
        ('requiere', 'reposicion_licencia', 'identificacion_oficial_vigente'),
        ('requiere', 'baja_vehiculo', 'entregar_placas'),
        ('requiere', 'baja_vehiculo', 'entregar_tarjeta_circulacion'),
        ('requiere', 'baja_vehiculo', 'formato_de_baja'),
        ('requiere', 'permiso_traslado_vehicular', 'revision_fisica_vehiculo'),
        ('requiere', 'permiso_traslado_vehicular', 'documentos_que_avalen_legalidad_vehiculo'),
        
        # Requisitos: Cambio de Propietario (subtipos)
        ('requiere', 'cambio_propietario_pf', 'factura_original'),
        ('requiere', 'cambio_propietario_pf', 'identificacion_original_con_foto'),
        ('requiere', 'cambio_propietario_pf', 'licencia_conducir_vigente_bc'),
        ('requiere', 'cambio_propietario_pf', 'comprobante_domicilio_reciente'),
        ('requiere', 'cambio_propietario_pf', 'tarjeta_circulacion_anterior'),
        ('requiere', 'cambio_propietario_pf', 'pago_derecho_cambio_propietario'),
        ('requiere', 'cambio_propietario_pf', 'seguro_responsabilidad_civil_vigente'),
        ('requiere', 'cambio_propietario_pm', 'acta_constitutiva'),
        ('requiere', 'cambio_propietario_pm', 'poder_notarial_representante_legal'),
        ('requiere', 'cambio_propietario_pm', 'rfc_empresa'),
        ('requiere', 'cambio_propietario_pm', 'identificacion_oficial_representante'),
        ('requiere', 'cambio_propietario_pm', 'factura_original_vehiculo'),
        ('requiere', 'cambio_propietario_pm', 'tarjeta_circulacion_anterior'),
        ('requiere', 'cambio_propietario_pm', 'comprobante_domicilio_empresa'),

        # Requisitos: Acta de Nacimiento (subtipos)
        ('requiere', 'acta_nacimiento_existente', 'CURP'),
        ('requiere', 'acta_nacimiento_existente', 'nombre_completo'),
        ('requiere', 'acta_nacimiento_existente', 'fecha_nacimiento'),
        ('requiere', 'acta_nacimiento_existente', 'lugar_nacimiento'),
        ('requiere', 'acta_nacimiento_existente', 'sexo'),
        ('requiere', 'acta_nacimiento_existente', 'nombres_padres'),
        ('requiere', 'acta_nacimiento_recien_nacido', 'certificado_nacimiento_hospital'),
        ('requiere', 'acta_nacimiento_recien_nacido', 'identificacion_padres'),
        ('requiere', 'acta_nacimiento_recien_nacido', 'CURP_padres'),
        ('requiere', 'acta_nacimiento_recien_nacido', 'comprobante_domicilio'),
        ('requiere', 'acta_nacimiento_recien_nacido', 'testigos'),
        
        # Requisitos: Acta de Matrimonio (subtipos)
        ('requiere', 'acta_matrimonio_en_linea', 'cuenta_digital_activa'),
        ('requiere', 'acta_matrimonio_en_linea', 'nombres_contrayentes'),
        ('requiere', 'acta_matrimonio_en_linea', 'CURP_contrayentes'),
        ('requiere', 'acta_matrimonio_en_linea', 'fecha_matrimonio'),
        ('requiere', 'acta_matrimonio_en_linea', 'lugar_matrimonio'),
        ('requiere', 'acta_matrimonio_en_linea', 'numero_acta_o_libro'),
        ('requiere', 'acta_matrimonio_presencial', 'identificacion_oficial_solicitante'),
        ('requiere', 'acta_matrimonio_presencial', 'nombres_conyuges'),
        ('requiere', 'acta_matrimonio_presencial', 'fecha_matrimonio'),
        ('requiere', 'acta_matrimonio_presencial', 'lugar_matrimonio'),
        ('requiere', 'acta_matrimonio_presencial', 'numero_acta_y_foja'),
        
        # Requisitos: Acta de Defunción (directos)
        ('requiere', 'acta_defuncion', 'certificado_defuncion_original'),
        ('requiere', 'acta_defuncion', 'acta_nacimiento_finado'),
        ('requiere', 'acta_defuncion', 'identificacion_y_CURP_finado'),
        ('requiere', 'acta_defuncion', 'acta_matrimonio_finado_si_aplica'),
        ('requiere', 'acta_defuncion', 'oficio_ministerio_publico_si_muerte_violenta'),
        ('requiere', 'acta_defuncion', 'identificacion_declarante'),
        ('requiere', 'acta_defuncion', 'identificaciones_testigos'),
        ('requiere', 'acta_defuncion', 'solicitud_acta_defuncion'),
        
        # Hecho para trámite sin datos (para evitar 'Falso')
        ('requiere', 'reposicion_placas_circulacion', 'informacion_no_disponible'),
        ('requiere', 'refrendo_tarjeta_circulacion', 'presentar_tarjeta_anterior'),
        ('requiere', 'alta_vehiculo', 'factura_o_titulo_vehiculo'),
        ('requiere', 'alta_vehiculo', 'identificacion_oficial'),
        ('requiere', 'constancia_antecedentes_penales', 'identificacion_oficial'),
        ('requiere', 'pasaporte', 'acta_nacimiento'),
        ('requiere', 'pasaporte', 'identificacion_oficial'),
        ('requiere', 'pasaporte', 'CURP'),
        ('requiere', 'pasaporte', 'comprobante_pago_derechos'),

        # --- Hechos: Gestores y Terceros (Regla 13) ---
        ('permite_tercero', 'refrendo_tarjeta_circulacion'), # Representante legal
        ('permite_tercero', 'alta_vehiculo'), # Representante legal
        ('permite_tercero', 'baja_vehiculo'), # Representante empresa
        ('permite_tercero', 'permiso_traslado_vehicular'), # Representante empresa
        ('permite_tercero', 'permiso_traslado_vehicular'), # Conductor sustituto (con formato)
        
        ('no_permite_tercero', 'constancia_antecedentes_penales'), # Solo interesado
        ('no_permite_tercero', 'reposicion_tarjeta_circulacion'), # Solo interesado
        ('no_permite_tercero', 'pasaporte'), # Solo interesado (o tutores para menores)

        # --- Hechos: Modalidad y Citas ---
        ('modalidad_tramite', 'pasaporte', 'presencial_unicamente'),
        ('modalidad_tramite', 'acta_matrimonio_en_linea', 'en_linea'),
        ('modalidad_tramite', 'acta_matrimonio_presencial', 'presencial'),
        ('requiere_cita', 'cambio_propietario_vehiculo'),
        ('metodo_cita', 'cambio_propietario_vehiculo', 'en_linea'),
        
        # --- Hechos: Vigencia ---
        ('vigencia', 'refrendo_tarjeta_circulacion', 'variable'),
        ('vigencia', 'constancia_antecedentes_penales', '3_meses'),
        ('vigencia', 'reposicion_tarjeta_circulacion', 'variable_segun_pago'),
        ('vigencia', 'permiso_traslado_vehicular', '15_dias'),
        
        # --- Hechos: Condiciones y Notas (Pasaporte) ---
        ('condicion', 'pasaporte', 'vigencia_1_año_solo_para_menores_3_años'),
        ('condicion', 'pasaporte', 'vigencia_10_años_no_aplica_trabajadores_agricolas'),
        ('condicion', 'pasaporte', 'tramite_menores_solo_con_patria_potestad_o_tutela'),
        ('descuento_pasaporte', 'mayor_60_años', 0.50),
        ('descuento_pasaporte', 'persona_con_discapacidad_comprobable', 0.50),
        ('descuento_pasaporte', 'trabajador_agricola_canada', 0.50),
        ('lugar_pago', 'pasaporte', 'oficinas_consulares'),
        ('lugar_pago', 'pasaporte', 'banco_autorizado'),
        ('banco_autorizado_pasaporte', 'banjercito'),
        ('banco_autorizado_pasaporte', 'banorte'),
        # ... (y el resto de los bancos) ...
        
        # --- Hechos: Condiciones y Notas (Vehículos) ---
        ('tipo_pago_aceptado', 'Recaudacion de Rentas Ensenada', 'efectivo'),
        ('tipo_pago_aceptado', 'Recaudacion de Rentas Ensenada', 'cheque_certificado'),
        ('tipo_pago_aceptado', 'Recaudacion de Rentas Ensenada', 'tarjeta_debito'),
        ('tipo_pago_aceptado', 'Recaudacion de Rentas Ensenada', 'tarjeta_credito (excepto Amex)'),
        ('tipo_persona_tramite', 'alta_vehiculo', 'persona_fisica'),
        ('tipo_persona_tramite', 'alta_vehiculo', 'persona_moral'),
        ('tipo_persona_tramite', 'cambio_propietario_vehiculo', 'persona_fisica'),
        ('tipo_persona_tramite', 'cambio_propietario_vehiculo', 'persona_moral'),
        ('incluye', 'alta_vehiculo', 'placas'),
        ('incluye', 'alta_vehiculo', 'tarjeta_circulacion'),
        ('requiere_verificacion_vehicular', 'alta_vehiculo'),
        ('requiere_verificacion_vehicular', 'permiso_traslado_vehicular'),
        ('requiere_verificacion_vehicular', 'cambio_propietario_vehiculo'),
        ('condicion', 'alta_vehiculo', 'se_puede_dar_de_alta_vehiculo_foraneo'),
        ('condicion', 'baja_vehiculo', 'no_es_necesario_llevar_vehiculo'),
        ('condicion', 'baja_vehiculo', 'puede_ser_temporal_o_definitiva'),
        ('condicion', 'cambio_propietario_vehiculo', 'costo_es_variable'),
        ('condicion', 'cambio_propietario_vehiculo', 'tramite_obligatorio_en_venta_vehiculo_usado'),
        
        # --- Hechos: Condiciones y Notas (Registro Civil) ---
        ('condicion', 'acta_defuncion', 'tramitar_en_oficialia_01_si_fallecio_en_ensenada'),
        ('condicion', 'acta_matrimonio_presencial', 'contrayentes_deben_casarse_en_ensenada'),
        
        # --- Hechos: Pago en línea (Regla 1) ---
        ('pago_no_disponible_en_linea', 'expedicion_licencia'),
        ('pago_no_disponible_en_linea', 'revalidacion_licencia'),
        ('pago_no_disponible_en_linea', 'reposicion_licencia'),
        ('pago_no_disponible_en_linea', 'alta_vehiculo'),
        ('pago_no_disponible_en_linea', 'baja_vehiculo'),
        ('pago_no_disponible_en_linea', 'cambio_propietario_vehiculo'),
    ]
}