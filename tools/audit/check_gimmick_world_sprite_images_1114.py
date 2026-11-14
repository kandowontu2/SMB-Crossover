"""Original CPU Gimmick natural image route and readonly current art census."""
from collections import Counter
from hashlib import sha256
import argparse,json
from unittest.mock import patch

import replay_gimmick_world_sprite_images_1114 as Factory
import check_shared_world_sprite_images_1114 as Source
import check_mr_gimmick_full11_current_1114 as Stage

W,N=Factory.W,Factory.N


def census(raw,units=False):
    b=dict(W.Symbols.bundle(),raw=raw);rows=[];windows=Counter();offsets={}
    for name,count in(('GmHeroTable',22),('GmStarTable',66),('GmEffectTable',4)):
        at=W.location(b,name);bank=(at-16)//8192
        for index in range(count):
            pointer=int.from_bytes(raw[at+2*index:at+2*index+2],'little')
            offset=16+bank*8192+(pointer&8191);parts=[]
            for i in range(16):
                if raw[offset+4*i]==0:break
                parts.append(list(raw[offset+4*i:offset+4*i+4]))
            else:raise AssertionError(('Terminated current Gimmick record',name,index))
            tiles=[p[1]for p in parts];used={(t&1)*4+(t>>6)for t in tiles}
            assert tiles and not any(t&1 for t in tiles)and used<={0,1},(name,index,tiles)
            windows.update(used);rows.append(dict(family=name,index=index,parts=len(parts),windows=sorted(used),tiles=tiles))
            for i,tile in enumerate(tiles):
                if tile>=64:
                    file=offset+4*i+1;new=(tile&63)|193
                    assert(new&62)==(tile&62)and((new&1)*4+(new>>6))==7
                    offsets[file]=(tile,new)
    publishers=[]
    for name,end in(('GmGraphics','GmColors'),('GmPortrait','GmScreenPoint')):
        at=W.location(b,name);limit=W.location(b,end)
        # Portrait and ScreenPoint live in different banks; its final RTS is
        # bounded by the original fixed source body and the X5 setter pattern.
        code=raw[at:limit]if limit>at and(limit-at)<1024 else raw[at:at+200]
        expected=bytes.fromhex('a932a203a001')
        matches=[i for i in range(len(code)-5)if code[i:i+6]==expected]
        assert len(matches)==1,(name,matches)
        offset=at+matches[0]+5
        publishers.append(dict(entry=name,operand_file=offset,operand_CPU=W.address(b,name)+matches[0]+5,
            old=1,proposed=7,private_page=818,actual_preimage=expected.hex()))
    kernel_cases=0
    if units:
        m=Stage.cold(raw);art=(W.location(b,'GmHeroTable')-16)//8192
        m.raw_page(2,art|128);N.put(m,CurrentBankC=art|128)
        for row in rows:
            table=W.location(b,row['family']);ptr=int.from_bytes(raw[table+2*row['index']:table+2*row['index']+2],'little')
            for facing in(0,1):
                for attribute in(0,1,64,65,128,129,192,193):
                    N.put(m,R0=ptr&255,R1=ptr>>8,R3=attribute,R4=96,R5=0,R6=120,R7=1,
                        GmTemp2=facing,CurrentOAMOffset=0,GuestOamRotationActive=0)
                    N.invoke(m,'GmEmitRecord',a=83,x=71,y=109,p=0x61)
                    tiles=[m[513+4*i]for i in range(N.get(m,'CurrentOAMOffset')//4)]
                    assert tiles==row['tiles'],(row,tiles)
                    for tile in tiles:
                        mapped=tile if tile<64 else(tile&63)|193
                        assert mapped&62==tile&62
                        old_bank=818 if tile>=64 else 816
                        new_bank=818 if mapped&1 else 816
                        pos=1048592+old_bank*1024+(tile&62)*16
                        newpos=1048592+new_bank*1024+(mapped&62)*16
                        assert raw[pos:pos+32]==raw[newpos:newpos+32]
                    kernel_cases+=1
    return dict(ROM_SHA256=sha256(raw).hexdigest(),current_source_record_cases=len(rows),used_windows=sorted(windows),
        record_digest=sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        proposed_metadata_only_tile_remap_bytes=len(offsets),proposed_tile_offset_digest=sha256(json.dumps(sorted(offsets.items())).encode()).hexdigest(),
        proposed_tile_offset_triples=[(at,*pair)for at,pair in sorted(offsets.items())],
        metadata_only_remap_preimage_samples=[dict(file=at,old=pair[0],new=pair[1])for at,pair in sorted(offsets.items())[:5]],
        private1_tile_domain=sorted({pair[0]for pair in offsets.values()}),
        actual_publisher_sites=publishers,current_kernel_pose_facing_attribute_cases=kernel_cases,
        alternative_proposal='Retarget two private publishers1→7 and only these immutable-record addressing bytes; same art/pair offsets/geometry/palette, no new code. Requires explicit grant, nothing placed.',
        art_immutable=True,proposal_placed=False,allocation_granted=False,outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--census',action='store_true');p.add_argument('--units',action='store_true');p.add_argument('--metadata',action='store_true');a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    with patch.object(Source,'Factory',Factory):
        q=census(raw,a.units)if a.census or a.units else Source.strict_metadata(raw,'mr_gimmick')if a.metadata else Source.run(raw,'mr_gimmick',1800)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not(a.metadata or a.census or a.units):assert q['passed'],'Gimmick natural image route remains source-unqualified'
