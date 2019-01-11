#!/usr/bin/env python3

'''
names: James You, Zicheng Jiang


b_exp -> b_term            ; [ b_exp.val = b_term.val
                               b_exp.type = b_term.type ]

       | b_exp "|" b_term  ; [ b_exp(1).val = b_exp(2).val | b_term.val if (b_exp(2).type, b_term.type == boolean) else "n/a"
                               b_exp(1).type = b_term.type if (b_exp(2).type, b_term.type == boolean) else "error" ]

b_term -> b_eq_factor               ; [ b_term.val = b_eq_factor.val
                                        b_term.type = b_eq_factor.type ]

        | b_term "&" b_eq_factor    ; [ b_term(1).val = b_term(2).val & b_eq_factor.val if (b_eq_factor.type, b_term(2).type == boolean) else "n/a"
                                        b_term(1).type = b_eq_factor.type if (b_eq_factor.type, b_term(2).type == boolean) else "error" ]

b_eq_factor -> b_not_factor                     ; [ b_eq_factor.val = b_not_factor.val
                                                    b_eq_factor.type = b_not_factor.type ]

             | b_eq_factor "=" b_not_factor     ; [ b_eq_factor(1).val = b_eq_factor(2).val = b_not_factor.val if b_eq_factor(1).type, b_not_factor.type == boolean else "n/a"
                                                    b_eq_factor(1).type = b_not_factor.type if b_eq_factor(2).type, b_not_factor.type == boolean else "error" ]

             | b_eq_factor "#" b_not_factor     ; [ b_eq_factor(1).val = b_eq_factor(2).val # b_not_factor.val if b_eq_factor(1).type, b_not_factor.type == boolean else "n/a"
                                                    b_eq_factor(1).type = b_not_factor.type if b_eq_factor(2).type, b_not_factor.type == boolean else "error" ]

b_not_factor -> exp      ; [ b_not_factor.val = exp.val
                             b_not_factor.type = b_not_factor.type ]
              | "~" exp  ; [ b_not_factor.val = ~ exp.val if exp.type == boolean else "n/a"
                             b_not_factor.type = boolean if exp.type == boolean else "error" ]

exp -> term                 ; [ exp.val = term.val
                                exp.type = term.type ]

       | exp "+" term       ; [ exp(1).val = exp(2).val + term.val if exp(2).type, term.type == int else "n/a"
                                exp(1).type = term.type if exp(2).type, term.type == int else "error" ]

       | exp "-" term       ; [ exp(1).val = exp(2).val - term.val if exp(2).type, term.type == int else "n/a"
                                exp(1).type = term.type if exp(2).type, term.type == int else "error" ]

term -> factor              ; [ term.val = factor.val
                                term.type = factor.type ]

      | term "*" factor     ; [ term(1).val = term(2).val * factor.val if term(2).type, factor.type == int else "n/a"
                                term(1).type = term(2).type if term(2).type, factor.type == int else "error" ]

      | term "/" factor     ; [ term(1).val = term(2).val / factor.val if term(2).type, factor.type == int else "n/a"
                                term(1).type = term(2).type if term(2).type, factor.type == int else "error" ]

factor -> number            ; [ factor.val = strtoint(number)
                                factor.type = integer ]

        | bool              ; [ factor.val = strtobool(bool)
                                factor.type = boolean ]

        | "(" b_exp ")"       ; [ factor.val = b_exp.value]

'''
import sys

BOOL = ['t', 'f']
DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def peek():
    global stream
    return stream[0]

def consume():
    global stream
    if not len(stream):
        raise IndexError
    else:
        return stream.pop(0)

def accept(char):
    global stream
    if len(stream) == 0:
        raise IndexError
    sym = peek()
    if sym == char or sym in char:
        return stream.pop(0)
    else:
        raise SyntaxError

def boolean():
    b = accept(BOOL)
    return True if b == 't' else False

def integer():
    digits = ''
    try:
        while True:
            digits += accept(DIGITS)
    except:
        if len(digits):
            return int(digits)
        else:
            raise SyntaxError

def b_exp():
    global stream
    token = b_term()
    try:
        while peek() == '|':
            symbol = peek()
            if symbol == '|':
                accept('|')
                _term = b_term()
                if type(token) is bool and type(_term) is bool:
                     token = token | _term
                else:
                    raise TypeError
    except IndexError:
        pass
    except:
        raise
    return token

def b_term():
    global stream
    token = b_eq_factor()
    try:
        while peek() == '&':
            symbol = peek()
            if symbol == '&':
                accept('&')
                _factor = b_eq_factor()
                if type(token) is bool and type(_factor) is bool:
                    token = token & _factor
                else:
                     raise TypeError
    except IndexError:
        pass
    except:
        raise
    return token

def b_eq_factor():
    global stream
    token = b_not_factor()
    symbol = None
    try:
        while peek() in ["=", "#"]:
            symbol = peek()
            if symbol == '=':
                accept('=')
                _factor = b_not_factor()
                if type(token) is bool and type(_factor) is bool:
                    token = token == _factor
                else:
                    raise TypeError
            elif symbol == '#':
                accept('#')
                _factor = b_not_factor()
                if type(token) is bool and type(_factor) is bool:
                    token = token != _factor
                else:
                     raise TypeError
    except IndexError:
        pass
    except:
        raise
    return token

def b_not_factor():
    global stream
    token = None
    symbol = None
    iterations = 0
    try:
        while peek() == '~':
            accept('~')
            iterations += 1
        token = exp()
        if iterations > 0 and type(token) != bool:
            raise TypeError
        for i in range(iterations):
            token = not token
    except IndexError:
        pass
    except:
        raise
    return token

def exp():
    global stream
    token = term()
    symbol = None
    try:
        while peek() in ["+","-"]:
            symbol = peek()
            if symbol == '+':
                accept('+')
                _term = term()
                if type(token) is int and type(_term) is int:
                    token += _term
                else:
                    raise TypeError
            elif symbol == '-':
                accept('-')
                _term = term()
                if type(token) is int and type(_term) is int:
                    token -= _term
                else:
                    raise TypeError
    except IndexError:
        pass
    except:
        raise
    return token


def term():
    global stream
    token = factor()
    symbol = None
    try:
        while peek() in ["*", "/"]:
            symbol = peek()
            if symbol == '*':
                accept('*')
                _factor = factor()
                if type(token) is int and type(_factor) is int:
                    token *= _factor
                else:
                    raise TypeError
            elif symbol == '/':
                accept("/")
                _factor = factor()
                if type(token) is int and type(_factor) is int:
                    token = token // _factor
                else:
                    raise TypeError
    except IndexError:
        pass
    except:
        raise
    return token

def factor():
    token = None

    symbol = peek()
    if symbol == "(":
        accept("(")
        token = b_exp()
        accept(")")
    elif symbol in BOOL:
        token = boolean()
    elif symbol in DIGITS:
        token = integer()
    return token

def main():
    global stream
    stream = list(sys.stdin.readline().rstrip())

    try:
        v = b_exp()
        t = "integer" if type(v) is int else "boolean"
        sys.stdout.write("type: {} val: {}\n".format(t, int(v)))
        assert(len(stream) == 0)
    except:
        sys.stdout.write("type: error val: n/a\n")

main()
