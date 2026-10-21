"""Verify the actual D MMC5 fixed clear against frozen ordinary discovery T."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def main():
    out=H/'samus-mmc5-review-ay.json';assert not out.exists()
    frozen=H/'t-discovery-freeze-ay.json';f=json.loads(frozen.read_text())
    a=R/'build/roster-through-2-2/root49-d-samus-m5-lowhop-t-2-v0-mmc5'
    b=R/'build/roster-through-2-2/root49-d-samus-m5-fixed-u-2-v0-mmc5'
    for n,h in f['files'].items():assert sha(a/n)==h['sha256'],n
    m=json.loads((b/'manifest.json').read_text());result=json.loads((b/'result.json').read_text())
    assert m['verified_through_2_2']and result==f['result']and result['frames']==27659 and result['deaths']==0
    assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and not m['config']['record']
    assert sha(b/'smb-crossover-mmc5.nes')==m['rom_sha256']=='1d84dbb52d73a6748c8663c2bc44b09ac303b7a3e31b78119dfe3e57811f468a'
    streams='inputs.csv trace.csv events.csv render.csv oam.csv chr.csv scroll-writes.csv audio-events.csv stomp-events.csv actual-injury-b.csv'.split()
    assert all((a/n).read_bytes()==(b/n).read_bytes()for n in streams)
    raw=list(a.glob('injury-*.ram'));assert all((b/p.name).read_bytes()==p.read_bytes()for p in raw)
    identity=json.loads((b/'current-c-identity.json').read_text());assert identity==dict(character=2,behavior=0,marioVariant=0,billVariant=0,outlinesOff=1)
    stomp=json.loads((b/'stomp-summary.json').read_text());assert stomp['illegal_guest_events']==0 and stomp['resident_opcode_mismatches']==0 and stomp['behavior_version']==0
    t=rows(b/'trace.csv');end=[x for x in t if x['world']=='1'and x['level']=='2'and x['engine']=='8'and x['mode']=='1'and x['task']=='3']
    assert len(t)==27659 and len(end)>=25 and end[0]['x']=='40'and int(end[-1]['x'])>40
    report=dict(status='PASS_ACTUAL_D_MMC5_SAMUS_FULL_FIXED_CLEAR',script_sha256=sha(__file__),
      discovery_freeze_sha256=sha(frozen),rehash_discovery_files=len(f['files']),identity=identity,result=result,
      ten_whole_CSVs_literal_to_discovery=streams,raw_snapshots_literal=len(raw),stomps=stomp,
      next_level_response=dict(active_rows=len(end),x=[int(end[0]['x']),int(end[-1]['x'])]),
      files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in b.iterdir()if p.is_file()},
      limits=['D/Easy0 only; future integrated E needs an actual transfer.',
       'Zero-death route, not necessarily damage-free or every-enemy/item/weapon coverage.',
       'No final movie or every-frame visual review claimed; raw snapshots are a bounded contact pool, not all-frame RAM coverage.'],goal_complete=False)
    out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],sha256=sha(out),snapshots=len(raw))))
if __name__=='__main__':main()
