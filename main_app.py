import motor_inferencia as motor  # Importamos tu motor lógico
import knowledge_base as kb       # Importamos tu Base de Conocimientos

# --- Variables de Sesión ---
# Estas variables guardan el estado de la conversación
KB_COMPLETA = kb.KB_LEGALMENTE.copy()
HECHOS_SESION = [] # Aquí guardaremos hechos nuevos, como la residencia del usuario
            
# --- Implementación de Reglas de Validación (Capa de Aplicación) ---

def listar_tramites_disponibles_no_residentes():
    """
    Lista todos los trámites que sí se pueden hacer fuera de Ensenada
    """
    print(f"\n","+"*10, " Lista de trámites ", "+"*10)
    
    # Consultando todos los trámites que no ocupan residencia local
    query_no_residencia = ('no_requiere_residencia_local', 'Tramite')
    
    tramites_disponibles = []
    
    # Se usa el motor para encontrar todos los trámites con no_requiere_residencia_local
    try:
        for solucion, _ in motor.solve(KB_COMPLETA, [query_no_residencia], {}, []):
            tramite = solucion.get('Tramite')
            if tramite and tramite not in tramites_disponibles:
                tramites_disponibles.append(tramite)
    except:
        pass
    
    if tramites_disponibles:
        for i, tramite in enumerate(sorted(tramites_disponibles), 1):
            print(f"{i:2d}. {tramite}")
        
    #     print(f"\nTotal: {len(tramites_disponibles)} trámites disponibles")
    # else:
    #     print("No se encontraron trámites disponibles sin restricción de residencia")
    
    return tramites_disponibles

def validar_caracteres_tramite(tramite):
    """
    Implementa Regla 5 ("caracteres sin sentido")
    Un trámite válido solo debe tener letras minúsculas y guion bajo.
    """
    if not tramite: # Si está vacío
        return False
    # Verificamos que solo tenga los caracteres permitidos
    for char in tramite:
        if not ('a' <= char <= 'z' or char == '_'):
            return False
    return True

def validar_tramite_en_bc(tramite):
    """
    Implementa Regla 4 y 14 ("no corresponde a uno de los trámites")
    Verifica si el trámite existe en la Base de Conocimientos.
    """
    # Usamos tu mismo motor 'solve' para una consulta rápida
    query_valida = ('es_tramite_valido', tramite)
    
    # solve devuelve un generador, intentamos obtener al menos una solución
    try:
        next(motor.solve(KB_COMPLETA, [query_valida], {}, []))
        return True # Éxito, el trámite existe
    except StopIteration:
        return False # Falla, el trámite no existe

def gestionar_residencia():
    """
    Implementa Regla 6 ("resides en ensenada?")
    Pregunta al usuario y añade un hecho a la sesión.
    """
    global HECHOS_SESION
    
    while True:
        print("\n--- Validación de Residencia (Regla 6) ---")
        respuesta = input("¿Resides actualmente en Ensenada, B.C.? (s/n): ").strip().lower()

        if respuesta == 's':
            # Añadimos un hecho temporal solo para esta sesión
            HECHOS_SESION.append(('reside_en_ensenada', 'usuario_actual'))
            print("Validado. Tienes acceso a trámites locales.")
            print(f"\n","+"*10, " Lista de trámites ", "+"*10)
            print('1. acta_nacimiento')
            print('2. expedicion_licencia')
            print('3. revalidacion_licencia')
            print('4. refrendo_tarjeta_circulacion')
            print('5. constancia_antecedentes_penales')
            print('6. reposicion_licencia')
            print('7. alta_vehiculo')
            print('8. baja_vehiculo')
            print('9. cambio_propietario_vehiculo')
            print('10. reposicion_tarjeta_circulacion')
            print('11. reposicion_placas_circulacion')
            print('12. permiso_traslado_vehicular')
            print('13. acta_matrimonio')
            print('14. acta_defuncion')
            print('15. pasaporte')
            break
        elif respuesta == 'n':
            print("Advertencia: No podrás realizar trámites que requieren residencia local.")
            # Mostrar trámites disponibles para no residentes
            tramites_disponibles = listar_tramites_disponibles_no_residentes()

            break
        else:
            # Implementa Regla 5 ("caracteres sin sentido" en la pregunta)
            print("Error: Respuesta no válida. Por favor, introduce 's' o 'n'.")

def checar_permiso_tramite(tramite):
    """
    Verifica si el usuario CUMPLE con los requisitos de residencia PARA ESE TRÁMITE.
    """
    # Creamos una KB temporal que incluye los hechos de la sesión
    kb_temporal = KB_COMPLETA.copy()
    kb_temporal['hechos'] = KB_COMPLETA['hechos'] + HECHOS_SESION
    
    # Preguntamos al motor: ¿Es el 'usuario_actual' apto para este 'tramite'?
    query_apto = ('es_apto_para_tramite', 'usuario_actual', tramite)
    
    try:
        next(motor.solve(kb_temporal, [query_apto], {}, []))
        return True # Es apto
    except StopIteration:
        return False # No es apto (ej. trámite es local y no reside)

# --- Aplicación Principal (CLI) ---
def main():
    """
    Bucle principal de la aplicación interactiva
    """
    print("====================================")
    print("  Bienvenido a LegalMente v0.5    ")
    print("====================================")
    print("Motor de Inferencia SLD conectado.")
    
    # 1. Validar residencia al inicio de la sesión
    gestionar_residencia()

    # 2. Bucle principal de consultas
    while True:
        print("\n¿Qué deseas consultar?")
        print("  1. Costos de un trámite")
        print("  2. Requisitos de un trámite")
        print("  3. Salir")
        opcion = input("Elige una opción (1-3): ").strip()

        if opcion == '3':
            print("Gracias por usar LegalMente. ¡Hasta pronto!")
            break
        
        if opcion in ('1', '2'):            
            # --- Validación de Entrada (Reglas 4, 5, 14) ---
            tramite = input("Escribe el nombre del trámite (ej. expedicion_licencia): ").strip().lower()
            
            # Regla 5: ¿Caracteres válidos?
            if not validar_caracteres_tramite(tramite):
                print(f"Error (Regla 5): El formato '{tramite}' es inválido. Solo usa minúsculas y '_'.")
                continue # Vuelve al menú sin cortar la ejecución

            # Regla 4/14: ¿Trámite existe?
            if not validar_tramite_en_bc(tramite):
                print(f"Error (Regla 4/14): El trámite '{tramite}' no se encuentra en la base de conocimientos.")
                continue # Vuelve al menú
            
            # --- Validación de Lógica (Regla 6) ---
            if not checar_permiso_tramite(tramite):
                print(f"Error (Regla 6): No cumples los requisitos de residencia para '{tramite}'.")
                continue # Vuelve al menú

            # --- Si pasa todas las validaciones, construye y ejecuta la query ---
            
            # Combinamos la KB original con los hechos de la sesión
            kb_para_solver = KB_COMPLETA.copy()
            kb_para_solver['hechos'] = KB_COMPLETA['hechos'] + HECHOS_SESION

            if opcion == '1':
                # Consultar Costos
                query = ('costo', tramite, 'Descripcion', 'Monto')
                print(f"\nConsultando costos para: {tramite}")
                motor.sld_solve(kb_para_solver, query)
                
            elif opcion == '2':
                # Consultar Requisitos
                query = ('requiere', tramite, 'Requisito')
                print(f"\nConsultando requisitos para: {tramite}")
                motor.sld_solve(kb_para_solver, query)
        
        else:
            # Regla 5 (aplicada al menú)
            print("Opción no válida. Por favor, introduce un número del 1 al 3.")

# --- Ejecución Principal ---
if __name__ == "__main__":
    main()
