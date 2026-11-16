"""Actual a3fb cold/public/BT/ISR composition gates; no native or outputs."""
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
from unittest.mock import patch

import replay_dkjr_footer_bt91dc_current_1116 as F
import check_dkjr_footer_ryu_1116 as Ryu
import check_dkjr_footer_lifecycle_1116 as Lifecycle
import check_dkjr_carry_camera_lifecycle_1116 as ColdLife
import check_dkjr_carry_camera_route_1116 as Route
import check_dkjr_footer_irq_1116 as FooterIRQ
import check_dkjr_carry_camera_irq_1116 as CameraIRQ
import current_battletoads_mature8_1116 as BTReference

C,N,W,L,Q,V=F.C,Ryu.N,Ryu.W,Ryu.L,Ryu.Q,Ryu.V
H=lambda value:sha256(value).hexdigest()


def bt_cold(raw,key):
    assert H(raw)==C.CANDIDATE
    name,cycle,variant=BTReference.IDENTITIES[key]
    expected=bytearray(raw[C.BT.CACHE:C.BT.CACHE+8192]);expected[0x1fe0:0x1ff0]=raw[C.BT.COOKIE:C.BT.COOKIE+16]
    entry=W.address(W.Symbols.bundle(),'BtConstruct');seen=[];Base=N.NesMPU
    class CPU(Base):
        def step(self):
            m=self.memory
            if self.pc==entry and m.rawtags[(entry-0x8000)//8192]==3 and not seen:
                assert bytes(m.ram[3])==expected
                seen.append(dict(PC=self.pc,SP=self.sp,SHA256=H(bytes(m.ram[3])),cookie=expected[0x1fe0:0x1ff0].hex()))
            return super().step()
    class Factory:
        @staticmethod
        def bindings(image,identity):
            assert image is raw and identity==key
            return dict(name=name,variant=variant,navigation=[2,4,4]+[32]*cycle)
    with patch.object(BTReference.Previous.Cold,'Factory',Factory),patch.object(N,'NesMPU',CPU):
        m=BTReference.Previous.Cold.cold(raw,key)
    assert seen and m.bundle['raw']is raw
    return m,dict(identity=key,variant=variant,actual_current_constructor_readback=seen[0])


def mains(seed,parent,candidate,name):
    models=[Ryu.mount(seed,raw)for raw in(parent,candidate)]
    counts=[Counter(),Counter()];minimum=255
    for m in models:
        for slot in range(6):N.invoke(m,'EraseEnemyObject',x=slot)
        for field,value in dict(Enemy_ID=37,Enemy_Flag=1,Enemy_State=0,
            Enemy_X_Position=N.get(m,'Player_X_Position'),Enemy_PageLoc=N.get(m,'Player_PageLoc'),
            Enemy_Y_Position=(N.get(m,'Player_Y_Position')+32)&255,Enemy_Y_HighPos=1).items():
            m[W.address(m.bundle,field)+3]=value
        N.invoke(m,'InitEnemyObject',x=3);m[W.address(m.bundle,'Enemy_BoundBoxCtrl')+3]=5
    cuts=[]
    for tick in range(8):
        for index,m in enumerate(models):
            def watch(memory,c):
                nonlocal minimum
                minimum=min(minimum,c.sp)
                tag=memory.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
                if(tag,c.pc)==(128,0xb43f):counts[index]['actual_large_dispatch']+=1
                if index==1 and tick==0 and(tag,c.pc)==(128,0xb442):cuts.append(L.clone(memory,c))
            Q.frame(m,0 if tick<4 else 1,watch)
        assert Ryu.native_data(models[0])==Ryu.native_data(models[1]),(name,tick,'full actual Main data')
        assert bytes(models[0][0x15a:0x17b])==bytes(models[1][0x15a:0x17b])
        assert models[0].contact_frame_registers==models[1].contact_frame_registers
    assert counts[0]==counts[1]and counts[1]['actual_large_dispatch']>=8
    return dict(name=name,actual_Main_updates=8,calls=dict(counts[1]),minimum_SP=minimum,
        full_AXYP_SMC33_private_native_maps_graphics_exact=True),cuts[:1]


def interrupts(seed,parent,candidate,foreign_cuts):
    """Composition samples only; unchanged62-PC/218-cut proof stays versioned."""
    changed={(((i-16)//8192)|128,(i-16)&8191)for i,(a,b)in enumerate(zip(parent,candidate))if a!=b}
    FooterIRQ.CURRENT=candidate
    contexts=[];seen=[]
    for case in(dict(name='eligible-public',entry='native'),dict(name='paused-direct-public',entry='native',timer=255)):
        m,c=FooterIRQ.start(seed,case);cuts=[]
        def observe(memory,cpu):
            tag=CameraIRQ.tag(cpu)
            if(tag,cpu.pc)in((128,0xb707),(128,0xb9a3),(128,0xb442))and not any(t==cpu.pc for t,_,_ in cuts):
                cuts.append((cpu.pc,*L.clone(memory,cpu)))
        CameraIRQ.run(m,c,(0x5b00,224),observe)
        seen.extend((case['name'],memory,cpu,(0x5b00,224))for _,memory,cpu in cuts)
    for index,(memory,cpu)in enumerate(foreign_cuts):seen.append(('foreign-Main-'+str(index),memory,cpu,(W.address(memory.bundle,'IdleLoop')+12,252)))
    # The freshly imported camera helper is exercised by its public caller.
    m,c=CameraIRQ.start(seed,dict(name='current-camera',delta=1))
    camera_cuts=[]
    def watch(memory,cpu):
        if CameraIRQ.tag(cpu)==3 and cpu.pc in(0xb770,0xb773)and not any(at==cpu.pc for at,_,_ in camera_cuts):
            camera_cuts.append((cpu.pc,*L.clone(memory,cpu)))
    CameraIRQ.run(m,c,(0x5b00,224),watch)
    assert len(camera_cuts)==2
    seen.extend(('camera-'+hex(at),memory,cpu,(0x5b00,224))for at,memory,cpu in camera_cuts)
    counts=Counter();minimum=255
    for name,m,c,stop in seen:
        for kind in('IRQ','lagNMI'):
            if kind=='IRQ'and c.p&4:continue
            q,z,mate,d,low,pending,_=V.matched_isr(m,c,parent,kind,changed)
            minimum=min(minimum,low);assert not pending
            CameraIRQ.run(q,z,stop);CameraIRQ.run(mate,d,stop)
            assert V.result(q,z)==V.result(mate,d)and bytes(q[0x100:0x200])==bytes(mate[0x100:0x200])
            Q.frame(q,0);Q.frame(mate,0)
            assert Ryu.native_data(q)==Ryu.native_data(mate)and q.contact_frame_registers==mate.contact_frame_registers
            assert bytes(q[0x15a:0x17b])==bytes(mate[0x15a:0x17b])
            counts[kind]+=1
        contexts.append(dict(name=name,PC=c.pc,SP=c.sp))
    assert counts['IRQ']and counts['lagNMI']
    return dict(cuts=contexts,vectors=dict(counts),minimum_ISR_SP=minimum,
        matched_current_unmodified_ISR_and_actual_public_plus_next_Main_exact=True,
        scope='Current composition samples; historical full218cut/all62PC gate retained separately, not relabeled')


def main():
    parent=C.BT.ROM.read_bytes();candidate,composition=C.proposal(parent)
    assert C.inverse(candidate)==parent
    native=F.controller(candidate);source=F.source_controller(candidate)
    print('DKJR_CURRENT_JOIN_PHASE actual-cold',flush=True)
    cookie=candidate[534485:534501];body=C.Camera.payload(candidate)
    readbacks=[];pending=None;Base=N.NesMPU
    class ColdReadback(Base):
        def step(self):
            nonlocal pending
            m=self.memory
            # Same actual loader-return boundary authenticated inside H.cold.
            # Constructor later rewrites legitimate private SMC operands.
            if self.pc==0xd25e and m.rawtags[2]==2:
                pending=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1,(self.sp+2)&255)
            if pending==(self.pc,self.sp):
                assert self.p&1 and bytes(m.ram[3][:0x1fe0])==body[:0x1fe0]
                assert bytes(m.ram[2][0x1000:0x1800])==body[9*1024:]
                readbacks.append(dict(PC=self.pc,SP=self.sp,packet_SHA256=H(body),code_bytes=8160,data_bytes=2048))
                pending=None
            return super().step()
    with patch.object(N,'NesMPU',ColdReadback):opening,seed=Route.cold(candidate)
    assert readbacks
    assert seed.bundle['raw']==candidate and all(bytes(seed.ram[b][0x1fe0:0x1ff0])==cookie for b in(2,3))
    print('DKJR_CURRENT_JOIN_PHASE cold-fault-retire-header',flush=True)
    cold=ColdLife.cold_cases(seed,candidate);retire=ColdLife.retire_cases(seed,candidate)
    headers=Lifecycle.header_contact(seed)
    print('DKJR_CURRENT_JOIN_PHASE foreign-BT-Main',flush=True)
    inventory=Q.Roster.Starts.C.inventory(parent)['rows'];rows=[];cuts=[];bt=[]
    for owner in(0,41):
        row=next(r for r in inventory if r['raw']==owner)
        bundle=dict(W.Symbols.bundle(),raw=candidate);_,m=Q.Roster.cold(bundle,row)
        result,part=mains(m,parent,candidate,row['name']);rows.append(result);cuts.extend(part)
    for key in('rash','zitz'):
        m,readback=bt_cold(candidate,key);bt.append(readback)
        result,part=mains(m,parent,candidate,key);rows.append(result);cuts.extend(part)
    print('DKJR_CURRENT_JOIN_PHASE Ryu-real-continuation',flush=True)
    bundle=dict(W.Symbols.bundle(),raw=candidate)
    _,ryu=Q.Roster.cold(bundle,dict(name='RYU HAYABUSA',slot=10,cycle=0,raw=10))
    actual_Ryu=[]
    for kind in(0,37,40,43,255):
        for scene in('ordinary','authored'):
            actual_Ryu.append(Ryu.pair(ryu,parent,candidate,kind,scene,p=0x79,saved=0x5a))
    ryu_mains=[]
    for kind in(37,40):
        paired,origin,seen=Ryu.Old.collect(parent,candidate,kind,'authored');outputs=[]
        for state,cpu in paired:
            L.finish(state,cpu,(W.address(state.bundle,'IdleLoop')+12,252),observe=lambda m,c:V.declared_admission(m,c,origin))
            outputs.append(Ryu.Old.outcome(state,cpu))
        assert outputs[0]==outputs[1]
        ryu_mains.append(dict(kind=kind,actual_LPC_caller_returns=seen,full_continuation_exact=True))
    print('DKJR_CURRENT_JOIN_PHASE reached-composition-ISR',flush=True)
    irq=interrupts(Q.C.setup(seed),parent,candidate,cuts)
    report=dict(passed=True,composition=composition,actual_CPU_ROM_SHA256=H(candidate),historical_reference_executed=False,
        native_Lua_SHA256=H(native.encode()),source_Lua_SHA256=H(source.encode()),
        actual_compiled_DK_cold=opening,actual_loader_readbacks=readbacks,
        retained_fixture_negative='Initial current checker incorrectly compared whole code after constructor SMC initialization; replaced by the same actual pre-initialization loader-return boundary. No game bytes or RAM exceptions changed.',
        cold_fault_retry=cold,retirement=retire,malformed_headers=headers,
        BT_actual_cold=bt,actual_foreign_Main=rows,Ryu_public_cases=len(actual_Ryu),Ryu_actual_Main=ryu_mains,interrupts=irq,
        ordinary_full_route_not_qualified=True,outputs=0,native_claim=False)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_CURRENT_JOIN '+encoded,flush=True);print('DKJR_CURRENT_JOIN_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
