"""Actual Mike/Steve parent-candidate Main/pause pairing; no outcome seeds."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import inspect,json
import current_jay_status_publication_00bb_1116 as J

C=J.C;Parent=J.Previous
COMPOSER_SHA='48fe2b7f1b9dd704f04f6118e333aca89f963cc0012bacd7c761ecf886bc2bca'
FACADE_SHA='c7cf5ec1f238fb0d4b0001fb1c43d1507165052bf695776a37101f8da22f607c'


def cold(raw,variant):
    owner=J if J.H(raw)==J.PIN else Parent
    q=owner.bindings(raw);frozen=Parent.Previous.Frozen
    source=inspect.getsource(frozen.cold)
    name=('MIKE JONES','JAY MCCRAY','STEVE HERMANN')[variant]
    edits=(('    W.UI.key(m,32)\n','    for _ in range('+str(variant)+'):W.UI.key(m,32)\n'),
           ("=='JAY MCCRAY'","=="+repr(name)),('m[0x730b]&96==32','m[0x730b]&96=='+str(variant*32)))
    for a,b in edits:assert source.count(a)==1;source=source.replace(a,b)
    if variant==0:
        for line in("    assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(COOKIE,COOKIE)\n",
                     "    assert bytes(m.ram[3][:0x8c0])==primary(raw)\n"):
            assert source.count(line)==1;source=source.replace(line,'')
    namespace=dict(frozen.__dict__,COOKIE=owner.COOKIE,bindings=lambda image:q if image is raw else (_ for _ in()).throw(AssertionError('Unknown image')),
        primary=lambda image:owner.primary(image))
    exec(compile(source,'<ordinary compiled sibling cold>','exec'),namespace)
    return namespace['cold'](raw)


def run(parent,candidate):
    assert J.H(parent)==C.PIN and J.H(candidate)==J.PIN and C.inverse(candidate)==parent
    assert J.H(Path(C.__file__).read_bytes())==COMPOSER_SHA and J.H(Path(J.__file__).read_bytes())==FACADE_SHA
    rows=[];fault=None
    for variant,name in((0,'Mike'),(2,'Steve')):
        old,new=cold(parent,variant),cold(candidate,variant);assert type(old)is type(new)
        counts=Counter();first=[];ctx={'inside':False};unread={};initial_stack=[];steps=0;phase='cold'
        base=J.N.NesMPU;old_read,old_write=type(old).__getitem__,type(old).__setitem__
        def views():
            result={}
            expected=[(3,0x1800,C.OLD_MAIN,C.NEW_MAIN),(3,0x1ed7,b'\xea'*8,C.LEAF)]
            expected +=[(bank,0x1fe0,C.OLD_COOKIE,C.COOKIE)for bank in(1,2,3)]
            # PacketBoot copies the complete current CHR371 cold row into
            # raw1:D800; its live ExpectedCookie is row offset925.
            expected +=[(1,0x1800+925,C.OLD_COOKIE,C.COOKIE)]
            for bank,at,a,b in expected:
                if bytes(old.ram[bank][at:at+len(a)])==a and bytes(new.ram[bank][at:at+len(b)])==b:
                    result[bank,at]=dict(old=a,new=b)
            return result
        def compare():
            allowed={(bank,at+i)for(bank,at),r in views().items()for i in range(len(r['old']))}
            for bank in range(len(old.ram)):
                for i,(a,b)in enumerate(zip(old.ram[bank],new.ram[bank],strict=True)):
                    assert a==b or(bank,i)in allowed,(name,phase,steps,'unowned workRAM',bank,hex(i),a,b)
            for at in range(0x800):
                a,b=old[at],new[at]
                assert a==b or at in initial_stack,(name,phase,steps,'unowned nativeRAM',hex(at),a,b)
            for key in('vram','chr_latches','rawtags','ppu_reads','oam'):
                if hasattr(old,key):assert getattr(old,key)==getattr(new,key),(name,phase,steps,key)
        for at in range(0x100,0x200):
            if old[at]!=new[at]:initial_stack.append(at)
        # These are only concrete cold return residues after the complete
        # top-level constructor returned. Every future CPU read stays hard
        # until that exact byte has first been overwritten on that side.
        unread={id(bus):set(initial_stack)for bus in(old,new)}
        compare()
        class CPU(base):
            def step(self):
                bus=self.memory;ctx.update(inside=True,bus=bus,PC=self.pc,SP=self.sp)
                tag=bus.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                if tag==3 and self.pc==0xb800:counts['B800_'+('parent'if bus is old else'candidate')]+=1
                try:return super().step()
                finally:ctx['inside']=False
        def read(bus,at):
            if isinstance(at,int)and ctx['inside']and ctx.get('bus')is bus and at in unread.get(id(bus),()):
                raise AssertionError((name,phase,steps,'Cold deadstack read before overwrite',hex(at),ctx['PC'],ctx['SP']))
            return old_read(bus,at)
        def write(bus,at,value):
            if bus is old or bus is new:
                if at in unread[id(bus)]:unread[id(bus)].remove(at);counts['cold_stack_bytes_overwritten']+=1
            return old_write(bus,at,value)
        def frame(pad,label):
            nonlocal steps,phase
            phase=label;steps+=1
            for bus in(old,new):bus.controller_pad=pad;J.Frames.frame(bus,whole_pass=True)
            compare();counts[label]+=1
        def pause_edge(label,expect):
            frame(16,label)
            statuses=[]
            for bus in(old,new):
                if J.N.get(bus,'GamePauseStatus')&1!=expect:
                    assert J.N.get(bus,'SavedJoypad1Bits')&16,'Actual sampled Start before native pause component'
                    J.N.invoke(bus,'PauseRoutine',a=0)
                statuses.append(J.N.get(bus,'GamePauseStatus')&1)
            assert statuses==[expect,expect],(name,label,statuses)
            compare()
        try:
            with patch.object(J.N,'NesMPU',CPU),patch.object(type(old),'__getitem__',read),patch.object(type(old),'__setitem__',write):
                for pad in[0]*4+[1]*8+[129]*8+[0]*4+[64]*2+[0]*38:frame(pad,'supported')
                pause_edge('actual Start/pause',1)
                for _ in range(44):frame(0,'paused rejected')
                pause_edge('actual Start/resume',0)
                for _ in range(8):frame(1,'resumed supported')
            assert counts['B800_parent']==counts['B800_candidate']==0
            assert J.N.get(old,'SelectedCharacter')==J.N.get(new,'SelectedCharacter')==16
            assert old[0x730b]&96==new[0x730b]&96==variant*32
        except Exception as error:
            fault=dict(error=repr(error),identity=name,phase=phase,steps=steps,context={k:v for k,v in ctx.items()if k!='bus'})
        rows.append(dict(name=name,variant=variant*32,steps=steps,counts=dict(counts),cold_stack_residue_addresses=initial_stack,
            unconsumed_cold_stack_residues={side:sorted(unread[id(bus)])for side,bus in(('parent',old),('candidate',new))},
            declared_loaded_views=[dict(bank=bank,offset=at,bytes=len(row['old']),old_SHA256=J.H(row['old']),new_SHA256=J.H(row['new']))for(bank,at),row in views().items()],
            terminal={field:J.N.get(new,field)for field in('JnHealth','JnMaxHearts','JnOwnedTier','JnStars','PlayerStatus','NumberofLives','GamePauseStatus')}))
        if fault:break
    out=dict(passed=fault is None,fault=fault,parent_SHA256=C.PIN,candidate_SHA256=J.PIN,rows=rows,
        no_gameplay_actor_health_position_seeds=True,original_and_granted_CPU_only=True,native=False,outputs=0,
        composer_SHA256=COMPOSER_SHA,candidate_facade_SHA256=FACADE_SHA,source_SHA256=J.H(Path(__file__).read_bytes()))
    out['receipt_SHA256']=J.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    parent=Parent.load_current_image();candidate=C.proposal(parent)[0]
    def deny(*a,**kw):raise AssertionError('Jay sibling regression attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(parent,candidate)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
