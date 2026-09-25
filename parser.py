"""Analisa tokens e constrói a árvore sintática abstrata da MiniLang."""

from ast_nodes import (
    Number, Identifier, BinaryExpression, Assignment,
    Block, If, For, While, FunctionDef, Call, Return,
)

# Parser descendente recursivo para a gramática da linguagem.
# Programa -> Instrução | Instrução Programa
# Instrução -> Atribuição | If | For | While | FunctionDef | Return | Call
class Parser:
    def __init__(self, tokens):
        # A lista de tokens é consumida da esquerda para a direita.
        self.tokens = tokens
        # Indica qual token será analisado pelo próximo método.
        self.position = 0

    def current(self):
        # Retorna o token atual ou None quando todos já foram consumidos.
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def peek(self, offset=1):
        # Olha um token à frente sem consumi-lo.
        posicao = self.position + offset
        return self.tokens[posicao] if posicao < len(self.tokens) else None

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
        # Um programa é uma lista de instruções separadas por ponto e vírgula
        # ou delimitadas por blocos com chaves.
        instrucoes: list = []
        while self.current() is not None:
            instrucoes.append(self.parse_statement())
        if not instrucoes:
            raise SyntaxError("Programa vazio.")
        return instrucoes

    def parse_statement(self):
        # Despacha cada instrução para o método especializado.
        token = self.current()
        if token is None:
            raise SyntaxError("Instrução esperada, mas a entrada terminou.")
        if token.tipo == "IF":
            return self.parse_if()
        if token.tipo == "FOR":
            return self.parse_for()
        if token.tipo == "ENQUANTO":
            return self.parse_while()
        if token.tipo == "FUNCAO":
            return self.parse_function()
        if token.tipo == "RETORNAR":
            return self.parse_return()
        if token.tipo == "IDENTIFICADOR":
            seguinte = self.peek()
            if seguinte is not None and seguinte.tipo == "ABRE_PARENTESES":
                # nome( ... é uma chamada usada como instrução (ex.: somar(2);)
                chamada = self.parse_call()
                self.consume("PONTO_E_VIRGULA")
                return chamada
            return self.parse_assignment()
        raise SyntaxError(f"Instrução inesperada: {token.tipo} ({token.valor}).")

    def parse_while(self):
        # Um while segue o formato: while (condição) { bloco }.
        self.consume("ENQUANTO")
        self.consume("ABRE_PARENTESES")
        condition = self.parse_expression()
        self.consume("FECHA_PARENTESES")
        body = self.parse_block()
        return While(condition, body)

    def parse_function(self):
        # Uma função segue o formato: function nome(a, b) { ... }.
        self.consume("FUNCAO")
        nome = self.consume("IDENTIFICADOR")
        self.consume("ABRE_PARENTESES")
        params: list = []
        token = self.current()
        if token is not None and token.tipo != "FECHA_PARENTESES":
            params.append(self.consume("IDENTIFICADOR").valor)
            while True:
                separador = self.current()
                if separador is None or separador.tipo != "VIRGULA":
                    break
                self.position += 1
                params.append(self.consume("IDENTIFICADOR").valor)
        self.consume("FECHA_PARENTESES")
        body = self.parse_block()
        return FunctionDef(nome.valor, params, body)

    def parse_return(self):
        # Um return segue o formato: return ; ou return expressão ;
        self.consume("RETORNAR")
        token = self.current()
        if token is not None and token.tipo != "PONTO_E_VIRGULA":
            nodo = Return(self.parse_expression())
            self.consume("PONTO_E_VIRGULA")
            return nodo
        self.consume("PONTO_E_VIRGULA")
        return Return(None)

    def parse_assignment(self, needs_semicolon=True):
        # Uma atribuição segue o formato: identificador = expressão ;
        # Dentro do for, as cláusulas não têm ; próprio (o for fornece os ;).
        nome = self.consume("IDENTIFICADOR")
        self.consume("ATRIBUICAO")
        valor = self.parse_expression()
        if needs_semicolon:
            self.consume("PONTO_E_VIRGULA")
        return Assignment(Identifier(nome.valor), valor)

    def parse_if(self):
        # Um if segue o formato: if (condição) { } else { }.
        # A parte else é opcional; else if é suportado por recursão natural.
        self.consume("IF")
        self.consume("ABRE_PARENTESES")
        condition = self.parse_expression()
        self.consume("FECHA_PARENTESES")
        then_branch = self.parse_block()
        else_branch = None
        seguinte = self.current()
        if seguinte is not None and seguinte.tipo == "ELSE":
            self.position += 1
            seguinte = self.current()
            if seguinte is not None and seguinte.tipo == "IF":
                # else if é apenas um novo if como ramificação alternativa.
                else_branch = self.parse_if()
            else:
                else_branch = self.parse_block()
        return If(condition, then_branch, else_branch)

    def parse_for(self):
        # Um for segue o formato: for (init; condição; update) { }.
        self.consume("FOR")
        self.consume("ABRE_PARENTESES")
        init = self.parse_assignment(needs_semicolon=False)
        self.consume("PONTO_E_VIRGULA")
        condition = self.parse_expression()
        self.consume("PONTO_E_VIRGULA")
        update = self.parse_assignment(needs_semicolon=False)
        self.consume("FECHA_PARENTESES")
        body = self.parse_block()
        return For(init, condition, update, body)

    def parse_block(self):
        # Um bloco é uma lista de instruções entre chaves { }.
        self.consume("ABRE_CHAVES")
        statements: list = []
        token = self.current()
        while token is not None and token.tipo != "FECHA_CHAVES":
            statements.append(self.parse_statement())
            token = self.current()
        self.consume("FECHA_CHAVES")
        return Block(statements)

    def parse_expression(self):
        # Comparações têm menor precedência que soma e subtração.
        # Apenas UMA comparação por expressão: cadeias como 1 < 2 < 3 seriam
        # avaliadas da esquerda para a direita com booleanos, o que é enganoso.
        left = self.parse_arithmetic()
        token = self.current()
        if token is not None and token.tipo in (
            "IGUALDADE", "DIFERENCA", "MENOR", "MAIOR", "MENOR_IGUAL", "MAIOR_IGUAL"
        ):
            self.position += 1
            right = self.parse_arithmetic()
            left = BinaryExpression(left, token.valor, right)
        return left

    def parse_arithmetic(self):
        # Soma e subtração têm menor precedência que multiplicação e divisão.
        left = self.parse_term()
        token = self.current()
        while token is not None and token.tipo in ("SOMA", "SUBTRACAO"):
            self.position += 1
            right = self.parse_term()
            left = BinaryExpression(left, token.valor, right)
            token = self.current()
        return left

    def parse_term(self):
        # Um termo agrupa fatores ligados por multiplicação ou divisão.
        left = self.parse_factor()
        token = self.current()
        while token is not None and token.tipo in ("MULTIPLICACAO", "DIVISAO"):
            self.position += 1
            right = self.parse_factor()
            left = BinaryExpression(left, token.valor, right)
            token = self.current()
        return left

    def parse_factor(self):
        # Fatores são números, variáveis ou expressões entre parênteses.
        token = self.current()
        if token is None:
            raise SyntaxError("Fim inesperado da expressão.")
        if token.tipo == "NUMERO":
            # A AST guarda números como inteiros, não como texto.
            self.position += 1
            try:
                return Number(int(token.valor))
            except ValueError:
                raise SyntaxError(f"Número inválido: {token.valor}")
        if token.tipo == "IDENTIFICADOR":
            seguinte = self.peek()
            if seguinte is not None and seguinte.tipo == "ABRE_PARENTESES":
                return self.parse_call()
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

    def parse_call(self):
        # Uma chamada segue o formato: nome(argumento, argumento).
        nome = self.consume("IDENTIFICADOR")
        self.consume("ABRE_PARENTESES")
        args: list = []
        token = self.current()
        if token is not None and token.tipo != "FECHA_PARENTESES":
            args.append(self.parse_expression())
            while True:
                separador = self.current()
                if separador is None or separador.tipo != "VIRGULA":
                    break
                self.position += 1
                args.append(self.parse_expression())
        self.consume("FECHA_PARENTESES")
        return Call(nome.valor, args)
