"""Freeze affirmative source supplement; retain earlier scoped negatives."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'build/bubble-bobble-source-1101-v1'
PIN='37959000690d3f9fe596823fc0910e86b9fc977448779360d523751764248b0c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 domain=O/'current3-domain-rebind.json';publication=O/'publication-CPU-controls.json'
 d=json.loads(domain.read_text());p=json.loads(publication.read_text());assert d['passed']and p['passed']and d['ROM_SHA256']==p['current_ROM_sha256']==PIN
 assert not d['Karnov_unrebound_restore_operands']and d['Karnov_known_source_changes_bound']and d['Karnov_cold_map_art_HUD_exact']
 assert d['native_inherited_writes_exact']==816 and sum(x['writes']for x in d['private_image_write_bindings'])==15 and len(d['current_table_bindings'])==44
 assert len(d['menu_states'])==92 and d['WWF_runtime_PRG96_and_metadata_current_exact']and d['WWF_zero_carrier667_retained']
 assert p['no_proposed_page_published']and p['actual_typed_setter_instruction_cuts']==2160 and p['actual_native_Mario_menu_clear_restore_cuts']==2376
 targets=set(d['proposed_code']+d['proposed_art']);assert targets==set(map(int,p['unpublished_transient_proposed_pairs']))
 rom=R/'build/excitebike-pose-1101-v3/current3.nes';raw=rom.read_bytes();assert sha(rom)==PIN
 manifest=R/'build/mario-tank-visible-host-1101-v5/candidate-patches.json';m=json.loads(manifest.read_text());patch=next(x for x in m['patches']if x['owner']=='MtFreshV5')
 after=bytes.fromhex(patch['new_hex']);at=patch['file_offset'];assert raw[at:at+len(after)]==after
 graft=R/'build/mario-tank-visible-host-1101-v5/graft-assembly.json';g=json.loads(graft.read_text());lease=next(x for x in g['source_owner_intervals']if x['name']=='MT_CONTACT')
 blob=R/'build/mario-tank-visible-host-1101-v5/MT_CONTACT.bin';assert sha(blob)==lease['sha256']
 at=16+78*8192+lease['physical_offset'];assert raw[at:at+lease['used']]==blob.read_bytes()
 body=raw[16+78*8192+0xfd6:16+78*8192+0xffb];assert body==bytes.fromhex('8d6a01a97e8d6c01a9b58d6d01a9d5205a018d6a01a9698d6c01a9bf8d6d01a99f205a0160')
 files=[Path(__file__),domain,publication,rom,manifest,graft,blob,R/'tools/audit/prepare_mario_tank_candidate_1101_v5.py',R/'tools/reference/mario_tank_graft_1101_v5.inc',R/'tools/audit/audit_bubble_bobble_current3_domains_1102_v3.py',R/'tools/audit/check_bubble_bobble_current3_publication_1102_v3.py']
 q=dict(passed=True,ROM_SHA256=PIN,source_supplement=True,prior_scoped_negative_receipts_retained=True,existing_candidate_consumer_closure=True,remaining_existing_finite_publishers=0,complete_new_BubBob_transport=False,resource_granted=False,proposed_code_pages=d['proposed_code'],proposed_art_pages=d['proposed_art'],preimage_SHA256=d['preimage_SHA256'],Tank_restore_source_binding=dict(original_call='D5:B57E genuineThSceneInit',current_call='CE:AFD6 MtFreshV5',continuation=['D5:B57E genuineThSceneInit','9F:BF69 MtColdLoadV4','RTS'],native_hex=body.hex(),source_files=['tools/audit/prepare_mario_tank_candidate_1101_v5.py:26','tools/reference/mario_tank_graft_1101_v5.inc:3'],source_owner_interval=lease),proof_counts=dict(current_tables=44,actual_menu_states=92,actual_newer_cold_map_rows=30,inherited_native_writers=816,inherited_private_writers=15,replaced_Karnov_writers=14,typed_setter_cuts=2160,native_menu_cuts=2376,actual_NMI_RTI_returns=4575),conditional_RAM=dict(code_bank=3,code_body_half_open=[0xa000,0xbfe0],state_bank=2,state_half_open=[0xc000,0xc400],owner_headers=[[0xbfe0,0xbff0],[0xdfe0,0xdff0]],unconditional_RAM=False,granted=False,conditions=['Authenticate own complete code/state headers before any mapped call.','Retire previous owner before copy/zero/header writes.','Cold source reads only under existing forced-blank commit rules; publish complete owner headers last.']),remaining_new_owner_work=['Resident loader/authentication/two-header transition/routing has no source-funded grant or implementation.','No rawID/menu/base-slot grant; new fifth-row base family required, no replacement of an existing family.','Compile/measure remaining update/camera glue and qualify actual owner-specific birth/AI/body-contact ingresses.','No Bub/Bob Main/IRQ/native emulator/full1-1 or actual audio qualification.'],scope='Candidate-specific finite existing-consumer closure for these nine physical pages on exact379590, with actual publisher/lag-NMI protocol cuts and explicit source-domain constructors. This affirmative supplement closes the earlier domain receipt stale prose about three Tank retarget operands; that negative artifact is retained. No allocation, new-loader/retirement/admission, arbitrary corrupt-state, hardware or full game proof.',bindings={x.relative_to(R).as_posix():sha(x)for x in files})
 path=O/'current3-closure-supplement.json';path.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,receipt=path.relative_to(R).as_posix(),receipt_SHA256=sha(path),remaining_existing_finite_publishers=0,resource_granted=False)))


if __name__=='__main__':main()
