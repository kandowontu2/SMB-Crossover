"""Freeze the qualified private proofs without creating a playable cartridge."""
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[2]
O=R/'build/bubble-bobble-source-1101-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()


def main():
 receipts=['native-model-CPU.json','native-helpers-CPU.json','common-cold-CPU.json','common-owner-CPU.json']
 files={Path(__file__)}
 for name in receipts:
  p=O/name;q=json.loads(p.read_text());assert q['passed'] and not q['ROM_written'];files.add(p)
  for rel,digest in q.get('bindings',{}).items():
   bound=R/rel;assert sha(bound.read_bytes())==digest,rel;files.add(bound)
 for name in ['bubble_bobble_native_model_1101_v3.py','bubble_bobble_native_leaves_1101_v3.inc','bubble_bobble_native_frame_1101_v3.inc']:
  files.add(R/'tools/reference'/name)
 for name in ['prepare_bubble_bobble_native_leaves_1101_v3.py','check_bubble_bobble_native_model_1101_v3.py']:
  files.add(R/'tools/audit'/name)
 for name in ['component.s','component.cfg','component.lbl','component-layout.json','native-leaves.s','native-leaves.cfg','native-leaves.lbl','native-leaves-layout.json','native-helpers.lbl','common-owner.s','common-owner.cfg','common-owner.lbl','common-owner-layout.json','common-split.s','common-split.cfg','common-split.lbl','common-cold-layout.json','common-Ex-frame.s','common-Ex-frame.cfg','common-Ex-frame.lbl','common-current-Ex-cookie.bin','common-BB-cookie.bin','component-native.chr','chr-closure.json']:
  files.add(O/name)
 for p in files:assert p.exists() and p.suffix.lower()not in['.nes','.dbg','.png','.o'],p
 archive=O/'qualified-native-proofs-1102-v1.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in sorted(files):
   item=zipfile.ZipInfo(p.relative_to(R).as_posix(),date_time=(2026,11,2,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED
   z.writestr(item,p.read_bytes(),compresslevel=9)
 q=dict(passed=True,ROM_written=False,installed=False,admitted=False,base_ROM_SHA256='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8',archive=archive.relative_to(R).as_posix(),archive_SHA256=sha(archive.read_bytes()),archive_bytes=archive.stat().st_size,files={p.relative_to(R).as_posix():dict(SHA256=sha(p.read_bytes()),bytes=p.stat().st_size)for p in sorted(files)},scope='Frozen private original/native core, immutable helpers and full nine-row cold/auth/foreign-retirement CPU receipts. Nine private rows0/1/2/15/17/18/26/30/36 are implemented;28 reject. Existing layout prose saying onlyfour rows or all33 reject is stale; the vector bytes and CPU receipt are authoritative. No actual shared Hu/Main/contact/AI/birth admission, native emulator or full-stage proof. Common owner full interrupt-cut proof is still pending; helper IRQ/Main-busy NMI cuts are332.')
 (O/'qualified-native-proofs-1102-v1.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps({k:q[k]for k in['passed','archive_bytes','archive_SHA256','ROM_written','admitted']}))


if __name__=='__main__':main()
