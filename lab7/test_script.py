'''
name: James You
'''

import pytest
import script as pascal0

class TestPascal0:

    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
        usually contains tests).
        """

    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """

    def setup_method(self, method):
        self.st = pascal0.SymbolTable()

    def teardown_method(self, method):
        self.st = None

    def test_new_obj_NameError(self):
        with pytest.raises(NameError):
            self.st.new_obj({'dsc', None}, None)

        self.st.new_obj({'name': 'x', 'tp': 'boolean', 'val': True}, pascal0.Class.CONST)
        with pytest.raises(NameError):
            self.st.new_obj({'name': 'x', 'tp': 'integer', 'val': 1}, pascal0.Class.VAR)

    def test_new_obj_VAR(self):
        self.st.new_obj({'name': 'x', 'tp': 'integer', 'val': 1}, pascal0.Class.VAR)
        assert self.st.top_scope['next'] == {'cls': pascal0.Class.VAR,\
                                            'lev': self.st.lvl,\
                                            'next': None,\
                                            'dsc': None,\
                                            'tp': 'integer',\
                                            'name': 'x',\
                                            'val': 1\
                                            }

    def test_new_obj_HEAD(self):
        assert self.st.top_scope == {'cls': pascal0.Class.HEAD,\
                                    'lev': None,\
                                    'next': None,\
                                    'dsc': None,\
                                    'tp': None,\
                                    'name': None,\
                                    'val': None\
                                    }

    def test_new_obj_CONST(self):
        self.st.new_obj({'name': 'IS_TRUE', 'tp': 'boolean', 'val': True}, pascal0.Class.CONST)
        assert self.st.top_scope['next'] == {'cls': pascal0.Class.CONST,\
                                            'lev': None,\
                                            'next': None,\
                                            'dsc': None,\
                                            'tp': 'boolean',\
                                            'name': 'IS_TRUE',\
                                            'val': True\
                                            }


    def test_open_scope(self):
        self.st.open_scope()
        assert self.st.lvl == 1
        self.st.open_scope()
        assert self.st.lvl == 2

    def test_close_scope_LookupError(self):
        with pytest.raises(LookupError):
            self.st.close_scope();

    def test_close_scope(self):
        self.st.open_scope()
        self.st.close_scope()
        assert self.st.lvl == 0

    def test_find(self):
        self.st.new_obj({'name': 'x', 'tp': 'boolean', 'val': True}, pascal0.Class.CONST)
        self.st.open_scope()
        self.st.new_obj({'name': 'x', 'tp': 'integer', 'val': 1}, pascal0.Class.VAR)
        assert self.st.find({'name': 'x'}) == {'cls': pascal0.Class.VAR,\
                                                'lev': 1,\
                                                'next': None,\
                                                'dsc': None,\
                                                'tp': 'integer',\
                                                'name': 'x',\
                                                'val': 1\
                                                }

    def test_find_NameError(self):
        self.st.new_obj({'name': 'x', 'tp': 'boolean', 'val': True}, pascal0.Class.CONST)
        self.st.open_scope()
        self.st.new_obj({'name': 'x', 'tp': 'integer', 'val': 1}, pascal0.Class.VAR)
        with pytest.raises(NameError):
            self.st.find({'name': 'y'})
