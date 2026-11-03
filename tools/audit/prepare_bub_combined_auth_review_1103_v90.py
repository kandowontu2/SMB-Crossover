"""Compact caller review and exact6c9e+DK90+auth83 memory recipe; no ROM."""
import hashlib,json,re
from pathlib import Path
import build_storage_guard_v1 as G
import check_bub_combined_auth_contracts_1103_v84 as P
from check_tmnt_render_oa import location

R,O=P.R,P.O
BASE=R/'build/prince-live-root-candidate-1103-v113/prince-live-private.nes'
BASE_SHA='6c9e85a94d34a4623d21789d5293c61af2ad14d214f5780f57613a51ae6bb25a'
sha=lambda data:hashlib.sha256(data).hexdigest()


def image():
    base=BASE.read_bytes();assert sha(base)==BASE_SHA
    live=R/'docs/qa/allocations/prince-live-lifetime-1103-v113.json'
    grant=json.loads(live.read_text());assert grant['granted']and grant['expected_candidate_SHA256']==BASE_SHA
    front=R/'docs/qa/allocations/prince-current-frontend-1103-v105.json'
    f=json.loads(front.read_text());assert f['granted']and len(f['approved_exact_patches'])==9
    old,new,parent,proposal=P.image()
    raw=bytearray(base);layers=[];ranges=[]
    def patch(at,before,after,role):
        assert len(before)==len(after)and raw[at:at+len(before)]==before,(role,at)
        raw[at:at+len(after)]=after;ranges.append((at,at+len(after)))
        return dict(file_offset=at,bytes=len(after),before_SHA256=sha(before),after_SHA256=sha(after),role=role,
            changed_bytes=sum(a!=z for a,z in zip(before,after)))
    rows=[]
    for q in parent['patches']:
        before,after=bytes.fromhex(q['old_hex']),bytes.fromhex(q['new_hex'])
        row=patch(q['file_offset'],before,after,q.get('role','Existing formally reviewed DK native gate'))
        row.update({name:q[name]for name in ['physical_PRG','physical_CHR','CPU_half_open','grant']if name in q})
        rows.append(row)
    layers.append(dict(source_manifest='build/dkjr-native-source-1102-v2/native-combined-owner-v101-measurement.json',patches=rows))
    rows=[]
    for q in proposal['patches']:
        at=16+65*8192+q['CPU']-0xa000
        rows.append(patch(at,bytes.fromhex(q['old_hex']),bytes.fromhex(q['new_hex']),f'Exact83 resident source at{q["CPU"]:04X}'))
    for row in [9,14,34]:
        at=16+65*8192+0x108c+row*3
        rows.append(patch(at,bytes.fromhex('4c40a7'),bytes([76])+proposal['labels']['CoNativePrimitive'].to_bytes(2,'little'),f'Raw39 full-auth primitive publicrow{row}; foreign exact old dispatcher'))
    layers.append(dict(source_manifest='build/bub-menu-candidate-1102-v2/combined-auth-v83-measurement.json',patches=rows))
    # Independent order: validated101/83 model first, then each unchanged
    # root105 frontend patch. This catches stale bases and overlap errors.
    counterpart=bytearray(new['raw'])
    for row in f['approved_exact_patches']:
        at=row['file_offset'];before,after=bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
        assert counterpart[at:at+len(before)]==before
        counterpart[at:at+len(after)]=after
        assert raw[at:at+len(after)]==base[at:at+len(after)]==after
    assert raw==counterpart
    allowed=set()
    for low,high in ranges:allowed.update(range(low,high))
    changed=[i for i,(a,z)in enumerate(zip(base,raw))if a!=z]
    assert all(i in allowed for i in changed)
    pages=P.P.D.A.CODE+P.P.D.A.ART
    assert pages==[817,833,847,856,867,881,882,883,959,960,961]
    for page in range((len(raw)-1048592)//1024):
        if page not in pages:
            at=1048592+page*1024;assert raw[at:at+1024]==base[at:at+1024]
    # No new scene40 or frontend admission is hidden in this recipe.
    scene=16+65*8192+0x1013
    assert raw[scene:scene+19]==base[scene:scene+19]
    assert bytes(raw[scene:scene+19]).startswith(bytes.fromhex('0848ad026038e925c903'))
    return bytes(raw),dict(passed=True,source_only=True,ROM_written=False,candidate_allowed=False,
        base_candidate=BASE.relative_to(R).as_posix(),base_SHA256=BASE_SHA,
        expected_memory_SHA256=sha(raw),total_changed_bytes=len(changed),
        code_pages=P.P.D.A.CODE,art_helper_pages=P.P.D.A.ART,
        all_other_CHR_pages_byte_identical=True,all_out_of_recipe_bytes_byte_identical=True,
        unchanged_root105_frontend_spans=9,root113_Prince159_preserved_except_explicit_combined_shared_unit=True,
        DK_scene_or_menu_admission_added=False,scene_gate_remains_37_to_39=True,
        ordered_exact_preimage_layers=layers,
        independent_reconstruction='Root6c9e->101pages/gates/resident->83 equals101/83->all9exact105frontend patches',
        cookie_location_scope='83 preserves101cookie locations/values;101itself is a source-factor successor of159 and relocates its own shared table/cookie layout. Values and all physical native component bytes outside explicit shared spans remain exact.',
        required='Root exact combined shared-span/native candidate grant before ROM output; future scene40/frontend admission remains separate.'),[live,front]


def pointer(path,needle):
    text=path.read_text();lines=text.splitlines()
    hits=[i+1 for i,line in enumerate(lines)if needle in line]
    assert len(hits)==1,(path.name,needle,hits)
    return dict(path=path.relative_to(R).as_posix(),line=hits[0],needle=needle)


def main():
    G.preflight(private_root=O,reserved_bytes=100000,reserved_files=2,fresh=True)
    out=O/'combined-auth-v90-composition.json';review=O/'combined-auth-v90-callers.json'
    assert not out.exists()and not review.exists()
    raw,recipe,inputs=image();old,new,parent,proposal=P.image();labels=proposal['labels']
    origin=16+65*8192;bank=raw[origin:origin+8192]
    own=O/'combined-auth-v83.s';sel=O/'combined-auth-v83-selector.s'
    reference=R/'tools/reference'
    targets={'ShCheckCode':0xa800,'CoCheckCode':labels['CoCheckCode'],
        'CoCheckIndex':labels['CoCheckIndex'],'CoCold':0xae00,'CoRetire':0xae0b,
        'CoSelect':labels['CoSelectIndex']-11,'CoSelectIndex':labels['CoSelectIndex'],
        'CoRetireOwners':labels['CoRetireOwners']}
    calls={}
    for name,target in targets.items():
        calls[name]=[dict(CPU=0xa000+i,opcode='JSR'if bank[i]==32 else'JMP',
            actual_hex=bank[i:i+3].hex())for i in range(8190)
            if bank[i]in [32,76]and bank[i+1:i+3]==target.to_bytes(2,'little')]
    assert [r['CPU']for r in calls['ShCheckCode']]==[0xa7ab,0xa8dd,0xabda,0xac8d]
    assert [r['CPU']for r in calls['CoCheckCode']]==[0xa75a,0xa824]
    assert [r['CPU']for r in calls['CoSelect']]==[0xae41,0xae79]
    assert [r['CPU']for r in calls['CoRetireOwners']]==[0xae38,0xae73]
    sh=[dict(caller='PrSh',CPU=0xa7ab,source=pointer(sel,' jsr ShCheckCode'),
        assumptions='Enclosed ShDispatch frame saves originalAXYP/CurrentC/fiveSMC; consumes only returnedC. Raw36 and37-row tag bounds checked beforecall.'),
        dict(caller='ShLoad',CPU=0xa8dd,source=pointer(reference/'shinobi_resident_loader_1101_v1.inc',' jsr ShCheckCode'),
        assumptions='Loader savesAXYP/R0..7/CurrentC/reload/fiveSMC. C1 is warmheader success; C0 enters real cold load. Forcedblank/FF/owner guards precede thiscall.'),
        dict(caller='ShChr',CPU=0xabda,source=pointer(reference/'shinobi_chr_1101_v6.inc',' jsr ShCheckCode'),
        assumptions='Graphics wrapper savesAXYP and consumesC only; C1 publishes currentfour sourceCHR requests, C0 rejects withoutpublication.'),
        dict(caller='ShInjury',CPU=0xac8d,source=pointer(reference/'shinobi_damage_1101_v10.inc',' jsr ShCheckCode'),
        assumptions='Injury wrapper savesAXYP/R0..7/CurrentC. C1 permits source/native injury guards; C0 rejects. No helper A/X/Y orNZ inference.')]
    source_pointers={name:pointer(own,name+':')for name in targets if name!='ShCheckCode'}
    source_pointers['ShCheckCode']=pointer(own,'ShCheckCode:')
    result=dict(passed=True,review_only=True,ROM_written=False,candidate_allowed=False,
        source_revision='Exact83, final84..88 proofs, compact89freeze',targets=targets,
        compiled_current_bank65_JSR_JMP_callers=calls,all_four_Sh_callers=sh,
        exact_source_pointers=source_pointers,
        ABI={
            'ShCheckCode':'PublicA800: preservesAXYP except returnedC, R0..7, originalCmap, fiveSMC andSP. Onlyraw36 may succeed afterboth16Bheaders. ActualFRC callers additionally normalizeNZ from returnedA, as82proves. Wrongraw nowpushes fullPAXY before reject;86/87qualify that frame.',
            'CoCheckCode':'Privatecarry-only AEE3. Caller savesAXYP; helperA/X/Y/NZV are not consumed. Raw37..40 range producesX0..3 thenfalls into CoCheckIndex; otherrawsreturnC0 withoutheader execution. AllR0..7/currentC/SP survive. Callersare PrOdd A75A (saveddispatchframe) and raw39primitive A824 (savedPAXY).',
            'CoCheckIndex':'PrivateAEEE: receivesX0..3 only from guardedCoCheckCode, or X4 only after ShCheckCode confirms36. Fifthcookie isAA78 Sh; descriptor table staysfourrecords and neverusesX4. Saves/restoresR5/R6, comparesbothcompleteheaders, restoresCmap/SP; onlycarry is an output.',
            'CoSelect':'Privatecold functionAF01; onlycalls AE41 guard and AE79 afterretire/invalidate. Raw37..40 only. SuccessX0..3,R3/R4descriptor,R5/R6cookie,A descriptorHi,Yunchanged,C1. InvalidreturnsC0 withoutchangingR3..6. Outer cold frame savesAXYP/R0..7/fiveSMC/currentC/reload.',
            'CoSelectIndex':'PrivateAF0C; solecall from CoRetireOwners loop withX3..0 independentofSelectedCharacter. Initializescookie+descriptorR3..6,C1; preservesX/Y. Headercheck immediatelyfollows. Outerpublicframe restoresall clobbers.',
            'CoRetireOwners':'PrivateAF50; enteredonly from AE38 publicretire mode and AE73 cold beforeoverwrite. ForX3..0 fullheaders authenticate beforetyped private retire vectors; invalidheaders cannotexecutecode. GenuineBubAI restoredbeforeinvalidation; finaltailShRetire. RequiresexistingouterR0..7/AXYP/SMC/currentC frame, not a standalonepublicABI.',
            'CoCold':'PublicAE00 savesAXYP/R0..7/fiveSMC/currentC/reload; onlyreturnedCchanges. B062 owning scene wrapper is the onlydirectcaller. Guards37..40,OperMode1,FamilyMainCommit,blankPPUMASK,DisableScreen,FF beforeoverwrite; warmfullheaders returnsready withoutcopy. B013 current scene gate routesonly37..39; source-only40 tests callAE00 explicitly.',
            'CoRetire':'PublicAE0B has same savedframe butrestoresallP includingcarry. B026 is a tailJMP calledby realShSceneAC2C andShMenuAD88; B100 Reset19 JSR thenSEC/RTS supplies its own handledC. Source/auth/mappings strict evenSelectedCharacterforeign.',
            'CoPublishChr':'Internal83 tailJMP invokes unchangedFarCallCommon andreturnsdirectly to original CoPublishChr caller. IncomingA stillpublishedtoSafecallA; all5SMC outerrestores unchanged. It removesone redundantJSR/RTS returnlevel only;84cold and86/87FF/nested proveunwind.',
            'primitive_public_rows':'Only9/14/34 B0A7/B0B6/B0F2 JMPA817 change. Selected39 savesPAXY andfullauth;9/34 restore+SEC,14restore+fixed958B. ForeignrawsrestoreP/A thenJMPoldA740. RealHuVisible/HuSide/HuWeaponTail -> HuCommonRestore -> FRC+3 ensures finalNZ fromA; arbitrarysame-bank directentry NZ is not claimed.'},
        owning_scene_carry='B013/B062 owns routed37..39 evenifcoldfails; wrapperownershipC is distinctfrom directAE00readyC. Cold/faultproofs useactual loader entry, not a fictitious fallback.',
        typed_jumps=[dict(from_CPU=0xb0c5,to_CPU=0xb100,role='ExistingReset19 veneer'),
            dict(from_CPU=0xb026,to_CPU=0xae0b,role='Existingforeignmenu/scene retirestub'),
            dict(from_CPU=0xb100,to_CPU=0xae0b,role='ExistingrealReset19 retirement'),
            dict(from_CPU=0xb062,to_CPU=0xae00,role='Existingowningscene load'),
            dict(from_CPU=0xa740,role='UnchangedShDispatchprologue thenPrFamily; whole176Bselector exact101')],
        limits='Typed/source/currentcompiled boundaries only. No arbitraryglobalindirectpointer or externalwriter census/cache permission. Shared101+83 spans remain ungranted pendingrootreview.',
        proof_pointers={name:str((O/file).relative_to(R))for name,file in [
            ('native_flags','complete-auth-v82-ingress.json'),('functional','combined-auth-v84-contracts.json'),
            ('native_trap_retire','combined-auth-v85-lifecycle.json'),('IRQ_FF','combined-auth-v86-ISR.json'),
            ('nested','combined-auth-v87-nested.json'),('resident_references','combined-auth-v88-references.json'),
            ('source_archive','combined-auth-source-v89.json')]})
    paths=[Path(__file__),BASE,*inputs,own,sel,O/'combined-auth-v83-measurement.json',
        O/'combined-auth-source-v89.json',P.P.D.O/'native-combined-owner-v101-measurement.json',
        R/'tools/audit/prepare_bubble_bobble_common_routes_1102_v5.py',
        R/'tools/audit/prepare_prince_public_routes_1102_v24.py',
        *[reference/name for name in ['shinobi_resident_loader_1101_v1.inc','shinobi_chr_1101_v6.inc','shinobi_damage_1101_v10.inc']]]
    binding={path.relative_to(R).as_posix():sha(path.read_bytes())for path in paths}
    result['bindings']=binding;recipe['bindings']=binding
    review.write_text(json.dumps(result,indent=2)+'\n');out.write_text(json.dumps(recipe,indent=2)+'\n')
    print(json.dumps(dict(passed=True,review=review.relative_to(R).as_posix(),composition=out.relative_to(R).as_posix(),
        expected_memory_SHA256=recipe['expected_memory_SHA256'],changed_bytes=recipe['total_changed_bytes'],
        task_storage=G.inventory(O,G.TASK_BYTES,G.TASK_FILES))))


if __name__=='__main__':main()
