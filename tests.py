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
import os
import sys

import parser
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

if __name__ == '__main__':
    ## Discover and run all tests on main entrypoint.
    unittest.main(exit=False)
    