"""Compact immutable current32slot DK Jr frontend+scene proposal checkpoint."""
from pathlib import Path
import json,zipfile
import rebind_dkjr_current_menu_1103_v6 as C
R,O,sha=C.R,C.O,C.sha


def main():
    names=['prepare_dkjr_current_menu_1103_v1.py','measure_dkjr_current_menu_1103_v2.py','check_dkjr_current_menu_1103_v3.py','measure_dkjr_current_scene_1103_v4.py','audit_dkjr_current_menu_funding_1103_v5.py','rebind_dkjr_current_menu_1103_v6.py','freeze_dkjr_current_menu_1103_v7.py']
    sources=[R/'tools/audit'/n for n in names];receipts=[O/n for n in ['current-input-v1.json','current-menu-v2.json','current-menu-v3-CPU.json','current-scene-v4-CPU.json','current-menu-funding-v5.json','current-current-v6-CPU.json']]
    for p in receipts:
        q=json.loads(p.read_text());assert q['passed']
        for rel,h in q.get('bindings',{}).items():assert sha((R/rel).read_bytes())==h,(p.name,rel)
    before,after,base,scene=C.stage();ui=json.loads((O/'current-menu-v2.json').read_text());final=json.loads(receipts[-1].read_text());assert sha(after['raw'])==final['expected_memory_only_SHA256']
    patches=ui['patches']+[scene];assert all(not(max(a['file_offset'],z['file_offset'])<min(a['file_offset']+len(bytes.fromhex(a['new_hex'])),z['file_offset']+len(bytes.fromhex(z['new_hex']))))for i,a in enumerate(patches)for z in patches[i+1:])
    payloads=sorted(p for p in O.iterdir()if p.suffix in ['.s','.bin','.lbl','.cfg']and not p.name.endswith('.zip'))
    negatives=sorted(p for p in O.iterdir()if p.name.endswith('-negative.json'))
    allfiles=list(dict.fromkeys(sources+receipts+payloads+negatives));assert not any(p.suffix in ['.nes','.dbg','.o','.png']for p in allfiles)
    archive=O/'current-menu-v7-inputs.zip';assert not archive.exists(),'Frozen packet is immutable; use a distinct successor.'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in allfiles:z.writestr(p.relative_to(R).as_posix(),p.read_bytes())
    manifest=dict(passed=True,status='FROZEN_CURRENT32SLOT_FOCUSED_DKJR_SOURCE_PROPOSAL',source_only=True,ROM_written=False,shared_source_mutated=False,menu_admitted=False,native_qualified=False,installed=False,private_menu_scene_grant_required=True,
        current_input_SHA256=base['expected_memory_only_SHA256'],expected_memory_only_SHA256=sha(after['raw']),preserved=['Root116 exact101+83 shared manager/auth and all13complete auth checks','Prince159 +all9exactroot105frontend patches/root113 candidate payload','Currentcf7 Bub initialtier/sourcehead/cookie, Metal,Arthur,Ex,WWF and all foreign carriers','FrozenDK100/109source/archives unchanged; currentprivateDK90code/art/state/header cookie unchanged','Existing32position BG renderer, DKfamily gridicon and nativeplatformactors; no standalone slot or newhelper'],
        proposed_patch_list=patches,requested_menu_source_extents=dict(PRG66_Gate=[0xad3c,0xad79],PRG66_Select_entry=[0xad39,0xad3c],PRG66_Code=[0xb02e,0xb0bf],PRG66_Data=[0xa58b,0xa5b5],PRG124_nav_existing=[0xa000,0xa0d6],PRG124_AltTail_existing=[0xadee,0xadff],other_exact_operands='Flattenedpatchlist; no expanded source footprint.'),requested_scene_operand=dict(PRG65=[0xb01c,0xb01d],old='03',new='04'),
        art=dict(physical_CHR=960,byte_half_open=[256,384],original_pose_tiles=[80,82,84,86],native_cells=4,width=32,height=16,source_opaque_RGB=[48,6,54],new_physical_pages=0,new_CHR_bytes=0,original_credits='Nintendo: original NES Donkey Kong Jr. World Rev1 idle instructions/OAM/pixels/palette.',existing_DK_family_grid_icon_deliberately_shared=True),
        controls=dict(slot=27,old_raw=28,new_raw=40,Select='Actual freshSelectP1 orP2 toggles28<->40; heldSelect stays.',confirm='ActualStart/A and simultaneousSelect+confirm launch highlighted40.',selector_state='ExistingSelectedCharacter only, no new persistent bit/byte.',limitation='Initialfocused-only alternate: leaving rosterfocus may resettoDK; intentional policy approved byroot. Life/respawn/stage/GameSelect must retain40 under eventualnativeowner path, qualification still required.'),
        profile_counts=dict(current_input_unique=93,current_input_machine_states=94,proposed_unique=94,proposed_machine_states=95,claimed_native_selectable_future=False),
        CPU=dict(foreign_confirms=467,navigation=768,cursor=384,constructors=32,own_select_flags_controller_buffer_cases=96,own_Start_A=192,scene_foreign_AXYP_SP_maps_SMC=1530,oldpadding_read_fetch_epochs=json.loads((O/'current-menu-funding-v5.json').read_text())['compiled_finite_UI_instruction_epochs'],actual_InitScreen_cold_then_scene36_then_real_entrance_then_first_GameCore=True,real_HuReset_retirement=True,CrossoverInit_AXYP_state_exact=True,actual128backing_art_bytes_exact=True),
        source_scope_correction='Earlier100/97 scene36direct fixture did not qualify nativeB013 range; frozenreceipts unchanged. Thisproposal adds separateexactexistingCMP3→4 andexecutesrealInitScreen first. V2/v3UI model on6c9e had noDKcarrierpublication; v6rebinding80d3 includes actualsourceportrait bytes.',
        remaining_before_native=['Root exact menu/code/data/operand +B01C range grant; no authorization inferred from existingcarrier orauth116 grant.','Actual newmenu/scene/previous-owner populatedretire/headerpoison/forcedblank/IRQ/FF/nested closure onfinalfingerprints.','Actual coldDK/JrSelectbothways/name/sourceportrait/Start/A/gameplay/respawn/stage/GameSelect underrootMesenqueue.','Realnative1-1 intendedabilities/traversal/lag qualification; only then assess existingnativeplatform helper placement andrecordeveryaffectedalternate/worldcoordinate. Nohelperplacednow.'],
        archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,archive_SHA256=sha(archive.read_bytes()),members=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,SHA256=sha(p.read_bytes()))for p in allfiles],source_files=[dict(path=p.relative_to(R).as_posix(),SHA256=sha(p.read_bytes()))for p in sources],bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [R/'docs/qa/allocations/combined-owner-auth-1103-v116.json',R/'docs/qa/allocations/prince-live-lifetime-1103-v113.json',R/'docs/qa/allocations/prince-current-frontend-1103-v105.json',R/'docs/qa/allocations/dkjr-private-resources-1102-v20.json',R/'docs/qa/allocations/dkjr-shared-gates-1103-v104.json']})
    out=O/'current-menu-v7.json';out.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(dict(passed=True,archive_bytes=manifest['archive_bytes'],archive_SHA256=manifest['archive_SHA256'],members=len(allfiles),source_files=len(sources),current_input_SHA256=manifest['current_input_SHA256'],expected_memory_only_SHA256=manifest['expected_memory_only_SHA256'],flattened_patches=len(patches),explicit_commit_paths=[p.relative_to(R).as_posix()for p in sources])))


if __name__=='__main__':main()
