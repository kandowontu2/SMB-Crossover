"""Actual menu admission, parser and Main on the private current composition."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from prepare_excitebike_host_1101_v1 import BASE,PIN
from prepare_excitebike_dispatch_1101_v1 import O,save,sha
from check_excitebike_cold_1101_v1 import bundle


def menus(b):
    b['segs']['excitebike_menu_policy']={'start':str(0xa000),'ooffs':str(16+76*8192)}
    b['syms']['FmPlayable']={'val':str(0xbff3),'seg':'excitebike_menu_policy'}
    counts=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2]
    seed=M.fresh(b);rows=[];source_pending=set();starts=0
    for slot,count in enumerate(counts):
        m=M.fork(seed);M.put(m,CrossoverMenuIndex=slot)
        M.invoke(m,'MenuResolveCharacter');M.invoke(m,'QueueSelection')
        for v in range(count):
            if v:
                M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
                M.invoke(m,'CrossoverMenuInput')
            pending=M.invoke(m,'FmPending');playable=M.invoke(m,'FmPlayable')
            if pending['P']&1:source_pending.add(pending['A'])
            row=dict(slot=slot,variant=v,raw=M.get(m,'SelectedCharacter'),
                     source_pending=pending['A']if pending['P']&1 else None,
                     locked=bool(playable['P']&1))
            for key in [16,128]:
              for flags in [0x30,0x31,0x71,0xf1]:
                n=M.fork(m);M.put(n,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
                M.invoke(n,'CrossoverMenuInput',p=flags)
                assert (M.get(n,'CrossoverMenuState')==0)!=row['locked'],('menu admission',row,key,flags)
                starts+=1
            rows.append(row)
    assert len(rows)==90
    return rows,sorted(source_pending),starts


def main():
    report=dict(passed=False,base_ROM_SHA256=PIN,native=False,installed=False)
    try:
        b=bundle();old=scoped_load(BASE);before,pending,_=menus(old);after,newpending,starts=menus(b)
        assert pending==newpending==[3,4,24,25],(pending,newpending)
        for a,z in zip(before,after):
            if (a['slot'],a['variant'])==(29,0):
                assert a['raw']==0 and a['locked']and z['raw']==37 and not z['locked']
            else:assert a==z,('foreign menu',a,z)
        assert any(r['slot']==29 and r['variant']==1 and r['locked']for r in after)
        report['menu']=dict(profiles=90,Start_A_flag_cases=starts,source_pending_domain=pending,
                            foreign_profiles_exact=89,only_admission='Excitebike slot29 alternate0 raw37',Prince_locked=True)
        m=M.fresh(b);M.put(m,CrossoverMenuIndex=29)
        for name in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:M.invoke(m,name)
        assert M.get(m,'SelectedCharacter')==37
        M.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
        start=M.invoke(m,'CrossoverMenuInput')
        M.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
        M.invoke(m,'PauseRoutine',a=0)
        for setup in range(600):
            if M.get(m,'OperMode_Task')==3 and M.get(m,'GameEngineSubroutine')==8:break
            M.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
            M.invoke(m,'GameLoop');M.consume(m)
        else:raise AssertionError('Actual parser/entrance bound')
        assert m.ram[2][0x800]==167 and m.ppu_reads==16400
        assert bytes(m.ram[3][:6144])==(O/'host-kernel.bin').read_bytes()
        report['parser']=dict(Main_updates=setup,PPU_reads=m.ppu_reads,constructor_ready=True)
        rows=[];lives=M.get(m,'NumberofLives');minimum=255;initialx=None
        for age in range(270):
            # Natural stage starts at48; limit forward movement here before
            # the first opponent. These phases cover idle, throttle, coast,
            # reverse and a source launch through the actual native Main.
            pad=0 if age<90 else 1 if age<120 else 0 if age<165 else 2 if age<210 else 0
            if age==220:pad=128
            M.put(m,SavedJoypadBits=pad,SavedJoypad1Bits=pad,SavedJoypad2Bits=0,
                  A_B_Buttons=pad&192,Left_Right_Buttons=pad&3,Up_Down_Buttons=pad&12,NmiDisable=255)
            z=M.invoke(m,'GameLoop')
            x=M.get(m,'Player_X_Position')+256*M.get(m,'Player_PageLoc');y=M.get(m,'Player_Y_Position')
            if initialx is None:initialx=x
            if age<90:assert x==initialx,('Actual Main idle drift',age,x,initialx)
            minimum=min(minimum,y)
            assert M.get(m,'SelectedCharacter')==37 and M.get(m,'NumberofLives')==lives,('Actual Main lost owner/life',age)
            assert M.get(m,'GameEngineSubroutine')!=11,('Unexpected native injury',age)
            if age%10==0:rows.append(dict(age=age,pad=pad,x=x,y=y,engine=M.get(m,'GameEngineSubroutine'),state=M.get(m,'Player_State'),source_speed=m.ram[2][0x90]+256*m.ram[2][0x94],CPU=z['CPU']))
            M.consume(m)
        assert max(r['x']for r in rows)>initialx+5 and minimum<176
        report['Main']=dict(updates=270,normal_NMI=270,initial_lives=lives,final_lives=M.get(m,'NumberofLives'),
                            idle_no_drift=True,minimum_y=minimum,rows=rows)
        report['memory_candidate_SHA256']=hashlib.sha256(b['raw']).hexdigest();report['passed']=True
    except Exception as e:
        report.update(error=repr(e),traceback=traceback.format_exc());raise
    finally:
        report['bindings']={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),BASE,O/'host-assembly.json',O/'router-assembly.json',O/'scene-assembly.json']}
        save('current-CPU.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['bindings','Main','traceback']}))

if __name__=='__main__':main()
