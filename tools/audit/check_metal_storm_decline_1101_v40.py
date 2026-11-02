"""Compare actual old/new public callbacks, including malformed cache headers."""
import itertools,json
import prepare_metal_storm_decline_1101_v40 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load

def main():
 seeds=[]
 for rom in [P.BASE/'candidate.nes',P.O/'candidate.nes']:
  m=M.fresh(scoped_load(rom))
  for bank,at,f in [(3,0,'native-actor.bin'),(2,0xd00,'native-render.bin'),(2,0x1ba0,'native-extra.bin')]:
   d=(P.BASE/f).read_bytes();m.ram[bank][at:at+len(d)]=d
  for bank in [2,3]:m.ram[bank][0x1fe0:0x1ff0]=(P.BASE/'native-cookie.bin').read_bytes()
  M.put(m,SelectedCharacter=35,OperMode=1,GameEngineSubroutine=8)
  seeds.append(m)
 cases=0;savings=[]
 for name,a,p,bad in itertools.product(['HuVisible','HuBox','HuUi'],[0,1,85,255],[0x20,0x21,0x60,0xa1],[-1,*range(32)]):
  pair=[]
  for seed in seeds:
   m=M.fork(seed)
   if bad>=0:m.ram[2+bad//16][0x1fe0+bad%16]^=1
   z=M.invoke(m,name,a=a,x=19,y=73,p=p);pair.append((m,z))
  old,z=pair[0];new,w=pair[1]
  assert [z[k] for k in ['A','X','Y','P']]==[w[k] for k in ['A','X','Y','P']],(name,a,p,bad,z,w)
  for lo,hi in [(0,256),(512,2048)]:assert old[lo:hi]==new[lo:hi],(name,lo)
  assert old.ram==new.ram,(name,'banked RAM')
  assert old.rawtags==new.rawtags,(name,'mapping')
  if bad<0:savings.append(z['CPU']-w['CPU'])
  cases+=1
 q=dict(passed=True,ROM_sha256=P.P.sha(P.O/'candidate.nes'),cases=cases,full_header_bit_corruptions=32,valid_cache_saved_cycles=[min(savings),max(savings)],scope='Actual public callbacks preserve returnedAXYP, non-stack nativeRAM, all four WRAM banks and mapping. Native timing/route regression pending.')
 (P.O/'CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
