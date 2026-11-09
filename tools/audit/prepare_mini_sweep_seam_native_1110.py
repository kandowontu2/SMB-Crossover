"""Validate declared-parent proofs, rebase disjoint spans, prepare native replay."""
import argparse,json,shutil
from pathlib import Path
from compose_mini_frame_budget_1108 import compose,load,digest,check_full_cpu
from qualify_mini_busy_1109 import bind_kernel
from prepare_selected_native_packet_v1 import prepare,sha

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args()
old=Path('build/mini-combined-camera-native-1110/candidate.nes')
raw=old.read_bytes();assert digest(raw)=='56c4135e3edd7421c207fd4cd623ad8f58cd263353342d0af54202cd790cbcbc'
original=Path('build/mini-box-terrain-visible-1110/candidate.nes').read_bytes()
retained=bytearray(original)
for p in ('build/mini-camera-lifts-v2-1110/proof.json','build/mini-lift-retention-1110/proof-v2.json'):
    q=load(Path(p));q['parent_SHA256']=q.get('parent_SHA256',q.get('base_ROM_SHA256'))
    compose(bytes(retained),retained,q,parent=digest(retained))
candidate=bytearray(raw)
paths=[Path('build/mini-sweep-center-1110/proof.json'),Path('build/mini-goomba-seam-1110/proof.json')]
for parent,path in zip((bytes(retained),original),paths):
    q=load(path)
    q['parent_SHA256']=q.get('parent_SHA256',q.get('base_ROM_SHA256'))
    q['expected_memory_only_SHA256']=q.get('expected_memory_only_SHA256',q.get('expected_memory_ROM_SHA256'))
    verified=bytearray(parent);compose(parent,verified,q,parent=digest(parent))
    for patch in q['patches']:
        at=patch.get('file_offset',patch.get('offset'))
        before=bytes.fromhex(patch.get('old_hex',patch.get('preimage')))
        after=bytes.fromhex(patch.get('new_hex',patch.get('replacement')))
        assert len(before)==len(after) and candidate[at:at+len(before)]==before
        candidate[at:at+len(after)]=after
rows=check_full_cpu(raw,candidate,{2:[(0x1fe3,0x1ff0)],3:[(0,5120),(0x1fe3,0x1ff0)]})
out=args.output;out.mkdir()
rom=out/'candidate.nes';rom.write_bytes(candidate)
for ext in ('.dbg','.lbl'):shutil.copyfile(old.with_suffix(ext),rom.with_suffix(ext))
meta=load(old.with_suffix('.json'))
meta.update(parent_SHA256=digest(raw),candidate_SHA256=sha(rom),whole_GameCore=rows,
            added_proofs={str(p):sha(p) for p in paths},verification='Private replay pending')
rom.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
source=Path('build/mini-combined-camera-native-1110/route-v2/controller.lua')
kernel=Path('build/mini-sweep-center-1110/kernel.bin')
text=source.read_text().replace(digest(raw),sha(rom))
text=bind_kernel(text,kernel).replace(sha(Path('build/mini-lift-retention-1110/kernel-v2.bin')),sha(kernel))
# Repair only the extra observer's numeric-key JSON serialization.
text=text.replace("f:write(json(camera_lift_spawns));f:close()",'''local rows={}
 for _,left in ipairs({560,688,864}) do
  if camera_lift_spawns[left] then
   local row=camera_lift_spawns[left];row.left=left;rows[#rows+1]=row
  end
 end
 f:write(json(rows));f:close()''')
prepare(out/'route',rom,text,{source,kernel,kernel.with_suffix('.lbl'),Path(__file__),*paths},
        expected=sha(rom),timeout=180,allow_interactive=True,
        scope='Same controller/early native lift route as56c; new shared Goomba seam and source Mini head-sweep optimization. Both lives/all3liftboarddepartures/active1-2 required.')
print(json.dumps(dict(candidate_SHA256=sha(rom),whole_GameCore=rows)))
