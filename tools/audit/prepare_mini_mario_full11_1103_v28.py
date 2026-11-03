"""Controller-only Mini1-1 route, original run/jump plus authorized wall cling."""
from pathlib import Path
import argparse,json,re,sys
import prepare_mini_mario_native_smoke_1103_v25 as S
import prepare_mini_mario_native_smoke_1103_v31 as S31
from prepare_selected_native_packet_v1 import R,prepare,sha
from observe_chip_committed_write import lua

O=R/'build/mini-mario-full11-packet-1103-v28'
ROUTE=Path(__file__).with_suffix('.lua')

def source_gap_cases():
    """Only isolated compiled-source/controller feasibility, no GameCore claim."""
    import prepare_mini_mario_host_1103_v22 as H
    import check_mini_mario_step_1103_v18 as T
    data=(H.O/'mini-host-v22.bin').read_bytes();K=S.labels(H.O/'mini-host-v22.lbl');L=H.symbols();cases=[]
    for width in [32,48]:
        m=T.memory(data,K,0)
        for addr,path in [(0xd300,R/'build/mini-mario-native-tile-1103-v13/native-attributes.bin'),(0xd000,R/'build/mini-mario-art-1103-v12/engine-animation-index.bin'),(0xd160,R/'build/mini-mario-art-1103-v12/engine-animation-frames.bin')]:
            v=path.read_bytes();m.memory[addr:addr+len(v)]=v
        for bx in range(6,6+width//16):
            for row in [176,192]:m.memory[0x300+row+bx]=0
        for n,v in dict(GameEngineSubroutine=8,Player_X_Position=40,Player_Y_Position=176,Player_Y_HighPos=1,PlayerStatus=0,AreaType=1).items():m.memory[L[n]]=v
        T.call(m,K['MiniHostFresh']);requests=[];miny=9999
        def w(a):return m.memory[a]|m.memory[a+1]<<8
        def solid(x,y):
            if y<32 or y>=240:return False
            tile=m.memory[0x300+((x//256)&1)*0xd0+(y&240)-32+((x&255)//16)]
            return m.memory[0xd300+tile]&3==1
        held=0;trace=[]
        for step in range(220):
            m.memory[L['FrameCounter']]=step&255;m.memory[L['SavedJoypadBits']]=held;T.call(m,K['MiniHostMain'])
            x,y=w(0xc250)/16,w(0xc252)/16;miny=min(miny,y)
            if len(trace)<100:trace.append([step,w(0xc250),w(0xc252),w(0xc200),w(0xc220),m.memory[0xc240],m.memory[0xc228],m.memory[0xc246],m.memory[0xc24c],held])
            if y>=240:
                fail=dict(CPU_only=True,passed=False,gap_width=width,requests=requests,trace=trace)
                (O/'gap-policy-negative.json').write_text(json.dumps(fail,indent=2)+'\n')
                raise AssertionError((width,step,x,y,requests))
            if x>=96+width+8 and m.memory[0xc24c]&1:
                cases.append(dict(gap_left=96,gap_right=96+width,updates=step+1,x16=w(0xc250),y16=w(0xc252),jump_requests=requests,min_sourceY=miny));break
            if step<1:held=0;continue
            floor=m.memory[0xc24c]&1 and m.memory[0xc246]==2
            gap=not solid(int(x+22),int(y+8))
            held=0x41
            if m.memory[0xc228]==12:held|=128
            elif floor:
                if gap and not m.memory[0xc248]&128:held|=128;requests.append(dict(step=step,x16=w(0xc250),y16=w(0xc252)))
            else:held|=128
        else:raise AssertionError(('Source-only adaptive gap failed',width,x,y))
    return dict(passed=True,isolated_CPU_only=True,host_SHA256=sha(H.O/'mini-host-v22.bin'),
        ordinary_run_and_original_jump=True,no_wall_restarts_or_helpers=True,cases=cases,
        scope='In-memory native-buffer gaps and compiled source host; no generic nativeBGCollision, enemies, realparser/camera or Mesen acceptance.')

def controller(rom,expected,kernel,kernel_labels,refs):
    text,deps=S31.build(rom,expected,kernel,kernel_labels,refs)
    L=S.labels(S.GLOBALS);L.update(S.labels(Path(rom).with_suffix('.lbl')))
    names=['WorldNumber','LevelNumber','Enemy_Flag','Enemy_ID','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_State']
    prefix='for k,v in pairs('+lua({n:L[n]for n in names})+')do L[k]=v end\nC.max_frames=22000\n'
    anchor='-- Controller inputs only.';assert text.count(anchor)==1
    text=text.replace(anchor,prefix+anchor)
    text=text.replace("local done,lastEpoch,pending,last=nil,nil,nil,nil", "local done,lastEpoch,pending,last=nil,nil,nil,nil\nlocal route_complete=false\nlocal route_pad={}\nlocal route_steps=0")
    text=text.replace('full_stage=false,helpers_added=false','full_stage=route_complete,helpers_added=false')
    anchor='local function sample()';assert text.count(anchor)==1
    text=text.replace(anchor,ROUTE.read_text()+'\n'+anchor)
    anchor=" if lastEpoch then check(((s.epoch-lastEpoch)&255)==1,"
    assert text.count(anchor)==1
    text=text.replace(anchor," if lastEpoch and r('WorldNumber')==0 and r('LevelNumber')==1 then lastEpoch=nil end\n"+anchor)
    anchor=' local n=updates-startUpdates';assert text.count(anchor)==1
    text=text.replace(anchor,anchor+"\n if phase=='fullstage'then route_tick(s);return end")
    text=text.replace("if phase=='game'then startLives=s.lives;transition('settle')", "if phase=='game'then startLives=s.lives;transition('fullstage')")
    anchor=" elseif phase=='right'then keys.right=true";assert text.count(anchor)==1
    text=text.replace(anchor," elseif phase=='fullstage'then for k,v in pairs(route_pad)do keys[k]=v end"+anchor)
    anchor=" elseif phase=='finish'then";assert text.count(anchor)==1
    text=text.replace(anchor," elseif phase=='fullstage'then route_endframe()"+anchor)
    text=text.replace("shot('mini-native');result(true)","shot('mini-active-1-2');result(true)")
    text=text.replace("print('PASS Mini source-epoch smoke')","print('PASS Mini actual nonshortcut1-1')")
    # Full route deliberately checks the original small profile; a naturally
    # earned power transition requires its separate capability qualification.
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    return text,[*deps,Path(__file__),ROUTE]

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path);p.add_argument('--sha');p.add_argument('--kernel',type=Path);p.add_argument('--labels',type=Path)
    p.add_argument('--ref',type=Path,action='append',default=[]);p.add_argument('--source-only',action='store_true');a=p.parse_args();O.mkdir(exist_ok=True)
    if a.source_only:
        sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
        from lupa.lua54 import LuaRuntime
        LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(ROUTE.read_text())
        q=dict(source_only=True,native=False,ROM_written=False,source_SHA256=sha(ROUTE),producer_SHA256=sha(__file__),
            pending='Repaired native collision successor and root grant; failed39bb smoke25 remains immutable.',
            policy='Genuine Right+B run; original held-Ajump on actual terrain/gap/enemy approach. At real falling wallcling, release heldA for one source epoch then freshA queues originalJUMP_INIT. No physics/helper/state writes.',
            authored_obstacles=[['pipe',448,480,176],['pipe',608,640,160],['pipe',736,768,144],['pipe',912,944,144],['pit',1104,1136],['pit',1376,1424],['pit',2448,2480]],
            max_PNGs=2,source_update_bound=10000,physical_frame_bound=22000,source_gap_policy=source_gap_cases())
        (O/'template.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q));return
    assert a.rom and a.sha and a.kernel and a.labels
    text,refs=controller(a.rom,a.sha,a.kernel,a.labels,a.ref)
    prepare(O/'full11',a.rom,text,refs,expected=a.sha,timeout=240,allow_interactive=True,
        scope='Controller-only Mini actual nonshortcut1-1; all four pipes/three authored pits and active1-2/no-life-loss. Original run/jump with explicit userauthorizedwallcling/freshA adaptation. Read-only source/native terrain/enemy choice, originalJumpInit records, physical bbox/CHR/sourcepixels/normalDMA guards, twoPNG. No helper/RAM writes/ability seeds.')

if __name__=='__main__':main()
