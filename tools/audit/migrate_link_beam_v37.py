"""Correct the bank-blind observer only after the frozen run has closed."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'build/verification/link-beam-v37-fixture-migration'
OUT.mkdir(exist_ok=False)
raw = ROOT/'build/verification/summary-roster-audit-v37-provisional-c.json'
j = json.loads(raw.read_text())
assert j['result'] == 'failed' and len(j['cases']) == 758
assert j['failures'] == ['link-beam-impact failed for smb-crossover-mmc3']
assert not j['changed_fixtures'] and j['fixture_hashes_before'] == j['fixture_hashes_after']
p = ROOT/'tests/link-beam-impact.lua'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = sha(p)
assert before == '4cb392b60c508cd8d302a5b2bf2e7c55344644d187abdecf5539bd0f9620e22b'
shutil.copyfile(p, OUT/'original-fixture.lua')
shutil.copyfile(raw, OUT/'original-summary.json')
shutil.copyfile(ROOT/'build/verification/smb-crossover-mmc3-link-beam-impact.log', OUT/'original-negative.log')
text = p.read_text()
anchor = 'local ready=false\n'
assert text.count(anchor) == 1
tracking = '''-- These CPU addresses also execute unrelated code in other PRG banks.
-- Manual audio switches do not update foreground CurrentBank; track hardware
-- selection and interrupt depth before accepting a real fragment/render call.
local beamBank,beamSelect,beamDepth=nil,nil,0
if ROM_NAME:find('mmc5')then
 emu.addMemoryCallback(function(_,v)beamBank=v%128 end,emu.callbackType.write,0x5115)
else
 emu.addMemoryCallback(function(_,v)beamSelect=v%8 end,emu.callbackType.write,0x8000)
 emu.addMemoryCallback(function(_,v)if beamSelect==7 then beamBank=v%128 end end,emu.callbackType.write,0x8001)
end
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()beamDepth=beamDepth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()beamDepth=beamDepth-1 end,emu.callbackType.exec,pc)end
'''
text = text.replace(anchor, anchor+tracking, 1)
text = text.replace('if not ready or frame<560 then return end', 'if not ready or frame<560 or beamBank~=4 or beamDepth~=0 then return end', 1)
text = text.replace('if pending==0 then return end', 'if pending==0 or beamBank~=4 or beamDepth~=0 then return end', 1)
p.write_text(text)
shutil.copyfile(p, OUT/'qualified-fixture.lua')
report = {'result': 'running', 'before_sha256': before, 'after_sha256': sha(p),
          'runtime_unchanged': True, 'original_frozen_result': '758/759; MMC3 bank-blind fragment observer failed',
          'passive_proof': 'build/verification/link-beam-v37-passive-a',
          'outside_qualified_control': 'build/verification/link-beam-v37-qualified-b',
          'retained_oracles': ['Every fragment quadrant/diagonal position', '84 pieces across21 updates', 'Source lifetime/expiration', 'Real attack/enemy impact/watchdog'],
          'fixture_hashes_before': {'tests/link-beam-impact.lua': sha(p), 'tools/run_mesen.py': sha(ROOT/'tools/run_mesen.py')}, 'cases': []}
for mapper in ('mmc3', 'mmc5'):
    rom = ROOT/f'build/checkpoints/roster-audit-v37-provisional-c/smb-crossover-{mapper}.nes'
    log = OUT/f'{mapper}.log'
    with log.open('w') as stream:
        result = subprocess.run([sys.executable, 'tools/run_mesen.py', str(p), str(rom), '--timeout', '70'], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    report['cases'].append({'rom': f'smb-crossover-{mapper}', 'test': 'link-beam-impact',
                            'exit': result.returncode, 'result': 'passed' if result.returncode == 0 else 'failed',
                            'rom_sha256': sha(rom), 'log': str(log.relative_to(ROOT)), 'log_sha256': sha(log)})
    print(mapper, result.returncode, flush=True)
report['fixture_hashes_after'] = {k: sha(ROOT/k) for k in report['fixture_hashes_before']}
assert report['fixture_hashes_before'] == report['fixture_hashes_after']
report['result'] = 'passed' if all(c['exit'] == 0 for c in report['cases']) else 'failed'
(OUT/'summary.json').write_text(json.dumps(report, indent=2)+'\n')
assert report['result'] == 'passed'
