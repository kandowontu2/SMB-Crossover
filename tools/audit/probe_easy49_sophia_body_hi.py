"""Preserve all physical RAM at Sophia's actual pre-injury firebar admission."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-gq-sophia-body-hi'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parent = V / 'root49-gq-sophia-firebar-hh'
    d = json.loads((parent / 'binding.json').read_text())
    assert sha(parent / 'policy.lua') == d['policy_sha256']
    text = (parent / 'policy.lua').read_text()
    anchor = ' local st=emu.getState();local stack,sc,bb,parts={},{},{},{}'
    assert text.count(anchor) == 1
    insert = '''
 if e=='ChgSDir'then
  local raw={}
  for a=0,0x7ff do raw[#raw+1]=string.char(emu.read(a,emu.memType.nesDebug))end
  for a=0x6000,0x7fff do raw[#raw+1]=string.char(emu.read(a,emu.memType.nesDebug))end
  local z=assert(io.open(ROSTER_CONFIG.out..'actual-firebar-body.bin','wb'));z:write(table.concat(raw));z:close()
 end
'''
    H.mkdir(exist_ok=False)
    policy = H / 'policy.lua';policy.write_text(text.replace(anchor, anchor + insert))
    command = list(d['command'])
    command[command.index('--policy') + 1] = str(policy)
    command[command.index('--tag') + 1] = 'root49hi-sophia-body'
    proof = R / 'build/roster-through-2-2/root49hg-sophia-live-11-v0-mmc3'
    assert sha(proof / 'inputs.csv') == d['input_sha256']
    assert sha(Path(command[command.index('--rom') + 1])) == d['ROM_sha256']
    record = dict(status='PREPARED_READ_ONLY_ACTUAL_SOPHIA_BODY_SNAPSHOT',
        script_sha256=sha(__file__), HH_binding_sha256=sha(parent / 'binding.json'),
        policy_sha256=sha(policy), normal_source_rectangle=d['normal_source_rectangle'],
        source_XML_sha256=d['source_XML_sha256'], input_sha256=d['input_sha256'],
        ROM_sha256=d['ROM_sha256'], command=command, emulated_writes=False, state_loads=False,
        snapshot='Unchanged2048internal+8192cartridgeRAM at actual guarded pre-ChgSDir. No decoded state grants or synthetic contacts.')
    (H / 'binding.json').write_text(json.dumps(record, indent=2) + '\n')
    rc = subprocess.run(command, cwd=R).returncode
    (H / 'host-result.json').write_text(json.dumps(dict(exit=rc), indent=2) + '\n')
    raise SystemExit(rc)


if __name__ == '__main__':
    main()
