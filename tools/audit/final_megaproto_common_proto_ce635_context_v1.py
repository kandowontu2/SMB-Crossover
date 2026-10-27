"""Rebind non-runtime human context only; preserve Proto14 mechanics and failures."""
from pathlib import Path
import argparse,copy,difflib,hashlib,json,shutil
from final_megaproto_common_proto_ce635_prepare_v1 import D,R,SHA
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_megaproto_common_proto_ce635_context_run_v1 import human_context_watch
OLD=D/'currentce635-proto-common-ready-v5'
NEG=D/'currentce635-proto-common-prelaunch-v1'
RUN=R/'tools/audit/final_megaproto_common_proto_ce635_context_run_v1.py'
USER=Path('C:/Mesen2/settings.json')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def bind(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def difference(a,b,path=''):
    if type(a)!=type(b):return [dict(path=path,old=a,current=b)]
    if isinstance(a,dict):return [z for k in sorted(a.keys()|b.keys())for z in difference(a.get(k),b.get(k),path+'.'+k)]
    if isinstance(a,list):
        if len(a)!=len(b):return [dict(path=path+'.length',old=len(a),current=len(b))]
        return [z for i,(x,y)in enumerate(zip(a,b))for z in difference(x,y,path+'.'+str(i))]
    return [] if a==b else [dict(path=path,old=a,current=b)]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--independent-role-proof',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    original=json.loads((OLD/'proof.json').read_text());assert sha(OLD/'proof.json')=='81b25bb24a900b0c5f5ecaa129b86fb62e09dd603e0af55ada2c55a808a685b7'
    oldrows=json.loads((OLD/'manifest.json').read_text())['bindings'];others=[];oldwatch=[]
    for q in oldrows:
        path=Path(q['path'])
        if path.resolve()==USER.resolve():oldwatch.append(q);continue
        assert path.stat().st_size==q['bytes'] and sha(path)==q['sha256'],path
        others.append(q)
    assert len(others)==1931 and len(oldwatch)==1
    assert not(OLD/'native/launch.json').exists() and not(OLD/'native/proof.json').exists()
    assert sha(NEG/'proof.json')=='63927470f7124ddd2e26197042e230f74d1a721589d586b74cb8103901de03a0'
    environment=copy.deepcopy(original['environment']);raw=USER.read_bytes();snap=a.output/'human-context-snapshot.json';snap.write_bytes(raw);human=json.loads(raw.decode('utf-8-sig'))
    compare={k:difference(environment[k],human[k],k)for k in ['Nes','Emulation']}
    put(a.output/'human-context-comparison.json',dict(passed=True,comparison='Current captured dictionaries versus old frozen environment dictionaries, not an invented full old-file diff.',snapshot=bind(snap),old_live_watch=oldwatch[0],first_prelaunch_actual=bind(NEG/'actual-user-settings.json'),current_dictionary_differences=compare,Nes_equal=not compare['Nes'],Emulation_equal=not compare['Emulation'],human_file_modified=False,live_hash_is_informational=True))
    driver=(R/'tools/audit/run_mesen_isolated.py').read_text();host=(R/'tools/run_mesen.py').read_text();base=(R/'tools/audit/final_megaproto_common_proto_ce635_run_v1.py').read_text();new=RUN.read_text()
    assert "namespace['run'](args.script, args.rom, args.emulator, args.timeout" in driver
    assert "executable = emulator or os.environ.get('MESEN') or shutil.which('Mesen')" in host
    assert "if not executable and Path('C:/mesen2/Mesen.exe').exists():" in host
    assert "'--emulator',str(exe)" in base and "exe=Path(env['emulator'])" in base
    assert 'C:/mesen2/settings.json' not in driver+host+base and 'C:/Mesen2/settings.json' not in driver+host+base
    changes=[('"""Exact combined ce635 ProtoHard14 one-shot with ordered refusal witnesses."""','"""Context-qualified ProtoHard14: strict runtime, informational human GUI watch."""'),
      ('def collect(out,cfg):','''def human_context_watch(path):
 try:
  raw=Path(path).read_bytes()
  return dict(available=True,path=str(path),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),runtime_input=False,informational=True)
 except OSError as error:
  return dict(available=False,path=str(path),error=type(error).__name__,runtime_input=False,informational=True)
def collect(out,cfg):'''),
      (' live=int(subprocess.check_output'," human_pre=human_context_watch(ready['environment']['human_context_watch_path'])\n live=int(subprocess.check_output"),
      ("profile='proto-hard-common',lane='B',acquisition=False)","profile='proto-hard-common',lane='B',acquisition=False,human_context_pre=human_pre,human_context_runtime_input=False)"),
      ('native_worker_released=True,ready_sha256=',"native_worker_released=True,human_context_pre=human_pre,human_context_post=human_context_watch(env['human_context_watch_path']),human_context_runtime_input=False,ready_sha256=")]
    expected=base
    for old,replacement in changes:assert expected.count(old)==1;expected=expected.replace(old,replacement)
    assert expected==new
    (a.output/'runner-context.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True),new.splitlines(True),fromfile='frozen-Proto14-runner',tofile='same-runner-additive-GUI-context-watch')),encoding='utf-8')
    emu=a.output/'emulator';emu.mkdir()
    oldemu=Path(environment['emulator']).parent
    runtime_rows=[]
    for q in oldemu.iterdir():
        if q.is_file():
            target=emu/q.name;shutil.copy2(q,target);assert sha(q)==sha(target);runtime_rows.append(dict(old=bind(q),current=bind(target),byte_exact=True))
    environment.update(emulator=str(emu/'Mesen.exe'),user_context_sha256=sha(snap),human_context_snapshot_path=str(snap),human_context_watch_path=str(USER),human_context_runtime_input=False,human_context_live_prepost_informational=True)
    assert sha(emu/'settings.json')==environment['worker_settings_sha256']=='627cd9c71a2011b4cf5fb03a0712d4d77f7890bc269b174d5757776034aab715'
    assert sha(emu/'Mesen.exe')==environment['emulator_sha256'] and sha(emu/'MesenCore.dll')==environment['core_sha256']
    probe=D/'mmc3-flag-fix-v23/script-budget-probe-v2/proof.json'
    assert sha(probe)=='494c8620e16b17bca84be11ec27cc065094b6f4be0e49ec8120cea176ee6475f'
    available=human_context_watch(snap);missing=human_context_watch(a.output/'deliberately-absent-context.json')
    assert available['sha256']==sha(snap) and available['informational'] and not available['runtime_input']
    assert missing['available'] is False and missing['informational'] and not missing['runtime_input']
    role=dict(passed=True,source_only=True,human_context_role='Protected external GUI provenance/watch, not a worker functional input.',
        python_launcher_consumes_human_settings=False,actual_explicit_emulator=str(emu/'Mesen.exe'),
        worker_settings=bind(emu/'settings.json'),runtime_files=runtime_rows,CLI_overrides=environment['actual_command_overrides'],
        source_facts=['Profile runner always supplies explicit --emulator from bound environment.',
                      'run_mesen_isolated forwards that explicit argument to tools/run_mesen.py.',
                      'run_mesen uses explicit emulator before environment/PATH/fallback; C:/mesen2/Mesen.exe fallback is unreachable in this invocation.',
                      'Neither Python driver opens or passes the human settings path. The isolated adjacent worker settings is strict and unchanged.',
                      'This source role proof is not an OS-level file-read trace or a new native experiment.'],
        independent_role_proof=bind(a.independent_role_proof)if a.independent_role_proof else None,
        historical_actual_private_setting_probe=bind(probe),
        historical_probe_scope='Same binary actual adjacent private settings consumption: one-second callback budget rejects; five seconds completes. Not rerun or retagged as current native coverage.',
        informational_watch_controls=dict(available=available,missing=missing,neither_controls_outcome=True),
        all1931_other_old_inputs_verified=True,no_human_settings_write=True,no_unchanged_heavy_CPU_rerun=True)
    put(a.output/'dependency-role.json',role);put(a.output/'environment.json',environment)
    out=a.output/'native';out.mkdir()
    for q in (OLD/'native').iterdir():
        assert q.name in ['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','config.json','run.lua','inherited-NMI-stack-APU-guards.lua'],q
        target=out/q.name;shutil.copy2(q,target);assert sha(q)==sha(target)
    assert sha(out/'run.lua')==original['script_sha256'] and sha(out/'candidate.nes')==SHA
    put(a.output/'context-invariants.json',dict(passed=True,all1931_other_old_inputs_exact=True,native_body_config_controller_mechanics_seeds_guards_collectors_literal=True,native_script_sha256=sha(out/'run.lua'),context_only_runner_additions=True,all_other_runner_predicates_reverse_exact=True,only_rebound_functional_paths=['explicit isolated emulator folder','native evidence output folder'],human_watch_rebound_to_strict_captured_provenance=True,live_human_hash_prepost_informational=True,source_CPU_controls_reused_for_same_ROM_and_unchanged_inputs=True,native_launches=0,original_prelaunch_FALSE_retained=bind(NEG/'proof.json')))
    files={Path(q['path'])for q in others}|{Path(__file__),RUN,OLD/'proof.json',OLD/'manifest.json',NEG/'proof.json',NEG/'other-bindings-proof.json',NEG/'actual-user-settings.json',probe}
    if a.independent_role_proof:
        role_manifest=a.independent_role_proof.parent/'manifest.json'
        verify_manifest(role_manifest);files.update({a.independent_role_proof,role_manifest})
        files.update(Path(q['path'])for q in json.loads(role_manifest.read_text())['bindings'])
    files.update(q for q in a.output.rglob('*')if q.is_file());assert USER.resolve()not in {q.resolve()for q in files}
    put(a.output/'manifest.json',dict(bindings=[bind(q)for q in sorted(files,key=str)]));count=verify_manifest(a.output/'manifest.json')
    proof=copy.deepcopy(original);command='python -B tools/audit/final_megaproto_common_proto_ce635_context_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant'
    proof.update(manifest_sha256=sha(a.output/'manifest.json'),bindings=count,output=str(out),script_sha256=sha(out/'run.lua'),environment=environment,stable_command=command,native_granted=False,native_run=False,context_only_successor=True,original_ready_sha256=sha(OLD/'proof.json'),original_prelaunch_FALSE=bind(NEG/'proof.json'),all1931_other_inputs_unchanged=True,human_context_role='captured non-runtime provenance; live pre/post informational',no_heavy_CPU_rerun=True)
    put(a.output/'proof.json',proof)
    print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=count,script_sha256=sha(out/'run.lua'),human_context_snapshot_sha256=sha(snap),dictionary_differences={k:len(v)for k,v in compare.items()},stable_command=command),indent=2))
if __name__=='__main__':main()
