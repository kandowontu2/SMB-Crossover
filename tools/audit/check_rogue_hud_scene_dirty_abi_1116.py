"""Independent leased79fd lifecycle/foreign/IRQ components; RAM only.

Declared ABI fixtures are distinct from the other worker's natural controls.
The paired old CPU is explicitly exactcb95 reference, never candidate evidence.
"""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,json
import current_rogue_hud_scene_dirty79fd_1116 as J

C,N,W,Frames,H=J.C,J.N,J.W,J.Frames,J.H
C_SHA='d7b924cbba68c99a2c3db6ec23e2b41e47b8ceb9e74476af3bcccc2bda52aa45'
J_SHA='bcd2f6aea2e6598eeff2ef7aee4a34f195c049e653fcb9b584596af1f9d07868'
WRAPPERS=('RdBodyNewSession','RdBodyNewLife','RdBodyEnterScene')

def auth(raw):
    assert H(Path(C.__file__).read_bytes())==C_SHA and H(Path(J.__file__).read_bytes())==J_SHA
    C.lease();assert H(raw)==C.CANDIDATE
    parent=C.inverse(raw);assert C.proposal(parent)[0]==raw
    b=W.Symbols.bundle()
    spans={(int(s['start'],0),int(s['size'],0))for s in b['segs'].values()if s.get('name','').strip('"')in('SHORTRAM','SMCCODE')}
    assert spans=={(0x100,0x5a),(0x15a,0x21)},spans
    assert W.address(b,'NmiDisable')==0x139 and W.address(b,'NmiSkipped')==0x13a
    return parent

def backing(m,raw):
    m.bundle=dict(m.bundle,raw=raw)
    for slot,tag in enumerate(list(m.rawtags)):
        if tag&128:m.raw_page(slot,tag)
    return m

def snapshot(m):
    # All native meaningful RAM/SMC plus private RAM. Dead hardware stack below
    # returnedSP is not a live ABI; its changed internal return PCs are expected.
    native=list(range(0x17b))+list(range(0x200,0x800))+list(range(0x5c00,0x8000))
    return {**{('cpu',at):m[at]for at in native},**{(bank,i):v for bank,page in enumerate(m.ram)for i,v in enumerate(page)}}

def regs(c):return(c.pc,c.sp,c.a,c.x,c.y,c.p|48)

def same(a,b,*,dirty=False):
    assert a.rawtags==b.rawtags and a.chr_latches==b.chr_latches
    left,right=snapshot(a),snapshot(b);key=('cpu',W.address(a.bundle,'InvDirty'))
    changes={k:(left[k],v)for k,v in right.items()if left[k]!=v}
    if dirty:assert changes=={key:(left[key],1)},changes
    else:assert not changes,changes
    assert bytes(a[0x1e1:0x200])==bytes(b[0x1e1:0x200])

def cold(raw):
    base=N.NesMPU;hits=[];pcs=set()
    class CPU(base):
        def step(self):
            m=self.memory
            if self.pc>=0x8000 and m.rawtags[(self.pc-0x8000)//8192]==223 and 0xb78f<=self.pc<0xb79d:
                assert m.bundle['raw']is raw and bytes(m[0xb78f:0xb79d])==C.NEW
                pcs.add(self.pc)
                if self.pc==0xb78f:hits.append(dict(PC=self.pc,SP=self.sp,P=self.p,owner=N.get(m,'SelectedCharacter'),variant=N.get(m,'RdVariant')))
            return super().step()
    with patch.object(N,'NesMPU',CPU):m=J.cold(raw)
    assert hits and all(r['P']&1 and(r['owner'],r['variant'])==(2,1)for r in hits)
    assert {0xb78f,0xb791,0xb794,0xb796,0xb799,0xb79c}<=pcs
    return m,dict(actual_owning_SHA256=H(raw),first_newtail=hits[0],newtail_entries=len(hits),reached_PCs=sorted(pcs),source_UI_vblank_limit=True)

def components(raw,seed):
    parent=auth(raw);rows=[];counts=Counter();dirty=W.address(seed.bundle,'InvDirty')
    for owner,variant in((2,1),(2,0),(2,2),(0,0),(41,0),(43,0)):
        owning=(owner,variant)==(2,1)
        for name in WRAPPERS:
            for flags in(0x30,0xf1):
                a,b=(backing(N.fork(seed),image)for image in(parent,raw))
                for m in(a,b):
                    N.put(m,SelectedCharacter=owner,RdVariant=variant,InvDirty=0,RdColorRequest=0,
                        RdGear=1,RdMaxMissiles=5,RdMissiles=3,RdTanks=1,RdHealthLo=0x50,RdHealthHi=0x19)
                    W.clear_logs(m)
                ra,rb=(N.invoke(m,name,a=85,x=7,y=91,p=flags)for m in(a,b))
                assert {k:v for k,v in ra.items()if k!='CPU'}=={k:v for k,v in rb.items()if k!='CPU'},(owner,variant,name,ra,rb)
                same(a,b,dirty=owning)
                writes=[v for at,v in b.writes if at==dirty]
                assert writes==([1]if owning else[]),(name,owner,variant,writes)
                assert N.get(b,'RdColorRequest')==(1 if owning else 0)
                assert bool(rb['P']&1)==owning
                rows.append(dict(owner=owner,variant=variant,wrapper=name,incoming_P=flags,old=ra,new=rb,CPU_delta=rb['CPU']-ra['CPU'],InvDirty_writes=writes))
                counts['owning'if owning else'foreign']+=1
    # Explicit warm, identity fault, retry, retirement and re-admission calls.
    m=N.fork(seed);transitions=[]
    for label,owner,variant in(('warm',2,1),('identity-fault',2,0),('retry',2,1),('retired-owner',41,0),('re-admit',2,1)):
        N.put(m,SelectedCharacter=owner,RdVariant=variant,InvDirty=0,RdColorRequest=0)
        result=N.invoke(m,'RdBodyEnterScene',p=0xf1)
        expected=(owner,variant)==(2,1)
        assert bool(result['P']&1)==expected and N.get(m,'InvDirty')==int(expected)
        transitions.append(dict(label=label,owner=owner,variant=variant,result=result,InvDirty=N.get(m,'InvDirty')))
    return dict(counts=dict(counts),cases=rows,lifecycle_components=transitions,
        only_direct_tail_delta='Actual InvDirty=1 on owning chains; all other meaningful RAM/maps/SMC/live stack and old AXYP behavior exact',
        component_resources_and_identity_explicitly_seeded=True,natural_acquisition_claim=False)

def menu(raw):
    parent=auth(raw);b=J.bindings(raw)['bundle'];models=[]
    for image in(parent,raw):
        with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(dict(b,raw=image),0)
        models.append(m)
    steps=[]
    for bits in(1,1,32,32,32):
        out=[W.UI.key(m,bits)for m in models]
        assert out[0]==out[1];same(*models)
        names=[W.UI.menu_name(m)[0]for m in models];assert names[0]==names[1]
        steps.append(dict(input=bits,name=names[1],owner=N.get(models[1],'SelectedCharacter'),variant=N.get(models[1],'RdVariant')))
    assert [(q['owner'],q['variant'])for q in steps[-3:]]==[(2,1),(2,0),(2,1)],steps
    assert steps[-3]['name']==steps[-1]['name']=='ROGUE DAWN',steps
    return dict(compiled_selector_retire_readmission=steps,actual_full_menu_paths=True,no_midlevel_swap_claim=True)

def interrupt_components(raw,seed):
    parent=auth(raw);base=N.NesMPU;counts=Counter();cuts=[];minimum=255
    tail={0xb78f,0xb791,0xb794,0xb796,0xb799,0xb79c}
    begin=W.address(seed.bundle,'RdTxMovementBegin');wanted=tail|{begin,begin+1,begin+2}
    def clone(model,c,image=raw):
        m=backing(N.fork(model),image);d=base(memory=m,pc=c.pc)
        d.a,d.x,d.y,d.p,d.sp=c.a,c.x,c.y,c.p,c.sp
        return m,d
    def inject(c,kind):
        before=regs(c);m=c.memory;low=c.sp;hits=0
        if kind=='IRQ'and c.p&4:
            old_cycles=c.processorCycles;c.irq();assert regs(c)==before and c.processorCycles==old_cycles
            return low,False
        c.irq()if kind=='IRQ'else c.nmi()
        for _ in range(100000):
            low=min(low,c.sp)
            if regs(c)[:2]==before[:2]:break
            assert m[c.pc],('ISR BRK',kind,hex(c.pc));hits+=1;base.step(c)
        else:raise AssertionError(('ISR return bound',kind,hex(c.pc)))
        assert hits and regs(c)==before,('ISR AXYP/PC/SP',kind,before,regs(c))
        return low,True
    def finish(m,c):
        for _ in range(500000):
            if(c.pc,c.sp)==(0x5b00,224):return
            assert m[c.pc],('Public continuation BRK',hex(c.pc));base.step(c)
        raise AssertionError('Interrupted actual public return bound')
    for name in WRAPPERS:
        m=N.fork(seed);seen=set()
        N.put(m,InvDirty=0,RdColorRequest=0,NmiDisable=255)
        # Real scheduler begin marks the foreground busy before the component.
        N.invoke(m,'PauseRoutine',a=255)
        class CPU(base):
            def step(self):
                nonlocal minimum
                if self.memory is m and self.pc in wanted and m.rawtags[(self.pc-0x8000)//8192]==223 and self.pc not in seen:
                    seen.add(self.pc)
                    for kind in('IRQ','lagNMI'):
                        plain,cp=clone(m,self);changed,ci=clone(m,self);baseline,cr=clone(m,self,parent)
                        before=snapshot(plain);prior=regs(ci)
                        low,delivered=inject(ci,kind);low2,delivered2=inject(cr,kind)
                        assert delivered==delivered2 and regs(ci)==regs(cr)==prior
                        same(changed,baseline)
                        assert bytes(changed[0x101+ci.sp:0x200])==bytes(baseline[0x101+cr.sp:0x200])
                        after=snapshot(changed);isr_delta={k:(v,after[k])for k,v in before.items()if v!=after[k]}
                        finish(plain,cp);finish(changed,ci);assert regs(cp)==regs(ci)
                        left,right=snapshot(plain),snapshot(changed)
                        for k,v in left.items():
                            if k in isr_delta:
                                assert v==before[k],('Foreground also owns actual ISR-mutated cell',kind,k,before[k],v,isr_delta[k])
                                want=after[k]
                            else:want=v
                            assert right[k]==want,('New foreground/ISR delta',kind,k,right[k],want)
                        assert plain.rawtags==changed.rawtags and plain.chr_latches==changed.chr_latches
                        assert bytes(plain[0x1e1:0x200])==bytes(changed[0x1e1:0x200])
                        minimum=min(minimum,low,low2);counts[kind if delivered else'maskedIRQ']+=1
                        cuts.append(dict(wrapper=name,PC=self.pc,SP=self.sp,P=self.p,kind=kind,delivered=delivered,minimum_SP=min(low,low2),paired_unchanged_ISR_delta=[dict(domain=k[0],offset=k[1],before=v[0],after=v[1])for k,v in isr_delta.items()]))
                return super().step()
        with patch.object(N,'NesMPU',CPU):N.invoke(m,name,p=0x31)
        assert wanted<=seen,(name,wanted-seen)
    assert counts['IRQ'] and counts['lagNMI']
    return dict(counts=dict(counts),minimum_SP=minimum,cuts=cuts,
        same_actual_cb95_ISR_effects_not_blanket_audio_mask=True,all_completed_public_continuations_checked=True,
        declared_lifecycle_component_not_natural_transition=True)

def run(raw,scope):
    auth(raw);seed,opening=cold(raw)
    q=dict(passed=True,actual_owning_SHA256=H(raw),reference_cpu_SHA256=C.PARENT,
        C_SHA256=C_SHA,J_SHA256=J_SHA,grant_SHA256=C.GRANT_SHA,cold=opening,scope=scope,
        checker_SHA256=H(Path(__file__).read_bytes()),live_SHORTRAM=[0x100,0x15a],live_SMCCODE=[0x15a,0x17b],
        proposed_CPU=True,native=False,outputs=0,natural_gameplay_claim=False)
    if scope in('components','all'):q['components']=components(raw,seed);q['menu']=menu(raw)
    if scope in('irq','all'):q['interrupts']=interrupt_components(raw,seed)
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--scope',choices=('components','irq','all'),default='all');a=p.parse_args()
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Rogue lifecycle source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.scope)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
