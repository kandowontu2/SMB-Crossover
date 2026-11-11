"""Compose and qualify the live Jay stock sprite with released Sonic 8c1e."""
import json
from types import SimpleNamespace
from unittest.mock import patch

import check_dkjr_late_girder_admission_1111 as Dk
import check_jay_silius_stock_draw_dispatch_1111 as Draw
import check_sonic_sms_fast_snapshot_1111 as Sonic

C,H = Draw.C,Draw.H
JAY = 'a2c36ff819a2f897dd58baec3df0ca3f397cac0f65133e03aa8101667a661d96'


def proposal(raw):
    """Return the merged bytes and matching runtime metadata without writes."""
    assert C.digest(raw)==Sonic.PIN
    parent = Dk.source_parent(raw)
    assert C.digest(parent)==Draw.PIN
    reproduced, release = Sonic.from_installed(parent)
    assert reproduced==raw and release['changes']==49
    with patch.object(H,'ROM',SimpleNamespace(read_bytes=lambda:parent)):
        trial,_,_,program,private,cookie,prior = Draw.proposal(C.actual_donor())
    jay = trial['raw']
    assert C.digest(jay)==JAY and prior['parent']==Draw.PIN
    jay_edits = Sonic.changed(parent,jay)
    sonic_edits = Sonic.changed(parent,raw)
    assert len(sonic_edits)==49 and not jay_edits & sonic_edits
    image = bytearray(raw)
    for offset in jay_edits:
        image[offset] = jay[offset]
    image = bytes(image)
    assert Sonic.changed(raw,image)==jay_edits
    assert Sonic.changed(jay,image)==sonic_edits
    report = dict(parent=Sonic.PIN,image=C.digest(image),jay_source=JAY,jay_edits=len(jay_edits),
                  preserved_Sonic_edits=len(sonic_edits),sonic_spans=release['spans'],
                  cookie=cookie.hex(),draw_hook=prior['draw_hook'])
    return image,dict(trial,raw=image),program,private,cookie,report


if __name__=='__main__':
    _,trial,program,private,cookie,report = proposal(H.ROM.read_bytes())
    print('Jay and released Sonic composition',report,flush=True)
    _,receipt = Draw.live_draw(trial,program,private,cookie,report)
    print(json.dumps(dict(passed=True,composition=report,natural_Main_DMA=receipt,
        Mesen=False,ROM_written=False,generated_files=0),sort_keys=True),flush=True)
