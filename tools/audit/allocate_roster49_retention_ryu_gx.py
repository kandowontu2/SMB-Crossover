"""Retain all evidence, raise working cap and bound Ryu motion investigation."""
from pathlib import Path
import datetime,hashlib,json,shutil,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
used=workspace_bytes(R);disk=shutil.disk_usage(R)
assert used<80000000000 and disk.free>22000000000
out=V/'root49-retention-and-ryu-motion-allocation-gx.json';assert not out.exists()
prior=V/'root49-lsr-g-allocation-gb.json';assert sha(prior)=='cf0fdba56955b03bd11da2082c8fc6bcfe2d8d2fd53576edb988285d0f4704e3'
z=dict(status='ADDITIVE_USER_AUTHORIZED_RETENTION_CAP_AND_PRIVATE_RYU_MOTION_ALLOCATION',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),user_authority='Retain lossless captures; raise cap',prior_global_cap=80000000000,new_global_cap=100000000000,current_global_bytes=used,drive_free_bytes=disk.free,retention='No deletion of failures, lossless recordings or frozen packets. Original receipts remain bound to their original runs/caps.',owner='link_simon_ryu',prior_owner_authority=str(prior.relative_to(R)),prior_owner_sha256=sha(prior),old_inclusive_cap=2200000000,new_inclusive_cap=2400000000,inclusive_reserve=100000000,new_private_phase='build/verification/agent49-ryu-motion-h-a',private_cap=200000000,private_reserve=50000000,scope='Investigate actual H Ryu positive14..16px completed-position jumps in1-2 and2-2; bind exact native position writes, realDMA and source/current/previous collision geometry. Frozen G AL and root H GS stay immutable. Private source fix only if native/source cause is demonstrated; no main install, no universal source or route retag. Source-copy/build plus bounded native windows must fit before each launch.',goal_complete=False)
out.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(path=str(out.relative_to(R)),sha256=sha(out),global_bytes=used,free=disk.free)))
