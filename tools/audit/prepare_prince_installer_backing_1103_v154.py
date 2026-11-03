"""Lossless153 runtime/state plus149 metadata, all44 existing carriers."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_strike_manifest_1103_v130 as C
O=C.O


def main():
 source=R/'tools/audit/prepare_prince_cold_link_1102_v44.py';text=source.read_text();changes={'import prepare_prince_successor_manifest_1102_v26 as M':'import prepare_prince_strike_manifest_1103_v130 as M','POOL=M.POOL+[514]':'POOL=M.M.POOL','base,_,_,_=M.bundle()':'base,_=M.parent()','native-runtime-v42.bin':'native-runtime-v153.bin','native-metadata-v42.bin':'native-metadata-v149.bin','native-state_code-v18.bin':'native-state-v153.bin','0xc100,0xc400':'0xc100,0xc300','M.A.PIN':'M.PIN','M.A.BASE':'M.BASE','v44':'v154'}
 for a,z in changes.items():assert a in text,a;text=text.replace(a,z)
 env=dict(__file__=str(Path(__file__)),__name__='prince_installer_backing_v154');exec(compile(text,str(source),'exec'),env);env['main']()
 for suffix in ['o','cfg','lbl']:(O/('cold-worker-v154.'+suffix)).unlink()
 path=O/'cold-link-storage-v154.json';q=json.loads(path.read_text());assert q['passed']and q['physical_spare']>0
 q.update(private_source_proposal=True,shared_and_execution_grant_required=True,runtime_version=153,metadata_version=149,state_bytes=1607,required_execution_amendment='Live53B formerfinalizer BFA3..BFD8 only after finalizer return; C766..C77F coldprefix overwritten by25B installer only after original prefix JMP has returned, installer executes only from resident continuation under authentic forcedblank/SEI/invalidheaders; stageC200..C235 zero before headerpublish. No ROM/native admission.')
 q['bindings'].update({p.relative_to(R).as_posix():C.M.sha(p.read_bytes())for p in [Path(__file__),source,O/'live-installer-measurement-v153.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
