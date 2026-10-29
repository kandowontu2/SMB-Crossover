"""Lossless original-executable SMB2 body/carry art, no painted replacements."""
from pathlib import Path
import json
from py65.devices.mpu6502 import MPU
import prepare_smb2_roster_native_v1 as D

ROOT=D.ROOT; OUT=D.OUT; ANIMS=[0,2,4,6,7,8,9,10]


def call(m,name,x=0,y=0,a=0):
    l=D.labels(); c=MPU(memory=m,pc=l[name]);c.sp=0xfd;c.p=0x24;c.x=x;c.y=y;c.a=a
    m[0x1fe]=0xfe;m[0x1ff]=0x7f
    for _ in range(50000):
        if c.pc==0x7fff:
            assert c.sp==255;return c
        assert m[c.pc]!=0,(name,hex(c.pc));c.step()
    raise AssertionError((name,'no return',hex(c.pc)))


def pattern(raw,m,t,l):
    start=(t&1)*4096+(t&254)*16
    if start<4096:page=m[l['SpriteCHR1']+start//1024]
    else:
        latch=m[l['BackgroundCHR1']+(start-4096)//2048]
        page=(latch&254)+(start%2048)//1024
    off=16+131072+page*1024+(start&1023)
    return raw[off:off+32],page


def main():
    OUT.mkdir(exist_ok=True);l=D.labels();raw=D.ROM.read_bytes()
    assert D.digest(raw)==D.SHA
    pages=[bytearray(1024)for _ in range(12)];records=[];keys={};pool=[];cases=[];seen={}
    # Stable semantic slots keep the common original geometry shared across
    # classes. Native eyeD5/D7/D9 is one role, actual pixels remain class-owned.
    slots={t:t//2 for t in range(0,52,2)}
    slots.update({180:26,182:27,213:28,215:28,217:28,251:29})
    for char in range(4):
        for size in range(2):
            profile=char*2+size
            for anim in ANIMS:
                for held in range(2):
                    for face in range(2):
                        m=D.original();m[0x200:0x300]=bytes([0xf8])*256
                        for n,v in dict(CurrentCharacter=char,PlayerCurrentSize=size,
                            PlayerAnimationFrame=anim,HoldingItem=held,PlayerDirection=face,
                            PlayerScreenX=80,PlayerScreenYLo=80).items():m[l[n]]=v
                        call(m,'LoadWorldCHRBanks');c=call(m,'RenderPlayer')
                        oam=[list(m[p:p+4])for p in range(0x200,0x300,4)if m[p]<240]
                        assert len(oam)==5
                        parts=[];source_pages=[]
                        for y,t,atr,x in reversed(oam):
                            data,page=pattern(raw,m,t,l);slot=slots[t]
                            key=(profile,slot)
                            assert key not in seen or seen[key]==data,(key,t,anim)
                            seen[key]=data;pages[profile][slot*32:slot*32+32]=data
                            parts += [slot*2,atr,(y-80)&255,(x-80)&255]
                            source_pages.append(page)
                        record=bytes([20]+parts)
                        if record not in keys:keys[record]=len(pool);pool.append(record)
                        records.append(keys[record])
                        cases.append(dict(native_character=char,size=size,animation=anim,
                            held=held,face=face,record=keys[record],page=profile,
                            source_OAM=oam,source_CHR_pages=source_pages,cycles=c.processorCycles))
    # Actual original vegetable renderer; no stock Samus/world-item substitute.
    object_records=[]
    for kind in [0x32,0x33]:
        for frame in [0,8]:
            for face in [0,1]:
                m=D.original(1);m[0x200:0x300]=bytes([0xf8])*256
                for n,v in dict(SpriteTempScreenX=80,SpriteTempScreenY=80,
                    ObjectType=kind,EnemyState=1,EnemyMovementDirection=face,
                    ObjectAnimationTimer=frame).items():m[l[n]]=v
                m[l['ObjectAttributes']]=m[l['ObjectAttributeTable']+kind]
                m[l['EnemyArray_46E']]=m[l['EnemyArray_46E_Data']+kind]
                call(m,'LoadWorldCHRBanks');c=call(m,'RenderSprite')
                oam=[list(m[p:p+4])for p in range(0x200,0x300,4)if m[p]<240]
                assert oam,('no actual vegetable art',kind,frame,face)
                parts=[]
                for y,t,atr,x in reversed(oam):
                    data,page=pattern(raw,m,t,l)
                    key=(8,data)
                    slot=next((i for i in range(32)if bytes(pages[8][i*32:i*32+32])==data),None)
                    if slot is None:
                        slot=next(i for i in range(32)if not any(pages[8][i*32:i*32+32]))
                        pages[8][slot*32:slot*32+32]=data
                    parts += [(slot*2)|0x81,atr,(y-80)&255,(x-80)&255]
                record=bytes([len(parts)]+parts)
                if record not in keys:keys[record]=len(pool);pool.append(record)
                object_records.append(keys[record])
                cases.append(dict(native_object=kind,frame=frame,face=face,record=keys[record],
                    page=8,source_OAM=oam,cycles=c.processorCycles))
    lines=['; Generated from genuine original RenderPlayer/LoadWorldCHR and RenderSprite.',
        '; Original pattern bytes incl actual page25 eyes and page9 Peach skirt retained.',
        '.pushseg','.segment "CD_GFX"','S2ArtStart:',
        'S2BodyRecord: .byte '+','.join(str(v)for v in records),
        'S2ObjectRecord: .byte '+','.join(str(v)for v in object_records),
        'S2ArtLo: .byte '+','.join('<S2Art'+str(i)for i in range(len(pool))),
        'S2ArtHi: .byte '+','.join('>S2Art'+str(i)for i in range(len(pool)))]
    for i,record in enumerate(pool):lines.append('S2Art'+str(i)+': .byte '+','.join(str(v)for v in record))
    lines+=['S2ArtEnd:','.assert S2ArtEnd-S2ArtStart<=2048,error,"SMB2 ART budget"','.popseg']
    art=ROOT/'src/smb2_roster_art.inc';art.write_text('\n'.join(lines)+'\n')
    chr=ROOT/'chr/characters/smb2-roster.chr';chr.write_bytes(b''.join(pages))
    size=len(records)+len(object_records)+len(pool)*2+sum(map(len,pool))
    assert size<=2048,('ART overflow',size,len(pool))
    result=dict(status='SOURCE_GENERATED_ORIGINAL_RENDERERS_NOT_NATIVE',
        original=D.binding(D.ROM),cases=cases,body_cases=256,object_cases=8,
        unique_records=len(pool),ART_bytes=size,CHR_bytes=12288,
        used_pages=[i for i,p in enumerate(pages)if any(p)],
        role_contract='Original bodypalette0 and eyepalette1 remain separate roles. Host must compose genuine colors without stealing world/pickup palettes; source-pattern equality is not all-area NES RGB equality.',
        outputs=[D.binding(art),D.binding(chr)],tool=D.binding(__file__))
    p=OUT/'art-source.json';p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(output=D.binding(p),records=len(pool),ART_bytes=size,CHR_bytes=12288),indent=2))


if __name__=='__main__':main()
