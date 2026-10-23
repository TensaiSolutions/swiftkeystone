import json
from pathlib import Path
import tempfile
import unittest

from keystone_common import ForgeError, inventory
from keystone_updates import stage_update


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.app = self.root / 'app'
        self.old = self.root / 'old'
        self.new = self.root / 'new'
        self.installed = self.app / '.agents/skills/example'
        self.names = ('example',)
        for root in (self.old / 'skills/example', self.new / 'skills/example', self.installed):
            root.mkdir(parents=True)
            (root / 'SKILL.md').write_text('original')
            (root / 'unchanged.md').write_text('same')
        self.profile = self.app / '.ios-forge/app.json'
        self.profile.parent.mkdir()
        self.profile.write_text('user profile')
        self.out = self.root / 'private'

    def stage(self, **kwargs):
        return stage_update(self.app, self.old, self.new, self.names, kwargs.get('output', self.out), kwargs.get('dry_run', False))

    def test_upgrade_stages_candidate_and_exact_backup_without_changing_app(self):
        (self.new / 'skills/example/SKILL.md').write_text('new instructions')
        before = inventory(self.app)
        dry = self.stage(dry_run=True)
        self.assertFalse(self.out.exists())
        self.assertEqual(dry['conflicts'], 0)
        result = self.stage()
        stage = Path(result['stage'])
        self.assertEqual((stage / 'candidate/example/SKILL.md').read_text(), 'new instructions')
        self.assertEqual((stage / 'backup/example/SKILL.md').read_text(), 'original')
        self.assertEqual(inventory(self.app), before)
        self.assertEqual(self.profile.read_text(), 'user profile')
        self.assertEqual(stage.stat().st_mode & 0o777, 0o700)

    def test_three_way_merge_preserves_local_edits_extras_and_deletions(self):
        (self.installed / 'unchanged.md').write_text('local customization')
        (self.installed / 'extra.txt').write_text('my extra')
        (self.old / 'skills/example/deleted.txt').write_text('old')
        (self.new / 'skills/example/deleted.txt').write_text('old')
        (self.new / 'skills/example/SKILL.md').write_text('upstream update')
        result = self.stage()
        candidate = Path(result['stage']) / 'candidate/example'
        self.assertEqual((candidate / 'unchanged.md').read_text(), 'local customization')
        self.assertEqual((candidate / 'extra.txt').read_text(), 'my extra')
        self.assertFalse((candidate / 'deleted.txt').exists())
        self.assertEqual((candidate / 'SKILL.md').read_text(), 'upstream update')
        self.assertEqual(result['conflicts'], 0)

    def test_conflict_keeps_local_copy_and_exposes_incoming_for_review(self):
        (self.installed / 'SKILL.md').write_text('local')
        (self.new / 'skills/example/SKILL.md').write_text('new')
        before = inventory(self.app)
        result = self.stage()
        stage = Path(result['stage'])
        self.assertEqual(result['conflicts'], 1)
        self.assertEqual((stage / 'candidate/example/SKILL.md').read_text(), 'local')
        self.assertEqual((stage / 'incoming/example/SKILL.md').read_text(), 'new')
        self.assertEqual((stage / 'backup/example/SKILL.md').read_text(), 'local')
        self.assertEqual(inventory(self.app), before)

    def test_upstream_file_removal_is_staged_only_when_locally_unmodified(self):
        (self.old / 'skills/example/remove.md').write_text('old')
        (self.installed / 'remove.md').write_text('old')
        result = self.stage()
        stage = Path(result['stage'])
        self.assertFalse((stage / 'candidate/example/remove.md').exists())
        self.assertEqual((self.installed / 'remove.md').read_text(), 'old')

    def test_missing_entrypoint_is_not_reintroduced_over_a_local_deletion(self):
        (self.installed / 'SKILL.md').unlink()
        result = self.stage(dry_run=True)
        self.assertFalse(result['candidate_entrypoints_present'])
        self.assertFalse(self.out.exists())

    def test_linked_inputs_and_nested_outputs_are_refused_without_app_writes(self):
        for output in (self.app / 'out', self.old / 'out', self.new / 'out'):
            with self.assertRaises(ForgeError):
                self.stage(output=output)
        (self.installed / 'link').symlink_to(self.root / 'private-file')
        with self.assertRaises(ForgeError):
            self.stage()
        self.assertFalse(self.out.exists())

    def test_repeated_staging_never_replaces_a_previous_backup(self):
        first = self.stage()
        marker = Path(first['stage']) / 'review.txt'
        marker.write_text('keep')
        second = self.stage()
        self.assertNotEqual(first['stage'], second['stage'])
        self.assertEqual(marker.read_text(), 'keep')
        self.assertEqual(json.loads((Path(first['stage']) / 'manifest.json').read_text())['operation'], 'stage_only')

    def test_executable_permissions_are_preserved_and_mode_edits_are_local_changes(self):
        script = self.installed / 'run.py'
        script.write_text('print("local")')
        script.chmod(0o750)
        result = self.stage()
        stage = Path(result['stage'])
        self.assertEqual((stage / 'backup/example/run.py').stat().st_mode & 0o777, 0o750)
        self.assertEqual((stage / 'candidate/example/run.py').stat().st_mode & 0o777, 0o750)
        for root in (self.old / 'skills/example', self.new / 'skills/example'):
            (root / 'run.py').write_text('print("local")')
            (root / 'run.py').chmod(0o644)
        result = self.stage()
        decision = next(d for d in result['files'] if d['file'] == 'run.py')
        self.assertEqual(decision['action'], 'preserve_local')
