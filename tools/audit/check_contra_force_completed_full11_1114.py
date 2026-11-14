"""CF full controls and declared real-CPU busy-input-poll differential."""
import argparse
from hashlib import sha256
import json
from unittest.mock import patch

import replay_contra_force_completed_full11_1114 as Factory
import check_contra_force_grounded_full11_1114 as Previous
import check_smb1_alts_full11_1114 as Harness


def metadata(raw,key):
    with patch.object(Previous,'Factory',Factory):return Previous.metadata(raw,key)


def run(raw,key):
    metadata(raw,key)
    with patch.object(Previous,'Factory',Factory):return Previous.run(raw,key)


def busy_case(raw,which):
    """A physical poll at real worker ingress after its entry observer.

    All source CPU state comes from genuine cold UI/Start/normal controls.
    Only another controller-peripheral poll is inserted, not a game-state edit.
    This diagnoses interleaving; it is not physical cadence qualification.
    """
    runtime_class=Harness.LuaRuntime;cpu_class=Factory.N.NesMPU
    frame=Harness.Frames.frame;poll_callbacks=[];injected=0;impacts=0;examples=[];terminal={}
    target=which.bindings(raw,'burns')['cf']['hooks']['CfHostMovement']['pc']
    hit=which.bindings(raw,'burns')['cf']['hooks']['CfSourceImpact']['pc']
    class Runtime:
        def __init__(self,*args,**kwargs):self.rt=runtime_class(*args,**kwargs)
        def __getattr__(self,name):return getattr(self.rt,name)
        def execute(self,text):
            api=self.rt.globals().emu;register=api.addEventCallback
            def add(fn,kind):
                if kind==0:poll_callbacks.append(fn)
                return register(fn,kind)
            api.addEventCallback=add
            return self.rt.execute(text)
    class CPU(cpu_class):
        def step(self):
            nonlocal injected,impacts
            m=self.memory
            if self.pc>=0x8000 and m.rawtags[(self.pc-0x8000)//8192]==3:
                if self.pc==hit:impacts+=1
                if self.pc==target and poll_callbacks:
                    old=m.controller_pad
                    for fn in tuple(poll_callbacks):fn()
                    injected+=1
                    if len(examples)<8 and old!=m.controller_pad:
                        examples.append(dict(poll=injected,pc=self.pc,SP=self.sp,
                            pad_before=old,pad_after=m.controller_pad,
                            x=Factory.N.get(m,'Player_X_Position')+256*Factory.N.get(m,'Player_PageLoc'),
                            y=Factory.N.get(m,'Player_Y_Position'),contact=m.ram[2][0x4d2],input=m.ram[2][0x4aa]))
            return super().step()
    class Earned(Exception):pass
    def observed(m,*args,**kwargs):
        nonlocal terminal
        result=frame(m,*args,**kwargs)
        if kwargs.get('whole_pass'):
            n=Factory.N
            terminal=dict(x=n.get(m,'Player_X_Position')+256*n.get(m,'Player_PageLoc'),
                y=n.get(m,'Player_Y_Position'),engine=n.get(m,'GameEngineSubroutine'),
                lives=n.get(m,'NumberofLives'),source_impacts=impacts)
            if impacts and terminal['engine']==8 and terminal['lives']==2:
                raise Earned
        return result
    result=None;earned=False
    try:
        with patch.object(Harness,'LuaRuntime',Runtime),patch.object(Factory.N,'NesMPU',CPU),\
             patch.object(Harness.Frames,'frame',observed),patch.object(Previous,'Factory',which):
            result=Previous.run(raw,'burns')
    except Earned:earned=True
    return dict(earned=earned,injected_actual_worker_ingress_input_polls=injected,
        real_controller_poll_changes=examples,terminal=terminal,
        failed_receipt_SHA256=result['source_receipt_SHA256']if result else None,
        failed_reason=result['receipt'].get('reason')if result else None,
        source_CPU_and_peripheral_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False)


def differential(raw):
    old=busy_case(raw,Factory.Grounded);new=busy_case(raw,Factory)
    assert not old['earned']and old['terminal']['engine']==11 and old['terminal']['source_impacts']==0,old
    assert new['earned']and new['terminal']['lives']==2 and new['terminal']['engine']==8,new
    return dict(passed=True,ROM_SHA256=Factory.PIN,old_entry_clock=old,new_completed_clock=new,
        conclusion='Only completed worker/Main snapshots may advance decisions; busy polls retain prior buttons.',
        physical_cadence_not_simulated=True,outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=Factory.IDENTITIES,default='burns')
    p.add_argument('--metadata',action='store_true');p.add_argument('--busy-differential',action='store_true');args=p.parse_args()
    raw=Factory.ROM.read_bytes()
    if args.busy_differential:q=differential(raw)
    elif args.metadata:q=metadata(raw,args.identity)
    else:q=run(raw,args.identity)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not args.metadata:assert q['passed'],'CF completed-worker source gate not passed'
