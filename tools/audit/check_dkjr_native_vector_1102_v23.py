"""CPU proof of actual DK vector/Fresh/Main/Draw, with unfinished rows visible."""
import collections,json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O;W=A.W;D=W.P.D


def main():
    q=json.loads((O/'native-vector-v22-layout.json').read_text());L=q['labels'];blob=(O/'native-vector-v22.bin').read_bytes();pause=(O/'native-vector-pause-v22.bin').read_bytes();mainpart=(O/'native-vector-main-v22.bin').read_bytes()
    old=json.loads((O/'native-body-v10-layout.json').read_text());oldcore=(O/'native-body-v10.bin').read_bytes();oldpause=(O/'native-pause-v16.bin').read_bytes()
    import re
    OL={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'native-pause-v16.lbl').read_text(),re.M)}
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');b['raw']=A.BASE.read_bytes();assert A.sha(b['raw'])==A.PIN
    counts=collections.Counter();rows=[]
    def call(m,target):
        c=N.NesMPU(memory=m,pc=target);c.a,c.x,c.y,c.p,c.sp=0x55,7,91,0xb1,224;c.stPushWord(0x5ffe)
        for _ in range(100000):
            if c.pc==0x5fff:break
            assert m[c.pc]!=0,('vector BRK',hex(target),hex(c.pc));c.step()
        else:raise AssertionError(('vector call bound',hex(target)))
        assert c.sp==224;return c
    def fresh(camera,x,y):
        m=N.Bus(b);m.ram[3][:len(blob)]=blob;m.ram[2][0x1540:0x1540+len(pause)]=pause;m.ram[2][0x165e:0x165e+len(mainpart)]=mainpart;m.raw_page(1,3);m.raw_page(2,2)
        N.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=0,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,TimerControl=0,AreaType=1,AreaPointer=0x25,WorldNumber=0,LevelNumber=0,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,ScreenRight_X_Pos=(camera+255)&255,ScreenRight_PageLoc=(camera+255)>>8,Player_X_Position=(camera+x)&255,Player_PageLoc=(camera+x)>>8,Player_Y_Position=y,Player_Y_HighPos=1,VRAM_Buffer1_Offset=0)
        return m
    for camera in [0,1,255,256,511]:
        for x,y in [(40,176),(112,144),(180,96)]:
            m=fresh(camera,x,y);z=call(m,0xa000+15*3);assert z.p&1
            oracle=D.Bus();oracle[:2048]=bytes(2048);oracle[0x4a]=1;oracle[0x49]=0;cpu=D.T.NesMPU(memory=oracle,pc=0);D.T.run(cpu,0xca82)
            oracle[0:3]=bytes([x-8,y+15,0x18]);D.T.run(cpu,0xe9ee)
            for i in range(8):oracle[0x212+4*i]=1
            # Native fruit records intentionally start unavailable until the
            # world producer supplies them. All other source constructor
            # variables through99 and genuine eight source body cells match.
            indices=[i for i in range(0x9a)if i not in list(range(0x8d,0x94))]
            assert all(m.ram[2][i]==oracle[i]for i in indices),(camera,x,y,'source constructor state',[(i,m.ram[2][i],oracle[i])for i in indices if m.ram[2][i]!=oracle[i]])
            assert bytes(m.ram[2][0x210:0x230])==bytes(oracle[0x210:0x230])
            assert m.ram[2][0x65]==36 and m.ram[2][0x6b]==1 and m.ram[2][0x8fe]==1
            N.put(m,CurrentOAMOffset=24,GuestOamRotationActive=0,RgOamRotation=0);z=call(m,0xa006);assert z.p&1 and N.get(m,'CurrentOAMOffset')==40
            assert N.get(m,'ObjectMetasprite')==0 and N.get(m,'SmPosePtr')+256*m[W.address(b,'SmPosePtr')+1]==W.address(b,'ObjectMetasprite')
            counts['actual_Fresh_vector_original_initialize_pose_and_native_Draw_vector']+=1
    # Real linked vector/Main versus the same already qualified source/native
    # phase before vector relocation. Source movement and state stay exact;
    # Main publishes only the declared native velocity/state cache afterwards.
    m=fresh(0,40,176);call(m,0xa02d)
    for name in ['Block_Buffer_1','Block_Buffer_2']:
        for row in [11,12]:m[W.address(b,name)+row*16:W.address(b,name)+row*16+16]=[0x54]*16
    ref=N.fork(m);ref.ram[3][:]=bytes(8192);ref.ram[3][:len(oldcore)]=oldcore;ref.ram[2][0x1540:0x1540+len(oldpause)]=oldpause
    ys=[];xs=[];directions=[]
    for epoch,pad in enumerate([0]*10+[1]*24+[129]+[2]*44+[0]*30,1):
        for mm in [m,ref]:N.put(mm,SavedJoypadBits=pad,VRAM_Buffer1_Offset=0)
        oldx=N.get(m,'Player_X_Position');oldy=N.get(m,'Player_Y_Position');za=call(ref,OL['DkPauseMain']);zn=call(m,0xa000)
        assert bool(za.p&1)==bool(zn.p&1)
        # Scratch source pointers are permitted to follow the new code/data
        # relocation; compare every source actor/fruit/OAM byte from04 upward.
        a=bytearray(ref.ram[2][4:0x800]);c=bytearray(m.ram[2][4:0x800]);assert a==c,(epoch,[(i+4,a[i],c[i])for i in range(len(a))if a[i]!=c[i]][:12])
        assert (N.get(m,'Player_X_Position'),N.get(m,'Player_Y_Position'))==(N.get(ref,'Player_X_Position'),N.get(ref,'Player_Y_Position'))
        assert N.get(m,'Player_X_Scroll')==(N.get(m,'Player_X_Position')-oldx)&255
        assert N.get(m,'Player_X_Speed')==((N.get(m,'Player_X_Position')-oldx)<<4)&255
        assert N.get(m,'Player_Y_Speed')==(N.get(m,'Player_Y_Position')-oldy)&255
        xs.append(N.get(m,'Player_X_Position'));ys.append(N.get(m,'Player_Y_Position'));directions.append(m.ram[2][0x54]);counts['actual_Main_vector_source_phase_relocation_native_velocity_commit']+=1
    assert min(ys)==161,(min(ys),ys)
    assert directions[34:78]==[4]*44,directions[34:78]
    # Explicitly unfinished rows reject without source/native state mutation.
    for i in q['unimplemented_rows']:
        state=bytes(m.ram[2]);native=bytes(m[:256])+bytes(m[0x200:0x800]);z=call(m,0xa000+i*3)
        assert not z.p&1 and state==bytes(m.ram[2])and native==bytes(m[:256])+bytes(m[0x200:0x800]);counts['unfinished_vector_rows_explicit_private_rejection_only']+=1
    out=dict(passed=True,qualified=False,native_owner_admitted=False,ROM_written=False,compiled_body_bytes=len(blob),body_end=q['body_end'],header_spare=q['header_spare'],vector_entries=38,implemented_rows=q['implemented_vector_rows'],checks=dict(counts),trajectory=dict(minimum_native_anchor_Y=min(ys),source_jump_rise=176-min(ys),final_native_X=xs[-1],original_latched_direction_preserved_during44air_updates=True),
        scope='Actual compiled A000 vector/Fresh/Main/Draw in conditional private overlays with exact original CA82/E9EE constructor and previously qualified source phase differential. Native services execute in isolated Mario0 fixtures. No shared/public raw40 admission, actual GameCore/IRQ or Mesen claim;35 rows remain unfinished.',
        remaining=q['remaining'],bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),O/'native-vector-v22-layout.json',O/'native-vector-v22.bin',O/'native-vector-main-v22.bin',O/'native-vector-pause-v22.bin',O/'native-body-v10.bin',O/'native-pause-v16.bin']})
    (O/'native-vector-v23-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','compiled_body_bytes','header_spare','checks','trajectory']}))


if __name__=='__main__':main()
