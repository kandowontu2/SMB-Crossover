"""Recover exact original Metal Storm body/shot art and source frame order."""
from pathlib import Path
import hashlib,itertools,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
import metal_storm_cpu_1101_v2 as M
OUT=ROOT/'build/metal-storm-render-host-1101-v7'
PACK=ROOT/'docs/qa/checkpoints/2026-11-01/metal-storm-original-component-v3/source-proof.zip'
V4=ROOT/'build/metal-storm-host-contract-1101-v4'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    OUT.mkdir(exist_ok=True)
    with zipfile.ZipFile(PACK)as z:body=z.read('assets/body.chr');old=json.loads(z.read('proof/art.json'))
    assert len(body)==4608
    (OUT/'body.chr').write_bytes(body+bytes(512));(OUT/'body-meta.bin').write_bytes((V4/'body-meta.bin').read_bytes())
    reference=M.boot()
    for tick in range(600):M.frame(reference,16 if tick in[120,121,300,301,480,481]else 0)
    initial=bytes(reference.memory[:2048]);palette=bytes(reference.memory.ppuread(0x3f10+i)for i in range(16))
    assert palette==bytes(old['packets'][0]['source_sprite_palette'])
    shapes=[];patterns=[];lookup={};events=[]
    # Visible projectile forms; source648 is a real2-frame spawn delay.
    # Negative83 impact frames are recovered too; lifecycle remains separately
    # source-verified before any actor integration is claimed.
    for typ,velocity,flags,phase in itertools.product([0x80,0x81,0x83],[0,12],[0,64,128,192],range(5)):
        c=M.machine();m=c.memory;m[:2048]=initial;m.regs[6:8]=[12,13];m.map()
        m[0x200:0x300]=bytes([240,0,0,0])*64
        values={0x482:128,0x49a:0,0x4b2:112,0x4ca:0,0x4e2:128 if typ==0x81 else 0,0x512:128,0x52a:typ,0x542:flags,0x55a:velocity,0x572:12 if not velocity else 0,0x64a:0,0x662:20,0x61a:0,0x632:phase,0x710:0,0x711:0,0x713:0,0x50:0,0x42:252}
        for a,v in values.items():m[a]=v
        table=m[0x800e]+256*m[0x800f];m[0x24]=table&255;m[0x25]=table>>8
        M.call(c,0xf282,x=2,y=0)
        m.regs[:6]=m[0x756:0x75c]
        assert c.y%4==0 and c.y<64
        cells=[]
        for slot in range(c.y//4):
            y,t,attr,x=m[0x200+4*slot:0x204+4*slot];at=(t&1)*4096+(t&254)*16
            pattern=bytes(m.ppuread(at+i)for i in range(32))
            if pattern not in lookup:lookup[pattern]=len(patterns);patterns.append(pattern)
            cells.append(dict(dx=x-128,dy=y+1-112,pattern_index=lookup[pattern],attributes=attr,source_tile=t))
        shapes.append(dict(type=typ,vertical=not velocity,flags=flags,phase=phase,cells=cells,active=m[0x512],retired=not m[0x512],source648=m[0x64a],source6A8=m[0x6aa]))
    assert len(patterns)<=32,len(patterns)
    (OUT/'shots.chr').write_bytes(b''.join(patterns)+bytes(1024-len(patterns)*32))
    # Compact3base projectile packets plus3impact packets (others are absent).
    # Native attributes/vertical doubling are derived from actual source forms.
    bases=[]
    for typ,vertical,phase in[(0x80,False,0),(0x81,False,0),(0x81,True,0),(0x83,False,0),(0x83,False,1),(0x83,False,2)]:
        r=next(v for v in shapes if(v['type'],v['vertical'],v['flags'],v['phase'])==(typ,vertical,0,phase))
        bases.append(r)
    blob=bytearray();pointers=[]
    for r in bases:
        pointers.append(len(blob));blob.append(len(r['cells'])*4)
        for cell in reversed(r['cells']):blob.extend([cell['pattern_index'],cell['attributes'],(cell['dy']-1)&255,cell['dx']&255])
    (OUT/'shot-meta.bin').write_bytes(blob)
    # Actual source event order, bounded trace only; no per-frame state files.
    for tick in range(32):
        frame=[]
        def observe(c):
            if c.pc in[0xad8c,0xdcae,0xf282,0x8eae,0x8e54]:
                if c.pc>=0x8000 and c.pc<0xa000 and c.memory.banks[0]!=4:return
                frame.append(dict(pc=f'{c.pc:04X}',slot=c.x,clock=c.memory[0x53]))
        M.frame(reference,0x40,trace=observe)
        if len(frame)>4 and len(events)<4:events.append(frame[:32])
    q=dict(passed=True,native=False,installed=False,admitted=False,body_contexts=208,body_patterns=144,body_pages=5,body_metadata_bytes=1002,shot_contexts=len(shapes),shot_patterns=len(patterns),shot_pages=1,shot_metadata_bytes=len(blob),shot_packet_offsets=pointers,source_sprite_palette=list(palette),body_packets=old['packets'],shot_packets=shapes,original_frame_order_samples=events,scope='Exact original F282 body packets reused from frozen proof; actual original negative80/81/83 renderer executed. CHR/palettes original, native OAM/publication/admission tested separately.',bindings={str(p.resolve()):sha(p)for p in[Path(__file__),Path(M.__file__),M.ROM,PACK,V4/'body-meta.bin',OUT/'body.chr',OUT/'body-meta.bin',OUT/'shots.chr',OUT/'shot-meta.bin']})
    (OUT/'art.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items()if k not in['body_packets','shot_packets','bindings']}))
if __name__=='__main__':main()
