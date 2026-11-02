"""Compare the real public shot callback; explicitly bound dead scratch differences."""
import itertools,json
import prepare_metal_storm_idle_shots_1101_v41 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load

def seed(rom,component):
 m=M.fresh(scoped_load(rom))
 for bank,at,f in [(3,0,'native-actor.bin'),(2,0xd00,'native-render.bin'),(2,0x1ba0,'native-extra.bin')]:
  d=(component/f).read_bytes();m.ram[bank][at:at+len(d)]=d
 for bank in [2,3]:m.ram[bank][0x1fe0:0x1ff0]=(component/'native-cookie.bin').read_bytes()
 M.put(m,SelectedCharacter=35,OperMode=1,GameEngineSubroutine=8,GamePauseStatus=0,ObjectOffset=4)
 return m

def main():
 seeds=[seed(P.BASE/'candidate.nes',P.P.O),seed(P.O/'candidate.nes',P.O)]
 cases=0;costs=[]
 for flags,pause,engine,invalid in itertools.product([(0,0),(1,127),(127,1),(128,0),(0,128),(128,128)],[0,1],[8,11],[-1,*range(32)]):
  pair=[]
  for s in seeds:
   m=M.fork(s);m.ram[2][0x512:0x514]=bytes(flags)
   M.put(m,GamePauseStatus=pause,GameEngineSubroutine=engine)
   if invalid>=0:m.ram[2+invalid//16][0x1fe0+invalid%16]^=1
   pair.append((m,M.invoke(m,'HuWeaponTail')))
  (a,z),(b,w)=pair
  assert all(z[k]==w[k] for k in ['A','X','Y','P'])
  assert a.rawtags==b.rawtags
  for lo,hi in [(0,256),(512,2048)]:assert a[lo:hi]==b[lo:hi]
  # Source state, lifecycle context, enemy effects and mapper state must match.
  # Only disposable renderer scratch C81A..C83C and C880..C887 may differ.
  for lo,hi in [(0,0x81a),(0x83d,0x880),(0x888,0xd00)]:assert a.ram[2][lo:hi]==b.ram[2][lo:hi],(flags,pause,engine,invalid,lo)
  assert a.ram[3][:0x1fe0]==b.ram[3][:0x1fe0]
  if invalid<0 and flags==(0,0) and pause==0 and engine==8:costs.append([z['CPU'],w['CPU']])
  cases+=1
 q=dict(passed=True,cases=cases,idle_cycles=costs,ROM_sha256=P.P.P.sha(P.O/'candidate.nes'),scope='Public callback AXYP/native RAM/mapper/source state match; intentional dead scratch omission only. All 32 header corruptions reject unchanged. Native timing pending.')
 (P.O/'CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
