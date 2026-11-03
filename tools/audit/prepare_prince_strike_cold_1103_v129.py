"""Measure final122 lossless backing without rebuilding historical graphs."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_current_post_return_1102_v97 as M
O=M.O
PARENT=R/'build/bub-upgrades-root-candidate-1102-v72/bub-original-upgrades.nes'


def main():
 assert M.sha(PARENT.read_bytes())==M.PARENT;M.NIGHTLY=PARENT
 source=R/'tools/audit/prepare_prince_cold_link_1102_v44.py';text=source.read_text()
 changes={
  'import prepare_prince_successor_manifest_1102_v26 as M':'import prepare_prince_current_post_return_1102_v97 as M',
  'POOL=M.POOL+[514]':'POOL=M.POOL',
  'base,_,_,_=M.bundle()':'base,_=M.parent()',
  'native-runtime-v42.bin':'native-runtime-v122.bin',
  'native-metadata-v42.bin':'native-metadata-v122.bin',
  'native-state_code-v18.bin':'native-state-v122.bin',
  '0xc100,0xc400':'0xc100,0xc300',
  'M.A.PIN':'M.PARENT','M.A.BASE':'M.NIGHTLY','v44':'v129',
 }
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 env=dict(__file__=str(Path(__file__)),__name__='prince_strike_cold_v129');exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'cold-link-storage-v129.json';q=json.loads(path.read_text());assert q['passed']
 assert q['physical_pages']==44 and q['source_art_bytes']==31072
 q.update(private_source_measurement_only=True,existing_granted_execution_only=True,new_resources=0,source_runtime_version=122,required_execution_amendment=None,metadata_end=0xdfcf,clock_untouched=[0xdfd0,0xdfd3],scope='Final122 sameMain deferred strike and source-closed native no-drop acknowledgement. Three actual original lossless decoder outputs match all runtime/metadata/state bytes, preserving unread staging inputs. Existing44 carriers and original art unchanged. Shared cookie/fullcold/currentcf7 rebase and native qualification remain pending; no ROM emitted.')
 q['bindings'].update({p.relative_to(R).as_posix():M.sha(p.read_bytes())for p in [Path(__file__),source,O/'deferred-strike-measurement-v122.json',O/'deferred-strike-CPU-v123.json',O/'strike-lifetime-CPU-v126.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
