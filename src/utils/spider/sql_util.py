#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
from typing import Tuple, Any, List, Set
import sqlparse
import sqlite3
import os


def sql_process(query):
    completion = query.replace('\n', ' ')
    completion = re.sub(r'\\t', '  ', completion)
    completion = re.sub(' +', ' ', completion)
    completion = completion.split("/*")[0].strip()
    if completion.startswith("SELECT"):
        completion = completion[6:].strip()
    query = sqlparse.format(f"SELECT {completion}", strip_comments=True)
    return query


def replace_cur_year(query: str) -> str:
    return re.sub(
        "YEAR\s*\(\s*CURDATE\s*\(\s*\)\s*\)\s*", "2020", query, flags=re.IGNORECASE
    )


# get the database cursor for a sqlite database path
def get_cursor_from_path(sqlite_path: str):
    try:
        if not os.path.exists(sqlite_path):
            print("Openning a new connection %s" % sqlite_path)
        connection = sqlite3.connect(sqlite_path)
    except Exception as e:
        print(sqlite_path)
        raise e
    connection.text_factory = lambda b: b.decode(errors="ignore")
    cursor = connection.cursor()
    return cursor


def add_collate_nocase(query: str):
    value_regexps = ['"[^"]*"', "'[^']*'"]
    value_strs = []
    for regex in value_regexps:
        value_strs += re.findall(regex, query)
    for str_ in set(value_strs):
        query = query.replace(str_, str_ + " COLLATE NOCASE ")
    return query


def exec_on_db(entry):
    db_path = entry['db_path']
    query = entry['query']
    db_id = entry['db_id']
    db_path = f'{db_path}/{db_id}/{db_id}.sqlite'
    query = replace_cur_year(query)
    query = add_collate_nocase(query)
    cursor = get_cursor_from_path(db_path)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        cursor.connection.close()
        return_tuple = ('result', result)
    except Exception as e:
        cursor.close()
        cursor.connection.close()
        return_tuple = ('exception', None)
    return return_tuple


def unorder_row(row: Tuple) -> Tuple:
    return tuple(sorted(row, key=lambda x: str(x) + str(type(x))))


# unorder each row in the table
# [result_1 and result_2 has the same bag of unordered row]
# is a necessary condition of
# [result_1 and result_2 are equivalent in denotation]
def quick_rej(result1: List[Tuple], result2: List[Tuple], order_matters: bool = False) -> bool:
    s1 = [unorder_row(row) for row in result1]
    s2 = [unorder_row(row) for row in result2]
    if order_matters:
        return s1 == s2
    else:
        return set(s1) == set(s2)


def result_eq(result1, result2) -> bool:
    if len(result1) == 0 and len(result2) == 0:
        return True

    # if exactly same, then return true
    if str(result1) == str(result2):
        return True

    # if length is not the same, then they are definitely different bag of rows
    if len(result1) != len(result2):
        return False

    num_cols = len(result1[0])

    # if the results do not have the same number of columns, they are different
    if len(result2[0]) != num_cols:
        return False

    # unorder each row and compare whether the denotation is the same
    # this can already find most pair of denotations that are different
    if not quick_rej(result1, result2):
        return False

    # if not strict, two sqls can be seem as equal if they pass above conditions
    return True
