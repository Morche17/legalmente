import io
import contextlib
import sys

# --- IMPORTS REALES (Apuntando a la carpeta core) ---
try:
    from core import motor_inferencia as motor
    from core import knowledge_base as kb
except ImportError:
    print("ERROR CRÍTICO: No se encontraron los archivos 'motor_inferencia.py' o 'knowledge_base.py' en la carpeta core.")
    sys.exit(1)

class BackendLegal:
    def __init__(self):
        # --- CONFIGURACIÓN BASE ---
        self.KB_BASE = kb.KB_LEGALMENTE.copy()
        self.HECHOS_SESION = []

        # --- GENERACIÓN DINÁMICA DE LISTAS ---
        # El sistema detecta automáticamente los trámites desde la KB
        self.TRAMITES_RESIDENTES, self.TRAMITES_NO_RESIDENTES = self._cargar_tramites_desde_kb()

    def _cargar_tramites_desde_kb(self):
        """Lee la base de hechos y separa los trámites automáticamente."""
        hechos = self.KB_BASE.get('hechos', [])
        
        # Identificamos subtipos para ocultarlos del menú principal
        subtipos = {h[1] for h in hechos if h[0] == 'subtipo_de'}

        # Lista de residentes: 'es_tramite_valido' menos los subtipos
        lista_residentes = [
            h[1] for h in hechos 
            if h[0] == 'es_tramite_valido' and h[1] not in subtipos
        ]

        # Lista de foráneos: 'no_requiere_residencia_local' menos los subtipos
        lista_foraneos = [
            h[1] for h in hechos 
            if h[0] == 'no_requiere_residencia_local' and h[1] not in subtipos
        ]

        return sorted(lista_residentes), sorted(lista_foraneos)

    # --- LÓGICA DE PROCESAMIENTO (BACKEND) ---

    def limpiar_respuesta_motor(self, texto_crudo):
        lineas = texto_crudo.split('\n')
        lineas_limpias = []
        palabras_prohibidas = ["Iniciando", "Solución", "Derivación", "derivación", "paso a paso", "-----", "Sustituciones", "Query:", "Resultado:", "Unifica", "Aplica", "HECHO:", "REGLA:"]

        for l in lineas:
            l = l.strip()
            if not l: continue
            if any(x in l for x in palabras_prohibidas): continue
            if "=" in l:
                partes = l.split("=")
                if len(partes) > 1: l = partes[1].strip()
            l = l.replace("_", " ").capitalize()
            if lineas_limpias and lineas_limpias[-1] == l: continue
            lineas_limpias.append(l)

        return "\n".join(lineas_limpias) if lineas_limpias else "N/A"

    def procesar_costos_inteligente(self, texto_crudo):
        lineas = texto_crudo.split('\n')
        items_formateados = []
        temp_desc = None
        temp_monto = None
        
        for l in lineas:
            l = l.strip()
            if not l: continue
            if "Descripcion =" in l:
                temp_desc = l.split("=")[1].strip().replace("_", " ").capitalize()
            elif "Monto =" in l:
                temp_monto = l.split("=")[1].strip()
            if temp_desc and temp_monto:
                items_formateados.append(f"{temp_desc}: ${temp_monto} MXN")
                temp_desc = None
                temp_monto = None
                
        if not items_formateados:
            return [self.limpiar_respuesta_motor(texto_crudo)]
        return items_formateados

    def consultar_motor_real(self, tramite, predicado, variable_buscada='Dato'):
        kb_actual = self.KB_BASE.copy()
        kb_actual['hechos'] = self.KB_BASE['hechos'] + self.HECHOS_SESION
        
        if predicado == 'costo': query = ('costo', tramite, 'Descripcion', 'Monto')
        elif predicado == 'requiere': query = ('requiere', tramite, 'Requisito')
        else: query = (predicado, tramite, variable_buscada)

        f = io.StringIO()
        try:
            with contextlib.redirect_stdout(f): motor.sld_solve(kb_actual, query)
            raw = f.getvalue()
        except: raw = ""
        return raw