"""Prepare/run one bounded current50b5 versus a983 native stress pilot.

Historical before-phase inventory/actors are disclosed same-work setup only.
No within-phase resource outcome, RNG, audio owner/sample or cadence writes.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import sys
from link_pit_rygar_sophia_audit_cpu import scoped_load as load
from check_tmnt_render_oa import address
from observe_chip_committed_write import lua
from tmnt_native_storage_driver import ROOT, CURRENT, OB, sha

CANDIDATE = 'a9838664f94d29d87fbf4742e31d4e20d8b3a96862beabd11224afa4742d9003'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['rom', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--behavior', type=int, choices=[0, 1], required=True)
    p.add_argument('--run', action='store_true')
    p.add_argument('--timeout', type=int, default=180)
    p.add_argument('--emulator', type=Path, default=Path('C:/mesen2/Mesen.exe'))
    a = p.parse_args()
    assert sha(a.rom) in [CURRENT, CANDIDATE]
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    b = load(a.rom)
    fixture = ROOT / 'tests/tmnt-performance.lua'
    observer = ROOT / 'tools/audit/tmnt_performance_observer.lua'
    guards = ROOT / 'tools/audit/vehicles_audio_wiring_guards.lua'
    extra = ROOT / 'tools/audit/tmnt_native_storage_native_guards.lua'
    chr_observer = ROOT / 'tools/audit/chr_commit_observer.lua'
    text = fixture.read_text()
    assert "C.mode=='hard'" in text
    text = text.replace("local phase=C.mode=='hard'and'options-focus'or'start'", "local phase=C.behavior==1 and'options-focus'or'start'")
    writer = "local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end"
    assert text.count(writer) == 1
    text = text.replace(writer, "local function w(n,v,i)assert(C.setup==1,'State writes only at before-phase setup');local at=assert(L[n],n)+(i or 0);C.writes[#C.writes+1]={address=at,before=emu.read(at,emu.memType.nesDebug),value=v%256,name=n};emu.write(at,v%256,emu.memType.nesDebug)end")
    text = text.replace("local trace=assert(io.open", "local boundary=assert(io.open(TEST_DIR..'before-phase-setup.jsonl','w'))\nlocal function json(v)if type(v)=='table'then local t={};for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;return'{'..table.concat(t,',')..'}'elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end end\nlocal trace=assert(io.open", 1)
    text = text.replace("local function arena()\n", """local function arena()
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('AreaType')==1,'Actual1-1 overworld stage')
 assert(r('Player_Y_HighPos')==1 and r('SelectedCharacter')==19,'Live native turtle before phase setup')
 for col=2,15 do assert(emu.read(L.Block_Buffer_1+0xb0+col,emu.memType.nesDebug)~=0,'Native first-screen ground at feet208 is retained')end
 C.setup=1;C.writes={};C.phase=names[phaseIndex]
 local before={phase=names[phaseIndex],step=step,hp=r('TnHealth',C.variant),gear=r('TnEquipment',C.variant),ammo=r('TnAmmo',C.variant),selected=r('TnGearSelected'),behavior=r('CrossoverBehaviorVersion')}
 boundary:write(json({kind='before',data=before})..'\\n');boundary:flush()
""")
    text = text.replace('for a=0x5c00,0x5cff do emu.write(a,0,emu.memType.nesDebug)end', "for a=0x5c00,0x5cff do C.writes[#C.writes+1]={address=a,before=emu.read(a,emu.memType.nesDebug),value=0,name='native-area-slab'};emu.write(a,0,emu.memType.nesDebug)end")
    text = text.replace("end\nfinish=function()", """ local q={phase=names[phaseIndex],step=step,hp=r('TnHealth',C.variant),gear=r('TnEquipment',C.variant),ammo=r('TnAmmo',C.variant),selected=r('TnGearSelected'),player_y=r('Player_Y_Position'),enemy_y=r('Enemy_Y_Position'),enemy_y1=r('Enemy_Y_Position',1)}
 if phaseIndex>=3 then assert(q.enemy_y==184 and q.enemy_y1==184,'Both real native Goomba actors have supported feet208')end
 boundary:write(json({kind='staged',data=q,writes=C.writes})..'\\n');boundary:flush();C.setup=0
end
finish=function()""", 1)
    text = text.replace('profile.finish();trace:close();', 'profile.finish();trace:close();boundary:close();')
    text = text.replace("entered=true\n", """assert((C.behavior==0 or C.behavior==1)and r('CrossoverBehaviorVersion')==C.behavior,'Actual cold selected numeric Easy/Hard')
   local f=assert(io.open(OUTPUT..'mode-readback.json','w'));f:write('{"requested":'..C.behavior..',"actual":'..r('CrossoverBehaviorVersion')..',"selected":'..r('SelectedCharacter')..'}');f:close()
   entered=true;C.entered=1
""", 1)
    # Finish the final physical frame so all600 source updates have a frame row.
    text = text.replace('if step==600 then completed=true;finish();return true end', 'if step==600 then completed=true end')
    text = text.replace('wall=wall+1\n', 'wall=wall+1\n if completed then finish();return end\n', 1)
    text = text.replace("trace:write(table.concat(v,',')..'\\n');step=step+1", "trace:write(table.concat(v,',')..'\\n');step=step+1;C.step=step")
    (a.output / 'performance-fixture.lua').write_text(text)
    (a.output / 'performance-observer.lua').write_bytes(observer.read_bytes())
    used = set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'", text + extra.read_text())) | set(re.findall(r'L\.([A-Za-z_][A-Za-z_0-9]*)', text + extra.read_text()))
    cfg = dict(behavior=a.behavior, mode='hard' if a.behavior else 'easy', variant=0,
               native=int(sha(a.rom) == CANDIDATE), entered=0, step=0, phase='startup',
               observer=(a.output / 'performance-observer.lua').as_posix(),
               ram={name: address(b, name) for name in used if name in b['syms']})
    cfg['sites'] = []
    if cfg['native']:
        preparation = json.loads((a.rom.parent.parent / 'current-swap-v2/preparation.json').read_text())
        cfg['sites'] = [dict(pc=row['pc'] + 0x2000 if row['pc'] < 0xc000 else row['pc'] - 0x2000,
                             address=row['address'], mode=row['mode']) for row in preparation['standalone_source']['APU_stores']]
        gold = a.output / 'gold';gold.mkdir();cfg['gold'] = gold.as_posix() + '/'
        coverage = json.loads((OB / 'probe-v2/coverage.json').read_text())
        for song in range(1, 17):
            path = OB / f'probe-v2/song-{song:02d}.json.gz'
            assert sha(path) == coverage['songs'][str(song)]['capture_sha256']
            rows = json.loads(gzip.decompress(path.read_bytes()))[:2002]
            data = bytearray()
            for row in rows:
                assert len(row['writes']) < 256
                data.append(len(row['writes']))
                for at, value in row['writes']: data.extend([at - 0x4000, value])
            (gold / f'song-{song}.bin').write_bytes(data)
    smc = next(g for g in b['segs'].values() if g.get('name') == '"SMCCODE"')
    guard_cfg = dict(nmi=address(b, 'NonMaskableInterrupt'),
                     nmi_return=address(b, 'NonMaskableInterrupt') + int(b['syms']['NonMaskableInterrupt']['size'], 0) - 1,
                     smc=[address(b, name) + 1 for name in ['NextBank_SMC', 'SafecallA_SMC', 'SafereturnA_SMC', 'FarcallJmpTarget_SMC']] + [address(b, 'FarcallJmpTarget_SMC') + 2],
                     stack_floor=(int(smc['start'], 0) + int(smc['size'], 0)) & 255,
                     stack_start=int(smc['start'], 0) & 255, music=0, chr_observer=chr_observer.as_posix())
    lines = ['VEHICLE_AUDIO_CONFIG=' + lua(guard_cfg), guards.read_text(),
             'TMNT_STORAGE_NATIVE=' + lua(cfg), 'TMNT_CFG=TMNT_STORAGE_NATIVE', extra.read_text(), text]
    script = a.output / 'run.lua';script.write_text('\n'.join(lines))
    assert '["behavior"]=' + str(a.behavior) in script.read_text()
    assert not re.search(r'\b(?:True|False)\b', '\n'.join([lines[0], lines[2]]))
    parser = ROOT / 'build/verification/agent47-samus-controller-batch-h-preparation/parser'
    py = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    command = 'import pathlib,sys;sys.path.insert(0,sys.argv[1]);from lupa.lua54 import LuaRuntime;LuaRuntime().eval("function(s)local f,e=load(s);assert(f,e);return true end")(pathlib.Path(sys.argv[2]).read_text());print("Lua54 syntax PASS")'
    parsed = subprocess.run([str(py), '-c', command, str(parser / 'runtime'), str(script)], capture_output=True, text=True)
    (a.output / 'parse.log').write_text(parsed.stdout + parsed.stderr)
    assert parsed.returncode == 0, parsed.stderr
    dependencies = {str(path): sha(path) for path in [Path(__file__), fixture, observer, guards, extra, chr_observer,
                                                     ROOT / 'tools/audit/run_mesen_isolated.py', ROOT / 'tools/run_mesen.py']}
    (a.output / 'config.json').write_text(json.dumps(cfg, indent=2) + '\n')
    binding = dict(prepared=True, ROM_sha256=sha(a.rom), ROM=str(a.rom), behavior=a.behavior,
                   script_sha256=sha(script), dependencies=dependencies, emulator_sha256=sha(a.emulator),
                   staged_inventory_before_phase_only=True, natural_acquisition_claim=False)
    (a.output / 'binding.json').write_text(json.dumps(binding, indent=2) + '\n')
    if not a.run:
        print(json.dumps(binding));return
    with (a.output / 'host.log').open('w') as log:
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'tools/audit/run_mesen_isolated.py'), '--output', str(a.output),
                                 '--emulator', str(a.emulator), str(script), str(a.rom.resolve()), '--timeout', str(a.timeout),
                                 '--option=--doNotSaveSettings', '--option=--nes.ramPowerOnState=AllZeros',
                                 '--option=--nes.randomizeCpuPpuAlignment=false', '--option=--nes.randomizeMapperPowerOnState=false'],
                                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    report = binding | dict(passed=False, exit=result.returncode)
    for name in ['result.json', 'ownership-guards.json', 'chr-commit.json', 'mode-readback.json',
                 'first-hardware-failure.json', 'native-source-hardware.json']:
        if (a.output / name).exists(): report[name] = json.loads((a.output / name).read_text())
    report['passed'] = result.returncode == 0 and all(report.get(name, {}).get('passed') for name in ['result.json', 'ownership-guards.json', 'chr-commit.json', 'native-source-hardware.json']) and report.get('mode-readback.json', {}).get('actual') == a.behavior
    (a.output / 'native-result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ['dependencies']}, indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
