"""Executable isolated C2 projection/oracle environment, no host mapping model."""
from pathlib import Path
import collections,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from py65.devices.mpu6502 import MPU
import wwf_action_source_controls_v2 as T
L=R/'build/wwf-c2-symbol-relocation-v3'
P=json.loads((L/'build-proof.json').read_text())
OldBus,old_call=T.LabBus,T.call
PTRS=[0x1f,0x21,0x23,0x25,0xc3]
SCOPED=P['scoped_R0_R7']
INDEX_WITNESS=collections.defaultdict(set)
HOST_CLOBBERS=set()
MIN_SP=255

class OracleBus(OldBus):
    def __init__(self,*args,**kwargs):
        self.state_events=[]
        super().__init__(*args,**kwargs)
    def __setitem__(self,a,v):
        super().__setitem__(a,v)
        data=a<0x2000 and (not 0x100<=a<0x200 or self.site==0xe9bb)
        self.state_events.append((a&2047,v&255)if data else None)

class StateProjection:
    def __init__(self,b):self.b=b
    def __len__(self):return 2048
    def __iter__(self):return iter(self.b.shadow)
    def __getitem__(self,i):return self.b.shadow[i]
    def __setitem__(self,i,v):
        if isinstance(i,slice):
            addresses=range(*i.indices(2048));assert len(addresses)==len(v)
            for a,x in zip(addresses,v):self[a]=x
            return
        self.b.shadow[i]=v&255
        pair=next((p for p in PTRS if i in[p,p+1]),None)
        if pair is None:self.b.mem[0xc000+i]=v&255
        else:
            word=self.b.shadow[pair]+256*self.b.shadow[pair+1];new=self.b.project(word)
            self.b.mem[0xc000+pair:0xc002+pair]=new.to_bytes(2,'little')

class C2Bus:
    def __init__(self,prg,ram,proof,variant):
        self.prg,self.bank=prg,0;self.proof,self.variant=proof,'relocated'
        self.labels=P['labels'];self.reverse={v:int(k[4:],16)for k,v in self.labels.items()if k.startswith('WfN_')}
        self.mem=bytearray(65536);self.mem[0x8000:]=prg[:32768]
        self.mem[0xa000:0xc000]=(L/'vm.bin').read_bytes();self.mem[0xc000:0xe000]=(L/'c2.bin').read_bytes()
        self.mem[0x7000:0x7200]=(L/'environment.bin').read_bytes();self.mem[0x7800:0x7900]=(L/'irq.bin').read_bytes()
        self.mem[:2048]=ram;self.shadow=bytearray(ram)
        self.ram=StateProjection(self)
        self.map={}
        for i in range(2048):self.map[i]=0xc000+i
        for n,a in self.labels.items():
            if n.startswith('WfN_'):self.map[int(n[4:],16)]=a
            if n.startswith('WfScript_'):self.map[int(n[9:],16)]=a
        for i,old in P['original_descriptors'].items():
            for offset in range(81):self.map[int(old)+offset]=self.labels['WfDescriptor'+i]+offset
        for offset in range(12):self.map[0xbb28+offset]=self.labels['WfDescriptorPointers']+offset
        for offset in range(180):self.map[0xe6ea+offset]=self.labels['WfOpcodeTable']+offset
        self.inverse={v:k for k,v in self.map.items()}
        assert len(self.inverse)==len(self.map)
        self.mem[0xc000:0xc800]=ram
        for ptr in PTRS:self.ram[ptr]=ram[ptr]
        for i,a in enumerate(SCOPED):self.mem[a]=0x91+i*7
        self.host_seed=bytes(self.mem[:2048])
        self.io,self.apu,self.writes,self.callbacks={ },[],[],[]
        self.canonical_writes,self.state_events,self.pointer_pending=[],[],{}
        self.executed=set();self.pc_by_context=collections.defaultdict(set)
        self.reads_by_context,self.writes_by_context=collections.defaultdict(set),collections.defaultdict(set)
        self.min_sp=255;self.handler_hits=collections.Counter();self.native_only=0;self.site=None;self.cpu=None
        self.oracles={self.labels['WfOracle_'+name]:name for name in P['callback_original'].values()}
        self.original={name:int(a)for a,name in P['callback_original'].items()}
        self.handler_starts={self.labels[f'WfOpcode{op:02X}']:op for op in range(8,0x62)}
        self.zpx_witness=collections.defaultdict(set);self.helper_reads=collections.Counter();self.hook=None
    def project(self,a):return self.map.get(a,a)
    def unproject(self,a):return self.inverse.get(a,a)
    def __getitem__(self,a):
        if isinstance(a,slice):return list(self.mem[a])
        if 0xc000<=a<0xc800:self.reads_by_context['component'].add(a-0xc000)
        return self.mem[a]
    def __setitem__(self,a,v):
        v&=255;self.mem[a]=v;self.writes.append((a,v));self.canonical_writes.append((a,v));event=None
        if 0xc000<=a<0xc800:
            at=a-0xc000;self.writes_by_context['component'].add(at);pair=next((p for p in PTRS if at in[p,p+1]),None)
            if pair is None:self.shadow[at]=v;event=(at,v)
            else:
                event=(at,v);self.pointer_pending.setdefault(pair,[]).append((len(self.state_events),at))
                if at==pair+1:
                    word=self.mem[0xc000+pair]+256*self.mem[0xc001+pair];old=self.unproject(word)
                    # Only declared pointer fields translate; all other state is raw exact.
                    self.shadow[pair:pair+2]=old.to_bytes(2,'little')
                    for index,pos in self.pointer_pending.pop(pair):
                        value=(old>>(8*(pos-pair)))&255
                        if index==len(self.state_events):event=(pos,value)
                        else:self.state_events[index]=(pos,value)
        self.state_events.append(event)
        if a in SCOPED and self.cpu and 0x7000<=self.cpu.pc<0x7200:HOST_CLOBBERS.add(a)
    def canonical_ram(self):return bytearray(self.shadow)
    def mark(self,c):
        self.cpu=c;self.site=self.reverse.get(c.pc);self.min_sp=min(self.min_sp,c.sp)
        if self.site is not None:
            self.executed.add((0,self.site));self.pc_by_context['component'].add((0,self.site))
            instruction=P['instructions'][str(self.site)]
            if instruction['mode']in['zpx','zpy']:
                index=c.x if instruction['mode']=='zpx'else c.y
                base=instruction['value'];assert base+index<256,('Unproved original ZP wrap',hex(self.site),base,index)
                self.zpx_witness[self.site].add(index);INDEX_WITNESS[self.site].add(index)
        if c.pc in self.handler_starts:self.handler_hits[self.handler_starts[c.pc]]+=1
        for ptr in PTRS:
            if c.pc==self.labels[f'WfReadPair{ptr:02X}']:self.helper_reads[ptr]+=1
    def source_write(self,a,v):
        """Native environment data write: selected storage with original state value."""
        a&=2047;v&=255;self.ram[a]=v
        self.writes.append((0xc000+a,self.mem[0xc000+a]));self.canonical_writes.append((a,v));self.state_events.append((a,v));self.writes_by_context['callback'].add(a)

class NativeView:
    def __init__(self,b):self.b=b
    def __getitem__(self,a):
        if isinstance(a,slice):return [self[i]for i in range(a.start,a.stop,a.step or 1)]
        b=self.b
        if a>=0x8000:return b.prg[b.bank*32768+a-0x8000]
        if 0x100<=a<0x200:return b.mem[a]
        if a<0x2000:b.reads_by_context['callback'].add(a&2047);return b.shadow[a&2047]
        if a==0x4015:return 0
        if a in b.io:return b.io[a]
        raise AssertionError(('Unmodeled native callback read',hex(a)))
    def __setitem__(self,a,v):
        b=self.b;v&=255
        if a>=0x8000:b.bank=v&3;b.writes.append((a,v));b.canonical_writes.append((a,v));b.state_events.append(None)
        elif 0x100<=a<0x200:b.mem[a]=v;b.writes.append((a,v));b.canonical_writes.append((a,v));b.state_events.append(None)
        elif a<0x2000:b.source_write(a,v)
        elif 0x4000<=a<=0x4017:b.io[a]=v;b.apu.append((a,v));b.writes.append((a,v));b.canonical_writes.append((a,v));b.state_events.append(None)
        else:raise AssertionError(('Unmodeled native callback write',hex(a),v))

def native_callback(b,c,name):
    offset=P['source_callback_oracle_stack_extra'];before=T.cpu_state(c);before[-1]+=offset
    target=(b.mem[0x100+((c.sp+1)&255)]+256*b.mem[0x100+((c.sp+2)&255)]+1)&65535;sp=(c.sp+2)&255
    view=NativeView(b);n=MPU(memory=view,pc=b.original[name]);n.a,n.x,n.y,n.p,n.sp=c.a,c.x,c.y,c.p,c.sp
    start,apu,bank=len(b.state_events),len(b.apu),b.bank;nested=[];b.native_only=1
    try:
        names={v:k for k,v in b.original.items()}
        for i in range(50000):
            if n.pc==target and n.sp==sp:break
            b.min_sp=min(b.min_sp,n.sp);b.executed.add((b.bank,n.pc));b.pc_by_context['callback'].add((b.bank,n.pc))
            if i and n.pc in names:
                state=T.cpu_state(n);state[-1]+=offset;nested.append(dict(name=names[n.pc],input=state))
            assert view[n.pc]!=0,('Callback BRK',name,hex(n.pc));n.step()
        else:raise AssertionError(('Callback bound',name,hex(n.pc)))
    finally:b.native_only=0
    c.a,c.x,c.y,c.p,c.sp,c.pc=n.a,n.x,n.y,n.p,n.sp,n.pc;c.processorCycles+=n.processorCycles
    output=T.cpu_state(c);output[-1]+=offset
    b.callbacks.append(dict(name=name,input=before,output=output,CPU_cycles=n.processorCycles,bank_before=bank,bank_after=b.bank,app_writes=[e for e in b.canonical_writes[start:]if not 0x100<=e[0]<0x200],audio=b.apu[apu:],nested=nested))

def factory(prg,ram,proof,variant):return C2Bus(prg,ram,proof,variant)if variant=='relocated'else OracleBus(prg,ram,proof,variant)

def call(b,name,*,a=0,x=0,y=0,flags=0x30):
    if not isinstance(b,C2Bus):return old_call(b,name,a=a,x=x,y=y,flags=flags)
    c=MPU(memory=b,pc=b.labels[name]);c.a,c.x,c.y,c.p,c.sp=a,x,y,flags,253
    scratch=bytes(b.mem[k]for k in SCOPED);host=bytes(b.mem[:2048]);b.site=None;b.cpu=c;c.stPushWord(0x7eff)
    for _ in range(100000):
        if c.pc==0x7f00:
            assert bytes(b.mem[k]for k in SCOPED)==scratch,('Scoped R0..7',name)
            assert bytes(b.mem[:0x100])==host[:0x100],('Host ZP escaped',name)
            assert bytes(b.mem[0x200:0x800])==host[0x200:],('Host RAM escaped',name)
            assert not b.pointer_pending,('Incomplete typed pointer store',name,b.pointer_pending)
            return c
        if b.hook:b.hook(b,c)
        if c.pc in b.oracles:native_callback(b,c,b.oracles[c.pc]);continue
        b.mark(c);assert b[c.pc]!=0,('Relocated BRK',name,hex(c.pc));c.step()
    raise AssertionError(('Relocated bound',name,hex(c.pc)))

def compare(buses,cpus,starts,location):
    a,n,b=buses;ca,cn,cb=cpus
    assert T.cpu_state(cn)==T.cpu_state(ca)and n.ram==a.ram and cn.processorCycles==ca.processorCycles,('Native baseline',location)
    assert n.canonical_writes[starts[1][0]:]==a.canonical_writes[starts[0][0]:]
    assert T.cpu_state(cb)==T.cpu_state(ca),('C2 AXYP/SP',location,T.cpu_state(ca),T.cpu_state(cb))
    actual=b.canonical_ram();diff=[(i,a.ram[i],actual[i])for i in range(2048)if not 0x100<=i<0x200 and a.ram[i]!=actual[i]]
    assert not diff,('C2 projected state',location,diff[:12])
    expected=[e for e in a.state_events[starts[0][0]:]if e is not None];current=[e for e in b.state_events[starts[2][0]:]if e is not None]
    assert expected==current,('C2 ordered state writes',location,expected,current)
    assert a.callbacks[starts[0][1]:]==b.callbacks[starts[2][1]:],('C2 callback ABI',location,a.callbacks[starts[0][1]:],b.callbacks[starts[2][1]:])
    assert a.apu==b.apu and a.io==b.io and a.bank==b.bank,('C2 audio/map callback',location)
    return cb.processorCycles-ca.processorCycles

def install():T.LabBus=factory;T.call=call;T.compare=compare
