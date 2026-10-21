"""Migrate only actual-entry qualification after preserving the frozen negative."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'build/verification/samus-injury-v38-fixture-migration'
OUT.mkdir(exist_ok=False)
raw = ROOT/'build/verification/summary-roster-audit-v38-provisional-e.json'
r = json.loads(raw.read_text())
assert r['result'] == 'failed' and len(r['cases']) == 760
assert r['failures'] == ['samus-injury-202 failed for smb-crossover-mmc3']
assert not r['changed_fixtures'] and r['fixture_hashes_before'] == r['fixture_hashes_after']
controls = ROOT/'build/verification/samus-injury-v38-qualified-c/manifest.json'
c = json.loads(controls.read_text())
assert len(c['runs']) == 4 and all(x['exit'] == 0 for x in c['runs'])
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = ROOT/'tests/samus-injury-202.lua'
before = sha(p)
assert before == c['original_fixture_sha256'] == r['fixture_hashes_before']['tests/samus-injury-202.lua']
shutil.copyfile(p, OUT/'original-fixture.lua')
shutil.copyfile(raw, OUT/'original-summary.json')
shutil.copyfile(ROOT/'build/verification/smb-crossover-mmc3-samus-injury-202.log', OUT/'original-negative.log')
shutil.copyfile(ROOT/'build/verification/roster-audit-v38e-full.log', OUT/'original-full.log')
text = p.read_text()
anchor = 'local injected=0\n'
assert text.count(anchor) == 1
tracking = '''-- Audio can execute this same CPU address while foreground CurrentBank
-- remains10. Accept only the real Samus bank outside NMI/IRQ; numeric recoil,
-- recovery, protection and one-real-injury-per-arena oracles are unchanged.
local injuryBank,injurySelect,injuryDepth=nil,nil,0
if ROM_NAME:find('mmc5')then
 emu.addMemoryCallback(function(_,v)injuryBank=v%128 end,emu.callbackType.write,0x5115)
else
 emu.addMemoryCallback(function(_,v)injurySelect=v%8 end,emu.callbackType.write,0x8000)
 emu.addMemoryCallback(function(_,v)if injurySelect==7 then injuryBank=v%128 end end,emu.callbackType.write,0x8001)
end
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()injuryDepth=injuryDepth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()injuryDepth=injuryDepth-1 end,emu.callbackType.exec,pc)end
'''
text = text.replace(anchor, anchor+tracking, 1)
old = "r('CurrentBank')%128~=10"
assert text.count(old) == 5
text = text.replace(old, old+' or injuryBank~=10 or injuryDepth~=0')
p.write_text(text)
shutil.copyfile(p, OUT/'qualified-fixture.lua')
report = {'result': 'running', 'before_sha256': before, 'after_sha256': sha(p),
          'runtime_roms_unchanged': True, 'original_frozen_result': '760 pass plus one MMC3 observer failure; not a green full run',
          'passive_proof': 'build/verification/samus-injury-v38-passive-a',
          'failure_context': {'frame': 2483, 'arena': 22, 'name': 'water-surface', 'physical_bank': 15,
                              'interrupt_depth': 1, 'foreground_CurrentBank': 10, 'pc': 'BA6B',
                              'opcode': '85 (unrelated audio); actual Samus entry opcode A9'},
          'outside_controls': str(controls.relative_to(ROOT)),
          'retained_oracles': ['32 actual injury arenas', '448 numeric recoil integrations', '250ms lock and late control masks',
                              '1250ms post-recoil protection', '25ms flicker phase', 'Actual cue and live unrelated enemy',
                              'Exactly one actual injury per arena and bounded progress'],
          'fixture_hashes_before': {'tests/samus-injury-202.lua': sha(p), 'tools/run_mesen.py': sha(ROOT/'tools/run_mesen.py')}, 'cases': []}
for mapper in ('mmc3', 'mmc5'):
    rom = ROOT/f'build/checkpoints/roster-audit-v38-provisional-e/smb-crossover-{mapper}.nes'
    log = OUT/f'{mapper}.log'
    with log.open('w') as stream:
        result = subprocess.run([sys.executable, 'tools/run_mesen.py', str(p), str(rom), '--timeout', '90'],
                                cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    report['cases'].append({'rom': f'smb-crossover-{mapper}', 'test': 'samus-injury-202', 'exit': result.returncode,
                           'result': 'passed' if result.returncode == 0 else 'failed', 'rom_sha256': sha(rom),
                           'log': str(log.relative_to(ROOT)), 'log_sha256': sha(log)})
    print(mapper, result.returncode, flush=True)
report['fixture_hashes_after'] = {n: sha(ROOT/n) for n in report['fixture_hashes_before']}
assert report['fixture_hashes_before'] == report['fixture_hashes_after']
report['result'] = 'passed' if all(x['exit'] == 0 for x in report['cases']) else 'failed'
(OUT/'summary.json').write_text(json.dumps(report, indent=2)+'\n')
assert report['result'] == 'passed'
