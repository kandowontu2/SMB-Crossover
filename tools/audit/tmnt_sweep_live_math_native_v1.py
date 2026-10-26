"""Freeze one current-environment Easy600 pair; never launch without grant.

The historical workload and observer bodies are retained literally. Only the
already-qualified static dispatcher and read-only import locations are rebound.
"""
from pathlib import Path
import argparse
import json
import re
import shutil
import subprocess
import sys
from check_tmnt_render_oa import load, address, location
from tmnt_native_storage_driver import ROOT, CURRENT, sha

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
DIGEST = '53736e142c6cf568039a3c4927c9356077e3358b7c02fb7b69d3ca72985f2ff6'
OLD = D / 'tmnt-native-storage-current50b5-v1/parser-native-pilot-v1'
STATIC = D / 'tmnt-static-observer-v1'


def prepare(out):
    assert not out.exists() and not out.resolve().is_relative_to(ROOT)
    assert sha(STATIC/'run.lua') == '3412b98077d9c4f5436ab3df00712004fee572a1a3ceaa2810f355da646b4eca'
    assert sha(D/'tmnt-static-observer-native-ready-v1/receipt.json') == 'b9df30662d09d6704f5ff07d56e5140d9c8a610faebd83120813dcb4c873c828'
    roms = dict(baseline=D/'tmnt-native-storage-current50b5-v1/current-baseline-v1/baseline.nes',
                candidate=D/'tmnt-sweep-live-math-v1/candidate.nes')
    assert sha(roms['baseline']) == CURRENT and sha(roms['candidate']) == DIGEST
    assert sha(ROOT/'build/smb-crossover-mmc5-expanded.nes') == CURRENT
    out.mkdir(parents=True)
    common = [Path(__file__), ROOT/'tools/run_mesen.py', ROOT/'tools/audit/run_mesen_isolated.py',
              ROOT/'tools/audit/tmnt_native_storage_native_compare.py',
              D/'tmnt-static-observer-native-ready-v1/receipt.json']
    metadata = {}
    for label, rom in roms.items():
        target = out/(label+'-easy');target.mkdir()
        historical = OLD/(label+'-easy')
        original = (historical/'run.lua').read_text()
        if label == 'candidate':
            text = (STATIC/'run.lua').read_text()
            assert text.startswith('dofile(') and text.endswith('\nTMNT_STATIC_EXEC.install()\n')
            prefix = text[:text.index('\n')+1]
            original_body = text[len(prefix):-len('\nTMNT_STATIC_EXEC.install()\n')]
            replacements = {
                (STATIC/'chr-commit-observer.lua').as_posix(): (target/'chr-commit-observer.lua').as_posix(),
                (STATIC/'performance-observer.lua').as_posix(): (target/'performance-observer.lua').as_posix(),
            }
            original_replacements = {
                'C:/Users/kando/Documents/ChatGPT/SMB Crossover/tools/audit/chr_commit_observer.lua': (STATIC/'chr-commit-observer.lua').as_posix(),
                json.loads((historical/'config.json').read_text())['observer']: (STATIC/'performance-observer.lua').as_posix(),
            }
            expected = original
            for before, after in original_replacements.items():
                assert expected.count(before) == 1;expected = expected.replace(before, after)
            assert original_body == expected, 'Static native-qualified workload no longer literal historical body'
        else:
            original_body = original
            replacements = {
                'C:/Users/kando/Documents/ChatGPT/SMB Crossover/tools/audit/chr_commit_observer.lua': (target/'chr-commit-observer.lua').as_posix(),
                json.loads((historical/'config.json').read_text())['observer']: (target/'performance-observer.lua').as_posix(),
            }
        text = original_body
        for before, after in replacements.items():
            assert text.count(before) == 1, before;text = text.replace(before, after)
        reverse = text
        for before, after in replacements.items():reverse = reverse.replace(after, before)
        assert reverse == original_body
        assert '["behavior"]=0' in text and 'State writes only at before-phase setup' in text
        assert not re.search(r'\b(?:True|False)\b', text)
        text = 'dofile('+json.dumps((target/'tmnt_static_exec_dispatcher_v1.lua').as_posix())+')\n'+text+'\nTMNT_STATIC_EXEC.install()\n'
        (target/'run.lua').write_text(text)
        for name in ['tmnt_static_exec_dispatcher_v1.lua', 'chr-commit-observer.lua', 'performance-observer.lua']:
            shutil.copyfile(STATIC/name, target/name)
        for name in ['config.json', 'performance-fixture.lua', 'profile-config.json']:
            shutil.copyfile(historical/name, target/name)
        cfg = json.loads((target/'config.json').read_text())
        profile = json.loads((target/'profile-config.json').read_text());b = load(rom)
        assert cfg['behavior'] == 0 and cfg['variant'] == 0
        for name, pc in cfg['ram'].items():assert address(b, name) == pc, (label, name)
        for hook in profile['hooks']:
            assert address(b, hook['name']) == hook['pc']
            if 'seg' in b['syms'][hook['name']]:assert (location(b, hook['name'])-16)//8192 == hook['bank']
            else:assert hook['name'] in ['TnNativeInit', 'TnNativePlay'] and hook['bank'] == 63
        for name, pc in profile['ram'].items():assert address(b, name) == pc
        for site in profile['stores']:
            at = 16+site['bank']*8192+site['pc']%8192
            assert b['raw'][at:at+3] == bytes([0x8d, site['register']&255, 0x40])
        common += list(target.iterdir())
        common += [rom, *[rom.with_suffix(ext) for ext in ['.lbl','.dbg','.map']]]
        common += list(historical.iterdir())
        metadata[label] = dict(ROM=str(rom), ROM_sha256=sha(rom), behavior=0,
            script_sha256=sha(target/'run.lua'), frozen_historical_template=str(historical),
            frozen_historical_run_sha256=sha(historical/'run.lua'),
            exact_workload_reverse_check=True, static_dispatcher_native_qualified=True,
            numeric_mode_and_actual_readback_required=True, staged_inventory_BEFORE_only=True,
            no_natural_acquisition_claim=True, no_within_phase_outcome_or_cadence_injection=True)
    gold = D/'tmnt-native-storage-current50b5-v1/native-pilots-v1/candidate-easy/gold'
    common += sorted(gold.glob('song-*.bin'))
    exe = Path('C:/Mesen2/Mesen.exe');runtime = [exe,*sorted(exe.parent.glob('*.dll')),exe.parent/'settings.json']
    env = {str(path):sha(path) for path in runtime}
    (out/'runtime').mkdir();shutil.copyfile(exe.parent/'settings.json',out/'runtime/settings.json')
    dependencies = {str(path):sha(path) for path in sorted(set(common+runtime)) if path.is_file()}
    for label, binding in metadata.items():
        binding['dependencies'] = dependencies;binding['actual_runtime'] = env
        (out/(label+'-easy')/'binding.json').write_text(json.dumps(binding,indent=2)+'\n')
    readiness = dict(prepared=True,native_run=False,accepted=False,baseline_ROM_sha256=CURRENT,
        candidate_ROM_sha256=DIGEST,mode=0,phases=5,updates_per_phase=120,
        actual_runtime=env,case_bindings={label:sha(out/(label+'-easy')/'binding.json') for label in metadata},
        full_original_hardware_source_DMC_OAM_CHR_IRQ_NMI_SMC_stack_guards_retained=True,
        original_static_9a_negative_566_of600_retained=True,
        original_native_raw_frames=0,source_model_saving449_cycles=True,
        reconstructed_strict_acceptance_target441_cycles=True,native_recovery_claim=False,
        actual_grant_required=True,one_bounded_pair_only=True,no_retry_Hard_or_broader_campaign=True,
        checker_sha256=sha(Path(__file__)))
    (out/'readiness.json').write_text(json.dumps(readiness,indent=2)+'\n')
    commands = {label:[sys.executable,'-B',str(Path(__file__)),'--output',str(out),'--run-granted',label] for label in metadata}
    commands['compare'] = [sys.executable,'-B',str(ROOT/'tools/audit/tmnt_native_storage_native_compare.py'),
        '--baseline',str(out/'baseline-easy'),'--candidate',str(out/'candidate-easy'),'--output',str(out/'easy-strict-proof.json')]
    (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    print(json.dumps(dict(prepared=True,native_run=False,readiness_sha256=sha(out/'readiness.json'),runtime=env)))


def run(out,label):
    folder=out/(label+'-easy');b=json.loads((folder/'binding.json').read_text());rom=Path(b['ROM'])
    ready=json.loads((out/'readiness.json').read_text())
    assert sha(folder/'binding.json') == ready['case_bindings'][label]
    assert not (folder/'host.log').exists(), 'ONE bounded run; no retry'
    assert all(sha(Path(p))==h for p,h in b['dependencies'].items())
    assert b['behavior']==0 and sha(rom)==b['ROM_sha256'] and sha(folder/'run.lua')==b['script_sha256']
    cmd="@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*Mesen*' -and $_.CommandLine -like '*--testRunner*' }).Count"
    assert int(subprocess.check_output(['powershell','-NoProfile','-Command',cmd],text=True).strip())<2
    command=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),
        '--emulator','C:/Mesen2/Mesen.exe',str(folder/'run.lua'),str(rom),'--timeout','180',
        '--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros',
        '--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    with (folder/'host.log').open('w')as log:r=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    report=b|dict(passed=False,exit=r.returncode,command=command)
    names=['result.json','ownership-guards.json','chr-commit.json','mode-readback.json','native-source-hardware.json','first-hardware-failure.json']
    for name in names:
        if(folder/name).exists():report[name]=json.loads((folder/name).read_text())
    report['passed']=r.returncode==0 and all(report.get(n,{}).get('passed')for n in names[:3]) and report.get('mode-readback.json',{}).get('actual')==0
    if label=='candidate':report['passed'] &= report.get('native-source-hardware.json',{}).get('passed',False)
    (folder/'native-result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=report['passed'],exit=r.returncode,label=label,ROM_sha256=b['ROM_sha256'])))
    raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--run-granted',choices=['baseline','candidate']);a=p.parse_args()
    run(a.output,a.run_granted)if a.run_granted else prepare(a.output)
