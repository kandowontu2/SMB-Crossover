"""Unallocated native/NoOp PC-routing research on f11; no instruction placement."""
from collections import Counter
from hashlib import sha256
import argparse,json
from pathlib import Path
from unittest.mock import patch

import compose_battletoads_camera_handoff_1114 as C
import check_battletoads_camera_candidate_1114 as Cold
import check_bub_current_budget_1113 as Frames
import profile_battletoads_current_idle_1114 as Profile
import current_battletoads_dispatch_input_1114 as Input

W,N=Cold.W,Cold.N


def route_redirect(cpu,validated=False):
    m=cpu.memory;tag=m.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1
    points=((3,0xb2d9),(3,0xb2eb),(215,0xb0b0))if validated else((255,0xe49d),(161,0xbec9),(215,0xb0b0))
    if(tag,cpu.pc)not in points:return None
    if N.get(m,'SelectedCharacter')!=33:return None
    if validated:
        if(tag,cpu.pc)==(3,0xb2d9):return 'validated_head',0x9587,(0x162,0x16a,0x16c,0x16d,0x179)
        if(tag,cpu.pc)==(3,0xb2eb):return 'validated_side',0x958b,(0x162,0x16a,0x16c,0x16d,0x179)
    else:
        if(tag,cpu.pc)==(255,0xe49d):return 'head',0x9587,(0x162,0x16a,0x16c,0x16d,0x179)
        if(tag,cpu.pc)==(161,0xbec9):return 'side',0xbeef,(0x162,0x16c,0x16d)
    if(tag,cpu.pc)==(215,0xb0b0)and cpu.x in(27,87):return 'slot'+str(cpu.x//3),0xb0ef,(0x162,0x16c,0x16d)
    return None


def execute(m,kind,p,y,fast=False,validated=False):
    if kind=='head':entry=W.address(m.bundle,'MmNativeHeadShortcut')
    elif kind=='side':entry=W.address(m.bundle,'MmNativeSideShortcut')
    else:
        entry=W.address(m.bundle,'FarCallCommon');slot=int(kind[4:]);target=0xb020+slot*3
        m[W.address(m.bundle,'SafecallA_SMC')+1]=85
        m[W.address(m.bundle,'FarcallJmpTarget_SMC')+1]=target&255;m[W.address(m.bundle,'FarcallJmpTarget_SMC')+2]=target>>8
    cpu=N.NesMPU(memory=m,pc=entry);cpu.a=215 if kind.startswith('slot')else 85
    cpu.x=7;cpu.y=y;cpu.p=p;cpu.sp=236;cpu.stPushWord(0x5aff);hits=0;minimum=cpu.sp
    for _ in range(100000):
        if(cpu.pc,cpu.sp)==(0x5b00,236):break
        tag=m.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1
        change=route_redirect(cpu,validated)if fast else None
        if change:cpu.pc=change[1];hits+=1
        minimum=min(minimum,cpu.sp);assert m[cpu.pc],('Research BRK',kind,hex(cpu.pc));cpu.step()
    else:raise AssertionError(('Research return bound',kind,hex(cpu.pc)))
    return dict(A=cpu.a,X=cpu.x,Y=cpu.y,P=cpu.p,SP=cpu.sp,CPU=cpu.processorCycles,hits=hits,minimum_SP=minimum)


def compare(pair,results,kind):
    assert all(results[0][k]==results[1][k]for k in('A','X','Y','SP')),(kind,results)
    assert results[0]['P']&0xef==results[1]['P']&0xef,(kind,results)
    assert tuple(map(bytes,pair[0].ram))==tuple(map(bytes,pair[1].ram)),('PhysicalRAM',kind)
    assert pair[0].rawtags==pair[1].rawtags and pair[0].chr_latches==pair[1].chr_latches
    live=range(0x5c00,0x8000);stack_floor=0x100+min(r['minimum_SP']for r in results)
    low_stack_globals=[at for at in range(0x100,stack_floor+1)if not 0x15a<=at<0x17b]
    delta=[at for at in list(range(256))+low_stack_globals+list(range(0x200,0x800))+list(live)if pair[0][at]!=pair[1][at]]
    assert not delta,('Live native RAM differences',kind,delta[:24])
    return [at for at in range(0x15a,0x17b)if pair[0][at]!=pair[1][at]]


def run(raw,validated=False):
    assert sha256(raw).hexdigest()==C.CANDIDATE
    m=Cold.cold(raw,'rash');b=m.bundle;hist={};smc={};cases=Counter();tiles=Counter()
    specs=(('head',range(7)),('side',range(7)),('slot9',(0,)),('slot29',(0,)))
    for kind,ys in specs:
        hist[kind]=Counter();smc[kind]=Counter()
        for y in ys:
            for p in range(256):
                if not p&32:continue
                pair=[N.fork(m),N.fork(m)];results=[execute(z,kind,p,y,fast=i==1,validated=validated)for i,z in enumerate(pair)]
                diff=compare(pair,results,kind);assert results[1]['hits']==1
                hist[kind][results[0]['CPU']-results[1]['CPU']]+=1;smc[kind].update(diff);cases[kind]+=1
                tiles[kind,results[0]['A']]+=1
    return dict(ROM_SHA256=C.CANDIDATE,explicit_component_fixtures=True,
        initial_state='Genuine Rash cold at40/176/HP47/lives2; only entry A/X/Y/P fixtures vary',
        prototype='CPU PC redirects only: '+('after-existing-full-check private Head/Side→native9587/958B'if validated else'UNQUALIFIED selected33 head/side shortcut')+'; slots9/29→existingNoB0EF',
        cases=dict(cases),architectural_AXY_P_SP_and_native_R_fields_exact=True,physical_RAM_and_maps_exact=True,
        optimistic_cycles_saved={k:dict(v)for k,v in hist.items()},SMC_different_offsets={k:dict(v)for k,v in smc.items()},
        native_result_domains=[dict(kind=k,result=a,cases=v)for(k,a),v in tiles.items()],
        caller_SMC_liveness_closed=False,ISR_new_path_closed=False,code_funding_closed=False,
        no_new_opcode_bytes_or_ROM_image=True,proposal_placed=False,allocation_granted=False,outputs=0,Mesen_run=False)


def routes(raw,validated=False):
    """Only actual normal inputs; track skipped transport fields until overwritten."""
    base_bus=W.ControllerBus
    class Bus(base_bus):
        def __getitem__(self,at):
            if isinstance(at,int)and at in getattr(self,'taint',()):
                kind,tag,pc=getattr(self,'cpu_point',('outside',-1,0))
                self.reads.append((kind,tag,pc,at))
                assert kind!='Main',('Skipped SMC field read before overwrite',tag,hex(pc),hex(at))
            return super().__getitem__(at)
        def __setitem__(self,at,value):
            if isinstance(at,int)and getattr(self,'cpu_point',('',))[0]=='Main':getattr(self,'taint',set()).discard(at)
            return super().__setitem__(at,value)
    with patch.object(W,'ControllerBus',Bus):m=Cold.cold(raw,'rash')
    pair=[N.fork(m),N.fork(m)];base=N.NesMPU;rows=[];hits=Counter();idle=W.address(m.bundle,'IdleLoop')
    for z in pair:z.taint=set();z.reads=[];z.cpu_point=('outside',-1,0)
    for phase,pad,count in(('idle',0,48),('walk_right',1,32)):
        hist=Counter();entries=Counter();returned=Counter()
        for main in range(count):
            cpus=[];cycles=[]
            for fast,z in enumerate(pair):
                class Probe(base):
                    def __init__(self,*args,**kwargs):
                        super().__init__(*args,**kwargs);self.kind='Main'if self.pc==idle else'NMI';self.pending=[];cpus.append(self)
                    def step(self):
                        tag=z.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                        z.cpu_point=(self.kind,tag,self.pc)
                        while self.pending and(self.pc,self.sp)==self.pending[-1]:self.pending.pop();returned[fast]+=1
                        if(tag,self.pc)==(254,W.address(z.bundle,'GameLoop')):
                            ret=z[256+((self.sp+1)&255)]+256*z[256+((self.sp+2)&255)]+1
                            self.pending.append((ret,(self.sp+2)&255));entries[fast]+=1
                        change=route_redirect(self,validated)if fast else None
                        if change:
                            name,target,fields=change;hits[phase,name]+=1;z.taint.update(fields);self.pc=target
                            tag=z.rawtags[(self.pc-0x8000)//8192];z.cpu_point=(self.kind,tag,self.pc)
                        return super().step()
                z.controller_pad=pad
                with patch.object(N,'NesMPU',Probe):cycles.append(Frames.frame(z,whole_pass=True))
                z.cpu_point=('outside',-1,0)
            assert entries==returned==Counter({0:main+1,1:main+1}),(phase,main,entries,returned)
            compare(pair,[dict(A=0,X=0,Y=0,P=32,SP=253,minimum_SP=180)]*2,phase)
            assert pair[0].vram==pair[1].vram and pair[0].ppuctrl==pair[1].ppuctrl
            assert Profile.state(pair[0])==Profile.state(pair[1])
            hist[cycles[0]-cycles[1]]+=1
        rows.append(dict(phase=phase,Main=count,one_GameLoop_entry_and_return_each=True,
            optimistic_cycles_saved=dict(hist),final=Profile.state(pair[1])))
    reads=Counter(pair[1].reads)
    return dict(ROM_SHA256=C.CANDIDATE,normal_inputs_only=[0,1],genuine_cold=True,
        route_phases=rows,skipped_paths=[dict(phase=p,service=s,count=n)for(p,s),n in sorted(hits.items())],
        architectural_state_global_RAM_physical_RAM_OAM_VRAM_maps_exact=True,
        Main_SMC_reads_before_overwrite=0,non_Main_transport_reads=[dict(kind=k,raw_tag=t,PC=pc,address=a,count=n)for(k,t,pc,a),n in sorted(reads.items())],
        remaining_tainted_fields=sorted(pair[1].taint),selectors_not_costed=True,
        no_new_opcode_bytes_or_ROM_image=True,proposal_placed=False,allocation_granted=False,outputs=0,Mesen_run=False)


def faults(raw,validated=False):
    seed=Cold.cold(raw,'rash');cases=Counter();failures=[]
    for bad in range(17):
        m=N.fork(seed)
        if bad<16:m.ram[3][0x1fe0+bad]^=1
        else:m.ram[3][:]=bytes(8192)
        for kind in('head','side','slot9','slot29'):
            for y in((0,1,2,5,6)if kind in('head','side')else(0,)):
                pair=[N.fork(m),N.fork(m)];results=[execute(z,kind,0xe5,y,fast=i==1,validated=validated)for i,z in enumerate(pair)]
                try:compare(pair,results,kind)
                except AssertionError as error:failures.append(dict(fault=bad,kind=kind,y=y,results=results,error=str(error)))
                cases[kind]+=1
    return dict(ROM_SHA256=C.CANDIDATE,cases=dict(cases),negative_fixture='Each16 header bytes corrupted, or all8192 cache bytes zero; no claim of natural gameplay state',
        prototype='post-existing-check private queries'if validated else'UNQUALIFIED selected33 precheck bypass',
        different_cases=len(failures),different_case_counts=dict(Counter(q['kind']for q in failures)),first_difference=failures[:1],
        all_fault_architectural_parity=not failures,
        no_new_opcode_bytes_or_ROM_image=True,proposal_placed=False,allocation_granted=False,outputs=0,Mesen_run=False)


def lifecycle(raw):
    """Genuine Start/pause/resume, then declared retirement/dead component contexts."""
    base=N.NesMPU;phase='cold';hits=Counter()
    class Probe(base):
        def step(self):
            change=route_redirect(self)
            if change:
                name,target,_=change;m=self.memory
                ready=m.ram[3][W.address(m.bundle,'BtHostReady')&8191]
                hits[phase,name,N.get(m,'OperMode'),N.get(m,'GameEngineSubroutine'),ready,m.ram[3][0x1fe0]]+=1
                self.pc=target
            return super().step()
    old=Cold.cold(raw,'rash')
    with patch.object(N,'NesMPU',Probe):new=Cold.cold(raw,'rash')
    pair=[old,new];assert Profile.state(old)==Profile.state(new)and old.ram==new.ram and old.vram==new.vram
    status='GamePauseStatus'if'GamePauseStatus'in old.bundle['syms']else'PauseStatus';observed=[]
    for phase,pad,count in(('walk',1,32),('pause_edge',16,1),('paused',0,64),('resume_edge',16,1),('resumed',0,8)):
        flags=[]
        for tick in range(count):
            for fast,m in enumerate(pair):
                m.controller_pad=pad
                with patch.object(N,'NesMPU',Probe if fast else base):Frames.frame(m,whole_pass=True)
            assert Profile.state(old)==Profile.state(new)and old.ram==new.ram and old.vram==new.vram,(phase,tick)
            assert bytes(old[0:256])==bytes(new[0:256])and bytes(old[0x200:0x800])==bytes(new[0x200:0x800])
            flags.append(N.get(new,status))
        observed.append(dict(phase=phase,Main=count,pad=pad,pause_values=sorted(set(flags)),state=Profile.state(new)))
    assert any(all(v&1 for v in q['pause_values'])for q in observed if q['phase']=='paused'),observed
    assert not N.get(new,status)&1
    contexts=[]
    for context in('valid','actual_BtRetire','declared_native_death11','declared_not_ready0'):
        seed=N.fork(new)
        if context=='actual_BtRetire':N.invoke(seed,'BtRetire');assert seed.ram[3][0x1fe0]==0
        elif context=='declared_native_death11':N.put(seed,GameEngineSubroutine=11)
        elif context=='declared_not_ready0':seed.ram[3][W.address(seed.bundle,'BtHostReady')&8191]=0
        for kind in('head','side'):
            m=N.fork(seed);before=tuple(map(bytes,m.ram));out=execute(m,kind,0xe5,1,True)
            assert out['hits']==1 and tuple(map(bytes,m.ram))==before
            contexts.append(dict(context=context,kind=kind,native_query_result=out,private_RAM_writes=0))
    return dict(ROM_SHA256=C.CANDIDATE,genuine_cold_Start_and_control_only_pause_resume=True,
        phases=observed,actual_reached_routes=[dict(phase=p,kind=k,mode=o,engine=e,ready=r,cookie_magic=c,count=n)for(p,k,o,e,r,c),n in sorted(hits.items())],
        component_contexts=contexts,death_and_not_ready_are_declared_components_not_natural_death=True,
        cache_independent_terrain_queries_only=True,private_code_unvalidated=False,
        allocation_granted=False,no_new_opcode_bytes_or_ROM_image=True,outputs=0,Mesen_run=False)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--routes',action='store_true');ap.add_argument('--faults',action='store_true');ap.add_argument('--validated',action='store_true');ap.add_argument('--lifecycle',action='store_true');args=ap.parse_args()
    raw,input_info=Input.load()
    def forbid(*args,**kwargs):raise RuntimeError('BT passthrough research attempted file/Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Cold.Runner.Native,'run',forbid):q=lifecycle(raw)if args.lifecycle else faults(raw,args.validated)if args.faults else routes(raw,args.validated)if args.routes else run(raw,args.validated)
    q.update(input_info);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
