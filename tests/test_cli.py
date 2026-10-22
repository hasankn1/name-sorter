from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.cwd = Path(self.temporary.name)
        self.input = self.cwd / 'input' / 'names.txt'
        self.input.parent.mkdir()
        self.output = self.cwd / 'sorted-names-list.txt'

    def run_sorter(self, *arguments):
        return subprocess.run([sys.executable, str(ROOT / 'name-sorter'), *map(str, arguments)],
                              cwd=self.cwd, capture_output=True, text=True)

    def test_assessment_example_prints_and_overwrites_in_working_directory(self):
        self.input.write_text((ROOT / 'unsorted-names-list.txt').read_text(), encoding='utf-8')
        self.output.write_text('stale content that must disappear', encoding='utf-8')
        result = self.run_sorter(self.input)
        expected = '\n'.join([
            'Marin Alvarez', 'Adonis Julius Archer', 'Beau Tristan Bentley',
            'Hunter Uriah Mathew Clarke', 'Leo Gardner', 'Vaugh Lewis',
            'London Lindsey', 'Mikayla Lopez', 'Janet Parsons',
            'Frankie Conner Ritter', 'Shelby Nathan Yoder']) + '\n'
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, expected)
        self.assertEqual(result.stderr, '')
        self.assertEqual(self.output.read_text(encoding='utf-8'), expected)
        self.assertFalse((self.input.parent / self.output.name).exists())

    def test_thousand_names(self):
        self.input.write_text(''.join(f'Person Surname{i:04d}\n' for i in reversed(range(1000))))
        result = self.run_sorter(self.input)
        expected = ''.join(f'Person Surname{i:04d}\n' for i in range(1000))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, expected)
        self.assertEqual(self.output.read_text(), expected)

    def test_blank_lines_and_empty_file(self):
        for content, expected in [('', ''), ('\nAmy Smith\n \n', 'Amy Smith\n')]:
            with self.subTest(content=content):
                self.input.write_text(content)
                result = self.run_sorter(self.input)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, expected)
                self.assertEqual(self.output.read_text(), expected)

    def test_invalid_line_preserves_existing_output(self):
        self.input.write_text('Amy Smith\n\nInvalid\n')
        self.output.write_text('keep me')
        result = self.run_sorter(self.input)
        self.assertEqual(result.returncode, 1)
        self.assertIn('line 3', result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertEqual(self.output.read_text(), 'keep me')

    def test_missing_input(self):
        result = self.run_sorter(self.input)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertFalse(self.output.exists())

    def test_invalid_utf8(self):
        self.input.write_bytes(b'\xff\xfe')
        result = self.run_sorter(self.input)
        self.assertEqual(result.returncode, 1)
        self.assertIn('error:', result.stderr)
        self.assertFalse(self.output.exists())

    def test_output_write_failure(self):
        self.input.write_text('Amy Smith\n')
        self.output.mkdir()
        result = self.run_sorter(self.input)
        self.assertEqual(result.returncode, 1)
        self.assertIn('error:', result.stderr)
        self.assertEqual(result.stdout, '')

    def test_requires_exactly_one_argument(self):
        for arguments in [(), ('one', 'two')]:
            with self.subTest(arguments=arguments):
                result = self.run_sorter(*arguments)
                self.assertEqual(result.returncode, 2)
                self.assertIn('usage:', result.stderr)

    def test_utf8_bom_and_windows_line_endings(self):
        self.input.write_bytes('\ufeffÉlodie Müller\r\nAmy Adams\r\n'.encode('utf-8'))
        result = self.run_sorter(self.input)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'Amy Adams\nÉlodie Müller\n')
