"""Actual Ryu28 caller/SMC liveness study; no new packing or ROM output."""
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from unittest.mock import patch

import check_dkjr_direct_foreign_funding_1113 as Fit
import check_dkjr_platform_contact_irq_1113 as V

Q,P,H,N,W,L=Fit.Q,Fit.P,Fit.H,Fit.N,Fit.W,Fit.L


def setup(parent,kind,scene):
    b=W.Symbols.bundle();b['raw']=parent
    _,m=Q.Roster.cold(b,dict(name='RYU HAYABUSA',slot=10,cycle=0,raw=10))
    for i in range(6):N.invoke(m,'EraseEnemyObject',x=i)
    N.put(m,WorldNumber=0,LevelNumber=3 if scene=='authored'else 0,AreaType=3,
        SecondaryHardMode=0)
    slot=3
    for field,value in dict(Enemy_ID=kind,Enemy_Flag=1,Enemy_State=0,
        Enemy_X_Position=N.get(m,'Player_X_Position')-2,
        Enemy_PageLoc=N.get(m,'Player_PageLoc'),
        Enemy_Y_Position=160 if kind==40 else (N.get(m,'Player_Y_Position')+32)&255,
        Enemy_Y_HighPos=1).items():m[W.address(m.bundle,field)+slot]=value
    N.invoke(m,'InitEnemyObject',x=slot)
    m[W.address(m.bundle,'Enemy_BoundBoxCtrl')+slot]=5
    return m


def outcome(m,c):
    return V.result(m,c),bytes(m[0x101+c.sp:0x200])


def collect(parent,fixture,kind,scene):
    seed=setup(parent,kind,scene);models=[Q.mounted(seed,r)for r in(parent,fixture)]
    origin='RYU HAYABUSA authored'if scene=='authored'else'RYU HAYABUSA ordinary'
    cuts=[None,None];ends=[None,None];seen=[Counter(),Counter()]
    for age in range(32):
        for i,m in enumerate(models):
            def watch(mem,c):
                V.declared_admission(mem,c,origin)
                tag=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
                if(tag,c.pc)==(128,0xb486):
                    seen[i]['actual_LPC_return']+=1
                    if cuts[i]is None:cuts[i]=L.clone(mem,c)
            Q.frame(m,128 if age<12 else 0,watch)
            if cuts[i]is not None and ends[i]is None:ends[i]=L.clone(m)
        assert models[0].contact_frame_registers==models[1].contact_frame_registers
        assert V.result(models[0],N.NesMPU(memory=models[0]))[:-1]==V.result(models[1],N.NesMPU(memory=models[1]))[:-1]
    assert all(cuts)and seen[0]==seen[1],(kind,scene,seen)
    return cuts,origin,seen


def tracked(m,c,addresses):
    """Track CPU accesses, including SMC operand fetches and genuine ISR steps."""
    Base=type(m);CPU=type(c)
    class Bus(Base):
        def __getitem__(self,at):
            value=super().__getitem__(at)
            if isinstance(at,int)and at in self.dead_smc and self.smc_cpu_active:
                assert at in self.smc_written,('SMC read before current writer',hex(at),hex(self.smc_pc))
                self.smc_events.append(('R',self.smc_pc,at))
            return value
        def __setitem__(self,at,value):
            if isinstance(at,int)and self.smc_cpu_active:
                self.smc_written.add(at)
                if at in self.dead_smc:self.smc_events.append(('W',self.smc_pc,at))
            return super().__setitem__(at,value)
    class Trace(CPU):
        def step(self):
            self.memory.smc_cpu_active=True;self.memory.smc_pc=self.pc
            try:return CPU.step(self)
            finally:self.memory.smc_cpu_active=False
    m.__class__=Bus;c.__class__=Trace
    m.dead_smc=set(addresses);m.smc_written=set();m.smc_events=[];m.smc_cpu_active=False
    return Trace


def main():
    parent,_=Fit.T.load_inputs(reuse_private=True);fixture,info=Fit.parts(parent)
    assert parent[16+0x1483:16+0x1489]==bytes.fromhex('2063b9a60d60')
    rows=[];taints=0;vectors=Counter();all_smc=set();accesses=Counter()
    for kind,scene in product((37,40),('ordinary','authored')):
        cuts,origin,seen=collect(parent,fixture,kind,scene)
        smc={at for at in range(0x15a,0x17b)if cuts[0][0][at]!=cuts[1][0][at]}
        assert smc<={0x162,0x16a,0x16c,0x16d,0x179},(kind,scene,smc)
        all_smc|=smc
        # Dead A/NZCV is proved at the actual sole caller, preserving I/D.
        baseline=[]
        for state,cpu in cuts:
            m,c=L.clone(state,cpu)
            L.finish(m,c,(W.address(m.bundle,'IdleLoop')+12,252),
                observe=lambda m,c:V.declared_admission(m,c,origin))
            baseline.append(outcome(m,c))
        assert baseline[0]==baseline[1],(kind,scene,'original versus Ryu28 complete caller continuation')
        for a,flags in product((0,1,40,255),range(16)):
            m,c=L.clone(*cuts[1]);c.a=a
            c.p=(c.p&~0xc3)|(flags&3)|((flags&4)<<4)|((flags&8)<<4)
            L.finish(m,c,(W.address(m.bundle,'IdleLoop')+12,252),
                observe=lambda m,c:V.declared_admission(m,c,origin))
            assert outcome(m,c)==baseline[1],(kind,scene,a,flags,'caller live result')
            taints+=1
        for vector in('none','IRQ','lagNMI'):
            results=[]
            for state,cpu in cuts:
                m,c=L.clone(state,cpu);Trace=tracked(m,c,smc)
                if vector!='none':
                    # The actual vector executes with tracked SMC operand reads.
                    with patch.object(N,'NesMPU',Trace):V.Lease.inject_checked(c,vector)
                    vectors[vector]+=1
                L.finish(m,c,(W.address(m.bundle,'IdleLoop')+12,252),
                    observe=lambda m,c:V.declared_admission(m,c,origin))
                for event,pc,at in m.smc_events:accesses[event]+=1
                results.append(outcome(m,c))
            assert results[0]==results[1],(kind,scene,vector,'paired genuine vector and caller return')
        rows.append(dict(native_ID=kind,scene=scene,actual_LPC_return_cuts=seen,
            differing_intermediate_SMC=sorted(hex(at)for at in smc),
            full_AXYP_live_stack_WRAM_SRAM_maps_graphics_equal=True))
        print('DKJR_RYU28_CALLER_ROW '+json.dumps(rows[-1],separators=(',',':')),flush=True)
    print('DKJR_RYU28_CALLER '+json.dumps(dict(passed=True,parent_SHA256=sha256(parent).hexdigest(),
        isolated_fixture_SHA256=sha256(fixture).hexdigest(),actual_caller_PC=0xb486,
        caller_preimage='a60d60',A_NZCV_taint_cases=taints,taint_preserves_incoming_I_D=True,
        intermediate_SMC=sorted(hex(at)for at in all_smc),actual_CPU_SMC_accesses=dict(accesses),
        every_differing_SMC_read_follows_current_writer=True,real_vector_runs=dict(vectors),
        outputs_written=0,full_fast_dispatch_candidate=False,grant=False,native_ready=False),separators=(',',':')),flush=True)


if __name__=='__main__':main()
