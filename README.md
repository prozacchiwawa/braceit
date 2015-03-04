# Braceit

A simple parser that rejects a source file if 'if', 'else', 'while' or 'for' are not followed by a body with
curly braces.  It's obviously too simple to distinguish valid C and C++ from relative gibberish but it does
enough to notice that conditionals in these languages are followed by statements without braces
and fail on these conditions.  Some C or C++ code might fool it, but so far it has worked well on a fairly
large C++ codebase.
