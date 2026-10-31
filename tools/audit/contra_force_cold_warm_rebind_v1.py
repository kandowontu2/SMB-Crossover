"""Narrow own lifecycle APIs rebound to genuine sibling cold/warm joined source."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import contra_force_lifecycle_controls_v4 as Q
J,C,T,D=Q.J,Q.C,Q.T,Q.D;P=R/'build/cf-cold-warm-source-v3';O=R/'build/contra-force-cold-warm-rebind-v1'
Q.P=Q.V.P=J.P=C.P=T.P=D.P=P;T.B=T.qualified(P/'joint/candidate.nes');T.PAYLOAD=(P/'joint/cf-stream.bin').read_bytes();T.COOKIE=(P/'joint/cf-cookie.bin').read_bytes()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();out=dict(passed=False,native=False,natural_cold_owned_by_sibling=True,checks={})
 try:
  stage=json.loads((P/'source-stage.json').read_text())
  for p,h in stage['bindings'].items():assert sha(p)==h,p
  assert sha(P/'joint/candidate.nes')=='8f0a925be0f1845952583a28dac7b54dd716c35539cfd65a13df37a7f9cdb310'
  old=R/'build/contra-force-lifecycle-cart-v4/joint'
  for n in ['cf-stream.bin','cf-cookie.bin']:assert (P/'joint'/n).read_bytes()==(old/n).read_bytes(),n
  bases=[Q.load(v)for v in range(4)]
  for n,f in [('warm_and_actual1up',Q.warm),('actual_native_life_player',Q.native_lives),('reset_once_all_flags',Q.reset),('source_draw_UI',Q.presentation)]:
   out['checks'][n]=f(bases);print('CF cold/warm own rebind',n,'PASS',flush=True)
  out['passed']=True
 except Exception as e:out.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  files=[Path(__file__),Path(Q.__file__),P/'source-stage.json',P/'joint/candidate.nes',P/'joint/candidate.dbg',P/'joint/cf-stream.bin',P/'joint/cf-cookie.bin',R/'build/contra-force-lifecycle-qualified-v1/handoff.json']
  out['bindings']={str(p.resolve()):sha(p)for p in files};p=O/'controls.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=out['passed'],error=out.get('error'))),flush=True)
if __name__=='__main__':main()

