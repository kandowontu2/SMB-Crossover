"""Verify the real Mac metadata move and complete, uniform Chip score data."""
from pathlib import Path
import argparse
import hashlib
import json
import re
from check_tmnt_render_oa import load, address, location
from check_tmnt_audio_fallback_oc import qualified

ROOT = Path(__file__).resolve().parents[2]
BASE = '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def verify_layout(path):
    baseline = ROOT/'build/smb-crossover-mmc5-expanded.nes'
    assert sha(baseline) == BASE
    old, new = load(baseline), load(path)
    before, after = old['raw'], new['raw']
    assert before[:16] == after[:16] and before[1048592:] == after[1048592:]
    names = re.findall(r'^(\w+):', (ROOT/'src/little_mac_art.inc').read_text(), re.M)
    qb, qn = qualified(baseline), qualified(path)
    moves = {k: (v, qn.get(k)) for k,v in qb.items() if qn.get(k) != v}
    assert set(moves) == {(n,) for n in names}
    assert all(b == a+0x11b0 for a,b in moves.values())
    records = []
    for name in [f'Lp{i}{face}' for i in range(10) for face in ['R','L']]+['LmStar']:
        p,q = location(old,name),location(new,name)
        size = before[p]+1
        assert before[p:p+size] == after[q:q+size],name
        records.append(dict(name=name,old=address(old,name),new=address(new,name),bytes=size,
                            source_sha256=hashlib.sha256(before[p:p+size]).hexdigest()))
    for face in ['R','L']:
        lo,hi = location(new,'LmPose'+face+'Lo'),location(new,'LmPose'+face+'Hi')
        for i in range(10):
            assert after[lo+i]+256*after[hi+i] == address(new,f'Lp{i}{face}')
        p,q = location(old,'LmChr'+face),location(new,'LmChr'+face)
        assert before[p:p+10] == after[q:q+10]
    # Reconstruct the entire changed Mac code bank using only the six typed
    # actual LmSetPose table operands and the real LmDrawGate star pointer.
    expected = bytearray(before[16+93*8192:16+94*8192])
    start = location(old,'LmSetPose')-(16+93*8192)
    size = int(old['syms']['LmSetPose']['size'],0)
    for name in ['LmPoseRLo','LmPoseRHi','LmChrR','LmPoseLLo','LmPoseLHi','LmChrL']:
        a,b = address(old,name),address(new,name)
        pattern = bytes([0xbd,a&255,a>>8])
        offsets = [i for i in range(start,start+size-2) if expected[i:i+3] == pattern]
        assert len(offsets) == 1,(name,offsets)
        at = offsets[0]; expected[at+1:at+3] = bytes([b&255,b>>8])
    a,b = address(old,'LmStar'),address(new,'LmStar')
    pattern = bytes([0xa9,a&255,0x85,address(old,'R0'),0xa9,a>>8,0x85,address(old,'R1')])
    offsets = [i for i in range(8192-len(pattern)+1) if expected[i:i+len(pattern)] == pattern]
    assert len(offsets) == 1,offsets
    at = offsets[0]; expected[at+1] = b&255; expected[at+5] = b>>8
    assert bytes(expected) == after[16+93*8192:16+94*8192]
    plan = json.loads((ROOT/'reference/new-roster-audio/playlist-plan.json').read_text())['chip']
    source = ROOT/plan['source']; original = source.read_bytes()
    assert sha(source) == '6a8b3729742654a5cc59bf2a1be904086fdbbf53d51c3a1b40bf16c387298b3f'
    assert after[location(new,'ChNativeDataA'):location(new,'ChNativeDataA')+0x1d00] == original[128+0x100:128+0x1e00]
    assert after[location(new,'ChNativeDataC'):location(new,'ChNativeDataC')+0x11b0] == original[128+0x1e00:]
    assert before[16+62*8192:16+62*8192+0x2b7] == after[16+62*8192:16+62*8192+0x2b7]
    return dict(genuine_mac_label_moves={'.'.join(k):list(v) for k,v in moves.items()},
                original_record_bytes=records,actual_typed_mac_code_bank_reconstructed=True,
                original_mac_CHR_exact=True,complete_original_score_data_bytes=11952,
                data_mapping='original8100..afaf uniformly +2200 across A62/C94',
                source_sha256=sha(source),original_bank62_publisher_prefix_exact=True,
                all_other_old_scoped_symbols_exact=len(qb)-len(moves),
                scope='Static compiled source/record/pointer/layout proof; dynamic Mac rendering and music/native timing remain separate.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists();a.output.mkdir(parents=True)
    result=dict(passed=True,native_run=False,accepted=False,candidate_ROM_sha256=sha(a.rom),
                layout=verify_layout(a.rom),checker_sha256=sha(__file__))
    (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,Mac_records=len(result['layout']['original_record_bytes']))))


if __name__ == '__main__': main()
