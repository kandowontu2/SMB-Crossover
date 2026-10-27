"""Freeze corrected HUD observer readiness and original FALSE; never launch."""
from pathlib import Path
import argparse,json,difflib
from final_bill_lance_combined_prepare_v3 import D,ROOT,PARENT,SHA,sha,put
from final_item_abilities_remaining731_run_v1 import verify_manifest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    prepared=json.loads((a.ready/'proof.json').read_text());assert prepared['ROM_sha256']==SHA and not prepared['native_run'] and prepared['HUD_observer_version']==2
    env_add=a.ready/'environment-addendum-v1';env_proof=json.loads((env_add/'proof.json').read_text())
    assert env_proof['Nes_and_Emulation_dictionaries_identical'] and sha('C:/Mesen2/settings.json')==env_proof['current_user_settings_sha256']==sha(env_add/'current-user-settings.json')
    initial_manifest=json.loads((a.ready/'manifest.json').read_text());assert len(initial_manifest['bindings'])==942
    skipped=[]
    for z in initial_manifest['bindings']:
        f=Path(z['path'])
        if str(f.resolve()).lower()==str(Path('C:/Mesen2/settings.json').resolve()).lower():
            assert z['sha256']==env_proof['old_user_settings_sha256'];skipped.append(str(f));continue
        assert f.stat().st_size==z['bytes'] and sha(f)==z['sha256'],f
    assert len(skipped)==1
    environment=prepared['environment']|dict(user_settings_sha256=env_proof['current_user_settings_sha256'])
    controls=a.ready/'hud-controls-v2/proof.json';cpu=json.loads(controls.read_text());assert cpu['passed'] and cpu['actual_full_RemainingDraw_calls']==96
    own=a.ready/'ownership-controls-v4/proof.json';owner=json.loads(own.read_text())
    assert owner['passed'] and owner['ROM_sha256']==SHA and [owner[k]for k in ['reproduced_original_generated_v1_FALSE_cases','corrected_actual_foreign_caller_cases','successful_pointer_then_foreign_stack_cleanup_cases','genuine_source_CHR_rejection_cases']]==[10,10,10,2]
    verify_manifest(a.ready/'ownership-controls-v4/manifest.json')
    negative=D/'final-bill-lance-combined-ce635-first-false-v1'
    assert not json.loads((negative/'proof.json').read_text())['passed'];verify_manifest(negative/'manifest.json')
    source=json.loads((PARENT/'source-manifest.json').read_text());assert len(source)==871
    for n,h in source.items():assert sha(PARENT/'source'/n)==h,n
    oldroot=D/'final-bill-lance-hard-gallery-ready-v5';prior=D/'final-bill-lance-combined-ce635-ready-v2'
    addon=(ROOT/'tools/audit/final_bill_lance_combined_hud_v2.lua').read_text();beforeaddon=(ROOT/'tools/audit/final_bill_lance_combined_hud_v1.lua').read_text()
    equal=[]
    for profile in prepared['profiles']:
        native=Path(profile['output']);assert not(native/'launch.json').exists()
        before=(oldroot/'profiles'/profile['profile']/'native/run.lua').read_text().split('\n',1)[1]
        after=(native/'run.lua').read_text().split('\n',1)[1]
        assert after.count(addon)==1 and after.replace(addon+'\n','',1)==before
        oldcfg=json.loads((prior/'profiles'/profile['profile']/'native/config.json').read_text());cfg=json.loads((native/'config.json').read_text())
        expected=json.loads(json.dumps(cfg));expected.pop('hud_call_chain');expected['hooks'].pop('RemainingDraw')
        for record in expected['hud_records'].values():record.pop('art')
        # New source-bound RAM metadata may only add AvDrawArt if not previously
        # used, plus RemainingDraw code-address metadata catalogued by the original
        # quoted-symbol preparer. Actual RAM/ROM bytes and old fields stay exact.
        for n in set(expected['ram'])-set(oldcfg['ram']):assert n in ['AvDrawArt','RemainingDraw'];expected['ram'].pop(n)
        assert expected==oldcfg,'Only real HUD caller-chain metadata changed'
        assert (native/'inherited-NMI-stack-APU-guards.lua').read_bytes()==(oldroot/'profiles'/profile['profile']/'native/inherited-NMI-stack-APU-guards.lua').read_bytes()
        equal.append(dict(profile=profile['profile'],original_full_native_v3_controller_and_guards_literal=True,typed_host_collector_unchanged=True,
            cfg_source_only_HUD_ownership_metadata_delta=True,script_sha256=sha(native/'run.lua'),config_sha256=sha(native/'config.json')))
    diff=''.join(difflib.unified_diff(beforeaddon.splitlines(True),addon.splitlines(True),fromfile='frozen-HUD-observer-v1.lua',tofile='HUD-observer-v2.lua'))
    (a.output/'observer-only.diff').write_text(diff,encoding='utf-8')
    put(a.output/'literal-equality.json',dict(passed=True,native_run=False,profiles=equal,
        game_source_and_ROM_unchanged=True,original_FALSE_and_Lance_unrun_retained=True,
        actual96draws_and32ownership_controls=True,no_original_native_oracle_relaxed=True))
    files={Path(z['path'])for z in json.loads((a.ready/'manifest.json').read_text())['bindings']}
    files.update(PARENT/'source'/n for n in source)
    for parent in [negative,a.ready/'hud-controls-v2',a.ready/'ownership-controls-v4']:
        files.update(Path(z['path'])for z in json.loads((parent/'manifest.json').read_text())['bindings'])
        files.update([parent/'proof.json',parent/'manifest.json'])
    files.update([Path(__file__),ROOT/'tools/audit/final_bill_lance_combined_freeze_v3.py',a.ready/'final-freeze-v2/first-freeze-negative.json',env_add/'proof.json',env_add/'current-user-settings.json',ROOT/'tools/audit/final_bill_lance_combined_freeze_v2.py',a.ready/'final-freeze-v1/first-freeze-negative.json',ROOT/'docs/qa/final-bill-lance-combined-hud-ownership-2026-10-26.txt',
        ROOT/'tools/audit/final_bill_lance_combined_false_v1.py',ROOT/'tools/audit/final_bill_lance_combined_hud_v2.lua',
        ROOT/'tools/audit/final_bill_lance_combined_prepare_v3.py',a.ready/'proof.json',a.ready/'manifest.json',
        a.output/'observer-only.diff',a.output/'literal-equality.json'])
    for sub in ['ownership-controls-v1','ownership-controls-v2','ownership-controls-v3']:
        files.update(f for f in(a.ready/sub).iterdir()if f.is_file())
    put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(files)]))
    profiles=[];commands={}
    for profile in prepared['profiles']:
        name=profile['profile'];dest=a.output/name;dest.mkdir()
        command='python -B tools/audit/final_bill_lance_combined_run_v1.py --ready "'+dest.as_posix()+'" --profile '+name+' --native-grant'
        put(dest/'manifest.json',json.loads((a.output/'manifest.json').read_text()))
        proof=prepared|dict(environment=environment,environment_addendum_sha256=sha(env_add/'proof.json'),profiles=[profile],commands={name:command},manifest_sha256=sha(dest/'manifest.json'),bindings=len(files),
            prepared=True,native_run=False,native_granted=False,automatic_next_profile=False,maximum_owned_workers=1,global_maximum_workers=2,
            source_files=871,complete_target_source_manifest_sha256=sha(PARENT/'source-manifest.json'),
            original_machine_FALSE_sha256=sha(negative/'proof.json'),actual96_HUD_calls_sha256=sha(controls),
            actual32_ownership_controls_sha256=sha(own),literal_equality_sha256=sha(a.output/'literal-equality.json'),
            needs_fresh_explicit_profile_grant=True,old_Lance_grant_not_portable=True,freeze_tool_sha256=sha(__file__))
        put(dest/'proof.json',proof);put(dest/'command.json',dict(command=command))
        profiles.append(dict(profile=name,readiness=str(dest/'proof.json'),readiness_sha256=sha(dest/'proof.json'),manifest_sha256=sha(dest/'manifest.json'),bindings=len(files),command=command));commands[name]=command
    put(a.output/'commands.json',commands)
    put(a.output/'proof.json',dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,source_files=871,
        environment_addendum_sha256=sha(env_add/'proof.json'),profiles=profiles,bindings=len(files),shared_manifest_sha256=sha(a.output/'manifest.json'),
        original_machine_FALSE_preserved=True,original_controller_guards_and_typed_host_unchanged=True,
        actual_source_calls=96,actual_ownership_controls=32,maximum_launches_per_separate_grant=1,
        automatic_next_profile=False,maximum_owned_workers=1,global_maximum_workers=2,
        scope='PREPARE ONLY. Read-only HUD ownership correction; actual old FALSE retained. No new native/adoption claim.'))
    print(json.dumps(dict(prepared_only=True,proof_sha256=sha(a.output/'proof.json'),bindings=len(files),profiles=profiles)))


if __name__=='__main__':main()
