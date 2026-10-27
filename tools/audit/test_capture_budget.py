"""Exercise real process termination/locking without launching an emulator."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import capture_budget as budget


class CaptureLimits(unittest.TestCase):
    def setUp(self):
        parent = budget.WORKSPACE/'build'
        parent.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='capture-limit-check-', dir=parent)
        self.root = Path(self.temp.name).resolve()
        assert self.root.is_relative_to(parent.resolve())
        self.addCleanup(self.temp.cleanup)
        self.archive = self.root/'archive'
        self.archive.mkdir()
        self.output = self.archive/'run'
        for name, value in [('WORKSPACE', self.root), ('ARCHIVE', self.archive),
                            ('LOCK', self.root/'capture.lock')]:
            setter = patch.object(budget, name, value)
            setter.start()
            self.addCleanup(setter.stop)

    def test_archive_cap_refuses_before_launch(self):
        with patch.object(budget, 'ARCHIVE_FILES', 1):
            (self.archive/'one').touch()
            (self.archive/'two').touch()
            with self.assertRaises(budget.CaptureBudgetExceeded):
                budget.run_capped([sys.executable, '-c', 'raise Exception("must not start")'],
                                  output=self.output, timeout=5)
        self.assertFalse(self.output.exists())

    def test_external_output_cannot_bypass_cap(self):
        with self.assertRaises(budget.CaptureBudgetExceeded):
            budget.preflight(self.root.parent/'elsewhere')

    def test_actual_process_stopped_on_growth(self):
        program = ('from pathlib import Path; import time,sys; '
                   'p=Path(sys.argv[1]); (p/"large").write_bytes(b"x"*2048); '
                   'time.sleep(3); (p/"should-not-exist").touch()')
        with patch.object(budget, 'PAYLOAD_BYTES', 1024):
            with self.assertRaises(budget.CaptureBudgetExceeded):
                budget.run_capped([sys.executable, '-c', program, str(self.output)],
                                  output=self.output, timeout=5)
        self.assertFalse((self.output/'should-not-exist').exists())
        receipt = json.loads((self.output/'capture-budget.json').read_text())
        self.assertTrue(receipt['violations'])
        self.assertTrue(receipt['owned_process_only'])

    def test_fast_exit_file_overflow_is_still_failure(self):
        program = ('from pathlib import Path; import sys; p=Path(sys.argv[1]); '
                   '[(p/str(i)).touch() for i in range(5)]')
        with patch.object(budget, 'PAYLOAD_FILES', 4):
            with self.assertRaises(budget.CaptureBudgetExceeded):
                budget.run_capped([sys.executable, '-c', program, str(self.output)],
                                  output=self.output, timeout=5)

    def test_second_process_refused_while_lease_is_held(self):
        module = str(Path(budget.__file__).parent)
        program = ('import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); '
                   'import capture_budget as c; c.LOCK=Path(sys.argv[2]); '
                   '\ntry:\n with c.capture_lease(): sys.exit(9)'
                   '\nexcept c.CaptureBudgetExceeded: sys.exit(0)')
        with budget.capture_lease():
            child = subprocess.run([sys.executable, '-B', '-c', program, module,
                                    str(budget.LOCK)], capture_output=True, timeout=5)
        self.assertEqual(child.returncode, 0, child.stderr.decode())
        with budget.capture_lease():
            pass  # Released leases can be used again; stale files are harmless.

    def test_success_writes_one_receipt(self):
        result = budget.run_capped([sys.executable, '-c', 'print("bounded")'],
                                   output=self.output, timeout=5)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), 'bounded')
        self.assertEqual(len(list(self.output.iterdir())), 1)


if __name__ == '__main__':
    unittest.main()
