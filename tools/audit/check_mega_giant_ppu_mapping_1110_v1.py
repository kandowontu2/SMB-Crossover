"""Rebind Mega Giant sprite pairs to the current MMC5 8×16 fetch addresses."""

import argparse
from itertools import product
import json
from pathlib import Path

from check_mega_giant_geometry_1110_v1 import M, ROM, HOST_PIN, DONOR, DONOR_PIN, address, bundle, sha
from check_tmnt_render_oa import location
from prepare_mega_giant_render_1110_v1 import donor_oam, draw


CHR_START=16+128*8192
PAGE_BYTES=1024
PAIR_BYTES=32
SPRITES_PER_PAGE=PAGE_BYTES//PAIR_BYTES
FIREBALL_TILES=(0x3c,0x3e)
FIXTURE_PAGES=(1022,1023)


class ColdBus(M.Bus):
    vblank_at_boot=True

    def __getitem__(self,at):
        if at==0x2002 and self.vblank_at_boot:
            self.toggle=0
            return 0x80
        return super().__getitem__(at)


def frame(m,keys=0):
    M.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,NmiDisable=255)
    M.invoke(m,'GameLoop')
    M.consume(m)


def start_stage(b):
    m=ColdBus(b)
    cpu=M.NesMPU(memory=m,pc=None)
    cpu.reset()
    start=cpu.pc
    for step in range(300000):
        if cpu.pc==address(b,'IdleLoop'):
            break
        assert m[cpu.pc],('Cold boot BRK',hex(cpu.pc))
        cpu.step()
    else:
        raise AssertionError(('Cold boot did not reach IdleLoop',hex(cpu.pc)))
    m.vblank_at_boot=False
    setup=[(at,v) for at,v in m.writes if at in (0x2000,0x5101)]
    assert setup==[(0x2000,0x10),(0x2000,0x20),(0x5101,3),(0x2000,0x28),(0x2000,0xa8)]

    for title in range(120):
        if M.get(m,'CrossoverMenuState')==2:
            break
        frame(m,16 if title==40 else 0)
    else:
        raise AssertionError('Cold title did not enter the character menu')
    assert M.get(m,'CrossoverMenuIndex')==M.get(m,'SelectedCharacter')==0
    frame(m)
    frame(m,16)
    for stage in range(600):
        if [M.get(m,n) for n in ('OperMode','OperMode_Task','GameEngineSubroutine')]==[1,3,8]:
            break
        frame(m)
    else:
        raise AssertionError('Cold Mario confirm did not reach gameplay')
    assert M.get(m,'WorldNumber')==M.get(m,'LevelNumber')==0
    frame(m)
    ctrl=[v for at,v in m.writes if at==0x2000]
    assert ctrl[0]==0x10 and all(v&0x20 for v in ctrl[1:]) and m[0x5101]==3
    return m,dict(reset_vector=start,idle_PC=cpu.pc,reset_instructions=step,boot_mapper_writes=setup,
                  title_updates=title,stage_updates=stage,active_PPUCTRL=m.ppuctrl,
                  observed_post_enable_PPUCTRL=sorted(set(ctrl[1:])),active_CHR_mode=m[0x5101])


def chr_page(raw,page):
    start=CHR_START+page*PAGE_BYTES
    return raw[start:start+PAGE_BYTES]


def sprite_pair(m,tile):
    # Standard 8×16 PPU address generation, and MMC5 sprite register set A.
    # In 1 KiB mode each full 8×16 pattern lies within one CHR window.
    assert m.ppuctrl&0x20 and m[0x5101]==3
    pattern=((tile&1)<<12)+((tile&0xfe)<<4)
    window,offset=divmod(pattern,PAGE_BYTES)
    page=m.chr_latches[window]
    return chr_page(m.bundle['raw'],page)[offset:offset+PAIR_BYTES]


def pixels(pair,attributes):
    assert len(pair)==PAIR_BYTES
    rows=[]
    for y in range(16):
        row=15-y if attributes&0x80 else y
        i=(row//8)*16+(row%8)
        p0,p1=pair[i],pair[i+8]
        shifts=range(8) if attributes&0x40 else range(7,-1,-1)
        rows.append(bytes(((p1>>s)&1)*2+((p0>>s)&1) for s in shifts))
    return b''.join(rows)


def split_pairs(page):
    return [page[i:i+PAIR_BYTES] for i in range(0,PAGE_BYTES,PAIR_BYTES)]


def repack(top,bottom,reserved):
    first,second=map(split_pairs,(top,bottom))
    assert len(first)==len(second)==SPRITES_PER_PAGE
    relocation={(w,i):(w,i) for w,p in enumerate((first,second)) for i,part in enumerate(p) if any(part)}
    for slot in reserved:
        part=first[slot]
        if any(part):
            for window,page in enumerate((first,second)):
                free=next((i for i,data in enumerate(page) if not any(data) and (window or i not in reserved)),None)
                if free is not None:
                    page[free]=part
                    relocation[0,slot]=window,free
                    break
            else:
                raise AssertionError('No room for Giant pattern plus the native fireballs')
        first[slot]=reserved[slot]
    return b''.join(first),b''.join(second),relocation


def install_pose(seed,pages):
    m=M.fork(seed)
    raw=bytearray(m.bundle['raw'])
    m.writes.clear()
    for window,(page,data) in enumerate(zip(FIXTURE_PAGES,pages,strict=True)):
        start=CHR_START+page*PAGE_BYTES
        raw[start:start+PAGE_BYTES]=data
        M.invoke(m,'X5SetPhysicalChr',a=page&255,x=page>>8,y=window)
    m.bundle=dict(m.bundle,raw=bytes(raw))
    M.consume(m)
    assert m.chr_latches==list(FIXTURE_PAGES)+seed.chr_latches[2:]
    assert m.ppuctrl==seed.ppuctrl and m[0x5101]==seed[0x5101]
    assert all(v&0x20 for at,v in m.writes if at==0x2000)
    return m


def descriptor(b,name):
    start=location(b,name)
    raw=b['raw']
    return raw[start:start+1+raw[start]]


def foreign_sprites(seed,test):
    cases=0
    for name in sorted(seed.bundle['syms']):
        if not name.startswith(('MetaspriteData_GOOMBA_WALKING_',
                                'MetaspriteData_KOOPA_WALKING_',
                                'MetaspriteData_FIREBALL_FRAME_')):
            continue
        packet=descriptor(seed.bundle,name)
        for attr in (0,0xc0):
            before=draw(seed,[packet],128,176,attr,0,0)
            after=draw(test,[packet],128,176,attr,0,0)
            assert before==after
            for _,tile,attributes,_ in before:
                base=sprite_pair(seed,tile)
                mapped=sprite_pair(test,tile)
                assert any(base) and mapped==base,(name,hex(tile),base.hex(),mapped.hex())
                assert pixels(mapped,attributes)==pixels(base,attributes)
            cases+=1
    assert cases==24,cases
    return cases


def split_draw(packet):
    assert packet[0]%4==0 and packet[0]==len(packet)-1 and 0<packet[0]<128
    return [packet[i:i+4] for i in range(len(packet)-4,0,-4)]


def sprite_counts(parts):
    # OAM evaluation sees sprite Y spans even if individual rows are transparent.
    return [sum(y<line<=y+16 for y,_,_,_ in parts) for line in range(240)]


def check(seed,source,old_data,old_pages,old_records):
    donor=bytearray(65536)
    donor[0x8000:]=source[16:32784]
    source_chr=source[32784:]
    reserved={t//2:sprite_pair(seed,t) for t in FIREBALL_TILES}
    assert all(any(p) for p in reserved.values())
    data=bytearray()
    all_pages=[]
    records=[]
    fit={}
    giant_cases=foreign_cases=visible_rows=0
    maximum_sprites_per_line=0

    for record in old_records:
        pose,left=record['pose'],record['left']
        ids=record['relative_CHR_windows']
        if pose not in fit:
            top,bottom=[old_pages[i*PAGE_BYTES:(i+1)*PAGE_BYTES] for i in ids]
            a,b,moves=repack(top,bottom,reserved)
            unique=[]
            for page in (a,b):
                if page not in all_pages:
                    all_pages.append(page)
                unique.append(all_pages.index(page))
            published=install_pose(seed,(a,b))
            foreign_cases+=foreign_sprites(seed,published)
            fit[pose]=published,moves,unique
        m,moves,unique=fit[pose]
        mapped=[]
        offsets=[]
        expected_indices=[]
        reference=donor_oam(donor,128,176,left,0,0)
        for index,(_,tile,_,_) in enumerate(reference):
            window=int(index>=32)
            at=(8+ids[window])*PAGE_BYTES+(tile>>1)*PAIR_BYTES
            if any(source_chr[at:at+PAIR_BYTES]):
                expected_indices.append((index,at))

        for offset in record['packet_offsets']:
            packet=bytearray(old_data[offset:offset+old_data[offset]+1])
            for i in range(1,len(packet),4):
                previous=packet[i]
                window,slot=moves[previous>>6,(previous&0x3f)>>1]
                packet[i]=64*window+2*slot
                assert packet[i] not in FIREBALL_TILES
            offsets.append(len(data))
            mapped.append(bytes(packet))
            data.extend(packet)
        records.append(dict(pose=pose,left=left,packet_offsets=offsets,parts=record['parts'],
                            relative_CHR_windows=unique))
        assert len(expected_indices)==sum(len(split_draw(p)) for p in mapped)==record['parts']

        for x,y,attr,offset,rotation in product((40,128,200),(144,176),(0,3,0x20),(0,4),(0,128)):
            original=donor_oam(donor,x,y,left,0,attr)
            got=draw(m,mapped,x,y,attr,offset,rotation)
            for (py,tile,attributes,px),(index,at) in zip(got,expected_indices,strict=True):
                dy,_,da,dx=original[index]
                assert (py,attributes,px)==(dy,da,dx),(pose,left,index,got)
                donor_pair=source_chr[at:at+PAIR_BYTES]
                current_pair=sprite_pair(m,tile)
                assert current_pair==donor_pair
                assert pixels(current_pair,attributes)==pixels(donor_pair,da)
                visible_rows+=16
            maximum_sprites_per_line=max(maximum_sprites_per_line,max(sprite_counts(got)))
            giant_cases+=1
    assert len(all_pages)==22 and maximum_sprites_per_line==8
    return bytes(data),b''.join(all_pages),records,dict(giant_pose_cases=giant_cases,
           foreign_standalone_descriptor_cases=foreign_cases,compared_giant_sprite_rows=visible_rows,
           maximum_giant_sprites_per_scanline=maximum_sprites_per_line)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve()
    assert sha(ROM)==HOST_PIN and sha(DONOR)==DONOR_PIN
    frozen_paths=[out/n for n in ('giant-render-packets.bin','giant-render-source-pages.chr','render-proof.json')]
    frozen=json.loads(frozen_paths[2].read_text())
    assert frozen['passed'] and frozen['host_SHA256']==HOST_PIN and frozen['donor_SHA256']==DONOR_PIN
    for path in frozen_paths[:2]:
        assert sha(path)==frozen['bindings'][str(path)]
    seed,cold=start_stage(bundle(ROM.read_bytes()))
    seed.writes.clear()
    data,pages,records,metrics=check(seed,DONOR.read_bytes(),frozen_paths[0].read_bytes(),
                                    frozen_paths[1].read_bytes(),frozen['descriptors'])
    packets=out/'giant-native-even-packets.bin'
    patterns=out/'giant-native-even-pages.chr'
    packets.write_bytes(data)
    patterns.write_bytes(pages)
    q=dict(passed=True,source_CPU_only=True,ROM_written=False,host_SHA256=HOST_PIN,donor_SHA256=DONOR_PIN,
           exact_cold_host=cold,stock_stage_CHR_slots=seed.chr_latches,fixture_only_CHR_slots=list(FIXTURE_PAGES),
           sprite_size=[8,16],preserved_fireball_tiles=list(FIREBALL_TILES),
           preserved_fireball_patterns={hex(t):sprite_pair(seed,t).hex() for t in FIREBALL_TILES},
           descriptors=records,descriptor_bytes=len(data),physical_CHR_bytes=len(pages),**metrics,
           bindings={str(p):sha(p) for p in (Path(__file__),ROM,DONOR,*frozen_paths,packets,patterns)},
           scope='Exact cold reset, active native 1-1 and normal NMI publisher. No PPU mode switch. '
                 'Pattern fetch and H/V flip decoding for the real OAM tile IDs. No joint OAM capacity, '
                 'scanline arbitration, RGB/palette composition, physical allocation, or native playability.')
    (out/'ppu-proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=True,descriptor_bytes=len(data),physical_CHR_bytes=len(pages),**metrics)))


if __name__=='__main__':
    main()
