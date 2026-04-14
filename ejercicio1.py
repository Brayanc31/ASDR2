# EJERCICIO 1 

EPSILON, EOF = 'ε', '$' 

#  Definición de la Gramática Original 
GRAM_ORIGINAL = { 
    'S': [['A', 'B', 'C'], ['D', 'E']], 
    'A': [['dos', 'B', 'tres'], [EPSILON]], 
    'B': [['B', 'cuatro', 'C', 'cinco'], [EPSILON]], 
    'C': [['seis', 'A', 'B'], [EPSILON]], 
    'D': [['uno', 'A', 'E'], ['B']], 
    'E': [['tres']], 
} 


# Eliminar la recursividad por la izquierda 

def transformar_gramatica(gram): 
    nueva = {} 
    for nt, prods in gram.items(): 
        rec = [p[1:] for p in prods if p[0] == nt] 
        no_rec = [p for p in prods if p[0] != nt] 
        
        if rec: 
            nt_p = nt + "'" 
            nueva[nt] = [p + [nt_p] for p in no_rec] 
            nueva[nt_p] = [p + [nt_p] for p in rec] + [[EPSILON]] 
        else: 
            nueva[nt] = prods 
    return nueva 

 
# Cálculo de Conjuntos (Primeros, Siguientes, Predicción) 
 
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
    
    # PRIMEROS 
    for _ in range(len(nts)): 
        for nt in nts: 
            for p in gram[nt]: 
                prim[nt] |= get_primeros_cadena(p, prim) 
    
    # SIGUIENTES 
    sig = {nt: set() for nt in nts}; sig['S'].add(EOF) 
    for _ in range(len(nts) * 2): 
        for nt, prods in gram.items(): 
            for p in prods: 
                for i, B in enumerate(p): 
                    if B in nts: 
                        res_beta = get_primeros_cadena(p[i+1:], prim) 
                        sig[B] |= (res_beta - {EPSILON}) 
                        if EPSILON in res_beta: sig[B] |= sig[nt] 

    # PREDICCIÓN 
    pred = {} 
    for nt, prods in gram.items(): 
        for p in prods: 
            p_first = get_primeros_cadena(p, prim) 
            res = (p_first - {EPSILON}) | (sig[nt] if EPSILON in p_first else set()) 
            pred[(nt, tuple(p))] = res 
            
    return prim, sig, pred 


#Analizador Sintáctico Descendente Recursivo (ASDR) 

class ASDR: 
    def __init__(self, tokens, pred_map): 
        self.tokens = tokens + [EOF] 
        self.pos = 0 
        self.pred = pred_map 
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
        if t in ('dos', 'seis', 'tres', EOF): 
            self.trace.append("S -> A B C"); self.A(); self.B(); self.C() 
        elif t == 'uno': 
            self.trace.append("S -> D E"); self.D(); self.E() 
        else: 
            self.trace.append("S -> A B C (Conflicto en 'cuatro' resuelto)"); self.A(); self.B(); self.C() 

    def A(self): 
        if self.match() == 'dos': 
            self.trace.append("  A -> dos B tres"); self.match('dos'); self.B(); self.match('tres') 
        else: self.trace.append("  A -> ε") 

    def B(self): 
        self.trace.append("  B -> B'"); self.Bp() 

    def Bp(self): 
        if self.match() == 'cuatro': 
            self.trace.append("    B' -> cuatro C cinco B'"); 
            self.match('cuatro'); self.C(); self.match('cinco'); self.Bp() 
        else: self.trace.append("    B' -> ε") 

    def C(self): 
        if self.match() == 'seis': 
            self.trace.append("  C -> seis A B"); self.match('seis'); self.A(); self.B() 
        else: self.trace.append("  C -> ε") 

    def D(self): 
        if self.match() == 'uno': 
            self.trace.append("  D -> uno A E"); self.match('uno'); self.A(); self.E() 
        else: 
            self.trace.append("  D -> B"); self.B() 

    def E(self): 
        self.trace.append("  E -> tres"); self.match('tres') 

    def parse(self): 
        try: 
            self.S() 
            if self.match() == EOF: return True 
            return False 
        except Exception as e: 
            self.trace.append(f"ERROR: {str(e)}") 
            return False 


# Salida de Resultados con Pruebas Aumentadas

def imprimir_solucion(): 
    print("=== TAREA: EJERCICIO 1 ===") 
    
    # Paso a 
    g_t = transformar_gramatica(GRAM_ORIGINAL) 
    print("\na) GRAMÁTICA SIN RECURSIVIDAD IZQUIERDA:") 
    for nt, prods in g_t.items(): 
        print(f"   {nt} -> {' | '.join([' '.join(p) for p in prods])}") 

    prim, sig, pred = calcular_conjuntos(g_t) 

    # Paso b (Primeros y Siguientes) 
    print("\nb) CONJUNTOS DE PRIMEROS:") 
    for nt in g_t: print(f"   PRIM({nt:<2}) = {sorted(list(prim[nt]))}") 

    print("\nb) CONJUNTOS DE SIGUIENTES:") 
    for nt in g_t: print(f"   SIG({nt:<2})  = {sorted(list(sig[nt]))}") 

    # Paso b (Predicción) 
    print("\nb) CONJUNTOS DE PREDICCIÓN:") 
    for (nt, prod), p_set in pred.items(): 
        print(f"   PRED({nt} -> {' '.join(prod):<15}) = {sorted(list(p_set))}") 

    # Paso b (LL1) 
    print("\nb) ¿ES LL(1)?") 
    es_ll1 = True 
    for nt in g_t: 
        reglas = [p_set for (n, p), p_set in pred.items() if n == nt] 
        for i in range(len(reglas)): 
            for j in range(i+1, len(reglas)): 
                inter = reglas[i] & reglas[j] 
                if inter: 
                    print(f"   (!) Conflicto en '{nt}': intersección no vacía {inter}") 
                    es_ll1 = False 
    print(f"   Resultado: La gramática {'ES' if es_ll1 else 'NO ES'} LL(1).") 

   
    print("\nb) IMPLEMENTACIÓN ASDR (Batería de Pruebas):") 
    
    pruebas = [
        (['uno', 'dos', 'tres', 'tres'], "Ruta S->DE con A derivando en dos..."),
        (['dos', 'tres'], "Ruta S->ABC con B y C derivando en ε"),
        (['cuatro', 'seis', 'cinco'], "Ruta S->ABC con recursividad en B'"),
        (['uno', 'tres'], "Ruta S->DE con D->B y B->ε"),
        (['dos', 'cuatro', 'cinco', 'tres'], "Combinación de A y B'")
    ]

    for entrada, desc in pruebas:
        print(f"\n--- Prueba: {desc} ---")
        analizador = ASDR(entrada, pred) 
        resultado = analizador.parse() 
        print(f"   Entrada: {entrada}") 
        print(f"   Resultado: {'ACEPTADA ✓' if resultado else 'RECHAZADA ✗'}") 
        print("   Derivación:") 
        for linea in analizador.trace: print(f"      {linea}") 

if __name__ == "__main__": 
    imprimir_solucion()
