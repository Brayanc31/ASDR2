"""
Ejercicio 3 - Análisis Sintáctico Descendente (ASD)
Gramática:
    S → A B C
    S → S uno
    A → dos B C
    A → ε
    B → C tres
    B → ε
    C → cuatro B
    C → ε
"""

EPSILON = 'ε'
EOF = '$'

# =============================================================================
# PASO a) Eliminar recursividad por la izquierda
# =============================================================================

GRAMATICA_ORIGINAL_3 = {
    'S':  [['A', 'B', 'C'], ['S', 'uno']],
    'A':  [['dos', 'B', 'C'], [EPSILON]],
    'B':  [['C', 'tres'], [EPSILON]],
    'C':  [['cuatro', 'B'], [EPSILON]],
}

NO_TERMINALES_ORIG_3 = ['S', 'A', 'B', 'C']
TERMINALES_3 = {'uno', 'dos', 'tres', 'cuatro', EOF}

def eliminar_recursividad_izquierda(gramatica, no_terminales):
    nueva_gramatica = {}
    nuevos_nt = []

    for A in no_terminales:
        reglas = gramatica[A]
        recursivas = [p[1:] for p in reglas if p[0] == A]
        no_recursivas = [p for p in reglas if p[0] != A]

        if not recursivas:
            nueva_gramatica[A] = reglas
            nuevos_nt.append(A)
        else:
            Ap = A + "'"
            nuevos_nt.extend([A, Ap])
            nueva_gramatica[A] = [beta + [Ap] for beta in no_recursivas]
            nueva_gramatica[Ap] = [alpha + [Ap] for alpha in recursivas] + [[EPSILON]]

    return nueva_gramatica, nuevos_nt

# =============================================================================
# PASO b) Cálculo de Conjuntos (PRIMEROS, SIGUIENTES, PREDICCIÓN)
# =============================================================================

def primeros_de_cadena(cadena, primeros):
    resultado = set()
    for simbolo in cadena:
        p = primeros.get(simbolo, {simbolo})
        resultado |= (p - {EPSILON})
        if EPSILON not in p: return resultado
    return resultado | {EPSILON}

def calcular_conjuntos(gramatica, no_terminales, terminales):
    primeros = {t: {t} for t in terminales}
    primeros[EPSILON] = {EPSILON}
    for nt in no_terminales: primeros[nt] = set()

    # PRIMEROS
    for _ in range(len(no_terminales)):
        for nt in no_terminales:
            for prod in gramatica[nt]:
                primeros[nt] |= primeros_de_cadena(prod, primeros)

    # SIGUIENTES
    siguientes = {nt: set() for nt in no_terminales}
    siguientes[no_terminales[0]].add(EOF)
    for _ in range(len(no_terminales) * 2):
        for nt in no_terminales:
            for prod in gramatica[nt]:
                for i, B in enumerate(prod):
                    if B in no_terminales:
                        beta = prod[i+1:]
                        prim_beta = primeros_de_cadena(beta, primeros)
                        siguientes[B] |= (prim_beta - {EPSILON})
                        if EPSILON in prim_beta: siguientes[B] |= siguientes[nt]

    # PREDICCIÓN
    prediccion = {}
    for nt in no_terminales:
        for prod in gramatica[nt]:
            prim = primeros_de_cadena(prod, primeros)
            pred = (prim - {EPSILON}) | (siguientes[nt] if EPSILON in prim else set())
            prediccion[(nt, tuple(prod))] = pred

    return primeros, siguientes, prediccion

# =============================================================================
# PASO b5) Analizador Sintáctico Descendente Recursivo (ASDR)
# =============================================================================

class ASDR:
    def __init__(self, tokens):
        self.tokens = tokens + [EOF]
        self.pos = 0
        self.token = self.tokens[0]
        self.traza = []

    def emparejar(self, esperado):
        if self.token == esperado:
            self.traza.append(f"  [emparejar] '{esperado}' ✓")
            self.pos += 1
            self.token = self.tokens[self.pos]
        else:
            raise SyntaxError(f"Se esperaba '{esperado}', se encontró '{self.token}'")

    def S(self):
        self.traza.append("S → A B C S'")
        self.A(); self.B(); self.C(); self.Sp()

    def Sp(self):
        if self.token == 'uno':
            self.traza.append("S' → uno S'")
            self.emparejar('uno'); self.Sp()
        else:
            self.traza.append("S' → ε")

    def A(self):
        if self.token == 'dos':
            self.traza.append("A → dos B C")
            self.emparejar('dos'); self.B(); self.C()
        else:
            self.traza.append("A → ε")

    def B(self):
        # PRED(B → C tres) = {cuatro, tres}
        if self.token in ('cuatro', 'tres'):
            self.traza.append("B → C tres")
            self.C(); self.emparejar('tres')
        else:
            self.traza.append("B → ε")

    def C(self):
        if self.token == 'cuatro':
            self.traza.append("C → cuatro B")
            self.emparejar('cuatro'); self.B()
        else:
            self.traza.append("C → ε")

    def parse(self):
        try:
            self.S()
            return self.token == EOF
        except SyntaxError as e:
            self.traza.append(f"ERROR: {e}")
            return False

# =============================================================================
# IMPRESIÓN DE RESULTADOS
# =============================================================================

def imprimir_ejercicio():
    print("=== RESOLUCIÓN EJERCICIO 3 ===")
    
    # a) Transformación
    gram_t, nts_t = eliminar_recursividad_izquierda(GRAMATICA_ORIGINAL_3, NO_TERMINALES_ORIG_3)
    print("\na) Gramática sin recursividad izquierda:")
    for nt in nts_t:
        for prod in gram_t[nt]:
            print(f"   {nt} → {' '.join(prod)}")

    # b) Conjuntos
    prim, sig, pred = calcular_conjuntos(gram_t, nts_t, TERMINALES_3)
    print("\nb) Conjuntos PRIMEROS:")
    for nt in nts_t: print(f"   PRIM({nt:<2}) = {sorted(list(prim[nt]))}")

    print("\nb) Conjuntos SIGUIENTES:")
    for nt in nts_t: print(f"   SIG({nt:<2})  = {sorted(list(sig[nt]))}")

    print("\nb) Conjuntos de PREDICCIÓN:")
    for (nt, prod), p_set in pred.items():
        print(f"   PRED({nt} → {' '.join(prod):<12}) = {sorted(list(p_set))}")

    # LL(1) Check
    print("\nb) ¿Es LL(1)?")
    es_ll1 = True
    for nt in nts_t:
        preds = [p_set for (n, p), p_set in pred.items() if n == nt]
        for i in range(len(preds)):
            for j in range(i+1, len(preds)):
                if preds[i] & preds[j]: es_ll1 = False
    print(f"   Resultado: {'SÍ' if es_ll1 else 'NO'} es LL(1)")

    # Prueba ASDR
    print("\nb) Prueba del ASDR:")
    prueba = ['dos', 'cuatro', 'tres', 'cuatro', 'uno']
    parser = ASDR(prueba)
    exito = parser.parse()
    print(f"   Entrada: {prueba}")
    print(f"   Resultado: {'ACEPTADA ✓' if exito else 'RECHAZADA ✗'}")
    print("   Traza de derivación:")
    for linea in parser.traza: print(f"    {linea}")

if __name__ == "__main__":
    imprimir_ejercicio()
