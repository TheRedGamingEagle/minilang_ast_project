"""Converte o texto da MiniLang em uma sequência de tokens."""

from token_model import Token

# Palavras reservadas da estrutura de controle da linguagem.
PALAVRAS_RESERVADAS = {
    "if": "IF", "else": "ELSE", "for": "FOR"
}

# Relaciona cada operador ou delimitador ao tipo usado pelo parser.
MAPA = {
    "=": "ATRIBUICAO", "+": "SOMA", "-": "SUBTRACAO",
    "*": "MULTIPLICACAO", "/": "DIVISAO", ";": "PONTO_E_VIRGULA",
    "(": "ABRE_PARENTESES", ")": "FECHA_PARENTESES",
    "{": "ABRE_CHAVES", "}": "FECHA_CHAVES",
    "<": "MENOR", ">": "MAIOR"
}

# Operadores de comparação de dois caracteres, casados antes do "=" simples.
# Cada um recebe um marcador temporário, seguido de bytes nulos, para que o
# espaçamento dos símbolos de um caractere não o quebra em dois.
MARCADOR_DE_SIMBOLO = {"==": "EQ", "!=": "NE", "<=": "LE", ">=": "GE"}

# Tipo e valor do token produzido por cada marcador.
TOKEN_DE_MARCADOR = {
    "EQ": ("IGUALDADE", "=="), "NE": ("DIFERENCA", "!="),
    "LE": ("MENOR_IGUAL", "<="), "GE": ("MAIOR_IGUAL", ">=")
}

# Símbolos de um caractere que precisam de espaços ao redor para serem separados.
SIMBOLOS = list(MAPA.keys())

def tokenize(codigo: str) -> list[Token]:
    # Protege os operadores dobrados com marcadores temporários.
    for simbolo, marcador in MARCADOR_DE_SIMBOLO.items():
        codigo = codigo.replace(simbolo, f" \x00{marcador}\x00 ")

    # Insere espaços ao redor dos símbolos de um caractere.
    for simbolo in SIMBOLOS:
        codigo = codigo.replace(simbolo, f" {simbolo} ")

    # A separação por espaços transforma o código em lexemas individuais.
    lexemas = codigo.split()

    # Classifica cada lexema e cria o token correspondente.
    tokens = []
    for lexema in lexemas:
        if lexema.startswith("\x00") and lexema.endswith("\x00"):
            # Marcadores de operadores dobrados viram tokens de comparação.
            tipo, valor = TOKEN_DE_MARCADOR[lexema.strip("\x00")]
            tokens.append(Token(tipo, valor))
        elif lexema.isdigit():
            # Números permanecem como texto; a conversão para int ocorre no parser.
            tokens.append(Token("NUMERO", lexema))
        elif lexema.isidentifier():
            # Palavras reservadas recebem um tipo próprio; o resto é variável.
            tokens.append(Token(PALAVRAS_RESERVADAS.get(lexema, "IDENTIFICADOR"), lexema))
        elif lexema in MAPA:
            # Operadores e delimitadores recebem seus tipos específicos.
            tokens.append(Token(MAPA[lexema], lexema))
        else:
            # Tokens desconhecidos são mantidos para que outra etapa possa informar o erro.
            tokens.append(Token("DESCONHECIDO", lexema))
    return tokens
