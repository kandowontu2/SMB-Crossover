"""Actual mounted funded-idle opcodes; bounded, source-only, zero files."""
from collections import Counter
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json
from py65.disassembler import Disassembler

import compose_battletoads_idle_funded_1115 as C
import replay_battletoads_idle_funded_1115 as F
import check_battletoads_native_service_model_1114 as M

R=C.Packet
W,N,Frames=R.W,R.N,R.Frames
OPAQUE={0x162,0x16c,0x16d}


def progress(**q):print('PROGRESS '+json.dumps(q,separators=(',',':')),flush=True)


@lru_cache(maxsize=2)
def symbols(raw):
    parent=C.inverse(raw)if sha256(raw).hexdigest()==C.CANDIDATE else raw
    assert sha256(parent).hexdigest()==C.PIN
    return dict(R.bundle(parent),raw=raw)


def cold(raw,key='rash'):
    b=symbols(raw);legacy=F.Previous.Score.inverse(F.Previous.parent(R.reference(C.inverse(raw)if sha256(raw).hexdigest()==C.CANDIDATE else raw)))
    class Factory:
        @staticmethod
        def bindings(image,identity):
            assert image is raw
            return F.Previous.Stage.bindings(legacy,identity)
    with patch.object(R.Frozen.Cold.Previous,'Factory',Factory):
        m=R.Frozen.Cold.Previous.cold(raw,key)
    assert m.bundle['raw']is raw and type(m) is W.ControllerBus
    return m


def strict(parent,image):
    info=C.proposal(parent)[1];rejects=[]
    def rejected(name,raw,method):
        try:method(raw)
        except AssertionError:rejects.append(name)
        else:raise AssertionError(('Wrong input accepted',name))
    for name,raw,method in(('parent_inverse',parent,C.inverse),('candidate_forward',image,C.proposal),
            ('truncated',image[:-1],C.inverse),('unknown',bytes(len(image)),C.inverse)):
        rejected(name,raw,method)
    for name,at in(('owned',653512),('cookie',765868),('score',1034694),('Gimmick',201137),
            ('Prince',1700000),('DK',105706),('common_reset',1034868),('unowned',90000)):
        dirty=bytearray(image);dirty[at]^=1;rejected(name,bytes(dirty),C.inverse)
        dirty=bytearray(parent);dirty[at]^=1;rejected('forward_'+name,bytes(dirty),C.proposal)
    reader=Path.read_bytes
    def guarded(path):
        assert path.resolve()!=F.ROM.resolve(),'Portable operation read mutable Downloads'
        return reader(path)
    C.inverse.cache_clear();C.proposal.cache_clear()
    with patch.object(Path,'read_bytes',guarded):
        assert C.inverse(image)==parent and C.proposal(parent)[0]==image
        metadata=F.metadata(image)
    return dict(info,strict_rejections=rejects,portable_inverse_roundtrip=True,mutable_ROM_reads_after_load=0,
        controllers=metadata,outputs=0)


def compare_memory(pair,minimum=152,opaque=()):
    dummy=dict(A=0,X=0,Y=0,P=32,SP=253,minimum_SP=minimum)
    M.Research.compare(pair,[dummy,dummy],'mounted source parity')
    assert pair[0].vram==pair[1].vram and pair[0].ppuctrl==pair[1].ppuctrl
    diff={at for at in range(0x15a,0x17b)if pair[0][at]!=pair[1][at]}
    assert diff<=set(opaque),('Unapproved SMC difference',sorted(diff))
    return sorted(diff)


def compare_component(pair,out,minimum=152,opaque=()):
    # N.invoke itself asserts its final SP224; its compact receipt omits SP.
    checked=[dict(row,SP=row.get('SP',224),minimum_SP=min(minimum,row['minimum_SP']))for row in out]
    M.Research.compare(pair,checked,'mounted component')
    diff={at for at in range(0x15a,0x17b)if pair[0][at]!=pair[1][at]}
    assert diff<=set(opaque),('Component SMC difference',sorted(diff))
    assert pair[0].vram==pair[1].vram and pair[0].ppuctrl==pair[1].ppuctrl
    return sorted(diff)


def foreign(parent,image):
    ms=[]
    for raw in(parent,image):
        m=N.Bus(symbols(raw));m.raw_page(1,207);N.put(m,CurrentBank=207,CurrentBankC=m.rawtags[2]);ms.append(m)
    fields={name:W.address(ms[0].bundle,name)for name in('SelectedCharacter','FmAlts','RdVariant')}
    cases=0;ends=Counter();minimum=255
    for owner in range(256):
        variants=[(fm,0)for fm in(0,4,32,36,64,68,96,100)]if owner in(9,10)else[(0,rd)for rd in(0,1,2)]if owner==2 else[(0,0)]
        for fm,rd in variants:
            for slot in range(36):
                if owner==33 and slot in(12,13):continue
                for p in(0x20,0x31,0x69,0xe5):
                    pair=[]
                    for m in ms:
                        for name,value in(('SelectedCharacter',owner),('FmAlts',fm),('RdVariant',rd)):m[fields[name]]=value
                        c=N.NesMPU(memory=m,pc=0xb600+16*slot);c.a=85;c.x=7;c.y=91;c.p=p;c.sp=224;c.stPushWord(0x5aff)
                        for step in range(1000):
                            if c.pc in(0x15a,0x15d,0x5b00):break
                            minimum=min(minimum,c.sp);assert m[c.pc],('Selector BRK',owner,slot,c.pc);c.step()
                        else:raise AssertionError(('Selector bound',owner,slot))
                        pair.append((c.pc,c.a,c.x,c.y,c.p&0xef,c.sp,bytes(m[:0x17b]),bytes(m[0x200:0x800]),
                            bytes(m[0x100+c.sp+1:0x200]),tuple(map(bytes,m.ram)),tuple(m.rawtags)))
                    assert pair[0]==pair[1],('Foreign endpoint',owner,fm,rd,slot,p,pair[0][:6],pair[1][:6])
                    cases+=1;ends[pair[0][0]]+=1
        if owner%64==63:progress(owner=owner,foreign_cases=cases)
    return dict(cases=cases,all256_owners_36_services_four_status_corners=True,minimum_SP=minimum,
        canonical_raw33_getters_separately_tested=True,exact_endpoint_AXYP_SP_RAM_maps_SMC=True,endpoints=dict(ends))


def units(parent,image):
    seeds=[cold(raw)for raw in(parent,image)];compare_memory(seeds);rows=[];minimum=255
    for name in('MegaManCollisionAdder','MegaManCollisionBox'):
        count=0;savings=Counter();smc=Counter()
        for p in range(256):
            if not p&32:continue
            for x,y in((0,0),(0,255),(71,109),(255,255)):
                pair=[N.fork(m)for m in seeds]
                out=[N.invoke(m,name,a=85,x=x,y=y,p=p)for m in pair]
                diff=compare_component(pair,out,opaque=OPAQUE)
                assert all(z['Y']==0 and z['P']&1 for z in out)
                minimum=min(minimum,*(z['minimum_SP']for z in out));savings[out[0]['CPU']-out[1]['CPU']]+=1
                smc[tuple(diff)]+=1;count+=1
        rows.append(dict(caller=name,cases=count,cycle_savings=dict(savings),SMC_differences=[dict(addresses=list(k),count=v)for k,v in smc.items()]))
        progress(caller=name,cases=count)
    return dict(actual_mounted_complete_frontends=rows,all128_valid_P_four_XY=True,minimum_SP=minimum,
        exact_AXYP_SP_RAM_maps_VRAM_except_only_three_opaque_published_operands=True)


def constructors(parent,image):
    captures,_=R.menu_captures(parent);rows=[];minimum=255;cases=0
    for key,(seed,regs)in captures.items():
        for p in range(256):
            if not p&32:continue
            for x,y in((0,255),(71,109)):
                pair=[];out=[]
                for raw,entry in((parent,0xba54),(image,0xba61)):
                    m=reimage(seed,raw);c=N.NesMPU(memory=m,pc=entry)
                    for name,value in regs.items():setattr(c,name,value)
                    c.pc=entry;c.p=p;c.x=x;c.y=y
                    low=c.sp
                    for _ in range(300000):
                        if(c.pc,c.sp)==(0x5b00,224):break
                        low=min(low,c.sp);assert m[c.pc],('Constructor BRK',key,c.pc);c.step()
                    else:raise AssertionError(('Constructor continuation bound',key,p,x,y,c.pc,c.sp))
                    pair.append(m);out.append(dict(A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,minimum_SP=low))
                    minimum=min(minimum,low)
                compare_component(pair,out);cases+=1
        rows.append(dict(menu=key,cases=256));progress(menu=key,constructor_cases=cases)
    return dict(actual_full_farcall_menu_continuation_cases=cases,menus=rows,all128validP_twoXY=True,
        declared_component_register_corners_not_natural_inputs=True,minimum_SP=minimum,
        exact_AXYP_SP_live_RAM_SMC_physical_RAM_VRAM_maps=True)


def reimage(seed,raw):
    m=N.fork(seed);m.bundle=dict(seed.bundle,raw=raw)
    tags=list(m.rawtags)
    for slot,tag in enumerate(tags):
        if tag&128:m.raw_page(slot,tag)
    return m


def profile(parent,image,counts=(48,32)):
    pair=[cold(raw)for raw in(parent,image)];rows=[];minimum=255;base=N.NesMPU
    points={(((W.location(pair[0].bundle,name)-16)//8192)|128,W.address(pair[0].bundle,name)):name
        for name in('AudioUpdate','BtCheck','BtRouter')if name in pair[0].bundle['syms']}
    for _ in range(4):
        for m in pair:m.controller_pad=0;Frames.frame(m,whole_pass=True)
        compare_memory(pair)
    for phase,pad,count in(('idle',0,counts[0]),('right',1,counts[1])):
        cycles=[[],[]];entries=[0,0];returns=[0,0];guard=Counter();calls=[Counter(),Counter()];heads=Counter()
        for tick in range(count):
            for side,m in enumerate(pair):
                class Probe(base):
                    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.pending=[]
                    def step(self):
                        nonlocal minimum
                        tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                        while self.pending and(self.pc,self.sp)==self.pending[-1]:self.pending.pop();returns[side]+=1
                        if(tag,self.pc)==(254,W.address(m.bundle,'GameLoop')):
                            entries[side]+=1;ret=m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1
                            self.pending.append((ret,(self.sp+2)&255))
                        if(tag,self.pc)in points:calls[side][points[tag,self.pc]]+=1
                        if side and tag==207 and self.pc==0xb8b8 and self.y in(12,13):guard[self.y]+=1
                        if side and tag==207 and(0xb8b8<=self.pc<0xb8e5 or 0xba61<=self.pc<0xbacd):heads[self.pc]+=1
                        minimum=min(minimum,self.sp);return super().step()
                m.controller_pad=pad
                with patch.object(N,'NesMPU',Probe):cycles[side].append(Frames.frame(m,whole_pass=True))
            assert entries==returns==[tick+1,tick+1],('Exactly one actual Main',phase,tick,entries,returns)
            compare_memory(pair);assert M.Profile.state(pair[0])==M.Profile.state(pair[1])
        progress(phase=phase,profile_parent_calls=dict(calls[0]),profile_mounted_calls=dict(calls[1]),
            parent_mean=sum(cycles[0])/count,mounted_mean=sum(cycles[1])/count,savings=dict(Counter(a-z for a,z in zip(*cycles,strict=True))))
        assert calls[0]==Counter(AudioUpdate=count,BtRouter=7*count,BtCheck=5*count),(phase,calls)
        assert calls[1]==Counter(AudioUpdate=count,BtRouter=5*count,BtCheck=3*count),(phase,calls)
        assert guard==Counter({12:count,13:count})
        row=dict(phase=phase,Main=count,one_entry_return_each=True,parent_cycles=cycles[0],mounted_cycles=cycles[1],
            mean_parent=sum(cycles[0])/count,mean_mounted=sum(cycles[1])/count,
            savings_histogram=dict(Counter(a-z for a,z in zip(*cycles,strict=True))),
            parent_calls=dict(calls[0]),mounted_calls=dict(calls[1]),getter_entries=dict(guard),actual_relocated_instruction_heads=dict(heads),final=M.Profile.state(pair[1]))
        rows.append(row);progress(phase=phase,parent=row['mean_parent'],mounted=row['mean_mounted'],savings=row['savings_histogram'])
    return dict(actual_mounted_profile=rows,minimum_SP=minimum,full_Main_RAM_VRAM_maps_SMC_exact=True,
        AudioUpdate_retained=True,source_cycles_only_no_native_cadence_or_FPS_claim=True)


def lifecycle(parent,image):
    pair=[cold(raw)for raw in(parent,image)];compare_memory(pair);phases=[]
    for phase,pad,count in(('walk',1,8),('pause_edge',16,1),('paused',0,64),('resume_edge',16,1),('resumed',0,8)):
        states=set()
        for _ in range(count):
            for m in pair:m.controller_pad=pad;Frames.frame(m,whole_pass=True)
            compare_memory(pair);states.add(N.get(pair[1],'GamePauseStatus'))
        phases.append(dict(phase=phase,Main=count,pad=pad,pause_values=sorted(states),state=M.Profile.state(pair[1])))
        progress(phase=phase,Main=count,pause=sorted(states))
    assert all(v&1 for v in phases[2]['pause_values'])and not N.get(pair[1],'GamePauseStatus')&1
    retired=[N.fork(m)for m in pair]
    for m in retired:N.invoke(m,'BtRetire');assert m.ram[3][0x1fe0]==0
    compare_memory(retired);rows=[]
    for name in('MegaManCollisionAdder','MegaManCollisionBox'):
        arenas=[N.fork(m)for m in retired];out=[N.invoke(m,name,a=85,x=7,y=91,p=0x20)for m in arenas]
        assert not out[0]['P']&1 and out[1]['Y']==0 and out[1]['P']&1
        assert arenas[0].ram==arenas[1].ram and arenas[0].rawtags==arenas[1].rawtags
        rows.append(dict(caller=name,parent={k:out[0][k]for k in('A','X','Y','P')},native={k:out[1][k]for k in('A','X','Y','P')}))
    # Corruption is an explicit diagnostic fixture, not a natural gameplay state.
    private=('slot0','slot2','slot9','slot29');faults=Counter()
    for fault in range(17):
        seeds=[N.fork(m)for m in pair]
        for m in seeds:
            if fault<16:m.ram[3][0x1fe0+fault]^=1
            else:m.ram[3][:]=bytes(8192)
        for name in('MegaManCollisionAdder','MegaManCollisionBox'):
            arenas=[N.fork(m)for m in seeds];out=[N.invoke(m,name,a=85,x=7,y=91,p=0x20)for m in arenas]
            assert not out[0]['P']&1 and out[1]['Y']==0 and out[1]['P']&1
            assert arenas[0].ram==arenas[1].ram and arenas[0].rawtags==arenas[1].rawtags
            faults['native_getter_intentional_admission']+=1
        for slot in private:
            arenas=[N.fork(m)for m in seeds];out=[M.Research.execute(m,slot,0x21,0)for m in arenas]
            compare_component(arenas,out);assert not out[1]['P']&1;faults['private_or_NoOp_rejection_parity']+=1
    death=[N.fork(m)for m in pair];out=[N.invoke(m,'HuDeathStart',a=33,p=0x21)for m in death]
    compare_component(death,out);events=[]
    for tick in range(8):
        for m in death:m.controller_pad=0;Frames.frame(m,whole_pass=True)
        compare_memory(death);events.append(M.Profile.state(death[1]))
    return dict(genuine_compiled_cold_Select_Start=True,ordinary_pause_resume=phases,retired_actual_API=rows,
        retired_getter_native_contract_changed=True,no_blanket_fault_parity_claim=True,
        explicit_17_corruption_fixtures=dict(faults),private_admission_BtCheck_unchanged=True,
        owning_death_scope='HuDeathStart public slot7 component request; not natural enemy or pit death',
        following_death_Main=8,death_events=events,natural_death_respawn_not_claimed=True,
        full_Main_RAM_SMC_maps_VRAM_exact=True)


def interrupts(parent,image):
    base=N.NesMPU;captures={};phase='cold';minimum=255
    ranges=[(at,at+len(bytes.fromhex(h)))for at,h in C.PREIMAGES]
    class Capture(base):
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw)
            self.funded_endpoint=(W.address(self.memory.bundle,'IdleLoop'),253)if self.pc==W.address(self.memory.bundle,'IdleLoop')else(0x5b00,224)
        def step(self):
            nonlocal minimum
            m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            at=16+(tag&127)*8192+(self.pc&8191)if tag&128 else-1
            # Bindings build read-only legacy menu metadata too. Those CPUs
            # are not executions of this mounted source image.
            if m.bundle['raw']is image and any(lo-2<=at<hi for lo,hi in ranges):
                length,_=Disassembler(self).instruction_at(self.pc)
                if any(at<hi and at+length>lo for lo,hi in ranges):
                    key=(phase,tag,self.pc,self.y if 0xb8b8<=self.pc<=0xb8c4 else-1,self.funded_endpoint)
                    if key not in captures:captures[key]=(N.fork(m),{n:getattr(self,n)for n in('pc','sp','a','x','y','p')},self.funded_endpoint)
            minimum=min(minimum,self.sp);return super().step()
    with patch.object(N,'NesMPU',Capture),patch.object(W.UI.F,'NesMPU',Capture):
        m=cold(image)
        for phase,pad in(('idle',0),('right',1)):
            m.controller_pad=pad;Frames.frame(m,whole_pass=True)
    assert captures and len(captures)<300,len(captures)
    # Capture the two other genuine compiled menu constructor paths as well.
    for menu,nav in(('gimmick',[1,4,4,4]),('donkey_kong',[4,4,4,1,1,1])):
        phase=menu
        with patch.object(N,'NesMPU',Capture),patch.object(W.UI.F,'NesMPU',Capture),patch.object(N,'Bus',W.ControllerBus):
            z=W.UI.seed(symbols(image),0)
            for pad in nav:W.UI.key(z,pad)
    rows=[];counts=Counter();effects=Counter();physical_effects=Counter();chr_effects=Counter()
    def finish(seed,regs,endpoint):
        z=reimage(seed,image);c=base(memory=z,pc=regs['pc'])
        for name,value in regs.items():setattr(c,name,value)
        for _ in range(500000):
            if(c.pc,c.sp)==endpoint:break
            assert z[c.pc],('ISR continuation BRK',hex(c.pc),regs);c.step()
        else:raise AssertionError(('ISR continuation bound',endpoint,c.pc,c.sp,regs))
        return z,tuple(getattr(c,n)for n in('pc','sp','a','x','y','p'))
    for key,(arena,regs,endpoint)in sorted(captures.items()):
        assert arena.bundle['raw']is image
        assert N.get(arena,'NmiDisable')&128,('Reached nonbusy arm needs separate qualification',key)
        kinds=('NMI',)if regs['p']&4 else('IRQ','NMI')
        for kind in kinds:
            results=[]
            for raw in(parent,image):
                z=reimage(arena,raw);c=base(memory=z,pc=regs['pc'])
                for name,value in regs.items():setattr(c,name,value)
                original=tuple(regs[n]for n in('pc','sp','a','x','y','p'));skipped=N.get(z,'NmiSkipped')
                c.irq()if kind=='IRQ'else c.nmi()
                for _ in range(200000):
                    minimum=min(minimum,c.sp)
                    if(c.pc,c.sp)==original[:2]:break
                    assert z[c.pc],('ISR BRK',key,kind,hex(c.pc));c.step()
                else:raise AssertionError(('ISR return bound',key,kind))
                actual=tuple(getattr(c,n)for n in('pc','sp','a','x','y','p'))
                assert actual[:5]==original[:5]and actual[5]&0xef==original[5]&0xef,(key,kind,original,actual)
                assert z.rawtags==arena.rawtags,('ISR PRG map restore',key,kind,arena.rawtags,z.rawtags)
                assert bytes(z[0x15a:0x17b])==bytes(arena[0x15a:0x17b])
                assert bytes(z[0x101+regs['sp']:0x200])==bytes(arena[0x101+regs['sp']:0x200])
                assert(N.get(z,'NmiSkipped')-skipped)&255==int(kind=='NMI')
                results.append((z,{n:getattr(c,n)for n in('pc','sp','a','x','y','p')}))
            compare_memory([z for z,_ in results],min(152,minimum))
            assert results[0][1]==results[1][1]
            for at in[*range(0x17b),*range(0x200,0x800),*range(0x5c00,0x8000)]:
                if arena[at]!=results[1][0][at]:effects[kind,at]+=1
            for bank,(old,new)in enumerate(zip(arena.ram,results[1][0].ram,strict=True)):
                for at,(a,z)in enumerate(zip(old,new,strict=True)):
                    if a!=z:physical_effects[kind,bank,at]+=1
            for slot,(old,new)in enumerate(zip(arena.chr_latches,results[1][0].chr_latches,strict=True)):
                if old!=new:chr_effects[kind,slot,old,new]+=1
            ends=[finish(z,r,endpoint)for z,r in results]
            compare_memory([z for z,_ in ends],min(152,minimum));assert ends[0][1]==ends[1][1]
            counts[kind]+=1
        rows.append(dict(context=key[0],tag=key[1],PC=key[2],guard_Y=key[3],P=regs['p'],SP=regs['sp'],endpoint=list(endpoint),arms=list(kinds)))
        if len(rows)%16==0:progress(reached_instruction_cuts=len(rows),arms=dict(counts),minimum_SP=minimum)
    return dict(actual_mounted_reached_instruction_cuts=rows,cuts=dict(counts),minimum_SP=minimum,
        actual_interrupts_match_unmodified_parent_handler_oracle=True,
        both_equally_interrupted_continuations_execute_mounted_candidate=True,
        exact_AXYP_SP_live_stack_SMC_RAM_VRAM_maps=True,
        observed_ISR_effects=[dict(kind=k,address=at,count=n)for(k,at),n in sorted(effects.items())],
        observed_ISR_physical_RAM_effects=[dict(kind=k,bank=bank,offset=at,count=n)for(k,bank,at),n in sorted(physical_effects.items())],
        observed_ISR_CHR_publication=[dict(kind=k,slot=slot,old=old,new=new,count=n)for(k,slot,old,new),n in sorted(chr_effects.items())],
        regular_NMI_inside_busy_owning_components_unreachable=True,forced_regular_NMI_arms=0)


def stage(parent,image,key):
    with patch.object(R.Frozen.Cold.Runner,'Factory',F),patch.object(R.Frozen.Cold.Runner,'cold',cold):
        q=R.Frozen.Cold.Runner.run(image,key,6500)
    assert q['passed'],q
    return dict(identity=key,route=q,normal_controls_only=True,gameplay_seeds=0,actual_mounted_image=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('mode',choices=('strict','foreign','units','constructors','profile','profile-short','lifecycle','interrupts','rash','zitz','metadata'))
    args=ap.parse_args();parent=C.load_current_image();image,info=C.proposal(parent)
    def forbid(*a,**kw):raise RuntimeError('Source checker attempted file or native output')
    fn={'strict':strict,'foreign':foreign,'units':units,'constructors':constructors,'profile':profile,'profile-short':lambda p,z:profile(p,z,(2,2)),'lifecycle':lifecycle,'interrupts':interrupts,
        'rash':lambda p,z:stage(p,z,'rash'),'zitz':lambda p,z:stage(p,z,'zitz'),'metadata':lambda p,z:F.metadata(z)}[args.mode]
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(R.Frozen.Cold.Runner.Native,'run',forbid):q=fn(parent,image)
    q.update(mode=args.mode,parent_SHA256=C.PIN,source_image_SHA256=C.CANDIDATE,source_only=True,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
