import unittest
from src.Common.Automaton import DFA, NFA
from src.Common.AutomatonOperations import automata_union, automata_concatenation, automata_closure
from src.Common.AutomatonUtils import nfa_to_dfa

class TestAutomata(unittest.TestCase):


    def setUp(self):
        self.a1 = NFA(states=3, finals=[2], transitions={(0, 'b'): [0], (0, 'a'): [1], (1, 'b'): [2]})
        self.a2 = NFA(states=2, finals=[1], transitions={(0, 'a'): [1]})

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

    def test_automata_union(self):
        result = automata_union(self.a1, self.a2)
        # Add your assertions here
        self.assertEqual(result.states, self.a1.states + self.a2.states + 2)

        print(result)

        self.assertTrue(result.recognize('a'))

    def test_automata_concatenation(self):
        result = automata_concatenation(self.a1, self.a2)
        # Add your assertions here
        self.assertEqual(result.states, self.a1.states + self.a2.states + 1)

    def test_automata_closure(self):
        result = automata_closure(self.a1)
        # Add your assertions here
        self.assertEqual(result.states, self.a1.states + 2)


if __name__ == '__main__':
    unittest.main()