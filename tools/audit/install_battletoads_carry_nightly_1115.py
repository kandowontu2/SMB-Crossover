"""Direct no-backup delivery of the native-qualified partial carry improvement."""
from hashlib import sha256
from pathlib import Path
import json
import compose_battletoads_carry_current_1115 as C
import replay_battletoads_carry_current_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check

OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/battletoads-carry-delivery-1115.json'

if __name__=='__main__':
    grant=json.loads(GRANT.read_bytes())
    assert grant['direct_Downloads_replacement_authorized']and grant['all_three_private_native_passed']
    assert len(grant['private_receipts'])==3 and Path(grant['destination'])==C.ROM
    assert not grant['backups_allowed']and not grant['releases_and_patch_assets_allowed']
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==grant['composer_SHA256']
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==grant['stage_factory_SHA256']
    before=check(C.ROM);old=C.ROM.read_bytes()
    assert sha256(old).hexdigest()in(C.PIN,C.CANDIDATE)
    candidate=(OUT/'candidate.nes').read_bytes()
    assert sha256(candidate).hexdigest()==grant['candidate_SHA256']==C.CANDIDATE
    parent=C.inverse(candidate)
    assert C.proposal(parent)[0]==candidate and(old==parent or old==candidate)
    assert check(OUT/'candidate.nes')['ROM_sha256']==C.CANDIDATE
    require_free_workspace(C.R,C.ROM,allow_interactive=True)
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    C.ROM.write_bytes(candidate);after=check(C.ROM)
    assert C.ROM.read_bytes()==candidate
    print(json.dumps(dict(installed=True,SHA256=C.CANDIDATE,bytes=len(candidate),
        destination=str(C.ROM),before=before,after=after,backups=0,
        partial_performance_only=True,actual_Downloads_repeats_still_required=True),separators=(',',':')),flush=True)
