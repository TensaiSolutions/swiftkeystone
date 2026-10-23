import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from keystone_audit import audit, openstep


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.app = Path(self.temp.name)
        self.project = self.app / 'Example.xcodeproj'
        self.project.mkdir()
        self.pbx = self.project / 'project.pbxproj'
        self.pbx.write_text('''// !$*UTF8*$!
        { objects = {
            ROOT = { isa = PBXProject; targets = (APP, TESTS,); };
            APP = { isa = PBXNativeTarget; name = Example; productType = "com.apple.product-type.application"; };
            TESTS = { isa = PBXNativeTarget; name = "Example Tests"; productType = "com.apple.product-type.bundle.unit-test"; };
        }; rootObject = ROOT; }''')
        self.scheme = self.project / 'xcshareddata/xcschemes/Example.xcscheme'
        self.scheme.parent.mkdir(parents=True)
        self.scheme.write_text('''<Scheme><TestAction><Testables><TestableReference skipped="NO">
          <BuildableReference BlueprintIdentifier="TESTS" BlueprintName="Example Tests" ReferencedContainer="container:Example.xcodeproj"/>
          </TestableReference></Testables></TestAction></Scheme>''')
        self.profile = {'project': 'Example.xcodeproj', 'scheme': 'Example', 'checks': ['build', 'test']}
        self.fp = patch('keystone_audit.source_fingerprint', return_value={'sha256': 'a' * 64})
        self.fp.start();self.addCleanup(self.fp.stop)
        self.git = patch('keystone_audit.git', return_value=None)
        self.git.start();self.addCleanup(self.git.stop)

    def run_audit(self):
        return audit(self.app, self.profile)

    def test_resolved_target_is_reported_without_running_xcode(self):
        with patch('subprocess.run', side_effect=AssertionError('No native commands allowed')):
            result = self.run_audit()
        self.assertEqual(result['status'], 'inspected')
        self.assertEqual(len(result['effective_tests']), 1)
        self.assertTrue(result['effective_tests'][0]['exists'])
        self.assertIn('Native compilation and test execution', result['not_verified'])

    def test_orphaned_disabled_scheme_reference_and_no_effective_tests_are_detected(self):
        self.scheme.write_text(self.scheme.read_text().replace('TESTS', 'MISSING').replace('skipped="NO"', 'skipped="YES"'))
        result = self.run_audit()
        codes = {f['code'] for f in result['findings']}
        self.assertIn('orphaned_test_reference', codes)
        self.assertIn('disabled_test_reference', codes)
        self.assertIn('no_effective_test_targets', codes)
        self.assertEqual(result['status'], 'findings')

    def test_default_plan_takes_precedence_over_enabled_legacy_scheme_testables(self):
        self.scheme.write_text(self.scheme.read_text().replace('</TestAction>',
            '<TestPlans><TestPlanReference reference="container:Example.xctestplan" default="YES"/></TestPlans></TestAction>'))
        plan = self.app / 'Example.xctestplan'
        plan.write_text(json.dumps({'testTargets': []}))
        result = self.run_audit()
        self.assertEqual(result['effective_tests'], [])
        self.assertIn('no_effective_test_targets', {f['code'] for f in result['findings']})
        plan.write_text(json.dumps({'testTargets': [{'target': {'identifier': 'TESTS', 'name': 'Example Tests',
            'containerPath': 'container:Example.xcodeproj'}, 'skippedTests': ['ExampleTests/testOne']}]}))
        result = self.run_audit()
        self.assertEqual(result['effective_tests'][0]['origin'], 'default_plan')
        self.assertIn('test_selection_filter', {f['code'] for f in result['findings']})

    def test_workspace_and_user_local_scheme_are_distinguished(self):
        workspace = self.app / 'Example.xcworkspace'
        workspace.mkdir()
        (workspace / 'contents.xcworkspacedata').write_text('<Workspace><FileRef location="group:Example.xcodeproj"/></Workspace>')
        local = self.project / 'xcuserdata/user.xcuserdatad/xcschemes/Example.xcscheme'
        local.parent.mkdir(parents=True);self.scheme.rename(local)
        self.profile['project'] = 'Example.xcworkspace'
        result = self.run_audit()
        self.assertFalse(result['scheme']['shared'])
        self.assertIn('scheme_not_shared', {f['code'] for f in result['findings']})
        self.assertTrue(result['effective_tests'][0]['exists'])

    def test_external_plan_and_malformed_project_produce_findings_not_health_claims(self):
        self.scheme.write_text(self.scheme.read_text().replace('container:Example.xcodeproj', 'container:../External.xcodeproj'))
        result = self.run_audit()
        self.assertEqual(result['status'], 'findings')
        self.pbx.write_text('not a project')
        self.assertIn('unreadable_project', {f['code'] for f in self.run_audit()['findings']})

    def test_parser_handles_comments_quoted_delimiters_and_rejects_truncated_strings(self):
        self.assertEqual(openstep('{ /* comment */ value = "("; values = ("}", token,); }'),
                         {'value': '(', 'values': ['}', 'token']})
        for text in ('{ value = "unclosed; }', '{ key = one; key = two; }', '{ value = (one; }'):
            with self.assertRaises(ValueError):
                openstep(text)

    def test_reference_matches_content_and_profile_even_when_commit_differs(self):
        profile = self.app / '.ios-forge/app.json';profile.parent.mkdir();profile.write_text('{}')
        import hashlib
        report = {'status': 'passed', 'commit': 'b' * 40, 'profile_sha256': hashlib.sha256(profile.read_bytes()).hexdigest(),
                  'source_fingerprint': {'sha256': 'a' * 64},
                  'checks': [{'name': 'build', 'status': 'passed', 'exit_code': 0}]}
        reference = self.app / 'old.json';reference.write_text(json.dumps(report))
        result = audit(self.app, self.profile, reference)
        self.assertTrue(result['reference_evidence']['source_and_profile_match'])
        self.assertFalse(result['reference_evidence']['same_commit'])
        report['source_fingerprint']['sha256'] = 'c' * 64;reference.write_text(json.dumps(report))
        self.assertIn('stale_or_unmatched_evidence', {f['code'] for f in audit(self.app, self.profile, reference)['findings']})
