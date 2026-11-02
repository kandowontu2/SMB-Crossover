"""Source recovery differentials and memory-only current-cartridge host calls.

No candidate ROM or emulator is written/launched. All fixtures are memory-only;
the output is one aggregate receipt. Root still owns real ingress/native runs.
"""
from pathlib import Path
import copy,hashlib,json,re,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit'),str(R/'tools/reference')]
import check_hogan_current_bounded_v1 as M
import excitebike_original_cpu_1101_v2 as E
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from prepare_excitebike_dispatch_1101_v1 import labels,sha,save,O
from prepare_excitebike_host_1101_v1 import BASE,PIN

def source_controls():
    lab=labels(O/'host.lbl');image=(O/'host-kernel.bin').read_bytes();cases=0
    seed=(R/'build/excite-prince-component-1101-v2/state-799.bin').read_bytes()
    for name,pc in [('ExCrashAll',0xddd1),('ExRecoveryAll',0xd918),('ExLaneAll',0xe96c)]:
      for case in range(384):
        ram=bytearray(seed);ram[0x3f7]=0;ram[0x9c]=case%6;ram[0x98]=[0,1,255][case%3]
        ram[0x3f]=case&255;ram[0x4c]=(case>>2)&3;ram[0x94]=(case>>4)%5
        ram[0x90]=(case*79)&255;ram[0x26]=case%8;ram[0x2a]=case%9;ram[0x36]=case%7
        ram[0xb0]=[0,2][case&1];ram[0x58]=case&1;ram[0x370]=case&1
        ram[0x3e0]=[0,32][(case>>2)&1]
        if name=='ExLaneAll':
            for actor in range(4):ram[0xa4+actor]=0;ram[0xb8+actor]=8+case%50;ram[0xdc+actor]=[0,1,255][case%3]
        old=E.machine();list.__setitem__(old.memory,slice(0,2048),ram)
        if name=='ExLaneAll':list.__setitem__(old.memory,0xea07,0x60)
        class Flat(list):pass
        new=E.T.NesMPU(memory=Flat([0]*65536));new.memory[0xa000:0xb800]=image;new.memory[0xc000:0xc800]=ram
        args=dict(a=0x55,x=case&3,y=91,p=0x20|(case&13))
        a=E.call(old,pc,**args);z=E.T.run(new,lab[name],**args)
        expected=bytearray(old.memory[:256]+old.memory[512:2048])
        actual=bytearray(new.memory[0xc000:0xc100]+new.memory[0xc200:0xc800])
        if name=='ExRecoveryAll':
            pointer=expected[0]+256*expected[1]
            assert actual[0]+256*actual[1]==lab[f'ExRec_{pointer:04X}']
            actual[:2]=expected[:2] # Typed relocated code pointer, not game state.
        assert expected==actual,(name,case,[(i,a,z)for i,(a,z)in enumerate(zip(expected,actual))if a!=z][:10])
        assert a[:3]==z[:3]and a[4]==z[4]and a[3]&0xef==z[3]&0xef,(name,case,a,z)
        assert not any(new.memory[:256]);cases+=1
    return cases

def fixture(*,scene=False):
    assert sha(BASE)==PIN;b=scoped_load(BASE);raw=bytearray(b['raw'])
    resident=labels(O/'dispatch.lbl')
    for off,file in [(0x740,'dispatch-body.bin'),(0xe00,'dispatch-loader.bin'),(0x108c,'dispatch-veneers.bin'),(0x1031,'dispatch-foreign.bin'),(0x1105,'dispatch-foreign-bank.bin')]:
        data=(O/file).read_bytes();at=16+65*8192+off
        assert raw[at:at+len(data)]==bytes([255])*len(data)
        raw[at:at+len(data)]=data
    if scene:
        for off,file in [(0x7e9,'scene-gate.bin'),(0x1062,'scene-own.bin'),(0x7fa,'menu-gate.bin'),(0x1077,'menu-body.bin'),(0x10fb,'menu-done.bin')]:
            data=(O/file).read_bytes();at=16+65*8192+off
            assert raw[at:at+len(data)]==bytes([255])*len(data)
            raw[at:at+len(data)]=data
    at=16+65*8192+resident['ExCookie']-0xa000
    raw[at:at+16]=(O/'host-cookie.bin').read_bytes()
    payload=(O/'host-kernel.bin').read_bytes()+(O/'host-metadata.bin').read_bytes()+(O/'body-native.chr').read_bytes()
    for i,page in enumerate(range(728,739)):
        at=1048592+page*1024;assert not any(raw[at:at+1024]);raw[at:at+1024]=payload[i*1024:i*1024+1024]
    b['raw']=bytes(raw);b['segs']['excitebike_resident']={'start':str(0xa000),'ooffs':str(16+65*8192)}
    for n,a in resident.items():b['syms'][n]={'val':str(a),'seg':'excitebike_resident'}
    if scene:
        for n,a in labels(O/'scene.lbl').items():b['syms'][n]={'val':str(a),'seg':'excitebike_resident'}
    for row in range(37):b['syms'][f'ExService{row}']={'val':str(0xb08c+3*row),'seg':'excitebike_resident'}
    m=M.fresh(b);M.put(m,SelectedCharacter=37,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,
        Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160,ReloadCHRBank=1,Player_X_Position=80,Player_PageLoc=1,
        Player_Y_Position=192,Player_Y_HighPos=1,PlayerFacingDir=1,PlayerSize=1,
        ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,GameEngineSubroutine=8,GamePauseStatus=0)
    for name in ['Block_Buffer_1','Block_Buffer_2']:
        at=address(b,name)
        for y in range(13):
            for x in range(16):m[at+y*16+x]=0x54 if y>=11 else 0
    if scene:
        assert M.invoke(m,'ExScene')['P']&1
    else:
        assert M.invoke(m,'ExLoad')['P']&1
        assert M.invoke(m,'ExService15')['P']&1
    assert m.ram[2][0x800]==167 and M.get(m,'Player_Y_Position')==176
    M.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,Player_State=0,Player_Y_Speed=0)
    return m,hashlib.sha256(raw).hexdigest()

def tick(m,frame,pad):
    M.put(m,FrameCounter=frame&255,SavedJoypadBits=pad)
    return M.invoke(m,'ExService0',a=0x55,x=7,y=91,p=0xf1)
def wx(m):return M.get(m,'Player_X_Position')+256*M.get(m,'Player_PageLoc')

def source_jump_rise():
    c=E.machine();list.__setitem__(c.memory,slice(0,2048),bytes(2048))
    c.memory[0x90]=0x20;c.memory[0x94]=3;c.memory[0x8c]=176;c.memory[0x5c]=0x80
    E.call(c,0xdd38,x=0);minimum=176
    for frame in range(40):
        c.memory[0x4c]=frame&3;E.call(c,0xdcf2,x=0)
        minimum=min(minimum,c.memory[0x8c])
        if c.memory[0x8c]>=176 and frame>2:break
    return 176-minimum

def main():
    source=source_controls();expected_rise=source_jump_rise();seed,digest=fixture();checks={};rows={};maximum=0
    for name,segments in [
        ('idle',[(0,120)]),('right',[(1,240)]),('stop',[(1,180),(0,180)]),
        ('reverse',[(1,180),(2,240)]),('jump',[(1,180),(129,1),(1,119)]),
        ('lean-jump',[(1,180),(137,1),(9,28),(1,140)]),
        ('lean-recovery',[(1,180),(9,160),(1,240)]),('turbo-heat',[(65,900),(0,180)])]:
        m=M.fork(seed);frame=0;xs=[];ys=[];crashes=set();recoveries=set();phases=set();poses=set();speeds=[]
        for pad,count in segments:
            for _ in range(count):
                z=tick(m,frame,pad);frame+=1;maximum=max(maximum,z['CPU'])
                assert [z[n]for n in ['A','X','Y']]==[0x55,7,91]and z['P']&1
                xs.append(wx(m));ys.append(M.get(m,'Player_Y_Position'));crashes.add(m.ram[2][0x98]);recoveries.add(m.ram[2][0x9c])
                phases.add(m.ram[2][0x4c]);speeds.append(m.ram[2][0x90]+256*m.ram[2][0x94])
        rows[name]=dict(updates=frame,start_x=xs[0],end_x=xs[-1],minimum_x=min(xs),maximum_x=max(xs),
                        end_y=ys[-1],rise=176-min(ys),crashes=sorted(crashes),recovery_states=sorted(recoveries),
                        final_crash=m.ram[2][0x98],final_recovery=m.ram[2][0x9c],final_facing=m.ram[2][0x804],
                        final_speed=speeds[-1],maximum_speed=max(speeds),phases=sorted(phases))
        if name=='idle':checks['idle_no_acceleration_or_drift']=len(set(xs))==1 and not any(speeds)
        if name=='right':checks['source_throttle_moves_and_caps']=xs[-1]-xs[0]>300 and max(speeds)<=0x320
        if name=='stop':checks['source_coast_stops']=speeds[-1]==0 and len(set(xs[-20:]))==1
        if name=='reverse':checks['coast_then_reverse']=m.ram[2][0x804]==2 and xs[-1]<max(xs)-100
        if name=='jump':checks['source_launch_rise_exact_and_lands']=rows[name]['rise']==expected_rise and ys[-1]==176 and m.ram[2][0xb0]==0
        if name=='lean-jump':checks['original_lean_extends_jump']=rows[name]['rise']>expected_rise and ys[-1]==176 and m.ram[2][0xb0]==0
        if name=='lean-recovery':checks['source_lean_crash_recovers']=bool(crashes-{0})and m.ram[2][0x98]==0 and m.ram[2][0x9c]in[0,5]
        if name=='turbo-heat':checks['source_turbo_heat_recovers']=m.ram[2][0x3e0]==0 and max(speeds)<=0x340
        checks[name+'_on_native_floor']=ys[-1]==176
        checks[name+'_quarter_phases']=phases=={0,1,2,3}
    m=M.fork(seed);tick(m,1,1);before=bytes(m.ram[2]);x=wx(m)
    tick(m,1,1);checks['duplicate_epoch_ignored']=bytes(m.ram[2])==before and wx(m)==x
    M.put(m,GamePauseStatus=1);tick(m,2,1);checks['pause_freezes_private_state']=bytes(m.ram[2])==before
    # Native32px support is imported before draw and source pose publication.
    m=M.fork(seed);m.ram[2][0xb0]=2;m.ram[2][0x37c]=3;M.put(m,Player_State=0)
    M.invoke(m,'ExService1');M.invoke(m,'X5PublishChr')
    checks['body_pages_exact']=m.chr_latches[4:8]==[736,737,738,739]
    M.put(m,CurrentOAMOffset=4,GuestOamRotationActive=0,RgOamRotation=0)
    z=M.invoke(m,'ExService2');checks['native_support_reconciled_before_draw']=m.ram[2][0xb0]==0
    checks['native_draw_emits']=M.get(m,'CurrentOAMOffset')>4 and bool(z['P']&1)
    querycases=0
    for row,target in [(10,'BlockBufferColli_Head'),(14,'BlockBufferColli_Side')]:
      for xpos,ypos,flags in [(80,176,0x30),(255,160,0x31),(0,144,0x70),(128,192,0xf1)]:
        a=M.fork(seed);M.put(a,Player_X_Position=xpos,Player_Y_Position=ypos)
        n=M.fork(a)
        z=M.invoke(a,f'ExService{row}',a=0x55,x=0,y=3,p=flags)
        ref=M.invoke(n,target,a=0x55,x=0,y=3,p=flags)
        assert [z[k]for k in ['A','X','Y','P']]==[ref[k]for k in ['A','X','Y','P']],(row,z,ref)
        assert bytes(a[address(a.bundle,'R0'):address(a.bundle,'R7')+1])==bytes(n[address(n.bundle,'R0'):address(n.bundle,'R7')+1])
        querycases+=1
    checks['head_side_queries_exact_native_ABI']=querycases==8
    m=M.fork(seed);z=M.invoke(m,'ExService12',x=7,y=91)
    checks['native_32px_probe_group']=z['Y']==3 and z['X']==7 and bool(z['P']&1)
    m=M.fork(seed);z=M.invoke(m,'ExService6')
    checks['source_crash_injury_policy']=z['A']==1 and bool(z['P']&1)
    M.invoke(m,'ExService5');assert m.ram[2][0x98]==255
    for frame in range(240):tick(m,frame,1)
    checks['enemy_crash_recovers']=m.ram[2][0x98]==0 and m.ram[2][0x9c]in[0,5]
    m=M.fork(seed);m.ram[2][0x90]=0x20;m.ram[2][0x94]=3
    z=M.invoke(m,'ExService31');tick(m,1,1)
    checks['stomp_uses_source_launch']=bool(z['P']&1) and M.get(m,'Player_Y_Position')<176 and m.ram[2][0xb0]==2
    q=dict(passed=all(checks.values()),component_only=True,source_recovery_CPU_cases=source,checks=checks,rows=rows,
           maximum_movement_CPU=maximum,source_original_plain_jump_rise=expected_rise,memory_cartridge_SHA256=digest,base_ROM_SHA256=PIN,
           actual_cartridge_file_written=False,native_emulator=False,installed=False,
           scope='Original crash/recovery RAM+CPU differentials and actual in-memory current cartridge ExLoad/dispatch/private host/renderer instructions. Flat block buffers; no Main/scene/menu/native replay or full1-1 claim.',
           bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),O/'host-assembly.json',O/'dispatch-assembly.json',O/'host-kernel.bin',O/'host-metadata.bin']})
    cold,scenehash=fixture(scene=True)
    checks['cold_scene_constructs_and_loads_exactly_once']=cold.ppu_reads==16400 and cold.ram[2][0x800]==167
    warm=0
    M.put(cold,DisableScreenFlag=1,Mirror_PPUMASK=0)
    for flags in [0x30,0x31,0x70,0xf1]:
        n=M.fork(cold);before=[bytes(z)for z in n.ram];reads=n.ppu_reads
        z=M.invoke(n,'ExScene',a=0x55,x=7,y=91,p=flags)
        assert [z[a]for a in ['A','X','Y']]==[0x55,7,91]and z['P']&0x4d==flags&0x4d
        assert before==[bytes(z)for z in n.ram] and n.ppu_reads==reads
        warm+=1
    checks['warm_scene_preserves_private_state']=warm==4
    q['passed']=all(checks.values());q['scene_ABI_cases']=warm;q['memory_scene_cartridge_SHA256']=scenehash
    q['bindings']['build/excitebike-pose-1101-v3/scene-assembly.json']=sha(O/'scene-assembly.json')
    save('host-CPU.json',q);print(json.dumps(q));assert q['passed'],checks

if __name__=='__main__':main()

