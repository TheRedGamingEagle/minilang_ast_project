"""Converte o texto da MiniLang em uma sequência de tokens."""

from token_model import Token

def tokenize(codigo: str) -> list[Token]:
    # Insere espaços ao redor dos símbolos para que possam ser separados.
    for simbolo in [";", "+", "-", "*", "/", "=", "(", ")"]:
        codigo = codigo.replace(simbolo, f" {simbolo} ")

    # A separação por espaços transforma o código em lexemas individuais.
    lexemas = codigo.split()

    # Relaciona cada operador ou delimitador ao tipo usado pelo parser.
    mapa = {
        "=": "ATRIBUICAO", "+": "SOMA", "-": "SUBTRACAO",
        "*": "MULTIPLICACAO", "/": "DIVISAO", ";": "PONTO_E_VIRGULA",
        "(": "ABRE_PARENTESES", ")": "FECHA_PARENTESES"
    }

    # Classifica cada lexema e cria o token correspondente.
    tokens = []
    for lexema in lexemas:
        if lexema.isdigit():
            # Números permanecem como texto; a conversão para int ocorre no parser.
            tokens.append(Token("NUMERO", lexema))
        elif lexema.isidentifier():
            # Identificadores são nomes válidos de variáveis na MiniLang.
            tokens.append(Token("IDENTIFICADOR", lexema))
        elif lexema in mapa:
            # Operadores e delimitadores recebem seus tipos específicos.
            tokens.append(Token(mapa[lexema], lexema))
        else:
            # Tokens desconhecidos são mantidos para que outra etapa possa informar o erro.
            tokens.append(Token("DESCONHECIDO", lexema))
    return tokens
