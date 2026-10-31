from pathlib import Path
import sys,json,traceback,hashlib
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bowser_gameplay_component_controls_v2 as C
from check_tmnt_render_oa import load,address
T=C.T;H=C.H
J=R/'build/bowser-playable-jump-v1/joint';O=R/'build/bowser-playable-body-geometry-v1'
def record(m,a,ram=False):
 if ram:src=m.ram[3];at=a&8191
 else:src=m;at=a
 return [list(src[i:i+4])for i in range(at+1,at+1+src[at],4)]
def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,source_CPU=True,native=False,rows=[])
 try:
  b=load(J/'candidate.nes')
  for form in [0,8]:
   m=T.make(b,FmAlts=form,CurrentPlayer=0);T.call(m,'BwLoad');C.rc(m,'BwConstruct')
   for pose in range(4 if form else 9):
    for face in [1,2]:
     m.ram[3][0x1e16]=pose;H.put(m,PlayerFacingDir=face);C.rc(m,'BwGraphics');got=record(m,0xbe40,True)
     if form:
      name=['OPEN1','OPEN2','CLOSED1','CLOSED2'][pose]+('RIGHT'if face==1 else'LEFT');base=address(b,'Bw1'+name);expected=record(m,base,True)
      expected=[[a,f,(y-8)&255,(x-8)&255]for a,f,y,x in expected]
     else:
      base=address(b,'Bw3Pose'+str(pose));expected=record(m,base,True)
      expected=[[a,f^(64 if face==1 else 0),(y-16)&255,((16-x)if face==1 else x)&255]for a,f,y,x in expected]
     q['rows'].append(dict(form=form,pose=pose,face=face,expected=expected,actual=got))
     assert sorted(got)==sorted(expected),('actual full native-record geometry',form,pose,face)
  q['passed']=True
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest()for p in[Path(__file__),J/'candidate.nes',J/'candidate.dbg',J/'bowser.bin']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=q['passed'],error=q.get('error'))));assert q['passed']
if __name__=='__main__':main()
