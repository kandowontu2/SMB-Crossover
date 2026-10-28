"""Derive exact Popo/Nana poses from pinned original Ice Climber executable data.

Only chr/characters/ice-climbers* and src/ice_climbers_art.inc are generated.
No hand-drawn/reskinned pixels: execute original D17C/EAFC/C73D, composite its
8x8 OAM, then losslessly repack the same palette indices into host 8x16 pairs.
"""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/audit'))
from verify_native_relocation import NesMPU
COMMIT='df2c8e55e7f13e5792482527db9e7c9e4a84c6e1'
SRC=ROOT/'chr/characters/ice-climbers-source-bank_FF.asm'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
PINNED={
 'bank_FF.asm':'767733b27d9c9537a4ad93339d4d49a2db7099da27f551335d74611db921caa0',
 'bank_ppu.asm':'5cf43537cd5eeeea62b26615d4887a0f146ce3dd91e980bcec86ee60bc8c0aab',
 'bank_ram.inc':'f2d851c3cc10ea6e9efec03e75772ba7a13bb2b90cdfd8ef91cd8a3b1a39610e',
 'bank_val.inc':'0e9aed749bf1cf8a8dbd28d53384d2970ba5d5a951a55b035c07ca5b119a69bb',
 'CHR_ROM_1.chr':'7e780c2cc75a8676399fe1d70b32b1309aed97bb2f194317f6122998718cc5fc',
 'CHR_ROM_2.chr':'2497c670b65a274657e7384a5cdc66d7fbdc26f3eae407b2dd95ed3ef4f95844'}

def original():
    for name,expected in PINNED.items():assert digest(ROOT/'chr/characters'/('ice-climbers-source-'+name))==expected,name
    data=bytearray(16384);known=set()
    for line in SRC.read_text().splitlines():
        m=re.search(r'00:([0-9A-F]{4}):\s+((?:[0-9A-F]{2}\s+)+)(.*)',line)
        if not m:continue
        at=int(m[1],16)-0xc000;values=bytes.fromhex(m[2]);asm=m[3].split(';')[0].strip()
        if asm.startswith('.byte '):
            parts=asm[6:].strip().split(',')
            if all(re.fullmatch(r'\s*\$[0-9A-Fa-f]{2}\s*',p)for p in parts):values=bytes(int(p.strip()[1:],16)for p in parts)
        assert 0<=at<16384
        data[at:at+len(values)]=values;known.update(range(at,at+len(values)))
    # These exact original executable spans and data are required by the renderer.
    for lo,hi in [(0xc73d,0xc839),(0xcbb3,0xcbda),(0xd17c,0xd1e5),(0xeaa2,0xeb14)]:
        assert all(i-0xc000 in known for i in range(lo,hi)),hex(lo)
    return data

def render(prg,variant,pose,facing):
    m=[0]*65536;m[0xc000:]=prg;m[0x55]=1;m[0x5f]=variant
    m[0x64+variant]=64;m[0x66+variant]=80;m[0x62+variant]=int(facing==1)
    for i in range(0x200,0x300,4):m[i]=248
    def call(pc,y):
        c=NesMPU(memory=m,pc=pc);c.x=variant;c.y=y;c.sp=253;c.stPushWord(0x5aff)
        for _ in range(3000):
            if c.pc==0x5b00:break
            c.step()
        assert c.pc==0x5b00 and c.sp==253
        return c.processorCycles
    cycles=call(0xd17c,pose if pose<11 else 0)
    if pose>=11:
        # Native death rotates six source tiles/attributes after the base OAM.
        m[0x6c+variant]=pose-11;m[0x32+variant]=1
        cycles+=call(0xd0d7,0)
    slots=list(range(variant*9,variant*9+6))+[7+variant]
    parts=[m[0x200+i*4:0x204+i*4]for i in slots if m[0x200+i*4]!=248]
    source=(ROOT/'chr/characters/ice-climbers-source-CHR_ROM_1.chr').read_bytes()
    pixels={}
    for y,t,a,x in parts:
        for yy in range(8):
            sy=7-yy if a&128 else yy
            for xx in range(8):
                sx=7-xx if a&64 else xx;at=t*16+sy
                v=((source[at]>>(7-sx))&1)|(((source[at+8]>>(7-sx))&1)<<1)
                if v:pixels[x-64+xx,y-80+yy]=v
    return pixels,parts,cycles

def encode(pixels,x,y):
    out=bytearray(32)
    for yy in range(16):
        for xx in range(8):
            v=pixels.get((x+xx,y+yy),0);at=(yy//8)*16+yy%8
            out[at]|=(v&1)<<(7-xx);out[at+8]|=((v>>1)&1)<<(7-xx)
    return bytes(out)

def main():
    prg=original();pages=[[]];records=[];facts=[];posepages=[]
    for variant in [0,1]:
        for pose in range(15):
            for face in [1,2]:
                pixels,parts,cycles=render(prg,variant,pose,face)
                record=[];restored={};needed=[]
                for y in [-8,8,24]:
                    for x in [-8,0,8,16]:
                        pair=encode(pixels,x,y)
                        if any(pair)and pair not in needed:needed.append(pair)
                candidates=[(len(set(needed)-set(p)),i)for i,p in enumerate(pages)if len(set(p+needed))<=32]
                if not candidates:pages.append([]);candidates=[(len(needed),len(pages)-1)]
                page=min(candidates)[1];pairs=pages[page];posepages.append(page)
                for y in [-8,8,24]:
                    for x in [-8,0,8,16]:
                        pair=encode(pixels,x,y)
                        if not any(pair):continue
                        if pair not in pairs:pairs.append(pair)
                        tile=2*pairs.index(pair) # Host sprite window0, 8x16 bank0.
                        record.extend([tile,0,(y+8)&255,x&255])
                        for yy in range(16):
                            for xx in range(8):
                                at=(yy//8)*16+yy%8;v=((pair[at]>>(7-xx))&1)|(((pair[at+8]>>(7-xx))&1)<<1)
                                if v:restored[x+xx,y+yy]=v
                assert restored==pixels,('Exact original full mask',variant,pose,face)
                assert len(record)<=32
                records.append(bytes([len(record)]+record))
                facts.append(dict(variant=variant,pose=pose,face=face,source_OAM=parts,opaque_pixels=len(pixels),host_parts=len(record)//4,original_cycles=cycles))
    assert len(pages)<=4,('Bounded4KB character allocation',len(pages))
    chrdata=b''.join(b''.join(pairs)+bytes(1024-len(pairs)*32)for pairs in pages)
    target=ROOT/'chr/characters/ice-climbers.chr';target.write_bytes(chrdata)
    lines=['; Generated from original Ice Climber executable renderer, commit '+COMMIT+'.',
        '; 11 native movement/hammer poses +4original death phases, x2facings x2variants.',
        '.pushseg','.segment "ICE_CLIMBERS_ART"','IcArtStart:','IcPoseLo:',
        ' .byte '+','.join('<IcPose'+str(i)for i in range(len(records))),'IcPoseHi:',
        ' .byte '+','.join('>IcPose'+str(i)for i in range(len(records))),'IcPosePage:',
        ' .byte '+','.join(str(x)for x in posepages)]
    for i,rec in enumerate(records):lines+=['IcPose'+str(i)+':',' .byte '+','.join('$%02x'%v for v in rec)]
    lines+=['IcArtEnd:','.popseg','']
    (ROOT/'src/ice_climbers_art.inc').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    out=ROOT/'chr/characters/ice-climbers-source.json'
    proof=dict(source_commit=COMMIT,original_manual='https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAAUE.pdf',
        original_source='https://github.com/cyneprepou4uk/NES-Games-Disassembly/tree/'+COMMIT+'/Ice%20Climber',
        source_hashes={p.name:digest(p)for p in(ROOT/'chr/characters').glob('ice-climbers-source-*')if p.is_file()},
        unique_pairs=sum(map(len,pages)),pages=len(pages),CHR_bytes=len(chrdata),CHR_sha256=digest(target),pose_count=len(records),records=facts,
        palette=dict(Popo=[0x30,0x11,0x26],Nana=[0x30,0x15,0x26]),
        assertions=['Actual original executable source renderer, no invented pose pixels','Exact complete original palette-index mask for every60pose','8x8 to8x16 lossless regrouping only','Selected hero uses host sprite palette0; original Popo/Nana three colors preserved'])
    out.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:proof[k]for k in['unique_pairs','CHR_bytes','pose_count','CHR_sha256']}))
if __name__=='__main__':main()
