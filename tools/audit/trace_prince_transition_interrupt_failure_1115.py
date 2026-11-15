"""Unchanged7700 ISR probe with detailed failure-only native/stack report."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import inspect,json
import check_prince_transition_interrupts_1115 as Frozen

PIN='7700a2d6782c62dc926fe6b07b655ebad47ef5d9394603c63004e5a831b53b02'


class DetailedDifference(Exception):
    def __init__(self,q):self.q=q


def fail(cpu,m,before,after,regs,left,right,protected,kind,base):
    native=[dict(address=0x200+i,before=a,after=b,legacy_masked=(0x200+i)==0x7da)
        for i,(a,b)in enumerate(zip(before[5],after[5]))if a!=b]
    upper=[dict(address=0x101+regs[4]+i,before=a,after=b)
        for i,(a,b)in enumerate(zip(protected,bytes(m[0x101+regs[4]:0x200])))if a!=b]
    wanted={row['address']for row in native+upper};symbols=[]
    for name,row in m.bundle['syms'].items():
        address=int(row['val'],0)
        if any(0<=at-address<=16 for at in wanted):
            segment=m.bundle['segs'].get(row.get('seg'),{}).get('name')
            symbols.append(dict(name=name,address=address,segment=segment))
    # Re-execute just this ISR on another copy of the SAME genuine context.
    # Record the actual instructions which write differing addresses.
    probe=Frozen.N.fork(cpu.memory);probe.__class__=Frozen.W.ControllerBus
    c=base(memory=probe,pc=cpu.pc);c.a,c.x,c.y,c.p,c.sp=cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp
    writes=[];c.irq()if kind=='IRQ'else c.nmi()
    for _ in range(100000):
        if(c.pc,c.sp)==(regs[5],regs[4]):break
        pc=c.pc;tag=probe.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
        values={at:probe[at]for at in wanted};opcode=bytes(probe[pc:pc+3]).hex();c.step()
        for at,value in values.items():
            if probe[at]!=value:writes.append(dict(PC=pc,map_tag=tag,opcode3=opcode,address=at,before=value,after=probe[at]))
    else:raise AssertionError('Failure-only ISR writer replay bound')
    q=dict(initial_probe_source_SHA256=PIN,kind=kind,foreground_PC=cpu.pc,foreground_SP=regs[4],foreground_P=regs[3],
        actual_genuine_context=Frozen.Model.state(cpu.memory),native_differences=native,
        native_difference_after_existing7DA_mask=[dict(address=0x200+i,before=a,after=b)for i,(a,b)in enumerate(zip(left,right))if a!=b],
        above_entry_stack_differences=upper,actual_symbol_addresses=sorted(symbols,key=lambda r:(r['address'],r['name'])),
        differing_address_actual_writer_instructions=writes,
        private_scratch_mapper_CHR_and_regs_checks_already_passed=True,
        NmiSkipped_increment_check_already_passed=kind=='busyNMI',
        widened_masks=0,gameplay_seeds=0,outputs=0,Mesen=False,
        scope='Detailed retained failure of the original strict ISR condition; no acceptance relaxation')
    raise DetailedDifference(q)


def run(raw):
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==PIN
    source=inspect.getsource(Frozen.run)
    old='        assert left==right and bytes(m[0x101+regs[4]:0x200])==protected'
    assert source.count(old)==1
    new="        if not(left==right and bytes(m[0x101+regs[4]:0x200])==protected):\n            failure_detail(cpu,m,before,after,regs,left,right,protected,kind,base)"
    space=dict(Frozen.__dict__,failure_detail=fail);exec(compile(source.replace(old,new,1),str(Path(__file__))+':unchanged-probe','exec'),space)
    try:q=space['run'](raw)
    except DetailedDifference as error:q=error.q;q['strict_ISR_probe_passed']=False
    else:q['strict_ISR_probe_passed']=True
    q['diagnostic_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Failure trace attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
