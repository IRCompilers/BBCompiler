import unittest
from unittest.mock import patch
from io import StringIO
import sys


def method_to_test():
    print("Hello, World!")


class TestPrint(unittest.TestCase):
    @patch('sys.stdout', new_callable=StringIO)
    def test_output(self, mock_stdout):
        method_to_test()
        self.assertEqual(mock_stdout.getvalue(), "Hello, World!\n")


if __name__ == '__main__':
    unittest.main()
