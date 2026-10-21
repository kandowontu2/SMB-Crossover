"""Freeze actual discovery T before an independent complete fixed replay."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=H/'t-discovery-freeze-ay.json';assert not out.exists()
    p=R/'build/roster-through-2-2/root49-d-samus-m5-lowhop-t-2-v0-mmc5';m=json.loads((p/'manifest.json').read_text())
    result=json.loads((p/'result.json').read_text())
    assert result['cleared']and result['all_six_stages']and result['deaths']==0 and result['frames']==27659
    assert not m['verified_through_2_2']and m['config']['replay']is None
    assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']
    assert m['rom_sha256']=='1d84dbb52d73a6748c8663c2bc44b09ac303b7a3e31b78119dfe3e57811f468a'
    assert sha(p/'inputs.csv')==m['inputs_sha256']=='0514efcc4d94dfc95aa86eb373a0ba9ceeb42be3f3d996d66f5287ade5bb7997'
    record=dict(status='FROZEN_ACTUAL_D_MMC5_SAMUS_DISCOVERY_BEFORE_INDEPENDENT_REPLAY',script_sha256=sha(__file__),
      result=result,files={x.name:dict(bytes=x.stat().st_size,sha256=sha(x))for x in p.iterdir()if x.is_file()},
      fixed_replay_policy_sha256=sha(H/'observer-c.lua'),
      limits='Discovery is not an independent fixed proof, final movie, all-arsenal or source-perfect claim.',goal_complete=False)
    out.write_text(json.dumps(record,indent=2)+'\n');print(record['status'],sha(out))
if __name__=='__main__':main()
