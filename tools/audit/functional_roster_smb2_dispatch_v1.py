"""Real shared caller endpoints, source identities, flags and mapper ABI.

Relocated Roll callbacks are compared by genuine linked symbol identity.
Only their actual target-bank/pointer transport metadata may differ.
"""
from pathlib import Path
import json,traceback
import current_quick_transport_controls_v4 as T
import prepare_functional_roster_smb2_v1 as B
O=B.O/'dispatch-controls';P=B.P;N=B.N
FLAGS=[p for p in range(256)if p&48==48]
def point_names(m,dest,tag):
 names=[]
 for n,v in m.lab.items():
  if v!=dest:continue
  try:bank=m.bank(n)|128
  except(KeyError,TypeError,ValueError):continue
  if bank==tag:names.append(n)
 return names
def same(old,new,case):
 x,a,c=old;y,b,d=new
 assert x['regs']==y['regs'],('caller AXYP/SP',case,x,y)
 assert x['mapper_entries']==y['mapper_entries'],('extra foreign resident mapper trip',case,x,y)
 names=point_names(a,x['dest'],x['bank']);matched=[]
 for n in names:
  if n not in b.lab:continue
  try:yes=b.lab[n]==y['dest']and(b.bank(n)|128)==y['bank']
  except(KeyError,TypeError,ValueError):yes=False
  if yes:matched.append(n)
 assert matched,('genuine callback identity',case,x,y,names)
 moved=(x['dest'],x['bank'])!=(y['dest'],y['bank'])
 transient={a.lab['FarcallJmpTarget_SMC']+1,a.lab['FarcallJmpTarget_SMC']+2,a.lab['NextBank_SMC']+1,a.lab['CurrentBank']}
 ignore=set(range(256,512))|set(range(0x5100,0x5140))|(transient if moved else set())
 assert all(a.ram[i]==b.ram[i]for i in range(0x8000)if i not in ignore),('application/SMC state',case)
 app=lambda m:[(ad,v)for ad,v in m.writes if ad not in ignore]
 assert app(a)==app(b),('ordered application/SMC writes',case)
 low=min(x['minimumSP'],y['minimumSP']);assert a.ram[256:256+low]==b.ram[256:256+low],('live/static page1',case)
 assert a.wram==b.wram and a.chr==b.chr,('all WRAM/CHR',case)
 assert a.tags[0]==b.tags[0]and a.tags[2:]==b.tags[2:]
 assert a.tags[1]==x['bank']and b.tags[1]==y['bank']
 return y['CPU']-x['CPU'],moved,matched[0]
def own(base,name,index,p):
 z,m,c=T.endpoint(T.fork(base),name,25,0,p)
 want=m.lab['S2ServiceVeneers']+3*index
 assert z['dest']==want and z['bank']==(m.bank('S2ServiceVeneers')|128),('actual S2 table slot',name,index,p,z,want)
 # The original Y and P are restored by the genuine shared restore/SFC.
 # Its final LDA sourceA imposes only N/Z, as in every original farcall.
 assert z['regs'][1]==90 and z['regs'][2]==199 and(z['regs'][3]&0x7d)==(p&0x7d)
 return z['CPU']
def main():
 assert not O.exists();O.mkdir();result=dict(passed=False,native=False,candidate=B.sha(N/'candidate.nes'));rows=[];moved={};counts={}
 try:
  aa,bb=[T.bus(x)for x in[P,N]]
  entries=T.FIRST+T.ONLY
  for name in['NrMovement','GmFreshGate']:
   values=[]
   for raw in range(256):
    if raw==25:continue
    for p in FLAGS:
     for alt in([0,32]if raw==9 else[0]):
      pair=[T.endpoint(T.fork(q),name,raw,alt,p)for q in[aa,bb]]
      delta,relocated,label=same(*pair,[raw,name,p,alt]);values.append(delta)
      if relocated:moved[label]=[pair[0][0]['bank'],pair[0][0]['dest'],pair[1][0]['bank'],pair[1][0]['dest']]
   counts[name]=dict(cases=len(values),CPU_delta=[min(values),max(values)])
   print(name,counts[name],flush=True)
  # Every current ingress/table index, all selectors, both Rogue domains.
  values=[]
  for raw in range(256):
   if raw==25:continue
   for index,name in enumerate(entries):
    for rd in([0,1]if raw==2 else[0]):
     pair=[T.endpoint(T.fork(q),name,raw,32 if raw==9 else 0,249,rd)for q in[aa,bb]]
     delta,relocated,label=same(*pair,[raw,name,rd]);values.append(delta)
     if relocated:moved[label]=[pair[0][0]['bank'],pair[0][0]['dest'],pair[1][0]['bank'],pair[1][0]['dest']]
  counts['all_foreign_ingresses']=dict(cases=len(values),CPU_delta=[min(values),max(values)])
  # Each first15 + Only16 public service caller, all64 status flags.
  values=[]
  for i,name in enumerate(entries):
   for p in FLAGS:values.append(own(bb,name,i,p))
  counts['actual_S2_service_delivery']=dict(cases=len(values),CPU_range=[min(values),max(values)])
  result.update(passed=True,checks=counts,real_relocated_callback_identities=moved,all_other_application_ordered_writes_SMC_live_page1_WRAM_CHR_exact=True)
 except Exception as e:result.update(error=repr(e),traceback=traceback.format_exc(),partial_checks=counts)
 result['bindings']={str(p.resolve()):B.sha(p)for p in[Path(__file__),Path(T.__file__),P/'candidate.nes',P/'candidate.dbg',N/'candidate.nes',N/'candidate.dbg',B.O/'source-stage.json']}
 (O/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='bindings'}));assert result['passed'],result.get('error')
if __name__=='__main__':main()
