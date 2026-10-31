"""Established legal47-identity Main suite on exact old/new Bowser source."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import quickman_wram_palette_controls_v6 as C
U=C.H.U
J=R/'build/cf-cold-warm-source-v3/joint';P=R/'build/cf-owner-retirement-v2/joint';O=R/'build/cf-cold-warm-foreign-main-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,source_CPU=True)
 oldload=U.scoped_load;old=oldload(P/'candidate.nes')
 def loader(p):return old if Path(p)==R/'build/pit-retold-host-v3/candidate.nes'else oldload(p)
 U.scoped_load=loader
 try:q.update(U.foreign(oldload(J/'candidate.nes')),passed=True)
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 finally:U.scoped_load=oldload
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(U.__file__),J/'candidate.nes',J/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['rows','bindings']}));assert q['passed']
if __name__=='__main__':main()
