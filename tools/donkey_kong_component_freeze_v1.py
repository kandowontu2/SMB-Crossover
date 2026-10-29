"""Freeze the working DK leaf implementation and honest remaining host requirements."""
from pathlib import Path
import json
import subprocess
import sys
from donkey_kong_component_controls_v1 import ROOT,OUT,bind


def main():
    hp=OUT/'handoff.json'
    assert not hp.exists(),'Frozen units require successors'
    build=json.loads((OUT/'build-proof.json').read_text())
    control=json.loads((OUT/'controls.json').read_text())
    assert control['passed'] and control['candidate']['sha256']==build['candidate']
    for row in control['bindings']:
        assert bind(row['path'])['sha256']==row['sha256']
    for p,h in build['actual_dependencies'].items():
        assert bind(p)['sha256']==h,p
    report=ROOT/'docs/qa/donkey-kong-component-progress-2026-10-29.json'
    assert not report.exists()
    data=dict(status='Original DK leaf implementation assembled and tested; host admission remains open',
        native_run=False,playable_build_promoted=False,
        candidate=bind(OUT/'candidate.nes'),build=bind(OUT/'build-proof.json'),controls=bind(OUT/'controls.json'),
        sizes=build['sizes'],
        authored_playable_rules=dict(movement='Genuine native SMB Mario movement; original DK is an NPC, so no original playable DK physics exists.',
            attack='FreshB performs a24-update pickup/hold/toss using original poses; publishes one barrel at16. ReleaseB to throw again.',
            mushroom='Earned protection/tier and second simultaneous rolling barrel.',
            flower='Third simultaneous barrel and Down+B straight vertical drop.',
            persistence='Explicit exact-raw activation constructor before overlay reads; same-life loaded scenes/extra lives preserve tiers, actual life loss clears.',
            animation='Authored waddle from authentic pickup/toss poses with facing correction. No original NPC walking animation is claimed.'),
        authentic=dict(body='Nine original48x32 records;18 actual emitted original-pixel raster comparisons across both facings.',
            barrels='Six original16x16 frames.1152 actual CPU comparisons against original DBEE roll animation, both directions/all frames/all six counter phases.',
            body_palette='0F/30/36/06, original BG2 and explicit falling-DK3F1D packet.',
            barrel_palette='0F/06/27/02, original25M sprite3 remapped to native weapon palette1 without color quantization.',
            source_bounds='Original NPC42x32: full48px canvas startsPlayerX-16; collider begins3px inside, so signedleft-13/right29/top0/bottom32.',
            menu='Complete24x16 half-size sample of original48x32 idle; a disclosed menu adaptation, not a cropped sprite.'),
        leases=dict(status='Conditional placement; actual old-owner pointer-consumer closure still required before menu admission',
            CORE='A36B9FD..<BFC0, actual799B, preserves RYU_SIDE_COLD prefix and SCORE_POPUP_COLD BFC0.',
            ART='C12DB13..<E000, actual1142B, preserves original GUEST_GFX prefix.',
            CHR='820..823 exclusive4KB;32/30/22/27 pattern pairs.',
            RAM='Exact raw28-only active5C00..7F. No persistent5F allocation or old inventory-owner indexing.'),
        checks=control['checks'],
        open=['Close legitimate old pointer/record consumers of conditional PRG tails.',
            'Actual raw28/menu27 admission and all shared routes before any old indexed character table.',
            'Apply42px bounds to real enemy/powerup contacts and background side/head/feet/platform collision.',
            'Connect barrel real terrain, eligible enemy HP/kill/slot-reuse receipts, brick/question/debris/score/SFX transactions.',
            'Integrate original DK audio and preserve other characters/native world palettes.',
            'Actual fresh/lives/scene/pipe/vine/spring/flag/death/powerup animation and fullcaller/interrupt tests.',
            'Native normal8sprite OAM/PPU/scroll/1-1 and every earned powerup in both modes.'],
        scope=build['limits'])
    report.write_text(json.dumps(data,indent=2)+'\n')
    files=[ROOT/p for p in ['src/donkey_kong_core.s','src/donkey_kong_render.s','src/donkey_kong_state.inc',
        'tools/prepare_donkey_kong_component_v1.py','tools/donkey_kong_component_controls_v1.py',
        'tools/donkey_kong_component_freeze_v1.py','tools/audit/prepare_original_dk_playable_assets_v2.py',
        'tools/audit/prepare_original_dk_playable_assets_v3.py']]
    files += [report,OUT/'build-proof.json',OUT/'controls.json',OUT/'entrypoint.s',OUT/'smb1base-mmc5-expanded.cfg',OUT/'main.d']
    asset_handoffs=[]
    for version in ['v2','v3']:
        folder=ROOT/('build/dk-playable-assets-'+version)
        asset_handoffs.append(bind(folder/'handoff.json'))
        files += [folder/n for n in ['handoff.json','dk.chr','dk-art.inc','barrels-and-menu.png']]
    bindings=dict(build['actual_dependencies'])
    for row in control['bindings']:
        bindings[row['path']]=row['sha256']
    for p in files:
        bindings[str(p.resolve())]=bind(p)['sha256']
    handoff=dict(status='FROZEN_PRIVATE_DK_LEAF_COMPONENT_HOST_AND_NATIVE_OPEN',
        candidate=bind(OUT/'candidate.nes'),DBG=bind(OUT/'candidate.dbg'),LBL=bind(OUT/'candidate.lbl'),
        MAP=bind(OUT/'candidate.map'),report=bind(report),controls=bind(OUT/'controls.json'),
        asset_handoffs=asset_handoffs,bindings=bindings,
        actual_ASM_dependencies=build['actual_dependencies'],owned_files=[bind(p)for p in files],
        limits=build['limits'])
    hp.write_text(json.dumps(handoff,indent=2)+'\n')
    subprocess.run([sys.executable,'-B',str(ROOT/'tools/audit/checkpoint_roster_component_v5.py'),
        '--handoff',str(hp),'--name','dk-original-playable-leaf-component'],cwd=ROOT,check=True)
    progress=ROOT/'docs/qa/new-character-source-progress-2026-10-28.json'
    state=json.loads(progress.read_text())
    state['DK_original_source']['status']='Authentic original art plus compiled playable leaf implementation. Constructor/tier/throw/barrel/render/palette CPU controls pass. Full host/native admission open.'
    state['DK_playable_component']=dict(handoff=bind(hp),report=bind(report),candidate=build['candidate'],
        checkpoint='checkpoints/2026-10-28/dk-original-playable-leaf-component',native=False,admitted=False)
    progress.write_text(json.dumps(state,indent=2)+'\n')
    public=[p for p in files if p.is_relative_to(ROOT/'src')or p.is_relative_to(ROOT/'tools')or p.is_relative_to(ROOT/'docs')]
    checkpoint=ROOT/'docs/qa/checkpoints/2026-10-28/dk-original-playable-leaf-component'
    public += [progress,checkpoint/'root-review.json',checkpoint/'frozen-source-packet.zip']
    (OUT/'public-stage-files.json').write_text(json.dumps([str(p)for p in public],indent=2)+'\n')
    print(json.dumps(dict(handoff=bind(hp),public_stage_manifest=str(OUT/'public-stage-files.json'))))


if __name__=='__main__':
    main()
