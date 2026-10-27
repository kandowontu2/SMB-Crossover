"""Prepare only a374..380 metadata focus extension of the retained strict run."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from final_item_abilities_run import lua

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OLD=D/'robot-cold-palette-candidate-v2/ready-v2'
C=D/'robot-cold-palette-candidate-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    assert sha(OLD/'readiness.json')=='6c7f6e71cbc5cef50f1e847262476f7df72eb722ef6bd20bf1a35682adf5370f'
    bindings=json.loads((OLD/'bindings.json').read_text())
    for f,h in bindings.items():assert sha(f)==h,f
    assert not json.loads((OLD/'launch-outcome-v1.json').read_text())['passed']
    original=json.loads((OLD/'native/config.json').read_text());cfg=json.loads(json.dumps(original))
    assert cfg['diagnostic']['first_frame']==374 and cfg['diagnostic']['last_frame']==377
    cfg['diagnostic']['last_frame']=380
    control=json.loads(json.dumps(cfg));control['diagnostic']['last_frame']=377
    assert control==original
    before=(OLD/'native/run.lua').read_text()
    prefix='FINAL_ITEM_PROGRESSIVE='+lua(original)+'\n';assert before.startswith(prefix)
    script='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+before[len(prefix):]
    assert script.split('\n',1)[1]==before.split('\n',1)[1]
    assert prefix+script[len('FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'):]==before
    native=a.output/'native';native.mkdir();put(native/'config.json',cfg);(native/'run.lua').write_text(script)
    command=json.loads((OLD/'command.json').read_text())
    command=[str(native)if x==str(OLD/'native')else str(native/'run.lua')if x==str(OLD/'native/run.lua')else x for x in command]
    assert str(native/'run.lua')in command and str(C/'candidate.nes')in command
    put(a.output/'command.json',command)
    put(a.output/'metadata-only-proof.json',dict(prepared=True,native_run=False,
        only_config_delta={'diagnostic.last_frame':[377,380]},config_reverse_exact=True,
        entire_postconfig_Lua_body_byte_exact=True,controller_mechanics_guards_callback_registrations_exact=True,
        same_ROM=True,same_mode_variant_caps_and_cases=True,original_strict_failure_preserved=True,
        original_readiness_sha256=sha(OLD/'readiness.json'),original_config_sha256=sha(OLD/'native/config.json'),
        new_config_sha256=sha(native/'config.json'),original_script_sha256=sha(OLD/'native/run.lua'),
        new_script_sha256=sha(native/'run.lua'),tool_sha256=sha(__file__)))
    extras=[OLD/x for x in ['readiness.json','bindings.json','ROOT-grant.json','launch-binding-v1.json','launch-outcome-v1.json','command.json']]
    extras += [C/'native-review-v1'/x for x in ['proof.json','external-raw-manifest.json','actual-source-evidence.json','samples.json','actual-startup-whole-images.png']]
    extras += [R/'tools/audit'/x for x in ['mm_proto_cold_palette_run_v1.py','mm_proto_cold_palette_native_review_v1.py','mm_proto_cold_palette_diagnostic_run_v1.py']]
    extras += [Path(__file__),Path(sys.executable),*a.output.rglob('*')]
    for f in extras:
        if f.is_file():bindings[str(f.resolve())]=sha(f)
    put(a.output/'bindings.json',dict(sorted(bindings.items())))
    put(a.output/'readiness.json',dict(prepared=True,native_run=False,native_granted=False,
        candidate_ROM_sha256=sha(C/'candidate.nes'),maximum_native_launches=1,maximum_workers=1,
        wall_bound=4000,host_seconds=1200,diagnostic_focus=[374,380],same_six_case_profile=True,
        only_config_change='diagnostic.last_frame377->380',all_postconfig_observer_mechanics_and_guards_exact=True,
        expected_first_strict_failure='PPU378 enable1:38, samecase1/use; not a pass if repeated',
        needed_evidence=['actual378NMI entry84-bytebuffer1/34-bytebuffer2/control/cache/CHRstate',
            'actual378parser heads+orderedwrites+boundedinclusiveownerreturns',
            'actualproducerbufferwrites/ownerentries374..378',
            'pre-original-assertPPUMASKstamp plus independentfull256DMAguard'],
        no_new_callbacks_or_runtime_host_registration=True,no_new_game_state_or_resource_writes=True,
        no_guard_relaxation=True,no_retry=True,bindings=len(bindings),bindings_sha256=sha(a.output/'bindings.json'),
        command_sha256=sha(a.output/'command.json'),metadata_proof_sha256=sha(a.output/'metadata-only-proof.json'),
        script_sha256=sha(native/'run.lua'),tool_sha256=sha(__file__),
        limitations='One unlaunched read-only focus extension; original stagedcomponentsetups remain literal. Original firstnegative immutable. No authorization to run without separateROOTgrant. Exact378 workload is unlogged in original; no CPU estimate is substituted for native evidence.'))
    print(json.dumps(dict(readiness=str(a.output/'readiness.json'),sha256=sha(a.output/'readiness.json'),bindings=len(bindings)),indent=2))


if __name__=='__main__':main()
