"""Freeze only the exact Mini native-end successor and selected CPU inputs."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_native_end_1103_v48 as P
W,R,O=P.W,P.R,P.O
def main():
 q=json.loads((O/'mini-host-v48.json').read_text());assert q['passed']and W.sha((O/'mini-host-v48.bin').read_bytes())==q['SHA256']
 prior=P.PRIOR/'mini-final-host-v45.json';p=json.loads(prior.read_text());raw=P.ROM.read_bytes();assert W.sha(raw)==P.PIN
 files=[Path(__file__),Path(P.__file__),prior]+[O/f'mini-host-v48.{x}'for x in['s','cfg','bin','lbl','json']]
 members={x.relative_to(R).as_posix():dict(bytes=x.stat().st_size,SHA256=W.sha(x.read_bytes()))for x in files}
 direct={f'direct-native-inputs/8daf-PRG{bank}.bin':raw[16+8192*bank:16+8192*(bank+1)]for bank in[1,126,127]}
 archive=O/'mini-native-end-v49.zip'
 with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=9)as z:
  for x in files:z.writestr(x.relative_to(R).as_posix(),x.read_bytes())
  for n,b in direct.items():z.writestr(n,b);members[n]=dict(bytes=len(b),SHA256=W.sha(b))
 out=dict(passed=True,source_CPU_only=True,native_admitted=False,archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,archive_SHA256=W.sha(archive.read_bytes()),kernel=dict(path=(O/'mini-host-v48.bin').relative_to(R).as_posix(),bytes=q['bytes'],SHA256=q['SHA256'],five_pages_spare=q['five_pages_spare'],labels=q['labels']),parent_ROM_SHA256=P.PIN,prior_source_checkpoint=dict(manifest=prior.relative_to(R).as_posix(),archive_SHA256=p['archive_SHA256'],retention='Retain unchanged prior v45 and referenced v30/world21 compact checkpoints; no graph rehydration.'),new_git_source_files=[Path(P.__file__).relative_to(R).as_posix(),Path(__file__).relative_to(R).as_posix()],git_source_files=p['git_source_files']+[Path(P.__file__).relative_to(R).as_posix(),Path(__file__).relative_to(R).as_posix()],scope=q['scope'],native_castle_fixture=q['native_castle_wall_fixture'],native_scope='Root end47 confirms old8dafengine5 walking through castle/StarFlag0/CollisionFF. Source48CPU repairs that exact contract; actual successor/native route and delivery are root-owned, pending at freeze.',members=members)
 (O/'mini-native-end-v49.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k]for k in['passed','archive_bytes','archive_SHA256','kernel','new_git_source_files']}))
if __name__=='__main__':main()
