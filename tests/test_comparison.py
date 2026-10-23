import copy
import json
from pathlib import Path
import tempfile
import unittest

from keystone_common import ForgeError, private_output
from keystone_evidence import compare, read_report, summarize


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.report = {'forge_version': '0.2.0', 'status': 'passed', 'commit': 'a' * 40, 'dirty': False,
            'app': 'PRIVATE APP', 'source_fingerprint': {'sha256': 'b' * 64}, 'profile_sha256': 'c' * 64,
            'toolchain': {'xcode': 'Xcode Test'}, 'checks': [{'name': 'test', 'status': 'passed', 'exit_code': 0,
                'argv': ['xcodebuild', '-project', '/private/secret/App.xcodeproj', '-scheme', 'Scheme',
                         '-destination', 'platform=macOS,arch=arm64', 'test'],
                'diagnostic': '/Users/private sensitive token',
                'test_summary': {'totalTestCount': 3, 'passedTests': 3, 'failedTests': 0,
                    'skippedTests': 0, 'expectedFailures': 0, 'result': 'Passed',
                    'testFailures': [{'failureText': 'PRIVATE RECIPE', 'testName': '/private/device-id'}]}}]}

    def save(self, name, report):
        path = self.root / name
        path.write_text(json.dumps(report))
        return path

    def failure(self):
        bad = copy.deepcopy(self.report)
        bad['status'] = 'failed'
        bad['source_fingerprint']['sha256'] = 'd' * 64
        bad['profile_sha256'] = 'e' * 64
        bad['checks'][0].update(status='failed', exit_code=65)
        bad['checks'][0]['test_summary'].update(passedTests=2, failedTests=1, result='Failed')
        return bad

    def test_legacy_red_green_comparison_proves_input_restoration_and_does_not_execute_argv(self):
        before = self.save('before.json', self.report)
        failed = self.save('failed.json', self.failure())
        after = self.save('restored.json', self.report)
        result = compare(before, failed, after)
        self.assertTrue(result['regression_cycle_supported'])
        self.assertTrue(result['restoration_verified'])
        self.assertTrue(result['legacy_context_inferred'])
        self.assertTrue(result['profile_changed'])
        self.assertEqual(result['after_tests']['failedTests'], 1)

    def test_changed_destination_toolchain_and_missing_provenance_need_review(self):
        before = self.save('before.json', self.report)
        for change in ('destination', 'toolchain', 'provenance'):
            report = copy.deepcopy(self.report)
            if change == 'destination':
                report['checks'][0]['argv'][-2] = 'platform=iOS Simulator,id=other'
            elif change == 'toolchain':
                report['toolchain']['xcode'] = 'Other Xcode'
            else:
                del report['source_fingerprint']
            result = compare(before, self.save('after.json', report))
            self.assertEqual(result['status'], 'needs_review')

    def test_restore_requires_matching_profile_source_and_check_selection(self):
        before = self.save('before.json', self.report)
        failed = self.save('failed.json', self.failure())
        for key in ('source_fingerprint', 'profile_sha256'):
            restored = copy.deepcopy(self.report)
            restored[key] = {'sha256': 'f' * 64} if key == 'source_fingerprint' else 'f' * 64
            result = compare(before, failed, self.save('restore.json', restored))
            self.assertFalse(result['restoration_verified'])
            self.assertFalse(result['regression_cycle_supported'])

    def test_malformed_or_contradictory_reports_cannot_claim_success(self):
        variants = []
        for key, value in [('passedTests', True), ('passedTests', 9), ('passedTests', -1)]:
            r = copy.deepcopy(self.report)
            r['checks'][0]['test_summary'][key] = value
            variants.append(r)
        r = self.failure(); r['status'] = 'passed'; variants.append(r)
        r = copy.deepcopy(self.report);r['checks'][0]['exit_code'] = True;variants.append(r)
        r = copy.deepcopy(self.report);r['checks'][0]['test_summary'] = {'error': 'missing'};variants.append(r)
        r = copy.deepcopy(self.report);r['checks'] *= 2;variants.append(r)
        for r in variants:
            with self.assertRaises(ForgeError):
                read_report(self.save('bad.json', r))

    def test_summary_omits_untrusted_names_diagnostics_argv_and_identifiers(self):
        text, _ = summarize(self.save('report.json', self.report))
        self.assertIn('3 passed', text)
        for private in ('PRIVATE APP', 'PRIVATE RECIPE', '/Users/', '/private/', 'device-id', 'sensitive token', 'Scheme'):
            self.assertNotIn(private, text)

    def test_build_only_and_unreadable_failed_test_results_remain_explicit(self):
        r = copy.deepcopy(self.report)
        r['checks'] = [{'name': 'build', 'status': 'passed', 'exit_code': 0}]
        text, _ = summarize(self.save('build.json', r))
        self.assertIn('Build-only', text)
        r = self.failure();r['checks'][0]['test_summary'] = {'error': 'PRIVATE failure'}
        text, _ = summarize(self.save('failed.json', r))
        self.assertIn('No readable', text)
        self.assertNotIn('PRIVATE failure', text)

    def test_outputs_never_replace_existing_or_linked_files(self):
        path = self.root / 'report.md'
        private_output(path, 'first')
        with self.assertRaises(FileExistsError):
            private_output(path, 'second')
        self.assertEqual(path.read_text(), 'first')
        link = self.root / 'link.md';link.symlink_to(self.root / 'missing')
        with self.assertRaises(ForgeError):
            private_output(link, 'unsafe')
        with self.assertRaises(ForgeError):
            private_output(self.root / 'nested/file', 'unsafe', (self.root,))

    def test_explicit_configuration_cannot_contradict_recorded_commands(self):
        first = self.save('first.json', self.report)
        newer = copy.deepcopy(self.report)
        newer['configuration'] = {'project': 'App.xcodeproj', 'scheme': 'Scheme',
            'destination': 'platform=macOS,arch=arm64', 'checks': ['test']}
        self.assertEqual(compare(first, self.save('new.json', newer))['status'], 'comparable')
        newer['configuration']['destination'] = 'platform=iOS Simulator,id=other'
        self.assertEqual(compare(first, self.save('bad.json', newer))['status'], 'needs_review')
        newer = copy.deepcopy(self.report);del newer['profile_sha256']
        self.assertEqual(compare(first, self.save('bad.json', newer))['status'], 'needs_review')

    def test_duplicate_json_and_empty_error_markers_do_not_create_passing_evidence(self):
        duplicate = self.root / 'duplicate.json'
        duplicate.write_text('{"status":"failed","status":"passed","checks":[]}')
        with self.assertRaises(ForgeError):
            read_report(duplicate)
        report = copy.deepcopy(self.report)
        report['checks'][0]['test_summary']['error'] = ''
        with self.assertRaises(ForgeError):
            read_report(self.save('invalid.json', report))
