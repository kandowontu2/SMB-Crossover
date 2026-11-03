"""Original pixel/source-OAM controls for bounded native DK fruit/effects."""
import contextlib,io,itertools,json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O;W=A.W;D=W.P.D


def main():
    path=R/'tools/audit/check_dkjr_native_lifecycle_1102_v31.py'
    source=path.read_text().replace('native-lifecycle-v30','native-effects-v39').replace('native-lifecycle-','native-effects-').replace('-v30.bin','-v39.bin')
    env={'__name__':'dk_effects_fixture','__file__':str(path)};exec(compile(source,str(path),'exec'),env)
    b,seed,L,q=env['fixture']();env['direct'](seed,L['DkConstruct'])
    tiles=D.donor()[16400:];rows={i:(O/f'native-art-{i}-v38.chr').read_bytes()for i in [959,960,961]}
    def pixel(data,tile,x,y):
        at=tile*16+y;shift=7-x
        return ((data[at]>>shift)&1)|(((data[at+8]>>shift)&1)<<1)
    def native_pixel(tile,x,y):
        top=tile&254;page=[959,960,961,961][top//64];index=(top&63)+(y//8)
        return pixel(rows[page],index,x,y&7)
    def fresh(offset=24):
        m=N.fork(seed);m.ram[2][0x200:0x300]=bytes([255])*256;m.ram[2][0x9a:0x9e]=bytes(4);m.ram[2][0x434]=0
        N.put(m,CurrentOAMOffset=offset,GuestOamRotationActive=0,RgOamRotation=0)
        m[0x200:0x300]=[0xa5]*256
        return m
    def draw(m,entry='DkNativeEffects'):
        state=bytes(m.ram[2][:0x800]);scratch=bytes(m[3:11]);smc=bytes(m[0x15a:0x17b]);cursor=N.get(m,'CurrentOAMOffset')
        c=env['direct'](m,L[entry]);assert c.p&1
        assert state==bytes(m.ram[2][:0x800])and scratch==bytes(m[3:11])and smc==bytes(m[0x15a:0x17b])
        end=N.get(m,'CurrentOAMOffset');return cursor,end,[list(m[0x200+i:0x204+i])for i in range(cursor,256 if end==0 and cursor else end,4)]
    hanging=0;falling=0;hits=0;points=0;pixels=0
    for kind,slot in itertools.product(range(3),range(4)):
        m=fresh();m.ram[2][0x434]=slot+1;m.ram[2][0x9a+slot]=1;m.ram[2][0x42c+slot]=0xa4+4*kind;m.ram[2][0x420+slot]=96;m.ram[2][0x428+slot]=80;m.ram[2][0x8d+slot]=0 if kind==0 else 2
        start,end,cells=draw(m);assert end==start+8 and cells==[[79,(88+4*kind)|1,2 if kind==0 else 1,96],[79,(90+4*kind)|1,2 if kind==0 else 1,104]]
        for column,cell in enumerate(cells):
            for y in range(16):
                for x in range(8):assert native_pixel(cell[1],x,y)==pixel(tiles,0x150+4*kind+2*column+y//8,x,y&7);pixels+=1
        hanging+=1
    for kind in range(3):
        oracle=D.Bus();oracle[0:5]=[96,80,0 if kind==0 else 2,4,0x30];c=D.T.NesMPU(memory=oracle,pc=0);D.T.run(c,0xea06)
        oracle[2:4]=[0xa4+4*kind,0x22];D.T.run(c,0xe9fc)
        m=fresh();m.ram[2][0x230:0x240]=bytes(oracle[0x230:0x240]);start,end,cells=draw(m)
        assert end==start+8 and cells==[[80,(128+4*kind)|1,2 if kind==0 else 1,96],[80,(130+4*kind)|1,2 if kind==0 else 1,104]]
        for column,cell in enumerate(cells):
            for y in range(16):
                for x in range(8):assert native_pixel(cell[1],x,y)==pixel(tiles,0xa4+4*kind+2*column+y//8,x,y&7);pixels+=1
        falling+=1
    for tile in range(0x90,0x94):
        m=fresh();m.ram[2][0x2c0:0x2c4]=bytes([80,tile,1,96]);start,end,cells=draw(m);assert end==start+4 and cells==[[80,(140+2*(tile-0x90))|1,3,96]]
        for y in range(16):
            for x in range(8):assert native_pixel(cells[0][1],x,y)==(pixel(tiles,tile,x,y)if y<8 else 0);pixels+=1
        hits+=1
    point_tiles=[0xf1,0xf2,0x5e,0xf3,0xf4,0xf5,0xf6,0xf7]
    for index in range(7):
        oracle=D.Bus();oracle[0x200]=oracle[0x230]=255;oracle[5:7]=[96,80];oracle[0x4a]=1
        c=D.T.NesMPU(memory=oracle,pc=0);D.T.run(c,0xec3b,x=index,limit=100000)
        assert oracle[0x201]==point_tiles[index]and oracle[0x205]==0xf7
        m=fresh();m.ram[2][0x200:0x208]=bytes(oracle[0x200:0x208]);start,end,cells=draw(m)
        assert end==start+8 and cells==[[80,(112+2*index)|1,3,96],[80,127,3,104]]
        for column,cell in enumerate(cells):
            original=point_tiles[index]if column==0 else 0xf7
            for y in range(16):
                for x in range(8):assert native_pixel(cell[1],x,y)==(pixel(tiles,original,x,y)if y<8 else 0);pixels+=1
        points+=1
    bounded=0
    for offset,rotation in itertools.product([0,1,2,3,4,236,240,244,248,252],[0,1,4]):
        m=fresh(offset);m.ram[2][0x434]=4
        for slot in range(4):m.ram[2][0x9a+slot]=1;m.ram[2][0x42c+slot]=0xa4;m.ram[2][0x420+slot]=40+32*slot;m.ram[2][0x428+slot]=80
        N.put(m,GuestOamRotationActive=1,RgOamRotation=rotation);before=bytes(m[0x200:0x300]);draw(m)
        end=N.get(m,'CurrentOAMOffset')
        if offset==0 or offset&3 or rotation&3:assert end==offset and before==bytes(m[0x200:0x300])
        else:
            expected=min(32,256-offset);assert end==(offset+expected)&255
            assert bytes(m[0x200:0x200+offset])==before[:offset]
            assert bytes(m[0x200+offset+expected:0x300])==before[offset+expected:]
        bounded+=1
    # Real public Draw transports this exact combined private body/effects
    # leaf. The body originalOAM stays genuine; effects add no duplicate body.
    m=N.fork(seed);N.put(m,CurrentOAMOffset=24,GuestOamRotationActive=0,RgOamRotation=0)
    state=bytes(m.ram[2][:0x800]);z=N.invoke(m,'HuDraw',a=85,x=7,y=91,p=0x31)
    assert z['P']&1 and N.get(m,'CurrentOAMOffset')==40 and bytes(m.ram[2][:0x800])==state
    assert N.get(m,'ObjectMetasprite')==0 and N.get(m,'SmPosePtr')+256*N.get(m,'SmPosePtr',1)==W.address(b,'ObjectMetasprite')
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,checks=dict(hanging_original_BG_glyph_and_palette_cases=hanging,falling_original_EA06_E9FC_pose_cases=falling,original_hit_tile_cases=hits,original_EC3B_point_popup_cases=points,native_pixel_comparisons=pixels,capacity_rotation_guard_cases=bounded,actual_authenticated_HuDraw_body_and_zeroheader=True),
        body_bytes=q['body_bytes'],header_spare=q['header_spare'],metadata_spare=q['metadata_spare'],
        scope='Original pixels and original falling/point OAM producers versus bounded native8x16 output. Explicit legal isolated art/worldfruit fixtures only; no authored native level fruit placement, earned native fruit traversal, emulator or final current-owner cookie claim.',
        remaining=q['remaining'],bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),path,O/'native-effects-v39-layout.json',O/'native-effects-v39.bin',O/'native-atlas-v38.json']})
    (O/'native-effects-v40-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','body_bytes','header_spare','checks']}))


if __name__=='__main__':main()
