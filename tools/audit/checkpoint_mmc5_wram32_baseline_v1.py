"""Freeze actual game-level header-only mapper parity, without adopting it."""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
from checkpoint_roster_progress_1030_v2 import save,sha


def main():
    o=R/'build/mmc5-wram32-game-baseline-v1'
    pp=o/'proof.json';p=json.loads(pp.read_text())
    assert p['passed']and p['native']and not p['shared_installation']
    assert p['ROM_sha256']==sha(o/'candidate.nes')=='f17df48cc4bcf358a6334a597bbe0e4b213561fe52e0c607551a276a5614e662'
    assert p['exact_same_native_result_except_ROM_hash']and len(p['exact_native_files'])==6
    assert p['baseline']['timing']['lag_nmi']==4
    bindings=dict(p['bindings'])
    for path in [pp,Path(__file__).resolve()]:bindings[str(path)]=sha(path)
    save('mmc5-wram32-game-baseline',dict(
        status='HEADER_ONLY_NATIVE_GAME_BASELINE_EXACT_NO_ADOPTION',
        ROM_sha256=p['ROM_sha256'],parent_ROM_sha256=p['parent_ROM_sha256'],
        changed_header_offset=10,old_value=7,new_value=9,
        unchanged_PRG_CHR_payload=True,actual_native=p['baseline'],
        exact_files=p['exact_native_files'],limits=p['limits']),bindings)


if __name__=='__main__':main()
