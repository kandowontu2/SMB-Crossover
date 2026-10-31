"""Actual cold portrait selection and unchanged source gameplay records."""
from pathlib import Path
import json,traceback
import prepare_goku_portrait_facing_source_v1 as B
import current_quick_transport_controls_v4 as T
C=T.C;S=T.S;R=B.R;P=B.P;O=R/'build/goku-portrait-facing-source-v3'

def bus(path):
 old=C.O;C.O=path
 try:return C.Bus()
 finally:C.O=old

def main():
 out=O/'portrait-controls.json';assert not out.exists();d=dict(passed=False,native=False);rows=[];graphics=[]
 try:
  templates=[bus(p)for p in [P,O]]
  for mode in [0,1]:
   for flags in [p for p in range(256)if p&48==48]:
    pair=[]
    for which,t in enumerate(templates):
     m=S.clone(t);m.set('SelectedCharacter',24);m.set('OperMode',mode)
     regs,cy,sp=S.execute(m,'DpAdmissionPortrait',A=131,X=90,Y=199,P=flags)
     assert m.get('DpRenderIndex')==which
     # Source record table is genuinely mapped by DpGraphicsBank.
     expected=m[m.lab['DpPoseLo']+which]+256*m[m.lab['DpPoseHi']+which]
     pointer=m.get('SmPosePtr')+256*m.ram[m.lab['SmPosePtr']+1]
     assert pointer==expected and m.get('ObjectMetasprite')==m.lab['METASPRITE_SAMUS_BODY']
     pair.append(dict(record=which,descriptor=pointer,registers=regs,CPU=cy,minimumSP=sp))
    rows.append(dict(OperMode=mode,flags=flags,old=pair[0],new=pair[1]))
  for pose in range(32):
   for face in [0,64]:
    pair=[]
    for t in templates:
     m=S.clone(t);m.set('SelectedCharacter',24);m.set('OperMode',1)
     S.execute(m,'DpEnsure');m.set('DpPose',pose);m.set('DpAttribute',face);m.set('DpProtection',0)
     regs,cy,sp=S.execute(m,'DpGraphics',A=131,X=90,Y=199,P=0xf9)
     pair.append((regs,cy,sp,bytes(m.ram),m.tags,m.wram,m.chr,m.writes))
    assert pair[0]==pair[1],('all source moving pose outputs unchanged',pose,face)
    graphics.append(dict(pose=pose,attribute=face,record=pose*2+(face>>6),CPU=pair[0][1]))
  d.update(passed=True,actual_cold_portraits_all64flags=len(rows),all32poses_bothsourcefacings_exact=len(graphics),rows=rows,gameplay=graphics,scope='Actual genuine cold/lives DpAdmissionPortrait and DpGraphics workers through FarCallCommon. No nativePPU or movement/attack rewrite. Source geometry/RGB witness is in source-proof.json.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc())
 d['bindings']={str(p.resolve()):B.sha(p)for p in [Path(__file__),O/'candidate.nes',O/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg',O/'source-proof.json']}
 out.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items()if k not in ['bindings','rows','gameplay','traceback']}));assert d['passed'],d.get('error')
if __name__=='__main__':main()
