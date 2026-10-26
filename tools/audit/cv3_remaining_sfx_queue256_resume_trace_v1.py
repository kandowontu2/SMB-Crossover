"""Retain the first pending-pause source register mismatch and actual writers."""
from pathlib import Path
import hashlib,json
from check_tmnt_render_oa import load,address
from cv3_remaining_sfx_queue256_support_v1 import init,sound
from verify_native_relocation import NesMPU
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/cv3-remaining-queue256-v1')
rows=[]
for directory in ['candidate-v1','candidate-v2']:
 p=D/directory/'candidate.nes';b=load(p);q=init(b,3);q.put(GamePauseStatus=1);sound(q,0x21)
 for _ in range(3):q.invoke('AudioUpdate')
 before={n:q.get(n)for n in ['Cv3FxOwned','Cv3NoiseActive','Cv3FxPendingNoise','Cv3FxPendingPulse','Cv3FxPulseID','Cv3FxQueueHead','Cv3FxQueueTail']}
 q.put(GamePauseStatus=0,RgAudioSilenced=0);sym=b['syms']['AudioUpdate'];seg=b['segs'][sym['seg']];bank=(int(seg['ooffs'],0)-16)//8192;pc=address(b,'AudioUpdate');window=(pc-0x8000)//8192;q.m.page(window,bank)
 if window in[1,2]:q.set('CurrentBank'if window==1 else'CurrentBankC',bank|128)
 c=NesMPU(memory=q.m,pc=pc);c.sp=253;c.stPushWord(0x5aff);q.m.writes=[];watches={0x4003,address(b,'GuestNativeDirty')+3,address(b,'Cv3FxOwned'),address(b,'Cv3FxPendingPulse')};trace=[]
 for _ in range(100000):
  if c.pc==0x5b00:break
  at=len(q.m.writes);pc=c.pc;c.step()
  for loc,value in q.m.writes[at:]:
   if loc in watches:trace.append(dict(pc=pc,cycle=c.processorCycles,address=loc,value=value,banks=list(q.m.banks)))
 else:raise AssertionError('timeout')
 rows.append(dict(directory=directory,ROM_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),before=before,trace=trace,APU=[r for r in q.m.writes if 0x4000<=r[0]<=0x4017]))
out=D/'resume-negative-v1';out.mkdir(exist_ok=False);(out/'proof.json').write_text(json.dumps(dict(accepted=False,expected_source_pulse_first_frame=[[0x4000,0x30],[0x4001,0x7f]],rows=rows),indent=2)+'\n');print(json.dumps(rows,indent=2))
