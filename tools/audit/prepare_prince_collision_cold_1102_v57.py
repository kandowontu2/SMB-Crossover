"""Measure proposed collision code/backing in the existing44 physical carriers."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_sunny_rebase_1102_v54 as M
O=M.O


def main():
 source=R/'tools/audit/prepare_prince_cold_link_1102_v44.py';text=source.read_text();changes={
  'import prepare_prince_successor_manifest_1102_v26 as M':'import prepare_prince_sunny_rebase_1102_v54 as M',
  'POOL=M.POOL+[514]':'POOL=M.P.M.POOL+[514]',
  'native-runtime-v42.bin':'native-runtime-v49.bin',
  'native-metadata-v42.bin':'native-metadata-v49.bin',
  'native-state_code-v18.bin':'native-state-v49.bin',
  '0xc100,0xc400':'0xc100,0xc300',
  'v44':'v57','M.A.PIN':'M.PIN','M.A.BASE':'M.BASE',
 }
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 env=dict(__file__=str(source),__name__='prince_collision_cold_v57');exec(compile(text,str(source),'exec'),env);env['main']()
 file=O/'cold-link-storage-v57.json';q=json.loads(file.read_text());assert q['passed']
 q.update(private_proposal_only=True,new_execution_granted=False,qualified_fixture_SHA256=hashlib.sha256(text.encode()).hexdigest(),required_execution_amendment=dict(source_dead_audio=[0xc780,0xc800],cold_staged_prefix_PC=[0xc65f,0xc678],original_dead_renderer_tail=[0xbd3e,0xbd4b],live_metadata_extension=[0xdfa2,0xdfce]),scope='Current16a9 source measurement only: original31072B art unchanged,44 existing granted physical carriers, lossless v49 runtime/6094B metadata/1503B state-and-audio backing fit. Three exact instruction decoder outputs preserve unread staging bytes. New live audio/staged-prefix/small-renderer-tail/metadata extension execution is ungranted; actual complete cold/Fresh/auth/retirement/native play still required.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'collision-services-measurement-v49.json',O/'collision-services-CPU-v56.json',O/'quiet-audio-code-proposal-v48.json',O/'sunny-rebase-manifest-v54.json']});file.write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps({k:q[k]for k in ['passed','payload_bytes','physical_spare','source_art_bytes','decoder_bytes','worker_storage_bytes','decoded_images','required_execution_amendment']}))


if __name__=='__main__':main()
