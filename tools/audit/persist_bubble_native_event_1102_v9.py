"""Preserve only the reviewed compact v9 checkpoint, without Git operations."""
import json,shutil
from pathlib import Path
import check_bubble_native_event_1102_v9 as E
P=E.P;R=E.R;O=E.O


def main():
 freeze=O/'native-event-v9-qualified.json';q=json.loads(freeze.read_text());archive=R/q['archive'];manifest=R/q['manifest']
 assert q['passed']and q['archive_bytes']==43057
 assert P.sha(archive.read_bytes())=='62a9b8596ab79b7894c4bc241f9a7e212b540892cea39ce25817b5651380ff81'
 assert P.sha(manifest.read_bytes())=='d2f1b54209812d6aca14d1eb0cbe234a3cf0bff93fad18445d189d0a00fa45dc'
 for rel,z in q['files'].items():assert P.sha((R/rel).read_bytes())==z['SHA256'],rel
 dest=R/'docs/qa/checkpoints/2026-11-02/bubble-native-event-v9';dest.mkdir(parents=True,exist_ok=True)
 files=[]
 for src,name in[(archive,'inputs.zip'),(freeze,'source-freeze.json'),(manifest,'proposal.json')]:
  out=dest/name
  if out.exists():assert out.read_bytes()==src.read_bytes(),name
  else:shutil.copyfile(src,out)
  assert out.read_bytes()==src.read_bytes();files.append(dict(path=out.relative_to(R).as_posix(),SHA256=P.sha(out.read_bytes()),bytes=out.stat().st_size))
 result=dict(passed=True,Git_operations=False,ROM_written=False,files=files,source_files=q['source_files'],persist_recipe=Path(__file__).relative_to(R).as_posix(),scope='Byte-exact compact checkpoint only; source/CPU qualification does not claim native gameplay or installation.')
 (O/'native-event-v9-durable.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
