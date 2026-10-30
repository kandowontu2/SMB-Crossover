"""Freeze qualified mandatory RCR ink and update the authorized WIP download."""
from pathlib import Path
import json
import runpy
import shutil
import sys

R=Path(__file__).resolve().parents[2]
O=R/'build/required-rcr-ink-shared-v3'
P=R/'build/full-roster-menu-v5/candidate.nes'
ROM=O/'candidate/candidate.nes'
EXPECTED='ec2f23edac3642c2e28acc1d8b6f17ef35063225375f4b4aa50a5f1ff56d6f46'
sys.path.insert(0,str(R/'tools/audit'))
from checkpoint_roster_progress_1030_v2 import save,sha


def main():
    target=R/'docs/qa/required-player-ink-2026-10-30.json'
    assert not target.exists()
    product=json.loads((O/'build-proof.json').read_text())
    assert product['passed']and sha(ROM)==product['ROM_sha256']==EXPECTED
    bindings=dict(product['bindings'])
    source_path=R/'build/required-rcr-ink-v2/controls.json'
    source=json.loads(source_path.read_text())
    assert source['passed']and len(source['actual_original_pixel_pose_pairs'])==144
    assert len(source['actual_complete_Main_pairs'])==24
    bindings.update(source['bindings'])
    native=[]
    for variant,off in [(0,1),(1,1),(0,0),(1,0)]:
        folder=O/f'native/v{variant}-off{off}'
        review=json.loads((folder/'capture-review.json').read_text())
        assert review['passed']and review['evidence_integrity_passed']
        assert review['native']['ROM_sha256']==EXPECTED and review['native']['smoke_active_Main_updates']==100
        assert review['hardware']['variant']==variant and review['hardware']['Shadows_off']==off
        assert review['hardware']['ink_parts']>0 and review['hardware']['palette'][29]==15
        bindings.update(review['bindings'])
        bindings[str(folder/'capture-review.json')]=sha(folder/'capture-review.json')
        native.append(dict(variant=variant,Shadows_off=off,native=review['native'],
                           actual_ink_parts=review['hardware']['ink_parts'],
                           verified_lossless_frames=review['container']['full_frames']))
    assert sum(q['verified_lossless_frames']for q in native)==956
    ar=R/'build/arthur-shadow-ownership-v2'
    assert sha(ar/'handoff.json')=='386b21c62651610460945ee0d3608721421f4864eaa18a740de6c6e7df1dfc72'
    ar_handoff=json.loads((ar/'handoff.json').read_text())
    ar_closure=json.loads((ar/'source-closure.json').read_text())
    for p,h in ar_closure['files'].items():
        bindings[str((R/Path(p)).resolve())]=h
    for name,h in ar_handoff['receipts'].items():
        assert sha(ar/name)==h
        bindings[str(ar/name)]=h
    # Two minimal IPS records, built from the qualified exact-source changes.
    original=P.read_bytes();current=ROM.read_bytes();patch=bytearray(b'PATCH')
    offsets=product['changed_file_offsets']
    for start in [offsets[0],offsets[5]]:
        assert current[start:start+5]==bytes([0xea])*5
        patch+=start.to_bytes(3,'big')+(5).to_bytes(2,'big')+current[start:start+5]
    patch+=b'EOF'
    ips=O/'from-5b09a3ed-to-ec2f23ed-required-ink.ips'
    ips.write_bytes(patch)
    checks=[dict(name='exact_current_parent_source_reproduction',passed=True),
            dict(name='only10qualifiedRCRcodebytes_header_CHR_othercode_symbols_exact',passed=True),
            dict(name='144actual_original_source_pixel_pose_pairs_bothsettings',passed=True),
            dict(name='24actualMain_pairs_all_other_application_live_stack_maps_exact',passed=True),
            dict(name='four_cold_controller_menu_lives_100Main_smokes_bothsettings',passed=True),
            dict(name='956lossless_frames_verified_normal8sprites_no_state_writes',passed=True),
            dict(name='root_viewed_all_four_menu_lives_gameplay_contact_sheets',passed=True)]
    manifest=O/'release-manifest.json';receipt=O/'release-verification.json'
    manifest.write_text(json.dumps(dict(output_sha256=EXPECTED,base_sha256=sha(P)),indent=2)+'\n')
    receipt.write_text(json.dumps(dict(rom_sha256=EXPECTED,checks=checks,passed=True,
        scope='Small RCR ink repair only; Arthur alreadyretains sourceblack independent ofsetting. Arthur crowdedscanline loss and unfinished newhosts are notqualified bythisreceipt.'),indent=2)+'\n')
    skill=Path('C:/Users/kando/.codex/skills/mario-porting/scripts/check_release.py')
    check=runpy.run_path(str(skill))['check_release']
    verified=check(ROM,manifest,receipt,base=P,ips=ips)
    (O/'release-consistency.json').write_text(json.dumps(verified,indent=2)+'\n')
    for path in [Path(__file__).resolve(),O/'build-proof.json',source_path,ar/'handoff.json',ar/'source-closure.json',
                 ips,manifest,receipt,O/'release-consistency.json',skill,
                 R/'tools/audit/prepare_required_rcr_ink_v1.py',R/'tools/audit/prepare_required_rcr_ink_v2.py',
                 R/'tools/audit/prepare_required_rcr_shared_v3.py',R/'tools/audit/required_rcr_ink_controls_v1.py',
                 R/'tools/audit/required_rcr_native_v1.py',R/'tools/audit/review_current_capture_progress_v1.py',
                 R/'build/required-rcr-ink-v1/candidate/compile-log.json']:
        bindings[str(path)]=sha(path)
    save('required-player-ink',dict(status='RCR_REQUIRED_INK_SOURCE_AND_NATIVE_PASS_ARTHUR_ALREADY_UNCONDITIONAL_OVERLOAD_OPEN',
        ROM_sha256=EXPECTED,parent_ROM_sha256=sha(P),changed_bytes=10,
        source_pose_pairs=144,actual_Main_pairs=24,native_smokes=native,
        original_RCR_ShadowOff_missing_opaque_pixels=source['original_ShadowOff_missing_opaque_pixels_range'],
        root_visual_review='Allfour actualnativecontact sheets viewed: eachmenu/lives/body/blackink coherent withbothrealmenuoptions. Sourceartcolor/pose/world intact.',
        Arthur=dict(code_change=False,source_black_pixels_per_option=6672,
                    originalRGB_pose_area_cases_per_option=201,actual_Main_updates_per_option=96,
                    source_and_menu_black_preserved_both_options=True,
                    remaining='Actualcrowd hardware8spriteoverflow: firstrequiredblackpixelOAM59/rank11 atupdate37; independentbody/weaponpriorityworkongoing.'),
        limits=['RCRnative checks are100activeMain smokes, not full1-1/allitems/FPS admission.',
                'Arthur remains pending insharedmenu; sourcegameplay/overflow work isprivate.',
                'No other unfinished character integration is installed.']),bindings)
    downloads=Path('C:/Users/kando/Downloads')
    latest=downloads/'SMB-Crossover-Latest-WIP-MMC5.nes'
    backup=downloads/'SMB-Crossover-Before-Required-Ink-5b09a3ed-MMC5.nes'
    version=downloads/'SMB-Crossover-2026-10-30-Required-Ink-MMC5.nes'
    previous=sha(latest)
    assert previous in [sha(P),EXPECTED], 'Preserve an unexpected newer/user build'
    if not backup.exists():
        shutil.copy2(P,backup)
    assert sha(backup)==sha(P)
    if version.exists():
        assert sha(version)==EXPECTED
    else:
        shutil.copy2(ROM,version)
    if previous!=EXPECTED:
        temp=downloads/'SMB-Crossover-Latest-WIP-MMC5.new-ec2f23ed.nes'
        assert not temp.exists()
        shutil.copy2(ROM,temp)
        assert sha(temp)==EXPECTED
        temp.replace(latest)
    assert sha(latest)==sha(version)==EXPECTED
    final=check(ROM,manifest,receipt,base=P,ips=ips,installed=latest)
    (O/'installed-consistency.json').write_text(json.dumps(final,indent=2)+'\n')
    result=dict(date='2026-10-30',passed=True,installed=True,ROM_sha256=EXPECTED,
                previous_ROM_sha256=sha(P),latest=str(latest),versioned=str(version),backup=str(backup),
                changes=['Alex/Ryan alwayscompose andpublish intrinsicblackink regardless ofShadows.',
                         'Arthur alreadykeeps intrinsicblack independently; sourceproofadded, crowdreadabilitystillopen.'],
                native_runs=4,verified_lossless_frames=956,source_pose_pairs=144,actual_Main_pairs=24,
                same_othercode_header_CHR_and_all_symbol_values=True,
                roster=dict(slots=32,identities=80,ready=47,pending=33),
                checkpoint=str(R/'docs/qa/checkpoints/2026-10-30/required-player-ink/root-review.json'),
                installed_consistency_sha256=sha(O/'installed-consistency.json'),checks=checks,
                limits=['Fullcampaign/everyitem/constant60Hz not claimed.',
                        'Independenthostintegrationbranches not included.'])
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(installed=True,ROM_sha256=EXPECTED,latest=str(latest),verified_frames=956)))


if __name__=='__main__':
    main()
