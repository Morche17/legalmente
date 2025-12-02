"""
Backend Legal - Capa de Lógica de Negocio
==========================================
Módulo que gestiona la interfaz entre el motor de inferencia Prolog y la interfaz
de usuario. Proporciona métodos para consultar la base de conocimientos, procesar
respuestas y mantener el estado de la sesión del usuario.

Este módulo actúa como intermediario entre:
- Motor de inferencia (core.motor_inferencia)
- Base de conocimientos (core.knowledge_base)
- Interfaz de usuario (main.py)

Responsabilidades:
- Inicialización y gestión de la base de conocimientos
- Ejecución de consultas al motor de inferencia
- Procesamiento y formateo de respuestas
- Gestión de hechos dinámicos de sesión
- Clasificación automática de trámites

"""

import io
import contextlib
import sys

# ============================================================================
# IMPORTACIÓN DE MÓDULOS DEL NÚCLEO
# ============================================================================
try:
    from core import motor_inferencia as motor
    from core import knowledge_base as kb
except ImportError:
    print(
        "ERROR CRÍTICO: No se encontraron los archivos 'motor_inferencia.py' "
        "o 'knowledge_base.py' en la carpeta core."
    )
    sys.exit(1)


# ============================================================================
# CLASE PRINCIPAL DEL BACKEND
# ============================================================================
class BackendLegal:
    """
    Clase principal que gestiona la lógica de negocio del sistema experto legal.
    
    Esta clase encapsula toda la interacción con el motor de inferencia Prolog,
    proporcionando una interfaz simplificada para la capa de presentación.
    
    Attributes:
        KB_BASE (dict): Copia de la base de conocimientos con hechos y reglas.
                       Estructura: {'hechos': [...], 'reglas': [...]}
        HECHOS_SESION (list): Lista de hechos dinámicos según el contexto del
                             usuario (ej: residencia en Ensenada).
        TRAMITES_RESIDENTES (list): Lista ordenada de trámites disponibles para
                                   residentes de Ensenada.
        TRAMITES_NO_RESIDENTES (list): Lista ordenada de trámites disponibles
                                      para usuarios foráneos.
    
    Example:
        >>> backend = BackendLegal()
        >>> backend.HECHOS_SESION = [('reside_en_ensenada', 'usuario_actual')]
        >>> resultado = backend.consultar_motor_real('acta_nacimiento', 'requiere')
    """
    
    def __init__(self):
        """
        Constructor que inicializa el backend y carga la configuración base.
        
        Realiza las siguientes operaciones:
        1. Carga una copia de la base de conocimientos desde el módulo KB
        2. Inicializa la lista de hechos de sesión vacía
        3. Genera automáticamente las listas de trámites clasificadas por tipo
        
        La generación dinámica de listas permite agregar nuevos trámites en la
        base de conocimientos sin modificar el código de la aplicación.
        """
        # Copia de la base de conocimientos para evitar modificaciones accidentales
        self.KB_BASE = kb.KB_LEGALMENTE.copy()
        
        # Lista de hechos contextuales del usuario actual
        # Ejemplo: [('reside_en_ensenada', 'usuario_actual')]
        self.HECHOS_SESION = []
        
        # Generación automática de listas de trámites
        # Separa trámites según requisitos de residencia
        self.TRAMITES_RESIDENTES, self.TRAMITES_NO_RESIDENTES = (
            self._cargar_tramites_desde_kb()
        )
    
    def _cargar_tramites_desde_kb(self):
        """
        Método privado que extrae y clasifica trámites desde la base de conocimientos.
        
        Analiza los hechos en la KB para identificar:
        - Trámites válidos generales (es_tramite_valido)
        - Trámites que no requieren residencia local (no_requiere_residencia_local)
        - Subtipos de trámites (subtipo_de) que deben ocultarse del menú principal
        
        Proceso:
        1. Identifica subtipos para excluirlos (evita duplicación en menús)
        2. Extrae trámites válidos excluyendo subtipos
        3. Extrae trámites para foráneos excluyendo subtipos
        4. Ordena ambas listas alfabéticamente
        
        Returns:
            tuple: (lista_residentes, lista_foraneos)
                - lista_residentes (list): Trámites disponibles para residentes
                - lista_foraneos (list): Trámites disponibles para foráneos
        
        Example:
            >>> lista_res, lista_for = self._cargar_tramites_desde_kb()
            >>> print(lista_res)
            ['acta_nacimiento', 'licencia_conducir', ...]
        
        Notes:
            - Los subtipos se identifican mediante el predicado 'subtipo_de'
            - Un trámite puede aparecer en ambas listas si cumple ambos criterios
            - Las listas se ordenan alfabéticamente para mejorar la UX
        """
        # Extrae todos los hechos de la base de conocimientos
        hechos = self.KB_BASE.get('hechos', [])
        
        # Identifica subtipos para excluirlos del menú principal
        # Los subtipos son variantes de trámites que se manejan internamente
        # Ejemplo: 'acta_nacimiento_reposicion' es subtipo de 'acta_nacimiento'
        subtipos = {h[1] for h in hechos if h[0] == 'subtipo_de'}
        
        # Extrae trámites para residentes
        # Criterio: tiene predicado 'es_tramite_valido' y NO es subtipo
        lista_residentes = [
            h[1] for h in hechos 
            if h[0] == 'es_tramite_valido' and h[1] not in subtipos
        ]
        
        # Extrae trámites para foráneos
        # Criterio: tiene predicado 'no_requiere_residencia_local' y NO es subtipo
        lista_foraneos = [
            h[1] for h in hechos 
            if h[0] == 'no_requiere_residencia_local' and h[1] not in subtipos
        ]
        
        # Retorna ambas listas ordenadas alfabéticamente
        return sorted(lista_residentes), sorted(lista_foraneos)
    
    # ========================================================================
    # MÉTODOS DE PROCESAMIENTO DE RESPUESTAS
    # ========================================================================
    
    def limpiar_respuesta_motor(self, texto_crudo):
        """
        Limpia y formatea la salida cruda del motor de inferencia.
        
        El motor de inferencia genera salida con información de depuración,
        trazas de derivación y formato técnico. Este método extrae únicamente
        la información relevante para el usuario final.
        
        Operaciones de limpieza:
        1. Elimina líneas vacías
        2. Filtra palabras clave de depuración (Derivación, Solución, etc.)
        3. Extrae valores de asignaciones (ej: "Variable = Valor" -> "Valor")
        4. Convierte guiones bajos a espacios
        5. Capitaliza la primera letra de cada línea
        6. Elimina líneas duplicadas consecutivas
        
        Args:
            texto_crudo (str): Salida directa del motor de inferencia, incluyendo
                             trazas de ejecución y formato técnico.
        
        Returns:
            str: Texto formateado y legible para el usuario final.
                 Retorna "N/A" si no hay contenido válido después del procesamiento.
        
        Example:
            >>> texto = "Derivación paso 1\\nRequisito = identificacion_oficial\\n-----"
            >>> backend.limpiar_respuesta_motor(texto)
            'Identificacion oficial'
        
        Notes:
            - Las palabras prohibidas se ignoran completamente
            - El formato "Variable = Valor" se convierte automáticamente a "Valor"
            - Los guiones bajos (_) se reemplazan por espacios para legibilidad
        """
        lineas = texto_crudo.split('\n')
        lineas_limpias = []
        
        # Lista de palabras clave que indican contenido de depuración
        palabras_prohibidas = [
            "Iniciando", "Solución", "Derivación", "derivación", 
            "paso a paso", "-----", "Sustituciones", "Query:", 
            "Resultado:", "Unifica", "Aplica", "HECHO:", "REGLA:"
        ]
        
        for l in lineas:
            l = l.strip()
            
            # Ignora líneas vacías
            if not l: 
                continue
            
            # Filtra líneas con palabras prohibidas
            if any(x in l for x in palabras_prohibidas): 
                continue
            
            # Extrae el valor si la línea contiene asignación (Variable = Valor)
            if "=" in l:
                partes = l.split("=")
                if len(partes) > 1: 
                    l = partes[1].strip()
            
            # Formatea el texto: reemplaza guiones bajos y capitaliza
            l = l.replace("_", " ").capitalize()
            
            # Previene duplicados consecutivos
            if lineas_limpias and lineas_limpias[-1] == l: 
                continue
            
            lineas_limpias.append(l)
        
        # Retorna las líneas unidas o "N/A" si no hay contenido
        return "\n".join(lineas_limpias) if lineas_limpias else "N/A"
    
    def procesar_costos_inteligente(self, texto_crudo):
        """
        Procesa y formatea información de costos desde la salida del motor.
        
        Los costos en la KB se almacenan como predicados con múltiples argumentos:
        costo(tramite, Descripcion, Monto). Este método empareja descripciones
        con sus montos correspondientes y genera un formato legible.
        
        Algoritmo:
        1. Busca líneas con "Descripcion =" y almacena temporalmente
        2. Busca líneas con "Monto =" que siguen a una descripción
        3. Empareja descripción + monto cuando ambos están presentes
        4. Formatea como "Descripción: $Monto MXN"
        5. Si no hay emparejamiento exitoso, aplica limpieza estándar
        
        Args:
            texto_crudo (str): Salida del motor de inferencia para consultas
                             de tipo 'costo'.
        
        Returns:
            list: Lista de strings formateados con información de costos.
                  Cada elemento tiene el formato: "Descripción: $Monto MXN"
        
        Example:
            >>> texto = "Descripcion = copia_certificada\\nMonto = 150\\n"
            >>> backend.procesar_costos_inteligente(texto)
            ['Copia certificada: $150 MXN']
        
        Notes:
            - El emparejamiento es secuencial: Descripcion seguida de Monto
            - Si falla el emparejamiento, usa limpiar_respuesta_motor como fallback
            - Los montos se formatean con símbolo $ y sufijo MXN
        """
        lineas = texto_crudo.split('\n')
        items_formateados = []
        
        # Variables temporales para emparejar descripción con monto
        temp_desc = None
        temp_monto = None
        
        for l in lineas:
            l = l.strip()
            if not l: 
                continue
            
            # Detecta y extrae descripción del costo
            if "Descripcion =" in l:
                temp_desc = (l.split("=")[1].strip()
                            .replace("_", " ")
                            .capitalize())
            
            # Detecta y extrae monto del costo
            elif "Monto =" in l:
                temp_monto = l.split("=")[1].strip()
            
            # Si ambos valores están disponibles, crea el formato final
            if temp_desc and temp_monto:
                items_formateados.append(f"{temp_desc}: ${temp_monto} MXN")
                # Resetea variables temporales para el siguiente costo
                temp_desc = None
                temp_monto = None
        
        # Fallback: si no se pudo emparejar, usa limpieza estándar
        if not items_formateados:
            return [self.limpiar_respuesta_motor(texto_crudo)]
        
        return items_formateados
    
    # ========================================================================
    # MÉTODO PRINCIPAL DE CONSULTA
    # ========================================================================
    
    def consultar_motor_real(self, tramite, predicado, variable_buscada='Dato'):
        """
        Ejecuta consultas al motor de inferencia Prolog y retorna resultados crudos.
        
        Este es el método principal de comunicación con el motor de inferencia.
        Construye queries dinámicamente según el tipo de consulta y ejecuta
        el algoritmo SLD-resolution sobre la base de conocimientos.
        
        Proceso:
        1. Prepara KB actual: KB_BASE + hechos de sesión del usuario
        2. Construye query según el predicado solicitado
        3. Ejecuta motor de inferencia capturando salida stdout
        4. Retorna resultado crudo para procesamiento posterior
        
        Args:
            tramite (str): Identificador del trámite a consultar.
                          Ejemplo: 'acta_nacimiento', 'licencia_conducir'
            
            predicado (str): Tipo de información a consultar.
                           Valores comunes: 'costo', 'requiere', 'dependencia',
                           'vigencia', 'modalidad_tramite'
            
            variable_buscada (str, optional): Nombre de la variable a resolver
                                            en la query. Default: 'Dato'
        
        Returns:
            str: Salida cruda del motor de inferencia, incluyendo trazas de
                 derivación y resultados. Retorna cadena vacía si hay error.
        
        Example:
            >>> backend.consultar_motor_real('acta_nacimiento', 'requiere')
            'Derivación...\\nRequisito = identificacion_oficial\\n...'
            
            >>> backend.consultar_motor_real('licencia_conducir', 'costo')
            'Descripcion = tramite\\nMonto = 500\\n...'
        
        Query Construction:
            - 'costo': ('costo', tramite, 'Descripcion', 'Monto')
            - 'requiere': ('requiere', tramite, 'Requisito')
            - otros: (predicado, tramite, variable_buscada)
        
        Notes:
            - La salida se captura redirigiendo stdout a un StringIO
            - Los hechos de sesión se agregan temporalmente sin modificar KB_BASE
            - Errores en la ejecución retornan cadena vacía (manejo silencioso)
            - La salida cruda debe procesarse con limpiar_respuesta_motor()
              o procesar_costos_inteligente()
        
        Raises:
            No lanza excepciones explícitamente. Errores se capturan y retornan
            cadena vacía.
        """
        # Prepara base de conocimientos para esta consulta
        # Combina KB base con hechos específicos de la sesión
        kb_actual = self.KB_BASE.copy()
        kb_actual['hechos'] = self.KB_BASE['hechos'] + self.HECHOS_SESION
        
        # Construcción dinámica de query según el tipo de predicado
        if predicado == 'costo':
            # Query especial para costos: necesita dos variables de salida
            query = ('costo', tramite, 'Descripcion', 'Monto')
        elif predicado == 'requiere':
            # Query para requisitos: una variable de salida
            query = ('requiere', tramite, 'Requisito')
        else:
            # Query genérica para otros predicados
            query = (predicado, tramite, variable_buscada)
        
        # Captura la salida estándar del motor de inferencia
        f = io.StringIO()
        
        try:
            # Redirección temporal de stdout para capturar trazas
            with contextlib.redirect_stdout(f): 
                motor.sld_solve(kb_actual, query)
            raw = f.getvalue()
        except:
            # Manejo silencioso de errores: retorna cadena vacía
            raw = ""
        
        return raw