"""Check configuration literal types in real Mesen Lua; no gameplay claim."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

from observe_chip_committed_write import lua
from audit_lua_config_literals import bare_python_literals

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

FIXTURE = r'''
local C=CONFIG_UNDER_TEST
assert(type(C.hard)=='boolean' and C.hard==true,'True survives as a Lua boolean')
assert(type(C.enabled)=='boolean' and C.enabled==false,'False survives as a Lua boolean')
assert(C.optional==nil,'None is a Lua nil')
assert((C.hard and 1 or 0)==1,'Mode predicate selects Hard')
assert((C.enabled and 1 or 0)==0,'False predicate stays false')
assert(C.nested.values[1]==false and C.nested.values[2]==true and C.nested.values[3]==nil and C.nested.values[4]==1,'Nested literal types survive')
assert(C.nested.values[5]=='True' and C.nested.values[6]=='False','String content stays literal')
local f=assert(io.open(OUTPUT..'runtime-proof.json','w'))
f:write('{"passed":true,"checks":7,"scope":"Real Lua configuration evaluation; no gameplay or mode coverage claim"}')
f:close()
emu.stop(0)
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['rom', 'emulator', 'output']:
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT), 'Evidence belongs outside the workspace'
    out.mkdir(parents=True, exist_ok=False)
    config = dict(hard=True, enabled=False, optional=None,
                  nested=dict(values=[False, True, None, 1, 'True', 'False']))
    rendered = 'CONFIG_UNDER_TEST='+lua(config)+'\n'+FIXTURE
    assert bare_python_literals(rendered) == []
    # Inventory must ignore comments, escaped quoted strings and Lua long strings.
    lexical = '-- True\n--[=[ False ]=]\n"None \\\" True"\n[==[False]==]\nTrue False None'
    assert [x['literal'] for x in bare_python_literals(lexical)] == ['True', 'False', 'None']
    script = out/'serializer-runtime.lua'
    script.write_text(rendered, encoding='utf-8')
    binding = dict(configuration=config, ROM_sha256=sha(a.rom),
                   emulator_sha256=sha(a.emulator), script_sha256=sha(script),
                   serializer_sha256=sha(ROOT/'tools/audit/observe_chip_committed_write.py'),
                   inventory_tool_sha256=sha(ROOT/'tools/audit/audit_lua_config_literals.py'),
                   regression_runner_sha256=sha(Path(__file__)))
    (out/'binding.json').write_text(json.dumps(binding, indent=2)+'\n', encoding='utf-8')
    command = [sys.executable, str(ROOT/'tools/audit/run_mesen_isolated.py'),
               '--output', str(out), '--emulator', str(a.emulator.resolve()),
               str(script), str(a.rom.resolve()), '--timeout', '30',
               '--option=--doNotSaveSettings', '--option=--nes.ramPowerOnState=AllZeros']
    with (out/'host.log').open('w', encoding='utf-8') as stream:
        result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    native = json.loads((out/'runtime-proof.json').read_text(encoding='utf-8')) if (out/'runtime-proof.json').exists() else {}
    proof = dict(binding, passed=result.returncode==0 and native.get('passed') is True,
                 emulator_exit=result.returncode, native=native,
                 configuration_lexical_checks_passed=True,
                 scope='Configuration literal regression only. No gameplay, RAM mode readback, character, or full-goal qualification.')
    (out/'proof.json').write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(proof))
    raise SystemExit(0 if proof['passed'] else 1)


if __name__ == '__main__':
    main()
