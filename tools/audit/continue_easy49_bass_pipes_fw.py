"""Correct FV's logging-only Lua syntax failure, retaining both earlier negatives."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
parent = V / 'root49-el-bass-pipes-fv-driver.py'
failure = R / 'build/roster-through-2-2/root49fv-bass-live-9-v0-mmc3/manifest.json'
assert json.loads(failure.read_text()).get('result') is None
source = parent.read_text().replace('root49-el-bass-pipes-fv', 'root49-el-bass-pipes-fw')
source = source.replace('root49fv-bass-live', 'root49fw-bass-live')
header = "log:write('poll,x,y,age,tile16,tile32,tile48,tile64\\n')"
row = "},',')..'\\n');log:flush()"
assert source.count(header) == 1 and source.count(row) == 1
source = source.replace(header, "log:write('poll,x,y,age,tile16,tile32,tile48,tile64'..string.char(10))")
source = source.replace(row, "},',')..string.char(10));log:flush()")
driver = V / 'root49-el-bass-pipes-fw-driver.py'
assert not driver.exists()
driver.write_text(source)
provenance = dict(script_sha256=sha(__file__), parent_driver_sha256=sha(parent),
    retained_instrumentation_negative_manifest_sha256=sha(failure), driver_sha256=sha(driver),
    correction='Use string.char(10) for Lua log newlines; same controller and original FS19820 prefix.',
    runtime_changes=False, root_Bass_phase_ceiling_bytes=400_000_000)
(V / 'root49-el-bass-pipes-fw-preparation.json').write_text(json.dumps(provenance, indent=2) + '\n')
raise SystemExit(subprocess.run([sys.executable, str(driver)], cwd=R).returncode)
