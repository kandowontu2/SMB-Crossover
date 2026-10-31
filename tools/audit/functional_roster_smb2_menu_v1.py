"""Execute every actual current menu identity and launch-prefix ABI."""
from pathlib import Path
import inspect,json,traceback
import arthur_quick_functional_admission_v1 as A
import prepare_functional_roster_smb2_v1 as B
O=B.O/'menu-controls';A.O=O;A.P=B.P;A.N=B.N
s=inspect.getsource(A.menus)
s=s.replace("(slot,variant)in[(9,2),(31,0)]","slot==24")
s=s.replace("ready==[52,54]","ready==[54,58]")
s=s.replace("[[9,2,9,'Quick Man'],[31,0,32,'Arthur']]","[[24,i,25,n]for i,n in enumerate(['SMB2 Mario','SMB2 Luigi','SMB2 Toad','SMB2 Peach'])]")
exec(compile(s,__file__,'exec'),A.__dict__)
def main():
 assert not O.exists();O.mkdir();d=dict(passed=False,native=False)
 try:
  q=A.menus();d.update(passed=True,profiles=q['profiles'],ready=q['ready_counts'],Start_A_all64flags=q['source_input_cases'])
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc())
 d['bindings']={str(p.resolve()):B.sha(p)for p in[Path(__file__),Path(A.__file__),B.P/'candidate.nes',B.P/'candidate.dbg',B.N/'candidate.nes',B.N/'candidate.dbg']}
 (O/'result.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items()if k!='bindings'}));assert d['passed'],d.get('error')
if __name__=='__main__':main()
