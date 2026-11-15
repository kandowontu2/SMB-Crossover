"""Read-only current Bub/Bob palette ownership; no image or CPU overlay.

The proposal is descriptors only. Ordinary CPU runs always use exact public40a.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re

import replay_bub_flower_margin_40a_1115 as F

R,B,W,N=F.R,F.B,F.W,F.N
PIN=F.PIN
CH=1048592


def digest(v):return sha256(v).hexdigest()


def metadata(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN
    image=b''.join(raw[CH+p*1024:CH+(p+1)*1024]for p in B.PAGES)
    q=json.loads((R/'build/bub-upgrades-root-1102-v48/proposal.json').read_text())
    lab=q['labels']
    native=(R/'build/bub-upgrades-root-1102-v48/native.bin').read_bytes()
    # Actual linked Pair and its two callers have not moved since this source.
    pair=lab['BbNativePair'];end=lab['BbNativePairDone']+1
    assert image[pair-0xa000:end-0xa000]==native[pair-0xb540:end-0xb540]
    calls=[]
    needle=bytes((0x20,pair&255,pair>>8))
    for at in range(8190):
        if image[at:at+3]==needle:calls.append(0xa000+at)
    assert len(calls)==2
    loaders=[]
    for source,target in ((0xc102,0xc3e6),(0xc106,0xc3e2)):
        pattern=bytes((0xb9,source&255,source>>8,0x8d,target&255,target>>8))
        matches=[i for i in range(pair-0xa000,end-0xa000)if image[i:i+6]==pattern]
        assert len(matches)==1
        at=matches[0];loaders.append(dict(pc=0xa000+at,before=pattern[:3].hex(),
            source_sprite_attribute=source,destination_pose_attribute=target,
            physical_file_offset=CH+B.PAGES[at//1024]*1024+at%1024))
    art=raw[CH+441*1024:CH+442*1024]
    packets=bytes.fromhex('3f1d032a26303f11032c2330')
    assert art.count(packets)==1
    at=art.index(packets)
    helper=dict(page=441,packet_PC=0xd000+at,packet_offset=at,
        packet_hex=packets.hex(),packet_file=CH+441*1024+at,
        helper_SHA256=digest(art[0x320:]),art_SHA256=digest(art[:0x320]))
    gap=(lab['BbCodeEnd'],0xb53a)
    gap_bytes=image[gap[0]-0xa000:gap[1]-0xa000]
    # This is retained retired-source space, not permission to overwrite it.
    code_end=lab['BbNativePaletteEnd']
    bundle=dict(W.Symbols.bundle(),raw=raw)
    palette_tables={}
    for name,expected in (
        ('WaterPaletteData','0f0f3010'),('GroundPaletteData','0f0f3617'),
        ('UndergroundPaletteData','0f0c3c1c'),('CastlePaletteData','0f003010')):
        off=W.location(bundle,name);data=raw[off:off+36]
        assert data[:3]==bytes.fromhex('3f0020')and data[-1]==0
        assert data[31:35].hex()==expected
        palette_tables[name]=dict(file=off,palette3=data[31:35].hex(),SHA256=digest(data))
    original=Path('C:/NES/Super Mario Bros. (World).nes').read_bytes()
    original_pal={}
    # Native original tables are found by their full36-byte command, not a
    # guessed CPU mapping; CHR pages are compared independently below.
    for name,row in palette_tables.items():
        command=raw[row['file']:row['file']+36]
        hits=[i for i in range(16,16+32768)if original[i:i+36]==command]
        assert len(hits)==1,(name,hits)
        original_pal[name]=hits[0]
    # Actual native OAM-selected Goomba patterns from root21455.
    patterns=[]
    for offset in(544,576):
        data=raw[CH+17*1024+offset:CH+17*1024+offset+32]
        halves=[]
        for part in(data[:16],data[16:]):
            hits=[i for i in range(16+32768,len(original)-15)if original[i:i+16]==part]
            assert len(hits)==1,(offset,part.hex(),hits)
            halves.append(hits[0])
        patterns.append(dict(page=17,offset=offset,SHA256=digest(data),original_8x8_files=halves))
    # Read-only assembly fit: no candidate image is constructed or mounted.
    # Entry2 loads right-half attr; Entry1 loads left-half attr. The common
    # mapper uses no C/V-changing instruction and returns original X/Y/stack.
    head=json.loads((R/'build/bub-menu-candidate-1102-v2/head-projection-v55.json').read_text())
    initial=json.loads((R/'build/bub-initial-tier-1103-v87/proposal.json').read_text())
    initial_body=(R/'build/bub-initial-tier-1103-v87/initial-tier.bin').read_bytes()
    assert len(initial_body)==10 and initial['leaf_CPU']==head['labels']['BbHeadEnd']
    assert image[initial['leaf_CPU']-0xa000:initial['leaf_CPU']-0xa000+10]==initial_body
    empty_start=initial['leaf_CPU']+len(initial_body)
    assert empty_start==0xb32a and 0xb53a-empty_start==initial['remaining_source_gap']==528
    # The delivered empty-loop recipe later consumes270 of those528 bytes.
    # Its tracked declaration and full current40a code pin close that reuse;
    # neither the head body nor the empty-loop prefixes are disposable.
    empty_path=R/'tools/audit/bub_empty_loops_1113.py'
    assert digest(empty_path.read_bytes())=='996003a033e7eb2a1e4139a472d136fd6b6e5ce0b26f1d6969497fac89874ca0'
    note=(R/'docs/qa/bub-empty-loop-probe-1113.md').read_text()
    assert 'adds 270 bytes'in note and '258 remaining bytes stay FF'in note
    start=empty_start+270
    assert start==0xb438
    spare=image[start-0xa000:0xb53a-0xa000]
    assert spare==b'\xff'*258
    mapper=bytes((0xb9,0x06,0xc1,0x4c,(start+9)&255,(start+9)>>8,0xb9,0x02,0xc1))+bytes.fromhex('48ad00c3d00c684829034903d0046829fc606860')
    assert len(mapper)==29
    spans=[]
    for index,row in enumerate(loaders):
        target=start+(6 if index==0 else 0)
        spans.append(dict(name='PairAttr'+str(index),space='private3',pc=row['pc'],
            before=row['before'],after=bytes((0x20,target&255,target>>8)).hex(),
            physical_file_offset=row['physical_file_offset']))
    spans.append(dict(name='BubOnlyPoseMapper',space='private3',pc=start,
        before=image[start-0xa000:start-0xa000+len(mapper)].hex(),after=mapper.hex(),
        physical_file_offset=CH+B.PAGES[(start-0xa000)//1024]*1024+(start%1024)))
    spans.append(dict(name='BubRGBDestination',space='helper2',pc=0xd000+at+1,
        before='1d',after='11',physical_file_offset=CH+441*1024+at+1))
    for row in spans:
        row['before_SHA256']=digest(bytes.fromhex(row['before']))
        row['after_SHA256']=digest(bytes.fromhex(row['after']))
    # No two-byte pointer to this proposed pool occurs anywhere outside the
    # retired source interval, including source tables/public JMP vectors.
    pool_words=[]
    for pos in range(len(image)-1):
        val=int.from_bytes(image[pos:pos+2],'little')
        if start<=val<start+len(mapper):
            pool_words.append(dict(pc=0xa000+pos,target=val,inside_retired_pool=gap[0]<=0xa000+pos<gap[1]))
    assert all(x['inside_retired_pool']for x in pool_words),pool_words
    assert not any(start<=pc<start+len(mapper)for pc in lab.values())
    # Source attribute bytes are owner/input discriminators. They must not be
    # modified: native pose copies are the exclusively visual boundary.
    owner_fragments={}
    for name,length,expected in(('BbOriginal_DF14',13,'b902c12903'),
            ('BbOriginal_DA30',14,'b902c14a')):
        pc=lab[name];data=image[pc-0xa000:pc-0xa000+length]
        assert data.hex().startswith(expected)
        owner_fragments[name]=dict(pc=pc,bytes=data.hex(),SHA256=digest(data))
    source=(R/'build/bub-upgrades-root-1102-v47/component.s').read_text()
    attr_stores=[]
    for match in re.finditer(r'(?m)^([A-Za-z0-9_]+):\n\s*(sta \$c10[26],y)\b',source):
        name,op=match.groups();pc=lab[name];data=image[pc-0xa000:pc-0xa000+3]
        assert data==bytes((0x99,0x02 if 'c102' in op else 0x06,0xc1)),(name,hex(pc),data.hex())
        attr_stores.append(dict(name=name,pc=pc,op=op))
    return dict(ROM_SHA256=PIN,code_SHA256=digest(image),art_helper=helper,
        pair=dict(pc=pair,end=end,SHA256=digest(image[pair-0xa000:end-0xa000]),
            direct_callers=calls,loaders=loaders),
        source_retired_gap=dict(start=gap[0],end=gap[1],size=len(gap_bytes),
            SHA256=digest(gap_bytes),partially_reused=True,
            declared_latest_spare=dict(start=start,end=0xb53a,size=258,SHA256=digest(spare)),
            reject_B300='Already live v55 deferred-head code; never allocated or mounted',granted=False),
        current_host_end=code_end,original_SHA256=digest(original),
        native_palette_tables=palette_tables,original_palette_files=original_pal,
        native_Goomba_patterns=patterns,source_attr_stores=attr_stores,
        owner_input_fragments=owner_fragments,
        proposal=dict(granted=False,mounted=False,ROM_composed=False,
            logical_owned_bytes=sum(len(bytes.fromhex(x['before']))for x in spans),spans=spans,
            old_pool_pointer_occurrences=pool_words,
            semantics='Only identity0 pose palette3 maps to0; all other palette bits/identities unchanged. Original private OAM/owner inputs untouched.',
            cold_cookie_reencoding_required=True,helper_art_changed=False))


def cold_observe(raw,identity,frames=8):
    m,opening=B.cold(raw,identity)
    lab=json.loads((R/'build/bub-upgrades-root-1102-v48/proposal.json').read_text())['labels']
    seen=Counter();attributes=Counter();writers=Counter();samples=[]
    pair=lab['BbNativePair']
    # Read-only execution observers; no controller state or CPU memory edits.
    def observe(mm,c):
        bank=mm.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
        if bank==3 and c.pc==pair:
            row=(c.x,c.y,mm.ram[2][0x102+c.y],mm.ram[2][0x106+c.y])
            attributes[row]+=1
        if bank==2 and 0xd320<=c.pc<0xd400:seen[c.pc]+=1
        if bank==3 and c.pc in(lab['BbNativeDraw'],lab['BbNativeEnemyDraw']):seen[c.pc]+=1
    # Complete current frame/NMI processing exposes real queued palette writes.
    for _ in range(frames):
        m.controller_pad=0
        B.frame(m,observe,whole_pass=True)
        samples.append([list(m.vram[0x3f10:0x3f14]),list(m.vram[0x3f1c:0x3f20])])
    return dict(identity=identity,opening=opening,terminal=B.state(m),
        palette0_palette3=samples,pair_inputs=[dict(x=k[0],y=k[1],a=k[2],b=k[3],count=v)
            for k,v in sorted(attributes.items())],entries={hex(k):v for k,v in sorted(seen.items())})


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--cold',action='store_true');a=ap.parse_args()
    raw=F.ROM.read_bytes();q=metadata(raw)
    if a.cold:q['cold']=[cold_observe(raw,i)for i in(0,1)]
    text=json.dumps(q,sort_keys=True,separators=(',',':'))
    print('RESULT '+text,flush=True)
    print('RECEIPT '+digest(text.encode()),flush=True)
