import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from passions import group_passions, passion_category, passion_total


class PassionsTest(unittest.TestCase):

    def test_categories(self):
        expected = {
            'Loyalty (Lord)': 'Fidelitas',
            'Fealthy (Lord)': 'Fidelitas',
            'Homage (Liege)': 'Fidelitas',
            'Love (Family)': 'Fervor',
            'Love(Family)': 'Fervor',
            'Hate Saxons': 'Fervor',
            'Hate (Saxons)': 'Fervor',
            'Amor (Ygraine)': 'Adoratio',
            'Devotion (Deity)': 'Adoratio',
            'Honor': 'Other',
            'Hospitability': 'Civilitas',
            'Station': 'Civilitas',
            'Directed Trait: Generous (Family)': 'Other',
            'Heritage (Place)': 'Other',
            '': 'Other',
        }
        for name, category in expected.items():
            self.assertEqual(passion_category(name), category, name)

    def test_group_order_and_values(self):
        groups = group_passions({'Honor': 15, 'Love (Family)': '12', 'Loyalty (Lord)': 15, 'Hate (Picts)': 3})
        self.assertEqual(groups, [
            ('Other', [('Honor', 15)]),
            ('Fidelitas', [('Loyalty (Lord)', 15)]),
            ('Fervor', [('Hate (Picts)', 3), ('Love (Family)', 12)]),
        ])
        self.assertEqual(passion_total(groups[2][1]), 15)

    def test_empty(self):
        self.assertEqual(group_passions({}), [])


if __name__ == '__main__':
    unittest.main()
