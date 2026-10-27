"""Small full-caller/foreign addendum, never an emulator or deadline proof."""
from pathlib import Path
import json
from current_mega_arsenal_prepare_v1 import scene,sha
from current_roster_compact_11_v1 import BASE
from proto_normal_palette_ack_9ea_cpu_v1 import P,N,NEW,EXPECTED,scoped_load,Arena,run,ppu,address,location

R=Path(__file__).resolve().parents[2];B=R/'build'
regs=lambda c:(c.a,c.x,c.y,c.p&207,c.sp)
queue=lambda q:bytes(q.get('VRAM_Buffer1',i)for i in range(q.get('VRAM_Buffer1_Offset')+1))

def main():
    assert sha(P)==EXPECTED and sha(N)==NEW;old,new=scoped_load(P),scoped_load(N)
    foreign=[]
    for identity,(_,character,variant,value)in BASE.items():
        for mode in [0,1]:
            pair=[];cpus=[]
            for b in [old,new]:
                q=Arena(b,character);q.put(CrossoverBehaviorVersion=mode,PlayerStatus=1,AreaType=1,MmLastPalette=0)
                if variant:q.set(variant,value)
                c,_=run(q,'X5GetPlayerColors');pair.append(q);cpus.append(c)
            assert regs(cpus[0])==regs(cpus[1])and pair[0].m.banks==pair[1].m.banks
            allowed={address(old,'MmLastPalette')}if identity=='proto'else set()
            assert all(pair[0].m[i]==pair[1].m[i]for i in range(0x8000)if i not in allowed),identity
            assert queue(pair[0])==queue(pair[1]),identity
            assert cpus[1].processorCycles-cpus[0].processorCycles==(4 if identity=='proto'else 0)
            foreign.append(dict(identity=identity,mode=mode,delta=cpus[1].processorCycles-cpus[0].processorCycles))
    states=[('normal',{}),('cold',{'PlayerStatus':0}),('tier2',{'PlayerStatus':2}),
            ('timer',{'TimerControl':12}),('paused',{'GamePauseStatus':1}),
            ('star',{'StarInvincibleTimer':12}),('charge',{'MmChargeFrames':48}),
            ('freeze',{'GuestPowerupActive':1,'GuestPowerupAge':20,'GuestPowerupOld':0,'GuestPowerupTarget':1,'GuestPowerupDisplay':0,'GameEngineSubroutine':9,'TimerControl':255}),
            ('freeze-finish',{'GuestPowerupActive':1,'GuestPowerupAge':59,'GuestPowerupOld':0,'GuestPowerupTarget':1,'GuestPowerupDisplay':1,'GameEngineSubroutine':9,'TimerControl':255})]
    callers=[]
    for name,state in states:
        pair=[];cpus=[];consumers=[]
        for b in [old,new]:
            q=Arena(b,1,proto=1);q.put(ProtoVariant=1,OperMode_Task=3,AreaType=1)
            q.invoke('InventoryInit');scene(q);q.put(**dict(dict(PlayerStatus=1,SsLastPalette=0,MmLastPalette=0),**state))
            run(q,'X5GetPlayerColors');c,_=run(q,'GameLoop');pair.append(q);cpus.append(c)
        assert regs(cpus[0])==regs(cpus[1])and pair[0].m.banks==pair[1].m.banks,(name,'caller live registers')
        # GetColors followed by the complete GameLoop kills the Graphics-only
        # X/Y/parser-index differences. Only queue bytes/extent may differ;
        # every application byte, all lower live stack and five SMC stay exact.
        at=address(old,'VRAM_Buffer1');allowed={address(old,'VRAM_Buffer1_Offset'),address(old,'MmLastPalette')}|set(range(at,at+84))
        diff=[(i,pair[0].m[i],pair[1].m[i])for i in range(0x8000)if i not in allowed and pair[0].m[i]!=pair[1].m[i]]
        assert not diff,(name,diff[:12])
        packets=[queue(q).hex()for q in pair]
        for q in pair:
            b=q.b;ptr=address(b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8)
            q.m.page(2,(location(b,'FastNmiVramCopy')-16)//8192)
            c,_=run(q,'UpdateScreen');consumers.append((c.processorCycles,ppu(q.m.writes)))
        assert consumers[0][1][0]==consumers[1][1][0],(name,'final PPU values')
        callers.append(dict(name=name,state=state,full_GameLoop_AXYP_SP_banks_application_RAM_lower_stack_SMC_exact_except_declared_queue_cache=True,
                            cache_after=[q.get('MmLastPalette')for q in pair],
                            queue_hex=packets,GameLoop_cycles=[c.processorCycles for c in cpus],
                            UpdateScreen_cycles=[x[0]for x in consumers],final_PPU_values_exact=True))
    result=dict(passed=True,source_only=True,native_run=False,parent_sha256=EXPECTED,candidate_sha256=NEW,
                complete_GetColors_current37_mode_cases=foreign,complete_GetColors_to_GameLoop_to_UpdateScreen=callers,
                intentional='Normal Proto may omit three redundant palette writes and six queue bytes. No whole ordered IO equality is claimed when that omission occurs. Complete final PPU values and complete GameLoop return state are exact.',
                limits='CPU source controls only; no new native, DMC, render deadline or general frame-rate certification.',
                bindings={str(p):sha(p)for p in [Path(__file__),P,P.with_suffix('.dbg'),N,N.with_suffix('.dbg'),R/'tools/audit/current_roster_compact_11_v1.py',R/'tools/audit/current_mega_arsenal_prepare_v1.py',R/'tools/audit/proto_normal_palette_ack_9ea_cpu_v1.py',B/'proto_normal_palette_ack_9ea_cpu.json']})
    out=B/'proto_normal_palette_ack_9ea_caller.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=True,cases=[len(foreign),len(callers)],path=str(out),sha256=sha(out))))

if __name__=='__main__':main()
