import re

# الگوهای مختلف برای شناسایی توکن‌ها
TOKEN_PATTERNS = {
    "reservedword": r"\b(?:int|float|void|return|if|while|cin|cout|continue|break|using|namespace|std|main)\b",  # کلمات کلیدی
    "preprocessor": r"#include",  # دستور پیش‌پردازنده
    "identifier": r"[a-zA-Z_][a-zA-Z_0-9]*",  # شناسه‌ها (نام متغیرها و توابع)
    "number": r"\b\d+\b",  # اعداد
    "symbol": r"[{}();,<>=!+\-*/]|<=|>=|==|!=|<<|>>",  # نمادها (عملگرها و پرانتزها)
    "string": r'".*?"'  # رشته‌ها
}

# کد نمونه به عنوان ورودی برای تجزیه
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

# تحلیلگر لغوی (شناسایی و جدا کردن توکن‌ها از کد)
def lexical_analyzer(code):
    tokens = []  # لیستی برای ذخیره توکن‌ها
    lines = code.splitlines()  # جدا کردن کد به خط‌های مختلف
    for line_no, line in enumerate(lines, start=1):
        while line:
            line = line.strip()  # حذف فاصله‌های اضافی در ابتدا و انتهای خط
            matched = False
            for token_type, pattern in TOKEN_PATTERNS.items():  # بررسی هر الگو
                match = re.match(pattern, line)  # تطابق با الگو
                if match:
                    token_value = match.group(0)  # مقدار توکن شناسایی شده
                    if token_value in ["<", ">", "iostream"]:
                        line = line[match.end():]
                        matched = True
                        break
                    if token_type == "preprocessor" and token_value == "#include":
                        tokens.append(("reservedword", "#include", line_no))  # اضافه کردن دستور پیش‌پردازنده
                    else:
                        tokens.append((token_type, token_value, line_no))  # اضافه کردن توکن
                    line = line[match.end():]  # به ادامه خط پرداخته می‌شود
                    matched = True
                    break
            if not matched:  # در صورت عدم تطابق
                tokens.append(("error", line[0], line_no))  # اضافه کردن خطا
                line = line[1:]  # ادامه پردازش خط
    return tokens

# ساخت جدول توکن‌ها
def create_token_table(tokens):
    token_table = {}  # جدول توکن‌ها
    for token_type, value, _ in tokens:
        if token_type not in token_table:
            token_table[token_type] = []
        if value not in token_table[token_type]:
            token_table[token_type].append(value)  # افزودن مقادیر توکن به جدول
    return token_table

# جدول تجزیه
parse_table = {
    ("Id", "int"): ["int", "L"],
    ("Id", "float"): ["float", "L"],
    ("N", "using"): ["using", "namespace", "std", ";"],
    ("N", "int"): ["epsilon"],
    ("K", "=="): ["=="],
    ("K", ">="): [">="],
    ("K", "<="): ["<="],
    ("K", "!="): ["!="],
    ("Loop", "while"): ["while", "(", "Expression", ")", "{", "T", "}"],
    ("V", "return"): ["return", "number", ";"],
    ("V", "}"): ["epsilon"],
    ("Start", "using"): ["S", "N", "M"],
    ("Start", "int"): ["S", "N", "M"],
    ("Start", "#include"): ["S", "N", "M"],
    ("Assign", "="): ["=", "Operation"],
    ("Assign", ","): ["epsilon"],
    ("Assign", ";"): ["epsilon"],
    ("Expression", "number"): ["Operation", "K", "Operation"],
    ("Expression", "identifier"): ["Operation", "K", "Operation"],
    ("Operation", "number"): ["number", "P"],
    ("Operation", "identifier"): ["identifier", "P"],
    ("P", "*"): ["O", "W", "P"],
    ("P", "-"): ["O", "W", "P"],
    ("P", "+"): ["O", "W", "P"],
    ("P", ")"): ["epsilon"],
    ("P", "=="): ["epsilon"],
    ("P", ";"): ["epsilon"],
    ("P", ">="): ["epsilon"],
    ("P", "!="): ["epsilon"],
    ("P", "<="): ["epsilon"],
    ("P", ","): ["epsilon"],
    ("O", "+"): ["+"],
    ("O", "-"): ["-"],
    ("O", "*"): ["*"],
    ("T", "int"): ["Id", "T"],
    ("T", "float"): ["Id", "T"],
    ("T", "identifier"): ["L", "T"],
    ("T", "while"): ["Loop", "T"],
    ("T", "cin"): ["Input", "T"],
    ("T", "cout"): ["Output", "T"],
    ("T", "}"): ["epsilon"],
    ("T", "return"): ["epsilon"],
    ("T", "$"):["epsilon"],
    ("F", ">>"): [">>", "identifier", "F"],
    ("F", ";"): ["epsilon"],
    ("H", "<<"): ["<<", "C", "H"],
    ("H", ";"): ["epsilon"],
    ("C", "number"): ["number"],
    ("C", "string"): ["string"],
    ("C", "identifier"): ["identifier"],
    ("M", "int"): ["int", "main", "(", ")", "{", "T", "V", "}"],
    ("S", "#include"): ["#include", "S"],
    ("S", "using"): ["epsilon"],
    ("S", "$"):["epsilon"],
    ("Input", "cin"): ["cin", ">>", "identifier", "F", ";"],
    ("L", "identifier"): ["identifier", "Assign", "Z"],
    ("Z", ","): [",", "identifier", "Assign", "Z"],
    ("Z", ";"): [";"],
    ("W", "number"): ["number"],
    ("W", "identifier"): ["identifier"],
    ("Output", "cout"): ["cout", "<<", "C", "H", ";"]
}

# کلاس برای نمایه‌سازی درخت تجزیه
class ParseTreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []  # فرزندان هر گره درخت

    def add_child(self, child):
        self.children.append(child)  # افزودن فرزند به گره

    def __str__(self):
        return self.value  # بازگرداندن مقدار گره

    def print_tree(self, level=0):
        print("  " * level + str(self.value))  # چاپ درخت با فواصل متناسب
        for child in self.children:
            child.print_tree(level + 1)

# ساخت درخت تجزیه
def build_parse_tree(tokens, parse_table, start_symbol):
    stack = ["$"]
    stack.append(start_symbol)  # شروع از نماد آغازین
    tokens.append(("end", "$", -1))  # افزودن نماد پایانی به توکن‌ها

    root = ParseTreeNode(start_symbol)  # ساخت ریشه درخت
    nodes_stack = [root]  # پشته گره‌ها

    index = 0
    while stack:
        top = stack.pop()  # برداشت نماد از بالای پشته
        current_node = nodes_stack.pop()  # برداشت گره از پشته گره‌ها
        current_token = tokens[index][1]  # دریافت توکن جاری

        print(f"[DEBUG] Stack: {stack}")
        print(f"[DEBUG] Current Token: {current_token}")
        print(f"[DEBUG] Top of Stack: {top}")

        if top == "$" and current_token == "$":
            print("Parsing successful!")  # موفقیت در تجزیه
            root.print_tree()  # چاپ درخت تجزیه
            return root

        if (top, current_token) in parse_table:  # استفاده از جدول تجزیه
            production = parse_table[(top, current_token)]
            print(f"[DEBUG] Applying Rule: {top} -> {production}")
            if production != ["epsilon"]:  # اگر تولید برابر "epsilon" نباشد
                stack.extend(reversed(production))  # افزودن نمادها به پشته
                for symbol in reversed(production):
                    child_node = ParseTreeNode(symbol)
                    current_node.add_child(child_node)  # افزودن فرزند به گره
                    nodes_stack.append(child_node)  # افزودن فرزند به پشته گره‌ها
        elif top == current_token:  # تطابق نماد بالای پشته با توکن جاری
            current_node.value = current_token
            index += 1
        else:
            print(f"Error: Unexpected token '{current_token}' at line {tokens[index][2]}. Expected '{top}'")
            return None

    if stack:
        print("Error: Stack is not empty after parsing.")
        return None

    return root

# پیدا کردن اولین متغیر تعریف شده در کد
def find_first_variable(tokens):
    for token_type, value, line_no in tokens:
        if token_type == "identifier":
            print(f"First defined variable: {value} at line {line_no}")
            return value, line_no
    print("No variables found.")
    return None

# اجرای تحلیل لغوی
tokens = lexical_analyzer(sample_code)

print("\nParsing:")
# ساخت درخت تجزیه
parse_tree = build_parse_tree(tokens, parse_table, "Start")
if parse_tree:
    print("Input parsed successfully.")
else:
    print("Parsing failed.")

# نمایش توکن‌ها
token_table = create_token_table(tokens)

print("\nTokens:")
for token_type, value, line_no in tokens:
    print(f"[{token_type}, {value}, line {line_no}]")

# نمایش جدول توکن‌ها
print("\nToken Table:")
for token_type, values in token_table.items():
    print(f"{token_type}: {values}")

# پیدا کردن اولین متغیر
find_first_variable(tokens)
