"""Current-hash menu/cold/Chip selector checks; no native or source edits."""
from pathlib import Path
import json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import arthur_quick_functional_admission_v1 as A
import prepare_functional_roster_ready54_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address,location
O=B.O/'controls';N=B.N
def main():
 assert not O.exists();O.mkdir();d=dict(passed=False,native=False,candidate=B.sha(N/'candidate.nes'))
 try:
  A.N=N;A.O=O
  menu=A.menus();d['menu']=dict(profiles=menu['profiles'],ready_counts=menu['ready_counts'],input_cases=menu['source_input_cases'])
  # Reuse the frozen genuine post-Ic/forced-blank consumer sequence on the
  # actual new cart. Its explicit native Select-C-publication ABI remains.
  source=R/'tools/audit/arthur_quick_functional_cold_v1.py';s=source.read_text()
  old="'QueueSelection','InitializeArea'";assert s.count(old)==1
  s=s.replace(old,"'QueueSelection','CrossoverMenuInput','InitializeArea'")
  exec(compile(s,str(source),'exec'),dict(__name__='__main__',__file__=str(source)))
  cold=json.loads((O/'cold/actual-cold-chains.json').read_text());assert cold['passed']
  d['actual_cold']=dict(Arthur_and_Quick=True,post_Ic_exactly_once=True,full16cookie=True,native_entrance8=True)
  b=scoped_load(N/'candidate.nes');rows=[]
  for pose in range(60):
   for face in [1,2]:
    q=Arena(b,14);bank=(location(b,'CdArtBegin')-16)//8192;q.m.page(2,bank);q.set('CurrentBankC',bank|128)
    q.put(PlayerFacingDir=face,Player_Rel_XPos=104);c,w=q.invoke('CdSetPose',x=pose)
    label=f'CdPose{pose}'+('Left'if face==1 else'Right')
    ptr=q.get('SmPosePtr')+256*q.get('SmPosePtr',1)
    assert ptr==address(b,label)and q.get('CdPose')==pose and q.get('PlayerFacingDir')==face and q.get('Player_Pos_ForScroll')==104 and c.sp==0xfd
    rows.append(dict(pose=pose,facing=face,record=label,pointer=ptr))
  d.update(passed=True,actual_Cd_selector_cases=120,Cd_cases=rows)
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc())
 d['bindings']={str(p.resolve()):B.sha(p)for p in[Path(__file__),Path(A.__file__),R/'tools/audit/arthur_quick_functional_cold_v1.py',N/'candidate.nes',N/'candidate.dbg',B.O/'source-proof.json']+list(O.rglob('*.json'))}
 (O/'controls.json').write_text(json.dumps(d,indent=2)+'\n',newline='\n');print(json.dumps({k:v for k,v in d.items()if k not in['bindings','Cd_cases']}));assert d['passed'],d.get('error')
if __name__=='__main__':main()
