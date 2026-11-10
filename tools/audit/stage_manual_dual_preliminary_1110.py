"""Stage private native tests while independent interrupt qualification runs."""
import argparse,json,hashlib,subprocess,sys
from pathlib import Path
import check_manual_dual_platform_1110 as D
R=D.R;BASE=R/'build/getsu-fast-head-native-1110/candidate.nes'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
 assert out.is_relative_to(R/'build') and not out.exists();qpath=D.OUT/'proof.json';q=json.loads(qpath.read_text())
 assert q['passed'] and q['source_CPU_only'] and not q['ROM_written']
 for name,h in q['bindings'].items():assert sha(R/name)==h,name
 old=D.BASE.read_bytes();current=BASE.read_bytes();assert hashlib.sha256(old).hexdigest()==q['parent_SHA256']
 used=set()
 for row in q['patches']:
  at=row['file_offset'];pre=bytes.fromhex(row['old_hex']);extent=set(range(at,at+len(pre)))
  assert not used&extent and old[at:at+len(pre)]==current[at:at+len(pre)]==pre;used|=extent
 image=D.P.install(current,q['patches']);digest=hashlib.sha256(image).hexdigest()
 assert all(x==y for i,(x,y) in enumerate(zip(current,image)) if i not in used)
 result=q|dict(parent_SHA256=sha(BASE),expected_memory_only_SHA256=digest,
   interrupt_qualification_pending=True,native_tests_pending=True,
   scope='Private native test setup only. Independent IRQ closure and final current-lineage CPU rebase are still required before delivery.',
   bindings=q['bindings']|{str(p.relative_to(R)):sha(p) for p in (Path(__file__).resolve(),qpath,BASE)})
 out.mkdir();proof=out/'preliminary.json';proof.write_text(json.dumps(result,indent=2)+'\n')
 rom=out/'candidate.nes';rom.write_bytes(image)
 subprocess.run([sys.executable,'-B',str(R/'tools/audit/prepare_manual_dual_native_1110.py'),'--output',str(out/'native'),
                 '--rom',str(rom),'--proof',str(proof)],check=True)
 print('Private native test candidate, IRQ qualification pending:',digest,flush=True)

if __name__=='__main__':main()
