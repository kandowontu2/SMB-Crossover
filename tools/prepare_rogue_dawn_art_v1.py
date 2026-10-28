"""Execute pinned Rogue Dawn 1.21 sprite decoder, losslessly pack selected poses.

No native emulator, host integration, source tree or full cartridge copy. The
cartridge's real DE4A decoder supplies all tile/attribute/placement decisions.
"""
from pathlib import Path
import argparse, hashlib, json, sys
from py65.devices.mpu6502 import MPU
import rogue_dawn_map_v1 as ref

ROOT=Path(__file__).resolve().parents[1]
BODY={3:'run-0',4:'run-1',5:'run-2',7:'front',8:'stand',
      12:'run-fire-0',13:'run-fire-1',14:'run-fire-2',16:'jump',18:'jump-fire',
      23:'somersault-0',24:'somersault-1',25:'somersault-2',26:'somersault-3',
      27:'morph-0',28:'morph-1',29:'morph-2',30:'morph-3',34:'stand-fire',
      35:'front-alt',43:'aim-up',48:'fire-up',56:'air-aim-0',57:'air-aim-1',
      64:'run-up-0',65:'run-up-1',66:'run-up-2',70:'run-up-fire-0',
      71:'run-up-fire-1',72:'run-up-fire-2'}
WEAPON={37:'missile-right',38:'missile-left',39:'missile-up',40:'beam',42:'impact',
        60:'bomb-explosion-0',73:'bomb-explosion-2',74:'bomb-explosion-1',
        75:'wave',77:'bomb-explosion-4',78:'bomb-fuse-0',79:'bomb-fuse-1',
        103:'missile-impact-0',104:'missile-impact-1',105:'missile-impact-2'}

class Memory(bytearray):
    def __init__(self,data):super().__init__(data);self.writes=[];self.stores=[];self.reads=set()
    def __getitem__(self,k):
        if isinstance(k,int):self.reads.add(k)
        return super().__getitem__(k)
    def __setitem__(self,k,v):
        if isinstance(k,int):self.writes.append(k);self.stores.append((k,v))
        return super().__setitem__(k,v)

def call(m,pc,a=0,x=0,y=0,p=0x30):
    c=MPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,0xfd
    c.stPushWord(0x5aff);m.writes.clear();m.stores.clear();m.reads.clear()
    for _ in range(20000):
        if c.pc==0x5b00:
            assert c.sp==0xfd
            return c
        assert m[c.pc]!=0,('BRK',hex(c.pc))
        c.step()
    raise AssertionError(('no return',hex(c.pc)))

def native_render(raw,frame,face,weapon=False,color=0,lower_bank=2):
    m=Memory(ref.cpu_image(raw,lower_bank=lower_bank));slot=0xd0 if weapon else 0
    m[0x4b]=slot;m[0x55]=int(not weapon);m[0x0300+slot]=1
    m[0x0303+slot]=frame;m[0x030d+slot]=128;m[0x030e+slot]=128
    m[0x49]=2;m[0x6b]=color|(0x10 if face else 0)
    for i in range(0x200,0x300,4):m[i]=248
    c=call(m,0xde4a)
    parts=[list(m[i:i+4]) for i in range(0x200,0x200+m[0x5b],4)]
    assert all(0<=k<0x100 or 0x100<=k<0x400 for k in m.writes),('renderer ownership',m.writes)
    return parts,c.processorCycles,[a for a in sorted(m.reads) if a>=0x8000],list(m[0x300+slot:0x310+slot])

def source_pixels(raw,parts,alt=0):
    # Reset90: sprite8x8, base0000. C606 row1 => MMC3 r0=08,r1=0A;
    # A2FF writes actual registers0/1. So native tiles000..FF read CHR8..11.
    first=(8+2*alt)*1024
    source=raw[16+524288+first:16+524288+first+4096]
    pixels={}
    for y,t,attr,x in reversed(parts): # Original lower OAM index wins overlap.
        for yy in range(8):
            sy=7-yy if attr&128 else yy
            for xx in range(8):
                sx=7-xx if attr&64 else xx;at=t*16+sy
                v=((source[at]>>(7-sx))&1)|(((source[at+8]>>(7-sx))&1)<<1)
                if v:pixels[x-128+xx,y+1-128+yy]=(v,attr&0x23)
    return pixels

def encode(pixels,x,y,attr):
    out=bytearray(32)
    for yy in range(16):
        for xx in range(8):
            v,a=pixels.get((x+xx,y+yy),(0,attr))
            if a!=attr:continue
            at=(yy//8)*16+yy%8
            out[at]|=(v&1)<<(7-xx);out[at+8]|=((v>>1)&1)<<(7-xx)
    return bytes(out)

def palettes(raw,lower_bank=2):
    """Run original palette request and actual PPU command writer, not guessed RGB."""
    rows=[]
    def output(m,ptr,prior):
        call(m,0xc20e,x=ptr&255,y=ptr>>8)
        image=dict(prior);address=0;hi=True;ctrl=0x90;writes=[]
        for k,v in m.stores:
            if k==0x2000:ctrl=v
            elif k==0x2006:
                address=(v<<8) if hi else ((address&0xff00)|v);hi=not hi
            elif k==0x2007:
                assert 0x3f00<=address<=0x3f1f,('palette address',hex(address))
                image[address]=v;writes.append([address,v]);address+=32 if ctrl&4 else 1
        return image,writes
    baseline=Memory(ref.cpu_image(raw,lower_bank=lower_bank));baseline[0xff]=0x90
    initialptr=baseline[0x9560]|baseline[0x9561]<<8
    initial,initialwrites=output(baseline,initialptr,{})
    assert len(initial)==32
    for alt in [0,1]:
        for gear in [0,0x20]:
            for missile in [0,1]:
                m=Memory(ref.cpu_image(raw,lower_bank=lower_bank));m[0x6878]=gear;m[0x010e]=missile;m[0x69b3]=alt
                call(m,0xcb73)
                request=m[0x1c];ptr=m[0x9560+(request-1)*2]|(m[0x9561+(request-1)*2]<<8)
                assert m[ptr]==0x3f
                m[0xff]=0x90;image,writes=output(m,ptr,initial)
                rows.append(dict(alt=alt,gear_suit=gear,missile=missile,request=request,pointer=f'{ptr:04X}',
                                 actual_PPU_stores=writes,sprite_colors=[image[0x3f10+i]for i in range(16)]))
    return dict(source_area_PRG=lower_bank,initial_pointer=f'{initialptr:04X}',initial_actual_PPU_stores=initialwrites,rows=rows)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=ROOT/'build/rogue-dawn-art-v1')
    ap.add_argument('--inspect-only',action='store_true')
    a=ap.parse_args();raw=ref.ROM.read_bytes();assert ref.digest(raw)==ref.EXPECTED
    pages=[[]];weaponpairs=[];records=[];facts=[];tables={}
    for kind,frames in [('body',BODY),('weapon',WEAPON)]:
        tables[kind]={}
        for frame,meaning in frames.items():
            for choice in [0,1]:
                face=choice if kind=='body' else 0
                color=0x81 if kind=='weapon' and choice else 0
                parts,cycles,reads,state=native_render(raw,frame,face,kind=='weapon',color)
                pixels=source_pixels(raw,parts)
                attrs=sorted(set(attr for v,attr in pixels.values()))
                minx=min((x for x,y in pixels),default=0);maxx=max((x for x,y in pixels),default=-1)
                miny=min((y for x,y in pixels),default=0);maxy=max((y for x,y in pixels),default=-1)
                # Fixed grid at native object center: same world geometry both facings.
                chunks=[]
                for attr in attrs:
                    for y in range((miny//16)*16,maxy+1,16):
                        for x in range((minx//8)*8,maxx+1,8):
                            pair=encode(pixels,x,y,attr)
                            if any(pair):chunks.append((pair,attr,x,y))
                needed=list(dict.fromkeys(p for p,_,_,_ in chunks))
                if kind=='body':
                    fits=[(len(set(needed)-set(p)),i)for i,p in enumerate(pages)if len(set(p+needed))<=32]
                    if not fits:pages.append([]);fits=[(len(needed),len(pages)-1)]
                    page=min(fits)[1];pairs=pages[page]
                else:page=len(pages);pairs=weaponpairs
                record=[];restored={}
                for pair,attr,x,y in chunks:
                    if pair not in pairs:pairs.append(pair)
                    # Host visibleY=OAMY+1. Player uses existing SMB top-left
                    # origin, source center=(hostX+8,hostY+16). Weapons take
                    # their actual native center directly, not player origin.
                    hostx=x+(8 if kind=='body' else 0)
                    hosty=y+(15 if kind=='body' else -1)
                    record.extend([2*pairs.index(pair)+(128 if kind=='weapon' else 0),attr,hosty&255,hostx&255])
                    for yy in range(16):
                        for xx in range(8):
                            at=(yy//8)*16+yy%8;v=((pair[at]>>(7-xx))&1)|(((pair[at+8]>>(7-xx))&1)<<1)
                            if v:restored[x+xx,y+yy]=(v,attr)
                assert restored==pixels,('complete exact source pixel and palette/priority mask',kind,frame,face)
                assert len(record)<=124,('host record length',kind,frame,len(record))
                rec=bytes([len(record)]+record)
                # Identical descriptors share a genuine record.
                key=(page,rec)
                if key not in records:records.append(key)
                index=records.index(key);tables[kind][f'{frame:02X}:{choice}']=index
                facts.append(dict(kind=kind,frame=frame,meaning=meaning,face=face,color=color,choice=choice,record=index,page=page,
                                  source_OAM=parts,original_cycles=cycles,source_read_addresses=reads,
                                  bounds=[minx,miny,maxx,maxy],opaque_pixels=len(pixels),host_parts=len(record)//4,
                                  native_radius=[state[1],state[2]]))
    assert len(weaponpairs)<=64,('fixed2KB weapon windows2/3',len(weaponpairs))
    print(json.dumps(dict(body_pages=len(pages),weapon_pairs=len(weaponpairs),pairs=sum(map(len,pages))+len(weaponpairs),records=len(records),
                         descriptor_bytes=sum(len(r) for _,r in records),cases=len(facts))))
    if a.inspect_only:return
    assert len(pages)+2<=16,('CHR reservation16KB',len(pages)+2)
    a.output.mkdir(parents=True,exist_ok=True)
    chrdata=b''.join(b''.join(p)+bytes(1024-32*len(p))for p in pages)
    chrdata+=b''.join(weaponpairs)+bytes(2048-len(weaponpairs)*32)
    chrdata+=bytes(16384-len(chrdata))
    (ROOT/'chr/characters/rogue-dawn.chr').write_bytes(chrdata)
    # Frame indices retain original byte numbers. FF is an explicit absent pose.
    lines=['; Generated by prepare_rogue_dawn_art_v1.py from pinned Rogue1.21.',
           '; Source pixels/priority/palette indices exact. No animation tick here.',
           'RD_WEAPON_CHR_OFFSET='+str(len(pages)),
           '.pushseg','.segment "ROGUE_DAWN_ART"','RdArtStart:']
    for kind in ['body','weapon']:
        for face in [0,1]:
            name='Rd'+kind.title()+'Index'+str(face)
            values=[tables[kind].get(f'{i:02X}:{face}',255)for i in range(106)]
            lines+=[name+':',' .byte '+','.join('$%02x'%v for v in values)]
    for suffix,values in [('Lo',['<RdArtRecord'+str(i)for i in range(len(records))]),
                          ('Hi',['>RdArtRecord'+str(i)for i in range(len(records))]),
                          ('Page',[str(p)for p,_ in records])]:
        lines+=['RdArtRecord'+suffix+':',' .byte '+','.join(values)]
    for kind in ['body','weapon']:
        for axis in [0,1]:
            radii={f['frame']:f['native_radius'][axis] for f in facts if f['kind']==kind}
            lines+=['Rd'+kind.title()+'Radius'+('Y'if axis==0 else'X')+':',
                    ' .byte '+','.join(str(radii.get(i,0))for i in range(106))]
    for i,(page,rec)in enumerate(records):lines+=['RdArtRecord'+str(i)+':',' .byte '+','.join('$%02x'%v for v in rec)]
    pal=palettes(raw)
    lines+=['RdArtAnimation:', ' .byte '+','.join('$%02x'%v for v in ref.cpu_image(raw,lower_bank=2)[0x8572:0x860b])]
    lines+=['RdArtPalette:']
    # Indexed alt*4+suit*2+missile, sixteen source sprite palette bytes each.
    for alt in [0,1]:
        for suit in [0,32]:
            for missile in [0,1]:
                row=next(r for r in pal['rows']if(r['alt'],r['gear_suit'],r['missile'])==(alt,suit,missile))
                lines+=[' .byte '+','.join('$%02x'%v for v in row['sprite_colors'])]
    lines+=['RdArtEmpty: .byte 0','RdArtEnd:','.assert RdArtEnd-RdArtStart <= $d00,error,"Rogue art reservation"','.popseg','']
    (ROOT/'src/rogue_dawn_art.inc').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    proof=dict(passed=True,native_run=False,ROM=ref.binding(ref.ROM),source_decoder='62:DE4A..63:E048',
               original_pattern_mapping='C08A PPUCTRL90; C606/C61F default r0=09,r1=0B (CPX carry);61:A2FF writes mapper => effective CHR8..11. Source69B3=1 instead maps10..13; unsupported here.',
               original_CHR= dict(first_page=8,bytes=4096,sha256=ref.digest(raw[16+524288+8192:16+524288+12288])),
               tables=tables,records=facts,palettes=palettes(raw),body_page_count=len(pages),weapon_pair_count=len(weaponpairs),
               page_count=len(pages)+2,unique_pairs=sum(map(len,pages))+len(weaponpairs),
               descriptor_bytes=sum(len(r)for _,r in records),record_count=len(records),
               outputs=[ref.binding(ROOT/p)for p in ['src/rogue_dawn_art.inc','chr/characters/rogue-dawn.chr']],
               limitations=['Static center-screen source decoder executions, not native displayed frames',
                            'Native animation advance remains frozen kernel/weapons owner',
                            'Death explosion dynamic placement, source69B3 alternate pattern costume, hurt/Screw palette flashes not yet selected',
                            'Palette pointer rows are original physicalPRG02 area context; world palette composition is not installed'])
    (a.output/'extraction.json').write_text(json.dumps(proof,indent=2)+'\n')

if __name__=='__main__':main()
