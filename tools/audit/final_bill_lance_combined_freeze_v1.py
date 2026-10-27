"""Freeze two separately granted one-profile combined-ROM galleries; never launch."""
from pathlib import Path
import argparse,json
from final_bill_lance_combined_prepare_v2 import D,ROOT,PARENT,SHA,sha,put
from final_item_abilities_remaining731_run_v1 import verify_manifest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    prepared=json.loads((a.ready/'proof.json').read_text());assert prepared['ROM_sha256']==SHA and not prepared['native_run']
    assert verify_manifest(a.ready/'manifest.json')==938
    controls=a.ready/'hud-controls-v2/proof.json';cpu=json.loads(controls.read_text());assert cpu['passed']and cpu['ROM_sha256']==SHA and cpu['actual_full_RemainingDraw_calls']==96
    source=json.loads((PARENT/'source-manifest.json').read_text());assert len(source)==871
    for n,h in source.items():assert sha(PARENT/'source'/n)==h,n
    old=D/'final-bill-lance-hard-gallery-ready-v5';addon=(ROOT/'tools/audit/final_bill_lance_combined_hud_v1.lua').read_text();equal=[]
    for profile in prepared['profiles']:
        native=Path(profile['output']);assert not(native/'launch.json').exists()
        before=(old/'profiles'/profile['profile']/'native/run.lua').read_text().split('\n',1)[1]
        after=(native/'run.lua').read_text().split('\n',1)[1]
        assert after.count(addon)==1 and after.replace(addon+'\n','',1)==before
        cfg=json.loads((native/'config.json').read_text());assert cfg['ROM_sha256']==SHA
        assert (native/'inherited-NMI-stack-APU-guards.lua').read_bytes()==(old/'profiles'/profile['profile']/'native/inherited-NMI-stack-APU-guards.lua').read_bytes()
        equal.append(dict(profile=profile['profile'],native_v3_whole_controller_and_guard_body_literal_except_addon=True,
                          config_ROM_RAM_hooks_records_derived_from_actual_combined_executable=True,extra_observer_readonly=True,
                          script_sha256=sha(native/'run.lua'),config_sha256=sha(native/'config.json')))
    before=(ROOT/'tools/audit/final_bill_lance_hard_gallery_run_v2.py').read_text();after=(ROOT/'tools/audit/final_bill_lance_combined_run_v1.py').read_text()
    old_collector=before[before.index('def collect(out,cfg):'):before.index('\ndef main():')].strip()
    new_collector=after[after.index('def collect(out,cfg):'):after.index('TYPED_ORIGINAL_COLLECT=collect')].strip()
    assert old_collector==new_collector and before[before.index('def main():'):]==after[after.index('def main():'):]
    put(a.output/'literal-equality.json',dict(passed=True,native_run=False,profiles=equal,typed_original_host_collector_literal=True,
        host_main_literal=True,host_metadata_delta='Explicit newce635 SHA; same main calls unchanged typed collector then validates added HUD receipt.',
        old_3b_native_results_remain_old_hash=True,new_combined_native_unrun=True))
    files={Path(z['path'])for z in json.loads((a.ready/'manifest.json').read_text())['bindings']}
    files.update(PARENT/'source'/n for n in source)
    files.update([Path(__file__),a.ready/'proof.json',a.ready/'manifest.json',controls,a.ready/'hud-controls-v2/manifest.json',
                  ROOT/'tools/audit/final_bill_lance_combined_hud_controls_v1.py',ROOT/'tools/audit/final_bill_lance_combined_hud_controls_v2.py',
                  ROOT/'tools/audit/final_bill_lance_combined_prepare_v1.py',ROOT/'tools/audit/final_bill_lance_combined_prepare_v2.py',
                  ROOT/'tools/audit/final_bill_lance_combined_run_v1.py',ROOT/'tools/audit/final_bill_lance_combined_hud_v1.lua',
                  D/'bill-capsule-hud-current3b-v1/source-freeze-v1/proof.json',D/'bill-capsule-hud-current3b-v1/source-freeze-v1/manifest.json'])
    for sub in ['hud-controls-v1','hud-controls-v2','hud-controls-parser-negative-v1']:
        files.update(f for f in(a.ready/sub).iterdir()if f.is_file())
    draft=D/'final-bill-lance-combined-ce635-ready-v1'
    files.update(f for f in draft.iterdir()if f.is_file())
    for profile in prepared['profiles']:
        files.update([old/'profiles'/profile['profile']/'native/run.lua',old/'profiles'/profile['profile']/'native/config.json'])
    files.add(a.output/'literal-equality.json')
    put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(files)]))
    commands={};profiles=[]
    for profile in prepared['profiles']:
        name=profile['profile'];dest=a.output/name;dest.mkdir()
        command='python -B tools/audit/final_bill_lance_combined_run_v1.py --ready "'+dest.as_posix()+'" --profile '+name+' --native-grant'
        put(dest/'manifest.json',json.loads((a.output/'manifest.json').read_text()))
        proof=prepared|dict(profiles=[profile],manifest_sha256=sha(dest/'manifest.json'),bindings=len(files),
            prepared=True,native_run=False,native_granted=False,automatic_next_profile=False,maximum_owned_workers=1,global_maximum_workers=2,
            commands={name:command},source_files=871,complete_target_source_manifest_sha256=sha(PARENT/'source-manifest.json'),
            actual_additive_HUD_compiled_calls=96,actual_additive_HUD_controls_sha256=sha(controls),
            literal_equality_sha256=sha(a.output/'literal-equality.json'),original_3b_results_not_transferred=True,
            source_component_9d_only='Separate920binding CPU/layout/cost receipt; no standalone9d native. This is a newcombined native qualification.',
            new_HUD_scope='Actual helper112/16 and full twelve source OAM fields at100..123/y1..16 for every upgraded case. Original controller/outcome/caps/hardware guards literal.',
            freeze_tool_sha256=sha(__file__))
        put(dest/'proof.json',proof);put(dest/'command.json',dict(command=command))
        profiles.append(dict(profile=name,readiness=str(dest/'proof.json'),readiness_sha256=sha(dest/'proof.json'),manifest_sha256=sha(dest/'manifest.json'),bindings=len(files),command=command))
        commands[name]=command
    put(a.output/'proof.json',dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,source_files=871,
        profiles=profiles,unchanged_native_v3_and_typed_original_host_collector=True,actual_HUD_observer_CPU_calls=96,
        shared_manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),maximum_launches_per_separate_grant=1,automatic_next_profile=False,
        maximum_owned_workers=1,global_maximum_workers=2,scope='PREPARE_ONLY; no combined native evidence or adoption. NewROM/hook/source metadata plus one read-only HUD observer. Original physical-grant/use/controller/source/hardware/cadence/caps unchanged.'))
    put(a.output/'commands.json',commands)
    print(json.dumps(dict(prepared=True,native_run=False,proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),profiles=profiles)))


if __name__=='__main__':main()
