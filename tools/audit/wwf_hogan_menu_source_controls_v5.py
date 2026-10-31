"""All current menus and actual funded Start masks, private Hogan only."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import benj_all_menu_controls_1030_v1 as B
import bowser_split_loader_controls_v1 as T
from link_pit_rygar_sophia_audit_cpu import scoped_load
J=R/'build/wwf-hogan-natural-source-v15/joint';P=R/'build/contra-force-world-roles-1031-v2/joint';O=R/'build/wwf-hogan-menu-source-controls-v5'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,native=False,installed=False)
 try:
  B.A.COUNTS[16]=4;B.A.COUNTS[23]=2
  old,new=[B.collect(p,True)for p in[P,J]]
  assert len(new)==len(old)==86
  for k,row in old.items():
   if k!=(28,0):assert row==new[k],('Current foreign menu/name/Start',k,row,new[k])
  assert old[28,0]['pending']and not new[28,0]['pending']and new[28,0]['raw']==29
  assert all(new[28,v]['pending']for v in range(1,6))
  assert sum(not r['pending']for r in new.values())==75
  seed=T.make(scoped_load(J/'candidate.nes'),SelectedCharacter=0);count=0
  for slot,flags in itertools.product(range(32),range(64)):
   m=T.fork(seed);T.H.put(m,FmAlts=255,FmGroups=255)
   p=T.flags(flags);c,low=T.call(m,'FmStartFlags',x=slot,a=85,y=99,p=p)
   assert(c.a,c.x,c.y,c.p,c.sp)==(0,slot,99,(p&125)|2,224)
   assert T.H.get(m,'FmAlts')=={9:32,10:68,26:8,31:128}.get(slot,0)
   assert T.H.get(m,'FmGroups')=={23:32,28:7,30:24}.get(slot,0)
   count+=1
  q.update(passed=True,candidate=sha(J/'candidate.nes'),profiles=len(new),private_ready=75,public_admission=False,all_prior74_and_other5_WWF_pending_exact=True,actual_Start_A_boundaries=688,Start_masks_all64flags=count,rows=list(new.values()))
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(B.__file__),Path(T.__file__),J/'candidate.nes',J/'candidate.dbg',J.parent/'source-stage.json',P/'candidate.nes',P/'candidate.dbg',R/'build/future-start-masks-1031-v1/joint/src/cf_menu_body.inc']}
  (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q.get(k)for k in['passed','candidate','profiles','private_ready','Start_masks_all64flags','error']}))
if __name__=='__main__':main()
