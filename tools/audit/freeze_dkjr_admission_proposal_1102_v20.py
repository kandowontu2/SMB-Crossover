"""Freeze the measured DK Jr proposal and its exact direct compact inputs.

This is an audit snapshot, not a qualified native candidate or an allocation.
No ROM, large debug data, emulator capture or historical tree is archived.
"""
import json,re,zipfile
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O


def main():
    parent=A.BASE.read_bytes();assert A.sha(parent)==A.PIN
    bbpath=R/'build/bub-menu-candidate-1102-v2/combined-current-landing.json';bb=json.loads(bbpath.read_text());current=bytearray(parent)
    for row in bb['patches']:
        at=row['offset'];old=bytes.fromhex(row['old']);new=bytes.fromhex(row['new']);assert current[at:at+len(old)]==old;current[at:at+len(new)]=new
    current=bytes(current);installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    assert A.sha(current)==bb['expected_rebased_ROM_sha256']=='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'
    assert installed==current
    receipts=['admission-proposal-v11.json','hit-freeze-v12-CPU.json','carrier-proposal-v13.json','publication-v14-CPU.json','native-pause-v16-CPU.json','menu-proposal-v17.json','retirement-proposal-v18.json','menu-name-proposal-v19.json']
    proof={name:json.loads((O/name).read_text())for name in receipts};assert all(q['passed']for q in proof.values())
    # Current delivered change only ownsBB301/666+cookie. Its entire finite
    # carrier/domain instruction/table evidence remains identical to16a9.
    carriers=proof['carrier-proposal-v13.json'];unchanged=[]
    for row in carriers['preimages']:
        at=row['offset'];assert A.sha(current[at:at+1024])==row['SHA256'];unchanged.append(row['page'])
    for row in bb['patches']:assert row['role'].startswith('Existing ')
    prince=R/'build/prince-actor-1101-v1/native-manifest-v65.json';pr=json.loads(prince.read_text());assert pr['expected_memory_only_SHA256']=='da4a84baf1d98e6748b80c25ba5f62e14e739c3b10c10eb83c948c778e044d05'
    # Flatten exact proposed shared/menu spans against the actual9cf image.
    # Prince-only payload/gates are explicitly an external pending prerequisite;
    # they are not silently folded into a raw40 native admission image.
    spans=[]
    def span(bank,pc,data,role,source_basis):
        at=16+bank*8192+pc-0xa000;old=current[at:at+len(data)]
        spans.append(dict(physical_PRG=bank,CPU_half_open=[pc,pc+len(data)],offset=at,old=old.hex(),new=data.hex(),role=role,original_owner_and_funding=source_basis,granted_for_DK=False))
    span(65,0xa740,(O/'retire-selector-v18.bin').read_bytes(),'Four-owner selector including proposed40','Existing source-owned178B selector extent before exactA7F2 typed row37. Factor eight long rejects to local JMP; add owner/cookie/descriptor. No use of typed A7F2.')
    frame=(R/'build/prince-actor-1101-v1/shared-frame-v22.bin').read_bytes();assert len(frame)==123
    span(65,0xaaf7,frame,'Pending granted Prince shared transport prerequisite, unchanged by DK proposal','Exact source-funded shared-frame-v22, grant prince-shared-successor-1102-v30; not new DK funding.')
    span(65,0xab72,(O/'retire-extra-v18.bin').read_bytes(),'Four-owner typed cold/retire tables and Prince cookie','Existing98B source-funded privatePrince extra extent. Factor old30B repeated PrRetire into common loop, reuse actual tables and add native DK pause thaw callback; explicit Ex37 Cset repair.')
    span(65,0xae00,(O/'retire-owner-v18.bin').read_bytes(),'Four-owner cold/auth/retire manager','Existing531B source-owned manager. Factor repeated full header/retire operations; main executed highwater B004 then15B explicit padding toB013. No FF-based expansion.')
    menu=bytearray(current)
    for key in ['menu-proposal-v17.json','menu-name-proposal-v19.json']:
        for row in proof[key]['patches']:
            at=row['offset'];old=bytes.fromhex(row['old']);new=bytes.fromhex(row['new']);assert menu[at:at+len(old)]==old;menu[at:at+len(new)]=new
    # Coalesce the overlapping source-funded menu successor into direct patches.
    i=0
    while i<len(menu):
        if menu[i]==current[i]:i+=1;continue
        start=i
        while i<len(menu)and menu[i]!=current[i]:i+=1
        bank=(start-16)//8192;pc=0xa000+(start-16)%8192
        spans.append(dict(physical_PRG=bank,CPU_half_open=[pc,pc+i-start],offset=start,old=current[start:i].hex(),new=bytes(menu[start:i]).hex(),role='Focused DK/Jr frontend successor actual changed run',original_owner_and_funding='v17 navigation210/214; publicAltTail17 with relocatedCold; source codec146B declaredEA tail and oldtoggle66; actual QueueSelection3B gate with copied original18B continuation',granted_for_DK=False))
    # No proposed span may touch delivered Sunny or live Bub carriers; BBcookie
    # is deliberately relinked as manager data, with its exact9cf value retained.
    q18=proof['retirement-proposal-v18.json'];assert q18['reference_private_Bub_SHA256']==A.sha(current)
    sprite_cookie=bytes.fromhex(next(x['new']for x in bb['patches']if len(bytes.fromhex(x['new']))==16))
    assert (O/'retire-owner-v18.bin').read_bytes().count(sprite_cookie)==1
    source_files=[R/'tools/audit'/name for name in ['measure_dkjr_admission_1102_v11.py','check_dkjr_hit_freeze_1102_v12.py','audit_dkjr_carriers_1102_v13.py','check_dkjr_carrier_publication_1102_v14.py','measure_dkjr_retirement_1102_v15.py','check_dkjr_native_pause_1102_v16.py','measure_dkjr_menu_1102_v17.py','rebind_dkjr_retirement_1102_v18.py','measure_dkjr_menu_name_1102_v19.py','freeze_dkjr_admission_proposal_1102_v20.py']]
    generated=receipts+['resource-menu-v13.json','native-body-v10.s','native-body-v10.bin','native-body-v10-layout.json','admission-owner-v11.s','admission-owner-v11.bin','admission-owner-extra-v11.bin','admission-owner-v11.lbl','admission-selector-v11.s','admission-selector-v11.bin','admission-cold-v11.s','admission-cold-v11.bin','admission-cold-v11.lbl','native-pause-v16.s','native-pause-v16.bin','native-pause-v16.lbl','retire-owner-v18.s','retire-owner-v18.bin','retire-owner-v18.lbl','retire-extra-v18.bin','retire-selector-v18.s','retire-selector-v18.bin','retire-selector-v18.lbl','menu-nav-v17.s','menu-nav-v17.bin','menu-nav-v17.lbl','menu-alt-v17.s','menu-alt-v17.bin','menu-toggle-v17.s','menu-toggle-v17.bin','menu-name-v19.s','menu-name-v19.bin','menu-name-v19.lbl','menu-name-extra-v19.bin']
    direct=[O/x for x in generated]+[bbpath,prince,R/'build/menu-family-root-candidate-1102-v1/producer-snapshot.py',R/'build/menu-family-root-candidate-1102-v1/family-v18-toggle.s',R/'build/bub-menu-navigation-1102-v1/proposal.json',R/'build/prince-actor-1101-v1/collision-owner-v59.s',R/'build/prince-actor-1101-v1/collision-owner-v59.lbl',R/'build/prince-actor-1101-v1/shared-frame-v22.s',R/'build/prince-actor-1101-v1/shared-frame-v22.bin']
    paths=sorted(set(source_files+direct));archive=O/'admission-proposal-v20-inputs.zip';members=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for path in paths:
            data=path.read_bytes();rel=path.relative_to(R).as_posix();z.writestr(rel,data);members.append(dict(path=rel,bytes=len(data),SHA256=A.sha(data)))
    assert archive.stat().st_size<512000
    manifest=dict(passed=True,status='FROZEN_RESOURCE_AND_SOURCE_MEASUREMENT_PROPOSAL_NOT_NATIVE_ADMISSION',ROM_written=False,shared_source_written=False,installed_changed=False,native_candidate_complete=False,base_ROM_SHA256=A.sha(current),source_parent_SHA256=A.PIN,pending_Prince_input_SHA256=pr['expected_memory_only_SHA256'],pending_Prince_warning='v65 exact source/payload only. Prince owner is separately measuring SMC0179/deferred-death successor. Any new fingerprint requires a distinct rebind before composition; no latest-source alias.',
        requested_resources=dict(raw_identity=40,slot27_DK28_Select_alternate=True,focused_only=True,code_pages=A.CODE,art_and_helpers=A.ART,code_RAM3_half_open=[0xa000,0xbfe0],mutable_state_RAM2_half_open=[0xc000,0xc900],immutable_RAM2_half_open=[0xd000,0xd800],headers=[0xbfe0,0xdfe0],shared_clock_retained=[0xdfd0,0xdfd3],conditional_lifetime='Exclusive only after authenticating both full headers, retiring every prior owner before overwrite, forcedblank/disabledNMI/IRQ copy/verify, final byte0 commit last. No unconditional RAM or public/menu grant inferred.'),
        actual_assembly=dict(source_body_bytes=7848,source_body_end=0xbea8,source_body_header_spare=312,public_vector_bytes=114,public_vector_compiled=False,body_plus_vector_projection=7962,remaining_projection=198,private_cold_bytes=119,private_cold_span=[0xd25e,0xd2d5],native_pause_bytes=286,native_pause_span=[0xd540,0xd65e],native_pause_state=[0xc440,0xc457],manager_bytes=531,manager_end=0xb013,manager_executed_end=0xb004,extra_bytes=92,extra_end=0xabce,selector_bytes=175,selector_end=0xa7ef,source_created_shared_spare=dict(main=15,extra=6,selector=3,total=24),menu_nav_used=210,menu_nav_extent=214,menu_toggle_bytes=75,menu_own_queue_gate_bytes=53,menu_own_name_bytes=70,menu_spare_bytes=11),
        art_remaining='Qualified body1408B+fallfruit192B+hit128B=1728B. Source hangingfruit192B/points<=256B still need final typed tile-index closure/native OAM. Three proposed art/helper pages permit measured cold/pause code without truncating source moves; final all-art/native helper layout/cookie is not frozen.',
        publication='v13 finite source domains exact; v14 actual2640setter+2376menu cuts and5057 real lagNMIreturns publish no target page. All eleven carrier preimages remain exact in delivered9cf. This does not qualify the changed owner/cold/retirement/public frames.',
        menu_policy='Select toggles28/40 both ways; focused resolver retains40, Start/A retain highlighted40. Leaving roster focus may resettoDK. Initial Jr uses deliberate shared native DK family portrait with distinct DONKEY KONG JR label. Gameplay life/stage/game-select identity closure remains pending.',
        hit_pause='v16 pure private leaf holds genuine live native flags with TimerControl and self-secondary only empty slots; exact60D1AE updates, cannon spawn/countdown and enemy motion proof passes. v12 all-secondary wrapper is superseded and must not ship as a fullfreeze. Native FrameCounter/jumpcoin/firebar frame animation remains nativepause host-effect adaptation.',
        remaining_required=['Compile genuine38entry public service vector and native Fresh/Scene/Main/Graphics/colors/status/contact/pickup/shot/body/head/side routes; direct source leaves are not functional public rows.','Earned capture Main must retain its normal fruit/clock and native AI pass before the following60D1AE updates; close actual full world order, platforms/firebar/hammer/body art.','Close actual nested Engine9 powerup completion and scene/death/retirement pipelines; current v16 proves typed direct state cancellation, not whole native lifecycle.','Full changed four-owner dispatcher/auth/copy/retire IRQ/lagNMI cuts, liveSMC/AXYP/caller/table/indirect reader closure. Existingv14 only covers unchanged publication protocol.','Final complete body/fruit/points CHR readers, bounded native OAM, helpers/constructor physical layout and full payload-derived two-header cookie; current DK cookie is an explicit placeholder.','Rebind pending Prince successor before any combined image or grant; retain delivered9cf301/666 and label-bound BBcookie plus Sunnyfive patches exactly.','Root grants and actual native cold/gameplay/1-1 qualification; no emulator or install by helper.'],
        proposed_shared_and_menu_patches=spans,unchanged_delivered_target_pages=unchanged,archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,archive_SHA256=A.sha(archive.read_bytes()),members=members,source_files=[dict(path=p.relative_to(R).as_posix(),SHA256=A.sha(p.read_bytes()))for p in source_files],receipts={name:A.sha((O/name).read_bytes())for name in receipts})
    (O/'admission-proposal-v20.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k]for k in ['passed','status','base_ROM_SHA256','archive','archive_bytes','archive_SHA256','actual_assembly']}))


if __name__=='__main__':main()
