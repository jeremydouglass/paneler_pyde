"""Simple unit testing for Processing.py sketches.

A single-tab simple unit testing solution for Processing.py.
Add groups of tests here organized in the unittest style:
Group test sets to be run simultaneously in classes that
extend unittest.TestCase. Group related tests as functions
named test_foo within TestCase classes.

Use `tests.run()` to auto-discover and run all tests.
Use `tests.run(TestFoo)` to run one specific test class.

"""
import unittest
import itertools
import os
import sys

import parser
import render
import utils

def run(case=None, out=sys.stdout):
    """Simple test runner.

    Call with case = a specific test set:
    the class name of a TestCase-derived class.
    When no case is provided, discovers and runs
    all tests in its own module (its own PDE tab).

    Default to normal console text (white text),
    set out=sys.stderr to print as error (red text).

    Args:
        case (TestCase): Tests to run.
        out  (stream file object): Where to write results.

    """
    if case is not None:
        suite = unittest.TestLoader().loadTestsFromTestCase(case)
    else:
        # load all tests from this module
        suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    # run test suite
    unittest.TextTestRunner(stream=out, descriptions=True,
                            verbosity=2, failfast=False, buffer=False,
                            resultclass=None).run(suite)

def phtml_equal(pcode_str1, pcode_str2, parselevel=parser.root):
    pcode_obj1 = parser.parse(pcode_str1, parselevel)
    pcode_obj2 = parser.parse(pcode_str2, parselevel)
    pcode_html1 = render.pobj_to_html5_ccs3_grid(pcode_obj1)
    pcode_html2 = render.pobj_to_html5_ccs3_grid(pcode_obj2)
    return (pcode_html1 == pcode_html2)

def item_pair_equalities(test_items):
    test_pairs = itertools.combinations (test_items, 2)
    for item1, item2 in (test for test in test_pairs):
        yield(phtml_equal(item1, item2))

class TestEnvironment(unittest.TestCase):
    """Confirm presence of default named directories and files."""

    def test_paths(self):
        """Check basic directory structure. """
        root = sketchPath()
        self.assertTrue(os.path.isdir(root))
        self.assertTrue(os.path.isdir(root  + '/data/input'))
        self.assertTrue(os.path.isdir(root  + '/data/output'))
        self.assertTrue(os.path.isdir(root  + '/data/templates'))
        self.assertTrue(os.path.isfile(root + '/data/templates/gallery_css3.html'))
        self.assertTrue(os.path.isdir(root  + '/styles'))
        self.assertTrue(os.path.isfile(root  + '/styles/panelcode-grid.css'))
        self.assertTrue(os.path.isfile(root + '/styles/site.css'))

class TestPickling(unittest.TestCase):
    """Test picking and unpicking of panelcode objects."""

    def test_load_save_remove(self):
        """Save, load, and remove pickled (serialized) panelcode pyparsing objects."""
        pcode_obj = parser.parse("1_2_3", parser.root)
        self.assertFalse(utils.exists('test.pickle'))
        utils.pickle_dump(pcode_obj, 'test.pickle')
        self.assertTrue(utils.exists('test.pickle'))
        pcode_obj2 = utils.pickle_load('test.pickle')
        self.assertEqual(pcode_obj.dump(), pcode_obj2.dump())
        utils.pickle_remove('test.pickle')
        self.assertFalse(os.path.exists('test.pickle'))

class TestRenderHTML(unittest.TestCase):
    """Test that renders are panelcode-correct and html-valid."""

    def test_simple_rows_summative(self):
        """Simple row addition is summative: 1+2 = 3."""
        self.assertTrue(phtml_equal('1+2', '3'))
        self.assertTrue(phtml_equal('2+5', '7'))
        self.assertTrue(phtml_equal('1+2+3', '6'))
        # check 0 in 10 isn't misparsed
        self.assertTrue(phtml_equal('7+3', '10'))
        # check two digits
        self.assertTrue(phtml_equal('4+7', '11'))
        self.assertTrue(phtml_equal('11+11', '22'))
        # wrong sums should fail
        self.assertFalse(phtml_equal('1+2', '4'))
        # sums work in layouts
        self.assertTrue(phtml_equal('1+2_3', '3_3'))
        self.assertFalse(phtml_equal('1+2_3', '3_4'))
        # sums work in layouts
        self.assertTrue(phtml_equal('1+2;3', '2+1;3'))
        self.assertTrue(phtml_equal('2+5;3', '7;3'))
        self.assertTrue(phtml_equal('10+2;3', '12;3'))
        self.assertTrue(phtml_equal('11+12;3', '23;3'))
        # sums work in spreads
        self.assertTrue(phtml_equal('1+2|3', '3|3'))
        self.assertTrue(phtml_equal('2+5|3', '7|3'))
        self.assertTrue(phtml_equal('10+2|3', '12|3'))
        self.assertTrue(phtml_equal('11+12|3', '23|3'))
        # sums work in galleries
        self.assertTrue(phtml_equal('1+2@3', '2+1@3'))
        self.assertTrue(phtml_equal('2+5@3', '7@3'))
        self.assertTrue(phtml_equal('10+2@3', '12@3'))
        self.assertTrue(phtml_equal('11+12@3', '23@3'))
        # sums fail with attributes -- attributed units are not summative
        self.assertFalse(phtml_equal('r2+2', '3.r2'))
        self.assertFalse(phtml_equal('1r2+2', '3.r2'))
        self.assertFalse(phtml_equal('1.r2+2', '3.r2'))
        self.assertFalse(phtml_equal('2r2+1', '3.r2'))
        self.assertFalse(phtml_equal('2.r2+1', '3.r2'))

    def test_simple_rows_commutative(self):
        """Simple row addition is commutative: 1+2 = 2+1."""
        test_sets = []
        test_sets.append([('1+2', '2+1'), ('2+5', '5+2'), ('10+2', '2+10'), ('1+2+3', '2+3+1'), ('1+2+3', '3+2+1')])
        ## build a commutative test set for each level delimiter
        test_sets.append([('1+2,3', '2+1,3'), ('2+5,3', '5+2,3'), ('10+2,3', '2+10,3'), ('11+12,3', '12+11,3')])
        test_sets.append([('1+2;3', '2+1;3'), ('2+5;3', '5+2;3'), ('10+2;3', '2+10;3'), ('11+12;3', '12+11;3')])
        test_sets.append([('1+2|3', '2+1|3'), ('2+5|3', '5+2|3'), ('10+2|3', '2+10|3'), ('11+12|3', '12+11|3')])
        test_sets.append([('1+2@3', '2+1@3'), ('2+5@3', '5+2@3'), ('10+2@3', '2+10@3'), ('11+12@3', '12+11@3')])
        for test_pairs in test_sets:
            for item1, item2 in (pair for pair in test_pairs):
                self.assertTrue(phtml_equal(item1, item2))

    def test_levels_non_commutative(self):
        """All levels above adjascent units are not commutative."""
        test_sets = []
        ## build a non-commutative test set for each level delimiter
        test_sets.append([('1;2', '2;1'), ('2;5', '5;2'), ('10;2', '2;10'), ('1;2;3', '2;3;1'), ('1;2;3', '3;2;1')])
        test_sets.append([('1|2', '2|1'), ('2|5', '5|2'), ('10|2', '2|10'), ('1|2|3', '2|3|1'), ('1|2|3', '3|2|1')])
        test_sets.append([('1@2', '2@1'), ('2@5', '5@2'), ('10@2', '2@10'), ('1@2@3', '2@3@1'), ('1@2@3', '3@2@1')])
        for test_pairs in test_sets:
            for item1, item2 in (pair for pair in test_pairs):
                self.assertFalse(phtml_equal(item1, item2))

    def test_simple_zero_units(self):
        """Zero units are NOT commutative, and have no additive identity (not summative)."""
        ## no additive identity
        self.assertFalse(phtml_equal('0', '0+0'))
        self.assertFalse(phtml_equal('0+1', '1'))
        self.assertFalse(phtml_equal('0+5', '5'))
        self.assertFalse(phtml_equal('0+10', '10'))
        self.assertFalse(phtml_equal('0+11', '11'))
        ## not commutative
        self.assertFalse(phtml_equal('0+1', '1+0'))
        self.assertFalse(phtml_equal('0+5', '5+0'))
        self.assertFalse(phtml_equal('0+10', '10+0'))
        self.assertFalse(phtml_equal('0+11', '11+0'))
        self.assertFalse(phtml_equal('1+0+2', '3+0'))
        self.assertFalse(phtml_equal('1+0+2', '0+3'))
        ## however doesn't interfere with normal units being commutative
        self.assertTrue(phtml_equal('1+2+0', '3+0'))
        self.assertTrue(phtml_equal('9+10+0', '19+0'))

    def test_simple_units_concise(self):
        """Unts can be written concisely: 1.r2 = 1r2 = r2"""
        self.assertTrue(phtml_equal('r2', '1r2'))
        self.assertTrue(phtml_equal('1r2', '1.r2'))
        self.assertTrue(phtml_equal('5r2', '5.r2'))
        # check 0 isn't misparsed
        self.assertTrue(phtml_equal('10r2', '10.r2'))
        # check two digits
        self.assertTrue(phtml_equal('11r2 +22r2 ', '33.r2'))

    def test_simple_groups(self):
        """Simple groups can be written with or without parens."""
        self.assertTrue(phtml_equal('(1,1)', '1,1'))
        self.assertTrue(phtml_equal('(2,1)', '2,1'))
        ## with attributes
        self.assertTrue(phtml_equal('(1.r2+1,1)', '1.r2+1,1'))
        self.assertTrue(phtml_equal('(1r2+1,1)', '1r2+1,1'))
        self.assertTrue(phtml_equal('(r2+1,1)', 'r2+1,1'))
        self.assertTrue(phtml_equal('(2.r2+1,1)', '2.r2+1,1'))
        self.assertTrue(phtml_equal('(2r2+1,1)', '2r2+1,1'))

    def test_level_inequalities(self):
        """No level join/division should be equivalent to any other."""
        for result in item_pair_equalities(['1+1', '1,1', '1_1', '1;1', '1|1', '1@1']):
            self.assertFalse(result)
        for result in item_pair_equalities(['2+3', '2,3', '2_3', '2;3', '2|3', '2@3']):
            self.assertFalse(result)
        for result in item_pair_equalities(['9+10+11', '9,10,11', '9_10_11', '9;10;11', '9|10|11', '9@10@11']):
            self.assertFalse(result)

    def test_whitespace_linebreaks(self):
        """Linebreaks have no impact on parsing between units."""
        test_items = ['1+2', '1+\n2', '1\n+2', '1\n+\n2']
        test_sets = []
        test_sets.append(test_items)
        ## build a linebreak test set for each level delimiter
        test_sets.append([item.replace('+', ',') for item in test_items])
        test_sets.append([item.replace('+', '_') for item in test_items])
        test_sets.append([item.replace('+', ';') for item in test_items])
        test_sets.append([item.replace('+', '|') for item in test_items])
        test_sets.append([item.replace('+', '@') for item in test_items])
        for tests in test_sets:
            for result in item_pair_equalities(tests):
                self.assertTrue(result)

    def test_whitespace_spaces(self):
        test_items = ['1+2', ' 1+2', '1 +2', '1+ 2', '1+2 ', '1 + 2', ' 1 + 2 ']
        test_sets = []
        test_sets.append(test_items)
        ## build a linebreak test set for each level delimiter
        test_sets.append([item.replace('+', ',') for item in test_items])
        test_sets.append([item.replace('+', '_') for item in test_items])
        test_sets.append([item.replace('+', ';') for item in test_items])
        test_sets.append([item.replace('+', '|') for item in test_items])
        test_sets.append([item.replace('+', '@') for item in test_items])
        for tests in test_sets:
            for result in item_pair_equalities(tests):
                self.assertTrue(result)

    def test_whitespace_tabs(self):
        test_items = ['1+2', '\t1+2', '1\t+2', '1+\t2', '1+2\t', '1\t+\t2', '\t1\t+\t2\t']
        test_sets = []
        test_sets.append(test_items)
        ## build a linebreak test set for each level delimiter
        test_sets.append([item.replace('+', ',') for item in test_items])
        test_sets.append([item.replace('+', '_') for item in test_items])
        test_sets.append([item.replace('+', ';') for item in test_items])
        test_sets.append([item.replace('+', '|') for item in test_items])
        test_sets.append([item.replace('+', '@') for item in test_items])
        for tests in test_sets:
            for result in item_pair_equalities(tests):
                self.assertTrue(result)

if __name__ == '__main__':
    ## Discover and run all tests on main entrypoint.
    unittest.main(exit=False)
    