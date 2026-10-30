"""Preserve the source-verified direct paths and measured remaining timing delta."""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
from checkpoint_roster_progress_1030_v2 import save,sha


def main():
    o=R/'build/character-host-union-v12'
    hp=o/'handoff.json';h=json.loads(hp.read_text())
    expected='2b65f0de7fdf8c6d9eeb9c96e6dd48849bbb121b026ecb25c4a2d299c5082090'
    assert h['candidate_sha256']==sha(o/'candidate.nes')==expected
    assert sha(hp)=='181bbe3027c2c245b643a6709aac7b6adbe6d6d04717dca43a24797acfaf0da7'
    assert not h['installation_ready']and h['native_route_qualification']
    assert len(h['receipts'])==28
    for path,digest in h['receipts'].items():
        assert sha(path)==digest,path
        q=json.loads(Path(path).read_text())
        assert q.get('passed')or q.get('status')=='PASS_ISOLATED_LINKED_6502_SOURCE_REVIEW',path
    assert sha(h['source_archive'])==h['source_archive_sha256']
    bindings=dict(h['bindings'])
    for p in [hp,Path(__file__).resolve(),o/'HANDOFF.md']:
        bindings[str(p)]=sha(p)
    save('four-host-union-v12',dict(
        status='DIRECT_FOREIGN_PATHS_PASS_SMALL_BILL_TIMING_DELTA_REMAINS',
        ROM_sha256=expected,source_suites=27,
        private_menu=dict(slots=32,identities=80,ready=51,pending=29),
        native=dict(Mario=dict(frames=300,Main_updates=300,lag_NMIs=0,mean_CPU=16739.0767),
            Bill=dict(frames=300,Main_updates=300,completion_histogram={'0':5,'1':290,'2':5},
                      lag_NMIs=5,parent_lag_NMIs=4,mean_CPU=21557.96,parent_mean_CPU=21514.725752508362),
            Gimmick='Easy1-1clear plus25controlled1-2updates,5191frames,3star rides,zero loss,HP1 OF2 S0'),
        changes='77source-linked byte changes; original Game/Reset/DP bodies and all1167RAM addresses retained. Foreign complete Main saves130CPU vsV11.',
        ABI_limit='Isolated Goku GameBridge X differs by3 due to real source TSX. Its retained negative is not normalized away. 232complete actual caller prefixes and256poisonX values prove no X read before genuine reservation LDX; full caller AXYP/SP/application/maps remain exact.',
        limits=['Bill remains43.2342CPU/Main over parent with5vs4missed frames and lagNMIs; held for further source optimization.',
                'Goku/DK/SuperMaaa exact-candidate1-1routes and fullpowerup coverage remain pending.',
                'Rogue, Quick, Arthur and proposed WRAM changes are independent and absent.']),bindings)


if __name__=='__main__':main()
