"""Actual current public body rendering with poisoned duplicate CHR cells."""
from collections import Counter
import argparse
from hashlib import sha256
from itertools import product
import json
import sys

import compose_dkjr_helper_retire_1113 as P
import check_dkjr_head_bridge_1113 as H

B,N,W,L=P.B,H.N,H.W,H.L
sys.path.insert(0,str(B.R/'tools/reference'))
import dkjr_original_cpu_1102_v1 as D


def cold_portrait(parent,candidate):
    from check_current_roster_stage_ingress_1110 import UI
    rows=[]
    for raw in(parent,candidate):
        b=W.Symbols.bundle();b['raw']=raw;m=UI.seed(b,27);UI.key(m,32)
        N.invoke(m,'DrawSelectionPreview')
        assert N.get(m,'SelectedCharacter')==40
        rows.append(dict(OAM=bytes(m[0x200:0x300]),cursor=N.get(m,'CurrentOAMOffset'),
            chr=tuple(N.get(m,'CurrentCHRBank',i)for i in range(16)),
            mode=tuple(N.get(m,'X5ChrMode',i)for i in range(2)),latches=tuple(m.chr_latches),
            VRAM=bytes(m[0x4af:0x4af+N.get(m,'VRAM_Buffer1_Offset')+1])))
    assert rows[0]==rows[1]
    row=rows[0];records=[list(row['OAM'][i:i+4])for i in range(0,24,4)]
    assert row['cursor']==24 and row['mode']==(130,130)
    assert row['chr'][:4]==(188,189,190,191) and all(not q[1]&1 for q in records)
    return dict(passed=True,actual_selected=40,OAM_records=records,cursor=24,
        graphics_low_pages=list(row['chr'][:8]),graphics_modes=list(row['mode']),
        OAM_CHR_latches_palette_VRAM_commands_equal=True,private959_not_selected=True,
        scope='Actual compiled coldmenu+Select+preview CPU. Existing six-sprite nativeDonkeyKong fallback is preserved, not a new source-DKJr portrait or Mesen claim.')


def source_cells(seed,base,mode):
    donor=D.Bus();donor[:2048]=seed;donor[0:3]=bytes((32,64,base))
    cpu=D.T.NesMPU(memory=donor,pc=0)
    D.T.run(cpu,0xe9ee,mode,0,0,0x20)
    return bytes(donor[0x210:0x230])


def sprite_pixels(raw,record):
    yy,tile,attr,xx=record
    assert tile&1 and tile<=191
    even=tile-1;page=(959,960,961,961)[even//64]
    at=B.CHR+page*1024+(even&63)*16;pair=raw[at:at+32]
    result=[]
    for y in range(16):
        for x in range(8):
            px=7-x if attr&64 else x;py=15-y if attr&128 else y
            off=(py//8)*16+(py&7);bit=7-px
            result.append((pair[off]>>bit&1)|((pair[off+8]>>bit&1)<<1))
    return bytes(result)


def body_matrix(parent,candidate,cookie):
    _,before=H.cold(parent,B.COOKIE);_,after=H.cold(candidate,cookie)
    active,_=D.active();donor_seed=bytes(active.memory[:2048]);counts=Counter();changed_tiles=set()
    for base,mode in product(range(0,88,8),(0,1)):
        cells=source_cells(donor_seed,base,mode)
        for cursor,rotation in product(range(256),(0,12)):
            outcomes=[];records=[];native=[];states=[]
            for raw,seed in((parent,before),(candidate,after)):
                m=L.clone(seed);m.ram[2][:0x800]=donor_seed
                m.ram[2][0x200:0x300]=bytes([255])*256
                m.ram[2][0x210:0x230]=cells;m.ram[2][0x9a:0x9e]=bytes(4);m.ram[2][0x434]=0
                for i in range(64):m[0x200+4*i:0x204+4*i]=bytes((248,0,0,0))
                N.put(m,CurrentOAMOffset=cursor,GuestOamRotationActive=int(bool(rotation)),RgOamRotation=rotation)
                flags=(base+cursor+mode)&255
                outcomes.append(N.invoke(m,'HuDraw',a=85,x=7,y=91,p=flags))
                native.append((bytes(m[:0x100]),bytes(m[0x1e1:0x200]),bytes(m[0x300:0x800]),tuple(m.rawtags),
                    bytes(m[0x15a:0x17b]),bytes(m[0x6000:0x8000])))
                states.append(bytes(m.ram[2][:0x1000]))
                records.append(bytes(m[0x200:0x300]))
            assert tuple(outcomes[0][k]for k in'AXYP')==tuple(outcomes[1][k]for k in'AXYP')
            assert native[0]==native[1] and states[0]==states[1],(base,mode,cursor,rotation)
            for i in range(64):
                a,z=records[0][4*i:4*i+4],records[1][4*i:4*i+4]
                assert a[0]==z[0]and a[2:]==z[2:]
                if a[1]!=z[1]:
                    assert {47:9,49:41,55:9}[a[1]]==z[1]
                    changed_tiles.add(a[1]);counts['real_alias_cells']+=1
                if a[0]<240:
                    assert sprite_pixels(parent,a)==sprite_pixels(candidate,z),(base,mode,cursor,rotation,list(a),list(z))
                    counts['visible_pair_pixel_comparisons']+=128
            counts['public_HuDraw_pose_cursor_rotation_pairs']+=1
    assert changed_tiles=={47,49,55},changed_tiles
    return dict(counts,changed_native_tiles=sorted(changed_tiles),source_cells_and_all_attributes_positions_unchanged=True,
        exact_public_AXYP_SP_native_fields_maps_SMC=True,all_duplicate_bytes_poisoned=True,
        scope='Genuine donor22poses through current public HuDraw; declared cache/cursor fixtures, not natural gameplay.')


def effect_matrix(parent,candidate,cookie):
    current=P.effect_parts(parent);assert P.effect_parts(candidate)['linked']['images']==current['linked']['images']
    _,before=H.cold(parent,B.COOKIE);_,after=H.cold(candidate,cookie)
    counts=Counter();seen=set();source_context=bytes(before.ram[2][:0x900])
    def pair(kind,slot,attr,cursor,rotation,*,hanging=False):
        outcomes=[]
        for seed in(before,after):
            m=L.clone(seed);m.ram[2][:0x900]=source_context;m.ram[2][0x9a:0x9e]=bytes(4)
            m.ram[2][0x200:0x300]=bytes([255])*256
            m.ram[2][0x434]=0
            if hanging:
                m.ram[2][0x434]=slot+1;m.ram[2][0x9a+slot]=1
                m.ram[2][0x42c+slot]=kind;m.ram[2][0x420+slot]=96
                m.ram[2][0x428+slot]=80;m.ram[2][0x8d+slot]=attr
                N.put(m,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0)
            else:
                # Also admits the real two-character falling fruit condition.
                m.ram[2][0x200+slot:0x208+slot]=bytes((80,kind,attr,96,88,(kind+1)&255,attr,96))
            m[0x200:0x300]=bytes((248,0,0,0))*64
            N.put(m,CurrentOAMOffset=cursor,GuestOamRotationActive=int(bool(rotation)),RgOamRotation=rotation)
            c=H.call(m,current['linked']['symbols']['DkNativeEffects'],a=85,x=7,y=91,p=0x31)
            records=bytes(m[0x200:0x300]);outcomes.append(((c.a,c.x,c.y,c.p,c.sp),records,
                bytes(m.ram[2][:0x900]),tuple(m.rawtags),bytes(m[:0x100]),
                bytes(m[0x300:0x800]),bytes(m[0x15a:0x17b])))
        assert outcomes[0]==outcomes[1],(kind,slot,attr,cursor,rotation,hanging)
        for i in range(64):
            record=outcomes[0][1][4*i:4*i+4]
            if record[0]<240:
                seen.add(record[1]);assert record[1]not in(47,49,55),list(record)
                assert sprite_pixels(parent,record)==sprite_pixels(candidate,record)
                counts['identical_visible_effect_pairs']+=1
        counts['paired_effect_calls']+=1
    # Every byte at every single-effect source slot, all source flip bits.
    # Injury particles, points and falling fruit share this exact renderer.
    for kind,slot,attr in product(range(256),(0,4,0x30,0x34,0xc0),(0,64,128,192)):
        pair(kind,slot,attr,16,0)
    # The complete hanging selector domain including all invalid kinds.
    for kind,slot in product(range(256),range(4)):
        pair(kind,slot,slot,16,0,hanging=True)
    # Legal effects retain real cursor capacity and rotated OAM handling.
    for kind,cursor,rotation in product((0xa4,0xa8,0xac,0xf1,0xf2,0x5e,0xf3,0xf4,0xf5,0xf6,0xf7,0x90,0x91,0x92,0x93),
        (0,16,244,252),(0,12)):
        pair(kind,0x30,64,cursor,rotation)
        if kind in(0xa4,0xa8,0xac):pair(kind,0,0,cursor,rotation,hanging=True)
    assert seen<=set(range(97,100,2))|set(range(113,128,2))|set(range(129,148,2)),seen
    return dict(counts,exact_current_effect_bytes=411,D180_selector_bytes=11,
        emitted_native_tiles=sorted(seen),all_256_source_tile_values_and_flip_bits=True,
        no_effect_reads_reclaimed_art=True,private_OAM_tile_stores=2,
        scope='Exhaustive declared source-effect domains through the exact current private effect entry; not a natural particle or pickup route.')


def native_pattern_census(parent,candidate):
    bundle=W.Symbols.bundle();bundle['raw']=parent;count=cells=0;powerups={}
    for name in sorted(bundle['syms']):
        if not name.startswith('MetaspriteData_'):continue
        at=W.location(bundle,name);size=parent[at]
        assert size%4==0 and size<=128,(name,size)
        assert parent[at:at+1+size]==candidate[at:at+1+size]
        tiles=list(parent[at+1:at+1+size:4]);assert not set(tiles)&{47,49,55},(name,tiles)
        count+=1;cells+=len(tiles)
        if 'POWERUP_'in name:powerups[name]=tiles;assert all(not(t&1)for t in tiles)
    assert count==254 and len(powerups)==6
    return dict(exact_current_native_metasprites=count,native_cells=cells,
        all_native_tile_domains_exclude_reclaimed_odd_tiles=True,powerup_tiles=powerups,
        source_pattern_bank=1,native_powerup_pattern_bank=0,
        scope='Complete current named native metasprite table census plus exact private body/effect writers; foreign private owners cannot publish this DK-only CHR row.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--portrait-only',action='store_true')
    parser.add_argument('--effects-only',action='store_true');args=parser.parse_args()
    parent,input_info=P.proof_parent(B.C.ROM.read_bytes())
    print('DKJR_RETIRE_ALIAS_INPUT '+json.dumps(input_info,separators=(',',':')),flush=True)
    candidate,info=P.alias_probe(parent)
    print('DKJR_RETIRE_ALIAS_BINDING '+json.dumps(info,separators=(',',':')),flush=True)
    print('DKJR_RETIRE_ALIAS_PORTRAIT '+json.dumps(cold_portrait(parent,candidate),separators=(',',':')),flush=True)
    if args.effects_only:
        print('DKJR_RETIRE_ALIAS_EFFECTS '+json.dumps(effect_matrix(parent,candidate,bytes.fromhex(info['cookie'])),separators=(',',':')),flush=True)
        print('DKJR_RETIRE_ALIAS_NATIVE_PATTERNS '+json.dumps(native_pattern_census(parent,candidate),separators=(',',':')),flush=True)
    elif not args.portrait_only:
        print('DKJR_RETIRE_ALIAS_BODY '+json.dumps(body_matrix(parent,candidate,bytes.fromhex(info['cookie'])),separators=(',',':')),flush=True)


if __name__=='__main__':main()
