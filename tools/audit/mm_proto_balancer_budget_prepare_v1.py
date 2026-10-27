"""Prepare only990..996 diagnostic metadata on the frozen strictdf profile."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from final_item_abilities_run import lua

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
C=D/'robot-base-palette-candidate-v2';OLD=C/'ready-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    assert sha(OLD/'readiness.json')=='d48e101f291439971146878107832bab23bdbc1fc534c2138ef9460e5406bb0d'
    bindings=json.loads((OLD/'bindings.json').read_text())
    for f,h in bindings.items():assert sha(f)==h,f
    assert not json.loads((OLD/'launch-outcome-v1.json').read_text())['passed']
    original=json.loads((OLD/'native/config.json').read_text());cfg=json.loads(json.dumps(original))
    assert[cfg['diagnostic']['first_frame'],cfg['diagnostic']['last_frame']]==[374,380]
    cfg['diagnostic']['first_frame'],cfg['diagnostic']['last_frame']=990,996
    restored=json.loads(json.dumps(cfg));restored['diagnostic']['first_frame'],restored['diagnostic']['last_frame']=374,380
    assert restored==original
    before=(OLD/'native/run.lua').read_text();prefix='FINAL_ITEM_PROGRESSIVE='+lua(original)+'\n';assert before.startswith(prefix)
    script='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+before[len(prefix):]
    assert prefix+script[len('FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'):]==before
    assert script.split('\n',1)[1]==before.split('\n',1)[1]
    native=a.output/'native';native.mkdir();put(native/'config.json',cfg);(native/'run.lua').write_text(script)
    command=json.loads((OLD/'command.json').read_text())
    command=[str(native)if x==str(OLD/'native')else str(native/'run.lua')if x==str(OLD/'native/run.lua')else x for x in command]
    assert str(native/'run.lua')in command and str(C/'candidate.nes')in command;put(a.output/'command.json',command)
    put(a.output/'metadata-only-proof.json',dict(prepared=True,native_run=False,
        only_config_delta={'diagnostic.first_frame':[374,990],'diagnostic.last_frame':[380,996]},
        config_reverse_exact=True,entire_postconfig_Lua_body_byte_exact=True,
        callback_registration_controller_mechanics_caps_strictguards_exact=True,
        same_exact_df_ROM=True,same_ProtoHard_sixcases=True,original_strict993_failure_preserved=True,
        prior_readiness_sha256=sha(OLD/'readiness.json'),original_script_sha256=sha(OLD/'native/run.lua'),
        new_script_sha256=sha(native/'run.lua'),tool_sha256=sha(__file__)))
    extra=[OLD/x for x in['readiness.json','bindings.json','ROOT-grant.json','launch-binding-v1.json','launch-outcome-v1.json','command.json']]
    extra+=[C/'native-review-v1'/x for x in['proof.json','external-raw-manifest.json','native-evidence.json','samples.json']]
    extra+=[R/'tools/audit'/x for x in['mm_proto_base_palette_run_v1.py','mm_proto_base_palette_native_review_v1.py','mm_proto_cold_palette_diagnostic_run_v1.py']]
    extra+=[Path(__file__),Path(sys.executable),*a.output.rglob('*')]
    for f in extra:
        if f.is_file():bindings[str(f.resolve())]=sha(f)
    put(a.output/'bindings.json',dict(sorted(bindings.items())))
    put(a.output/'readiness.json',dict(prepared=True,native_run=False,native_granted=False,
        candidate_ROM_sha256=sha(C/'candidate.nes'),diagnostic_focus=[990,996],
        maximum_native_launches=1,maximum_workers=1,wall_bound=4000,host_seconds=1200,no_retry=True,
        same_sixcase_controller_body_callbacks_and_allguards=True,
        expected_first_failure='PPU993enable1:57 duringcase6Balancer/use; strictFALSE remainsFALSE',
        needed_evidence=['actual993NMI queues84/34,control,CHR/cache/palette/HUD state',
            '990..993actualproducerwriteandownerchronology includingBalancerchoice/refill state',
            '993actualparserheads/writes/inclusivepalettegatewayandCHRcost',
            'actualPPUMASKbeforeoriginalassert andindependentfull256DMA'],
        no_new_callbacks_or_runtime_registration=True,no_new_game_state_writes=True,no_guard_relaxation=True,
        metadata_proof_sha256=sha(a.output/'metadata-only-proof.json'),bindings=len(bindings),bindings_sha256=sha(a.output/'bindings.json'),
        command_sha256=sha(a.output/'command.json'),script_sha256=sha(native/'run.lua'),tool_sha256=sha(__file__),
        limitations='Source/instrumentation preparationonly; no native grant. Original stagedsetups literal, not naturalacquisition. Exact993queue was not previouslylogged, so no cost/producer hypothesis treatedasobserved. OriginalfirstFALSE/profile preserved.'))
    print(json.dumps(dict(readiness=str(a.output/'readiness.json'),sha256=sha(a.output/'readiness.json'),bindings=len(bindings)),indent=2))


if __name__=='__main__':main()
