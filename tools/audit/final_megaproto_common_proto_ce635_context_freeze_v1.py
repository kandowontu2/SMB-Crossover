"""Publish compact context-role correction; raw human settings stay external."""
from pathlib import Path
import argparse,hashlib,json,shutil
from final_megaproto_common_proto_ce635_context_v1 import D,R,SHA,OLD,NEG,RUN
from final_item_abilities_remaining731_run_v1 import verify_manifest
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def bind(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);ready=a.ready
    z=json.loads((ready/'proof.json').read_text());count=verify_manifest(ready/'manifest.json');diff=json.loads((ready/'human-context-comparison.json').read_text());role=json.loads((ready/'dependency-role.json').read_text())
    assert z['context_only_successor'] and z['all1931_other_inputs_unchanged'] and not z['native_run'] and not z['native_granted']
    assert not(ready/'native/launch.json').exists() and not(ready/'ROOT-grant.json').exists()
    summary=dict(passed=True,source_context_only=True,native_launches=0,ROM_sha256=SHA,profile='proto-hard-common',mode=1,variant=1,cases=14,ready_bindings=count,
                 all1931_other_original_inputs_exact=True,native_body_config_controller_guards_script_exact=True,
                 original_ready_sha256=sha(OLD/'proof.json'),original_prelaunch_FALSE_sha256=sha(NEG/'proof.json'),
                 original_prelaunch_game_failure=False,worker_settings_sha256=z['environment']['worker_settings_sha256'],
                 human_context_snapshot_sha256=diff['snapshot']['sha256'],human_context_runtime_input=False,
                 live_prepost_informational=True,Nes_equal=diff['Nes_equal'],Emulation_equal=diff['Emulation_equal'],
                 all_actual_runtime_inputs_strict=True,all_other_runner_predicates_reverse_exact=True,no_human_file_write=True,
                 no_heavy_CPU_rerun=True,independent_role_proof=role['independent_role_proof'],historical_probe=role['historical_actual_private_setting_probe'])
    put(a.output/'summary.json',summary)
    report=R/'docs/qa/final-megaproto-common-proto-ce635-context-2026-10-26.txt'
    report.write_text('\n'.join([
        'ProtoHard14 ce635: protected GUI context role correction',
        '26 October 2026. Exact private ROM '+SHA+'.',
        '',
        'SOURCE/CONTEXT only. No new native grant or launch. Original readiness 81b25bb24a900b0c5f5ecaa129b86fb62e09dd603e0af55ada2c55a808a685b7 and prelaunch FALSE 63927470f7124ddd2e26197042e230f74d1a721589d586b74cb8103901de03a0 remain unchanged. The command stopped in manifest verification before launch.json, emulator execution or any game assertion. This was not a game failure; no worker was acquired.',
        '',
        'Original GUI watch expected 253026 bytes / 8a439e0a5eeddc2d4776e516aacfc224c03048b9c7d23d9926a463460a7e748a. The actual saved prelaunch snapshot is 253006 bytes / ace939a892f08d12f6a2d6aecf680a1016e59bf2e846c2500a609fc0abf87fcb. Later legitimate GUI saves are separate snapshots; no unavailable full old-file diff is invented.',
        'Fresh captured GUI snapshot: '+diff['snapshot']['sha256']+'. It is immutable external provenance, bound in the new manifest. Current Nes dictionary differences versus the old frozen environment: '+str(len(diff['current_dictionary_differences']['Nes']))+'; Emulation differences: '+str(len(diff['current_dictionary_differences']['Emulation']))+'. Full human settings bytes remain external and are never copied into the public checkpoint.',
        '',
        'Actual dependency role: the profile runner always supplies the explicit private emulator path. run_mesen_isolated forwards it unchanged to tools/run_mesen.py; its environment/PATH/C:/mesen2/Mesen.exe fallback cannot win. Neither Python driver opens or passes C:/Mesen2/settings.json. The historical same-binary private-setting probe records the same host-only callback rejected with a one-second budget and completed with five seconds, demonstrating adjacent private settings consumption. It is reused at its original hash, not rerun or labeled current gameplay evidence. C independently froze this role proof. No OS-wide file-read trace is claimed.',
        '',
        'Runtime remains strict: adjacent private settings SHA627cd9c71a2011b4cf5fb03a0712d4d77f7890bc269b174d5757776034aab715, all emulator/core/support files, original deterministic CLI overrides, eight-sprite hardware limit, adaptive-off, runahead0, AllZeros/nonrandom/no-save, Python/Lua tools, all871 source inputs, ROM/debug/data, native Lua/config/controller/seeds/mechanics/guards/74callbacks/ordered collector. All1931 other original bindings were freshly rehashed exact. No unchanged CPU suites were rerun or awarded new case counts.',
        '',
        'Only functional path rebinding is to a fresh identical private emulator folder and empty evidence output folder. Native Lua and configuration files are copied byte-for-byte. New host runner differs only by docstring and read-only live GUI hash logging before/after execution. Missing/changed live GUI context is informational and cannot alter pass/fail; captured provenance remains strict. Reverse-normalization proves every old collector, native guard, cap, command, runtime dependency predicate and game result condition unchanged. Finite available/missing watch controls pass without settings writes.',
        '',
        'No human settings file was written or restored. The external GUI may legitimately continue saving; its live pre/post hashes are informational. Fresh source-only readiness requires a new ROOT grant before a single attempt. No retry, Hard/Easy/other profile expansion, ROM change or adoption is authorized.',
        '',
        'Readiness: '+str(ready/'proof.json'),
        'Stable command (NOT GRANTED):',z['stable_command'],
        'Original Mega14 proof and all prior source/native/negative packets remain immutable.',
    ])+'\n',encoding='utf-8')
    cp=R/'docs/qa/checkpoints/2026-10-26/currentce635-proto-common-context-v1';cp.mkdir(parents=True,exist_ok=False)
    for src,name in [(ready/'proof.json','readiness.json'),(ready/'context-invariants.json','context-invariants.json'),(ready/'human-context-comparison.json','human-context-comparison.json'),(ready/'runner-context.patch','runner-context.patch'),(ready/'dependency-role.json','dependency-role.json'),(NEG/'proof.json','original-prelaunch-FALSE.json'),(NEG/'other-bindings-proof.json','original-other1931.json'),(a.output/'summary.json','summary.json')]:shutil.copy2(src,cp/name)
    (cp/'README.txt').write_text('Source/context only, zero native launches. Original GUI-watch prelaunch FALSE retained. Captured GUI settings are non-runtime provenance; live hashes informational. All actual private-worker627/runtime/ROM/game/controller/guard inputs remain strict and unchanged. No raw settings or game/capture binaries are included.\n',encoding='utf-8')
    refs=[Path(__file__),R/'tools/audit/final_megaproto_common_proto_ce635_context_v1.py',RUN,report,ready/'proof.json',ready/'manifest.json',ready/'dependency-role.json',ready/'context-invariants.json',ready/'human-context-comparison.json',ready/'runner-context.patch',OLD/'proof.json',OLD/'manifest.json',NEG/'proof.json',NEG/'other-bindings-proof.json',a.output/'summary.json']
    put(cp/'external-bindings.json',dict(bindings=[bind(q)for q in sorted(set(refs),key=str)]));put(cp/'manifest.json',dict(bindings=[bind(q)for q in sorted(cp.iterdir())if q.is_file()]));size=sum(q.stat().st_size for q in cp.iterdir()if q.is_file());assert size<1024*1024
    owned={q for q in refs if str(q).startswith(str(R))}|set(cp.iterdir());put(a.output/'owned-files.json',dict(bindings=[bind(q)for q in sorted(owned,key=str)]));refs+=list(cp.iterdir())+[a.output/'owned-files.json'];put(a.output/'manifest.json',dict(bindings=[bind(q)for q in sorted(set(refs),key=str)]));n=verify_manifest(a.output/'manifest.json')
    put(a.output/'proof.json',dict(passed=True,source_context_only=True,native_launches=0,native_grant=False,ROM_sha256=SHA,ready_sha256=sha(ready/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=n,owned_list_sha256=sha(a.output/'owned-files.json'),owned_files=len(owned),checkpoint_bytes=size,report_sha256=sha(report),all_old_packets_unchanged=True,stable_command=z['stable_command']))
    print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),owned_list_sha256=sha(a.output/'owned-files.json'),owned_files=len(owned),checkpoint_bytes=size),indent=2))
if __name__=='__main__':main()
