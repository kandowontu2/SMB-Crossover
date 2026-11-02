"""Measure original André attack selection against the observed native geometry."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as M
O=R/'build/bub-menu-candidate-1102-v2'
P=R/'build/wwf-helper-stable-1102-v2/candidate2.nes'
PIN='f5c30ceaa36894f3e814ef277081ecd9cf434a934c0f7b3f514c2291be0e1cfc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert sha(P)==PIN
    b=dict(M.scoped_load(R/'build/wwf-death-1102-v2/candidate.nes'));b['raw']=P.read_bytes();seed=M.fresh(b)
    M.put(seed,SelectedCharacter=29,FmGroups=5,OperMode=1,GameEngineSubroutine=8,
        FamilyMainCommit=1,NmiDisable=255,DisableScreenFlag=1,Mirror_PPUMASK=0)
    M.invoke(seed,'WfLoad');M.invoke(seed,'WfConstructCold')
    assert seed.ram[2][0x2b]==4,'Actual André descriptor identity'
    M.put(seed,GameEngineSubroutine=8,TimerControl=0,GamePauseStatus=0,Player_X_Position=128,Player_PageLoc=0,
        Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,Player_Y_Speed=0,AreaType=1)
    for i in range(6):seed[M.address(b,'Enemy_Flag')+i]=0
    for _ in range(90):
        M.put(seed,SavedJoypadBits=0,A_B_Buttons=0,PreviousA_B_Buttons=0);M.invoke(seed,'WfMovement')
    rows=[]
    for dx in [11,16,24,44]:
        for name,keys in [('B',64),('Down+B',68),('Right+B',65),('Up+B',72)]:
            m=M.fork(seed);M.put(m,Enemy_ID=6,Enemy_Flag=1,Enemy_State=0,Enemy_X_Position=128+dx,Enemy_PageLoc=0,
                Enemy_Y_Position=184,Enemy_Y_HighPos=1,ObjectOffset=0)
            M.invoke(m,'InitGoomba',x=0)
            first=None;actions=set();poses=set();hit_writes=[]
            for epoch in range(90):
                held=keys if epoch%18<3 else 0
                M.put(m,SavedJoypadBits=held,A_B_Buttons=held&192,PreviousA_B_Buttons=0)
                result=M.invoke(m,'WfMovement')
                actions.add(m.ram[2][0x3c]);poses.add(m.ram[2][0x32])
                if M.get(m,'Enemy_State')&32:
                    first=epoch;break
            rows.append(dict(native_enemy_dx=dx,native_enemy_y=184,keys=name,first_native_defeat_update=first,
                actions=sorted(actions),pose_groups=sorted(poses),final_source_damage=m.ram[2][0x89],
                source_proxy_depth_delta=(m.ram[2][0x2f]-m.ram[2][0x2e])&255,
                final_native_x=M.get(m,'Player_X_Position'),final_native_enemy_state=M.get(m,'Enemy_State')))
    q=dict(passed=True,source_CPU_geometry_only=True,native=False,ROM_SHA256=PIN,ROM_changed=False,
        scope='Actual cold/constructor André, 90neutral source steps, actual InitGoomba/native-bound-box ABI; static enemy at observedgroundY184 and declaredDX. Only existing WfMovement/source damage/native defeat runs. No naturalroute or incominginjury proof.',
        rows=rows,bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),P,R/'build/wwf-helper-stable-1102-v2/native-andre-contact/capture/contact.csv']})
    target=O/'andre-attack-geometry-CPU-v1.json';assert not target.exists();target.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(q))

if __name__=='__main__':main()
