"""Read-only source adoption plan: exact SMB3+05b1 onto installed Bowser66c663.

No compiler/linker/emulator invocation; frozen source, readiness and ROMs stay
untouched. The generated diff is review material, never a binary overlay.
"""
from pathlib import Path
import collections,difflib,hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
P=R/'build/peach-palette-fix-1030-v1/joint'
S=R/'build/smb3plus-peach-gravity-consumer-1031-v1/joint'
C=R/'build/bowser-playable-jump-v1/joint'
O=R/'build/smb3plus-current66-adoption-plan-1031-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def main():
    assert not O.exists()
    expected=['f56e55cd69b93821e66548848305cf9822e2ac0e8a25752d7192332cded53b78',
              '05b1c5a861eaf49fbaea1f8278229f2970defa3e81909178e0eb46e1ad2f2d10',
              'c6635815711a624a02c4337cd9f1830ca9c43b14a824f2ea51963f796ad98c2a']
    for d,h in zip([P,S,C],expected):assert sha(d/'candidate.nes')==h
    a,b,c=[scoped_load(d/'candidate.nes')for d in[P,S,C]]
    ds={i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y}
    dc={i for i,(x,y)in enumerate(zip(a['raw'],c['raw']))if x!=y}
    assert not(ds&dc),'Physical byte delta conflict'
    assert a['raw'][:16]==b['raw'][:16]==c['raw'][:16]
    ch=16+128*8192
    pages=sorted({(i-ch)//1024 for i in ds if i>=ch})
    assert pages==list(range(969,1019))
    perbank=dict(collections.Counter((i-16)//8192 for i in ds if 16<=i<ch))
    assert perbank=={66:51,81:124,90:178,91:733,92:26}
    O.mkdir(parents=True)
    source_paths=['src/smb3_mario_motion.s','src/smb3_mario_render.s',
                  'src/smb3_native_controller.inc','src/smb3_mario_art.inc',
                  'src/smb3_mario_dispatch.s','src/character_select.s',
                  'src/new_roster_dispatch.s','entrypoint.s','private.cfg']
    module_paths=source_paths[:5]
    normalize=lambda text,d:text.replace(str(d),'JOINT').replace(d.as_posix(),'JOINT')
    patch=[];source_inventory=[]
    for n in source_paths:
        old=normalize((P/n).read_text(),P);new=normalize((S/n).read_text(),S)
        current=normalize((C/n).read_text(),C)
        if n in module_paths:assert old==current,('Current66 M3 source differs',n)
        patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='f56/'+n,tofile='SMB3PLUS/'+n,n=4))
        source_inventory.append(dict(path=n,f56_sha256=sha(P/n),leaf_sha256=sha(S/n),current66_sha256=sha(C/n),
                                     current_module_equals_ancestor=old==current,
                                     adoption='Copy genuine M3 module into NEW private clone'if n in module_paths else'Surgical source hunk; retain all current66 owner changes'))
    (O/'source-graft.diff').write_text(''.join(patch),encoding='utf-8')
    newfiles=['smb3plus_body_host.s','smb3plus_kick_host.s','smb3plus_float_state.inc',
              'smb3plus_float_data.s','smb3plus_menu_name.s','smb3plus-chr.s',
              'toad-smb3plus-body.chr','peach-smb3plus-body.chr']
    assert all((S/n).exists()for n in newfiles)
    # Enumerate every original existing M3 label and genuine object exports,
    # explicitly retaining the four permitted internal-label movements.
    rows=[];removed=[]
    for n,z in a['syms'].items():
        if not n.startswith('M3')or z.get('type')!='lab':continue
        assert n in c['syms'],n
        assert address(a,n)==address(c,n),('Current66 M3 drift',n)
        if n not in b['syms']:
            assert n in ['M3Palette::Pick','M3Palette::Identity'],n
            removed.append(dict(name=n,current=address(c,n),classification='Private rewritten palette block; genuine logic moved to MbOriginalPaletteIndex, not an exported entry'))
            continue
        rows.append(dict(name=n,current=address(c,n),leaf=address(b,n),unchanged=address(c,n)==address(b,n)))
    moved=[r for r in rows if not r['unchanged']]
    assert {r['name']for r in moved}=={'M3NoToggle','M3StatusNameDispatch::Names','M3StatusNameDispatch::Loop','M3StatusNameDispatch::Done'}
    cmd=[str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-exports',str(C/'main.o')]
    z=subprocess.run(cmd,cwd=R,text=True,capture_output=True);assert z.returncode==0
    exports=[n for n in re.findall(r'Name:\s+"([^"]+)"',z.stdout)if n.startswith('M3')]
    assert all(address(c,n)==address(b,n)for n in exports)
    write(O/'M3-label-retention.json',dict(existing_labels=len(rows)+len(removed),matched_labels=len(rows),removed_private_labels=removed,unchanged=len(rows)-len(moved),
        moved_internal_labels=moved,actual_main_object_M3_exports=exports,all_actual_exports_exact=True,rows=rows))
    segments=[]
    for n in ['M3_LOGIC','M3_GFX','M3_NATIVE','RIVER_CITY_CORE','NEW_ROSTER_NAMES','PROTO_MENU']:
        rr=[]
        for label,bb in [('f56',a),('current66',c),('SMB3PLUS',b)]:
            g=next(g for g in bb['segs'].values()if g['name']=='"'+n+'"')
            off=int(g['ooffs'],0);start=int(g['start'],0);size=int(g['size'],0)
            rr.append(dict(stage=label,physical_bank=(off-16)//8192,start=start,end_exclusive=start+size,size=size,file_offset=off))
        segments.append(dict(name=n,stages=rr))
    # No current66 live emitted segment overlaps the three append-only spans.
    append=[(90,0xecc,0xefa),(91,0x139d,0x13fd),(81,0x105b,0x10ce)]
    for bank,lo,hi in append:
        first=16+bank*8192+lo;last=16+bank*8192+hi
        for g in c['segs'].values():
            if 'ooffs'not in g:continue
            gl=int(g['ooffs'],0);gh=gl+int(g['size'],0)
            assert not(max(first,gl)<min(last,gh)),('Current live span collision',bank,lo,hi,g['name'])
        assert c['raw'][first:last]==a['raw'][first:last]
    # Actual current objects are copied forward by the jump successor; use
    # their original current64 producer, not stale inherited joint logs.
    producer=R/'build/bowser-current64-v3'
    assert sha(C/'main.o')==sha(producer/'joint/main.o')
    assert sha(C/'union.o')==sha(producer/'joint/union.o')
    recipes={}
    for label,p in [('current_main',producer/'main-build.json'),('current_union',producer/'union-build.json'),
                    ('current_final_link',C.parent/'final-link.json'),
                    ('leaf_main',S.parent/'main-build.json'),('leaf_union',S.parent/'union-build.json'),
                    ('leaf_CHR',S.parent/'chr-build.json'),('leaf_final_link',S.parent/'final-link.json')]:
        v=json.loads(p.read_text());assert v['returncode']==0
        recipes[label]=dict(path=str(p),sha256=sha(p),command=v['command'])
    write(O/'actual-producer-recipes.json',recipes)
    assert normalize((P/'union.s').read_text(),P)==normalize((S/'union.s').read_text(),S), 'Leaf union gameplay source differs'
    q=dict(retained_initial_plan_negative='V1 required two private rewritten M3Palette labels to survive; Pick/Identity are not actual exported entries and their logic lives in MbOriginalPaletteIndex. Explicitly recorded here; no source or ROM mutation.',status='READ_ONLY_CONCRETE_SMB3PLUS_SOURCE_ADOPTION_PLAN_NO_BUILD',
        source_base=expected[2],leaf=expected[1],common_ancestor=expected[0],native=False,built=False,
        frozen_sources_modified=False,readiness_modified=False,
        total_leaf_changed_bytes=len(ds),PRG_changed_bytes=sum(perbank.values()),PRG_by_physical_bank=perbank,
        CHR_pages=[969,1019],CHR_body_bytes=51200,changed_CHR_bytes=sum(i>=ch for i in ds),
        actual_current66_byte_delta_intersection=0,header_exact=True,
        physical_resource_conflicts_found=[],full_emitted_segment_append_checks_pass=True,
        new_helpers_append=[dict(physical_bank=bank,offset_start=lo,offset_end_exclusive=hi)for bank,lo,hi in append],
        segment_evidence=segments,
        tight_boundaries=['M3_LOGIC endsAEFA; Rogue AF00 starts6B later','M3_GFX endsD3FD; Rogue upper audio D400 starts3B later','A81 helper endsB0CE; Rogue page4 beginsB100'],
        source_inventory=source_inventory,new_source_assets={n:sha(S/n)for n in newfiles},
        runtime_state=dict(fields='MbFloatExpired/Timer/Anchor/Ready $5C64..$5C67',
            temporal_owner='Existing selected17 M3 $5C00..$5CFF state; native100B ends5C63, host fields start5C80',
            existing_constructor='Actual M3Reset clears entire5C00..5CFF before ready; preserve existing foreign ownership/5FFF protocol',
            new_global_address_lease=False),
        public_M3_retention=dict(existing_labels=len(rows)+len(removed),matched_labels=len(rows),removed_private_labels=removed,unchanged=len(rows)-len(moved),
            actual_main_exports=exports,all_existing_public_entry_PCs_exact=True,
            four_internal_movements_explicitly_recorded=True),
        stages=[
            'Create NEW source/output clone of immutable c663. Preserve all current66 Bowser/BT/common/RCR/Benj/Peach inputs, cookies and header.',
            'Copy only five unchanged-since-f56 M3 module producers listed above, with genuine SMB3+ modified bodies. Append the five consumed helper includes after current entrypoint tail, keeping helper segment order.',
            'Apply only Select INC/AND3 and navigation12->9 padding hunk in current character_select; only name JMP+6NOP hunk in current new_roster_dispatch. Never copy either complete donor shared file.',
            'Add SMB3PLUS_BODY_CHR segment line after current BENJ_MARIO_CHR in current private.cfg, keeping all current MEMORY/ROM/cache partitions. Assemble genuine two25-page body files into a new CHR object.',
            'Use actual current64 main/union recipes and currentc663 final-link recipe, ALL output/dependency/MEMORY file paths relocated to new root and private_build_outputs.validate before every invocation. Replace only actual current main.o and union.o inputs; retain all Bowser/BT component inputs. Add only new SMB3CHR object.',
            'Preserve compressed current46-group union source/labels/prologues. Leaf union.s has no gameplay delta; reassemble current genuine source against final imports if desired and require its emitted bytes exact. Do not import the old uncompressed f56 union or stale consumer-18 paths.',
            'Regenerate the existing CV3 final125 mirror from final127, then require all fixed119/120/125/127/DMC bytes exact because this adoption has no fixed-code delta.',
            'Compare final ROM against currentc663 with only approved SMB3 leaf delta offsets allowed; forbid binary overlay. All current66 M3 public PCs and following segment boundaries remain exact. Retain native/parser/whole-controller/graphics/foreign/ISR tests bound to the NEW hash before any install.'
        ],
        menu_effect='Original Mario3/Luigi3 variants0/1 remain. Four-cycle adds Toad2/Peach3; if later enabled as the leaf does, reachable profiles83->85 and ready66->68 (no readiness bytes changed in this plan). Root decides WIP rollout.',
        known_limits=['Donor ground pound unjoined','Custom stomp delay unjoined','Special art incomplete','Kick sound request currently dropped','No perfect/final/full-campaign claim; native donor terrain is distinct from SMB1 host terrain'],
        verification_plan=['Exact source reproduction/delta/public-M3/layout/header/current66 payload+cookie closure',
            'Retarget current2016 original controller/1344 foreign movement/9072 graphics/81 foreign menu/768 status/3380 ISR checks without weakening',
            'Real current roster/menu/Start and a bounded Toad/Peach select/lives/jump/land smoke on final hash only under root grant'],
        bindings={})
    files=[Path(__file__),R/'tools/audit/plan_smb3plus_current66_adoption_1031_v1.py',P/'candidate.nes',P/'candidate.dbg',C/'candidate.nes',C/'candidate.dbg',C/'main.o',C/'union.o',
        S/'candidate.nes',S/'candidate.dbg',S.parent/'source-stage.json',C.parent/'handoff.json',
        O/'source-graft.diff',O/'M3-label-retention.json',O/'actual-producer-recipes.json']
    files +=[S/n for n in source_paths+newfiles]+[C/n for n in source_paths]
    files +=[Path(v['path'])for v in recipes.values()]
    q['bindings']={str(p.resolve()):sha(p)for p in files}
    write(O/'plan.json',q)
    print(json.dumps(dict(status=q['status'],plan_sha256=sha(O/'plan.json'),bindings=len(q['bindings']),
                         conflict_bytes=0,existing_M3_labels=len(rows),public_M3_PCs_exact=True)))


if __name__=='__main__':main()
