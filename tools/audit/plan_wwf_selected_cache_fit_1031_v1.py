"""Concrete read-only WWF storage/state plan; no resource acquisition or port."""
from pathlib import Path
import hashlib,json,re,zipfile
R=Path(__file__).resolve().parents[2];O=R/'build/wwf-selected-cache-fit-1031-v1'
J=R/'build/bt-ready-menu-1031-v2/joint';D=R/'docs/qa/checkpoints/2026-10-31/wwf-host-resource-fit-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')

def main():
    assert not (O/'handoff.json').exists()and not (D/'handoff.json').exists();O.mkdir(exist_ok=True);D.mkdir(parents=True,exist_ok=True)
    cp=R/'build/wwf-resource-consumers-1031-v1/consumers.json';bp=R/'build/wwf-owner-split-baseline-1031-v3/proof.json'
    consumers=json.loads(cp.read_text());baseline=json.loads(bp.read_text())
    for q in [consumers,baseline]:
        assert q['passed']
        for p,h in q['bindings'].items():assert sha(p)==h,p
    artpath=R/'build/wwf-roster-source-review-v1/wrestlers.json';art=json.loads(artpath.read_text());bundle=bytearray();rows=[]
    for c in art['characters']:
        poses=sorted((p for p in art['poses']if p['character']==c['id']),key=lambda p:(p['group'],p['frame']))
        g=len(c['groups']);n=len(poses);head=2+2*g+3*n;blob=bytearray([g,n]);start=0
        for group in range(g):
            members=[p for p in poses if p['group']==group]
            assert [p['frame']for p in members]==list(range(len(members)))
            blob.extend([start,len(members)]);start+=len(members)
        record=bytearray();index=bytearray()
        for p in poses:
            index.extend((head+len(record)).to_bytes(2,'little'));index.append(p['packed_page'])
            record.extend([p['width'],len(p['packed_8x16_cells'])])
            for cell in p['packed_8x16_cells']:
                record.extend([cell['page_tile'],cell['role'],cell['x']&255,cell['y']&255])
        blob.extend(index);blob.extend(record)
        # Decode every proposed record and compare the existing source metadata.
        for i,p in enumerate(poses):
            at=2+2*g+3*i;off=int.from_bytes(blob[at:at+2],'little');page=blob[at+2]
            assert page==p['packed_page']and blob[off]==p['width']and blob[off+1]==len(p['packed_8x16_cells'])
            for k,cell in enumerate(p['packed_8x16_cells']):
                assert list(blob[off+2+4*k:off+6+4*k])==[cell['page_tile'],cell['role'],cell['x']&255,cell['y']&255]
        rows.append(dict(original_id=c['id'],name=c['name'],offset=len(bundle),bytes=len(blob),poses=n,groups=g,sha256=hashlib.sha256(blob).hexdigest(),theme=c['theme']))
        bundle.extend(blob)
    (O/'selected-metadata-proposal.bin').write_bytes(bundle)
    metadata_pages=(len(bundle)+1023)//1024;assert metadata_pages==11
    symbols={k:int(v,16)for v,k in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(J/'candidate.lbl').read_text())}
    helper_used=symbols['FmCfHelperEnd']-symbols['FmCfHelperStart'];assert helper_used<=394
    vm_growth=consumers['script_code_relocation']['direct_ZP_expansion_sites'];assert sum(vm_growth.values())==573
    plan=dict(source=True,plan_only=True,read_only_current_sources=True,no_allocation=True,native=False,installed=False,
        parent=baseline['candidate'],layout_only_baseline_exact=True,full_family_storage=dict(body_pages=84,common_three_bank_carrier_pages=24,selected_metadata_pages=metadata_pages,optional_original_portrait_pages=6,total_pages=84+24+metadata_pages+6,proposed_owner_release_pages=131,remaining_retained_pages=6,original_top_five_pages_untouched=True),
        exact_owner_release_requests=consumers['proposed_retained_owner_tails'],
        proposed_family_CHR_split=dict(body=[dict(pages=[546,604],original_page_indexes=[0,58]),dict(pages=[426,452],original_page_indexes=[58,84])],carrier_pages=[629,653],metadata_pages=[653,664],optional_portraits=[[664,668],[452,454]],unconsumed_old_owner_tail=[454,460]),
        first_Hogan_only=dict(menu_variant=0,original_id=5,theme=1,source_pose_pages_used=17,all_31_source_poses_preserved=True,selected_metadata=next(r for r in rows if r['original_id']==5),notes=['Reuse the existing Hogan-first menu identity. Do not reorder six identities.','An idle body record can serve the first cold preview without additional original portrait pages.','Full-family allocation remains a request; first wrestler can consume only its17 source body pages,24 template pages and2 metadata pages.']),
        metadata_overlay=dict(format='2B header;2B/group(first,count);3B/pose(record offset16,page index);record(width,count,4B/cell tile/role/x/y)',total_bytes=len(bundle),rows=rows,decode_checks=195,no_raster_or_palette_change=True,notes=['One24KB code/state template plus packed per-wrestler metadata avoids six separate24KB cache copies.','The loader must patch/read back selected metadata before publishing its class/full16-byte cookie last.','Each class cookie is generated from the genuine final template+metadata image, not invented constants.']),
        selected_RAM_request=dict(family=29,conditional_owner='Authenticated selected WWF epoch only',banks=[1,2,3],new_global_or_ZP_bytes=0,
            A3_VM=dict(original_code_bytes=3248,max_direct_state_instruction_growth_before_pointer_savings=573,dispatch_bytes=180,script_bundle_bytes=3634,proposed36JMP_API_bytes=108,total_before_branch_fixes=7743,bytes_remaining=449,notes=['This is a measured byte-count plan, NOT an assembled dense-cache fit. Conditional-branch expansion/pointer wrappers remain to link.','Move code or constants to the selected C2 helper region if genuine branch fixes exceed449B. Preserve all scripts and every handler.']),
            A1_music=dict(original_source_union_bytes=7897,bytes_remaining=295,notes=['Dense source relocation of8018..<88D7 plusE222..<F83C must symbolically rebind code/data pointers. No high-only or generic tune substitute.','Scratch01..08 uses the same scoped8B at the separate audio phase, saving/restoring the interrupted foreground values.']),
            C2_layout=[dict(start=0xc000,end=0xc800,role='Relocated native VM state compatibility envelope, including original01D2 side effect atC1D2'),dict(start=0xc800,end=0xc8c0,role='192B original music state relocated separately'),dict(start=0xc8c0,end=0xcab2,role='486B descriptors plus12B descriptor directory'),dict(start=0xcac0,end=0xd3a0,role='Selected wrestler metadata; current measured maximum'+str(max(r['bytes']for r in rows))+'B'),dict(start=0xd3a0,end=0xdfd0,role='3120B proposed source/native callbacks, transport and temporary saved pointer context'),dict(start=0xdfd0,end=0xdfe0,role='Proposed epoch/readiness/audio state; no shared lease yet'),dict(start=0xdfe0,end=0xdff0,role='Full16-byte family/class/version/source cookie, valid-last')]),
        pointer_relocation=dict(actual_indirect_pairs=['1F/20','21/22','23/24','25/26','C3/C4'],scoped_R0_R7_roles=dict(R0_R1='Self descriptor25/26 during VM; constructor/selector1F/20 only in separate phase',R2_R3='Opponent descriptorC3/C4',R4_R5='Script21/22',R6_R7='Action directory23/24'),dispatch='1F/20 during VM is stored in selected RAM and used by legal absolute JMP(C01F); it needs no ZP pair.',contracts=['Nonpointer native state operands become selected C2 source symbols, not a wholesale ZP swap.','Retain original indexed wrapping and original absolute00D3,Y→C0D3,Y behavior; prove nativeactor0/1 and constructor loop bounds.','Persist source pointer values in the selected context between APIs; save/restore all8 hostR0..7 around every source phase.','Every native callback marshals explicit source fields and saves/restores live source pointers around native scratch use.','Normal/lag/pausedNMI and nestedIRQ must restore actual interruptedR0..7,33SMC,rawA/C/E and livepage1; no NMI disable as a shortcut.']),
        resident_ROM_request=consumers['PRG_resident_candidate']|dict(requested_view='A-resident cold/guard/router, plus explicitly reviewed C-view copy phase if source copier requires it',notes=['5834B is a verified source/FF preimage candidate still owned by Mike, not a grant or emitted WWF capacity measurement.','No current Jn entry moves; all existing Mike instructions and data remain belowA936.','A-source worker cannot replace its own A mapping while fetching.24KB loader needs a real stable C-view phase (new alias review) or a separately reviewed descriptor refactor of an existing stable copier.']),
        menu_and_shared_source_plan=dict(slot=28,raw=29,menu_to_original_identity=[5,0,1,2,3,4],existing_variant='FmGroups low3, already cycles six with upper bits preserved',current_menu_helper_bytes=helper_used,
            Start='Add six-byte LDA#7/CPX#28/BEQ Groups to FmStartRetireFlags before its finalzero mask; current393B helper has7B headroom. Preserve all old masks and retirement order.',
            A79='No-growth classifier proposal: range27..<34; handle28 via existing DK target and30 via originalFetch; remaining27/29/31/33 share B020 setup. Move/remove the old later4-byte DK comparison to fund the four additional bytes. All36 prologues/public suffixes remain.',
            NrOnly='Replace final AND#FC/CMP#24 with 24<=raw<30 and remove redundant earlier raw28 special case: net2B shorter, restore explicit padding. This adds only29 to the original admitted set;30 remains native.',
            B020='Saved-AXYP owner gate can classify odd27..33 in14B versus current15B. Keep row/worker labels and captureSFCtargetLo before any nested mapper.',
            resolver='Retarget the existing same-size resolver farcall to an owned ROM dispatcher:29 authenticates in ROM then resolves A000+3Y/raw3;27/31/33 delegate to the genuine existing resolver. No silent admission of29 in BtCheck or CfOrBtCheck.',
            retirement='Outer menu retirement beforeSelected publication and actual pre-loader chain must retire WWF C2/full epoch before every Quick/Ar/FF/Bowser/BT/CF foreign A1/C2/A3 write. Loader APIs retain explicit caller preconditions; do not infer protection from a worker existing.',
            cold='ROM-only names/portrait/colors work before load. Invalid15/19 use real CmHostFresh/JnResetDispatch once. Forcedblank InitScreen copies/patches/verifies all3 banks, authenticates then constructs source once; valid same-player/life warm scene retains earned state. No Ready gate cleared until natural parser/Main/root native proof.'),
        music_plan=dict(original_themes=[6,7,4,2,5,1],menu_theme_order=[1,6,7,4,2,5],natural_end_ticks=[5036,1634,2567,2563,2738,2306],original_tick_cycles=[284,2200],
            placement='Actual reset.s normal path completes UpdateScreen, BankSwitchCHR and OAM/input/render publication BEFORE AudioUpdate; use its normal/lag source-audio callback phase, not the PPU deadline-critical prefix.',
            NMI_gate_proposal='AudioUpdate existing12B prefix maps new own resident gateway instead ofA63; use4B STA5115/RTS inside its old6EA pad as a fixed same-frame A-map trampoline. Foreign paths must replay actual GmFamilyNmiGate with the original saved-A frame, no extra shadow/SMC mutation. Requires explicit root review, no new fixed span.',
            policies=['Scene initializes selected original song exactlyonce before readiness; all four area types retain it.','On true source all-channel end, call the genuine init entry for the same theme, not a recording or generic area song.','Audio-owned192B is separate from foreground VM state. Foreground may reset it only after full epoch invalidation; valid playing epochs save/restore interrupted pointers and map state.','Pause/death/result/world-SFX channel ownership and actual scanlineIRQ/deadline measurements remain required.2200 source cycles are not an NMI fit/admission claim.']),
        semantic_work_remaining=['Dense source-symbol state/code/data relocation is not yet assembled; action directories contain real native pointers that must be rebuilt, including the deliberate action0 code pointer.','Recover genuine match/actor initialization beyond D1A5 stats; a captured2KiB initialized fixture is not a host constructor implementation.','Translate ring X/depth/clamp/contact eligibility to SMB world coordinates/terrain while preserving each script timing, opponent side effects and source damage. Basic native jump/gravity must not reinterpret ring depth as platformY.','Marshal real SMB enemy epochs into the original opponent/contact state and apply source damage through native enemy defeat APIs exactlyonce. Grapple/rope/pin eligibility cannot be fabricated.','Source body both-facing raster/anchor and two-palette role ownership must be qualified; current84-page records preserve original pixels but host mapping is unfinished.','Assemble/loop the actual music source and native cue/channel mixing; no generic area-music fallback qualifies all-areas music.','Existing source-lab60/90 dynamic handler coverage is bounded evidence, not natural host eligibility for every move.'])
    save(O/'plan.json',plan)
    text='''WWF source resource-fit plan — read-only, no owner release or host allocation.

The exact f0b7 current cart has131 source-unused, zero-filled pages within three retained owners: Chip426..<460(34), originalM3 546..<604(58), TMNT629..<668(39). The linked page tables and real publishers stop at425,545 and628 respectively. No emitted art is repacked or changed. The guarded layout-only relink reproduces every ROM byte and public/private label, using all86 genuine objects and the same deterministic CV3 final127→125 source pipeline. Its source-only MEMORY splits retain original ownership; they grant nothing.

Proposed full family storage fits these131pages:84 original pose pages,24 common code/state template pages,11 losslessly encoded selected-pose metadata pages,6 optional original portrait pages=125;6 owner pages remain. Source metadata2270B maximum is patched into one C2 template before class-cookie publication; six full24KB image copies are unnecessary. First Hogan can use only17 original body pages+24template+2metadata, retaining all31authentic Hogan poses. Current menu order is already Hogan,Ted,Bam,Honky,Randy,Andre, mapping to original IDs5,0,1,2,3,4.

No107-byte ZP swap is proposed. Nonpointer state moves to selectedC2 absolute source symbols. Five original indirect pairs are1F,21,23,25,C3. Four live data-pointer pairs use scopedR0..7; VM dispatch1F uses legal absolute JMP(C01F), and constructor/selector reuse a pair outsideVM.573 direct-ZP expansion sites give3821B code before pointer savings/branch fixes. A3 code+dispatch+scripts+36JMPtable totals7743B before those remaining fixes. A1's actual7897B music source union leaves295B; C2 has the2KiB VM envelope,192music state,498descriptors,2270maximum metadata and~3KiB callback/transport room. These are source-derived bounds, not an assembled host fit or granted24KB family.

The proposed resident candidate is physical96 A936..<C000(5834FF bytes), immediately after the actual MIKE_CORE endpoint. It is still Mike-owned. A24KB loader cannot self-unmap an A-view worker; explicit C-view execution review or a proven existing stable-copier refactor is required. No speculative empty PRG bank or DMC-mirror filler is offered. All currently live Mike endpoints remain fixed.

plan.json specifies no-growth A79/Nr/B020 classification, six-byte WWF Start-mask funding in existing393/400B helper, ROM-only cold callbacks, full-cookie-before-firstRAM opcode, and retirement before every foreign overwrite. None is implemented. Actual AudioUpdate occurs after deadline-critical PPU/CHR/OAM publication; a same18B-prefix+4B oldpad gateway could admit original looping music without common512growth, but needs separate source/IRQ/cadence review. Music's2200-cycle worstcase is not claimed safe before physical measurement.

The major remaining work is semantic, not just storage: genuine cold actor init; dense code/data/state relocation; ring-depth versus SMB gravity; source contact/throw/rope/pin eligibility and native enemy epochs; two-palette fairness; source music relocation/loop/cue mixing. First authenticated Hogan menu→blankload→parser→walk/jump/native scripts→kill/life should precede expansion to allsix. Nothing was admitted or installed and no Mesen ran.
'''
    (O/'README.txt').write_text(text,encoding='utf-8')
    files={Path(__file__),cp,bp,O/'plan.json',O/'README.txt',O/'selected-metadata-proposal.bin',artpath,R/'build/wwf-resource-inventory-1031-v1/inventory.json',R/'build/wwf-action-source-component-qualified-v1/integration-api.json',R/'build/wwf-action-source-component-qualified-v1/footprint.json',R/'build/wwf-roster-source-review-v1/music.json'}
    toolnames=['wwf_resource_inventory_1031_v1.py','wwf_resource_consumers_1031_v1.py','plan_wwf_owner_split_baseline_1031_v1.py','plan_wwf_owner_split_baseline_1031_v2.py','plan_wwf_owner_split_baseline_1031_v3.py']
    files.update(R/'tools/audit'/n for n in toolnames)
    for name in ['private.cfg','link.json','proof.json']:files.add(bp.parent/name)
    files.update([R/'build/wwf-owner-split-baseline-1031-v1/negative.json',R/'build/wwf-owner-split-baseline-1031-v2/negative.json'])
    bindings={str(p.resolve()):sha(p)for p in files}
    for q in [consumers,baseline]:bindings.update(q['bindings'])
    for name in ['chip-dale.chr','tmnt.chr','smb3-mario.chr']:bindings[str((R/'chr/characters'/name).resolve())]=sha(R/'chr/characters'/name)
    archive=O/'source-only.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for p in files:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
    for p,h in bindings.items():assert sha(p)==h,p
    handoff=dict(source=True,plan_only=True,no_resource_grant_or_admission=True,parent=plan['parent'],all_current_ROM_and_labels_unchanged=True,verified_owner_tail_pages=131,proposed_fullfamily_pages=125,metadata_bytes=len(bundle),selected_metadata_max=max(r['bytes']for r in rows),CFG_baseline_sha256=sha(bp),consumer_closure_sha256=sha(cp),plan_sha256=sha(O/'plan.json'),bindings=bindings,archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,members={p.relative_to(R).as_posix():sha(p)for p in sorted(files)})
    save(O/'handoff.json',handoff)
    for n in ['handoff.json','plan.json','README.txt','source-only.zip']:(D/n).write_bytes((O/n).read_bytes())
    (D/'owned-files.txt').write_text('\n'.join(['tools/audit/'+n for n in toolnames]+['tools/audit/'+Path(__file__).name,D.relative_to(R).as_posix()+'/'])+'\n')
    print(json.dumps(dict(passed=True,handoff_sha256=sha(D/'handoff.json'),bindings=len(bindings),ZIP_members=len(files),archive_bytes=archive.stat().st_size,metadata_bytes=len(bundle),max_metadata=max(r['bytes']for r in rows),menu_helper_bytes=helper_used)))
if __name__=='__main__':main()
