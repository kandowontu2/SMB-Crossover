"""Retain FU's short-lookahead negative and test a controller probe that reaches the real pipe."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
parent = R / 'tools/audit/continue_easy49_bass_pipes_fu.py'
binding = V / 'root49-el-bass-pipes-fu/binding.json'
assert sha(parent) == json.loads(binding.read_text())['script_sha256']
negative = R / 'build/roster-through-2-2/root49fu-bass-live-9-v0-mmc3/manifest.json'
assert json.loads(negative.read_text())['result']['frames'] == 27184
source = parent.read_text().replace('root49-el-bass-pipes-fu', 'root49-el-bass-pipes-fv')
source = source.replace('root49fu-bass-live', 'root49fv-bass-live')
assert source.count('c.x+32') == 2
source = source.replace('c.x+32', 'c.x+64').replace('A32px actual pipe lookahead', 'A64px actual pipe lookahead')
source = source.replace('local age,offAge=-1,0', '''local age,offAge,regionCalls=-1,0,0
local log=assert(io.open(ROSTER_CONFIG.out..'pipe-controller.csv','w'))
log:write('poll,x,y,age,tile16,tile32,tile48,tile64\\n')''')
anchor = '  local function pipe(t)return t==0x10 or t==0x11 or t==0x14 or t==0x15 end'
assert source.count(anchor) == 1
source = source.replace(anchor, '''  regionCalls=regionCalls+1
  assert(regionCalls<1200,'Bounded ordinary pipe controller must progress')
  if regionCalls==1 or regionCalls%100==0 then
   log:write(table.concat({c.poll,c.x,c.y,age,c.block(c.x+16,c.y+24),c.block(c.x+32,c.y+24),c.block(c.x+48,c.y+24),c.block(c.x+64,c.y+24)},',')..'\\n');log:flush()
  end
''' + anchor)
driver = V / 'root49-el-bass-pipes-fv-driver.py'
assert not driver.exists()
driver.write_text(source)
provenance = dict(script_sha256=sha(__file__), parent_script_sha256=sha(parent),
    parent_binding_sha256=sha(binding), parent_negative_manifest_sha256=sha(negative),
    generated_driver_sha256=sha(driver), source_runtime_changes=False,
    rationale='At1798,32px does not reach the visible pipe beginning1840. Probe64px and retain observed tile values; do not alter the game.')
(V / 'root49-el-bass-pipes-fv-preparation.json').write_text(json.dumps(provenance, indent=2) + '\n')
raise SystemExit(subprocess.run([sys.executable, str(driver)], cwd=R).returncode)
