"""Stage the same genuine arm/body composites in Pharaoh's alternate palette."""
from pathlib import Path
import sys,hashlib,json
from PIL import Image
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/reference'))
O=R/'build/verification/new-roster-1-1-nd/bass-special-arm';O.mkdir(exist_ok=False)
overlay=O/'overlay';(overlay/'src').mkdir(parents=True);(overlay/'chr/characters').mkdir(parents=True)
source=(R/'tools/reference/build_bass_special_poses.py').read_text()
for name in('src/bass_special_poses.inc','src/bass_special_pose_ids.inc','chr/characters/special-bass-body.chr'):
 old="(ROOT/'"+name+"').write_";new="(OVERLAY/'"+name+"').write_"
 assert source.count(old)==1;source=source.replace(old,new)
ns=dict(__name__='bass_special_staged',__file__=str(R/'tools/reference/build_bass_special_poses.py'),OVERLAY=overlay)
exec(compile(source,ns['__file__'],'exec'),ns)
expanded=ns['expanded'];original=expanded.body
replacements={original('BASS',p,0).tobytes():Image.open(O.parent/'bass-arm-plan'/(p+'.png')).convert('RGBA')for p in('STAND','ATTACK1','JUMPSHOOT')}
def complete(role,pose,power):
 image=original(role,pose,power)
 return replacements.get(image.tobytes(),image).copy()
expanded.body=complete
ns['main']()
body=overlay/'chr/characters/special-bass-body.chr'
assert body.stat().st_size<=14*1024,'Do not grow into Lance reserved logical74..77'
assert (overlay/'src/bass_special_pose_ids.inc').read_bytes()==(R/'src/bass_special_pose_ids.inc').read_bytes()
(O/'manifest.json').write_text(json.dumps(dict(bytes=body.stat().st_size,sha256=hashlib.sha256(body.read_bytes()).hexdigest(),stable_pose_IDs=True,no_new_chr_banks=True),indent=2)+'\n')
