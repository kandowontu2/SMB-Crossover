"""Actual lossless backing measurement for149; no ROM or shared admission."""
from pathlib import Path
import json,sys
from types import SimpleNamespace
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_strike_manifest_1103_v130 as C
O=C.O


def main():
 source=R/'tools/audit/prepare_prince_cold_link_1102_v44.py';text=source.read_text()
 changes={'import prepare_prince_successor_manifest_1102_v26 as M':'import prepare_prince_strike_manifest_1103_v130 as M','POOL=M.POOL+[514]':'POOL=M.M.POOL','base,_,_,_=M.bundle()':'base,_=M.parent()','native-runtime-v42.bin':'native-runtime-v149.bin','native-metadata-v42.bin':'native-metadata-v149.bin','native-state_code-v18.bin':'native-state-v149.bin','0xc100,0xc400':'0xc100,0xc300','M.A.PIN':'M.PIN','M.A.BASE':'M.BASE','v44':'v150'}
 for a,z in changes.items():assert a in text,a;text=text.replace(a,z)
 env=dict(__file__=str(Path(__file__)),__name__='prince_live_backing_v150');exec(compile(text,str(source),'exec'),env);env['main']()
 (O/'cold-worker-v150.o').unlink()
 path=O/'cold-link-storage-v150.json';q=json.loads(path.read_text());assert q['passed']and q['physical_pages']==44 and q['physical_spare']>0
 q.update(private_source_measurement_only=True,existing_grants_not_extended=True,source_runtime_version=149,metadata_end=0xdfcc,state_staged_extra_half_open=[0xc6f9,0xc72e],required_execution_amendment='New live53B in formercoldBFA3..BFD8 only after finalizer returns;53B coldpacketC200..C235 between fullycopied sourcecode and native constructor, copied/readback/cleared before header publication; shared149 alternative funding and complete readers/lifecycle/ISR proof required. No ROM emitted.')
 q['bindings'].update({p.relative_to(R).as_posix():C.M.sha(p.read_bytes())for p in [Path(__file__),source,O/'live-policies-measurement-v149.json',O/'native-labels-v149.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
