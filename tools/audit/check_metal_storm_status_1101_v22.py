"""Actual cartridge transport: typed A/Z status, guards and scratch lifetime."""
import itertools,json
import prepare_metal_storm_status_1101_v22 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load

def main():
 q=json.loads((P.O/'assembly.json').read_text())
 for p,h in q['bindings'].items():assert P.P.sha(p)==h,p
 b=scoped_load(P.O/'candidate.nes');seed=M.fresh(b)
 for bank,offset,name in [(3,0,'native-actor.bin'),(2,0xd00,'native-render.bin')]:
  data=(P.O/name).read_bytes();seed.ram[bank][offset:offset+len(data)]=data;seed.ram[bank][0x1fe0:0x1ff0]=bytes.fromhex(q['cookie'])
 M.put(seed,SelectedCharacter=35);cases=0
 for armor,immune,barrier,gravity,flags,incoming in itertools.product([0,1,128],[0,1,128],[0,128],[0,128],[0x30,0x71,0xb0,0xf1],[0,85]):
  m=M.fork(seed)
  for at,v in [(0x5d0,armor),(0x648,immune),(0x660,barrier),(0x630,gravity)]:m.ram[2][at]=v
  zp=bytes(m[:11]);maps=m.rawtags[:]
  result=M.invoke(m,'HuInjuryStatus',a=incoming,x=7,y=91,p=flags)
  expected=int(bool(armor or ((immune|barrier|gravity)&128)))
  assert result['A']==expected and bool(result['P']&2)==(expected==0),(armor,immune,barrier,gravity,result)
  assert result['X']==7 and result['Y']==91 and result['P']&1 and not result['P']&128
  assert bytes(m[:11])==zp and m.rawtags==maps
  cases+=1
 rejects=0
 for bank,index in itertools.product([2,3],range(16)):
  m=M.fork(seed);m.ram[bank][0x1fe0+index]^=1
  before=[bytes(m.ram[n]) for n in [2,3]];result=M.invoke(m,'HuInjuryStatus',a=85,p=0x71)
  assert result['A']==85 and not result['P']&1 and [bytes(m.ram[n]) for n in [2,3]]==before
  rejects+=1
 result=dict(passed=True,ROM_sha256=q['ROM_sha256'],typed_status_cases=cases,corrupt_header_cases=rejects,fixture='Manually seeded compiled code/data caches and owner cookies. Actual ROM ingress and bank transport executed; not cold-loader or native play proof.',scope='Status only; injury start and source hurt/death lifecycle are still pending. Not installed.')
 (P.O/'status-CPU.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
