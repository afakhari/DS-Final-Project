import re

TOKEN_PATTERNS = {
    "reservedword": r"\b(?:int|float|void|return|if|while|cin|cout|continue|break|using|namespace|std|main|iostream)\b",
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
    for line in code.splitlines():
        while line:
            line = line.strip()
            matched = False
            for token_type, pattern in TOKEN_PATTERNS.items():
                match = re.match(pattern, line)
                if match:
                    if token_type == "preprocessor" and match.group(0) == "#include":
                        tokens.append(("reservedword", "#include"))
                    elif token_type == "symbol" and match.group(0) == "<":
                        tokens.append(("symbol", "<"))
                    elif token_type == "identifier" and match.group(0) == "iostream":
                        tokens.append(("reservedword", "iostream"))
                    else:
                        tokens.append((token_type, match.group(0)))
                    line = line[match.end():]
                    matched = True
                    break
            if not matched:  
                tokens.append(("error", line[0]))
                line = line[1:]
    return tokens

tokens = lexical_analyzer(sample_code)

print("Tokens:")
for token_type, value in tokens:
    print(f"[{token_type}, {value}]")
