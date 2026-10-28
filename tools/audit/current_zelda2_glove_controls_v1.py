"""Actual Z2 Easy Glove counterexample, fixed complete callers and finite IRQ/NMI seams."""
from pathlib import Path
import hashlib,json
import current_zelda2_earned_cpu_v1 as earned
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU

R=Path(__file__).resolve().parents[2];B=R/'build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:dict(path=str(Path(p).resolve()),bytes=Path(p).stat().st_size,sha256=sha(p))
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n',newline='\n')
BASE=B/'roster-20261028-fixes.nes';NEW=B/'zelda2_easy_glove.nes'

def main():
    old,new=scoped_load(BASE),scoped_load(NEW);out=B/'zelda2_easy_glove_controls.json';assert not out.exists()
    probes=[];dma=[];interrupts=[];active={'ROM':'baseline'}
    class Observed(Arena):
        def invoke(self,name,*args,**kwargs):
            saved=NesMPU.step
            def watch(c):
                bank=self.m.banks[(c.pc-32768)//8192]if c.pc>=32768 else-1
                for n in ['EasyWhipProbe','EasyWhipProbe::Done']:
                    if c.pc==address(self.b,n)and bank==22:
                        probes.append(dict(ROM=active['ROM'],owner=n,pc=c.pc,bank=bank,sp=c.sp,type=self.get('MmBulletType'),point=[self.get(t)for t in ['MmProbeX','MmProbePage','MmProbeY']],edges=[self.get(t)for t in ['MmBillEdgeX','MmBillEdgeX+1']]if'MmBillEdgeX+1'in self.b['syms']else[self.get('MmBillEdgeX'),self.get('MmBillEdgeX',1)],variant=self.get('Z2Variant'),mode=self.get('CrossoverBehaviorVersion')))
                before=len(self.m.writes);pc=c.pc;saved(c)
                if any(at==0x4014 for at,_ in self.m.writes[before:]):
                    dma.append(dict(ROM=active['ROM'],call=name,pc=pc,next_pc=c.pc,bank=bank,sp=c.sp,pending=self.get('Z2PanelPending'),panel=self.get('Z2PanelActive'),blank=self.get('DisableScreenFlag'),mirror_mask=self.get('Mirror_PPUMASK'),NmiDisable=self.get('NmiDisable')))
            NesMPU.step=watch
            try:return super().invoke(name,*args,**kwargs)
            finally:NesMPU.step=saved
    previous=earned.Arena;earned.Arena=Observed
    try:
        try:earned.campaign(old,0)
        except AssertionError as e:
            assert e.args[0][0]=='Glove brick',e
            negative=dict(passed=False,native_run=False,ROM_sha256=sha(BASE),first_FALSE=str(e.args[0]),native_not_attempted=True)
        else:raise AssertionError('Baseline must reproduce its real Glove failure')
        active['ROM']='fixed';earned.EXPECTED=sha(NEW)
        fixed=[]
        for mode in [0,1]:
            z=earned.campaign(new,mode);z.update(tool_sha256=sha(R/'tools/audit/current_zelda2_earned_cpu_v1.py'),qualification_tool_sha256=sha(Path(__file__)))
            p=B/f'zelda2_easy_glove_source_{mode}.json';assert not p.exists();put(p,z);fixed.append(p)
    finally:earned.Arena=previous
    # Complete real legacy helper returns; all application bytes and the real
    # caller's return address/lower stack remain exact on unchanged families.
    direct=[]
    for char in range(20):
        for mode in [0,1]:
            for variant in [0,1]:
                for typ in range(256)if char in [4,5]else[0,14,16,19,21,23,25,255]:
                    results=[]
                    for b in [old,new]:
                        q=Arena(b,char);q.put(CrossoverBehaviorVersion=mode,Z2Variant=variant,MmBulletType=typ)
                        for i in range(256):q.m[256+i]=(17*i+91)&255
                        c,_=q.invoke('EasyWhipEligible',a=87,x=7,y=9)
                        results.append((c,q))
                    (a,x),(c,y)=results;intended=char==4 and mode==0 and variant==1
                    if intended:assert not c.p&1
                    else:
                        assert(a.a,a.x,a.y,a.p&0xcf,a.sp)==(c.a,c.x,c.y,c.p&0xcf,c.sp),(char,mode,variant,typ)
                    assert list(x.m[:0x1fa])==list(y.m[:0x1fa])and list(x.m[0x1fc:0x8000])==list(y.m[0x1fc:0x8000]),('Only two exact dead JSR stack bytes',char,mode,variant,typ)
                    direct.append(dict(character=char,mode=mode,variant=variant,type=typ,intended_Z2_reject=intended,cycles_old=a.processorCycles,cycles_new=c.processorCycles))
    # Interrupt the actual 12-byte helper before every instruction. These
    # execute real RTI continuations; no PPU/frame timing claim is made.
    for variant in [0,1]:
        for which in ['NMI','IRQ']:
            start=address(new,'Z2LegacyEasyProbeType');pcs=[];q=Arena(new,4);q.put(CrossoverBehaviorVersion=0,Z2Variant=variant,MmBulletType=14,NmiDisable=255,Sprite0HitDetectFlag=1)
            saved=NesMPU.step
            def collect(c):
                if start<=c.pc<start+12 and q.m.banks[(c.pc-32768)//8192]==22:pcs.append(c.pc)
                saved(c)
            NesMPU.step=collect
            try:q.invoke('EasyWhipEligible')
            finally:NesMPU.step=saved
            for pc in pcs:
                q=Arena(new,4);q.put(CrossoverBehaviorVersion=0,Z2Variant=variant,MmBulletType=14,NmiDisable=255,Sprite0HitDetectFlag=1)
                fired=False;saved=NesMPU.step
                def step(c):
                    nonlocal fired
                    if not fired and c.pc==pc and q.m.banks[(c.pc-32768)//8192]==22:
                        fired=True;before=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'))
                        if which=='NMI':c.nmi()
                        else:
                            c.stPushWord(c.pc);c.stPush(c.p&~c.BREAK|c.UNUSED);c.p|=c.INTERRUPT;c.pc=address(new,'IrqScrollSplit')
                        for _ in range(20000):
                            saved(c)
                            if c.pc==before[5]and c.sp==before[4]:break
                        else:raise AssertionError('Real interrupt must RTI')
                        after=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'))
                        assert before==after,(which,variant,pc,before,after)
                    saved(c)
                NesMPU.step=step
                try:q.invoke('EasyWhipEligible')
                finally:NesMPU.step=saved
                assert fired;interrupts.append(dict(kind=which,variant=variant,interrupted_PC=pc,actual_return_preserved=True))
    assert dma and all(z['panel']==1 and z['pending']in[1,2]and z['blank']==1 and z['mirror_mask']&24==0 and z['NmiDisable']==255 for z in dma)
    wrong=[p for p in probes if p['ROM']=='baseline'and p['owner']=='EasyWhipProbe'and p['variant']==1 and p['mode']==0]
    assert wrong
    put(out,dict(passed=True,native_run=False,Lua_VM_executed=False,parent_sha256=sha(BASE),candidate_sha256=sha(NEW),baseline_counterexample=negative,fixed_source_campaigns=[bind(p)for p in fixed],baseline_actual_probe_chronology=probes,actual_foreground_panel_DMA_requests=dma,direct_full_returns=direct,interrupt_seams=interrupts,dead_stack_exact_addresses=[0x1fa,0x1fb],cost_delta_cycles=sorted(set(x['cycles_new']-x['cycles_old']for x in direct)),limitations='CPU model: actual assembled callers/RTI and typed scene; no native acquisition, real PPU/panel pixels or timing claim. Fixed source campaigns genuinely execute both Easy0 and Hard1; original ee Easy remains failed.',bindings=[bind(p)for p in [Path(__file__),R/'tools/audit/current_zelda2_earned_cpu_v1.py',BASE,BASE.with_suffix('.dbg'),NEW,NEW.with_suffix('.dbg'),B/'zelda2_easy_glove_build.json']]))
    print(json.dumps(dict(passed=True,proof=str(out),sha256=sha(out),direct_cases=len(direct),interrupts=len(interrupts),source_GameLoops=[json.loads(p.read_text())['GameLoop_calls']for p in fixed])))

if __name__=='__main__':main()
