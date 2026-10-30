"""Read-only lossless FF FX mask/OAM/storage and native donor audit.

Models exact bitplane projections; allocates no cartridge pages or RAM.
"""
from pathlib import Path
import collections, hashlib, itertools, json, sys, traceback

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_fx_palette_audit_v2 as A
from check_tmnt_render_oa import address,location
H=A.H
O=R/'build/ff-fx-mask-feasibility-v1'
sha=A.sha


def pixels(pattern):
    return [((pattern[(y//8)*16+y%8]>>x)&1)|(((pattern[(y//8)*16+8+y%8]>>x)&1)<<1)
       for y in range(16) for x in range(8)]


def pattern(values):
    out=bytearray(32)
    for y in range(16):
        for x in range(8):
            i=values[y*8+x]
            out[(y//8)*16+y%8]|=(i&1)<<x
            out[(y//8)*16+8+y%8]|=((i>>1)&1)<<x
    return bytes(out)


def records(b):
    m=A.T.base(b);out=[]
    raw=(R/'chr/characters/final-fantasy.chr').read_bytes()
    for entry in range(158):
        for chunk in range(8):
            H.put(m,FfSlot=1,PlayerOutlinesOff=0)
            c=A.source(m,'FfRenderChunk',a=entry,x=chunk,y=0)
            if not c.p&1:break
            page=H.get(m,'FfRenderPage');n=H.get(m,'FfRenderBuffer')
            yoff=H.get(m,'FfRenderYOffset')+256*m[address(b,'FfRenderYOffset')+1]
            if yoff&32768:yoff-=65536
            for i in range(0,n,4):
                at=address(b,'FfRenderBuffer')+1+i
                tile,attr,y,x=m[at:at+4]
                cell=raw[page*1024+tile*16:page*1024+tile*16+32]
                out.append(dict(entry=entry,chunk=chunk,page=page,tile=tile,role=attr&3,
                    x=x-256 if x&128 else x,y=yoff+(y-256 if y&128 else y),pattern=cell))
    H.exact(m)
    return out


def mask_proof(rows):
    projections={
      'Fire':({1:1,3:2},{2:1},[0,0x16,0x26,0x30],[0,0x26,0x12,0x21]),
      'Ice':({3:2},{1:2,2:3},[0,0x12,0x21,0x30],[0,0x26,0x12,0x21]),
      'Bolt':({3:2},{1:2,2:3},[0,0x18,0x28,0x30],[0,0x26,0x18,0x28]),
    }
    per_page=collections.defaultdict(set)
    per_pose=collections.defaultdict(set)
    counts=collections.defaultdict(lambda:collections.Counter())
    sprites=collections.defaultdict(list)
    palette2=[0,0x16,0x30,0x27]
    checked=0;extra=0
    for r in rows:
        if r['entry']<144:
            per_page[r['page']].add(r['pattern'])
            continue
        family='Fire' if r['entry']<147 else 'Ice' if r['entry']<152 else 'Bolt'
        p2_map,p1_map,original,palette1=projections[family]
        old=pixels(r['pattern'])
        base=[p2_map.get(v,0)for v in old]
        overlay=[p1_map.get(v,0)for v in old]
        assert all(not(a and c)for a,c in zip(base,overlay))
        # Every opaque source pixel survives once, with exactly its NES code.
        assert [original[v]if v else None for v in old]==[
            palette2[a]if a else palette1[c]if c else None for a,c in zip(base,overlay)]
        layers=[pattern(v)for v in[base,overlay]if any(v)]
        assert layers
        extra+=len(layers)-1;checked+=128
        per_page[r['page']].update(layers)
        per_pose[r['entry']].update(layers)
        counts[r['entry']]['old_parts']+=1
        counts[r['entry']]['mask_parts']+=len(layers)
        for _ in layers:sprites[r['entry']].append((r['x'],r['y']))
    poses=[]
    for entry,c in sorted(counts.items()):
        old_y=[r['y']for r in rows if r['entry']==entry]
        def peak(ys):return max(sum(y<line<=y+16 for y in ys)for line in range(min(ys),max(ys)+17))
        poses.append(dict(entry=entry,**dict(c),extra_parts=c['mask_parts']-c['old_parts'],
            original_max_sprites_per_line=peak(old_y),mask_max_sprites_per_line=peak([y for x,y in sprites[entry]]),
            distinct_mask_pairs=len(per_pose[entry]),minimum_pages_for_this_pose=(len(per_pose[entry])+31)//32))
    pages=[dict(relative_page=page,distinct_pairs=len(v),capacity=32,over_by=max(0,len(v)-32))
      for page,v in sorted(per_page.items())]
    return dict(pixel_code_comparisons=checked,all_opaque_source_pixels_and_transparency_exact=True,
       no_world_palette_writes_or_new_lease=True,
       mapping='P2=[16,30,27], P1=[26,12,21] for Fire+Ice/White or [26,18,28] for Fire+Bolt. P0 untouched.',
       split_every_effect_without_dynamic_fast_path=True,extra_part_instances=extra,
       per_pose=poses,source_page_preserving_layout=pages,
       pages_exceeding_original_1KB_capacity=[r for r in pages if r['over_by']],
       all_used_patterns_including_unmodified_body_after_masks=sum(len(v)for v in per_page.values()),
       qualification_limit='Masks are a pixel-exact model, not an executable atlas/renderer. Normal8sprite/OAM/window fit is NOT established.')


def native_world(b):
    m=A.T.base(b);rows=[]
    for area in range(4):
        H.put(m,AreaType=area,VRAM_Buffer1_Offset=0)
        H.invoke(m,'QueueMegaManFacePalette')
        p=address(b,'VRAM_Buffer1')
        actual=list(m[p:p+6])
        assert actual[:3]==[63,29,3]
        rows.append(dict(area=area,actual_source_P3_packet=actual))
    H.put(m,VRAM_Buffer1_Offset=0)
    H.invoke(m,'QueueGuestWeaponPalette')
    p=address(b,'VRAM_Buffer1');p2=list(m[p:p+6])
    assert p2==[63,25,3,22,48,39]
    objects=[('GreenKoopa','KOOPA_WALKING_1','ProcessGreenKoopa'),
      ('RedKoopa','KOOPA_WALKING_1','ProcessRedKoopa'),
      ('Piranha','PIRANHA_MOUTH_OPEN',None),('Bowser','BOWSER_FRONT_MOUTH_OPEN',None),
      ('Mushroom','POWERUP_MUSHROOM',None),('1UP','POWERUP_1UP',None),
      ('Goomba','GOOMBA_WALKING_1',None),('Fireflower','POWERUP_FIREFLOWER',None)]
    actual=[]
    for name,pose,setup in objects:
        attr=0
        if setup:
            H.put(m,TimerControl=0,Enemy_SprAttrib=0,Enemy_State=0,FrameCounter=0)
            H.invoke(m,setup,x=0)
            attr=H.get(m,'Enemy_SprAttrib')
        pointer=address(b,'MetaspriteData_'+pose+'_RIGHT')
        H.put(m,R0=pointer&255,R1=pointer>>8,R3=attr,R4=120,R5=0,R6=160,R7=1,
            CurrentOAMOffset=0,GuestOamRotationActive=0)
        H.invoke(m,'MetaspriteRenderLoop')
        n=H.get(m,'CurrentOAMOffset')
        assert n and n%4==0
        palettes=[m[0x202+i]&3 for i in range(0,n,4)]
        actual.append(dict(object=name,parts=n//4,palettes=palettes))
    expected=[[1]*4,[2]*4,[1]*4,[1]*3,[2]*2,[1]*2,[3]*2,[0,0,1,1]]
    # Renderer consumes the records in reverse order. Mixed fireflower still
    # requires both P0 and P1, so hiding just P1 records is NOT whole-object.
    assert all(sorted(r['palettes'])==sorted(v)for r,v in zip(actual,expected)),actual
    H.exact(m)
    return dict(native_P3_packets=rows,native_P2_packet=p2,actual_native_OAM=actual,
      optional_black_exact_in_areas=[0,1],optional_black_not_exact_in_areas=[2,3])


def schedules():
    rows=[]
    for colors,world in itertools.product([['Fire'],['Ice'],['Bolt'],['Sword'],['Fire','Ice'],['Fire','Bolt']], [False,True]):
        owners=colors+(['WorldP1']if world else [])
        observed=collections.Counter()
        for frame in range(60):observed[owners[frame%len(owners)]]+=1
        assert all(v>0 for v in observed.values())
        rows.append(dict(effect_color_families=colors,world_P1_visible=world,
            original_pattern_single_P1_owner_cycle=owners,
            worst_color_family_interval=len(owners),
            simultaneous_mask_P1_owner_cycle=['all_FX','WorldP1']if world else ['all_FX']))
    return dict(model_only=True,rows=rows,
      obligations=['Use completed displayed-draw/NMI epoch, not arbitrary Main count; queue palette and matching OAM atomically.',
       'Schedule color families, not individual Fire slots; all same-color slots can be drawn together.',
       'Only add world phase when a native P1-consuming object has actually admitted visible parts.',
       'Hide complete conflicting native object, including its non-P1 parts (fireflower is mixed P0/P1).',
       'Melee sword shares body descriptors/optional ink; attribute filtering alone is not proof of complete sword-object suppression.',
       'No damage/update/allocation changes, no palette approximations, preserve P2/P3, restore area/Bowser native P1 on world phase.',
       'Normal8sprite/OAM overload fairness remains required independently of palette fairness.'])


def main():
    O.mkdir(exist_ok=False);p=dict(passed=False,native=False,admitted=False,read_only=True)
    try:
        assert sha(A.H.O/'candidate.nes')==A.EXPECTED
        audit=json.loads((R/'build/ff-fx-palette-audit-v2/audit.json').read_text())
        for f,h in audit['bindings'].items():assert sha(f)==h,f
        b=H.C.qualified(A.H.O/'candidate.nes')
        p['lossless_masks']=mask_proof(records(b))
        print('exact mask/color/opaque pixel model PASS',flush=True)
        p['actual_world_consumers']=native_world(b)
        print('actual native palette packets/OAM consumers PASS',flush=True)
        p['fair_scheduling_proposal']=schedules()
        p['passed']=True
    except Exception as e:p.update(error=repr(e),traceback=traceback.format_exc())
    paths=[Path(__file__),Path(A.__file__),R/'build/ff-fx-palette-audit-v2/audit.json',
       H.O/'candidate.nes',H.O/'candidate.dbg',H.O/'src/metasprite_engine.s',H.O/'src/metasprite.s',
       H.O/'src/characters.s',H.O/'src/sprite_render.s']
    p['bindings']={str(f.resolve()):sha(f)for f in paths}
    out=O/('audit.json'if p['passed']else'negative-v1.json')
    out.write_text(json.dumps(p,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=p['passed'],path=str(out),error=p.get('error'))),flush=True)
    assert p['passed']


if __name__=='__main__':main()
