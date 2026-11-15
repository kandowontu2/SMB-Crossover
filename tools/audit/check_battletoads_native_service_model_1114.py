"""Root-leased physical PRG read overlay; no composed ROM or native run."""
from collections import Counter
from copy import deepcopy
from contextlib import contextmanager
from hashlib import sha256
import argparse,json
from pathlib import Path
from unittest.mock import patch

import compose_battletoads_camera_handoff_1114 as BT
import compose_native_floatey_score_1114 as Score
import current_battletoads_dispatch_input_1114 as Input
import measure_battletoads_passthrough_fit_1114 as Fit
import check_battletoads_native_passthrough_research_1114 as Research
import profile_battletoads_current_idle_1114 as Profile
import check_battletoads_camera_candidate_1114 as Cold

W,N,Frames=Research.W,Research.N,Research.Frames
R=Path(__file__).resolve().parents[2]
LEASE=R/'docs/qa/allocations/battletoads-native-service-research-1114.json'
LEASE_SHA='be498c276f02b7602ea8ef60f7b0f2a6bb288e6c5488d72914ad3c52a4c83068'


def typed(raw):
    pin=sha256(raw).hexdigest();kind={BT.CANDIDATE:'f11',Score.CANDIDATE:'score-571'}.get(pin)
    assert kind is not None,'Unknown/dirty source-model input'
    return Input.normalize(raw,kind=kind)


def recipe(raw):
    base=typed(raw);data=LEASE.read_bytes();assert sha256(data).hexdigest()==LEASE_SHA;q=json.loads(data)
    assert sha256(raw).hexdigest()in q['eligible_actual_inputs_SHA256']
    assert sha256((R/q['proposal_tool']).read_bytes()).hexdigest()==q['proposal_tool_SHA256']
    assert not q['ROM_composition_authorized']and not q['native_or_delivery_authorized']
    changes={};spans=[]
    for row,make in zip(q['envelopes'],(Fit.router,Fit.head,Fit.side),strict=True):
        lo,hi=row['file_half_open'];code,labels=make();assert hi-lo==len(code)
        assert sha256(raw[lo:hi]).hexdigest()==row['old_SHA256']and sha256(code).hexdigest()==row['new_SHA256']
        assert raw[lo:hi]==base[lo:hi]
        changes.update({lo+i:v for i,v in enumerate(code)})
        spans.append(dict(file=[lo,hi],PRG=row['PRG'],CPU=row['CPU_half_open'],labels=labels))
    for at in q['prefix_operand_file_bytes']:
        assert raw[at:at+1].hex()==q['prefix_operand_old_hex'];changes[at]=int(q['prefix_operand_new_hex'],16)
    assert len(changes)==q['funded_bytes_total']==347
    assert not set(changes)&set(range(BT.BASE,BT.BASE+8192))
    assert not set(changes)&set(range(765863,765879))and not set(changes)&set(range(Score.AT,Score.AT+10))
    for name in('BtCheck',):
        b=Cold.bundle(base);at=W.location(b,name);assert not set(changes)&set(range(at,at+256))
    clock_fields=[dict(name=n,CPU=int(s['val'],0),physical_RAM3_offset=int(s['val'],0)&8191)
        for n,s in b['syms'].items()if n.startswith('Bt')and(int(s.get('val','0'),0)&8191)in(7904,7905)]
    return changes,dict(actual_input_SHA256=sha256(raw).hexdigest(),normalized_source_SHA256=BT.CANDIDATE,
        research_lease_SHA256=LEASE_SHA,model_envelope_bytes=347,changed_model_bytes=sum(raw[at]!=v for at,v in changes.items()),
        physical_PRG_read_overlay=True,whole_ROM_composed=False,spans=spans,
        entire_BT8192_cookie_Check_and_score10_untouched=True,private_clock_fields=clock_fields)


@contextmanager
def model_bus(raw,enabled):
    changes,info=recipe(raw);base=W.ControllerBus
    class Overlay(base):
        def __getitem__(self,at):
            if isinstance(at,int)and at>=0x8000 and getattr(self,'_overlay_enabled',True):
                tag=self.rawtags[(at-0x8000)//8192]
                if tag&128:
                    pos=16+(tag&127)*8192+(at&8191)
                    if pos in changes:return changes[pos]
            return super().__getitem__(at)
    with patch.object(W,'ControllerBus',Overlay if enabled else base):yield info


def cold(raw,key='rash',enabled=True):
    normalized=typed(raw);factory=Cold.F
    class Current:
        @staticmethod
        def bindings(image,identity):
            assert image==raw
            return factory.bindings(normalized,identity)
    with model_bus(raw,enabled),patch.object(Cold.Previous,'Factory',Current):
        m=Cold.Previous.cold(raw,key)
    assert m.bundle['raw']is raw,'Owning model retains actual input bytes'
    return m


def compare(pair,minimum):
    dummy=dict(A=0,X=0,Y=0,P=32,SP=253,minimum_SP=minimum)
    Research.compare(pair,[dummy,dummy],'actual opcode model')
    assert pair[0].vram==pair[1].vram and pair[0].ppuctrl==pair[1].ppuctrl
    assert Profile.state(pair[0])==Profile.state(pair[1])
    assert bytes(pair[0][0x15a:0x17b])==bytes(pair[1][0x15a:0x17b]),'End-of-Main complete SMC parity'


def profile(raw):
    _,info=recipe(raw);pair=[cold(raw,enabled=False),cold(raw)];base=N.NesMPU;b=pair[0].bundle
    points={}
    for name in('GameLoop','BtRouter','CfOrBtCheck','BtCheck'):
        points[((W.location(b,name)-16)//8192)|128,W.address(b,name)]=name
    points[254,0x9587]='NativeHead';points[254,0x958b]='NativeSide'
    points[255,0xe4a5]='BTHeadPass';points[161,0xbef1]='BTSidePass'
    for m in pair:
        for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    rows=[];minimum=255
    for phase,pad,count in(('idle',0,48),('walk_right',1,32)):
        counts=[Counter(),Counter()];cycles=[[],[]];pc_visits=Counter();entries=[0,0];returns=[0,0]
        for tick in range(count):
            for side,m in enumerate(pair):
                class Probe(base):
                    def __init__(self,*a,**k):super().__init__(*a,**k);self.pending=[]
                    def step(self):
                        nonlocal minimum
                        tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                        while self.pending and(self.pc,self.sp)==self.pending[-1]:self.pending.pop();returns[side]+=1
                        name=points.get((tag,self.pc))
                        if name:
                            counts[side][name]+=1
                            if name=='GameLoop':
                                entries[side]+=1
                                ret=m[256+((self.sp+1)&255)]+256*m[256+((self.sp+2)&255)]+1
                                self.pending.append((ret,(self.sp+2)&255))
                        if side:
                            at=16+(tag&127)*8192+(self.pc&8191)if tag&128 else-1
                            if any(lo<=at<hi for lo,hi in(q['file']for q in info['spans'])):pc_visits[tag,self.pc]+=1
                        minimum=min(minimum,self.sp);return super().step()
                m.controller_pad=pad
                with patch.object(N,'NesMPU',Probe):cycles[side].append(Frames.frame(m,whole_pass=True))
            assert entries==returns==[tick+1,tick+1],('Actual one Main per iteration',phase,tick,entries,returns)
            compare(pair,minimum)
        assert counts[1]['BtRouter']==7*count and counts[1]['BtCheck']==counts[1]['CfOrBtCheck']==5*count
        assert counts[1]['BTHeadPass']==count and counts[1]['BTSidePass']==4*count,dict(counts[1])
        assert all(counts[0][name]==counts[1][name]for name in('NativeHead','NativeSide')),[dict(c)for c in counts]
        row=dict(phase=phase,Main=count,one_GameLoop_entry_and_return_each=True,
            parent_cycles=cycles[0],overlay_cycles=cycles[1],mean_parent=sum(cycles[0])/count,mean_overlay=sum(cycles[1])/count,
            savings_histogram=dict(Counter(a-z for a,z in zip(*cycles,strict=True))),
            parent_calls=dict(counts[0]),overlay_calls=dict(counts[1]),final=Profile.state(pair[1]),
            actual_new_instruction_PCs=[dict(raw_tag=t,PC=pc,visits=n)for(t,pc),n in sorted(pc_visits.items())])
        rows.append(row);print('PROGRESS '+json.dumps(dict(phase=phase,mean_overlay=row['mean_overlay'],saving=row['savings_histogram'])),flush=True)
    assert raw[BT.BASE:BT.BASE+8192]==pair[1].bundle['raw'][BT.BASE:BT.BASE+8192]
    return dict(proposal=info,actual_opcode_profile=rows,minimum_SP=minimum,
        all_game_physical_RAM_OAM_VRAM_maps_and_end_SMC_exact=True,physical_FPS_claim=False,
        allocation_scope='Source model only; no ROM or native grant',outputs=0,Mesen_run=False)


def ingress_inventory(raw):
    _,info=recipe(raw);b=Cold.bundle(typed(raw));containers=[];relevant=[]
    for key,s in b['segs'].items():
        if not all(k in s for k in('start','size','ooffs')):continue
        start,size,at=(int(s[k],0)for k in('start','size','ooffs'))
        if at>=1048592 and size:
            containers.append(dict(id=key,name=s['name'],CPU=start,size=size,file=at,
                SHA256=sha256(raw[at:at+size]).hexdigest()))
        if start<=0xbee2<start+size or start<=0xe4a7<start+size:
            relevant.append(dict(id=key,name=s['name'],CPU=start,size=size,file=at))
    declarations=[]
    for name,s in b['syms'].items():
        if not any(term in name.lower()for term in('stream','decode','cookie','payload','pack')):continue
        if'val'not in s or'seg'not in s:continue
        seg=b['segs'].get(s['seg'],{});at=int(seg.get('ooffs','0'),0)
        if not at:continue
        value=int(s['val'],0);start=int(seg.get('start','0'),0)
        if 0x8000<=value<=0xffff and any(token in name for token in('Load','Decode','Ensure','ExpectedCookie','Stream')):
            declarations.append(dict(name=name,CPU=value,file=at+value-start,segment=seg.get('name')))
    return dict(proposal=info,CHR_container_segments=containers,target_address_segments=relevant,
        decoder_and_stream_declarations=declarations,inventory_only=True,decoded_ingress_closed=False,
        outputs=0,Mesen_run=False)


def interrupts(raw):
    changes,info=recipe(raw);base=N.NesMPU;m=cold(raw);b=m.bundle;captures={};minimum=255
    idle=W.address(b,'IdleLoop');skipped=W.address(b,'NmiSkipped')
    def point(c):
        tag=c.memory.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        at=16+(tag&127)*8192+(c.pc&8191)if tag&128 else-1
        return tag,c.pc,at
    class Capture(base):
        def step(self):
            tag,pc,at=point(self)
            if at in changes and N.get(self.memory,'NmiDisable')&128 and(tag,pc)not in captures:
                captures[tag,pc]=(N.fork(self.memory),{n:getattr(self,n)for n in('pc','sp','a','x','y','p')})
            return super().step()
    with patch.object(N,'NesMPU',Capture):
        for pad in(0,1):m.controller_pad=pad;Frames.frame(m,whole_pass=True)
    assert captures and len(captures)<160
    def same_memory(left,right,ignore=()):
        assert left.ram==right.ram and left.rawtags==right.rawtags and left.chr_latches==right.chr_latches
        assert left.vram==right.vram and(left.ppuctrl,left.upper)==(right.ppuctrl,right.upper)
        addresses=[*range(0x17b),*range(0x200,0x800),*range(0x5c00,0x8000)]
        diff=[at for at in addresses if at not in ignore and left[at]!=right[at]]
        assert not diff,('ISR application/global/SMC difference',diff[:16])
    def finish(arena,regs):
        nonlocal minimum
        z=N.fork(arena);c=base(memory=z,pc=regs['pc'])
        for name,value in regs.items():setattr(c,name,value)
        for _ in range(500000):
            if(c.pc,c.sp)==(idle,253):break
            minimum=min(minimum,c.sp);assert z[c.pc],('Continuation BRK',hex(c.pc));c.step()
        else:raise AssertionError('Real Main continuation bound')
        return z,{n:getattr(c,n)for n in('pc','sp','a','x','y','p')}
    counts=Counter();rows=[];effects=Counter();continuation_deltas=Counter();examples=[]
    for key,(arena,regs)in sorted(captures.items()):
        baseline,terminal=finish(arena,regs)
        kinds=('NMI',)if regs['p']&4 else('IRQ','NMI')
        for kind in kinds:
            results=[]
            for oracle in(False,True):
                z=N.fork(arena);z._overlay_enabled=not oracle;c=base(memory=z,pc=regs['pc'])
                for name,value in regs.items():setattr(c,name,value)
                assert N.get(z,'NmiDisable')&128
                start=N.get(z,'NmiSkipped');original=tuple(regs[n]for n in('pc','sp','a','x','y','p'))
                c.irq()if kind=='IRQ'else c.nmi()
                for _ in range(200000):
                    minimum=min(minimum,c.sp)
                    if(c.pc,c.sp)==original[:2]:break
                    assert z[c.pc],('Real ISR BRK',kind,hex(c.pc));c.step()
                else:raise AssertionError('Actual ISR return bound')
                result=tuple(getattr(c,n)for n in('pc','sp','a','x','y','p'))
                assert result[:5]==original[:5]and result[5]&0xef==original[5]&0xef
                assert bytes(z[0x101+regs['sp']:0x200])==bytes(arena[0x101+regs['sp']:0x200])
                assert z.ram==arena.ram and z.rawtags==arena.rawtags and z.chr_latches==arena.chr_latches
                assert bytes(z[0x15a:0x17b])==bytes(arena[0x15a:0x17b])
                assert(N.get(z,'NmiSkipped')-start)&255==int(kind=='NMI')
                results.append((z,{n:getattr(c,n)for n in('pc','sp','a','x','y','p')}))
            same_memory(results[0][0],results[1][0])
            for at in[*range(0x17b),*range(0x200,0x800),*range(0x5c00,0x8000)]:
                if arena[at]!=results[1][0][at]:effects[kind,at]+=1
            z,captured=results[0];after,final=finish(z,captured)
            assert(final['pc'],final['sp'])==(terminal['pc'],terminal['sp'])
            oracle,captured=results[1];oracle._overlay_enabled=True;expected,expected_regs=finish(oracle,captured)
            same_memory(after,expected);assert final==expected_regs;counts[kind]+=1
            for bank,(aa,bb)in enumerate(zip(baseline.ram,after.ram,strict=True)):
                for at,(a,zv)in enumerate(zip(aa,bb,strict=True)):
                    if a!=zv:continuation_deltas[kind,bank,at]+=1
            if len(examples)<4 and(baseline.ram!=after.ram or Profile.state(baseline)!=Profile.state(after)):
                examples.append(dict(kind=kind,raw_tag=key[0],PC=key[1],baseline_state=Profile.state(baseline),
                    interrupted_state=Profile.state(after),different_RAM=[dict(bank=k,offset=at,old=a,new=zv)
                        for k,(aa,bb)in enumerate(zip(baseline.ram,after.ram,strict=True))
                        for at,(a,zv)in enumerate(zip(aa,bb,strict=True))if a!=zv][:16]))
        rows.append(dict(raw_tag=key[0],PC=key[1],actual_SP=regs['sp'],actual_P=regs['p'],arms=list(kinds)))
        if len(rows)%16==0:print('PROGRESS '+json.dumps(dict(ISR_PCs=len(rows),cuts=dict(counts),minimum_SP=minimum)),flush=True)
    return dict(proposal=info,actual_reached_new_instruction_cuts=rows,cuts=dict(counts),minimum_SP=minimum,
        exact_ISR_AXYP_SP_maps_SMC_live_stack=True,all_ISR_global_effects_match_unmodified_current571_oracle=True,
        actual_reference_ISR_effects=[dict(kind=k,address=at,count=n)for(k,at),n in sorted(effects.items())],
        full_Main_all_RAM_VRAM_maps_globals_regs_SMC_exact_vs_equally_interrupted_oracle=True,
        no_event_Main_equality_not_assumed=True,no_event_continuation_different_RAM=[dict(kind=k,bank=b,offset=at,count=n)for(k,b,at),n in sorted(continuation_deltas.items())],
        no_event_continuation_examples=examples,
        regular_NMI_inside_Main_busy_unreachable=True,forced_regular_NMI_arms=0,outputs=0,Mesen_run=False)


def stage(raw,key):
    """Frozen ordinary policy, rebound only to owning input for the source overlay."""
    _,info=recipe(raw);normalized=typed(raw);frozen=Cold.F;pin=sha256(raw).hexdigest()
    class Current:
        ROM=Input.ROM
        @staticmethod
        def normalize(image):return frozen.normalize(typed(image))
        @staticmethod
        def bindings(image,identity):
            assert image==raw;typed(image);q=deepcopy(frozen.bindings(normalized,identity));q['sha']=pin
            for h in q['hooks'].values():
                if'bank'in h:
                    at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
            return q
        @staticmethod
        def controller(image,identity):
            config=Current.bindings(image,identity);text=frozen.controller(normalized,identity)
            lua=frozen.Previous.Parent.Frozen.lua;prefix='local C='+lua(frozen.bindings(normalized,identity))+'\n'
            assert text.startswith(prefix);out='local C='+lua(config)+'\n'+text[len(prefix):]
            frozen.Frozen.LuaRuntime().compile(out);return out
        @staticmethod
        def metadata(image,identity):
            q=deepcopy(frozen.metadata(normalized,identity));q['ROM_SHA256']=pin
            q['controller_SHA256']=sha256(Current.controller(image,identity).encode()).hexdigest()
            q['source_model_overlay_lease']=LEASE_SHA;q['native_controller_qualified']=False;return q
    with patch.object(Cold.Runner,'Factory',Current),patch.object(Cold.Runner,'cold',lambda image,identity:cold(image,identity)):
        result=Cold.Runner.run(raw,key,6500)
    assert result['passed'],result
    return dict(proposal=info,frozen_source_policy=True,only_config_rebound=True,route=result,
        model_only_not_native_candidate=True,outputs=0,Mesen_run=False)


def units(raw):
    _,info=recipe(raw);seeds=[cold(raw,enabled=False),cold(raw)];cases=Counter();savings={};minimum=255
    for kind,ys in(('head',range(7)),('side',range(7)),('slot9',(0,)),('slot29',(0,))):
        histogram=Counter()
        for y in ys:
            for p in range(32,256):
                if not p&32:continue
                pair=[N.fork(seed)for seed in seeds];results=[Research.execute(m,kind,p,y)for m in pair]
                Research.compare(pair,results,kind);cases[kind]+=1
                histogram[results[0]['CPU']-results[1]['CPU']]+=1;minimum=min(minimum,*(q['minimum_SP']for q in results))
        savings[kind]=dict(histogram)
    return dict(proposal=info,actual_proposed_opcodes=True,component_cases=dict(cases),cycles_saved=savings,minimum_SP=minimum,
        exact_AXY_P_SP_native_fields_physical_RAM_maps=True,foreign_branch_contract='Frozen4c8/Root70216 all256 owners/all128status detached executable endpoints',outputs=0,Mesen_run=False)


def paired_events(raw):
    """Same actual IRQ/NMI at common parent/model function entries; full Main parity."""
    _,info=recipe(raw);base=N.NesMPU;captures=[];minimum=255
    for enabled in(False,True):
        m=cold(raw,enabled=enabled)
        for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
        found={}
        class Capture(base):
            def step(self):
                mm=self.memory;tag=mm.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1;key=None
                if(tag,self.pc)==(255,0xe49a):key='head'
                elif(tag,self.pc)==(161,0xbea2):key='side'+str(self.y)
                elif(tag,self.pc)==(215,0xb08e):
                    slot=(mm[0x16c]-0x20)//3
                    if slot not in(10,14):key='router'+str(slot)
                if key and key not in found:found[key]=(N.fork(mm),{n:getattr(self,n)for n in('pc','sp','a','x','y','p')})
                return super().step()
        m.controller_pad=0
        with patch.object(N,'NesMPU',Capture):Frames.frame(m,whole_pass=True)
        captures.append(found)
    assert set(captures[0])==set(captures[1]),[sorted(c)for c in captures];cuts=Counter();states=[]
    for key in sorted(captures[0]):
        for kind in('IRQ','NMI'):
            pair=[];regs=[]
            for found in captures:
                seed,saved=found[key];m=N.fork(seed);c=base(memory=m,pc=saved['pc'])
                for name,value in saved.items():setattr(c,name,value)
                assert N.get(m,'NmiDisable')&128 and not c.p&4
                c.irq()if kind=='IRQ'else c.nmi();idle=W.address(m.bundle,'IdleLoop')
                for _ in range(500000):
                    if(c.pc,c.sp)==(idle,253):break
                    minimum=min(minimum,c.sp);assert m[c.pc],('Paired event BRK',key,kind,hex(c.pc));c.step()
                else:raise AssertionError(('Paired continuation bound',key,kind))
                pair.append(m);regs.append({n:getattr(c,n)for n in('pc','sp','a','x','y','p')})
            compare(pair,minimum)
            assert all(regs[0][n]==regs[1][n]for n in('pc','sp','a','x','y'))and regs[0]['p']&0xef==regs[1]['p']&0xef
            cuts[kind]+=1
        states.append(key)
    return dict(proposal=info,actual_common_entry_contexts=states,paired_parent_overlay_events=dict(cuts),minimum_SP=minimum,
        full_Main_regs_globals_SMC_physical_RAM_OAM_VRAM_maps_exact=True,outputs=0,Mesen_run=False)


def faults(raw):
    _,info=recipe(raw);seed=cold(raw);base=N.NesMPU;cases=Counter()
    class NoPrivate(base):
        def step(self):
            if self.pc>=0x8000:assert self.memory.rawtags[(self.pc-0x8000)//8192]!=3,('Unvalidated private execution',hex(self.pc))
            return super().step()
    for bad in range(17):
        fixture=N.fork(seed)
        if bad<16:fixture.ram[3][0x1fe0+bad]^=1
        else:fixture.ram[3][:]=bytes(8192)
        with patch.object(N,'NesMPU',NoPrivate):
            check=N.invoke(N.fork(fixture),'BtCheck',p=0xe5);assert not check['P']&1;cases['full_BtCheck_rejects']+=1
            for kind in('head','side'):
                for y in(0,1,2,5,6):
                    m=N.fork(fixture);before=tuple(map(bytes,m.ram));out=Research.execute(m,kind,0xe5,y)
                    oracle=N.fork(fixture);pc=0x9587 if kind=='head' else 0x958b
                    c=base(memory=oracle,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,7,y,0xe5,236;c.stPushWord(0x5aff)
                    for _ in range(2000):
                        if(c.pc,c.sp)==(0x5b00,236):break
                        c.step()
                    else:raise AssertionError('Native terrain oracle bound')
                    assert(out['A'],out['X'],out['Y'],out['P']&0xef,out['SP'])==(c.a,c.x,c.y,c.p&0xef,c.sp)
                    assert tuple(map(bytes,m.ram))==before;cases[kind]+=1
            for slot in(0,2,9,29):
                m=N.fork(fixture);before=tuple(map(bytes,m.ram));out=Research.execute(m,'slot'+str(slot),0xe5,0)
                assert not out['P']&1 and tuple(map(bytes,m.ram))==before;cases['slot'+str(slot)]+=1
    return dict(proposal=info,actual_opcode_fault_cases=dict(cases),each16_header_byte_plus_absent8192_cache=True,
        terrain_returns_exact_genuine_native_oracle=True,terrain_cache_rejection_intentionally_removed=True,
        full_BtCheck_and_private_movement_draw_rejection_unchanged=True,unvalidated_private_executions=0,private_RAM_writes=0,outputs=0,Mesen_run=False)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--profile',action='store_true');ap.add_argument('--ingress',action='store_true');ap.add_argument('--interrupts',action='store_true');ap.add_argument('--stage',action='store_true');ap.add_argument('--units',action='store_true');ap.add_argument('--paired-events',action='store_true');ap.add_argument('--faults',action='store_true');ap.add_argument('--identity',choices=('rash','zitz'),default='rash');args=ap.parse_args()
    raw=Input.ROM.read_bytes();typed(raw)
    def forbid(*a,**k):raise RuntimeError('Source model attempted file or Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Cold.Runner.Native,'run',forbid):
        q=faults(raw)if args.faults else paired_events(raw)if args.paired_events else units(raw)if args.units else stage(raw,args.identity)if args.stage else interrupts(raw)if args.interrupts else ingress_inventory(raw)if args.ingress else profile(raw)if args.profile else recipe(raw)[1]
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
