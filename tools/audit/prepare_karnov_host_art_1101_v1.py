"""Pack Karnov's original body packets and projectile patterns into its lease."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from recover_karnov_actor_1101_v1 import ROM,EXPECTED
from recover_karnov_art_1101_v1 import Memory,pixels
from verify_native_relocation import NesMPU
O=R/'build/karnov-host-resource-base-1101-v1';A=R/'build/karnov-original-art-1101-v1'
REF=R/'build/karnov-native-reference-1101-v1/capture/reference.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not(O/'source-stage.json').exists()and sha(ROM)==EXPECTED
    art=json.loads((A/'art-controls.json').read_text());assert art['passed']
    for p,h in art['bindings'].items():assert sha(p)==h,p
    raw=ROM.read_bytes();chrdata=raw[16+131072:];body=bytearray((A/'body.chr').read_bytes());fixture=json.loads(REF.read_text())['initial_fixture']
    # Every body read is known from all32 states/two facings/hurt/clock cases.
    used={p:set()for p in range(5)}
    for pose in art['poses']:
        for i in range(1,len(pose['packet']),4):used[pose['packed_page']].add(pose['packet'][i]//2)
    free=[0,23,24,25,26,27,28];assert not used[3].intersection(free)
    source_tiles=[0x75,0x77,0x69,0x61,0x63,0x65,0x67];mapping={}
    assert fixture[0x16]==12
    for tile,pair in zip(source_tiles,free):
        ppu=(tile&1)*4096+(tile&254)*16;assert ppu//1024==5
        pattern=chrdata[12*1024+(ppu&1023):12*1024+(ppu&1023)+32];assert len(pattern)==32
        body[3*1024+pair*32:3*1024+pair*32+32]=pattern
        mapping[tile]=192+pair*2
    # Prove every original body pattern remains untouched after this packing.
    for pose in art['poses']:
        for i in range(1,len(pose['packet']),4):
            at=pose['packed_page']*1024+pose['packet'][i]*16
            assert body[at:at+32]==(A/'body.chr').read_bytes()[at:at+32]
    # Compact64 body packet pointers +64 physical-page selectors. Metadata
    # is copied to C2/D000 so native farcalls can read it while A3 is unmapped.
    blob=bytearray(192);packets={};rows=[]
    for face in [0,128]:
        for state in range(32):
            pose=next(p for p in art['poses']if p['state']==state and p['facing']==face and not p['hurt']and not p['phase'])
            source_packet=pose['packet']
            cells=[source_packet[i:i+4]for i in range(1,len(source_packet),4)]
            # Native MetaspriteRenderLoop consumes records backwards. Reverse
            # storage so hardware OAM retains the donor's exact sprite order.
            packet=bytes([source_packet[0],*(v for cell in reversed(cells)for v in cell)])
            if packet not in packets:packets[packet]=0xd000+len(blob);blob.extend(packet)
            pointer=packets[packet];index=state+(32 if face else 0)
            blob[index]=pointer&255;blob[64+index]=pointer>>8;blob[128+index]=pose['packed_page'];rows.append(dict(index=index,pointer=pointer,page=pose['packed_page'],packet=list(packet)))
    # Execute the unmodified original shot renderer; compare source pattern
    # pixels to their remapped physical page, across source modes/flags/clocks.
    count=0;digest=hashlib.sha256();observed=set()
    for mode,flag,clock in itertools.product([0,1,2,8],[0,0x84,0xc4,0x94,0xa4,0xb4],range(32)):
        m=Memory(raw,fixture);m[0x200:0x300]=[240,0,0,0]*64
        m[0x65]=mode;m[0xe8]=clock
        for n in range(9):m[0x6e+3*n]=flag;m[0x6f+3*n]=40+20*n;m[0x70+3*n]=120+16*(n%3)
        c=NesMPU(memory=m,pc=0xa152);c.sp=224;c.stPushWord(0x5aff)
        for _ in range(4000):
            if c.pc==0x5b00:break
            assert m[c.pc]!=0,('Original shot renderer BRK',hex(c.pc));c.step()
        else:raise AssertionError('Original shot renderer bound')
        for n in range(9):
            y,t,a,x=m[0x22c+4*n:0x230+4*n]
            if y>=240:continue
            observed.add(t);assert t in mapping,(mode,flag,clock,t)
            source=chrdata[12*1024+(((t&254)*16)&1023):12*1024+(((t&254)*16)&1023)+32]
            packed=body[3*1024+(mapping[t]-192)*16:3*1024+(mapping[t]-192)*16+32]
            assert pixels(source,a)==pixels(packed,a)
            digest.update(bytes([mode,flag,clock,n,y,t,a,x]));count+=1
    assert observed==set(source_tiles)
    (O/'kr-pose-meta.bin').write_bytes(blob);(O/'kr-body.chr').write_bytes(body)
    (O/'kr-shot-tiles.bin').write_bytes(bytes(mapping[t]for t in source_tiles))
    result=dict(passed=True,native=False,installed=False,donor_sha256=EXPECTED,body_cases_preserved=len(art['poses']),body_profiles=64,unique_packets=len(packets),metadata_bytes=len(blob),metadata_base=0xd000,shot_render_cases=768,visible_shot_cells=count,source_shot_CHR_page=12,source_sprite_window=5,host_physical_page=410,host_sprite_window=3,source_tiles=source_tiles,host_tiles=[mapping[t]for t in source_tiles],free_pairs_used=free,shot_trace_sha256=digest.hexdigest(),profiles=rows,scope='Actual original A152 projectile renderer, unchanged pattern pixels, exact64 body packets in native OAM order and preservation of every256body-case read. Source shadow16=12 is from the cold original native fixture. Native PPU publication remains a later check.',bindings={str(p.resolve()):sha(p)for p in [Path(__file__),ROM,REF,A/'art-controls.json',A/'body.chr',O/'kr-pose-meta.bin',O/'kr-body.chr',O/'kr-shot-tiles.bin']})
    (O/'render-art.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items()if k not in ['profiles','bindings']}))

if __name__=='__main__':main()
