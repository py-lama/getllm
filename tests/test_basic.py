import unittest

class TestBasic(unittest.TestCase):
    def test_import(self):
        """Test that the package can be imported"""
        try:
            import getllm
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import getllm package")

if __name__ == "__main__":
    unittest.main()
