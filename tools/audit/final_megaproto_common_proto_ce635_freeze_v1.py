"""Compact ProtoHard14 SOURCE-only checkpoint; never launches an emulator."""
from pathlib import Path
import argparse, hashlib, json, shutil
from final_megaproto_common_proto_ce635_prepare_v1 import D,R,CAND,SHA,RUN
from final_item_abilities_remaining731_run_v1 import verify_manifest
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def bind(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    ready=a.ready;r=json.loads((ready/'proof.json').read_text());count=verify_manifest(ready/'manifest.json')
    assert r['prepared'] and not r['native_run'] and not r['native_granted'] and r['ROM_sha256']==SHA
    assert r['profile']=='proto-hard-common' and r['mode_value']==r['variant']==1 and r['maximum_cases']==14
    assert not(ready/'native/launch.json').exists() and not(ready/'ROOT-grant.json').exists()
    own=json.loads((ready/'fresh-owner-controls.json').read_text());render=json.loads((ready/'fresh-render-controls.json').read_text());release=json.loads((ready/'fresh-release-controls.json').read_text());lu=json.loads((ready/'fresh-Lua-controls.json').read_text())
    summary=dict(passed=True,source_only=True,native_run=False,native_grant=False,ROM_sha256=SHA,
                 profile='proto-hard-common',mode_value=1,variant=1,source_inputs=871,ready_bindings=count,
                 deliberate_config_delta={'identity.variant':[0,1]},native_body_after_config_literal=True,
                 all14_case_plans_controller_seeds_caps_guards_and_finalizers_literal=True,
                 complete_UI_primary_Special_owner_cells=own['complete_owner_cells'],
                 complete_selection_cycles=len(own['selection_cycles']),
                 complete_render_components=len(render['components']),
                 complete_UI_Proc_Motion_Release_cases=release['complete_UI_Proc_Motion_Release_cases'],
                 Lua_art_models=len(lu['art']['models']),complete_Lua_setups=lu['complete_setup']['complete_declared_component_setups'],
                 Lua_release_models=lu['full_release_callback']['models'],
                 Lua_cold_readback_negative_controls=len(lu['cold_readback_negatives']),
                 static_callbacks=74,dispatcher_last=True,three_inactive_frames=True,
                 ordered_collector_unchanged=True,all_prior_Mega_native_FALSEs_and_hashes_preserved=True)
    put(a.output/'source-summary.json',summary)
    put(a.output/'preparation-drafts.json',dict(native_launches=0,source_only=True,drafts=[
        dict(directory=str(D/'currentce635-proto-common-ready-v1'),reason='Trace owner inventory omitted RosterOamReady; actual rotation was 1. Add genuine compiled trace names before asserting recorded entry.'),
        dict(directory=str(D/'currentce635-proto-common-ready-v2'),reason='New mock export executed outside generated local C/setup/menu scope. Move mock-only exports into the same source chunk.'),
        dict(directory=str(D/'currentce635-proto-common-ready-v3'),reason='Wrong-readback negative entered unchanged failure writer; mock intentionally prohibited synthetic PPU capture and masked the expected assertion.'),
        dict(directory=str(D/'currentce635-proto-common-ready-v4'),reason='Same mock error now logged concretely: No synthetic PPU outcome. Empty host-only buffer permits the original owner/mode assertion to propagate; no pixels count as evidence.')],native_controller_or_game_changes=False))
    report=R/'docs/qa/final-megaproto-common-proto-ce635-source-2026-10-26.txt'
    report.write_text('\n'.join([
        'Proto Man Hard: fourteen common-special SOURCE readiness',
        '26 October 2026. Exact private ROM '+SHA+'.',
        '',
        'Prepared only: no native grant or launch. Same ce635 source and actual 871-file inventory as the passing MegaHard14 packet. No production/default/settings/Git change. Mega final proof 55ce2d5c410cf046c3f464524d93f30204f1c2bb12f7ec72d9cc61d5b975886b and all older FALSEs remain immutable.',
        '',
        'Only native configuration change: identity.variant 0 -> 1. Character/owner 1, inventory base 16, ammo indices 17..23, numeric Hard 1, fourteen plans, every resource/actor/terrain seed, controller interval, caps, source hooks, body/shot metadata and all guards/finalizers remain literal. The Lua body after its configuration prefix is byte-for-byte identical. Family megaman names the shared mechanics, not a mistaken display identity. Native startup uses the original Select policy to choose Proto Man; no ProtoVariant/SelectedCharacter/mode/InvSelected write is added.',
        '',
        'Fresh compiled full CrossoverMenuInput Select toggles 0->1 and 1->0, QueueSelectName yields the actual sixteen-tile PROTO MAN row, and PlayerGfxHandler -> SamusFreezeDrawAll reaches the genuine rotated RosterOamReady owner. Every special HUD name/cost/icon and art record was reread from the actual linked ROM and remains identical to the Mega common-special metadata. This source evidence does not substitute for Proto physical PPU visibility.',
        '',
        f'Fresh source controls: {summary["complete_UI_primary_Special_owner_cells"]} complete UI/primary/Special cells for variant 1, both facings and funded/underfunded/full-pool states; {summary["complete_selection_cycles"]} common-only cycles; {summary["complete_render_components"]} full render components including genuine RgSlot and foreign AvSlot exclusion; {summary["complete_UI_Proc_Motion_Release_cases"]} complete direct PHARAOH owner/return cases. Library scene seed parameterization sets only ProtoVariant=1 for SelectedCharacter=1 and asserts it at every full gateway entry/return; compiled instructions and expected source cost/contact/art policies are unchanged.',
        f'Actual Lua source models: {summary["Lua_art_models"]} immediate art/return/rejection observations, {summary["complete_Lua_setups"]} complete boundary setups, {summary["Lua_release_models"]} direct-release callbacks, actual menu Select-vs-confirm inputs, one correct cold readback and {summary["Lua_cold_readback_negative_controls"]} wrong variant/mode/owner rejections. Mock helper exports share the real generated local scope. All 74 callbacks register at startup; the final range dispatcher remains last; three inactive start/end frames add no registration or observation writes. Model-only memory seeds and the empty rejection capture are not claimed native/PPU output.',
        '',
        'The one-shot runner reverse-normalizes exactly to the passing ce635 Mega runner after only its profile/docstring/required-variant changes. The ordered refusal/pool/cleanup collector is the same proven module. Raw emptyChecked reset fields remain retained; no historical collector FALSE or summary is rewritten. Physical E3 encoding applies only to hardware attribute bytes; every unmasked source/publication/input byte, destination ordinal, complete256 E008 protocol, rendering-off, scoped deadline, CHR, IRQ31, 5SMC, banks, stack and APU assertion remains literal.',
        '',
        'Fresh isolated runtime copies bind actual Mesen/core/settings/Python/Lua inputs and current user settings as context without modifying them. Hardware eight-sprite limit, adaptive-off, runahead 0, AllZeros/nonrandom/no-save command overrides and original host 1800 / emulated caps remain. A readiness packet is not permission to run; ROOT must grant a single attempt. No retry or next profile is authorized.',
        '',
        'B-only controlled inventory/stock/pool/terrain/target setup, not physical acquisition. ARM/METAL/KNUCKLE/PHARAOH/KICK/FLAME/WATER both facings only. Default buster, Rush, passives, Easy, physical item delivery, star/1-up, campaign, all-pixel/source-art fidelity, waveform identity, global NMI/DMC/FPS and body-flicker closure remain separate. No native coverage is inferred from shared source or the prior Mega run.',
        '',
        'Readiness: '+str(ready/'proof.json'),
        'Stable one-shot command (NOT GRANTED):',r['stable_command'],
        'Source-only draft errors are preserved and classified in preparation-drafts.json; none launched an emulator.',
    ])+'\n',encoding='utf-8')
    cp=R/'docs/qa/checkpoints/2026-10-26/currentce635-proto-common-source-v1';cp.mkdir(parents=True,exist_ok=False)
    for src,name in [(ready/'proof.json','readiness.json'),(ready/'identity-delta.json','identity-delta.json'),(ready/'literal-invariants.json','literal-invariants.json'),(ready/'runner.patch','runner.patch'),(a.output/'source-summary.json','source-summary.json'),(a.output/'preparation-drafts.json','preparation-drafts.json')]:shutil.copy2(src,cp/name)
    (cp/'README.txt').write_text('SOURCE and mocks only. Exact ce635 ProtoHard14; only native config identity.variant changes from passing MegaHard14. Original body/controller/guards and ordered collector remain. No launch/grant/adoption/acquisition claim. Raw source/runtime/models remain externally hash-bound; prior results unchanged.\n',encoding='utf-8')
    refs=[Path(__file__),R/'tools/audit/final_megaproto_common_proto_ce635_prepare_v1.py',RUN,report,CAND/'proof.json',CAND/'source-manifest.json',ready/'proof.json',ready/'manifest.json',D/'currentce635-mega-common-final-v1/proof.json',D/'currentce635-mega-common-final-v1/manifest.json']+[q for q in ready.iterdir()if q.is_file()]+[ready/'native/run.lua',ready/'native/config.json',a.output/'source-summary.json',a.output/'preparation-drafts.json']
    put(cp/'external-bindings.json',dict(bindings=[bind(q)for q in sorted(set(refs),key=str)]));put(cp/'manifest.json',dict(bindings=[bind(q)for q in sorted(cp.iterdir())if q.is_file()]));size=sum(q.stat().st_size for q in cp.iterdir()if q.is_file());assert size<1024*1024
    owned={q for q in refs if str(q).startswith(str(R))}|set(cp.iterdir());put(a.output/'owned-files.json',dict(bindings=[bind(q)for q in sorted(owned,key=str)]));refs+=list(cp.iterdir())+[a.output/'owned-files.json'];put(a.output/'manifest.json',dict(bindings=[bind(q)for q in sorted(set(refs),key=str)]));count=verify_manifest(a.output/'manifest.json')
    put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,native_grant=False,ROM_sha256=SHA,profile='proto-hard-common',mode_value=1,variant=1,cases=14,ready_sha256=sha(ready/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=count,owned_list_sha256=sha(a.output/'owned-files.json'),owned_files=len(owned),checkpoint_bytes=size,report_sha256=sha(report),all_prior_Mega_proofs_unchanged=True,stable_command=r['stable_command']))
    print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),owned_list_sha256=sha(a.output/'owned-files.json'),owned_files=len(owned),checkpoint_bytes=size),indent=2))
if __name__=='__main__':main()
