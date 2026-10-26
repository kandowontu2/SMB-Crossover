"""Prepare, never launch, one 450-frame physical menu/first-active preflight."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re
import sys

from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from observe_chip_committed_write import lua

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, v):
    p.write_text(json.dumps(v, indent=2) + '\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--expected-ROM-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert sha(a.candidate / 'candidate.nes') == a.expected_ROM_sha256
    manifest = json.loads((a.candidate / 'source-manifest.json').read_text(encoding='utf-8'))
    for rel, expected in manifest.items():
        assert sha(a.candidate / 'source' / rel) == expected, rel
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    b = scoped_load(a.candidate / 'candidate.nes')
    original = D / 'mm-proto-postdma-native-ready-v3/native/megaman-easy-direct/inputs.csv'
    with original.open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    fixed = {}
    for row in rows:
        n, value = int(row['frame']), int(row['mask'])
        if n <= 450:
            assert n not in fixed or fixed[n] == value
            fixed[n] = value
    assert len(fixed) == 450 and set(fixed) == set(range(1, 451))
    (a.output / 'prefix.csv').write_text('frame,mask\n' + ''.join(f'{n},{fixed[n]}\n' for n in sorted(fixed)), encoding='utf-8')
    names = ['DisableScreenFlag', 'CrossoverMenuState', 'OperMode', 'OperMode_Task',
             'GameEngineSubroutine', 'SelectedCharacter', 'Sprite0HitDetectFlag',
             'ReloadCHRBank', 'X5WideChrActive', 'CurrentBank', 'CurrentBankC',
             'NmiR0', 'NmiR1', 'ProtoVariant', 'CrossoverBehaviorVersion']
    hooks = {}
    for alias, name in [('NmiEntry', 'NonMaskableInterrupt'), ('NmiReturn', 'NonMaskableInterrupt'),
                        ('IrqEntry', 'IrqScrollSplit'), ('UpdateScreen', 'UpdateScreen')]:
        pc, off = address(b, name), location(b, name)
        if alias == 'NmiReturn':
            delta = int(b['syms'][name]['size'], 0) - 1
            pc += delta
            off += delta
        hooks[alias] = dict(pc=pc, bank=(off - 16) // 8192, bytes=list(b['raw'][off:off + (1 if alias == 'NmiReturn' else 3)]))
    assert hooks['NmiReturn']['bytes'] == [0x40]
    pc, off = address(b, 'OAMandReadJoypad'), location(b, 'OAMandReadJoypad')
    assert pc == 0xe000 and b['raw'][off:off+13] == bytes.fromhex('a9028d1440ad7a078d0120a201')
    hooks['DmaBefore'] = dict(pc=pc+5, bank=127, bytes=list(b['raw'][off+5:off+13]))
    hooks['DmaComplete'] = dict(pc=pc+8, bank=127, bytes=[0x8d, 1, 0x20])
    cfg = dict(out=a.output.resolve().as_posix()+'/', limit=450, ROM_sha256=a.expected_ROM_sha256,
               prefix=(a.output/'prefix.csv').resolve().as_posix(), hooks=hooks,
               ram={n:address(b,n) for n in names}, smc=[address(b,n)+1 for n in
               ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
    module = ROOT/'tools/audit/presentation_timing_preflight_v1.lua'
    text = module.read_text(encoding='utf-8')
    assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(', text)
    sys.path.insert(0, str(D/'final-tmnt-items-v1/lua-parser-deps-v1'))
    from luaparser import ast
    ast.parse(text)
    sys.path.insert(0, str(D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'))
    from lupa import LuaRuntime
    pure=text.split('-- PURE_ENABLE_DEADLINE_BEGIN\n',1)[1].split('-- PURE_ENABLE_DEADLINE_END',1)[0]
    runtime=LuaRuntime();runtime.execute(pure);fn=runtime.globals().PRESENTATION_SAFE_ENABLE
    cases=[(241,0,True),(260,340,True),(-1,0,True),(-1,274,True),(-1,275,False),
           (-1,320,False),(0,115,False),(2,282,False),(4,65,False),(240,340,False)]
    for line,dot,expected in cases:
        assert fn(line,dot) is expected
    put(a.output/'deadline-source-controls.json',dict(passed=True,source_only=True,native_run=False,cases=cases,
        limits='Finite pure deadline predicate controls and full Lua parse; not a complete callback mock or native proof.'))
    put(a.output/'config.json',cfg)
    script=a.output/'run.lua'
    script.write_text('PRESENTATION_PREFLIGHT='+lua(cfg)+'\ndofile('+lua(module.as_posix())+')\n',encoding='utf-8')
    ready0=D/'mm-proto-postdma-native-ready-v3/readiness.json'
    env=json.loads(ready0.read_text(encoding='utf-8'))['environment']
    for n in ['emulator','core','worker_settings','user_settings']:
        assert sha(env[n])==env[n+'_sha256'],n
    cmd=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),
         '--emulator',env['emulator'],str(script),str(a.candidate/'candidate.nes'),'--timeout','180']
    cmd+=['--option='+v for v in env['actual_overrides']]
    deps={Path(__file__),module,ROOT/'tools/audit/check_tmnt_render_oa.py',
          ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',ROOT/'tools/audit/observe_chip_committed_write.py',
          ROOT/'tools/audit/run_mesen_isolated.py',ROOT/'tools/run_mesen.py',original,ready0,
          a.candidate/'source-manifest.json',a.candidate/'proof.json'}
    deps|={a.candidate/('candidate'+s) for s in ['.nes','.dbg','.lbl','.map']}
    deps|={a.candidate/'source'/rel for rel in manifest}
    deps|={Path(env[n]) for n in ['emulator','core','worker_settings','user_settings']}
    deps|={f for f in a.output.iterdir() if f.is_file()}
    ready=dict(passed=True,native_run=False,native_grant=False,ROM_sha256=a.expected_ROM_sha256,
               limit_actual_PPU_frames=450,maximum_launches=1,maximum_workers=1,command=cmd,
               environment=env,bindings={str(p.resolve()):sha(p) for p in sorted(deps)},
               limits='Prepared only. A fresh ROOT grant must also bind passing same-ROM source CPU/IRQ and menu caller controls before launch. Preserves actual diagnostic failures; no retagged old native coverage.')
    put(a.output/'readiness.json',ready)
    print(json.dumps(dict(prepared=True,bindings=len(ready['bindings']),readiness_sha256=sha(a.output/'readiness.json'))))


if __name__=='__main__':
    main()
