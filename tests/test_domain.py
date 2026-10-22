import unittest

from name_sorter.domain import Name, sort_names


class NameTests(unittest.TestCase):
    def test_parses_one_to_three_given_names(self):
        for text, given in [('Janet Parsons', ('Janet',)),
                            ('Adonis Julius Archer', ('Adonis', 'Julius')),
                            ('Hunter Uriah Mathew Clarke', ('Hunter', 'Uriah', 'Mathew'))]:
            with self.subTest(text=text):
                name = Name.parse(text)
                self.assertEqual(name.given_names, given)
                self.assertEqual(str(name), text)

    def test_normalizes_whitespace_and_preserves_spelling(self):
        self.assertEqual(str(Name.parse("  Anne-Marie\tO'Neill  ")), "Anne-Marie O'Neill")

    def test_rejects_invalid_number_of_name_parts(self):
        for text in ['', 'Smith', 'One Two Three Four Smith']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                Name.parse(text)

    def test_preserves_unicode(self):
        self.assertEqual(str(Name.parse('Élodie Müller')), 'Élodie Müller')


class SortingTests(unittest.TestCase):
    def test_sorts_by_surname_then_all_given_names(self):
        original = [Name.parse(n) for n in [
            'Amy Beth Smith', 'Amy Anne Zoe Smith', 'Zoe Adams',
            'Amy Smith', 'Adam Smith', 'Amy Anne Bea Smith']]
        snapshot = original.copy()
        self.assertEqual([str(n) for n in sort_names(original)], [
            'Zoe Adams', 'Adam Smith', 'Amy Smith', 'Amy Anne Bea Smith',
            'Amy Anne Zoe Smith', 'Amy Beth Smith'])
        self.assertEqual(original, snapshot)

    def test_keeps_duplicates(self):
        name = Name.parse('Amy Smith')
        self.assertEqual(sort_names([name, name]), [name, name])

    def test_empty_input(self):
        self.assertEqual(sort_names([]), [])

    def test_case_sensitive_order_is_deterministic(self):
        names = [Name.parse(n) for n in ['amy Smith', 'Amy Smith', 'Zoe Adams']]
        self.assertEqual([str(n) for n in sort_names(names)],
                         ['Zoe Adams', 'Amy Smith', 'amy Smith'])
