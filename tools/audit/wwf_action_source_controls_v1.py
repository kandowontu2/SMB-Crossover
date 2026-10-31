"""Original-oracle comparison for the isolated, assembled WWF action VM.

The environment callbacks execute the original donor instructions dynamically.
They are not canned return values and are not SMB host implementations.
"""
from pathlib import Path
import collections
import hashlib
import json
import sys
import traceback

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
from py65.devices.mpu6502 import MPU
import wwf_action_vm_recovery_1031_v1 as W

O = R/'build/wwf-action-source-controls-v1'
L = R/'build/wwf-action-source-lab-v2'
INPUTS = [('A',128,128), ('B',64,64), ('Up',8,0), ('Down',4,0),
          ('A+B',192,192), ('Up+A',136,128), ('Down+A',132,128),
          ('Up+B',72,64), ('Down+B',68,64), ('Up+A+B',200,192),
          ('Down+A+B',196,192)]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
save = lambda p,q: Path(p).write_text(json.dumps(q,indent=2)+'\n')


def cpu_state(c):
    return [c.a,c.x,c.y,c.p,c.sp]


class LabBus(W.Bus):
    def __init__(self, prg, ram, proof, variant):
        super().__init__(prg,ram)
        self.variant, self.proof = variant, proof
        self.info = proof['variants'][variant] if variant else None
        self.image = Path(self.info['binary']).read_bytes() if self.info else None
        self.overlays = [(q['start'],q['start']+q['size']) for q in self.info['spans']] if self.info else []
        self.labels = self.info['labels'] if self.info else proof['variants']['native']['labels']
        self.reverse = {v:int(k[4:],16) for k,v in self.labels.items() if k.startswith('WfN_')}
        self.callback_original = proof['callback_original_entries']
        self.callback_pcs = {v:k for k,v in (self.info['callbacks'] if self.info else self.callback_original).items()}
        self.native_only, self.site, self.cpu = 0, None, None
        self.canonical_writes, self.pointer_writes, self.callbacks = [], [], []
        self.reads_by_context, self.writes_by_context = collections.defaultdict(set), collections.defaultdict(set)
        self.pc_by_context, self.min_sp = collections.defaultdict(set), 255
        self.handler_hits = collections.Counter()
        self.handler_starts = collections.defaultdict(list)
        for name,pc in self.labels.items():
            if name.startswith('WfOpcode') and name != 'WfOpcodeTable':
                self.handler_starts[pc].append(int(name[8:],16))

    def __getitem__(self,a):
        if isinstance(a,slice):
            return [self[i] for i in range(a.start,a.stop,a.step or 1)]
        if a < 0x2000:
            self.reads_by_context['callback' if self.native_only else 'component'].add(a&2047)
        if self.info and not self.native_only and self.bank == 0 and a >= 0x8000:
            if any(lo <= a < hi for lo,hi in self.overlays):
                return self.image[a-0x8000]
        return super().__getitem__(a)

    def __setitem__(self,a,v):
        value = v & 255
        canonical = value
        if a < 0x2000:
            self.writes_by_context['callback' if self.native_only else 'component'].add(a&2047)
        if self.variant == 'relocated' and not self.native_only and self.site in [0xe39c,0xe3a1]:
            assert a == (0x1f if self.site == 0xe39c else 0x20), (self.site,a)
            table = self.labels['WfOpcodeTable'] + self.cpu.y
            candidate = self.image[table-0x8000]
            original = self.prg[0xe6ea+self.cpu.y-0x8000]
            assert value == candidate, ('Exact linked dispatch-byte producer',self.site,value,candidate,self.cpu.y)
            canonical = original
            self.pointer_writes.append((self.site,a,value,original,self.cpu.y))
        super().__setitem__(a,value)
        self.canonical_writes.append((a,canonical))

    def mark(self,c,native=False):
        self.cpu = c
        self.site = c.pc if native else self.reverse.get(c.pc,c.pc)
        self.executed.add((self.bank,self.site))
        self.pc_by_context['callback' if native else 'component'].add((self.bank,self.site))
        self.min_sp = min(self.min_sp,c.sp)
        if not native and self.bank == 0:
            for op in self.handler_starts.get(c.pc,[]):
                self.handler_hits[op] += 1

    def canonical_ram(self):
        ram = bytearray(self.ram)
        if self.variant == 'relocated':
            word = ram[0x1f]+256*ram[0x20]
            original = self.reverse.get(word)
            native_table = self.prg[0xe6ea-0x8000:0xe79e-0x8000]
            allowed = {native_table[i]+256*native_table[i+1] for i in range(0,len(native_table),2)}
            if original in allowed:
                ram[0x1f],ram[0x20] = original&255,original>>8
        return ram


def callback(b,c,name):
    """Execute donor callback using the already-present real JSR/tail frame."""
    before = cpu_state(c)
    # Read the live caller frame without modifying it or pushing a new one.
    target = ((b.ram[0x100+((c.sp+1)&255)] +
               256*b.ram[0x100+((c.sp+2)&255)])+1)&65535
    return_sp = (c.sp+2)&255
    n = MPU(memory=b,pc=b.callback_original[name])
    n.a,n.x,n.y,n.p,n.sp = c.a,c.x,c.y,c.p,c.sp
    start_writes, start_apu, bank = len(b.writes),len(b.apu),b.bank
    b.native_only += 1
    nested = []
    try:
        original_names = {v:k for k,v in b.callback_original.items()}
        for count in range(50000):
            if n.pc == target and n.sp == return_sp:
                break
            b.mark(n,native=True)
            if count and n.pc in original_names:
                nested.append(dict(name=original_names[n.pc],input=cpu_state(n)))
            assert b[n.pc] != 0, ('Native callback BRK',name,hex(n.pc),b.bank)
            n.step()
        else:
            raise AssertionError(('Native callback bound',name,hex(n.pc),n.sp,target,return_sp))
    finally:
        b.native_only -= 1
    c.a,c.x,c.y,c.p,c.sp,c.pc = n.a,n.x,n.y,n.p,n.sp,n.pc
    c.processorCycles += n.processorCycles
    b.callbacks.append(dict(name=name,input=before,output=cpu_state(c),
        CPU_cycles=n.processorCycles,bank_before=bank,bank_after=b.bank,
        app_writes=[w for w in b.canonical_writes[start_writes:] if not 0x100<=w[0]<0x200],
        audio=b.apu[start_apu:],nested=nested))


def call(b,name,*,a=0,x=0,y=0,flags=0x30):
    c = MPU(memory=b,pc=b.labels[name])
    c.a,c.x,c.y,c.p,c.sp = a,x,y,flags,253
    b.site=None; b.cpu=c
    c.stPushWord(0x7eff)
    for _ in range(50000):
        if c.pc == 0x7f00:
            return c
        if b.bank == 0 and c.pc in b.callback_pcs:
            callback(b,c,b.callback_pcs[c.pc])
            continue
        b.mark(c)
        assert b[c.pc] != 0, ('Component BRK',b.variant,b.bank,hex(c.pc))
        c.step()
    raise AssertionError(('Component bound',name,b.variant,hex(c.pc)))


def compare(buses,cpus,starts,location):
    oracle = buses[0]
    expected = oracle.ram
    exact_cycles = cpus[0].processorCycles
    for i,b in enumerate(buses[1:],1):
        assert cpu_state(cpus[i]) == cpu_state(cpus[0]), ('AXYP/SP',location,b.variant,cpu_state(cpus[0]),cpu_state(cpus[i]))
        current = b.ram if b.variant=='native' else b.canonical_ram()
        # Dead source stack return addresses relocate; every live byte remains exact.
        allowed_dead = set(range(0x100,0x101+cpus[i].sp)) if b.variant=='relocated' else set()
        diffs = [(a,expected[a],current[a]) for a in range(2048) if a not in allowed_dead and expected[a]!=current[a]]
        assert not diffs, ('RAM',location,b.variant,diffs[:20])
        ow = oracle.canonical_writes[starts[0][0]:]
        nw = b.canonical_writes[starts[i][0]:]
        if b.variant=='relocated':
            ow = [w for w in ow if not 0x100<=w[0]<0x200]
            nw = [w for w in nw if not 0x100<=w[0]<0x200]
        assert ow == nw, ('Ordered writes',location,b.variant,ow,nw)
        assert oracle.callbacks[starts[0][1]:] == b.callbacks[starts[i][1]:], ('Callback ABI/order',location,b.variant,oracle.callbacks[starts[0][1]:],b.callbacks[starts[i][1]:])
        assert oracle.bank == b.bank and oracle.io == b.io and oracle.apu == b.apu, ('Hardware callbacks',location,b.variant)
        if b.variant=='native':
            assert cpus[i].processorCycles == exact_cycles, ('Native origin cycles',location)
    return cpus[2].processorCycles-exact_cycles


def main():
    assert not O.exists(); O.mkdir()
    proof=json.loads((L/'build-proof.json').read_text())
    for p,h in proof['bindings'].items(): assert sha(p)==h,p
    ref=json.loads((W.O/'controls.json').read_text()); assert ref['passed'] and len(ref['cases'])==66
    prg=W.W.raw(); snapshot=(W.N/'capture/ram-match-entry.bin').read_bytes(); chars=W.W.tables(prg)
    report=dict(passed=False,source_CPU_lab=True,native_host=False,installed=False,
        original_native_trace_dispatches=1076,root_reference_updates=4224,
        callback_contract='Dynamic genuine donor code with original live return frame; no canned outputs or new source frame.',
        cases=[],limits=proof['limits']+[
            'No dense relocation of native state/data or SMB contact/ring adaptation is established.',
            'Oracle callback functions still depend on original donor environment; their code/data are excluded from component footprint.',
            'Actor1 cohorts are supplementary source fixtures, not part of the original66 root input cases.',
            'Dead page1 return bytes differ in relocated code; original-origin build compares every RAM byte/write.'])
    totals={variant:dict(read=set(),write=set(),callback_read=set(),callback_write=set(),pc=set(),callbacks=collections.Counter(),handlers=collections.Counter(),min_sp=255) for variant in [None,'native','relocated']}
    cycle_deltas=[]; api_calls=0; root_cases=0
    try:
        for actor in [0,1]:
            for ch in chars:
                for inp,held,fresh in INPUTS:
                    buses=[LabBus(prg,snapshot,proof,v) for v in [None,'native','relocated']]
                    def group(name,**kwargs):
                        nonlocal api_calls
                        starts=[(len(b.writes),len(b.callbacks)) for b in buses]
                        cpus=[call(b,name,**kwargs) for b in buses]
                        delta=compare(buses,cpus,starts,(actor,ch['id'],inp,name,api_calls));cycle_deltas.append(delta);api_calls+=1
                        return cpus,starts
                    for b in buses:
                        b.ram[0x2a+int(actor==0)],b.ram[0x2b-int(actor==0)] = ch['id'],(ch['id']+1)%6
                    group('WfInitDescriptors')
                    for b in buses:
                        for at in [0x3c,0x3d,0x3e,0x3f,0x40,0x41,0x8b,0x8c,0xa2,0xa3,0xa4,0xa5,0xcb,0xcc,0xc0,0xc1]: b.ram[at]=0
                        b.ram[0x0d+actor*2],b.ram[0x0e+actor*2]=held,fresh
                    group('WfSelectAction',x=actor,y=actor*2)
                    action=buses[0].ram[0x3e+actor]
                    expected=next(q['side_action'] for q in ch['original_input_action_selectors'] if q['input']==inp)
                    assert action==expected,(actor,ch['id'],inp,action,expected)
                    group('WfAdoptRequests')
                    for b in buses:
                        assert b.ram[0x3c+actor]==action
                        b.ram[0x0d+actor*2]=b.ram[0x0e+actor*2]=0
                    sequence=[]
                    for tick in range(64):
                        for b in buses:
                            b.ram[0x71]=(tick*2+actor)%6
                            b.ram[0x8d]=(snapshot[0x8d]+tick*2+actor)&255
                        cpus,starts=group('WfVmTick')
                        b=buses[0]
                        row=dict(tick=tick,action=b.ram[0x3c+actor],cursor=b.ram[0x40+actor],group=b.ram[0x32+actor],pose=b.ram[0x34+actor],x=b.ram[0x2c+actor],y=b.ram[0x2e+actor],direction=b.ram[0x3a+actor],CPU_cycles=cpus[0].processorCycles,writes=b.writes[starts[0][0]:])
                        sequence.append(row)
                    if actor==0:
                        old=ref['cases'][root_cases];root_cases+=1
                        assert old['character']==ch['id'] and old['input']==inp
                        assert json.loads(json.dumps(sequence))==old['sequence'],('Frozen4224 reference',ch['id'],inp)
                        assert buses[0].apu==[tuple(w) for w in old['original_audio_writes']] and buses[0].bank==old['final_bank']
                    report['cases'].append(dict(actor=actor,character=ch['id'],name=ch['name'],input=inp,native_action=action,source_updates=64,sequence_sha256=hashlib.sha256(json.dumps(sequence,sort_keys=True).encode()).hexdigest(),callback_counts=dict(collections.Counter(q['name'] for q in buses[0].callbacks))))
                    for b in buses:
                        t=totals[b.variant]
                        for key,source in [('read',b.reads_by_context['component']),('write',b.writes_by_context['component']),('callback_read',b.reads_by_context['callback']),('callback_write',b.writes_by_context['callback']),('pc',b.pc_by_context['component'])]:t[key].update(source)
                        t['callbacks'].update(q['name'] for q in b.callbacks);t['handlers'].update(b.handler_hits);t['min_sp']=min(t['min_sp'],b.min_sp)
            print(json.dumps(dict(actor=actor,cases=len(report['cases']),API_triplets=api_calls)),flush=True)
        report.update(passed=True,root_cases_reproduced=root_cases,native_origin_tick_pairs=8448,relocated_tick_pairs=8448,API_triplets=api_calls,relocated_cycle_delta=[min(cycle_deltas),max(cycle_deltas)],footprint={k:proof[k] for k in ['code_bytes','dispatch_table_bytes','descriptor_bytes','descriptor_pointer_bytes','script_bundle_bytes','actual_source_total_bytes']})
    except Exception as e:
        report.update(error=repr(e),traceback=traceback.format_exc());raise
    finally:
        report['observed']={str(v):{k:sorted(value) if isinstance(value,set) else dict(sorted(value.items())) if isinstance(value,collections.Counter) else value for k,value in t.items()} for v,t in totals.items()}
        report['bindings']={str(p.resolve()):sha(p) for p in [Path(__file__),Path(W.__file__),Path(W.W.__file__),W.W.ROM,W.N/'capture/ram-match-entry.bin',W.O/'controls.json',L/'build-proof.json',*list(L.glob('*.bin'))]}
        save(O/'controls.json',report)
        print(json.dumps({k:report.get(k) for k in ['passed','root_cases_reproduced','API_triplets','relocated_cycle_delta','error']}),flush=True)


if __name__=='__main__':main()
