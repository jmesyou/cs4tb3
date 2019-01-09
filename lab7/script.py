#!/usr/bin/env python3

'''
names: James You, Zicheng Jiang
'''

from enum import Enum, auto

"""
    Enum-like class to represent Pascal0 classes, all entries in the SymbolTable
    must represent 1 of these classes
"""
class Class(Enum):
    HEAD = auto()
    VAR = auto()
    PAR = auto()
    CONST = auto()
    FIELD = auto()
    TYPE = auto()
    PROC = auto()
    SPROC = auto()

class SymbolTable:

    """
        SymbolTable constructor for linked list representation of Pascal0
        Symbol Table

        Usage:
            import script as pascal0
            st = pascal0.SymbolTable()
    """
    def __init__(self):
        self.lvl = 0
        self.top_scope = self.new_obj({'dsc': None}, Class.HEAD)

    """
        Add a new obj to the current scope, only the needed fields are called
        from the `obj` variable, all extra fields are considered redundant.

        For example:
        a Class.VAR object is a dict of {'name': $NAME, 'tp': $TYPE, 'val': $VAL}
        all other fields are constructed by the method

        usage:
            import script as pascal0
            st = pascal0.SymbolTable()
            st.new_obj({'name': 'x', 'type': 'integer', 'val': 1})
    """
    def new_obj(self, obj, cls):
        if cls not in Class:
            raise NameError("Error: invalid class")
        obj_desc = {
            'cls': cls,
            'lev': self.lvl if cls in [Class.VAR] else None,
            'next': None,
            'dsc': obj['dsc'] if cls is Class.HEAD else None,
            'tp': obj['tp'] if cls in [Class.VAR, Class.PAR, Class.CONST, Class.FIELD] else None,
            'name': obj['name'] if cls in [Class.VAR, Class.PAR, Class.CONST, Class.FIELD, Class.TYPE, Class.PROC] else None,
            'val': obj['val'] if cls is not Class.HEAD else None,
        }

        if cls is not Class.HEAD:
            obj_iter = self.top_scope
            while obj_iter['next'] is not None:
                obj_iter = obj_iter['next']
                if obj_iter['name'] == obj['name']:
                    raise NameError('Error: id {} already defined'.format(obj['name']))
            obj_iter['next'] = obj_desc

        return obj_desc

    """
        Open a scope, increase scope depth by 1
    """
    def open_scope(self):
        self.top_scope = self.new_obj({'dsc': self.top_scope}, Class.HEAD)
        self.lvl += 1
        return

    """
        Immediately delete the top, leaving it with no pointer references
        for garbage collection, decrease depth by 1

        raises:
            LookupError - if at minimum scope depth (universe)
    """
    def close_scope(self):
        if self.lvl:
            self.top_scope = self.top_scope['dsc']
            self.lvl -= 1
            return
        else:
            raise LookupError("Error: reached universe scope, no more scopes to close")

    """
        Search for an object by id (the 'name' field)

        usage:
            import script as pascal0
            st = pascal0.SymbolTable()
            st.new_obj({'name': 'x', 'type': 'integer', 'val': 1})
            st.find({'name': 'x'})
    """
    def find(self, var):
        scope = self.top_scope
        while True:
            obj = scope # HEAD
            while obj['next'] is not None:
                obj = obj['next']
                if obj['name'] == var['name']:
                    return obj
            scope = scope['dsc']
            if scope['dsc'] is None:
                raise NameError('Error: {} undefined', var)
            else:
                scope = scope['dsc']
