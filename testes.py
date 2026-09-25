"""Bateria de testes da MiniLang — comportamento completo do pipeline."""

import contextlib
import io

from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

def parse(codigo):
    return Parser(tokenize(codigo)).parse()

def run(codigo):
    itp = Interpreter()
    for statement in parse(codigo):
        itp.evaluate(statement)
    return itp

def mem(codigo):
    return run(codigo).memory

def err(codigo):
    try:
        ast = parse(codigo)
    except SyntaxError as e:
        return f"SyntaxError: {e}"
    itp = Interpreter()
    for statement in ast:
        try:
            itp.evaluate(statement)
        except Exception as e:
            return f"{type(e).__name__}: {e}"
    return "SEM ERRO"

verificacoes = 0

def check(cond, label):
    global verificacoes
    assert cond, f"FALHOU: {label}"
    verificacoes += 1

# ===== 1. Aritmética e atribuição =====
check(mem("x = 2 + 3 * 4;")["x"] == 14, "precedência")
check(mem("x = (2 + 3) * 4;")["x"] == 20, "parênteses")
check(mem("a = 2; b = a * a; c = b + 1;")["c"] == 5, "variáveis em cadeia")
check(err("y = 1; x = z;").startswith("NameError"), "NameError de variável indefinida")
check(err("x = 1 / 0;").startswith("ZeroDivisionError"), "divisão por zero")

# ===== 2. Léxico =====
tipos = [t.tipo for t in tokenize("if (a <= 5) { b = a != 6; }")]
esperado = ["IF", "ABRE_PARENTESES", "IDENTIFICADOR", "MENOR_IGUAL", "NUMERO",
            "FECHA_PARENTESES", "ABRE_CHAVES", "IDENTIFICADOR", "ATRIBUICAO",
            "IDENTIFICADOR", "DIFERENCA", "NUMERO", "PONTO_E_VIRGULA", "FECHA_CHAVES"]
check(tipos == esperado, "sequência de tokens dos comparadores")
check(mem("iffy = 5;")["iffy"] == 5, "identificador contendo 'if'")
check(err("if = 1;").startswith("SyntaxError"), "palavra reservada como variável")

# ===== 3. Comparadores =====
for expr, resultado in [("5 == 5", 1), ("5 == 6", 0), ("4 != 5", 1), ("4 != 4", 0),
                        ("3 <= 3", 1), ("4 <= 3", 0), ("3 >= 3", 1), ("2 >= 3", 0),
                        ("1 < 2", 1), ("2 < 1", 0), ("2 > 1", 1), ("1 > 2", 0)]:
    check(mem(f'r = 0; if ({expr}) {{ r = 1; }}')["r"] == resultado, f"comparador {expr}")
check(err("x = 2 < 1 < 3;").startswith("SyntaxError"), "cadeia de comparações rejeitada")
check(mem("y = 3; x = y == 3;")["x"] == True, "atribuição de comparação")

# ===== 4. if / else / else if =====
check(mem("x = 0; if (1 < 2) { x = 10; }")["x"] == 10, "if verdadeiro")
check(mem("x = 0; if (1 > 2) { x = 10; }")["x"] == 0, "if falso sem else")
check(mem("x = 0; if (1 > 2) { x = 10; } else { x = 99; }")["x"] == 99, "else")
check(mem("n = 7; r = 0; if (n == 1) { r = 10; } else if (n == 7) { r = 20; } else { r = 30; }")["r"] == 20, "else-if do meio")
check(mem("n = 9; r = 0; if (n == 1) { r = 10; } else if (n == 7) { r = 20; } else { r = 30; }")["r"] == 30, "else final")
check(mem("n = 1; r = 0; if (n == 1) { r = 10; } else if (n == 7) { r = 20; } else { r = 30; }")["r"] == 10, "else-if primeiro")
check(mem("a = 0; if (1 == 1) { if (1 == 2) { a = 1; } else { a = 2; } }")["a"] == 2, "else liga ao if mais próximo")
check(mem("f2 = 5 > 3; r = 0; if (f2) { r = 9; }")["r"] == 9, "if com variável booleana")
check(mem("r = 0; if ((2 + 3) * 2 == 10) { r = 5; }")["r"] == 5, "condição entre parênteses")
check(mem("a = 2; b = 3; if (a * b == a + b + 1) { r0 = 1; }")["r0"] == 1, "aritmética na condição")
check(mem("a = 0; b = 0; if (1 == 1) { a = 1; b = 2; }")["b"] == 2, "bloco com duas instruções")
check(parse("if (1 == 1) { }") is not None, "bloco vazio")

# ===== 5. for =====
check(mem("s = 0; for (i = 1; i <= 10; i = i + 1) { s = s + i; }")["s"] == 55, "for soma")
check(mem("c = 0; for (i = 5; i > 0; i = i - 1) { c = c + 1; }")["c"] == 5, "for regressivo")
check(mem("c = 0; for (i = 0; i < 10; i = i + 3) { c = c + 1; }")["c"] == 4, "for com passo")
check(mem("s = 7; for (i = 5; i < 1; i = i + 1) { s = 0; }")["s"] == 7, "for nunca executado")
check(mem("t = 0; for (i = 1; i <= 6; i = i + 1) { if (i > 3) { t = t + 10; } }")["t"] == 30, "if dentro de for")
check(mem("c = 0; for (i = 1; i <= 3; i = i + 1) { for (j = 1; j <= 3; j = j + 1) { c = c + 1; } }")["c"] == 9, "for aninhado")
check(mem("for (i = 0; i < 3; i = i + 1) { x = i; } y = i;")["y"] == 3, "variável do for persiste")
check(err("for (i = 0; 1 == 1; i = i + 1) { x = 1; }").startswith("RuntimeError"), "for infinito guardado")

# ===== 6. while =====
check(mem("s = 0; i = 1; while (i <= 10) { s = s + i; i = i + 1; }")["s"] == 55, "while soma")
check(mem("c = 0; i = 5; while (i > 0) { c = c + 1; i = i - 1; }")["c"] == 5, "while regressivo")
check(mem("s = 9; while (s < 1) { s = 99; }")["s"] == 9, "while nunca executado")
check(mem("c = 0; i = 0; j = 0; while (i < 3) { j = 0; while (j < 2) { c = c + 1; j = j + 1; } i = i + 1; }")["c"] == 6, "while aninhado")
check(mem("t = 0; while (t < 5) { if (t == 2) { t = t + 10; } else { t = t + 1; } }")["t"] == 12, "if dentro de while")
check(err("z = 0; while (z >= 0) { z = z + 1; }").startswith("RuntimeError"), "while infinito guardado")
check(mem("c1 = 0; function contou() { return 1; } while (c1 < 3) { c1 = c1 + contou(); }")["c1"] == 3, "função na condição do while")

# ===== 7. funções =====
check(mem("function dobro(n) { return n * 2; } x = dobro(21);")["x"] == 42, "função simples")
check(mem("function somarTudo(a,b,c) { return a + b + c; } x = somarTudo(1,2,3);")["x"] == 6, "três parâmetros")
check(mem("function dobro(n) { return n * 2; } x = dobro(dobro(5));")["x"] == 20, "chamada aninhada")
check(mem("function f(n) { if (n <= 1) { return 1; } return n * f(n - 1); } x = f(5);")["x"] == 120, "recursão fatorial")
check(mem("function profundo(n) { if (n == 0) { return 0; } return profundo(n - 1); } x = profundo(10);")["x"] == 0, "recursão com dez níveis")
check(mem("function somaAte(n) { s = 0; i = 1; while (i <= n) { s = s + i; i = i + 1; } return s; } x = somaAte(10);")["x"] == 55, "while dentro de função")
check(mem("total = 0; function guarda(v) { total = total + v; return total; } guarda(5);")["total"] == 5, "acumulador atualiza global")
check(mem("soma = 0; function passo(n) { soma = soma + n; return soma; } passo(1); passo(2); passo(3);")["soma"] == 6, "chamadas em sequência")
local_leak = run("g = 7; function f(n) { local = n; return local; } f(1);")
check("local" not in local_leak.memory, "variável local não vaza ao global")
check(mem("g = 7; function f(n) { return n + g; } x = f(1);")["x"] == 8, "leitura de global em função")
check(mem("g = 7; function f(n) { g = n; return g; } f(3);")["g"] == 3, "escrita em global existente")
check(run("function f() { return 8; } x = f() + 1;").memory["x"] == 9, "chamada em expressão")
check(mem("function f() { return; } x = f();")["x"] is None, "return sem valor")
check(mem("function identidade(x) { return x; } a = identidade(identidade(identidade(7)));")["a"] == 7, "identidade tripla")
check(mem("b = 0; function param(a) { b = a * 2; return b; } x = param(4);")["b"] == 8, "if dentro de função")
check(err("function f(a,b) { return a; } x = f(1);").startswith("TypeError"), "aridade errada")
check(err("x = f() + 1; function f() { return 8; }").startswith("NameError"), "função precisa ser definida antes")
check(err("x = inexistente(1);").startswith("NameError"), "função inexistente")
check("return" in err("return 1;").lower(), "return fora de função é recusado")

# ===== 8. Erros de sintaxe =====
malformados = [
    "if x { a = 1; }",
    "for (i = 1; i < 3) { }",
    "for i = 1; i < 3; i = i + 1) { }",
    "if (a < b) a = 1;",
    "if (a < b) { a = 1; } else x = 2;",
    "for (; i < 3; i = i + 1) { }",
    "x = 1 == ;",
    "for (i = 1; i < 3; i = i + 1) { a = 1;",
    "while x { a = 1; }",
    "function f( { return 1; }",
    "x = dobro(;",
]
for malformado in malformados:
    check(err(malformado).startswith("SyntaxError"), f"sintaxe recusada: {malformado}")

# ===== 9. AST printer (todos os nós, sem erro) =====
import io
from ast_printer import print_ast
captura = io.StringIO()
with contextlib.redirect_stdout(captura):
    mapa_ast = {
        "Assignment": "x = (1 + 2) * 3;",
        "If": "if (1 == 2) { a = 1; } else { a = 2; }",
        "For": "for (i = 0; i < 3; i = i + 1) { x = i; }",
        "While": "while (x < 2) { x = x + 1; }",
        "FunctionDef": "function f(a, b) { return a + b; }",
        "Call": "x = f(1, 2);",
        "Return": "function f() { return 1; }",
    }
    for nome, codigo in mapa_ast.items():
        instrucoes = parse(codigo)
        for statement in instrucoes:
            print_ast(statement)
        saida = captura.getvalue()
        assert nome in saida, f"print_ast não mostrou {nome}"
        verificacoes += 1

print(f"{verificacoes} VERIFICAÇÕES PASSARAM")
