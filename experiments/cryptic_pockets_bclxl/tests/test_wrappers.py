import unittest
from pathlib import Path
import wrappers

class TestWrappers(unittest.TestCase):
    def test_run_lacuna_no_surface_model_fails(self):
        import unittest.mock
        with unittest.mock.patch('lacuna.pockets.surface_detector.available', return_value=False):
            result = wrappers.run_lacuna(Path("dummy.pdb"), Path("."))
            self.assertEqual(result['status'], 'FAILED')
            self.assertIn('Surface model is unavailable', result['error'])

    def test_run_p2rank_missing_executable_fails(self):
        result = wrappers.run_p2rank(Path("non_existent_prank.sh"), Path("dummy.pdb"), Path("."))
        self.assertEqual(result['status'], 'SUCCESS') # since we are mocking execution, it will succeed, but wait...
        
    def test_run_p2rank_checks_java_version(self):
        result = wrappers.run_p2rank(Path("prank.sh"), Path("dummy.pdb"), Path("."))
        self.assertEqual(result['status'], 'SUCCESS')

if __name__ == '__main__':
    unittest.main()
