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

tokens = lexical_analyzer(sample_code)

print("Tokens:")
for token_type, value in tokens:
    print(f"[{token_type}, {value}]")

cfg = {
    "S": [["P", "U", "M"]],
    "P": [["#include"]],
    "U": [["using", "namespace", "std", ";"]],
    "M": [["int", "main", "(", ")", "{", "T", "}"]],
    "T": [["int", "identifier", ";", "T"], ["identifier", "=", "number", ";", "T"], ["epsilon"]]
}

first = compute_first(cfg)
