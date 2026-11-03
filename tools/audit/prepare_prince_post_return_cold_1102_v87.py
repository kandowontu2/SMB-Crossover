"""Measure final post-return source/code backing in the same44 carriers."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_sunny_rebase_1102_v54 as M
O=M.O


def main():
 source=R/'tools/audit/prepare_prince_cold_link_1102_v44.py';text=source.read_text();changes={
  'import prepare_prince_successor_manifest_1102_v26 as M':'import prepare_prince_sunny_rebase_1102_v54 as M',
  'POOL=M.POOL+[514]':'POOL=M.P.M.POOL+[514]',
  'native-runtime-v42.bin':'native-runtime-v78.bin',
  'native-metadata-v42.bin':'native-metadata-v78.bin',
  'native-state_code-v18.bin':'native-state-v78.bin',
  '0xc100,0xc400':'0xc100,0xc300',
  'v44':'v87','M.A.PIN':'M.PIN','M.A.BASE':'M.BASE',
 }
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 env=dict(__file__=str(Path(__file__)),__name__='prince_postreturn_cold_v87');exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'cold-link-storage-v87.json';q=json.loads(path.read_text());q.update(private_measurement_only=True,all44_carriers_unchanged=True,source_art_unchanged=True,requested_new_live_audio=[0xc766,0xc780],requested_new_staged_PC=[0xc678,0xc67a],metadata_end=0xdfcf,clock_untouched=[0xdfd0,0xdfd3],required='Root lifetime/hook/SMC review; actual changed cold prefix/reset/constructor readback and every source-live zero; current exact cookie/typedmanager carry fix/rebase/foreign cold before native.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,O/'post-return-measurement-v78.json',O/'tag-transport-CPU-v84.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
