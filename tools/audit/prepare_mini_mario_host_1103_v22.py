"""Link Mini private native host against frozen source slice; no cartridge."""
from pathlib import Path
from zipfile import ZipFile
import json,re,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_world_1103_v11 as W
R=W.R;O=R/'build/mini-mario-host-1103-v22';INC=R/'tools/reference/mini_mario_native_host_1103_v22.inc'
BASELABELS=R/'build/roster-combined-1101-v3/candidate.lbl'

def symbols():return {n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',BASELABELS.read_text(),re.M)}

def source():
    world=(W.O/'motion-proposed-v11.s').read_text()+'\n'+(R/'tools/reference/mini_mario_world_1103_v16.inc').read_text()
    tile=(R/'build/mini-mario-native-tile-1103-v13/native-tile.s').read_text().replace('.segment "MINI_NATIVE"','.segment "CODE"').replace('MiniTileAttributes=$d000','MiniTileAttributes=$d300')
    for n in ['Done','Classify','Store','Buffer2','Solid','Vine']:tile=re.sub(r'\b'+n+r'\b','Tile_'+n,tile)
    render=(R/'build/mini-mario-native-render-1103-v15/native-render.s').read_text().replace('.segment "MINI_RENDER"','.segment "CODE"');render=re.sub(r'\bDone\b','Render_Done',render)
    animate=(R/'build/mini-mario-animation-1103-v20/animate.s').read_text()
    S=symbols();names=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_X_Speed','Player_Y_Speed','Player_State','Player_X_Scroll','TimerControl','GamePauseStatus','FrameCounter','GameEngineSubroutine','AreaType','BackgroundColorCtrl','PlayerStatus','ObjectOffset','VRAM_Buffer1_Offset','VRAM_Buffer1','Player_Rel_XPos','Player_Rel_YPos','SavedJoypadBits','CurrentCHRBank','X5WideChrActive','ReloadCHRBank','SsChrActive','GuestBodyNoStomp','BoundingBox_UL_Corner','OperMode','ScreenLeft_X_Pos','ScreenLeft_PageLoc','BlockBufferColli_Head','BlockBufferColli_Side','PlayerFacingDir']+['R'+str(i)for i in range(8)]
    const='\n'.join(f'{n}=${S[n]:04x}'for n in names)+'\nX5ChrMode=$73e0\n'
    # Vector must start atA000; all source and host calls relink symbolically.
    host=INC.read_text();at=host.index('MiniHostNo:');prefix=host[:at];body=host[at:]
    s='.setcpu "6502"\n.macpack longbranch\n.segment "CODE"\n'+const+prefix+'\n'+world+'\n'+tile+'\n'+render+'\n'+animate+'\n'+body
    # Shared private equates are identical; retain exactly one definition.
    seen={};lines=[]
    for l in s.splitlines():
        m=re.match(r'^(\w+)\s*=\s*\$([0-9a-fA-F]+)',l)
        if m:
            n,v=m[1],int(m[2],16)
            if n in seen:assert seen[n]==v,(n,v,seen[n]);continue
            seen[n]=v
        lines.append(l)
    return lines

def build():
    O.mkdir(exist_ok=True);p=O/'mini-host-v22';lines=source();long=set();cc=R/'tools/Windows/cc65/bin'
    p.with_suffix('.cfg').write_text('MEMORY{P:start=$a000,size=$2000,file=%O;}SEGMENTS{CODE:load=P,type=ro;}')
    for attempt in range(20):
        out=[]
        for i,l in enumerate(lines):
            if i in long:l=re.sub(r'^(\s*)b(cc|cs|eq|ne|mi|pl|vc|vs)\b',r'\1j\2',l,flags=re.I)
            out.append(l)
        p.with_suffix('.s').write_text('\n'.join(out)+'\n')
        c=subprocess.run([str(cc/'ca65.exe'),str(p.with_suffix('.s')),'-o',str(p.with_suffix('.o'))],capture_output=True,text=True)
        if c.returncode==0:break
        bad=[int(x)-1 for x in re.findall(r':(\d+): Error: Range error',c.stderr)]
        assert bad,c.stderr
        before=len(long);long.update(bad);assert len(long)>before,c.stderr
    else:raise AssertionError('Branch relaxation did not converge')
    c=subprocess.run([str(cc/'ld65.exe'),'-C',str(p.with_suffix('.cfg')),str(p.with_suffix('.o')),'-o',str(p.with_suffix('.bin')),'-Ln',str(p.with_suffix('.lbl'))],capture_output=True,text=True);assert c.returncode==0,c.stderr
    data=p.with_suffix('.bin').read_bytes();L={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',p.with_suffix('.lbl').read_text(),re.M)}
    return data,L,dict(lines=len(lines),long_conditionals=len(long),relax_iterations=attempt+1)

def main():
    data,L,relax=build();assert L['MiniVectors']==0xa000
    vectors=[int.from_bytes(data[i*3+1:i*3+3],'little')for i in range(38)];assert all(data[i*3]==76 for i in range(38))
    out=dict(passed=True,compiled_only=True,CPU_qualified=False,ROM_written=False,native_admitted=False,bytes=len(data),code_end=0xa000+len(data),five_1KB_pages_fit=len(data)<=5120,SHA256=W.sha(data),labels=L,vectors=vectors,branch_relaxation=relax,source_step_immutable=True,host_adaptation='Userauthorizedwallcling/freshAqueues originalJUMP_INIT. Native16px terrain/firstEntranceY+24 and normalcanvasY+8. Host imports preserve fractions; sourcephysics constants unchanged.',unimplemented_reject_rows=[4,5,7,8,19,20,21,22,24,25,27,28,29,33,35,37],bindings={p.relative_to(R).as_posix():W.sha(p.read_bytes())for p in [Path(__file__),INC,R/'tools/reference/mini_mario_world_1103_v16.inc',W.O/'world-source-v21.json',R/'build/mini-mario-native-render-1103-v15/native-render.s',R/'build/mini-mario-animation-1103-v20/animate.s',R/'build/mini-mario-native-tile-1103-v13/native-tile.s',BASELABELS]})
    (O/'mini-host-v22.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','bytes','code_end','five_1KB_pages_fit','SHA256','labels','branch_relaxation']}))
if __name__=='__main__':main()
