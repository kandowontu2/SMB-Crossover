"""Direct no-backup delivery of the exact visually qualified combined candidate."""
from hashlib import sha256
from pathlib import Path
import json
import compose_bub_selected_star_palette_prince_1115 as C
import replay_bub_star_images_physical_67_1115 as G
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check

OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/bub-star-prince-delivery-1115.json'

if __name__=='__main__':
    grant=json.loads(GRANT.read_bytes());assert grant['direct_Downloads_replacement_authorized']
    assert set(grant['private_native_receipts'])=={'Bub','Bob'}and grant['six_PNGs_visually_reviewed']
    assert not grant['backups_allowed']and not grant['releases_and_patch_assets_allowed']
    assert grant['candidate_SHA256']==C.CANDIDATE and Path(grant['destination'])==C.ROM
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==grant['composer_SHA256']
    assert sha256(Path(G.__file__).read_bytes()).hexdigest()==grant['picture_factory_SHA256']
    C.lease();before=check(C.ROM);old=C.ROM.read_bytes()
    assert sha256(old).hexdigest()in(C.PIN,C.CANDIDATE)
    candidate=(OUT/'candidate.nes').read_bytes();assert sha256(candidate).hexdigest()==C.CANDIDATE
    assert candidate[C.FILE:C.FILE+56]==C.NEW and candidate[C.COOKIE:C.COOKIE+16]==C.cookie(candidate)
    restored=bytearray(candidate);restored[C.FILE:C.FILE+56]=C.OLD
    restored[C.COOKIE:C.COOKIE+16]=C.OLD_COOKIE;parent=bytes(restored)
    assert sha256(parent).hexdigest()==C.PIN and old in(parent,candidate)
    assert check(OUT/'candidate.nes')['ROM_sha256']==C.CANDIDATE
    require_free_workspace(C.R,C.ROM,allow_interactive=True)
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    C.ROM.write_bytes(candidate);after=check(C.ROM);assert C.ROM.read_bytes()==candidate
    print(json.dumps(dict(installed=True,SHA256=C.CANDIDATE,bytes=len(candidate),
        destination=str(C.ROM),before=before,after=after,backups=0,
        actual_Downloads_repeats_still_required=True),separators=(',',':')),flush=True)
