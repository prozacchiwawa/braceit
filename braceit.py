from lrparsing import Grammar, Prio, Ref, Token, Keyword, Tokens, Choice, TokenRegistry, repr_parse_tree

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
        _ = Token(re='[^ \t\r\n;{}\\(\\)]+|;|[{]|[}]|\\(|\\)|\"(\\.|[^"])*\"')
    WHITESPACE=' \t\r\n'
    # Thanks: http://ostermiller.org/findcomment.html
    COMMENTS=Token(re='(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//[^\r\n]*)')
    t_any = T._ | T._lp | T._rp
    t_any_cond = T._ | T._semi
    t_any_semi = t_any | T._semi
    cond_mid = Ref("cond_mid")
    cond_mid = t_any_cond | \
               t_any_cond + cond_mid | \
               T._lp + T._rp | \
               T._lp + cond_mid + T._rp | \
               T._lp + T._rp + cond_mid | \
               T._lp + cond_mid + T._rp + cond_mid
    cond = T._lp + cond_mid + T._rp
    body = Ref("body")
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
    txunit = Ref("txunit")
    txunit = toplevel | toplevel + txunit
    START = txunit


def printer(x):
    print x

if __name__ == '__main__':
    import sys, traceback
    for fn in sys.argv[1:]:
        try:
            print '%s:' % fn
            ps = pp_strip(open(fn).read())
            PermissiveLanguageParser.parse(ps)
        except Exception as e:
            traceback.print_exc()
            sys.exit(1)
