# EJERCICIO 2 - PROCESADORES DE LENGUAJE
# Resolución: Primeros, Siguientes, Predicción, Verificación LL(1) y ASDR

EPSILON, EOF = 'ε', '$'

# 1. Definición de la Gramática del Ejercicio 2
GRAMATICA_2 = {
    'S': [['B', 'uno'], ['dos', 'C'], [EPSILON]],
    'A': [['S', 'tres', 'B', 'C'], ['cuatro'], [EPSILON]],
    'B': [['A', 'cinco', 'C', 'seis'], [EPSILON]],
    'C': [['siete', 'B'], [EPSILON]],
}

# =============================================================================
# a, b, c) Cálculo de Conjuntos
# =============================================================================

def get_primeros_cadena(cadena, primeros_map):
    res = set()
    for sim in cadena:
        p = primeros_map.get(sim, {sim})
        res |= (p - {EPSILON})
        if EPSILON not in p: return res
    return res | {EPSILON}

def calcular_conjuntos(gram):
    nts = list(gram.keys())
    prim = {nt: set() for nt in nts}
    
    # a) PRIMEROS (Iterativo hasta punto fijo)
    for _ in range(len(nts) * 2):
        for nt in nts:
            for p in gram[nt]:
                prim[nt] |= get_primeros_cadena(p, prim)
    
    # b) SIGUIENTES
    sig = {nt: set() for nt in nts}; sig['S'].add(EOF)
    for _ in range(len(nts) * 3):
        for nt, prods in gram.items():
            for p in prods:
                for i, B in enumerate(p):
                    if B in nts:
                        res_beta = get_primeros_cadena(p[i+1:], prim)
                        sig[B] |= (res_beta - {EPSILON})
                        if EPSILON in res_beta: sig[B] |= sig[nt]

    # c) PREDICCIÓN
    pred = {}
    for nt, prods in gram.items():
        for p in prods:
            p_first = get_primeros_cadena(p, prim)
            res = (p_first - {EPSILON}) | (sig[nt] if EPSILON in p_first else set())
            pred[(nt, tuple(p))] = res
            
    return prim, sig, pred

# =============================================================================
# e) Implementación de funciones para el ASDR
# =============================================================================

class ASDR_Ejercicio2:
    def __init__(self, tokens):
        self.tokens = tokens + [EOF]
        self.pos = 0
        self.trace = []

    def match(self, exp=None):
        actual = self.tokens[self.pos]
        if exp:
            if actual == exp: 
                self.trace.append(f"  Emparejar: '{actual}'")
                self.pos += 1
            else: raise SyntaxError(f"Se esperaba '{exp}', se halló '{actual}'")
        return actual

    def S(self):
        t = self.match()
        # Basado en Predicción (Simplificado para el ejercicio)
        if t in ('cinco', 'cuatro', 'tres', 'dos', 'uno', 'siete'):
            self.trace.append("S -> B uno"); self.B(); self.match('uno')
        elif t == 'dos':
            self.trace.append("S -> dos C"); self.match('dos'); self.C()
        else:
            self.trace.append("S -> ε")

    def A(self):
        t = self.match()
        if t in ('dos', 'uno', 'cinco', 'siete', 'tres'):
            self.trace.append("A -> S tres B C"); self.S(); self.match('tres'); self.B(); self.C()
        elif t == 'cuatro':
            self.trace.append("A -> cuatro"); self.match('cuatro')
        else:
            self.trace.append("A -> ε")

    def B(self):
        t = self.match()
        if t in ('uno', 'dos', 'tres', 'cuatro', 'cinco', 'siete'):
            self.trace.append("B -> A cinco C seis"); self.A(); self.match('cinco'); self.C(); self.match('seis')
        else:
            self.trace.append("B -> ε")

    def C(self):
        if self.match() == 'siete':
            self.trace.append("C -> siete B"); self.match('siete'); self.B()
        else:
            self.trace.append("C -> ε")

    def parse(self):
        try:
            self.S()
            return self.match() == EOF, self.trace
        except Exception as e: return False, [str(e)]

# =============================================================================
# d) Verificación LL(1) e Impresión Final
# =============================================================================

def imprimir_solucion():
    print("=== RESOLUCIÓN EJERCICIO 2 ===")
    
    prim, sig, pred = calcular_conjuntos(GRAMATICA_2)

    print("\na) CONJUNTOS DE PRIMEROS:")
    for nt in GRAMATICA_2: print(f"   PRIM({nt:<2}) = {sorted(list(prim[nt]))}")

    print("\nb) CONJUNTOS DE SIGUIENTES:")
    for nt in GRAMATICA_2: print(f"   SIG({nt:<2})  = {sorted(list(sig[nt]))}")

    print("\nc) CONJUNTOS DE PREDICCIÓN:")
    for (nt, prod), p_set in pred.items():
        print(f"   PRED({nt} -> {' '.join(prod) if prod else EPSILON:<15}) = {sorted(list(p_set))}")

    print("\nd) ¿ES LL(1)?")
    es_ll1 = True
    for nt in GRAMATICA_2:
        reglas = [p_set for (n, p), p_set in pred.items() if n == nt]
        for i in range(len(reglas)):
            for j in range(i+1, len(reglas)):
                inter = reglas[i] & reglas[j]
                if inter:
                    print(f"   (!) Conflicto en '{nt}': intersección {inter}")
                    es_ll1 = False
    
    if not es_ll1:
        print("   Resultado: NO ES LL(1).")
        print("   Razón: Existe recursividad indirecta (S->B, B->A, A->S) y los conjuntos")
        print("   de predicción de reglas alternativas tienen símbolos comunes.")
    else:
        print("   Resultado: La gramática ES LL(1).")

    print("\ne) PRUEBA DEL ASDR (Implementación de funciones):")
    prueba = ['dos', 'siete', 'uno'] # Ejemplo de entrada
    ok, traza = ASDR_Ejercicio2(prueba).parse()
    print(f"   Entrada: {prueba}")
    print(f"   Estado: {'ACEPTADA ✓' if ok else 'RECHAZADA ✗'}")

if __name__ == "__main__":
    imprimir_solucion()
