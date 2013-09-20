#!/usr/bin/python
"""Touch up a LaTeX file

   Snarf up a LaTeX input file importing appropriate code where requested
   and adding markup to code snippets delimited by #'s"""
import sys
from sys import argv
import re


def matches(line, methods):
    """Math a line of python code to a method definition

    Determine if this line of python code is a method definition listed
    in methods"""
    m = re.match(r'\s{4}def\s+(\w+)(\(.*\))\s*:', line)
    if (not m): return False
    name = m.group(1)
    args = re.sub(r' |self,', '', m.group(2))
    sig = name + args
    return sig in methods
    
def touchup_code(line):
    """Touch up a line of python code to make it look more like pseudocode"""
    # some easy cleanups
    line = re.sub(r'==', r'=', line)
    line = re.sub(r'self\.', '', line)
    line = re.sub(r'\bdef ', '', line)
    line = re.sub(r'\bself\b,?\s*', '', line)
    # for <blah>: => for <blah> do
    line = re.sub(r'\b(for\b[^:]+):', r'\1 do', line)
    # if <blah>: => if <blah> then
    line = re.sub(r'\bif (.*):', r'if \1 then', line) 
    # len(<blah>) => length(<blah>)
    line = re.sub(r'\blen\s*\(\s*(\w+)\s*\)', r'length(\1)', line)
    line = re.sub(r'\b(\w+)\.length', r'length(\1)', line)
    # range(a,b,-1) => a,...,b+1
    line = re.sub(r'\brange\s*\(\s*(.*),\s*(.*),\s*-1\s*\)',
                  r'\2,...,\1+1', line)
    # range(a, b-1) => a,...,b-2
    line = re.sub(r'\brange\s*\(\s*(.*),\s*(.*)\s*\-\s*1\s*\)', 
                  r'\1,...,\2-2', line)
    # range(a, b) => a,...,b-1
    line = re.sub(r'\brange\s*\(\s*(.*),\s*(.*)\s*\)', r'\1,...,\2-1', line)
    # range(a) => 0,...,a-1
    line = re.sub(r'\brange\s*\(\s*([^),]+)\s*\)', r'0,...,\1-1', line)
    # a += b => a = a + b
    line = re.sub(r'\b(\w+)\b\s*\+=\s*(.*)\s*', r'\1 = \1 + \2', line)
    line = re.sub(r'\b(\w+)\b\s*-=\s*(.*)\s*', r'\1 = \1 - \2', line)
    # get rid of any remaining colons
    line = re.sub(r':', '', line)
    return line

def color_code(code):
    """Syntax highlight a piece of code"""
    keywords = r'\b(if|then|else|in|for|do)\b'
    code = re.sub(keywords, r'{\color{keyword}\1}', code)
    return line

def print_code(clazz, methods):
    """Print out the methods in clazz that are listed in methods"""
    print r'\begin{Verbatim}[frame=single,label=\texttt{%s}]' % clazz 
    printed = False
    try:
        filename = "../python/" + clazz.lower() + ".py"
        code = open(filename).read().splitlines()
        printing = False
        for line in code:
            line = re.sub(r'[ \.]_', ' ', line)
            line = re.sub(r'_[ \.]', ' ', line)
            line = re.sub(r'\(\s*self\s*\)', '()', line)
            if printing:
                printing = line == '' or line.startswith('     ')
            if not printing and matches(line, methods):
                printing = True
            if printing and len(line.strip()) > 0:
                printed = True
                print touchup_code(line)
    except IOError:
        print "Unable to open %s" % filename
    if not printed: print "NO OUTPUT"
    print r'\end{Verbatim}'

def code_subs(line):
    """Touch up code snippets in a line of LaTeX code"""
    pattern = r'#([^#]+)#'
    m = re.search(pattern, line)
    while m:
        code = touchup_code(m.group(1))
        if re.search(r'[A-Z]\w*', code):
            code = r'\\texttt{%s}' % code # just a class name
        else:
            code = re.sub(r'%', r'\%', code)
            code = re.sub(r'&', r'\&', code)
            code = r'\ensuremath{\mathtt{%s}}' % code
        line = re.sub(pattern, code, line, 1)
        m = re.search(pattern, line)
    return line

def snarf(infile):
    """Program entry point"""
    lines = infile.read().splitlines();
    for line in lines:
        if line.startswith(r'\cppimport') or line.startswith(r'\javaimport'):
            print "%%%s" % line
        elif line.startswith('\\codeimport'):
            print "%%importing %s: " % line
            m = re.search(r'\{\w+/(\w+)(.*)\}', line)
            clazz = m.group(1)
            methods = m.group(2).lstrip('.').split('.')
            print_code(clazz, methods)
        else:
            print code_subs(line)

def die(msg, code=-1):
    """Print the error message msg and exit"""
    sys.stderr.write("Fatal Error: " + msg + "\n")
    sys.exit(code)

if len(argv) == 1:
    infile = sys.stdin
elif len(argv) == 2:
    try:
        infile = open(argv[1])
    except IOError:
        die("Unable to open input file %s" % argv[1])
else:
    die("Usage: %s [<infile>]" % argv[0])
snarf(infile)



