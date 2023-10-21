#!/usr/bin/env python3
import json
import sqlite3
from typing import Dict, Tuple

import pandas as pd
import sqlparse

from .bridge_content_encoder import get_database_matches

global_cache = {}


def maybe_add_quotes(val):
    if isinstance(val, str):
        return f'"{val}"'
    return str(val)


def get_db_schemas(db_root: str, db_name: str) -> Dict[str, str]:
    """
    Read an sqlite file, and return the CREATE commands for each of the tables in the database.
    """
    with sqlite3.connect(f'file:{db_root}/{db_name}/{db_name}.sqlite?mode=ro', uri=True) as conn:
        # conn.text_factory = bytes
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        schemas = {}
        for table in tables:
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='{}';".format(table[0]))
            schemas[table[0]] = cursor.fetchone()[0]
        return schemas


def get_db_rows(db_root: str, db_name: str, *, rows=5, db_content_matching=False,
                db_content_random=False, question=None) -> Dict[str, str]:
    """
    Read an sqlite database, and for each table return the first rows.
    """
    db_path = f'file:{db_root}/{db_name}/{db_name}.sqlite?mode=ro'
    results = {}
    with sqlite3.connect(db_path, uri=True) as conn:
        # conn.text_factory = bytes
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute("PRAGMA table_info({})".format(table[0]))
            if db_content_random:
                results[table[0]] = pd.read_sql_query(f"SELECT * FROM {table[0]} ORDER BY RANDOM() LIMIT {rows}", conn)
            else:
                results[table[0]] = pd.read_sql_query(f"SELECT * FROM {table[0]} LIMIT {rows}", conn)
        if db_content_matching and rows > 0:
            for table in results.keys():
                where_clauses = list()
                for col in results[table].keys():
                    matches = get_database_matches(question, table, col, db_path)
                    for match in matches:
                        where_clause = f'"{col}" = {maybe_add_quotes(match)}'
                        where_clauses.append(where_clause)
                if len(where_clauses) > 0:
                    table_matches = pd.read_sql_query(
                        f"SELECT DISTINCT * FROM {table} WHERE {' OR '.join(where_clauses)} LIMIT {rows}", conn)
                    results[table] = table_matches
    for k, v in results.items():
        results[k] = v.to_string(index=False)
    return results


def get_db_descriptions(db_root: str, db_name: str) -> Tuple[str, Dict[str, Dict[str, str]]]:
    """
    Get database and table descriptions for KaggleDBQA.
    """
    if db_root != 'kaggle':
        raise ValueError('Database descriptions are only available for KaggleDBQA.')

    with open('kaggle/KaggleDBQA_tables.json') as f:
        table_data = json.load(f)
    db_names = [td['db_id'] for td in table_data]
    db_index = db_names.index(db_name)
    db_description = table_data[db_index]['db_overview']
    descriptions = {}

    for i, table_name in enumerate(table_data[db_index]['table_names_original']):
        table_descriptions = {}
        for x in list(filter(lambda x: x[0][0] == i, zip(table_data[db_index]['column_names_original'],
                                                         table_data[db_index]['column_descriptions']))):
            table_descriptions[x[0][1]] = x[1]
        descriptions[table_name] = table_descriptions
    return db_description, descriptions


def get_db_prompt(db_root: str, db_name: str, schema=True, description=False, rows=0,
                  db_content_matching=False, db_content_random=False, question=None, reindent_aligned=True) -> str:
    """
    Construct prompt for Codex API call.
    """
    global global_cache
    key = f"{db_name}-{question}"
    if key in global_cache:
        return global_cache[key]

    schemas = get_db_schemas(db_root, db_name)
    examples = get_db_rows(db_root, db_name, rows=rows, db_content_matching=db_content_matching,
                           db_content_random=db_content_random, question=question)
    db_description, table_descriptions = get_db_descriptions(db_root, db_name) if description else ('', {})
    prompt = ''

    if description:
        prompt += f"-- {db_description}\n\n"

    if schema or (rows > 0) or description:
        for table in schemas.keys():
            if schema:
                prompt += sqlparse.format(schemas[table], reindent_aligned=reindent_aligned)
                prompt += '\n'
            if description:
                for col_name, col_description in table_descriptions[table].items():
                    prompt += f"-- {col_name}: {col_description}\n"
            if rows > 0:
                prompt += '/*\n'
                prompt += f'{rows} example rows from table {table}:\n'
                prompt += f'SELECT * FROM {table} LIMIT {rows};\n'
                if not schema:
                    prompt += f'Table: {table}\n'
                prompt += examples[table]
                prompt += '\n*/\n'
            prompt += '\n'

    global_cache[key] = prompt
    return prompt