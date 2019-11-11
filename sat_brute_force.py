from numpy import binary_repr
from sat_parser import TokenType, Parser, Literal, Expr, Operation, stringify


def get_literals(ast, literals=None):
    if literals is None:
        literals = set()

    if isinstance(ast, Literal):
        literals.add(ast.literal)
    elif isinstance(ast, Operation):
        get_literals(ast.lhs, literals)
        get_literals(ast.rhs, literals)
    elif isinstance(ast, Expr):
        get_literals(ast.expr, literals)

    return literals


def combinations(literals):
    n = len(literals)
    d = dict()

    for combination in range(2 ** n):
        bin_value = binary_repr(combination, n)
        for pos, l in enumerate(literals):
            d[l] = False if bin_value[pos] == "0" else True
        yield d


def test_combination(dic, ast):
    if isinstance(ast, Literal):
        if ast.negated:
            return not dic[ast.literal]
        return dic[ast.literal]
    elif isinstance(ast, Operation):
        result = None
        op1 = test_combination(dic, ast.lhs)
        op2 = test_combination(dic, ast.rhs)
        if ast.op == TokenType.AND:
            result = op1 and op2
        elif ast.op == TokenType.OR:
            result = op1 or op2

        if ast.negated:
            return not result
        return result

    elif isinstance(ast, Expr):
        result = test_combination(dic, ast.expr)
        if ast.negated:
            return not result
        return result


def print_combination(dic):
    for l, r in dic.items():
        print(f"{l} = {r},  ", end="")
    print()


source = input("> ")
ast = Parser().parse(source)

print(f"Processed input")
print("¯" * 50)

print(stringify(ast), end="\n\n")

literals = get_literals(ast)

print("Obtained literals")
print("¯" * 50)

for i, x in enumerate(literals):
    print(x, end="")
    if i < len(literals) - 1:
        print(", ", end="")
    else:
        print("\n")

print(">>> Testing values... \n")

print("Result")
print("¯" * 50)

result = False

for dic in combinations(literals):
    if test_combination(dic, ast):
        print("Combination found: ")
        print_combination(dic)
        result = True
        break

if not result:
    print("Combination not found. Problem not satisfiable")
