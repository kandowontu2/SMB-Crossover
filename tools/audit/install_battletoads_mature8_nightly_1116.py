"""Direct no-backup replacement after all eight private native BT gates."""
from pathlib import Path
import json
import compose_battletoads_mature8_1116 as C
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check

OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/battletoads-mature8-delivery-1116.json'

if __name__=='__main__':
    g=json.loads(GRANT.read_bytes());assert g['direct_Downloads_replacement_authorized']
    assert not g['backups_allowed'] and not g['releases_and_patch_assets_allowed']
    assert g['parent_SHA256']==C.PIN and g['candidate_SHA256']==C.CANDIDATE and Path(g['destination'])==C.ROM
    assert C.digest(Path(C.__file__).read_bytes())==g['composer_SHA256']
    assert set(g['private_native_receipts'])=={k+'_'+n for k in ('mushroom','oneup','star','full') for n in ('rash','zitz')}
    before=check(C.ROM);old=C.ROM.read_bytes();assert C.digest(old) in (C.PIN,C.CANDIDATE)
    candidate=(OUT/'candidate.nes').read_bytes();assert C.digest(candidate)==C.CANDIDATE
    parent=C.inverse(candidate);assert C.digest(parent)==C.PIN and old in (parent,candidate)
    owned=set()
    for at,previous,current in C.spans():
        assert parent[at:at+len(previous)]==previous and candidate[at:at+len(current)]==current
        owned.update(range(at,at+len(previous)))
    changed={i for i,(a,b) in enumerate(zip(parent,candidate,strict=True)) if a!=b}
    assert len(owned)==27 and len(changed)==22 and changed<=owned and len(candidate)==2097168
    assert check(OUT/'candidate.nes')['ROM_sha256']==C.CANDIDATE
    require_free_workspace(C.R,C.ROM,allow_interactive=True)
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    C.ROM.write_bytes(candidate);after=check(C.ROM);assert C.ROM.read_bytes()==candidate
    print(json.dumps(dict(installed=True,SHA256=C.CANDIDATE,bytes=len(candidate),destination=str(C.ROM),before=before,
        after=after,backups=0,actual_Downloads_eight_repeats_still_required=True),separators=(',',':')),flush=True)
