"""Observe current Mike native music ROM reads beside the final Tank region."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
import mike_native_music_cpu as C
from check_tank_terminal_leaves_1101_v1 import O,P,PIN
def main():
 b=scoped_load(P);assert hashlib.sha256(b['raw']).hexdigest()==PIN
 assert address(b,'StNativeBankStart')==0xa200
 original=C.MusicMemory
 class Reads(original):
  def __getitem__(self,i):
   if isinstance(i,int)and 0xa000<=i<0xc000 and self.banks[1]==115:
    assert i>=0xa200,('Mike reads preceding owner',hex(i),getattr(self,'pc',None))
    self.low=min(getattr(self,'low',0xffff),i);self.high=max(getattr(self,'high',0),i)
   return super().__getitem__(i)
 rows=[];C.MusicMemory=Reads
 try:
  for song in [1,2,4,5,9,11,13,14,15,17,22]:
   r=C.Run(b);r.call('StNativeSourceInit',a=song-1)
   for _ in range(18000):r.call('StNativeMusicPlay')
   rows.append(dict(song=song,play_calls=18000,read_half_open=[r.m.low,r.m.high+1]))
   print(json.dumps(rows[-1]),flush=True)
 finally:C.MusicMemory=original
 q=dict(passed=True,ROM_sha256=PIN,tracks=rows,total_play_calls=198000,proposed_gap=[0xa195,0xa200],scope='Actual current compiled source init and active music leaf, original supported track domain,18000 calls each. Read-boundary check only; no waveform or gameplay qualification.',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (O/'Mike-music-tail.json').write_text(json.dumps(q,indent=2)+'\n')
if __name__=='__main__':main()
