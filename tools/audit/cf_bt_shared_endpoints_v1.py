"""Actual current66 public/Only endpoints: CF joins without foreign ABI changes."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_transport_controls_v1 as T
import battletoads_only_transport_controls_v1 as F
H=T.H;L=T.L;address=T.address
P=R/'build/bowser-playable-jump-v1/joint';J=R/'build/cf-bt-shared-transport-v3/joint'
O=R/'build/cf-bt-shared-endpoints-v1';sha=T.sha
def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,source_CPU=True,native=False)
 try:
  bundles=[H.C.qualified(p/'candidate.nes')for p in[P,J]];pair=[L.make(b)for b in bundles]
  deltas=[];members=rawpairs=onlypairs=cfpairs=0
  for raw,rd in[(0,0),(28,0),(24,0),(2,1)]:
   for slot,p in itertools.product(range(36),T.FLAGS):
    rows=[]
    for m in pair:T.reset(m,raw,rd);rows.append(T.endpoint(m,slot,p)[0])
    deltas.append(F.same(*rows,*pair,[raw,rd,slot,p]));members+=1
  for raw,slot,p in itertools.product([x for x in range(256)if x!=31],range(36),[T.FLAGS[0],T.FLAGS[-1]]):
   for rd,alt in([(0,0),(1,0),(255,0)]if raw==2 else[(0,0),(0,32)]if raw==9 else[(0,0)]):
    rows=[]
    for m in pair:T.reset(m,raw,rd,alt);rows.append(T.endpoint(m,slot,p)[0])
    deltas.append(F.same(*rows,*pair,[raw,rd,alt,slot,p]));rawpairs+=1
  for raw,name in itertools.product(range(256),F.ONLY):
   flags=T.FLAGS if name in['GmFreshGate','GmColorsGate']else[T.FLAGS[0],T.FLAGS[-1]]
   for p in flags:
    for rd,alt in([(0,0),(1,0),(255,0)]if raw==2 else[(0,0),(0,32)]if raw==9 else[(0,0)]):
     rows=[]
     for m in pair:T.reset(m,raw,rd,alt);rows.append(F.endpoint(m,name,p)[0])
     if raw!=31:deltas.append(F.same(*rows,*pair,[raw,name,p,rd,alt]));onlypairs+=1
     else:
      i=F.ONLY.index(name)+15;z=rows[1]
      assert(z['target'],z['bank'])==(address(pair[1].bundle,'BtServiceVeneers')+3*i,215)
      assert z['AXYP_SP'][:4]==[0x83,0x5a,0xc7,(p&~0x82)|0x80];cfpairs+=1
  m=pair[1]
  for slot,p in itertools.product(range(36),T.FLAGS):
   T.reset(m,31);z,c=T.endpoint(m,slot,p)
   assert(z['target'],z['bank'])==(address(m.bundle,'BtServiceVeneers')+slot*3,215)
   assert z['AXYP_SP'][:4]==[0x83,0x5a,0xc7,(p&~0x82)|0x80];cfpairs+=1
  for index,p in itertools.product([36,37,127,255],T.FLAGS):
   T.reset(m,31);z,c=T.endpoint(m,0,p,forced_index=index)
   assert(z['target'],z['bank'])==(address(m.bundle,'BtServiceUnavailable'),215);cfpairs+=1
  q.update(passed=True,all144_members_full64flag_pairs=members,all256raw_foreign_Quickalt_pairs=rawpairs,
   all16Only_actual_foreign_pairs=onlypairs,CF_only_public_invalid_cases=cfpairs,
   all_AXYP_SP_33SMC_maps_livepage1_orderedwrites_exact=True,foreign_CPU_delta=[min(deltas),max(deltas)],
   scope='True public entry to real SFC worker endpoint. CF remains pending; no natural loader/lifecycle claim.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(T.__file__),Path(F.__file__),J/'candidate.nes',J/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg',J/'union.s',J/'src/new_roster_dispatch.s',J/'source-stage.json']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}));assert q['passed']
if __name__=='__main__':main()
