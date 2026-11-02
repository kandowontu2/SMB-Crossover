"""Freeze the qualified private ingress successor and its pending shared lease."""
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'build/bubble-bobble-source-1101-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()


def main():
 files={Path(__file__)}
 for name in['common-routes-CPU.json','native-policy-CPU.json']:
  p=O/name;q=json.loads(p.read_text());assert q['passed']and not q['ROM_written']and not q['admitted'];files.add(p)
  for rel,digest in q['bindings'].items():
   p=R/rel;assert sha(p.read_bytes())==digest,rel;files.add(p)
 for name in['common-routes-layout.json','common-routes.s','common-routes.cfg','common-routes.lbl','common-route-foreign-bank.bin','native-policy-layout.json','native-policy-leaves.s','native-policy-leaves.cfg','native-policy-leaves.lbl','native-policy-helpers.s','native-policy-helpers.cfg','native-policy-helpers.lbl','native-policy-owner.s','native-policy-owner.cfg','native-policy-owner.lbl','native-policy-BB-cookie.bin','native-contact-gate.s','native-contact-gate.cfg','native-contact-gate.lbl']:
  files.add(O/name)
 for p in files:assert p.exists()and p.suffix.lower()not in['.nes','.dbg','.png','.o'],p
 archive=O/'native-ingress-qualified-1102-v4.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in sorted(files):
   info=zipfile.ZipInfo(p.relative_to(R).as_posix(),date_time=(2026,11,2,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes(),compresslevel=9)
 q=dict(passed=True,ROM_written=False,shared_source_written=False,admitted=False,base_ROM_SHA256='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8',inherited_native_core_freeze='qualified-native-proofs-1102-v1.json',archive=archive.relative_to(R).as_posix(),archive_SHA256=sha(archive.read_bytes()),archive_bytes=archive.stat().st_size,files={p.relative_to(R).as_posix():dict(SHA256=sha(p.read_bytes()),bytes=p.stat().st_size)for p in sorted(files)},source_files=[p.relative_to(R).as_posix()for p in sorted(files)if p.is_relative_to(R/'tools')],pending_source_lease=dict(physical_PRG=74,half_open=[0xbf03,0xbf34],bytes=49,existing_source_span_only=True,adjacent_BF00_jump_unchanged=True,granted=False),scope='Qualified actual current bank79 endpoint/scene/dispatch/auth/body/hazard/status/visibility/geometry CPU ingress proposals with complete recorded foreign and ISR cases. Frozen15 original native source files remain unchanged. Raw39 gameplay admission, native Main/AI/birth/shot-bank/fullbox/head/side/item-effect/fullstage and emulator qualification remain incomplete. No candidate or installation is produced.')
 (O/'native-ingress-qualified-1102-v4.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps({k:q[k]for k in['passed','archive_bytes','archive_SHA256','ROM_written','admitted']}))


if __name__=='__main__':main()
