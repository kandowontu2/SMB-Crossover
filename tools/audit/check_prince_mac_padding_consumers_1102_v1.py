"""Actual finite Mac audio playback read closure for three source-declared pads.

No patch. Every read/fetch from these physical bytes fails immediately.
"""
from pathlib import Path
import hashlib,json
import audit_prince_pool_1102_v1 as A
import check_hogan_current_bounded_v1 as M
R,O=A.R,A.O


def main():
 assert A.sha(A.ROM)==A.SHA;b=A.scoped_load(A.ROM);seed=M.fresh(b)
 decl=json.loads((O/'resident-padding-proposal.json').read_text())
 assert decl['passed']and decl['ROM_SHA256']==A.SHA
 ranges=[tuple(v['CPU_half_open'])for v in decl['declared_pads']]
 class Reads(M.Bus):
  def __getitem__(self,i):
   if isinstance(i,int)and getattr(self,'monitor',False)and 0xa000<=i<0xc000 and self.rawtags[1]&127==123:
    assert not any(lo<=i<hi for lo,hi in ranges),('Actual Mac code/data reads declared pad',hex(i),self.song,self.tick)
    self.read_count+=1
   return super().__getitem__(i)
 ram=A.address(b,'LmNativeRam');zp=A.address(b,'LmNativeZp');rows=[]
 for song in [1,2,4,6,7,9,20,22,23]:
  m=M.fork(seed);m.__class__=Reads;m.song=song;m.tick=0;m.read_count=0;m.monitor=True
  m[ram:ram+288]=bytes(288);m[zp:zp+16]=bytes(16);m[248]=m[249]=0
  M.put(m,SelectedCharacter=15,OperMode=1)
  M.invoke(m,'LmNativeSourceInit',a=song-1)
  states={};digest=hashlib.sha256();cycles=0;minimum=255
  for tick in range(200000):
   m.tick=tick
   # This includes the complete original48B music state, all16 direct-ZP
   # bytes and the only genuine source indirect pointer F8/F9. APU output
   # images/dirty marks are write-only children, not music-control inputs.
   state=bytes(m[ram:ram+48])+bytes(m[zp:zp+16])+bytes([m[248],m[249]])
   if state in states:
    loop_start=states[state];period=tick-loop_start;break
   states[state]=tick;digest.update(state)
   r=M.invoke(m,'LmNativeMusicPlay');cycles+=r['CPU'];minimum=min(minimum,r['minimum_SP'])
   if tick and tick%20000==0:print(json.dumps(dict(song=song,updates=tick,source_reads=m.read_count,still_seeking_exact_state_repeat=True)),flush=True)
  else:raise AssertionError(('Source state did not close in finite bound',song))
  assert tick>100 and period>0,(song,tick,period)
  rows.append(dict(song=song,original_updates_to_closed_state=tick,loop_start=loop_start,period=period,actual_source_bank_reads=m.read_count,CPU=cycles,minimum_SP=minimum,ordered_source_state_SHA256=digest.hexdigest()))
  print(json.dumps(rows[-1]),flush=True)
 q=dict(passed=True,ROM_SHA256=A.SHA,proposal_only=True,resource_granted=False,source_declared_padding_only=True,all_nine_legal_track_state_machines_closed=True,actual_source_code_and_data_reads_never_enter_pad=True,rows=rows,scope='All nine source tracks from their genuine initialization until exact source control-state repetition, executing actual current bank123 source instructions and real APU-store children. No arbitrary corrupted-source pointers, raster or native audio waveform claim. Mixed request/restart/retirement call closure still requires source review.',bindings={str(p.relative_to(R)):A.sha(p)for p in[Path(__file__),A.ROM,R/'src/mac_native_music.s',O/'resident-padding-proposal.json']})
 (O/'resident-pad-consumers.json').write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
