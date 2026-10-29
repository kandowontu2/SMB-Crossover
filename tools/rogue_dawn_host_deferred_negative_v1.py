"""Preserve the second real SP192 lag-NMI failure; CPU only."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_host_deferred_controls_v1 as d
import rogue_dawn_map_v1 as ref
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU

def main():
 b=d.old.scoped_load(d.B);m=d.setup(b,tile=0x60)
 for name in ['RdTxMovementBegin','RdControlStep','RdHsExportPosition']:d.call(m,name)
 d.service.invoke(m,address(b,'AudioInit'),sp=240)
 d.service.invoke(m,address(b,'SamusAudioInit'),sp=240)
 m[address(b,'AreaMusicQueue')]=1;m[address(b,'NmiDisable')]=255
 m.page(1,95);m[address(b,'CurrentBank')]=223
 c=NesMPU(memory=m,pc=address(b,'RdTxAfterMovement'));c.sp=192;c.p=0x71;c.stPushWord(0x5aff)
 low=c.sp;fired=False;row={}
 smc=[address(b,n)+k for n,k in [('NextBank_SMC',1),('SafecallA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2),('SafereturnA_SMC',1)]]
 for _ in range(100000):
  if (c.pc,m.banks[1])==(address(b,'RdHsPrepareActor'),95):
   row=dict(entry_PC=c.pc,physical_A=95,entry_SP=c.sp,before_SMC=[m[z]for z in smc]);ret=c.pc;sp=c.sp
   c.nmi()
   for _ in range(50000):
    low=min(low,c.sp);c.step()
    if c.pc==ret and c.sp==sp:break
   else:raise AssertionError('ISR timeout')
   row.update(minimum_SP=low,after_SMC=[m[z]for z in smc]);fired=True;break
  assert m[c.pc]!=0,('BRK',hex(c.pc));c.step();low=min(low,c.sp)
 assert fired and row['before_SMC']!=row['after_SMC'] and low<123,row
 frozen=[]
 for p in [R/'src/rogue_dawn_host_deferred.s',R/'tools/rogue_dawn_host_deferred_controls_v1.py',R/'tools/prepare_rogue_dawn_host_deferred_v1.py']:
  q=d.O/('frozen-'+p.name)
  if q.exists():assert q.read_bytes()==p.read_bytes()
  else:q.write_bytes(p.read_bytes())
  frozen.append(dict(original=str(p),saved=ref.binding(q)))
 proof=dict(passed=False,expected_negative=True,native_run=False,ROM_sha256=ref.digest(d.B.read_bytes()),classification='Deferred world effect still has eight unnecessary incoming native scratch saves in its preserved standalone ABI; lag NMI reaches live SMC at original SP192.',actual=row,completed_prior_campaign=dict(action_pad_facing_gear_cells=18432,immediate_source_and_final_native_effect_comparisons=40),preserved_sources=frozen,bindings=[ref.binding(p)for p in[Path(__file__),d.B,d.B.with_suffix('.dbg'),d.O/'build.json']])
 (d.O/'control-SP192-deferred-negative.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(row))
if __name__=='__main__':main()
