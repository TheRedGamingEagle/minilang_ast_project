# MiniLang — Lexer, Parser, AST e Interpretador

Projeto didático de Teoria da Computação e Compiladores.

## Fluxo

Código-fonte -> Lexer -> Tokens -> Parser -> AST -> Interpreter -> Resultado

## Estrutura

- `token_model.py`: modelo de Token
- `lexer.py`: análise léxica
- `ast_nodes.py`: nós da AST
- `parser.py`: análise sintática e construção da AST
- `interpreter.py`: execução da AST
- `ast_printer.py`: visualização textual da AST
- `main.py`: exemplos e integração

## Criando a venv

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Executar

```bash
python main.py
```

O `main.py` carrega o programa completo do arquivo `calcula_bonus.mini` e executa cada instrução
na ordem em que aparece. Para testar outro programa, substitua o conteúdo desse arquivo
mantendo a sintaxe suportada.

## Exemplos suportados

```text
idade = 20 + 5 * 2;
bonus = 10;
total = idade + bonus * 2;
resultado = (20 + 5) * 2;
```

## Controle de fluxo: if, else e for

A linguagem agora suporta escolhas e repetições com blocos entre chaves `{ }`.

```text
if (total > 40) {
  categoria = 1;
} else {
  categoria = 0;
}

for (i = 1; i <= 5; i = i + 1) {
  total = total + i;
}

if (nota == 10) {
  conceito = 3;
} else if (nota >= 7) {
  conceito = 2;
} else {
  conceito = 1;
}
```

Condições aceitam os comparadores `==`, `!=`, `<`, `>`, `<=` e `>=`, combinados livremente
com a aritmética existente (por exemplo, `if (a * 2 + 1 >= b) { ... }`).

### Regras da gramática

- `if`, `while` e `for` exigem parênteses na condição/cláusulas e chaves nos blocos de corpo.
- O `else` é opcional; `else if` encadeia novas escolhas.
- O `for` tem três cláusulas separadas por `;`: inicialização, condição e atualização.
  Cada cláusula é uma atribuição comum, sem `;` próprio.
- Um laço `for` ou `while` cuja condição nunca se torna falsa é interrompido após 10.000 iterações.
- Cada expressão aceita apenas UM comparador; cadeias como `1 < 2 < 3` são rejeitadas.

## Laços: while

```text
while (i <= 10) {
  soma = soma + i;
  i = i + 1;
}
```

A condição é testada antes de cada repetição; um `while` com condição falsa
de início não executa nada.

## Funções

```text
function dobro(n) {
  return n * 2;
}
dobrado = dobro(soma);

function media(a, b) {
  return (a + b) / 2;
}
```

- `function nome(parametro, parametro) { ... }` declara a função; a declaração
  precisa aparecer antes da chamada, pois funções são registradas em tempo de execução.
- `return expressão;` encerra a função e devolve o valor; `return;` e ausência de
  `return` devolvem nada.
- Chamadas funcionam em expressões (`dobro(dobro(5))`) e como instrução solta:
  `somar(2, 3);`
- Parâmetros e variáveis novas declaradas dentro da função vivem no escopo local;
  leituras caem para a memória global quando o nome não é local.
- Uma variável existente é atualizada onde ela vive (inclusive no global), então
  acumuladores como `total = total + v;` funcionam dentro de funções.
- Recursão é suportada, com limite de profundidade da máquina virtual Python.

## O que já funciona

- números inteiros
- identificadores
- atribuição
- +, -, *, / com precedência e parênteses
- comparações ==, !=, <, >, <=, >=
- variáveis em memória com escopo local para funções
- blocos com chaves { }
- if / else / else if
- laço for com init, condição e update
- laço while com condição e corpo
- funções com parâmetros, return e recursão
- chamadas em expressões ou como instrução
- AST
- interpretação

## Próximos passos

`let`, `print`, strings, escopo de blocos, análise semântica e geração de código C.
