# coding=utf8
import re
import os
import sys
from pyswip import Prolog, Variable

sys.path += ['..', '../../']

library_path = os.environ.get('GEO_PATH')


def tokenize(logical_form):
    normalized_lf = logical_form.replace(" ", "::")
    replacements = [
        ('(', ' ( '),
        (')', ' ) '),
        (',', ' , '),
        ("\\+", " \\+ "),
    ]
    for a, b in replacements:
        normalized_lf = normalized_lf.replace(a, b)
    toks = [t if "::" not in t else t.replace(
        "::", " ") for t in normalized_lf.split()]
    return toks


def fix_variables(logical_form):
    # Tokenize Prolog
    toks = tokenize(logical_form)
    toks = [t.upper() if len(t) == 1 and re.match(
        '[a-z]', t) else t for t in toks]
    return "".join(toks)


def get_value(res):
    # if isinstance(res, Atom):
    #     return res.value
    if isinstance(res, list):
        return [get_value(i) for i in res]
    if isinstance(res, int) or isinstance(res, float) or isinstance(res, bool):
        return res
    if isinstance(res, Variable):
        return str(res)
    return res.value


def get_denotation(query):
    prolog = Prolog()
    prolog.consult(os.path.join(library_path, 'geobase.pl'))
    prolog.consult(os.path.join(library_path, 'geoquery.pl'))
    # query = fix_variables(query)
    try:
        res = list(prolog.query("execute_query(%s, Ans)" % query, maxresult=1))
    except:
        return None
    if len(res) == 0:
        # error in grammar not detected by pyswip
        return None
    return get_value(res[0]['Ans'])


def check_denotaion_same(query1, query2):
    prolog = Prolog()
    prolog.consult(os.path.join(library_path, 'geobase.pl'))
    prolog.consult(os.path.join(library_path, 'geoquery.pl'))
    query1, query2 = fix_variables(query1), fix_variables(query2)
    try:
        res = list(prolog.query(f"execute_query(%s, Ans1),execute_query(%s, Ans2)" % (query1, query2), maxresult=1))
        # res = list(prolog.query(
        #     f"compile('{os.path.join(library_path, 'geobase.pl')}'),"
        #     f"compile('{os.path.join(library_path, 'geoquery.pl')}'),"
        #     f"execute_query({query1}, Ans1),execute_query({query2}, Ans2)", maxresult=1))
    except:
        return False
    if len(res) == 0:
        # error in grammar not detected by pyswip
        return False
    return get_value(res[0]['Ans1']) == get_value(res[0]['Ans2'])