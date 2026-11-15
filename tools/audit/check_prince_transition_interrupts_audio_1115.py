"""Separate7700 successor: one authenticated square1 duration decrement."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import inspect,json
import check_prince_transition_interrupts_1115 as Frozen

PIN='7700a2d6782c62dc926fe6b07b655ebad47ef5d9394603c63004e5a831b53b02'
WRITER_PC,WRITER_TAG=0xa19b,157


def run(raw):
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==PIN
    reports=[]
    def probe_cpu(base,m,kind):
        address=Frozen.W.address(m.bundle,'Squ1_SfxLenCounter');assert address==0x7d8
        at=16+(WRITER_TAG&127)*8192+(WRITER_PC&8191)
        assert raw[at:at+3]==bytes((0xce,address&255,address>>8))
        class Probe(base):
            def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.square1_writes=[]
            def step(self):
                hit=self.pc==WRITER_PC and self.memory.rawtags[1]==WRITER_TAG
                if hit:
                    assert bytes(self.memory[self.pc:self.pc+3])==raw[at:at+3]
                    before=self.memory[address]
                result=super().step()
                if hit:self.square1_writes.append(dict(PC=WRITER_PC,bank_tag=WRITER_TAG,address=address,before=before,after=self.memory[address]))
                return result
        return Probe
    def validate(c,m,before,after,left,right,kind):
        offset=0x7d8-0x200
        if left[offset]==right[offset]:return
        assert kind=='busyNMI'and len(c.square1_writes)==1,'Only one reached busy-NMI square1 DEC may differ'
        row=c.square1_writes[0];old,new=left[offset],right[offset]
        assert old>0 and new==old-1 and row['before']==old and row['after']==new
        reports.append(row)
        left[offset]=right[offset]=0
    source=inspect.getsource(Frozen.run)
    old='c=base(memory=m,pc=cpu.pc);';new='c=probe_cpu(base,m,kind)(memory=m,pc=cpu.pc);'
    assert source.count(old)==1;source=source.replace(old,new,1)
    marker='        assert left==right and bytes(m[0x101+regs[4]:0x200])==protected'
    assert source.count(marker)==1;source=source.replace(marker,'        validate_square1(c,m,before,after,left,right,kind)\n'+marker,1)
    space=dict(Frozen.__dict__,probe_cpu=probe_cpu,validate_square1=validate)
    exec(compile(source,str(Path(__file__))+':scoped-successor','exec'),space)
    q=space['run'](raw)
    q.update(initial_strict_probe_source_SHA256=PIN,additional_native_difference_scope='Only named Squ1_SfxLenCounter7D8, one authenticated PRG29:A19B DEC, positive N-toN-1, busyNMI only',
        square1_duration_cases=len(reports),square1_actual_writer=reports[:3],
        legacy_square2_mask_unchanged=True,all_other_native_RAM_and_above_entry_stack_strict=True)
    q['scoped_interrupt_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Scoped ISR source proof attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
