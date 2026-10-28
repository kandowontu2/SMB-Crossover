"""Read existing eight samples/OAM in memory; write no images or native data."""
from pathlib import Path
import ast, collections, hashlib, json, sys
from PIL import Image
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from final_bill_lance_hard_gallery_source_v2 import BillArena
from final_bill_lance_hard_gallery_source_v1 import OWNER_NAMES, EXTRA_OWNERS
from verify_native_relocation import NesMPU

R=Path(__file__).resolve().parents[2]
N=R/'build/current-44204-bill-hard-earned-v1/native'
ROM=R/'build/bill_inert_pool.nes'
BASE=R/'build/zelda2_easy_glove.nes'
OUT=R/'docs/qa/bill-current-capsule-hud-finding-2026-10-28.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    if OUT.exists():assert sha(OUT)=='f8268f6675c68bf3b92576a5b711fc437c32f8b6931c984c52277e91dcac0785','Preserve frozen findings'
    b=scoped_load(ROM);old=scoped_load(BASE);raw=b['raw']
    assert sha(ROM)=='44204c9b573a82dd4838df1821afeaad8ffab8b264ebb234f31a8e156434ff5a'
    assert sha(BASE)=='32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
    assert 'BillHudAnchor'not in b['syms']and 'BillHudAnchor'not in old['syms']
    for name in ['RemainingDraw','SamusFixedMissileHud']:
        p,z=location(b,name),location(old,name);size=int(b['syms'][name]['size'],0)
        assert raw[p:p+size]==old['raw'][z:z+size]
    selection=json.loads((N/'selected-eight-whole-frames.json').read_text())
    # Read only the existing eight whole panels, with exact raw-pixel hashes.
    # The first draft independently decoded the container and matched these
    # same eight hashes. No additional frame or image file is extracted.
    sheet=Image.open(N/'selected-eight-whole-frames.png').convert('RGBA');frames={}
    for item in selection['selected']:
        x,y=item['column']*256,item['row']*240
        panel=sheet.crop((x,y,x+256,y+240))
        assert hashlib.sha256(panel.tobytes('raw','BGRA')).hexdigest()==item['raw_sha256']
        frames[item['name']]=panel.convert('RGB')
    value=lambda n,i=0:raw[location(b,n)+i]
    art={}
    for selected in [0,2,3,4,5]:
        a=value('RemainingDraw::PickupArts',8+selected)
        ptr=value('AvArtRightLo',a)+256*value('AvArtRightHi',a);bank=value('AvArtBanks',a)&127
        off=16+bank*8192+ptr%8192;record=list(raw[off:off+raw[off]+1]);family=value('AvArtFamilies',a)
        expected=[]
        for i in range(1,len(record),4):
            tile,attr,y,x=record[i:i+4]
            expected.append([(24+(y-256 if y>=128 else y))&255,tile,attr&0xe3,(192+(x-256 if x>=128 else x))&255])
        art[selected]=dict(art=a,source_record_bank=bank,pointer=ptr,record=record,family=family,
            physical_page=value('AvPhysicalBanks',family)|1,expected_hardware=expected)
    # Extract only the two surviving setup/run functions. Importing their whole
    # historical module demands a deleted, unrelated SMB3 archive at import time.
    # No absent archive is restored or replaced; these exact functions invoke the
    # genuine current full RemainingDraw/MetaspriteRenderLoop instructions.
    helper=R/'tools/audit/bill_capsule_hud_controls_v4.py'
    tree=ast.parse(helper.read_text());functions=[q for q in tree.body if isinstance(q,ast.FunctionDef)and q.name in ['setup','run']]
    assert len(functions)==2
    ns=dict(BillArena=BillArena,NesMPU=NesMPU,address=address,location=location)
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(helper)+'::two-functions','exec'),ns)
    for name in EXTRA_OWNERS:
        if name not in OWNER_NAMES:OWNER_NAMES.append(name)
    cpu=[]
    for selected in [0,2,3,4,5]:
        q=ns['setup'](b,item=selected);_,writes,coords,entries=ns['run'](q)
        hud=[z for z in entries if z['index']==20]
        assert bool(hud)==bool(selected)
        if selected:
            assert all(z['x']==192 and z['y']==24 and z['pointer']==art[selected]['pointer']and z['Cbank']==art[selected]['source_record_bank']for z in hud)
        cpu.append(dict(selected=selected,actual_full_RemainingDraw=True,source_HUD_coordinates=coords,actual_HUD_renderer_entries=hud,
            actual_OAM_stores=[z for z in writes if z['index']==20]))
    # Last genuine completed DMA before each exact screenshot CPU cycle. Safe
    # pre-render guards already passed; no display-epoch guess from filename.
    last={};samples=selection['selected']
    for line in(N/'ability-dma-epochs.jsonl').open():
        q=json.loads(line)
        if q['kind']!='completed-DMA-before-render-enable':continue
        for sample in samples:
            if q['complete']['cpu']<=sample['record']['stamp']['cpu_cycle']:last[sample['name']]=q
    names=['normal','machine','spread','laser','flare','machine-rapid1','machine-rapid2','laser']
    selecteds=[0,4,5,2,3,4,4,2]
    chrbase=16+raw[4]*16384
    rows=[];normal=frames['normal-1-source-art']
    header_counts=collections.Counter(normal.getpixel((x,y))for y in range(8,24)for x in range(144,232))
    header_white=max(header_counts,key=lambda rgb:sum(rgb))
    assert header_white==(255,254,255)
    for sample,name,selected in zip(samples,names,selecteds):
        q=last[sample['name']];source=art[selected];im=frames[sample['name']]
        parts=[dict(slot=i//4,bytes=q['hardware'][i:i+4])for i in range(0,256,4)if q['hardware'][i:i+4]in source['expected_hardware']]
        patterns=collections.defaultdict(set);mask={}
        for part in parts:
            y,tile,attr,x=part['bytes']
            for py in range(16):
                sy=15-py if attr&128 else py
                at=chrbase+source['physical_page']*1024+((tile&254)*16)%1024+sy//8*16+sy%8
                for px in range(8):
                    sx=7-px if attr&64 else px
                    color=((raw[at]>>(7-sx))&1)|(((raw[at+8]>>(7-sx))&1)<<1)
                    if color:
                        pos=(x+px,y+1+py);rgb=im.getpixel(pos);patterns[color].add(rgb);mask[pos]=color
        coherent=bool(mask)and all(len(z)==1 for z in patterns.values())and len({next(iter(z))for z in patterns.values()})==len(patterns)
        changed_white=[list(pos)for pos in sorted(mask)if 144<=pos[0]<232 and 8<=pos[1]<24 and normal.getpixel(pos)==header_white and im.getpixel(pos)!=header_white]
        if selected in [4,5]:assert len(parts)==3 and coherent
        if selected==0:assert not parts
        rows.append(dict(case=name,selected=selected,frame=sample['record']['stamp'],sample_raw_sha256=sample['raw_sha256'],last_completed_DMA=q['id'],DMA_start=q['start'],DMA_complete=q['complete'],
            exact_compiled_HUD_OAM_parts=parts,pattern_opaque_pixels=len(mask),source_pattern_RGB_classes={str(k):sorted(v)for k,v in patterns.items()},
            coherent_actual_ROM_pattern=coherent,overwritten_static_white_header_pixels=changed_white,
            limits='No native per-HUD caller/pointer or physical CHR/palette register dump exists. OAM/CPU/source routing plus actual rendered pattern classes attribute this to the selected capsule; absent Laser/Flare capsule does not alone prove a defect.'))
    result=dict(read_only=True,native_launches=0,new_images=0,ROM_sha256=sha(ROM),parent_ROM_sha256=sha(BASE),
        finding='Real preexisting Bill selected-capsule HUD layout overlap. Not a leftover natural reward actor and not introduced by the 31-byte inert-pool optimization.',
        exact_source_path='RemainingDraw::Hud reads InvSelected[3] -> PickupArt ((character-2)*8+selected) -> actual capsule record -> anchor192,24 -> SamusFixedMissileHud native fallback -> ArtPointer -> MetaspriteRenderLoop.',
        actual_OAM_bounds=[180,9,203,24],actual_visible_sprite_bounds=[180,10,203,25],actual_header_white_RGB=header_white,
        source_palette='Record palette3; build_remaining_art declares fixed black/peach/brown world quantization. Gold/brown appearance is consistent; layout over the header is the defect.',
        why_not_reward='Gallery clearArena clears all six Enemy_Flag slots between stages; physical pickups are staged at156,176 (world art anchor164,200), while the three matched sprites exactly equal the selected HUD capsule at192,24. No new natural reward is staged in free-emission phase.',
        why_case_difference='Normal selected0 skips HUD. Laser/Flare use a separate active shot CHR family; ArtPointer rejects an incompatible later family. Their selected samples lack matching capsule OAM; actual first-family source order was not logged, so this is a source-consistent explanation, not an instrumented cause claim.',
        preexisting_private_fix='docs/qa/bill-lance-capsule-hud-source-2026-10-26.txt describes unadopted HUD9d anchor112,16. Its $BFAE helper site is now occupied by SamusFixedMissileHud; do not overlay that old patch blindly. Any new product fix needs current-layout qualification.',
        native_functional_result='PASS4338wall/3860updates/3288DMA/minSP200 remains functional component evidence, not all-pixel correctness.',
        compiled_art=art,current_full_caller_controls=cpu,actual_samples=rows,
        retained_tool_setup_limits=['First attempted whole helper-module import stopped at a deleted unrelated SMB3 archive dependency; no native/data writes. Only the existing exact two helper function ASTs were then loaded.','Initial standalone typed-control call omitted the historical OWNER_NAMES extension; its tracing assertion failed before capture. Corrected observer owner registration; no game source change.','Unsubmitted first analysis f8268f...c0785 used RGB255/255/255 to count white header pixels and reported0. Actual original header RGB is255/254/255. Corrected this offline color-class oracle, with no PNG/native/source modification.'],
        bindings={str(p):sha(p)for p in [Path(__file__).resolve(),ROM,ROM.with_suffix('.dbg'),BASE,N/'selected-eight-whole-frames.json',N/'selected-eight-whole-frames.png',N/'ability-dma-epochs.jsonl',N/'captures.nesppuv1',N/'native-bill-gallery.json',helper,R/'tools/reference/build_remaining_art.py',R/'src/samus_fixed_hud.s',R/'docs/qa/bill-lance-capsule-hud-source-2026-10-26.txt']})
    OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(report=str(OUT),sha256=sha(OUT),rows=[dict(case=z['case'],parts=len(z['exact_compiled_HUD_OAM_parts']),opaque=z['pattern_opaque_pixels'],coherent=z['coherent_actual_ROM_pattern'],overwritten_white=len(z['overwritten_static_white_header_pixels']))for z in rows])))


if __name__=='__main__':main()
