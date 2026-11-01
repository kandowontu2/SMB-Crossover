"""Run the real menu, parser, fatal injury, life loss and next-life control."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as C
import ff_wram_host_controls_v7 as H
import ff_host_pickups_vectors_v2 as V
from check_tmnt_render_oa import address
O=R/'build/karnov-host-resource-base-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    q=dict(passed=False,source_CPU=True,native_emulator=False,installed=False)
    refs=[Path(__file__),O/'terrain-assembly.json',O/'candidate.nes',O/'candidate.dbg']
    try:
        stage=json.loads((O/'terrain-assembly.json').read_text());assert stage['passed']and stage['health']
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        b=H.C.qualified(O/'candidate.nes');m=C.fresh(b)
        H.put(m,CrossoverMenuIndex=7)
        C.invoke(m,'MenuResolveCharacter');C.invoke(m,'QueueSelection')
        H.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
        C.invoke(m,'CrossoverMenuInput');C.invoke(m,'DrawSelectionPreview')
        assert H.get(m,'SelectedCharacter')==34
        H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0)
        C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',a=0)
        def step(keys=0):
            H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
            c=H.start(m,'GameLoop');c,low=H.finish(m,c)
            C.consume(m)
            return low
        setup=0
        while not(H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8):
            assert setup<600;step();setup+=1
        for _ in range(10):step()
        lives=H.get(m,'NumberofLives');x=H.get(m,'Player_X_Position')
        # Deliberate native injury fixture: the first hit was spent and its
        # source invulnerability expired. No code/vector/state overlay occurs.
        m.ram[2][0x68]=128;m.ram[2][0x69]=1;m.ram[2][0x65]=2
        H.put(m,InjuryTimer=0,CheatInvincible=0,GuestHurtTicks=0,MmDeathFlag=0,PlayerStatus=2)
        c=H.start(m,'InjurePlayer');c,low=H.finish(m,c)
        assert H.get(m,'GameEngineSubroutine')==11 and m.ram[2][0x62]&31==25
        engines=set();minimum=low;lost=False;restarted=False;death_updates=0
        for tick in range(900):
            eng=H.get(m,'GameEngineSubroutine');engines.add(eng)
            if eng==11:death_updates+=1
            minimum=min(minimum,step())
            if H.get(m,'NumberofLives')==lives-1:lost=True
            if lost and H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:
                restarted=True;break
        assert lost and restarted,('Life/parser restart bound',lost,restarted,sorted(engines),H.get(m,'OperMode_Task'),H.get(m,'GameEngineSubroutine'))
        assert H.get(m,'SelectedCharacter')==34 and H.get(m,'MmDeathFlag')==0
        assert m.ram[2][0x68]==m.ram[2][0x65]==0
        assert m.ram[2][address(b,'KrReady')&8191]==167
        before=H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc')
        for _ in range(30):minimum=min(minimum,step(1))
        after=H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc')
        assert after>before+15 and H.get(m,'GameEngineSubroutine')==8
        q.update(passed=True,ROM_sha256=stage['ROM_sha256'],setup_Main=setup,death_Main=death_updates,life_restart_Main=tick+1,normal_NMIs=setup+10+tick+1+30,lives_before=lives,lives_after=H.get(m,'NumberofLives'),engines=sorted(engines),native_death_flag_cleared=True,source_health_gear_reset=True,next_life_control_delta=after-before,minimum_SP=minimum,scope='Real menu Select/Start, native parser/Main and complete normal NMI updates. A declared source-health128 fixture enters actual InjurePlayer; original death reaches life loss and native parser restarts Karnov with fresh health/gear and real rightward control. Not a controller-earned fatal collision, emulator video or full-stage qualification.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in refs}
    (O/'life-restart-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','traceback']}));assert q['passed'],q.get('error')


if __name__=='__main__':main()
