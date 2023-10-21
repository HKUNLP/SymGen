import importlib
from .filter_tool import FilterTool


def get_filter(name, **kwargs):
    filter_getter = importlib.import_module('src.filters.{}_filter'.format(name)).filter_getter
    return FilterTool(filter_getter=filter_getter, **kwargs)