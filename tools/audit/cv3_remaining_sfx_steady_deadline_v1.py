"""Reconstruct actual Hard-ice acceptance cutoff; seven ISR entry cycles are not slack."""
from pathlib import Path
import argparse,csv,hashlib,json
from check_tmnt_render_oa import load,Memory,address
from verify_native_relocation import NesMPU
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):return[{k:int(v)if v.lstrip('-').isdigit()else v for k,v in r.items()}for r in csv.DictReader(p.open())]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--basic',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old=a.basic/'baselines-v1/hard-ice';new=a.basic/'hard-ice';bt,nt=[rows(q/'deadline-timing.csv')for q in[old,new]];bpub=next(r for r in bt if r['kind']=='publication-write'and r['wall']==470);bnmi=next(r for r in bt if r['kind']=='NMI-entry'and r['wall']==471);nnmi=next(r for r in nt if r['kind']=='NMI-entry'and r['wall']==471);bdraw=next(r for r in bt if r['kind']=='NoLagSoDraw'and r['wall']==470);ndraw=next(r for r in nt if r['kind']=='NoLagSoDraw'and r['wall']==470);assert bpub['cpuCycle']==14024076 and bnmi['cpuCycle']==14024254 and nnmi['cpuCycle']==14024255 and nnmi['interruptedPC']==0x84a1;shift=ndraw['cpuCycle']-bdraw['cpuCycle'];assert shift==207
 prep=json.loads((new/'preparation.json').read_text());b=load(Path(prep['ROM']));traces=[]
 for ctrl in[0,6]:
  m=Memory(b);m[address(b,'VRAM_Buffer_AddrCtrl')]=ctrl;m[address(b,'AreaParserTaskNum')]=0;m[address(b,'ScrollThirtyTwo')]=0;c=NesMPU(memory=m,pc=0x84a1);c.sp=250;c.stPushWord(address(b,'PauseSkip')-1);m.writes=[];trace=[]
  for _ in range(40):
   pc=c.pc;before=c.processorCycles;n=len(m.writes);c.step();trace.append(dict(pc=pc,opcode=m[pc],cycles=c.processorCycles-before))
   if any(at==address(b,'NmiDisable')and v==0 for at,v in m.writes[n:]):break
  else:raise AssertionError('No original foreground publication')
  traces.append(dict(VRAMcontrol=ctrl,parser=0,scrollThirtyTwo=0,cycles_to_actual_publication=c.processorCycles,trace=trace))
 assert traces[0]['cycles_to_actual_publication']==35 and traces[1]['cycles_to_actual_publication']==21
 accept=nnmi['cpuCycle']-7;hyp=bpub['cpuCycle']+shift;recovery=hyp-accept;assert recovery==35 and hyp==14024283 and accept==14024248;assert m[0x849e:0x84a1]==[0x8d,0x5a,0x05]
 result=dict(passed=True,native_executed=False,actual_baseline_publication=bpub,actual_baseline_NMI_entry=bnmi,actual_candidate_NMI_entry=nnmi,actual_NoLagSoDraw_comparison=dict(baseline=bdraw,candidate=ndraw),assumed_hardware_NMI_entry_cycles=7,last_foreground_boundary_cycle=accept,stacked_next_PC=0x84a1,preceding_foreground_instruction=dict(pc=0x849e,bytes=[0x8d,0x5a,0x05],meaning='STA Left_Right_Buttons',cycles=4),matched_foreground_start_delay=shift,reconstructed_uninterrupted_publication=hyp,minimum_publication_recovery_cycles=recovery,baseline_margin_to_last_foreground_boundary=bnmi['cpuCycle']-7-bpub['cpuCycle'],compiled_tail_alternatives=traces,calculation='207 - (178 - 7) -1 NMI-entry phase difference =35',scope='Reconstruction from actual matched NoLag->publication foreground path and actual stacked nextPC, subtracting seven hardware-entrycycles. The compiled no-parser/no-scroll Ctrl0 tail uniquely matches35 remainingcycles. No mid-frame RAM snapshot was recorded: Ctrl6 alternative21 is disclosed, not falsely observed. Equal foreground work is source/actor/unchanged-code justified; this is a recovery target, not a new native outcome or grant. The later NmiDisable read inside ISR supplies NO additional foreground slack.',artifacts={str(q):sha(q)for q in[old/'deadline-timing.csv',new/'deadline-timing.csv',old/'actors.csv',new/'actors.csv']},ROM_sha256=sha(Path(prep['ROM'])),tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,native_executed=False,acceptance_cycle=accept,reconstructed_uninterrupted_publication=hyp,recovery_target=35,measured_RAM_snapshot_available=False),indent=2))
if __name__=='__main__':main()
