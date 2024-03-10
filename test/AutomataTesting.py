import unittest
from src.Common.Automaton import DFA, NFA
from src.Common.AutomatonUtils import nfa_to_dfa

class TestAutomata(unittest.TestCase):

    def test_dfa(self):
        dfa_transitions = {
            (0, '0'): 0,
            (0, '1'): 1,
            (1, '0'): 2,
            (2, '1'): 3,
            (3, '0'): 2,
            (3, '1'): 3,
        }
        dfa = DFA(states=4, finals=[3], transitions=dfa_transitions)

        self.assertTrue(dfa.recognize('0101'))
        self.assertFalse(dfa.recognize('1001'))

    def test_nfa(self):
        nfa_transitions = {
            (0, 'a'): [1],
            (1, 'b'): [2, 3],
            (2, 'c'): [4],
            (3, 'c'): [4],
            (0, 'b'): [3],
            (3, 'b'): [3],
        }
        nfa = NFA(states=5, finals=[2, 4], transitions=nfa_transitions)

        self.assertTrue(nfa.recognize('abc'))
        self.assertFalse(nfa.recognize('bcbc'))
        self.assertFalse(nfa.recognize('acb'))
        self.assertTrue(nfa.recognize('ab'))

    def test_nfa_to_dfa(self):
        nfa_transitions = {
            (0, 'a'): [1],
            (1, 'b'): [2, 3],
            (2, 'c'): [4],
            (3, 'c'): [4],
            (0, 'b'): [3],
            (3, 'b'): [3],
        }
        nfa = NFA(states=5, finals=[2, 4], transitions=nfa_transitions)
        dfa = nfa_to_dfa(nfa)

        self.assertTrue(dfa.recognize('abc'))
        self.assertFalse(dfa.recognize('bcbc'))
        self.assertFalse(dfa.recognize('acb'))
        self.assertTrue(dfa.recognize('ab'))

if __name__ == '__main__':
    unittest.main()