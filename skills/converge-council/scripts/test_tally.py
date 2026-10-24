import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('tally', Path(__file__).parent / 'tally.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TallyTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            'candidates': ['A', 'B', 'C'],
            'reviewers': [
                {'id': 'r1', 'family': 'openai', 'context': 'fresh'},
                {'id': 'r2', 'family': 'anthropic', 'context': 'fresh'}],
            'ballots': [
                {'reviewer': 'r1', 'ranking': ['A', 'B', 'C']},
                {'reviewer': 'r2', 'ranking': ['C', 'B', 'A']}],
        }

    def test_reverse_preferences_preserve_three_way_tie(self):
        r = module.tally(self.data)
        self.assertEqual(r['scores'], {'A': .5, 'B': .5, 'C': .5})
        self.assertEqual(r['preference_leaders'], ['A', 'B', 'C'])
        self.assertEqual(r['coverage'], 'cross_family')

    def test_duplicating_a_family_does_not_increase_its_weight(self):
        for i in range(3, 7):
            self.data['reviewers'].append({'id': f'r{i}', 'family': 'openai', 'context': 'fresh'})
            self.data['ballots'].append({'reviewer': f'r{i}', 'ranking': ['A', 'B', 'C']})
        self.assertEqual(module.tally(self.data)['scores'], {'A': .5, 'B': .5, 'C': .5})

    def test_duplicate_rank_omitted_rank_unknown_rank_and_wrong_types_rejected(self):
        for rank in (['A', 'A', 'C'], ['A', 'B'], ['A', 'B', 'D'], None, 'ABC', ['A', [], 'C']):
            with self.subTest(rank=rank):
                d = copy.deepcopy(self.data)
                d['ballots'][0]['ranking'] = rank
                r = module.tally(d)
                self.assertEqual(len(r['valid_ballots']), 1)
                self.assertEqual(r['coverage'], 'insufficient_reviewers')
                self.assertEqual(len(r['rejected_ballots']), 1)

    def test_duplicate_reviewer_rejects_both_ballots(self):
        self.data['ballots'].append(copy.deepcopy(self.data['ballots'][0]))
        r = module.tally(self.data)
        self.assertEqual(len(r['valid_ballots']), 1)
        self.assertEqual([x['reason'] for x in r['rejected_ballots']], ['duplicate_reviewer'] * 2)

    def test_reused_author_ballot_is_excluded(self):
        self.data['reviewers'][0]['context'] = 'reused-author'
        r = module.tally(self.data)
        self.assertEqual(r['rejected_ballots'][0]['reason'], 'reused_author_context')

    def test_no_ballots_have_no_leader_or_scores(self):
        self.data['ballots'] = []
        r = module.tally(self.data)
        self.assertEqual(r['preference_leaders'], [])
        self.assertEqual(r['scores'], {})
        self.assertEqual(r['missing_reviewers'], ['r1', 'r2'])

    def test_unknown_reviewer_and_nonobject_rejected(self):
        self.data['ballots'] += [None, {'reviewer': 'intruder', 'ranking': ['A', 'B', 'C']}]
        self.assertEqual(len(module.tally(self.data)['rejected_ballots']), 2)

    def test_same_family_is_labeled(self):
        self.data['reviewers'][1]['family'] = 'openai'
        self.assertEqual(module.tally(self.data)['coverage'], 'single_family')

    def test_duplicate_roster_and_candidates_fail_closed(self):
        d = copy.deepcopy(self.data)
        d['reviewers'].append(d['reviewers'][0])
        with self.assertRaises(ValueError):
            module.tally(d)
        self.data['candidates'] = ['A', 'A']
        with self.assertRaises(ValueError):
            module.tally(self.data)

    def test_real_winner_and_two_candidate_normalization(self):
        self.data['candidates'] = ['A', 'B']
        for b in self.data['ballots']:
            b['ranking'] = ['B', 'A']
        r = module.tally(self.data)
        self.assertEqual(r['scores'], {'A': 0, 'B': 1})
        self.assertEqual(r['preference_leaders'], ['B'])
        self.assertFalse(r['tie'])


if __name__ == '__main__':
    unittest.main()
