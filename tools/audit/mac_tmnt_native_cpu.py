"""Current55 CPU regression, full-byte Mac life transitions, canonical game-over."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
from vehicles_mike_mac_audit_cpu_v1 import mac,Arena
from link_pit_rygar_sophia_audit_cpu import scoped_load as load
from check_tmnt_render_oa import address,location
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(exist_ok=False)
 subprocess.run([sys.executable,str(ROOT/'tools/audit/vehicles_mike_mac_audit_cpu_v1.py'),'--baseline',str(a.baseline),'--candidate',str(a.candidate),'--output',str(a.output/'prior-regression')],check=True,stdout=subprocess.DEVNULL)
 b=load(a.candidate);base=load(a.baseline);rows=[]
 fields=['LmHealth','LmStars','LmHearts','LmAttack','LmSuper','LmPrevious','LmWalk']
 for old in range(256):
  for delta in [0,1,2,-1]:
   now=(old+delta)&255;q=mac(b,old,now);got=[q.get(n)for n in fields]
   want=[96,0,20,0,0,0,0]if delta<0 else[37,3,9,24,1,64,17]
   assert got==want,(old,delta,now,got,want)
   assert q.get('LmLife')==now
   if delta>0:
    q.set('NumberofLives',(now-1)&255);q.call('LmEnsure')
    assert [q.get(n)for n in fields]==[96,0,20,0,0,0,0]
   rows.append(dict(old=old,delta=delta,new=now,state=got))
 # Preserve canonical signed DEC/BPL semantics, including its unusual high
 # counts. Execute the actual opcode stream until the canonical BPL decides.
 decisions=[]
 for lives in range(256):
  q=Arena(b);q.put(NumberofLives=lives,OperMode=1,OperMode_Task=3)
  n='PlayerLoseLife';at=location(b,n);pc=address(b,n);q.m.page((pc-32768)//8192,(at-16)//8192)
  from verify_native_relocation import NesMPU
  c=NesMPU(memory=q.m,pc=pc);trace=[]
  for _ in range(20):
   op=q.m[c.pc];trace.append(c.pc)
   if op==0x10:
    expected=(lives-1)&255;assert q.get('NumberofLives')==expected
    taken=expected<128;c.step()
    decisions.append(dict(before=lives,after=expected,continues=taken,branch_pc=trace[-1],next_pc=c.pc));break
   c.step()
  else:raise AssertionError('Canonical DEC/BPL not reached')
 assert decisions[0]['continues']is False and decisions[128]['continues']is True and decisions[129]['continues']is False
 original=base['raw'];new=b['raw'];n='PlayerLoseLife';assert original[location(base,n):location(base,n)+int(base['syms'][n]['size'],0)]==new[location(b,n):location(b,n)+int(b['syms'][n]['size'],0)]
 (a.output/'life-transitions.json').write_text(json.dumps(rows,separators=(',',':')))
 (a.output/'canonical-death-decisions.json').write_text(json.dumps(decisions,separators=(',',':')))
 proof=dict(passed=True,baseline_sha256=sha(a.baseline),ROM_sha256=sha(a.candidate),full_byte_life_cases=len(rows),gain_then_actual_assembled_ensure_loss_cases=512,canonical_native_DEC_BPL_decisions=len(decisions),prior_regression=json.loads((a.output/'prior-regression/proof.json').read_text()),tool_sha256=sha(Path(__file__)),scope='Actual assembled CPU component routines. All byte values cover counter behavior, not claims all counts are naturally reached. Delta classification is valid for bounded native 0/+1/+2/-1 events; 127+ simultaneous gains unproved. Canonical high-count signed game-over rule unchanged. Prior component area/new-game and TMNT box/edge/rise/core coverage retained. Interrupt and visible actor qualification is separate.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps({k:v for k,v in proof.items()if k!='prior_regression'}))
if __name__=='__main__':main()
