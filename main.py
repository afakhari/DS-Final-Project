import re

TOKEN_PATTERNS = {
    "reservedword": r"\b(?:int|float|void|return|if|while|cin|cout|continue|break|using|namespace|std|main)\b",
    "preprocessor": r"#include",
    "identifier": r"[a-zA-Z_][a-zA-Z_0-9]*",
    "number": r"\b\d+\b",
    "symbol": r"[{}();,<>=!+\-*/]|<=|>=|==|!=|<<|>>",
    "string": r'".*?"'
}

sample_code = """#include <iostream>
using namespace std;
int main() {
    int x;
    int s = 0, t = 10;
    while (t >= 0) {
        cin >> x;
        t = t - 1;
        s = s + x;
    }
    cout << "sum=" << s;
    return 0;
}"""

def lexical_analyzer(code):
    tokens = []
    lines = code.splitlines()
    for line_no, line in enumerate(lines, start=1):
        while line:
            line = line.strip()
            matched = False
            for token_type, pattern in TOKEN_PATTERNS.items():
                match = re.match(pattern, line)
                if match:
                    token_value = match.group(0)
                    if token_value in ["<", ">", "iostream"]:
                        line = line[match.end():]
                        matched = True
                        break
                    if token_type == "preprocessor" and token_value == "#include":
                        tokens.append(("reservedword", "#include", line_no))
                    else:
                        tokens.append((token_type, token_value, line_no))
                    line = line[match.end():]
                    matched = True
                    break
            if not matched: 
                tokens.append(("error", line[0], line_no))
                line = line[1:]
    return tokens

def create_token_table(tokens):
    token_table = {}
    for token_type, value, _ in tokens:
        if token_type not in token_table:
            token_table[token_type] = []
        if value not in token_table[token_type]:
            token_table[token_type].append(value)
    return token_table

def compute_first(cfg):
    first = {nt: set() for nt in cfg.keys()}
    changed = True

    while changed:
        changed = False
        for nt, productions in cfg.items():
            for production in productions:
                for symbol in production:
                    if symbol in cfg:
                        new_firsts = first[symbol] - {"epsilon"}
                        if not new_firsts.issubset(first[nt]):
                            first[nt].update(new_firsts)
                            changed = True
                        if "epsilon" not in first[symbol]:
                            break
                    else: 
                        if symbol not in first[nt]:
                            first[nt].add(symbol)
                            changed = True
                        break
                else: 
                    if "epsilon" not in first[nt]:
                        first[nt].add("epsilon")
                        changed = True
    return first

def compute_follow(cfg, start_symbol, first):
    follow = {nt: set() for nt in cfg.keys()}
    follow[start_symbol].add("$")
    changed = True

    while changed:
        changed = False
        for nt, productions in cfg.items():
            for production in productions:
                trailer = follow[nt].copy()
                for symbol in reversed(production):
                    if symbol in cfg: 
                        if not trailer.issubset(follow[symbol]):
                            follow[symbol].update(trailer)
                            changed = True
                        if "epsilon" in first[symbol]:
                            trailer.update(first[symbol] - {"epsilon"})
                        else:
                            trailer = first[symbol].copy()
                    else: 
                        trailer = {symbol}
    return follow

def create_parse_table(cfg, first, follow):
    parse_table = {}
    for nt, productions in cfg.items():
        for production in productions:
            first_set = compute_first({nt: [production]})[nt]
            for terminal in first_set:
                if terminal != "epsilon":
                    parse_table[(nt, terminal)] = production
            if "epsilon" in first_set:
                for terminal in follow[nt]:
                    parse_table[(nt, terminal)] = production
    return parse_table

def predictive_parser(tokens, parse_table, start_symbol):
    stack = ["$"]
    stack.append(start_symbol)
    tokens.append(("end", "$", -1)) 

    index = 0
    while stack:
        top = stack.pop()
        current_token = tokens[index][1]

        if top == "$" and current_token == "$":
            print("Parsing successful!")
            return True

        if top not in cfg and top != current_token:
            print(f"Error: Unexpected token '{current_token}' at line {tokens[index][2]}.")
            return False

        if top in cfg:
            if (top, current_token) in parse_table:
                production = parse_table[(top, current_token)]
                if production != ["epsilon"]:
                    stack.extend(reversed(production))
            else:
                print(f"Error: No rule for ({top}, {current_token}) at line {tokens[index][2]}.")
                return False
        else:
            index += 1

    if stack:
        print("Error: Stack is not empty after parsing.")
        return False

    return True

def find_first_variable(tokens):
    for token_type, value, line_no in tokens:
        if token_type == "identifier":
            print(f"First defined variable: {value} at line {line_no}")
            return value, line_no
    print("No variables found.")
    return None

def handle_errors(tokens):
    for i, (token_type, value, line_no) in enumerate(tokens):
        if token_type == "identifier" and i + 2 < len(tokens):
            next_token_type, next_value, _ = tokens[i + 1]
            next_next_token_type, next_next_value, _ = tokens[i + 2]
            if next_token_type == "symbol" and next_value == "=" and next_next_token_type not in ["number", "identifier"]:
                print(f"Error: Incorrect assignment to variable '{value}' at line {line_no}.")
                return
    print("No errors found.")

def search_in_parse_tree(node, target_variable):
    if node.value == target_variable:
        print(f"Variable '{target_variable}' found in the parse tree.")
        return True
    for child in node.children:
        if search_in_parse_tree(child, target_variable):
            return True
    return False

def build_parse_tree(tokens):

    root = ParseTreeNode("S")
    current_node = root
    for token_type, value, line_no in tokens:
        if token_type == "identifier":
            node = ParseTreeNode(value)
            current_node.add_child(node)
    return root

class ParseTreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

cfg = {
    "S": [["P", "U", "M"]],
    "P": [["#include"]],
    "U": [["using", "namespace", "std", ";"]],
    "M": [["int", "main", "(", ")", "{", "T", "}"]],
    "T": [["int", "identifier", ";", "T"], ["identifier", "=", "number", ";", "T"], ["epsilon"]]
}

first = compute_first(cfg)
follow = compute_follow(cfg, "S", first)

parse_table = create_parse_table(cfg, first, follow)

tokens = lexical_analyzer(sample_code)

print("\nParsing:")
if predictive_parser(tokens, parse_table, "S"):
    print("Input parsed successfully.")
else:
    print("Parsing failed.")

token_table = create_token_table(tokens)

print("\nTokens:")
for token_type, value, line_no in tokens:
    print(f"[{token_type}, {value}, line {line_no}]")

print("\nToken Table:")
for token_type, values in token_table.items():
    print(f"{token_type}: {values}")

print("\nBonus Section 1: Find First Defined Variable")
find_first_variable(tokens)

print("\nBonus Section 2: Error Handling")
handle_errors(tokens)

print("\nBonus Section 1: Tree in Search")
parse_tree_root = build_parse_tree(tokens)
target_variable = "s" 
if not search_in_parse_tree(parse_tree_root, target_variable):
    print(f"Variable '{target_variable}' not found in the parse tree.")