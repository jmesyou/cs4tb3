#!/usr/bin/env python3

'''
names: James You, Zichen Jiang
'''

"""
Pascal0 Parser, Emil Sekerinski, February 2017,
Main program, type-checks, folds constants, calls scanner SC and code
generator CG, uses symbol table ST
"""

from sys import argv
import SC  #  used for SC.init, SC.sym, SC.val, SC.error
from SC import TIMES, DIV, MOD, AND, PLUS, MINUS, OR, EQ, NE, LT, GT, \
     LE, GE, PERIOD, COMMA, COLON, RPAREN, RBRAK, OF, THEN, DO, LPAREN, \
     LBRAK, NOT, BECOMES, NUMBER, IDENT, SEMICOLON, END, ELSE, IF, WHILE, \
     ARRAY, RECORD, CONST, TYPE, VAR, PROCEDURE, BEGIN, PROGRAM, EOF, \
     getSym, mark
import ST  #  used for ST.init
from ST import Var, Ref, Const, Type, Proc, StdProc, Int, Bool, Enum, \
     Record, Array, newObj, find, openScope, topScope, closeScope


# first and follow sets for recursive descent parsing

FIRSTFACTOR = {IDENT, NUMBER, LPAREN, NOT}
FOLLOWFACTOR = {TIMES, DIV, MOD, AND, OR, PLUS, MINUS, EQ, NE, LT, LE, GT, GE,
                COMMA, SEMICOLON, THEN, ELSE, RPAREN, RBRAK, DO, PERIOD, END}
FIRSTEXPRESSION = {PLUS, MINUS, IDENT, NUMBER, LPAREN, NOT}
FIRSTSTATEMENT = {IDENT, IF, WHILE, BEGIN}
FOLLOWSTATEMENT = {SEMICOLON, END, ELSE}
FIRSTTYPE = {IDENT, RECORD, ARRAY, LPAREN}
FOLLOWTYPE = {SEMICOLON}
FIRSTDECL = {CONST, TYPE, VAR, PROCEDURE}
FOLLOWDECL = {BEGIN}
FOLLOWPROCCALL = {SEMICOLON, END, ELSE}
STRONGSYMS = {CONST, TYPE, VAR, PROCEDURE, WHILE, IF, BEGIN, EOF}

from sys import stdout

def write(s): stdout.write(s)
def writeln(): stdout.write('\n')

def writeHtml(s, tag='span', _class=''):
    global html
    idents = ['boolean','integer','true','false','read','write','writeln']
    keywords = ['do','if','of','or','and','not','end','mod','var','else','then','type','array','begin','const','while','record','procedure','div','program']
    if any(i in s for i in idents):
        _class = 'ident'
    if any(i in s for i in keywords):
        _class = 'keyword'
    startTag = '<' + tag + ' class="' + _class + '">'
    endTag = '</' + tag + '>'
    html += startTag + s + endTag
def writeHtmlLn():
    global html
    html += '<br/>'

depth = 0
indent = '  '

html = ''
htmlIndent = '&nbsp;&nbsp;'
css = """
<style>
body{
    font-family: Consolas,"courier new";
}

.keyword {
    font-weight: 700;
}

.ident {
    font-style: italic;
}

</style>
"""


# parsing procedures

def selector(x):
    """
    Parses
        selector = {"." ident | "[" expression "]"}.
    Assumes x is the entry for the identifier in front of the selector;
    generates code for the selector if no error is reported
    """
    while SC.sym in {PERIOD, LBRAK}:
        if SC.sym == PERIOD:  #  x.f
            # attribute
            write('.')
            writeHtml('.')
            #
            getSym()
            if SC.sym == IDENT:
                # attribute
                write(SC.val)
                writeHtml(SC.val)
                #
                if type(x.tp) == Record:
                    for f in x.tp.fields:
                        if f.name == SC.val:
                            x = CG.genSelect(x, f); break
                    else: mark("not a field")
                    getSym()
                else: mark("not a record")
            else: mark("identifier expected")
        else:  #  x[y]
            getSym()
            # attribute
            write('[')
            writeHtml('[')
            #
            y = expression()
            if type(x.tp) == Array:
                if y.tp == Int:
                    if type(y) == Const and \
                       (y.val < x.tp.lower or y.val >= x.tp.lower + x.tp.length):
                        mark('index out of bounds')
                    else: x = CG.genIndex(x, y)
                else: mark('index not integer')
            else: mark('not an array')
            if SC.sym == RBRAK:
                getSym()
                # attribute
                write(']')
                writeHtml(']')

            else: mark("] expected")
    return x

def factor():
    """
    Parses
        factor = ident «write(ident)» selector |
                 integer «write(integer)» |
                 "(" «write('(')» expression ")" «write(')')» |
                 "not" «write('not ') factor.
    Generates code for the factor if no error is reported
    """
    if SC.sym not in FIRSTFACTOR:
        mark("expression expected"); getSym()
        while SC.sym not in FIRSTFACTOR | STRONGSYMS | FOLLOWFACTOR:
            getSym()
    if SC.sym == IDENT:
        x = find(SC.val)
        if type(x) in {Var, Ref}: x = CG.genVar(x)
        elif type(x) == Const: x = Const(x.tp, x.val); x = CG.genConst(x)
        else: mark('expression expected')
        write(SC.val); writeHtml(SC.val); getSym(); x = selector(x)
    elif SC.sym == NUMBER:
        x = Const(Int, SC.val); x = CG.genConst(x); write(str(SC.val)); writeHtml(str(SC.val)); getSym()
    elif SC.sym == LPAREN:
        write('(')
        writeHtml('(')
        getSym()
        x = expression()
        if SC.sym == RPAREN:
            write(')')
            writeHtml(')')
            getSym()
        else: mark(") expected")
    elif SC.sym == NOT:
        write('not '); writeHtml('not '); getSym(); x = factor()
        if x.tp != Bool: mark('not boolean')
        elif type(x) == Const: x.val = 1 - x.val # constant folding
        else: x = CG.genUnaryOp(NOT, x)
    else: x = Const(None, 0)
    return x

def term():
    """
    Parses
        term = factor {("*" | "div" | "mod" | "and") factor}.
    Generates code for the term if no error is reported
    """
    x = factor()
    while SC.sym in {TIMES, DIV, MOD, AND}:
        op = SC.sym
        # attribute
        symbols_of = {TIMES: ' * ', DIV: ' div ', MOD: ' mod ', AND: ' and '}
        write(symbols_of[op])
        writeHtml(symbols_of[op])
        #
        getSym()
        if op == AND and type(x) != Const: x = CG.genUnaryOp(AND, x)
        y = factor() # x op y
        if x.tp == Int == y.tp and op in {TIMES, DIV, MOD}:
            if type(x) == Const == type(y): # constant folding
                if op == TIMES: x.val = x.val * y.val
                elif op == DIV: x.val = x.val // y.val
                elif op == MOD: x.val = x.val % y.val
            else: x = CG.genBinaryOp(op, x, y)
        elif x.tp == Bool == y.tp and op == AND:
            if type(x) == Const: # constant folding
                if x.val: x = y # if x is true, take y, else x
            else: x = CG.genBinaryOp(AND, x, y)
        else: mark('bad type')
    return x

def simpleExpression():
    """
    Parses
        simpleExpression = ["+" | "-"] term {("+" | "-" | "or") term}.
    Generates code for the simpleExpression if no error is reported
    """
    if SC.sym == PLUS:
        # attribute
        write(' + ')
        writeHtml(' + ')
        #
        getSym()
        x = term()
    elif SC.sym == MINUS:
        # attribute
        write(' - ')
        writeHtml(' - ')
        #
        getSym()
        x = term()
        if x.tp != Int: mark('bad type')
        elif type(x) == Const: x.val = - x.val # constant folding
        else: x = CG.genUnaryOp(MINUS, x)
    else: x = term()
    while SC.sym in {PLUS, MINUS, OR}:
        op = SC.sym; getSym()
        symbols_of = {5: ' + ', 6: ' - ', 7: ' or '}
        write(symbols_of[op])
        writeHtml(symbols_of[op])
        if op == OR and type(x) != Const: x = CG.genUnaryOp(OR, x)
        y = term() # x op y
        if x.tp == Int == y.tp and op in {PLUS, MINUS}:
            if type(x) == Const == type(y): # constant folding
                if op == PLUS: x.val = x.val + y.val
                elif op == MINUS: x.val = x.val - y.val
            else: x = CG.genBinaryOp(op, x, y)
        elif x.tp == Bool == y.tp and op == OR:
            if type(x) == Const: # constant folding
                if not x.val: x = y # if x is false, take y, else x
            else: x = CG.genBinaryOp(OR, x, y)
        else: mark('bad type')
    return x

def expression():
    """
    Parses
        expression = simpleExpression
                     {("=" | "<>" | "<" | "<=" | ">" | ">=") simpleExpression}.
    Generates code for the expression if no error is reported
    """
    x = simpleExpression()
    while SC.sym in {EQ, NE, LT, LE, GT, GE}:
        op = SC.sym
        # attribute
        symbols_of = {EQ: ' = ', NE: '<>', LT: ' < ', LE: ' <= ',  GT: ' > ', GE: ' >= '}
        write(symbols_of[op])
        writeHtml(symbols_of[op])
        #
        getSym(); y = simpleExpression() # x op y
        if x.tp == Int == y.tp:
            x = CG.genRelation(op, x, y)
        else: mark('bad type')
    return x

def compoundStatement(l):
    """
    Parses
        compoundStatement(l) =
            "begin" «writeln; write(l * indent + 'begin')»
            statement(l + 1) {";" «write(';')» statement(l + 1)}
            "end" «writeln; write(l * ident + 'end')»
    Generates code for the compoundStatement if no error is reported
    """
    if SC.sym == BEGIN:
        writeln()
        write(l * indent + 'begin')

        writeHtmlLn()
        writeHtml(l * htmlIndent + 'begin')

        getSym()

    else: mark("'begin' expected")
    x = statement(l + 1)
    while SC.sym == SEMICOLON or SC.sym in FIRSTSTATEMENT:
        if SC.sym == SEMICOLON:
            write(';'); getSym()
            writeHtml(';')
        else: mark("; missing")
        y = statement(l + 1); x = CG.genSeq(x, y)
    if SC.sym == END:
        writeln()
        write(l * indent)
        write('end')
        writeln()

        writeHtmlLn()
        writeHtml(l * htmlIndent)
        writeHtml('end')
        writeHtmlLn()

        getSym()
    else: mark("'end' expected")
    return x

def statement(l):
    """
    Parses
        statement =
EDIT LINE   ident selector ":=" expression |
            ident «write(l * indent + ident)» "(" «write('(')» [expression
                {"," «write(', ')» expression}] ")" «write(')')» |
            compoundStatement(l) |
            "if" «writeln; write(l * indent + 'if ')» expression
                "then" «write(' then')» statement(l + 1)
                ["else" «writeln; write(l * indent + 'else')» statement(l + 1)] |
EDIT LINE   "while" expression "do" statement.
    Generates code for the statement if no error is reported
    """
    if SC.sym not in FIRSTSTATEMENT:
        mark("statement expected"); getSym()
        while SC.sym not in FIRSTSTATEMENT | STRONGSYMS | FOLLOWSTATEMENT:
            getSym()
    if SC.sym == IDENT:
        x = find(SC.val); writeln(); write(l * indent + SC.val); getSym()
        writeHtmlLn()
        writeHtml(l * htmlIndent + SC.val)
        x = CG.genVar(x)
        if type(x) in {Var, Ref}:
            x = selector(x)
            if SC.sym == BECOMES:
                write(' := ')
                writeHtml(' := ')
                getSym(); y = expression()
                if x.tp == y.tp in {Bool, Int}: # and not SC.error: type(y) could be Type
                    #if type(x) == Var: ### and type(y) in {Var, Const}: incomplete, y may be Reg
                        x = CG.genAssign(x, y)
                    #else: mark('illegal assignment')
                else: mark('incompatible assignment')
            elif SC.sym == EQ:
                mark(':= expected'); getSym(); y = expression()
            else: mark(':= expected')
        elif type(x) in {Proc, StdProc}:
            fp, i = x.par, 0  #  list of formals, count of actuals
            if SC.sym == LPAREN:
                write('('); getSym()
                writeHtml('(')
                if SC.sym in FIRSTEXPRESSION:
                    y = expression()
                    if i < len(fp):
                        if (type(fp[i]) == Var or type(y) == Var) and \
                           fp[i].tp == y.tp:
                            if type(x) == Proc: CG.genActualPara(y, fp[i], i)
                            i = i + 1
                        else: mark('illegal parameter mode')
                    else: mark('extra parameter')
                    while SC.sym == COMMA:
                        write(', '); getSym()
                        writeHtml(', ')
                        y = expression()
                        if i < len(fp):
                            if (type(fp[i]) == Var or type(y) == Var) and \
                               fp[i].tp == y.tp:
                                if type(x) == Proc: CG.genActualPara(y, fp[i], i)
                                i = i + 1
                            else: mark('illegal parameter mode')
                        else: mark('extra parameter')
                if SC.sym == RPAREN:
                    write(')'); getSym()
                    writeHtml(')')
                else: mark("')' expected")
            if i < len(fp): mark('too few parameters')
            if type(x) == StdProc:
                if x.name == 'read': x = CG.genRead(y)
                elif x.name == 'write': x = CG.genWrite(y)
                elif x.name == 'writeln': x = CG.genWriteln()
            else: x = CG.genCall(x)
        else: mark("variable or procedure expected")
    elif SC.sym == BEGIN: x = compoundStatement(l + 1)
    elif SC.sym == IF:
        writeln()
        write(l * indent + 'if ')
        writeHtmlLn()
        writeHtml(l * htmlIndent + 'if ')
        getSym()
        x = expression()
        if x.tp == Bool: x = CG.genCond(x)
        else: mark('boolean expected')
        if SC.sym == THEN:
            write(' then')
            writeHtml(' then')
            getSym()
        else: mark("'then' expected")
        y = statement(l + 1)
        if SC.sym == ELSE:
            if x.tp == Bool: y = CG.genThen(x, y);
            writeln()
            write(l * indent + 'else')
            writeHtmlLn()
            writeHtml(l * htmlIndent + ' else')
            getSym()
            z = statement(l + 1);
            if x.tp == Bool: x = CG.genIfElse(x, y, z)
        else:
            if x.tp == Bool: x = CG.genIfThen(x, y)
    elif SC.sym == WHILE:
        writeln()
        write(indent*(l+1))
        write('while ')
        writeHtmlLn()
        writeHtml(htmlIndent*(l+1))
        writeHtml('while ')
        getSym(); t = CG.genTarget(); x = expression()
        if x.tp == Bool: x = CG.genCond(x)
        else: mark('boolean expected')
        if SC.sym == DO:
            write(' do')
            writeHtml(' do')
            getSym()
        else: mark("'do' expected")
        y = statement(l + 2)
        if x.tp == Bool: x = CG.genWhile(t, x, y)
    else: x = None
    return x

def typ():
    """
    Parses
        type = ident |
               "array" "[" expression ".." expression "]" "of" type |
               "record" typedIds {";" typedIds} "end".
    Returns a type descriptor
    """
    global depth
    if SC.sym not in FIRSTTYPE:
        getSym(); mark("type expected")
        while SC.sym not in FIRSTTYPE | STRONGSYMS | FOLLOWTYPE:
            getSym()
    if SC.sym == IDENT:
        # attribute
        ident = SC.val
        write(ident)
        writeHtml(ident, _class='ident')
        #
        x = find(ident)
        getSym()
        if type(x) == Type: x = Type(x.tp)
        else: mark('not a type'); x = Type(None)
    elif SC.sym == ARRAY:
        depth += 1
        # attribute
        writeln()
        write(indent*depth)
        write('array ')
        writeHtmlLn()
        writeHtml(htmlIndent * depth)
        writeHtml('array ')
        #
        getSym()
        if SC.sym == LBRAK:
            # attribute
            write('[')
            writeHtml('[')
            #
            getSym()
        else: mark("'[' expected")
        x = expression()
        if SC.sym == PERIOD:
            # attribute
            write(' .')
            writeHtml(' .')
            #
            getSym()
        else: mark("'.' expected")
        if SC.sym == PERIOD:
            # attribute
            write('. ')
            writeHtml('. ')
            #
            getSym()
        else: mark("'.' expected")
        y = expression()
        if SC.sym == RBRAK:
            # attribute
            write('] ')
            writeHtml('] ')
            #
            getSym()
        else: mark("']' expected")
        if SC.sym == OF:
            # attribute
            write('of')
            writeHtml('of')
            #
            getSym()
        else: mark("'of' expected")
        z = typ().tp
        if type(x) != Const or x.val < 0:
            mark('bad lower bound'); x = Type(None)
        elif type(y) != Const or y.val < x.val:
            mark('bad upper bound'); y = Type(None)
        else: x = Type(CG.genArray(Array(z, x.val, y.val - x.val + 1)))
        depth -= 1
    elif SC.sym == RECORD:
        # attributes
        depth += 1
        writeln()
        write(indent*depth)
        write('record')
        writeln()
        writeHtmlLn()
        writeHtml(htmlIndent*depth)
        writeHtml('record')
        writeHtmlLn()
        depth += 1
        #
        getSym()

        # attributes
        write(indent*depth)
        write(SC.val)
        writeHtml(htmlIndent*depth)
        writeHtml(SC.val)
        #
        openScope()
        typedIds(Var)
        while SC.sym == SEMICOLON:
            # attributes
            write(';')
            writeln()
            writeHtml(';')
            writeHtmlLn()
            #
            getSym()

            # attributes
            write(indent*depth)
            write(SC.val)
            writeHtml(htmlIndent * depth)
            writeHtml(SC.val)
            #
            typedIds(Var)
        # attributes
        writeln()
        writeHtmlLn()
        depth -= 1
        write(indent*depth)
        writeHtml(htmlIndent * depth)
        #
        if SC.sym == END:
            # attributes
            write('end')
            writeHtml('end')
            #
            getSym()
        else: mark("'end' expected")
        r = topScope(); closeScope()
        x = Type(CG.genRec(Record(r)))
        depth -= 1
    else: x = Type(None)
    return x

def typedIds(kind):
    """
    Parses
        typedIds = ident {"," ident} ":" type.
    Updates current scope of symbol table
    Assumes kind is Var or Ref and applies it to all identifiers
    Reports an error if an identifier is already defined in the current scope
    """
    if SC.sym == IDENT: tid = [SC.val]; getSym()
    else: mark("identifier expected"); tid = []
    while SC.sym == COMMA:
        # attribute
        write(', ')
        writeHtml(', ')
        #
        getSym()
        if SC.sym == IDENT:
            # attribute
            write(SC.val)
            writeHtml(SC.val)
            #
            tid.append(SC.val); getSym()
        else: mark('identifier expected')
    if SC.sym == COLON:
        # attribute
        write(': ')
        writeHtml(': ')
        #
        getSym(); tp = typ().tp
        if tp != None:
            for i in tid: newObj(i, kind(tp))
    else: mark("':' expected")

def declarations(allocVar):
    """
    Parses
        declarations =
            {"const" ident "=" expression ";"}
            {"type" ident "=" type ";"}
            {"var" typedIds ";"}
            {"procedure" ident ["(" [["var"] typedIds {";" ["var"] typedIds}] ")"] ";"
                declarations compoundStatement ";"}.
    Updates current scope of symbol table.
    Reports an error if an identifier is already defined in the current scope.
    For each procedure, code is generated
    """
    global depth
    if SC.sym not in FIRSTDECL | FOLLOWDECL:
        getSym(); mark("'begin' or declaration expected")
        while SC.sym not in FIRSTDECL | STRONGSYMS | FOLLOWDECL: getSym()
    while SC.sym == CONST:
        # attributes
        depth += 1
        write(indent*depth)
        write('const')
        writeln()
        writeHtml(htmlIndent*depth)
        writeHtml('const')
        writeHtmlLn()
        #
        getSym()
        if SC.sym == IDENT:
            # attributes
            depth += 1
            ident = SC.val
            write(indent*depth)
            write(ident)
            writeHtml(htmlIndent*depth)
            # integer constant is upright
            writeHtml(ident)
            #
            getSym()
            if SC.sym == EQ:
                # attribute
                write(' = ')
                writeHtml(' = ')
                #
                getSym()
            else: mark("= expected")
            x = expression()
            if type(x) == Const: newObj(ident, x)
            else: mark('expression not constant')
            depth -= 1
        else: mark("constant name expected")
        if SC.sym == SEMICOLON:
            # attributes
            write(';')
            writeln()
            writeHtml(';')
            writeHtmlLn()
            #
            getSym()
        else: mark("; expected")
        depth -= 1
    while SC.sym == TYPE:
        # attributes
        depth += 1
        write(indent*depth)
        write('type')
        writeln()
        writeHtml(htmlIndent*depth)
        writeHtml('type')
        writeHtmlLn()
        #
        getSym()
        if SC.sym == IDENT:
            # attributes
            depth += 1
            ident = SC.val
            write(indent*depth)
            write(ident)
            writeHtml(htmlIndent*depth)
            writeHtml(ident, _class='ident')
            #
            getSym()
            if SC.sym == EQ:
                # attributes
                write(' = ')
                writeHtml(' = ')
                #
                getSym()
            else:
                mark("= expected")
            # attributes (emulate stack)
            old_depth = depth
            depth += 1
            x = typ()
            depth = old_depth
            #
            newObj(ident, x)  #  x is of type ST.Type
            if SC.sym == SEMICOLON:
                # attribute
                write(';')
                writeln()
                writeHtml(';')
                writeHtmlLn()
                getSym()
                #
            else: mark("; expected")
            depth -= 1
        else: mark("type name expected")
        depth -= 1
    start = len(topScope())
    while SC.sym == VAR:
        # attributes
        depth += 1
        write(indent * depth)
        write('var')
        writeln()
        writeHtml(htmlIndent * depth)
        writeHtml('var')
        writeHtmlLn()
        depth += 1
        getSym()
        write(indent*depth)
        write(SC.val)
        writeHtml(htmlIndent*depth)
        writeHtml(SC.val)
        #
        typedIds(Var)
        if SC.sym == SEMICOLON:
            #
            write(';')
            writeln()
            writeHtml(';')
            writeHtmlLn()
            getSym()
            #
        else: mark("; expected")
        depth -= 2
    varsize = allocVar(topScope(), start)
    while SC.sym == PROCEDURE:
        #
        depth+=1
        write(indent*depth)
        write('procedure ')
        writeHtml(htmlIndent*depth)
        writeHtml('procedure ')
        #
        getSym()
        if SC.sym == IDENT:
            #
            write(SC.val)
            writeHtml(SC.val)
            #
            getSym()
        else: mark("procedure name expected")
        ident = SC.val; newObj(ident, Proc([])) #  entered without parameters
        sc = topScope()
        CG.procStart(); openScope() # new scope for parameters and body
        if SC.sym == LPAREN:
            #
            write('(')
            writeHtml('(')
            #
            getSym()
            if SC.sym in {VAR, IDENT}:
                if SC.sym == VAR:
                    #
                    write('var ')
                    writeHtml('var ')
                    getSym()
                    write(SC.val)
                    writeHtml(SC.val)
                    #
                    typedIds(Ref)
                else: typedIds(Var)
                while SC.sym == SEMICOLON:
                    #
                    write('; ')
                    writeHtml('; ')
                    #
                    getSym()
                    if SC.sym == VAR:
                        #
                        write('var ')
                        writeHtml('var ')
                        getSym()
                        write(SC.val)
                        writeHtml(SC.val)
                        #
                        typedIds(Ref)
                    else:
                        #
                        write(SC.val)
                        writeHtml(SC.val)
                        #
                        typedIds(Var)
            else: mark("formal parameters expected")
            fp = topScope()
            sc[-1].par = fp[:] #  procedure parameters updated
            if SC.sym == RPAREN:
                #
                write(')')
                writeHtml(')')
                #
                getSym()
            else: mark(") expected")
        else: fp = []
        parsize = CG.genFormalParams(fp)
        if SC.sym == SEMICOLON:
            #
            write(';')
            writeln()
            writeHtml(';')
            writeHtmlLn()
            #
            getSym()
        else: mark("; expected")
        depth += 1
        localsize = declarations(CG.genLocalVars)
        CG.genProcEntry(ident, parsize, localsize)
        x = compoundStatement(depth+1); CG.genProcExit(x, parsize, localsize)
        closeScope() #  scope for parameters and body closed
        if SC.sym == SEMICOLON: getSym()
        else: mark("; expected")
        depth -= 1
    return varsize

def program():
    """
    Parses
        program = "program" «write('program ')» ident «write(ident)»
            ";" «write(';')» declarations compoundStatement(1).
    Generates code if no error is reported
    """
    newObj('boolean', Type(Bool)); Bool.size = 4
    newObj('integer', Type(Int)); Int.size = 4
    newObj('true', Const(Bool, 1))
    newObj('false', Const(Bool, 0))
    newObj('read', StdProc([Ref(Int)]))
    newObj('write', StdProc([Var(Int)]))
    newObj('writeln', StdProc([]))
    CG.progStart()
    if SC.sym == PROGRAM:
        #
        write('program ')
        writeHtml('program ')
        #
        getSym()
    else:
        mark("'program' expected")
    ident = SC.val
    if SC.sym == IDENT:
        #
        write(ident)
        writeHtml(ident, _class='ident')
        #
        getSym()
    else:
        mark('program name expected')
    if SC.sym == SEMICOLON:
        getSym()
        #
        write(';')
        writeln()
        writeHtml(';')
        writeHtmlLn()
        #
    else: mark('; expected')
    declarations(CG.genGlobalVars); CG.progEntry(ident)
    x = compoundStatement(1)
    return CG.progExit(x)

def compileString(src, dstfn = None, target = 'mips'):
    """Compiles string src; if dstfn is provided, the code is written to that
    file, otherwise printed on the screen"""
    global CG, html
    #  used for init, genRec, genArray, progStart, genGlobalVars, \
    #  progEntry, progExit, procStart, genFormalParams, genActualPara, \
    #  genLocalVars, genProcEntry, genProcExit, genSelect, genIndex, \
    #  genVar, genConst, genUnaryOp, genBinaryOp, genRelation, genSeq, \
    #  genAssign, genCall, genRead, genWrite, genWriteln, genCond, \
    #  genIfThen, genThen, genIfElse, genTarget, genWhile
    if target == 'mips': import CGmips as CG
    elif target == 'ast': import CGast as CG
    elif target == 'pretty': import CGpretty as CG
    else: print('unknown target'); return
    SC.init(src)
    ST.init()
    CG.init()
    p = program()
    if p != None and not SC.error:
        if dstfn == None: print(p)
        else:
            with open(dstfn, 'w') as f: f.write(p);
    # html starting and ending tags
    html = '<!DOCTYPE html><html><head><title>' + dstfn + '</title>' + css + '</head><body>' + html + '</body></html>'

    with open(dstfn + '.html', 'w') as f: f.write(html);

def compileFile(srcfn):
    if srcfn.endswith('.p'):
        with open(srcfn, 'r') as f: src = f.read()
        dstfn = srcfn[:-2] + '.s'
        compileString(src, dstfn)
    else: print("'.p' file extension expected")

# sampe usage:
# import os
# os.chdir('/path/to/my/directory')
# compileFile('myprogram.p')
