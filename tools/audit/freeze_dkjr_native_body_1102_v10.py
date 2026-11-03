"""Freeze qualified private DK native body/world/victim source and exact limits."""
import json,shutil,zipfile
from pathlib import Path
import prepare_dkjr_native_body_1102_v10 as P
R=P.R;O=P.O;W=P.W


def main():
    body=json.loads((O/'native-body-v10-CPU.json').read_text());victim=json.loads((O/'native-victim-v9-CPU.json').read_text());world=json.loads((O/'native-victim-v9-world-CPU.json').read_text());assert body['passed']and victim['passed']and world['passed']
    for q in [body,victim,world]:
        for rel,sha in q['bindings'].items():assert W.P.sha((R/rel).read_bytes())==sha,rel
    layout=json.loads((O/'native-body-v10-layout.json').read_text());labels=layout['labels']
    source=[R/'tools/audit'/n for n in ['prepare_dkjr_native_fruit_1102_v8.py','check_dkjr_native_fruit_1102_v8.py',
        'prepare_dkjr_native_victim_1102_v9.py','check_dkjr_native_victim_1102_v9.py','prepare_dkjr_native_body_1102_v10.py','check_dkjr_native_body_1102_v10.py','freeze_dkjr_native_body_1102_v10.py']]
    generated=[O/('native-body-v10'+suffix)for suffix in ['.s','.cfg','.bin','.lbl','-layout.json','-CPU.json']]
    generated +=[O/'native-victim-v9-CPU.json',O/'native-victim-v9-world-CPU.json',O/'native-fruit-v8-CPU.json']
    files=source+generated;packet=O/'native-body-v10-qualified.zip'
    with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED,9)as z:
        for p in files:
            item=zipfile.ZipInfo(p.relative_to(R).as_posix(),(1980,1,1,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;z.writestr(item,p.read_bytes())
    checkpoint=R/'docs/qa/checkpoints/2026-11-02/dkjr-native-body-v10'
    contract={
        'DkjrNativePhase':'GameEngine8/Timer0/sourceprofile1/state1..5/CameraReadyD7. Normalized input, actual BlockBuffer/source2hand terrain, current platforms, world fruit/current native victim/source clock/phase/native score and source anchor publication. Public Main/carry/contact/AI ownership unadmitted.',
        'DkjrNativeFruitReset':'Constructor after original actor init/body/native anchor. No fruit placement. Clear source/world fruit availability, source profile1, bind0400source records and sync camera.',
        'DkjrNativeFruitSet':'Xslot0..3,R0/R1worldXlo/hi,R2Y32..200,R3kind0..2; Cset accepted, invalid before private write. Immutable stage placement data not granted.',
        'DkjrNativeFruitProject':'Project up to4world fruits to source7-byte records; visible relativeX0..239 only. Consumption persists across camera exit/reentry.',
        'DkjrNativeShiftCamera':'At most8pixels signed camera delta per call, all64 source OAM cells, hidden cells untouched, repeats idempotent. Larger scripted changes require explicit import/sync.',
        'DkjrNativeCameraSync':'Explicit constructor/scene resync; source physics is not reset.',
        'DkjrNativeImportAnchor':'Explicit script/cold/carry position event. Native relativeX8..231/Y0..224/high1; sourceX=nativeX-8,sourceY=nativeY+15; preserves original phase/fractions.',
        'DkjrNativePublishAnchor':'SourceX0..223/Y15..255 -> currentcamera+sourceX+8/nativeYsource-15. Cset on acceptance.',
        'DkjrNativeRefreshPlatforms':'Actual current native platform bbox recomputation; AXYP/maps/ObjectOffset/R0..7/all33SMC preserved. Ordinary platform positions are not advanced.',
        'DkjrNativeCarryEvent':'Xactualnativeplatformslot0..5, after genuine PositionPlayerOnH/V/SPlat event. Ground translation preserves fractions; air/fall uses original pre-snap fall-distance injury and Land(top-17). Event ingress/sourceDY caller not wired.',
        'DkjrNativeLifeTerminal':'Original CF62 seam. Source5/nativeengine8or0B/once latch -> actual native EndDeath fields(engine6/Timer0), no direct life decrement. Native PlayerLoseLife owns life/checkpoint/gameover.',
        'DkjrNativeLifeReset':'Constructor/reset of exactly-once death handoff latch.',
        'DkjrNativeFruitCollision':'Original fruit C2DD box versus actual current native eligible victim boxes. Positive primary ordinary00..14exceptPodoboo, no defeated/secondary/offpage. Actual nativeShellOrBlockDefeat; native defaultscore popup suppressed; original60-update source hit then source800/1200/1600 award. Positive nativeGoomba fixtures qualified.',
        'DkjrNativeAwardSourcePoints':'Original C61B indexX0..6 -> actual native AddToScore. Preserves AXYP/maps/R0..7/ObjectOffset/all33SMC; native HUD owns score display.',
        'DkjrNativeDrawBody':'Validated4sourceverticalpairs ->4native8x16 cells; cursoraligned4..240 and aligned active rotation only. Stable unbanked ObjectMetasprite0/SmPosePtr always published. No sprite/rotation mask. Native atlas/palette/publicDraw publication pending.'}
    inherited=R/'docs/qa/checkpoints/2026-11-02/dkjr-native-phase-v7/manifest.json'
    q=dict(passed=True,source_only=True,native_playable=False,ROM_written=False,installed=False,archive_bytes=packet.stat().st_size,archive_SHA256=W.P.sha(packet.read_bytes()),
        component_bytes=body['component_bytes'],component_SHA256=body['component_SHA256'],header_reserved_spare=body['header_reserved_spare'],
        base_ROM_SHA256=P.PIN,donor_ROM_SHA256=P.D.SHA,original_credits='Nintendo — original NES Donkey Kong Jr. World Rev1 code/state/controls/animation/CHR.',
        inherited_checkpoint='docs/qa/checkpoints/2026-11-02/dkjr-native-phase-v7',inherited_manifest_SHA256=W.P.sha(inherited.read_bytes()),
        files={p.relative_to(R).as_posix():dict(bytes=p.stat().st_size,SHA256=W.P.sha(p.read_bytes()))for p in files},source_files=[p.relative_to(R).as_posix()for p in source],
        direct_rebuild='Compile archived native-body-v10.s with ca65 -g and ld65 -C native-body-v10.cfg. Exact authoritative source avoids expanded historical dependency restoration.',
        exports={name:dict(CPU_address=labels[name],ABI=abi)for name,abi in contract.items()},
        CPU_checks=dict(world=world['checks'],native_victim=victim['checks'],body=body['checks']),
        measurement_resources=dict(code_half_open=[0xa000,0xa000+body['component_bytes']],header_reserved_at=0xbfe0,code_nominal_pages=8,
            original_state_half_open=[0xc000,0xc800],context_half_open=[0xc800,0xc900],world_records_retyped_within_original_state=[0xc400,0xc439],
            current_qualified_atlas_bytes=1728,body_atlas_bytes=1408,art_nominal_pages=2,service_vector_budget_bytes=114,spare_after_vector_before_remaining_ports=body['header_reserved_spare']-114,
            new_rawID_granted=False,physical_carrier_grant=False,conditional_RAM_grant=False,resident_loader_or_routing_grant=False,public_vector_implemented=False),
        required_native_path=['Grant independent physical code/art payload after actual current publisher/reader audit; no reuse of Bub/Prince carrier reservations.',
            'Fund owner descriptor/authentication/retirement/current-call/actualIRQ/NMI and private cold constructor, without assuming Ex556B is generic.',
            'Compile genuine actual38typed public entries: Graphics/Colors/nativeoriginalStatus+name/Main/Draw/Fresh/Scene/Death/fullbox/head/side/carry/contact/pickup; reject unsupported rows before legacy out-of-range tables.',
            'Finish fruit/hit/points/hanging art/OAM and exact native body palette/background/HUD consumer; current1728B atlas does not close source hanging/point art.',
            'Close global source hit-freeze versus native enemyAI/contact timing. Existing private Main freezes source actor only; no shared AI hook is claimed.',
            'Verify native controls/life/actualhardware cadence and1-1. Original15px jump requires genuine native platform/vine helpers; no helpers placed or named yet.'],
        scope='Qualified private native movement/terrain/vine/platform carry/life/source phase/native score/world fruit/current nativeGoomba victim and source-authentic body pixel leaves. No new shared/ROM/menu/installer writes, public owner/rawID, complete integration fit or native Mesen claim.')
    manifest=O/'native-body-v10-qualified.json';manifest.write_text(json.dumps(q,indent=2)+'\n');checkpoint.mkdir(parents=True,exist_ok=True)
    for src,name in[(packet,'inputs.zip'),(manifest,'manifest.json')]:
        dst=checkpoint/name
        if dst.exists():assert src.read_bytes()==dst.read_bytes()
        else:shutil.copyfile(src,dst)
        assert src.read_bytes()==dst.read_bytes()
    print(json.dumps(dict(passed=True,checkpoint=checkpoint.relative_to(R).as_posix(),archive_bytes=q['archive_bytes'],archive_SHA256=q['archive_SHA256'],component_bytes=q['component_bytes'],git_files=[*q['source_files'],(checkpoint/'inputs.zip').relative_to(R).as_posix(),(checkpoint/'manifest.json').relative_to(R).as_posix()])))


if __name__=='__main__':main()
