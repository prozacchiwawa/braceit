import re
from lrparsing import Grammar, Prio, Ref, Token, Keyword, Tokens, Choice, Repeat, TokenRegistry, repr_parse_tree

def pp_strip(txt):
    lines = txt.split('\n')
    ol = []
    stripping = False
    for l in lines:
        line = l.strip()
        if not stripping:
            if line.startswith('#'):
                stripping = True
        if not stripping:
            ol.append(l)
        else:
            ol.append('')
            if not line.endswith('\\'):
                stripping = False
    return '\n'.join(ol)

class PermissiveLanguageParser(Grammar):
    """Consumes a language whose main feature is that when it contains tokens matching
    'if', 'else', 'for', 'do' and 'while', these are followed by curly brace bodies.
    Specifically, semicolon is illegal between 'if' and 'else' unless it occurs in a curly
    brace body, between 'do' and 'while', after 'while' or 'for' and their conditional
    expression but before a curly brace body.  This parser recognizes C but doesn't care
    all that much about what's consumed.  The only purpose is to stop parsing when 'if',
    'while' or 'for' are used without curly braces."""

    class T(TokenRegistry):
        _do = Keyword('do')
        _else = Keyword('else')
        _for = Keyword('for')
        _if = Keyword('if')
        _while = Keyword('while')
        _switch = Keyword('switch')
        _lb = Keyword('{')
        _rb = Keyword('}')
        _lp = Keyword('(')
        _rp = Keyword(')')
        _semi = Keyword(';')
        # Note: I've avoided using ( and ) in the regex below because they
        # match the regexes lrparsing uses to find groups.
        _ = Token(re='[^\'-\\* \t\r\n;\\}\\{"]+') | \
            Token(re='(\\()|(\\))') | \
            Token(re='\\*') | \
            Token(re=';') | \
            Token(re='\\{') | \
            Token(re='\\}') | \
            Token(re='"(\\\\.|[^"])*"') | \
            Token(re="'(\\\\.|[^'])*'")
    WHITESPACE=' \t\r\n'
    # Thanks: http://ostermiller.org/findcomment.html
    COMMENTS=Token(re='(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//[^\r\n]*)')
    t_any = T._ | T._lp | T._rp
    t_any_cond = T._ | T._semi
    t_any_semi = t_any | T._semi
    body = Ref("body")
    cond_mid = Ref("cond_mid")
    cond_mid = t_any_cond | \
               t_any_cond + cond_mid | \
               T._lp + T._rp | \
               T._lp + cond_mid + T._rp | \
               T._lp + T._rp + cond_mid | \
               T._lp + cond_mid + T._rp + cond_mid | \
               body
    cond = T._lp + cond_mid + T._rp
    stmt = Ref("stmt")
    if_stmt = Ref("if_stmt")
    if_stmt = T._if + cond + body | \
              T._if + cond + body + T._else + body | \
              T._if + cond + body + T._else + if_stmt
    stmt = if_stmt | \
           T._do + body + T._while + cond + T._semi | \
           T._while + cond + body | \
           T._for + cond + body | \
           T._switch + cond + body | \
           T._semi | \
           body | \
           t_any
    stmts = Ref("stmts")
    stmts = stmt + stmts | stmt
    body = T._lb + T._rb | T._lb + stmts + T._rb
    decl = Ref("decl")
    decl = T._semi | t_any + decl
    defn = Ref("defn")
    defn = body | t_any + defn
    toplevel = defn | decl
    START = Repeat(toplevel)

def printer(x):
    print x

def read_file(fn):
    import codecs
    data = open(fn,'rb').read()
    if data.startswith(codecs.BOM_UTF16):
        return codecs.encode(codecs.decode(data,'utf_16'),'utf_8')
    else:
        return data

def parse(fn):
    import os
    import os.path
    if os.path.isdir(fn):
        sublist = [os.path.join(fn,x) for x in os.listdir(fn) if os.path.splitext(x)[1] in ['.c','.cpp','.h','.hpp','.cxx','.hxx','.cc','.hh']]
        for fn in sublist:
            if not parse(fn):
                return False
    else:
        try:
            ps = pp_strip(read_file(fn))
            PermissiveLanguageParser.parse(ps)
            return True
        except Exception as e:
            print '%s:' % fn
            traceback.print_exc()
            return False

if __name__ == '__main__':
    import sys, traceback
    for fn in sys.argv[1:]:
        if not parse(fn):
            sys.exit(1)
