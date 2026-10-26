"""Prepare the unchanged strict CV3 pressure control for the composed display build."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
from check_tmnt_render_oa import load, address, location
from check_tmnt_audio_fallback_oc import qualified
from observe_chip_committed_write import lua

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT = D / 'root-postdma900-hard1f-v2'
ROM = D / 'current3cee-postdma-mask-v1/canonical-v2/candidate.nes'
PARENT = D / 'root-composed3cee-hard1f-v1/fixture'
FINAL = '900b669e212b878041c23e438f2fb26e310ce8f929f904681a9c4b17405b6968'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(ROM) == FINAL
    assert json.loads((PARENT / 'proof.json').read_text())['passed']
    assert not OUT.exists()
    OUT.mkdir()
    fixture = OUT / 'fixture'
    fixture.mkdir()
    old = json.loads((PARENT / 'configuration.json').read_text())
    cfg = json.loads(json.dumps(old))
    b = load(ROM)
    labels = qualified(ROM)
    for n, h in cfg['hooks'].items():
        if n == 'NmiReturn':
            off = 16 + h['physical_bank']*8192 + (h['address'] & 8191)
            assert h['bytes'] == [64] and b['raw'][off] == 64
            continue
        proc, sep, leaf = n.partition('::')
        pc = labels[(proc, leaf)] if sep else address(b, n)
        off = location(b, proc) + pc - address(b, proc)
        assert (off-16)//8192 == h['physical_bank'], n
        h['address'] = pc
        h['bytes'] = list(b['raw'][off:off+3])
    for n, at in cfg['ram'].items():
        cfg['ram'][n] = address(b, n)
    for n in cfg['queue_writers'].values():
        off = 16 + n['bank']*8192 + (n['pc'] & 8191)
        assert list(b['raw'][off:off+len(n['opcode'])]) == n['opcode']
    body = (PARENT / 'run.lua').read_text(encoding='utf-8').split('\n', 1)[1]
    script = fixture / 'run.lua'
    script.write_text('CV3_REMAINING_NATIVE_CONFIG=' + lua(cfg) + '\n' + body, encoding='utf-8', newline='\n')
    assert script.read_text(encoding='utf-8').split('\n', 1)[1] == body
    assert sha(PARENT/'run.lua') == '6dd92121fb64bb92ce2c471a50aac7dd45fae1c5d20f10aa1e0aa22cb0fc605a', 'Original exact3cee control must remain unchanged'
    assert script.read_text().split('\n',1)[1] == (PARENT/'run.lua').read_text().split('\n',1)[1]
    shutil.copyfile(ROM.with_suffix('.lbl'), fixture / 'candidate.lbl')
    (fixture / 'configuration.json').write_text(json.dumps(cfg, indent=2) + '\n')
    prep = dict(prepared=True, native_executed=False, ROM=str(ROM), ROM_sha256=FINAL,
                script=str(script), script_sha256=sha(script),
                configuration_sha256=sha(fixture / 'configuration.json'),
                same_input_baseline=str(PARENT), parent_script_sha256=sha(PARENT / 'run.lua'),
                controller_seed_workload_and_all_original_guards_byteexact=True,only_genuine_compiled_hook_code_label_metadata_rebound=True,
                scope='Same unchanged Hard1F240 control on3cee versus installed6c69, for shared display/NMI interaction only. No grant or native run.')
    (fixture / 'preparation.json').write_text(json.dumps(prep, indent=2) + '\n')
    deps = D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'
    for tool, arg, name in [('cv3_remaining_sfx_queue_native_startup_v2.py', '--fixture', 'startup'),
                            ('cv3_remaining_sfx_legacy_wrapper_observer_v1.py', '--fixture', 'observer')]:
        with (OUT / (name + '.log')).open('w') as log:
            subprocess.run([sys.executable, '-B', str(ROOT / 'tools/audit' / tool), arg, str(fixture),
                            '--lua-root', str(deps), '--output', str(OUT / name)], cwd=ROOT,
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        assert json.loads((OUT / name / 'proof.json').read_text())['passed']
    combined = D / 'cv3-parodius-combined-f35-v1/freeze-v1/readiness-source-only.json'
    native = D / 'cv3-remaining-legacy-wrapper-v2/native-freeze-v1/qualification-native.json'
    bindings = dict(json.loads(combined.read_text())['all_frozen_bindings'])
    bindings.update(json.loads(native.read_text())['all_new_frozen_bindings'])
    for p in [combined, native, Path(__file__), D / 'root-combined4285-hard1f-v1/failed-preparer-v1.py.txt', D / 'root-combined4285-hard1f-v1/startup.log', ROOT / 'tools/audit/run_mesen_isolated.py',
              ROOT / 'tools/audit/cv3_remaining_sfx_lifecycle_verify_v3.py',
              ROOT / 'tools/audit/cv3_remaining_sfx_lifecycle_launch_v1.py']:
        bindings[str(p)] = sha(p)
    for folder in [OUT, PARENT, deps]:
        for p in folder.rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:
                bindings[str(p)] = sha(p)
    padding = D / 'world-firebar-padding-v2'
    gate = padding / 'ready-v1/receipt.json'
    assert sha(gate) == '9225b3bafce11ac542d6d10725d7e2ca99757bf586d908ff469af943f045722f'
    bindings[str(gate)] = sha(gate)
    for n, row in json.loads(gate.read_text())['files'].items():
        assert sha(n) == row['sha256'], n
        bindings[n] = row['sha256']
    for n, h in json.loads((padding / 'source-manifest.json').read_text()).items():
        bindings[str(padding / 'source' / n)] = h
    composed = D / 'root-chip-hud-composed-v1'
    cpu = D / 'chip-hot-control-composed3cee-v1/freeze-v1/receipt.json'
    assert sha(cpu) == '3884f62509f34f7c3204da5d2586cec9bd55f9fd5b0483a9e95c3537509934a9'
    cq = json.loads(cpu.read_text())
    assert cq['passed'] and cq['candidate_ROM_sha256'] == '3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
    bindings[str(cpu)] = sha(cpu)
    for row in cq['bindings']:
        assert sha(row['path']) == row['sha256']
        bindings[row['path']] = row['sha256']
    for suffix in ['.nes', '.dbg', '.lbl', '.map', '.build.json', '.cv3-mirror.json']:
        f = ROM.with_suffix(suffix)
        bindings[str(f)] = sha(f)
    for name in ['proof.json', 'source-manifest.json']:
        bindings[str(composed / name)] = sha(composed / name)
    for name, digest in json.loads((composed / 'source-manifest.json').read_text()).items():
        bindings[str(composed / 'source' / name)] = digest
    candidate = D / 'current3cee-postdma-mask-v1/canonical-v2'
    for name in ['proof.json','source-manifest.json']:
        bindings[str(candidate/name)] = sha(candidate/name)
    for name,h in json.loads((candidate/'source-manifest.json').read_text()).items():
        assert sha(candidate/'source'/name)==h
        bindings[str(candidate/'source'/name)] = h
    for f in [D/'current3cee-postdma-mask-v1/NMI-CPU-v4/proof.json',D/'root-current3cee-postdma-bootstrap-review-v2/proof.json']:
        assert json.loads(f.read_text())['passed'];bindings[str(f)] = sha(f)
    for p, h in bindings.items():
        assert sha(p) == h, p
    command = [sys.executable, '-B', str(ROOT / 'tools/audit/run_mesen_isolated.py'), '--output', str(fixture),
               '--emulator', 'C:/Mesen2/Mesen.exe', str(script), str(ROM), '--timeout', '180',
               '--option=--doNotSaveSettings', '--option=--nes.ramPowerOnState=AllZeros',
               '--option=--nes.randomizeCpuPpuAlignment=false', '--option=--nes.randomizeMapperPowerOnState=false',
               '--option=--nes.removeSpriteLimit=false']
    cell = dict(name='combined-pressure-fireball-hard', version='candidate', profile='pressure', mode=1,
                expected_updates=240, fixture=str(fixture), same_input_baseline=str(PARENT),
                ROM=dict(path=str(ROM), sha256=FINAL), future_separately_granted_command=command)
    ready = dict(passed=True, native_executed=False, native_grant=False, candidate_ROM_sha256=FINAL,
                 baseline_ROM_sha256='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99',
                 future_launches=[cell], settings=dict(path='C:/Mesen2/settings.json', sha256=sha('C:/Mesen2/settings.json')),
                 designated_native_validator=str(ROOT / 'tools/audit/cv3_remaining_sfx_lifecycle_verify_v3.py'),
                 all_frozen_bindings=bindings, original_guard_body_unchanged=True,
                 changed_metadata_hooks=[n for n in cfg['hooks'] if cfg['hooks'][n] != old['hooks'][n]],
                 changed_code_label_fields=[n for n in cfg['ram'] if cfg['ram'][n] != old['ram'][n]],
                 scope='One postDMA900 same-input strict pressure control against3cee; original6dd92121 Lua body unchanged and only genuine compiled hook/code-label metadata rebound. Existing startup pair/source checks are separate; no gameplay/performance/adoption result yet.')
    p = OUT / 'readiness-source-only.json'
    p.write_text(json.dumps(ready, indent=2) + '\n')
    print(json.dumps(dict(passed=True, readiness=str(p), sha256=sha(p), bindings=len(bindings),
                          changed_metadata_hooks=ready['changed_metadata_hooks'])))


if __name__ == '__main__':
    main()
