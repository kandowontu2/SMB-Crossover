"""Native8x16 body bytes/capacity and exact original body pixel differential."""
import collections,json,zipfile
from pathlib import Path
import prepare_dkjr_native_body_1102_v10 as P
import check_hogan_current_bounded_v1 as N
R=P.R;O=P.O;W=P.W;D=P.D


def main():
    q=json.loads((O/'native-body-v10-layout.json').read_text());L=q['labels'];blob=(O/'native-body-v10.bin').read_bytes();assert W.P.sha(blob)==q['code_SHA256']
    prior=(O/'native-victim-v9.bin').read_bytes();assert blob[:len(prior)]==prior
    proof=json.loads((O/'native-victim-v9-CPU.json').read_text());assert proof['passed']and W.P.sha(prior)==proof['component_SHA256']
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');b['raw']=P.CURRENT.read_bytes();assert W.P.sha(b['raw'])==P.PIN
    with zipfile.ZipFile(R/'docs/qa/checkpoints/2026-11-02/dkjr-source-core-v1/inputs.zip')as z:
        atlas=z.read('generated/body.chr')[:1408];meta=json.loads(z.read('generated/body-poses.json'))
    raw=D.donor()[16400:];active,_=D.active();seed=bytes(active.memory[:2048]);counts=collections.Counter();cycles=[];minimum_sp=255
    m=N.Bus(b);m.ram[3][:len(blob)]=blob;m.ram[2][:2048]=seed;m.raw_page(1,3);m.raw_page(2,2)
    def put(name,value):m[N.address(b,name)]=value
    def get(name):return N.get(m,name)
    def call():
        nonlocal minimum_sp
        c=N.NesMPU(memory=m,pc=L['DkjrNativeDrawBody']);c.a,c.x,c.y,c.p,c.sp=0x57,7,9,0xf1,224;c.stPushWord(0x5ffe)
        for _ in range(10000):
            if c.pc==0x5fff:break
            minimum_sp=min(minimum_sp,c.sp);assert m[c.pc]!=0;c.step()
        else:raise AssertionError(('body renderer bound',hex(c.pc)))
        assert c.sp==224 and(c.a,c.x,c.y)==(0x57,7,9)and c.p&0xfe==0xf0
        return bool(c.p&1),c.processorCycles
    def initialize(cells,cursor=24):
        m.ram[2][:2048]=seed;m.ram[2][0x210:0x230]=cells
        for i in range(256):m[0x200+i]=(0xa5+i)&255
        put('CurrentOAMOffset',cursor);put('GuestOamRotationActive',0);put('RgOamRotation',0)
        put('ObjectMetasprite',0x41);put('SmPosePtr',0x99);m[N.address(b,'SmPosePtr')+1]=0xc8
    def assert_header():
        assert get('ObjectMetasprite')==0 and get('SmPosePtr')+256*m[N.address(b,'SmPosePtr')+1]==N.address(b,'ObjectMetasprite')
    def source_cells(base,mode):
        donor=D.Bus();donor[:2048]=seed;donor[0:3]=bytes([32,64,base]);c=D.T.NesMPU(memory=donor,pc=0);D.T.run(c,0xe9ee,mode,0,0,0x20)
        return bytes(donor[0x210:0x230])
    def pixel(chrdata,tile,x,y):
        at=tile*16+y;bit=7-x;return(chrdata[at]>>bit&1)|((chrdata[at+8]>>bit&1)<<1)
    def raster(cells,paired=False):
        out=bytearray(512)
        for at in range(0,len(cells),4):
            y,t,a,x=cells[at:at+4]
            for dy in range(16 if paired else 8):
                for dx in range(8):
                    px=7-dx if a&64 else dx;py=dy;tile=(t&254)+(py//8)if paired else t
                    value=pixel(atlas if paired else raw,tile,px,py&7)
                    ox=x-32+dx;oy=y-64+dy;assert 0<=ox<32 and 0<=oy<16
                    out[oy*32+ox]=value
        return out
    pose_rows=[]
    for base in range(0,88,8):
        for mode in [0,1]:
            cells=source_cells(base,mode)
            for cursor in range(256):
                initialize(cells,cursor);before=bytes(m[0x200:0x300]);state=bytes(m.ram[2][:2048]);smc=bytes(m[0x15a:0x17b]);maps=list(m.rawtags);r0=bytes(m[N.address(b,'R0'):N.address(b,'R0')+8])
                accepted,duration=call();expected=cursor!=0 and cursor%4==0 and cursor<=240
                assert accepted==expected and get('CurrentOAMOffset')==((cursor+16)&255 if expected else cursor)
                emitted=bytearray(before)
                if expected:
                    for i in range(4):
                        src=cells[i*8:i*8+4];emitted[cursor+4*i:cursor+4*i+4]=bytes([src[0],src[1]|1,(src[2]&0xe0)|3,src[3]])
                    cycles.append(duration)
                assert bytes(m[0x200:0x300])==emitted and bytes(m.ram[2][:2048])==state and smc==bytes(m[0x15a:0x17b])and maps==m.rawtags and r0==bytes(m[N.address(b,'R0'):N.address(b,'R0')+8]);assert_header()
                counts['all22_source_poses_all256_cursor_values_complete_pair_capacity']+=1
            initialize(cells);accepted,_=call();assert accepted
            native=bytes(m[0x218:0x228]);assert raster(cells)==raster(native,True)
            counts['original_body_pixels_exact']+=512
            pose_rows.append(dict(source_base=base,source_mode=mode,body_pairs=4,raster_SHA256=W.P.sha(raster(native,True))))
    cells=source_cells(0,0)
    for offset,value in [(0,240),(1,1),(1,88),(4,73),(5,3),(6,2),(7,33),(2,0x81),(6,0x81)]:
        bad=bytearray(cells);bad[offset]=value;initialize(bad);before=bytes(m[0x200:0x300]);accepted,_=call();assert not accepted and get('CurrentOAMOffset')==24 and before==bytes(m[0x200:0x300]);assert_header();counts['malformed_source_pair_rejects_before_native_OAM']+=1
    for rotation in [0,1,2,3,4,252,253]:
        initialize(cells);put('GuestOamRotationActive',1);put('RgOamRotation',rotation);before=bytes(m[0x200:0x300]);accepted,_=call()
        assert accepted==(rotation%4==0)and get('RgOamRotation')==rotation
        if not accepted:assert before==bytes(m[0x200:0x300])and get('CurrentOAMOffset')==24
        assert_header();counts['native_rotation_alignment_preserved_no_mask']+=1
    out=dict(passed=True,native_emulator=False,ROM_written=False,native_owner_admitted=False,base_ROM_SHA256=P.PIN,component_SHA256=q['code_SHA256'],component_bytes=len(blob),header_reserved_spare=8160-len(blob),checks=dict(counts),poses=pose_rows,minimum_CPU_SP=minimum_sp,draw_CPU=dict(minimum=min(cycles),maximum=max(cycles)),inherited_native_victim_prefix_SHA256=W.P.sha(prior),prefix_byte_identical=True,
        assumptions=['Native CHR pattern1 publishes the proven1408B atlas, not implemented by this leaf','Native palette3 contains the source body palette1 opaque RGB; actual PPU palette publication pending','Genuine source body cache comes from actual original pose/update; typed raw owner/public Draw ingress and native hardware still unqualified'],
        scope='Exact original source8x8 OAM versus paired native8x16 bytes/pixels, complete capacity/zero-full/malformed/rotation guards and stable unbanked zeroheader. Existing source/native victim code is byte-identical prefix of already qualified v9. No source animation replacement or actual hardware claim.',
        bindings={p.relative_to(R).as_posix():W.P.sha(p.read_bytes())for p in[Path(__file__),Path(P.__file__),O/'native-body-v10.s',O/'native-body-v10.bin',O/'native-body-v10-layout.json',O/'native-victim-v9-CPU.json']})
    (O/'native-body-v10-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in['passed','component_bytes','header_reserved_spare','component_SHA256','checks','minimum_CPU_SP','draw_CPU']}))


if __name__=='__main__':main()
