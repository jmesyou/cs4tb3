#!/usr/bin/env python3
'''
name: James You
'''

import sys, re

SYMBOL_CLASS = []

SYMBOL_CLASS.append((r'(:=)', "BecomesSym"))
SYMBOL_CLASS.append((r'(<>)', "NeqSym"))
SYMBOL_CLASS.append((r'(<=)', "LeqSym"))
SYMBOL_CLASS.append((r'(>=)', "GeqSym"))
SYMBOL_CLASS.append((r'(\*)', "TimesSym"))
SYMBOL_CLASS.append((r'(\+)', "PlusSym"))
SYMBOL_CLASS.append((r'(\-)', "MinusSym"))
SYMBOL_CLASS.append((r'(=)', "EqlSym"))
SYMBOL_CLASS.append((r'(<)', "LssSym"))
SYMBOL_CLASS.append((r'(>)', "GtrSym"))
SYMBOL_CLASS.append((r'(\.)', "PeriodSym"))
SYMBOL_CLASS.append((r'(,)', "CommaSym"))
SYMBOL_CLASS.append((r'(:)', "ColonSym"))
SYMBOL_CLASS.append((r'(;)', "SemiColonSym"))
SYMBOL_CLASS.append((r'(\()', "LparenSym"))
SYMBOL_CLASS.append((r'(\))', "RparenSym"))
SYMBOL_CLASS.append((r'(\[)', "LbrakSym"))
SYMBOL_CLASS.append((r'(\])', "RbrakSym"))
SYMBOL_CLASS.append((r'([0-9]+)', "NumberSym"))
SYMBOL_CLASS.append((r'([a-zA-Z_]\w*)', "GenericSym"))
#SYMBOL_CLASS.append((r'([^\s\w\*\+=\-<>\.,:;\(\)\[\]])', "UnknownSym"))

KEYWORD_DISPATCH = {
    'div': "DivSym",
    'mod': "ModSym",
    'and': "AndSym",
    'or': "OrSym",
    'of': "OfSym",
    'then': "ThenSym",
    'do': "DoSym",
    'not': "NotSym",
    'begin': "BeginSym",
    'end': "EndSym",
    'if': "IfSym",
    'else': "ElseSym",
    'while': "WhileSym",
    'array': "ArraySym",
    'record': "RecordSym",
    'const': "ConstSym",
    'type': "TypeSym",
    'var': "VarSym",
    'procedure': "ProcedureSym",
    'program': "ProgramSym"
}

def main():
    if len(sys.argv) != 2:
        print("please provide (1) file argument", file=sys.stderr)
        sys.exit(0)
    else:
        f = sys.argv[1]
        for line in open(f):
            while line:
                if line.isspace():
                    break
                line = line.lstrip()
                try:
                    succ = False
                    for pattern, symbol in SYMBOL_CLASS:
                        capture = re.match(pattern, line)
                        if capture:
                            token = capture.group(1)
                            if symbol == 'GenericSym':
                                symbol = KEYWORD_DISPATCH.get(token, "IdentSym")
                            # print("'{}' {}".format(token, symbol))
                            print(symbol, file=sys.stdout)
                            _, line = line.split(token, 1)
                            succ = True
                            break
                    if not succ:
                        raise SyntaxError
                except SyntaxError:
                    print("unknown symbol encountered! exiting...")
                    sys.exit(0)

        print("EofSym", file=sys.stdout)

if __name__ == "__main__":
    main()
