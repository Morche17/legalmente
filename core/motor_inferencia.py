"""
El código implementa la Resolución SLD usando un motor de encadenamiento hacia atrás recursivo. 
La lógica de búsqueda es Depth-First Search (DFS) y el emparejamiento de patrones se hace con un algoritmo de unificación. 
Las reglas se renombran sobre la marcha usando variables frescas para prevenir conflictos
"""
import sys
import core.knowledge_base as knowledge_base


# Clase para manejar el contador de variables de forma encapsulada
class ContadorVariables:
    """Maneja el contador de variables para renombramientos."""
    def __init__(self):
        self.contador = 0
    
    def siguiente(self):
        """Obtiene el siguiente número de variable."""
        self.contador += 1
        return self.contador
    
    def reiniciar(self):
        """Reinicia el contador a 0."""
        self.contador = 0


# Funciones para manejo de variables
def es_variable(termino):
    """
    Verifica si un término es una variable.
    Ej. Var. Usuario: 'Costo' o Var. Interna: '_P_1'
    """
    return isinstance(termino, str) and (termino[0].isupper() or termino[0] == '_')


def aplicar_sustituciones(termino, sustituciones):
    """
    Aplica de forma recursiva las sustituciones a un término.
    Si ese término es una variable, la sustituye por su valor en el diccionario de sustituciones,
    o si es una tupla, aplica las sustituciones a cada elemento de la tupla.
    Devuelve el término con las sustituciones aplicadas.
    """
    if es_variable(termino):
        while termino in sustituciones:
            termino_nuevo = sustituciones[termino]
            if termino_nuevo == termino:
                break
            termino = termino_nuevo
        return termino
    elif isinstance(termino, tuple):
        return tuple(aplicar_sustituciones(t, sustituciones) for t in termino)
    else:
        return termino

    
def renombrar_variables(termino, sustituciones_renombre, contador):
    """
    Renombra las variables en una regla para evitar colisiones.
    Crea variables "nuevas" únicas.
    """
    if es_variable(termino):
        if termino not in sustituciones_renombre:
            # Las variables internas inician con '_' para reconocerlas
            sustituciones_renombre[termino] = f"_{termino}_{contador.siguiente()}"
        return sustituciones_renombre[termino]
    # Si es una tupla, renombra cada elemento recursivamente 
    elif isinstance(termino, tuple):
        return tuple(renombrar_variables(t, sustituciones_renombre, contador) for t in termino)
    else:
        return termino


# Principio de Estandarización de Variables
def regla_fresca(regla, contador):
    """
    Crea una copia de una regla con todas sus variables renombradas.
    Esto se hace utilizando recursividad en la función renombrar_variables.
    """
    sustituciones_renombre = {}
    # La cabeza de una regla es su conclusión, el cuerpo son sus condiciones
    cabeza_fresca = renombrar_variables(regla['cabeza'], sustituciones_renombre, contador)
    cuerpo_fresca = [renombrar_variables(g, sustituciones_renombre, contador) for g in regla["cuerpo"]]
    return {"cabeza": cabeza_fresca, "cuerpo": cuerpo_fresca}


# Unificación (versión simplificada de Algoritmo de Unificación de Robinson)
def unificar(p1, p2, sustituciones):
    """
    Intenta unificar dos patrones dados un conjunto de sustituciones.
    Devuelve un nuevo diccionario de sustituciones o None si falla.

    Reglas de unificación:
    1. Si p1 y p2 son idénticos, éxito.
    2. Si p1 es una variable, ligar p1 a p2.
    3. Si p2 es una variable, ligar p2 a p1.
    4. Si p1 y p2 son predicados (tuplas), unificar sus argumentos recursivamente.
    5. Si no, falla.
    """
    subs = sustituciones.copy()
    p1 = aplicar_sustituciones(p1, subs)
    p2 = aplicar_sustituciones(p2, subs)
    
    # Éxito si son iguales
    if p1 == p2:
        return subs
    # Si p1 es una variable se liga a p2
    elif es_variable(p1):
        subs[p1] = p2
        return subs
    # Si p2 es una variable se liga a p1
    elif es_variable(p2):
        subs[p2] = p1
        return subs
    # Verificamos que ambas tuplas sean del mismo tamaño
    elif isinstance(p1, tuple) and isinstance(p2, tuple):
        if len(p1) != len(p2):
            return None
        # Unificamos cada elemento de las tuplas recursivamente
        for i in range(len(p1)):
            subs_nuevas = unificar(p1[i], p2[i], subs)
            if subs_nuevas is None:
                return None
            subs = subs_nuevas  # Actualizamos las sustituciones con las nuevas
        return subs
    else:
        return None

    
# Motor de Resolución SLD (Encadenamiento hacia atrás recursivo)
def solve(kb, lista_queries, sustituciones, ruta_derivacion, contador):
    """
    Algoritmo de búsqueda DFS (Depth-First Search).
    Motor de resolución SLD recursivo (generador).
    Busca soluciones que satisfagan la lista de queries (metas).

    Este es el nucleo del motor de inferencia. en este punto, el motor utiliza las reglas para inferencia lógica.
    """
    # Si no hay más queries, hemos encontrado una solución
    if not lista_queries:
        yield sustituciones, ruta_derivacion
        return
    
    # Tomamos la primera query de la lista
    query_actual = lista_queries[0]
    # Las queries restantes
    queries_restantes = lista_queries[1:]
    
    # Aplicamos las sustituciones actuales a la query actual
    query_sustituida = aplicar_sustituciones(query_actual, sustituciones)

    # 1. Intentar unificar con HECHOS 
    for hechos in kb['hechos']:
        subs_unificacion = unificar(query_sustituida, hechos, sustituciones)
        
        # Si la unificación fue exitosa
        if subs_unificacion is not None:
            ruta = ruta_derivacion + [f"Query: {query_sustituida} -> Unifica con HECHO: {hechos}"]
            yield from solve(kb, queries_restantes, subs_unificacion, ruta, contador)

    # 2. Intentar unificar con REGLAS
    for regla in kb['reglas']:
        regla_f = regla_fresca(regla, contador)

        subs_unificacion = unificar(query_sustituida, regla_f['cabeza'], sustituciones)

        # Si la unificación fue exitosa
        if subs_unificacion is not None:
            ruta = ruta_derivacion + [f"Query: {query_sustituida} -> Aplica REGLA: {regla_f['cabeza']}"]
            # Nuevas queries son el cuerpo de la regla más las queries restantes
            nuevas_queries = regla_f['cuerpo'] + queries_restantes
            yield from solve(kb, nuevas_queries, subs_unificacion, ruta, contador)


def sld_solve(kb, query):
    """
    Función principal que inicia la resolución y formatea los resultados.
    Recibe la KB (el programa) y un query (tupla).
    """
    print(f"Iniciando consulta: {query}\n")
    
    # Crea un nuevo contador para esta consulta
    contador = ContadorVariables()

    # Inicializa la lista de queries con el query dado
    query_inicial = [query] 
    soluciones_encontradas = 0

    for i, (solucion, ruta) in enumerate(solve(kb, query_inicial, {}, [], contador)): 
        soluciones_encontradas += 1
        print(f"Solución {soluciones_encontradas}")
        
        variables_query = [t for t in query if es_variable(t) and t[0].isupper()]  # Solo mostrar vars de usuario
        if not variables_query:
            print("Resultado: Verdadero (True)")
        else:
            print("Sustituciones:")
            for var in variables_query:
                valor_final = aplicar_sustituciones(var, solucion)
                print(f"  {var} = {valor_final}")

        print("\nRuta de derivación (paso a paso):")
        for j, paso in enumerate(ruta):
            print(f"  {j+1}. {paso}")
        print("-" * (17 + len(str(soluciones_encontradas))))
    
    if soluciones_encontradas == 0:
        print("Resultado: Falso (False)")
        print("No se encontraron soluciones.")


# --- Ejecución Principal ---
if __name__ == "__main__":
    print("--- Demostración de Consultas LegalMente ---")