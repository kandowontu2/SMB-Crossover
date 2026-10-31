"""Actual unchanged86 menu pairs and10240 Start masks on CF publisher child."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import contra_force_menu_admission_controls_1031_v4 as M
from prepare_ff_current_component_v2 import qualified
P=R/'build/contra-force-world-chr-publisher-1031-v1';OLD=R/'build/contra-force-scroll-publisher-1031-v2'
O=R/'build/contra-force-world-chr-menu-controls-1031-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,source_CPU=True,native=False,rows=[])
 try:
  old,new=[qualified(p/'joint/candidate.nes')for p in(OLD,P)];ready=[0,0]
  for slot,count in enumerate(M.COUNTS):
   pair=[]
   for b in(old,new):
    m=M.C.fresh(b,0);M.H.put(m,CrossoverMenuIndex=slot,FfVariant=0,FmAlts=0)
    M.C.invoke(m,'MenuResolveCharacter');M.C.invoke(m,'QueueSelection');pair.append(m)
   for variant in range(count):
    if variant:
     for m in pair:
      M.H.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0);M.C.invoke(m,'CrossoverMenuInput')
    got=[]
    for i,m in enumerate(pair):
     z=M.C.invoke(m,'FmPending');a=z['AXYP_SP'];pending=a[3]&1
     got.append(dict(selected=M.H.get(m,'SelectedCharacter'),A=a[0],P=a[3],pending=pending,**M.snapshot(m)));ready[i]+=not pending
    assert got[0]==got[1],(slot,variant,got)
    q['rows'].append(dict(slot=slot,variant=variant,selected=got[1]['selected'],name_index=got[1]['A'],pending=got[1]['pending']))
  assert len(q['rows'])==86 and ready==[74,74]
  q.update(Start=M.start(new),passed=True,actual_menu_pairs=86,ready_counts=ready,
    scope='Menu/Start exact source consumers only; inherited menu factory seed96 is irrelevant to this byte-paired frontend scope and is not used as cold scrolling evidence.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(M.__file__),P/'source-stage.json',P/'joint/candidate.nes',P/'joint/candidate.dbg',OLD/'source-stage.json',OLD/'joint/candidate.nes',OLD/'joint/candidate.dbg']}
  p=O/'controls.json';p.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(path=str(p),passed=q['passed'],sha256=sha(p),menus=len(q['rows']),Start=q.get('Start'),error=q.get('error')),indent=2),flush=True)
if __name__=='__main__':main()
