"""Reached footer/Ryu/foreign IRQ cuts with actual public continuations."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import check_dkjr_footer_ryu_1116 as R
import check_dkjr_carry_camera_route_1116 as Route
import check_dkjr_carry_camera_irq_1116 as Helpers
import dkjr_footer_source_input_1116 as Input

C,N,W,L,Q,V=R.C,R.N,R.W,R.L,R.Q,R.V
H=lambda value:sha256(value).hexdigest()
DATA=(*range(0x100),*range(0x200,0x800),*range(0x5c00,0x8000))


def start(seed,case):
    m=R.mount(seed,CURRENT)
    N.put(m,SelectedCharacter=case.get('owner',40),TimerControl=case.get('timer',0),ObjectOffset=3,
        Player_State=case.get('state',0),Player_Y_Speed=case.get('vy',0),NmiDisable=255)
    m[0x566+3]=case.get('passenger',3)
    m[0x65b]=case.get('footer',136);m[0xbe+3]=case.get('plane',138)
    entry=case.get('entry','dispatch')
    if entry=='native':
        pc=N.address(m.bundle,'RunLargePlatform')
        m[0x16a]=85;m[0x16c],m[0x16d]=pc&255,pc>>8
        c=N.NesMPU(memory=m,pc=N.address(m.bundle,'FarCallCommon'))
        c.a=((N.location(m.bundle,'RunLargePlatform')-16)//8192)|128
    else:
        m.raw_page(1,128);N.put(m,CurrentBank=128)
        c=N.NesMPU(memory=m,pc=0xb483 if entry=='ryu'else 0xb97e);c.a=85
    c.x,c.y,c.p,c.sp=3,16,case.get('P',0x31),224;c.stPushWord(0x5aff)
    return m,c


def main():
    global CURRENT
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--public',type=Path,required=True)
    ap.add_argument('--input-kind',default='exact-6a3',choices=('exact-6a3','bt91dc-reference-only'))
    args=ap.parse_args();public,input_binding=Input.normalize(args.public.read_bytes(),kind=args.input_kind)
    parent,_=C.Camera.proposal(public);CURRENT,composition=C.proposal(parent)
    assert C.inverse(CURRENT)==parent
    _,dk=Route.cold(CURRENT);dk=Q.C.setup(dk)
    bundle=W.Symbols.bundle();bundle['raw']=CURRENT
    _,ryu=Q.Roster.cold(bundle,dict(name='RYU HAYABUSA',slot=10,cycle=0,raw=10))
    ryu=R.setup(ryu,40,'authored');ryu[3]=184
    inventory=Q.Roster.Starts.C.inventory(parent)['rows'];foreign={}
    for owner in(0,41):
        row=next(r for r in inventory if r['raw']==owner)
        _,foreign[owner]=Q.Roster.cold(bundle,row)
    linked=C.Plan.Funding.H.T.assemble(C.Plan.SOURCE,C.Plan.LAYOUT)
    emitted={(128 if i['segment']in('RYU','NATIVE','POLICY')else 186,i['pc'])for i in linked['instructions']}
    changed={(((i-16)//8192)|128,(i-16)&8191)for i,(a,b)in enumerate(zip(parent,CURRENT))if a!=b}
    cases=[dict(name='DK-native',entry='native'),dict(name='DK-native-paused',entry='native',timer=1),
        dict(name='DK-descend'),dict(name='DK-even-state2',state=2),dict(name='DK-native1',state=1),
        dict(name='DK-vine3',state=3),dict(name='DK-upward',vy=255),dict(name='DK-unowned-passenger',passenger=255),
        dict(name='DK-footer-low',footer=30,plane=32),dict(name='DK-overflow',footer=255,plane=1),
        dict(name='DK-gap1',plane=137),dict(name='DK-I1',P=0x35),dict(name='DK-V1-D1',P=0x79),
        dict(name='foreign-slow',owner=0),dict(name='foreign-fast',owner=41),dict(name='foreign-paused',owner=41,timer=255),
        dict(name='Ryu-authored',entry='ryu',owner=10),dict(name='Ryu-other-ID',entry='ryu',owner=10,kind=37),
        dict(name='Ryu-disjoint',entry='ryu',owner=10,scene='outside'),
        dict(name='Ryu-foreign',entry='ryu',owner=41)]
    reached=set();seen=set();counts=Counter();minimum=255;dead_stack=0;audio=Counter();contexts=[]
    print('DKJR_FOOTER_IRQ_PHASE reached-cuts',flush=True)
    for case in cases:
        owner=case.get('owner',40)
        seed=ryu if owner==10 else foreign[owner]if owner in foreign else dk
        if case.get('scene')=='outside':
            seed=L.clone(seed);seed[0x76+3]=200;seed[0x5d+3]=0
        if 'kind'in case:
            seed=L.clone(seed);seed[0x17+3]=case['kind']
        m,c=start(seed,case);cuts=[];steps=0
        def observe(memory,cpu):
            nonlocal steps
            tag=Helpers.tag(cpu);key=(tag,cpu.pc,cpu.sp,cpu.p&0xcf)
            if(tag,cpu.pc)in emitted:
                reached.add((tag,cpu.pc))
                if key not in seen:seen.add(key);cuts.append((steps,key))
            steps+=1
        Helpers.run(m,c,(0x5b00,224),observe);baseline=(m,c)
        for step,key in cuts:
            cut,cpu=start(seed,case)
            for _ in range(step):N.NesMPU.step(cpu)
            assert(Helpers.tag(cpu),cpu.pc,cpu.sp,cpu.p&0xcf)==key
            for kind in('IRQ','lagNMI'):
                if kind=='IRQ'and cpu.p&4:
                    q,z=L.clone(cut,cpu);before=Helpers.full(q,z);cycle=z.processorCycles;z.irq()
                    assert Helpers.full(q,z)==before and z.processorCycles==cycle;counts['maskedIRQ']+=1;continue
                live=bytes(cut[0x101+cpu.sp:0x200]);before_SMC=bytes(cut[0x15a:0x17b])
                q,z,mate,d,low,pending,trace=V.matched_isr(cut,cpu,parent,kind,changed)
                minimum=min(minimum,low);counts['pending_mapper_commit']+=int(pending)
                assert bytes(q[0x101+z.sp:0x200])==live and bytes(q[0x15a:0x17b])==before_SMC
                altered={at for at in DATA if cut[at]!=q[at]};values={at:q[at]for at in altered}
                assert altered<={at for op,_,at,_ in trace if op=='W'}
                foreground=[];Bus=type(q)
                class Foreground(Bus):
                    def __getitem__(self,at):
                        value=super().__getitem__(at)
                        if isinstance(at,int)and at in self.footer_ISR_altered and self.footer_active:foreground.append(('R',at))
                        return value
                    def __setitem__(self,at,value):
                        if isinstance(at,int)and at in self.footer_ISR_altered and self.footer_active:foreground.append(('W',at))
                        return super().__setitem__(at,value)
                q.__class__=Foreground;q.footer_ISR_altered=altered;q.footer_active=False
                def active(memory,c):memory.footer_active=True
                Helpers.run(q,z,(0x5b00,224),active);q.footer_active=False
                Helpers.run(mate,d,(0x5b00,224))
                assert V.result(q,z)==V.result(mate,d),('matched actual public continuation',case['name'],key,kind)
                assert bytes(q[0x101+z.sp:0x200])==bytes(baseline[0][0x101+baseline[1].sp:0x200])
                assert tuple(q.rawtags)==tuple(baseline[0].rawtags)
                assert tuple(bytes(r)for r in q.ram)==tuple(bytes(r)for r in baseline[0].ram)
                assert bytes(q[0x15a:0x17b])==bytes(baseline[0][0x15a:0x17b])
                assert(z.a,z.x,z.y,z.p&0xef,z.sp,z.pc)==(baseline[1].a,baseline[1].x,baseline[1].y,baseline[1].p&0xef,baseline[1].sp,baseline[1].pc)
                differences={at for at in DATA if q[at]!=baseline[0][at]};accessed={at for _,at in foreground}
                assert differences<=altered and not differences&accessed,('extra ISR data consumed',case['name'],key,kind,differences&accessed)
                for at in differences:
                    assert q[at]==values[at] and baseline[0][at]==cut[at];audio[hex(at)]+=1
                assert bytes(q.vram)==bytes(baseline[0].vram)and tuple(q.chr_latches)==tuple(baseline[0].chr_latches)
                stackdiff={at for at in range(0x17b,0x1df)if q[at]!=baseline[0][at]};dead_stack+=len(stackdiff)
                # The next real Main must overwrite each discarded byte before
                # reading it; live return/SMC state above already compares exactly.
                for model in(q,mate):
                    Base=type(model)
                    class Stack(Base):
                        def __getitem__(self,at):
                            if isinstance(at,int)and at in self.footer_discarded:
                                assert at in self.footer_written,('discarded stack read',case['name'],kind,hex(at))
                            return super().__getitem__(at)
                        def __setitem__(self,at,value):
                            if isinstance(at,int):self.footer_written.add(at)
                            return super().__setitem__(at,value)
                    model.__class__=Stack;model.footer_discarded=stackdiff;model.footer_written=set()
                Q.frame(q,0);Q.frame(mate,0)
                assert R.native_data(q)==R.native_data(mate)and q.contact_frame_registers==mate.contact_frame_registers
                assert bytes(q[0x15a:0x17b])==bytes(mate[0x15a:0x17b])
                counts[kind]+=1
        contexts.append(dict(name=case['name'],new_cuts=len(cuts)))
        print('DKJR_FOOTER_IRQ_PROGRESS '+json.dumps(dict(context=case['name'],cuts=len(seen),vectors=dict(counts)),separators=(',',':')),flush=True)
    assert emitted<=reached,('Unreached emitted footer instructions',sorted(emitted-reached))
    report=dict(passed=True,composition=composition,input_binding=input_binding,emitted_PCs=len(emitted),reached_PCs=len(reached),cuts=len(seen),
        vectors=dict(counts),minimum_ISR_SP=minimum,dead_stack_bytes_read_only_after_writer=dead_stack,
        matched_unchanged_actual_ISR_progress=dict(audio),contexts=contexts,
        full_public_AXYP_SMC33_live_stack_mapper_and_private_state_exact=True,next_actual_Main_checked=True,
        scope='Actual public RunLargePlatform plus declared internal B483/dispatch guard fixtures; not ordinary full-stage/native qualification',output_files=0)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_FOOTER_IRQ '+encoded,flush=True);print('DKJR_FOOTER_IRQ_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
