"""Actual source-classifier target/ABI proof; declared transport effects retained."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_transport_controls_v1 as T
import battletoads_only_transport_controls_v1 as F
L=T.L;H=T.H;V=T.V;address=T.address
P=R/'build/thomas-physical-host-1031-v9';J=R/'build/thomas-private-ingress-1031-v5';O=R/'build/thomas-ingress-endpoints-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
NAMES=['NrMovement','NrGraphics','NrDraw','NrPortrait','NrWeapons','NrInjury','NrLegacyInjuryStatus','NrDeathStart','NrDeath','NrVisible','NrHead','NrBody','NrAdder','NrBox','NrSide']
def endpoint(m,name,p,hook=None):
 c=H.start(m,name,a=0x83,x=0x5a,y=0xc7,p=p,sp=224);smc=address(m.bundle,'FarcallJmpTarget_SMC');hu=address(m.bundle,'HuEntryBase');seen=False;low=c.sp
 for step in range(3500):
  if hook:hook(m,c,step)
  low=min(low,c.sp)
  if c.pc==smc:
   dest=m[smc+1]|m[smc+2]<<8
   internal=m.rawtags[1]==207 and hu<=dest<hu+576
   helper=m.rawtags[1]==213 and dest==address(m.bundle,'ThArExtended')
   if seen and not(internal or helper):return dict(target=dest,bank=m.rawtags[1],regs=(c.a,c.x,c.y,c.p,c.sp),CPU=c.processorCycles,minimumSP=low),c
   seen=True
  assert m[c.pc]!=0,(name,hex(c.pc),m.rawtags)
  c.step()
 raise AssertionError(('endpoint bound',name,hex(c.pc)))
def main():
 assert not O.exists();O.mkdir(parents=True);q=dict(passed=False,native=False)
 try:
  stage=json.loads((J/'source-stage.json').read_text())
  for p,h in stage['bindings'].items():assert sha(p)==h,p
  bs=[H.C.qualified(x/'candidate.nes')for x in[P,J]];pair=[L.make(b)for b in bs];count=0;own=0;ds=[];smcdiff={};mapperdiff={}
  oldhead=address(bs[0],'GmHeadWithinOwn');newhead=address(bs[1],'ThGmHeadWithinOwn')
  def check(name,raw,alt,p,rd=0):
   nonlocal count,own
   zs=[]
   for m in pair:T.reset(m,raw,rd,alt);zs.append(endpoint(m,name,p)[0])
   a,z=zs
   if raw==10 and alt&68==64:
    slot=(NAMES.index(name)if name in NAMES else F.ONLY.index(name)+15)if not name.startswith('Hu')else T.ROWS.index(name[2:])
    assert(z['target'],z['bank'])==(address(bs[1],'ThServiceVeneers')+3*slot,213),(name,slot,z)
    assert z['regs']==(0x83,0x5a,0xc7,(p&~130)|128,217),('Thomas live sourceABI',name,p,z)
    own+=1;return
   expected=(newhead,213)if(a['target'],a['bank'])==(oldhead,252)else(a['target'],a['bank'])
   assert(z['target'],z['bank'])==expected,('foreign target',name,raw,alt,p,a,z,expected)
   assert a['regs']==z['regs'],('foreign live AXYP/SP',name,raw,alt,p,a,z)
   assert pair[0].rawtags[2:]==pair[1].rawtags[2:] and pair[0].ram==pair[1].ram,('foreign C/RAM payload',name,raw,alt,p)
   # Only actual transport registers/SMC may differ; keep and count their
   # exact changed values. Application writes retain original ordered identity.
   app=lambda m:[(a,v)for a,v in m.writes if not(0x100<=a<0x200 or a in[0x5115,0x5116])]
   assert app(pair[0])==app(pair[1]),('ordered application writes',name,raw,alt,p,app(pair[0]),app(pair[1]))
   differing=tuple(i for i in range(0x15a,0x17b)if pair[0][i]!=pair[1][i])
   if differing:smcdiff[str((raw,name))]=[hex(i)for i in differing]
   maps=lambda m:[(a,v)for a,v in m.writes if a in[0x5115,0x5116]]
   if maps(pair[0])!=maps(pair[1]):mapperdiff[str((raw,name))]=[len(maps(pair[0])),len(maps(pair[1]))]
   ds.append(z['CPU']-a['CPU']);count+=1
  # Every actual public service covers all raw owner values at both flag
  # extremes, then all64 flags for each admitted family/variant boundary.
  names=['Hu'+n for n in T.ROWS]+F.ONLY+NAMES
  for name in names:
   for raw,p in itertools.product(range(256),[48,255]):check(name,raw,0,p)
   for raw,alt,rd in[(2,0,1),(9,32,0),(10,4,0),(10,64,0),(10,68,0),(22,0,0),(24,0,0),(25,0,0),(26,0,0),(27,0,0),(28,0,0),(31,0,0),(32,0,0),(33,0,0)]:
    for f in range(64):check(name,raw,alt,L.flags(f),rd)
   print(name,count,own,flush=True)
  q.update(passed=True,foreign_target_liveABI_pairs=count,Thomas_true_row_pairs=own,all256raw=True,all64flags_each_active_family_and_variant_boundary=True,CPU_delta=[min(ds),max(ds)],transport_SMC_differences=smcdiff,mapper_write_count_differences=mapperdiff,
   limits=['Strict actual target/liveAXYP/SP/orderedapplication-write comparison; transportSMC and mapper traces are disclosed separately','This is entry-to-real-child proof, not natural cold/Main or readiness','Arthur helper adds genuine farcall; its returnedA temporarily changes SafereturnA until real native callback overwrites it'])
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p):sha(p)for p in[Path(__file__),Path(T.__file__),Path(F.__file__),J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg']}
 dump(O/'controls.json',q);print(json.dumps({k:v for k,v in q.items()if k not in['bindings','traceback','transport_SMC_differences','mapper_write_count_differences']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
