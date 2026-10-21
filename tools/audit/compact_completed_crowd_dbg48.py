"""Losslessly archive root-owned completed v48 crowd DBG duplicates only."""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    'crowd47_compaction', ROOT/'tools/audit/compact_completed_crowd_dbg47.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Reuse the audited round-trip and protected-file procedure, with an explicit
# new allowlist. The canonical checkpoint remains available as uncompressed DBG.
source = (ROOT/'tools/audit/compact_completed_crowd_dbg47.py').read_text()
source = source.replace("'roster-audit-v46','roster-audit-v47-provisional-a'",
                        "'roster-audit-v48-provisional-a',")
source = source.replace('len(targets)==19', 'len(targets)==11')
source = source.replace("{r['path']for r in targets})==19", "{r['path']for r in targets})==11")
source = source.replace('Only19 root-owned', 'Only11 root-owned')
namespace = {'__name__': 'frozen_compaction_procedure', '__file__': str(
    ROOT/'tools/audit/compact_completed_crowd_dbg47.py')}
exec(compile(source, str(ROOT/'tools/audit/compact_completed_crowd_dbg47.py'), 'exec'), namespace)
namespace['NAMES'] = (
    'plain-walking-v48a-terrain-three-after-a',
    'plain-walking-v48a-terrain-other-after-a',
    'plain-walking-v48a-terrain-six-repeat-after-a',
)
namespace['OUT'] = ROOT/'build/verification/root-completed-crowd-dbg48-compaction-a'
if __name__ == '__main__':
    namespace['main']()
