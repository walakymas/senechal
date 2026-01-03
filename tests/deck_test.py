from feast import Deck
import unittest

class DeckTest(unittest.TestCase):
    def init_test(self):
        d = Deck()
        print(f'{d}')

if __name__ == '__main__':
    unittest.main()
