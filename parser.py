"""Analisa tokens e constrói a árvore sintática abstrata da MiniLang."""

from ast_nodes import Number, Identifier, BinaryExpression, Assignment

# Parser descendente recursivo para a gramática das expressões da linguagem.
class Parser:
    def __init__(self, tokens):
        # A lista de tokens é consumida da esquerda para a direita.
        self.tokens = tokens
        # Indica qual token será analisado pelo próximo método.
        self.position = 0

    def current(self):
        # Retorna o token atual ou None quando todos já foram consumidos.
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def consume(self, tipo):
        # Confere o tipo esperado e avança a posição em caso de sucesso.
        token = self.current()
        if token is None:
            raise SyntaxError(f"Esperado {tipo}, mas a entrada terminou.")
        if token.tipo != tipo:
            raise SyntaxError(f"Esperado {tipo}, encontrado {token.tipo} ({token.valor}).")
        self.position += 1
        return token

    def parse(self):
        # O programa atual contém uma atribuição completa como expressão principal.
        node = self.parse_assignment()
        # Nenhum token pode sobrar depois do ponto e vírgula final.
        if self.current() is not None:
            raise SyntaxError(f"Token inesperado: {self.current().valor}")
        return node

    def parse_assignment(self):
        # Uma atribuição segue o formato: identificador = expressão ;
        nome = self.consume("IDENTIFICADOR")
        self.consume("ATRIBUICAO")
        valor = self.parse_expression()
        self.consume("PONTO_E_VIRGULA")
        return Assignment(Identifier(nome.valor), valor)

    def parse_expression(self):
        # Soma e subtração têm menor precedência que multiplicação e divisão.
        left = self.parse_term()
        while self.current() and self.current().tipo in ("SOMA", "SUBTRACAO"):
            op = self.current().valor
            self.position += 1
            right = self.parse_term()
            left = BinaryExpression(left, op, right)
        return left

    def parse_term(self):
        # Um termo agrupa fatores ligados por multiplicação ou divisão.
        left = self.parse_factor()
        while self.current() and self.current().tipo in ("MULTIPLICACAO", "DIVISAO"):
            op = self.current().valor
            self.position += 1
            right = self.parse_factor()
            left = BinaryExpression(left, op, right)
        return left

    def parse_factor(self):
        # Fatores são números, variáveis ou expressões entre parênteses.
        token = self.current()
        if token is None:
            raise SyntaxError("Fim inesperado da expressão.")
        if token.tipo == "NUMERO":
            # A AST guarda números como inteiros, não como texto.
            self.position += 1
            return Number(int(token.valor))
        if token.tipo == "IDENTIFICADOR":
            # A resolução do valor da variável fica para o interpretador.
            self.position += 1
            return Identifier(token.valor)
        if token.tipo == "ABRE_PARENTESES":
            # Os parênteses alteram a ordem natural de avaliação.
            self.position += 1
            expr = self.parse_expression()
            self.consume("FECHA_PARENTESES")
            return expr
        raise SyntaxError(f"Token inesperado: {token.tipo} ({token.valor})")
