# Analizador Sintáctico Descendente - Taller de Compiladores


## Contenido

El repositorio incluye la resolución detallada de los siguientes ejercicios:

1.  **Ejercicio 1**: Gramática con múltiples producciones iniciales y recursividad por la izquierda en el no terminal `B`.
2.  **Ejercicio 2**: Gramática con recursividad indirecta y análisis de ambigüedad LL(1).
3.  **Ejercicio 3**: Gramática transformada para manejar flujos de tokens específicos (`uno`, `dos`, `tres`, `cuatro`).

## 🛠️ Funcionalidades del Código

Cada script sigue un pipeline de compilación clásico:
* **Transformación**: Eliminación automática de recursividad por la izquierda.
* **Análisis de Conjuntos**: 
    * **PRIMEROS**: Símbolos terminales con los que puede empezar una derivación.
    * **SIGUIENTES**: Terminales que pueden aparecer inmediatamente a la derecha de un no terminal.
    * **PREDICCIÓN**: Conjuntos utilizados por el analizador para decidir qué regla aplicar.
* **Verificación LL(1)**: Comprobación de intersecciones vacías entre conjuntos de predicción.
* **ASDR**: Implementación funcional mediante funciones recursivas que validan cadenas de tokens.

## 📋 Requisitos

* **Lenguaje**: Python 3.x
* **Librerías**: No requiere librerías externas (Standard Library únicamente).

## 💻 Ejecución y Pruebas

Para ejecutar cualquiera de los ejercicios y ver los resultados junto con la batería de pruebas extendida, usa:

```bash
python ejercicio1.py
