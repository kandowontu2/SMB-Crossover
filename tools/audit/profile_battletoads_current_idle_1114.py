"""Genuine f11a Rash idle48/walk32 source CPU profile, no artifacts or FPS claim."""
from collections import Counter
from hashlib import sha256
import argparse,json
from pathlib import Path
from unittest.mock import patch

import compose_battletoads_camera_handoff_1114 as C
import replay_battletoads_camera_full11_1114 as F
import check_battletoads_camera_candidate_1114 as Cold
import check_bub_current_budget_1113 as Frames

W,N=F.W,F.N


def actors(m):
    camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc');rows=[]
    for i in range(6):
        flag=N.get(m,'Enemy_Flag',i)
        if not flag:continue
        x=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i)
        y=N.get(m,'Enemy_Y_Position',i);high=N.get(m,'Enemy_Y_HighPos',i)
        rows.append(dict(slot=i,flag=flag,id=N.get(m,'Enemy_ID',i),state=N.get(m,'Enemy_State',i),
            x=x,y=y,y_high=high,relative_x=x-camera,onscreen=-16<x-camera<256 and high==1 and y<240))
    return rows


def state(m):
    b=m.bundle
    return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
        y=N.get(m,'Player_Y_Position'),camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc'),
        native_state=N.get(m,'Player_State'),engine=N.get(m,'GameEngineSubroutine'),
        HP=m.ram[3][W.address(b,'BtSrc_Objects_Life')&8191],variant=m.ram[3][W.address(b,'BtVariant')&8191],
        lives=N.get(m,'NumberofLives'),power=N.get(m,'PlayerStatus'),star=N.get(m,'StarInvincibleTimer'),actors=actors(m))


def points(raw,b):
    out={}
    for name in('GameLoop','CfOrBtCheck','CfLoaderProposal','CfLoaderCoreProposal','BtCheck','BtLoad','BtRetire',
            'BtServiceVeneers','BtConstruct','BtActive','BtMovement','BtImportNative','BtExportNative',
            'BtCoreStep','BtGraphics','BtDraw','BtWeapons','BtFullBox','BtColors','BtLivesColors',
            'BtStatusName','BtPickup','BtHostTerrain','BtHostCamera','MetaspriteRenderLoop',
            'CrossoverVanillaMovement','ScrollHandler'):
        if name not in b['syms']:continue
        sym=b['syms'][name];segment=b['segs'].get(sym.get('seg'),{})
        if segment.get('name','').startswith('"BT_CACHE'):tag=3
        else:
            try:tag=((W.location(b,name)-16)//8192)|128
            except(KeyError,AssertionError):continue
        out.setdefault((tag,W.address(b,name)),[]).append(name)
    # The original core's synthetic linker segment does not identify its live
    # copied map. Bind the actual current RAM3 tail-JMP operand instead.
    at=W.address(b,'BtCoreStep')&8191;core=raw[C.BASE+at:C.BASE+at+6]
    assert core[0]==0x8e and core[3]==0x4c
    target=int.from_bytes(core[4:6],'little');assert target==W.address(b,'BtPhysicsStep')
    out.setdefault((3,target),[]).append('BtPhysicsStep_actual')
    bank=raw[16+65*8192:16+66*8192]
    auth=[0xa000+i for i in range(0xe00,0xf27)if bank[i:i+8]==bytes.fromhex('ad026038e925c907')]
    assert len(auth)==1
    out.setdefault((193,auth[0]),[]).append('CoCheckCode_actual')
    return out


def save_blocks(raw,b):
    cache=raw[C.BASE:C.BASE+8192]
    save=bytes.fromhex('08488a489848')+b''.join(bytes((0xa5,W.address(b,'R'+str(i)),0x48))for i in range(8))
    restore=b''.join(bytes((0x68,0x85,W.address(b,'R'+str(i))))for i in range(7,-1,-1))+bytes.fromhex('68a868aa6828')
    result={}
    for name,pattern in(('BtSave',save),('BtRestore',restore)):
        sites=[0xa000+i for i in range(0xd9c,0x15e6-len(pattern)+1)if cache[i:i+len(pattern)]==pattern]
        assert sites,(name,pattern.hex())
        result[name]=[(pc,pc+len(pattern))for pc in sites]
    return result


def profile(raw):
    assert sha256(raw).hexdigest()==C.CANDIDATE
    m=Cold.cold(raw,'rash');b=m.bundle;entries=points(raw,b);macros=save_blocks(raw,b);base=N.NesMPU
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    rows=[];idle=W.address(b,'IdleLoop')
    for phase,pad,count in(('idle',0,48),('walk_right',1,32)):
        calls=Counter();returned=Counter();inclusive=Counter();innermost=Counter();bank_cost=Counter();pc_cost=Counter()
        macro_cost=Counter();macro_calls=Counter();all_cpus=[];perMain=[];actor_seen={};minimum=255
        initial=state(m)
        class Probe(base):
            def __init__(self,*args,**kwargs):
                super().__init__(*args,**kwargs);self.pending=[]
                self.kind='Main_scheduler'if self.pc==idle else'normal_NMI'
                all_cpus.append(self)
            def step(self):
                nonlocal minimum
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                while self.pending and(self.pc,self.sp)==self.pending[-1]['return']:
                    done=self.pending.pop();inclusive[done['name']]+=self.processorCycles-done['cycles'];returned[done['name']]+=1
                for name in entries.get((tag,self.pc),()):
                    ret=(m[256+((self.sp+1)&255)]+256*m[256+((self.sp+2)&255)]+1)&65535
                    self.pending.append(dict(name=name,**{'return':(ret,(self.sp+2)&255)},cycles=self.processorCycles))
                    calls[name]+=1
                pc=self.pc;before=self.processorCycles;minimum=min(minimum,self.sp)
                result=super().step();cost=self.processorCycles-before
                bank_cost[self.kind,tag]+=cost;pc_cost[self.kind,tag,pc]+=cost
                if self.pending:innermost[self.pending[-1]['name']]+=cost
                if tag==3:
                    for name,spans in macros.items():
                        for start,end in spans:
                            if start<=pc<end:
                                macro_cost[name]+=cost
                                if pc==start:macro_calls[name]+=1
                return result
        with patch.object(N,'NesMPU',Probe):
            for main in range(count):
                entered,completed=calls['GameLoop'],returned['GameLoop']
                m.controller_pad=pad;cycles=Frames.frame(m,whole_pass=True)
                entries_delta,returns_delta=calls['GameLoop']-entered,returned['GameLoop']-completed
                assert(entries_delta,returns_delta)==(1,1),'One actual GameLoop per scheduler iteration'
                s=state(m);assert(s['HP'],s['lives'],s['power'],s['star'],s['variant'])==(47,2,0,0,0)
                assert s['engine']==8 and s['native_state']==0
                for a in s['actors']:actor_seen[(a['slot'],a['id'],a['x'],a['y'],a['onscreen'])]=a
                perMain.append(dict(Main=main+1,GameLoop_entries=entries_delta,GameLoop_returns=returns_delta,
                    cycles=cycles,x=s['x'],camera=s['camera'],active_actors=len(s['actors']),onscreen_actors=sum(a['onscreen']for a in s['actors'])))
        unclosed=[dict(name=q['name'],kind=cpu.kind,PC=cpu.pc,SP=cpu.sp,target=q['return'])for cpu in all_cpus for q in cpu.pending]
        assert not unclosed and calls['GameLoop']==returned['GameLoop']==count
        assert calls['BtPhysicsStep_actual']==returned['BtPhysicsStep_actual']==count
        assert macro_cost['BtSave']==64*macro_calls['BtSave']and macro_cost['BtRestore']==76*macro_calls['BtRestore']
        rows.append(dict(phase=phase,pad=pad,Main_returns=count,initial=initial,final=state(m),per_Main=perMain,
            mean_Main_scheduler_cycles=sum(q['cycles']for q in perMain)/count,
            inclusive_function_cycles_per_Main={k:v/count for k,v in sorted(inclusive.items())},
            innermost_tracked_function_cycles_per_Main={k:v/count for k,v in sorted(innermost.items())},
            calls=dict(sorted(calls.items())),returns=dict(sorted(returned.items())),unclosed_scopes=unclosed,
            cycle_maps=[dict(kind=kind,raw_tag=tag,cycles_per_Main=value/count)for(kind,tag),value in sorted(bank_cost.items())],
            top_instructions=[dict(kind=kind,raw_tag=tag,PC=pc,cycles_per_Main=value/count)for(kind,tag,pc),value in pc_cost.most_common(24)],
            BtSave_Restore_calls=dict(macro_calls),BtSave_Restore_cycles_per_Main={k:v/count for k,v in sorted(macro_cost.items())},
            active_actor_positions=list(actor_seen.values()),minimum_SP=minimum))
        print('PROGRESS '+json.dumps(dict(phase=phase,Main=count,mean_cycles=rows[-1]['mean_Main_scheduler_cycles'])),flush=True)
    return dict(ROM_SHA256=C.CANDIDATE,identity='rash',genuine_cold_Start=True,warmup_idle_Main=4,
        main_vs_NMI_separately_attributed=True,tracked_functions=[dict(raw_tag=tag,PC=pc,names=names)for(tag,pc),names in sorted(entries.items())],
        current_exact_BtSave_Restore_sites=macros,phases=rows,inputs_only=[0,1],
        gameplay_seeds=0,ROM_changes=False,source_CPU_only=True,physical_FPS_claim=False,outputs=0,Mesen_run=False)


if __name__=='__main__':
    raw=C.load_current_image()
    def forbid(*args,**kwargs):raise RuntimeError('BT profile attempted file/Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Cold.Runner.Native,'run',forbid):q=profile(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
