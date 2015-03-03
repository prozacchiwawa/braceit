# Braceit

A simple parser that rejects a source file if 'if', 'else', 'while' or 'for' are not followed by a body with
curly braces.  Doesn't parse anything even remotely close to the full C or C++ language, but does recognize
and fail on these conditions.  Some C or C++ code might fool it, but so far it has worked well on a fairly
large C++ codebase.
