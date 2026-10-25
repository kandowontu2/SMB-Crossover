"""Exact native caller replay and CI/CJ consumer liveness through GameLoop."""
from pathlib import Path
import argparse, collections, hashlib, importlib.util, json, struct, traceback

R=Path(__file__).resolve().parents[2];V=R/'build/verification'
O=V/'water-current-suffix-cr'
P=V/'agent49-samus-bill-arsenal-a/palette_native_model_cu.py'
spec=importlib.util.spec_from_file_location('water_cp_model',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class CPU(m.q.core.NesMPU):
    cycletime=list(m.q.core.NesMPU.cycletime);cycletime[0xce]=6
m.q.core.NesMPU=CPU
class Tracked(m.Bus):
    def __init__(self,*args):
        super().__init__(*args);self.written=set();self.first_reads={};self.writer_banks=[]
    def __getitem__(self,a):
        if a not in self.written:self.first_reads.setdefault(a,(self.pc,self.op))
        return super().__getitem__(a)
    def write(self,a,physical,value):
        self.writer_banks.append(self.banks[self.pc&0xe000]if self.pc>=0x8000 else-1)
        self.written.add(physical);super().write(a,physical,value)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def writer_identity(im,pc,physical):
    bank=(physical-16)//8192 if physical>=16 else -1
    candidates=[]
    for symbol in im.data['sym']:
        if 'seg'not in symbol or not symbol.get('size'):continue
        seg=im.segs[symbol['seg']]
        if 'ooffs'not in seg or not symbol['val']<=pc<symbol['val']+symbol['size']:continue
        offset=seg['ooffs']+pc-seg['start']
        if(offset-16)//8192!=bank:continue
        scope=im.scopes.get(symbol.get('scope'),{}).get('name','')
        candidates.append((symbol['size'],scope,symbol['name'],pc-symbol['val']))
    assert candidates,('Actual relocated writer identity',pc,physical)
    return min(candidates)[1:]

def suffix_writes(ims,ss):
    # Bind each changed write to its decoded producer. No stack or SMC
    # range is dropped from the ordered trace.
    left,right=[s['trace']for s in ss];assert len(left)==len(right)
    annotated=[]
    for index,(a,b)in enumerate(zip(left,right)):
        assert a[2:4]==b[2:4]
        if a[4]==b[4]:continue
        ad=a[3]
        if a[1]==b[1]==0x20 and 0x100<=ad<=0x100+ss[0]['regs'][4]:
            identities=[]
            for image,write in zip(ims,(a,b)):
                bank=ss[len(identities)]['writer_banks'][index]
                offset=16+bank*8192+(write[0]&8191)
                assert image.raw[offset]==0x20
                assert write[4]in((write[0]+2)&255,(write[0]+2)>>8)
                identities.append(writer_identity(image,write[0],offset))
            assert identities[0]==identities[1]
            annotated.append(dict(index=index,address=ad,producer='relocated JSR return push',writer=identities[0]))
        else:
            assert a[1]==b[1]==0x8d and ad in(ims[0].ram['FarcallJmpTarget_SMC']+1,ims[0].ram['FarcallJmpTarget_SMC']+2)
            shift=8*(ad-ims[0].ram['FarcallJmpTarget_SMC']-1)
            targets=[]
            for which,(image,write)in enumerate(zip(ims,(a,b))):
                bank=ss[which]['writer_banks'][index];off=16+bank*8192+(write[0]&8191)
                base=off-(5 if shift else 0);code=image.raw[base-2:base+13]
                assert code[0]==code[5]==code[10]==0xa9 and code[2]==code[7]==0x8d and code[12]==0x20
                target=code[1]+256*code[6];target_bank=code[11]&127
                assert write[4]==(target>>shift)&255
                assert code[3]+256*code[4]==image.ram['FarcallJmpTarget_SMC']+1
                assert code[8]+256*code[9]==image.ram['FarcallJmpTarget_SMC']+2
                targets.append(image.pointer(target_bank,target))
            assert targets[0]&targets[1],('Same symbolic farcall target',targets)
            annotated.append(dict(index=index,address=ad,producer='standard farcall symbolic operand',targets=sorted(targets[0]&targets[1])))
    return annotated

def suffix(im,q,dirtyY):
    bus=Tracked(im,q['ram'],q['banks'],());cpu=CPU(memory=bus)
    cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc=q['regs'];cpu.processorCycles=0
    target=im.hook('PauseSkip','GameLoop')['address'];firstY=None
    for steps in range(50000):
        if cpu.pc==target:break
        bus.pc=cpu.pc;bus.op=bus.data[cpu.pc]
        mnemonic,mode=cpu.disassemble[bus.op]
        if dirtyY:
            assert mnemonic not in('STY','TYA','INY','DEY')and mode not in('aby','iny','zpy'),('Changed Y read before replacement',cpu.pc,mnemonic,mode)
            if mnemonic in('LDY','TAY','PLY'):
                dirtyY=False;firstY=dict(PC=cpu.pc,opcode=bus.op,mnemonic=mnemonic)
        popped=bus.data[0x100+((cpu.sp+1)&255)]if bus.op in(0x28,0x40)else None
        cpu.step()
        if popped is not None:cpu.p=popped&0xcf
    else:raise AssertionError('Bounded actual parent GameLoop suffix')
    assert not dirtyY
    return dict(regs=[cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc],ram=bus.ram(),banks=bus.banks,
        selector=bus.selector,ports=bus.ports,trace=bus.trace,writer_banks=bus.writer_banks,first_reads=bus.first_reads,firstY=firstY,steps=steps)

def main():
    global O
    parser=argparse.ArgumentParser();parser.add_argument('--dense',action='store_true');args=parser.parse_args()
    if args.dense:O=V/'water-current-dense-caller-cu'
    assert not O.exists();O.mkdir()
    report=dict(status='REVIEWING',groups=[],script_sha256=sha(__file__),model_sha256=sha(P),
        scope='Actual current native full caller replays every attained ISR, RAM byte and ordered write. Separate matched noISR CI/CJ calls continue through the real parent GameLoop, checking changed registerY and every differing input RAM cell before overwrite. Authored equipment diagnostic, not a route clear or natural acquisition.',goal_complete=False)
    try:
        for mapper in('mmc3','mmc5'):
            ims=[m.q.Image(R/'build/checkpoints/firebar-budget-ci/build'/f'smb-crossover-{mapper}.nes'),m.q.Image(R/'build'/f'smb-crossover-{mapper}.nes')]
            old,im=ims;L=im.ram;assert old.ram==L
            names={ad:n for n,ad in L.items()}
            for char in((9,)if args.dense else(1,9)):
                folder=V/'water-current-dense-ct'/f'{mapper}-H'if args.dense else V/'water-visible-profile-cm'/f'CJ-{mapper}-{char}'
                binding=json.loads((folder/'binding.json').read_text());assert sha(im.path)==binding['ROM']['rom']['sha256']
                native=folder/'native';events=[json.loads(z)for z in(native/'caller.jsonl').read_text().splitlines()]
                raw=(native/'caller-ram.bin').read_bytes();ws=list(struct.Struct('<HHBIh').iter_unpack((native/'caller-writes.bin').read_bytes()))
                hardware=[json.loads(z)for z in(native/'caller-hardware.jsonl').read_text().splitlines()]
                pairs={}
                for z in events:
                    if z['event']in('entry','return'):pairs.setdefault(z['id'],{})[z['event']]=z
                group=dict(mapper=mapper,character=char,calls=[],differences=collections.Counter())
                report['groups'].append(group)
                for ident,pair in pairs.items():
                    assert set(pair)=={'entry','return'};e,z=pair['entry'],pair['return']
                    before=m.snapshot(raw,e);after=m.snapshot(raw,z);regs=[e[n]for n in('A','X','Y','P','SP')]
                    banks={ad:e[n]for ad,n in((0x8000,'bank8'),(0xa000,'bankA'),(0xc000,'bankC'),(0xe000,'bankE'))}
                    interrupts=m.irq_records(events,raw,e,z);reads=[r for r in hardware if e['cycle']<r['cycle']<z['cycle']]
                    exact=m.execute(im,before,regs,banks,e['PC'],z['PC'],z['SP'],interrupts=interrupts,hardware=reads)
                    assert exact['regs']==[z[n]for n in('A','X','Y','P','SP','PC')]
                    assert exact['ram']==after,'Every native RAM byte including scratch, stack and SMC'
                    assert [(w[1],w[2])for w in ws[e['writeCount']:z['writeCount']]]==[(t[2],t[4])for t in exact['trace']]
                    assert exact['banks']==banks=={ad:z[n]for ad,n in((0x8000,'bank8'),(0xa000,'bankA'),(0xc000,'bankC'),(0xe000,'bankE'))}
                    if'BankShadow'in L:assert exact['selector']==after[L['BankShadow']]
                    qs=[m.execute(image,before,regs,banks,e['PC'],z['PC'],z['SP'])for image in ims]
                    a,b=qs
                    assert a['regs'][:2]+a['regs'][3:]==b['regs'][:2]+b['regs'][3:],'Same caller AX/P/SP/PC; Y explicitly tracked'
                    assert a['banks']==b['banks']and a['selector']==b['selector']and a['ports']==b['ports']
                    diff={i if i<2048 else i-2048+0x6000 for i,(x,y)in enumerate(zip(a['ram'],b['ram']))if x!=y}
                    ss=[suffix(image,q,a['regs'][2]!=b['regs'][2])for image,q in zip(ims,qs)]
                    for s in ss:
                        assert not diff&set(s['first_reads']),('Changed input read by actual GameLoop suffix',mapper,char,ident,[(hex(ad),s['first_reads'][ad])for ad in diff&set(s['first_reads'])])
                    assert ss[0]['regs']==ss[1]['regs']and ss[0]['banks']==ss[1]['banks']and ss[0]['selector']==ss[1]['selector']and ss[0]['ports']==ss[1]['ports']
                    annotated=suffix_writes(ims,ss)
                    remaining={i if i<2048 else i-2048+0x6000 for i,(x,y)in enumerate(zip(ss[0]['ram'],ss[1]['ram']))if x!=y}
                    assert remaining<=diff|{r['address']for r in annotated},'Only explicitly decoded dead return pushes can introduce new differences'
                    for ad in diff:group['differences'][names.get(ad,hex(ad))]+=1
                    group['calls'].append(dict(id=ident,frame=e['frame'],actual_interrupts=len(exact['interrupts']),native_exact=True,
                        matched_cycles=[a['cycles'],b['cycles']],changed_input_cells=sorted(diff),dead_through_GameLoop=True,
                        firstY_replacement=[s['firstY']for s in ss],remaining_dead_cells=sorted(remaining),suffix_steps=ss[0]['steps'],relocated_suffix_writes=annotated))
                print('CURRENT_CP',mapper,char,len(group['calls']),sum(z['actual_interrupts']for z in group['calls']),flush=True)
        report['status']='PASS_NATIVE_EXACT_AND_CURRENT_CALLER_SUFFIX_NO_CHANGED_INPUT_READ'
    except Exception as error:
        report.update(status='FAIL_RETAINED',error=repr(error),traceback=traceback.format_exc());raise
    finally:(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
