"""Read-only current Celeste ownership and compact control input inventory."""
from pathlib import Path
from hashlib import sha256
from unittest.mock import patch
from zipfile import ZipFile
import json
import check_ff_white_mushroom_current_1110 as W

R=W.R;ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21'
PACKET=R/'docs/qa/checkpoints/2026-10-30/celeste-easy-current-natural-11/source-and-native-evidence.zip'
PACKET_SHA='cedae99a0719e44fb8ed860b1a6bb725e4a86591530dc8753485b40538ebf568'
H=lambda b:sha256(b).hexdigest()


def inspect():
    raw=ROM.read_bytes();assert H(raw)==PIN;b=dict(W.Symbols.bundle(),raw=raw)
    names=('CmCoreStart','CmCoreEnd','CmSmallChrStart','CmSmallChrEnd','CmEnter','CmEnsure','CmMovement','CmAfterBG','CmWeapons','CmPickup','CmDraw',
        'CmHostEnabled','CmHostEnsure','CmHostMovement','CmHostAfterBG','CmHostPickup','KmNextVariant','FmToggle')
    rows=[]
    for name in names:
        if name not in b['syms']:continue
        pc,at=W.address(b,name),W.location(b,name);bank=(at-16)//8192
        rows.append(dict(name=name,PC=pc,file=at,bank=bank,prefix32=raw[at:at+32].hex(),bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192])))
    assert all(n in{name['name']for name in rows}for n in('CmMovement','CmPickup','CmHostMovement','CmHostPickup','CmHostEnsure'))
    state={n:W.address(b,n)for n in('CmTier','CmLife','CmActive','CmMarker','CmClock','CmState','CmWallGrace','CmWallKick','CmDashStock','CmDashTimer','CmPose','PlayerSize','PlayerStatus','MarioVariant')}
    assert state['CmTier']==0x5ff8 and state['CmActive']==0x5ffd
    assert H(PACKET.read_bytes())==PACKET_SHA
    controls=[]
    with ZipFile(PACKET)as z:
        ready=json.loads(z.read('build/current-celeste-easy-11-1030-v4/ready.json'))
        for name in('tools/playthroughs/celeste_small_upgrades_11_v2.lua','tools/playthroughs/celeste_upgrades_11_v8.lua','tools/playthroughs/sunny_11_v3.lua'):
            data=z.read(name);current=(R/name).read_bytes();assert data==current
            controls.append(dict(path=name,bytes=len(data),SHA256=H(data),current_repo_exact=True))
    data=raw[16+98*8192+0x1000:16+98*8192+0x1e0b]
    return dict(passed=True,ROM_SHA256=PIN,compiled_code_anchors=rows,state=state,
        core_bank98_B000_BE0B=dict(bytes=len(data),SHA256=H(data)),CHR740_743_SHA256=H(raw[1048592+740*1024:1048592+744*1024]),
        retained_historical_control_packet=dict(path=str(PACKET.relative_to(R)),SHA256=PACKET_SHA,controls=controls,
            versioned_ROM=ready['ROM_sha256'],old_native_claim_only=True,no_extraction=True),
        source_policy='Small size1; M/F increment CmTier to max2; S/L decline CmPickup and follow actual native fallback; positive life count preserves tier, actual decrement resets',
        CPU_executed=False,outputs=0,Mesen=False,game_bytes_changed=0,
        limits='Current code hashes/metadata anchors only. Compiled menu cycle, first returned owning movement and current caller/pickup routing require new actual cold CPU before item routes; no historical native relabeling.')


if __name__=='__main__':
    def deny(*args,**kw):raise AssertionError('Celeste inspection attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=inspect()
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
