"""Independently verify the actual D Bill/Lance fixed full clears."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
STREAMS='inputs.csv trace.csv events.csv render.csv oam.csv chr.csv scroll-writes.csv audio-events.csv stomp-events.csv'.split()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def main():
    out=V/'root49-current-d-transfers-a/bill-lance-review-ax.json';assert not out.exists()
    proofs=[]
    for name,suffix,variant,frames in [('Bill','a',0,31773),('Lance','b',1,31258)]:
        hpath=V/f'specialist-bill-lance-current-d-a/handoff-d-{suffix}.json'
        h=json.loads(hpath.read_text());p=R/h['proof'];before=R/h['comparison']['reference']
        m=json.loads((p/'manifest.json').read_text());r=json.loads((p/'result.json').read_text())
        assert sha(p/'manifest.json')==h['manifest_sha256']
        assert sha(p/'smb-crossover-mmc3.nes')==m['rom_sha256']==h['ROM_sha256']=='653ca0e82f27d9aa4a2033d9b4c68488b75ead18ae5b460bbf51bd05fa994a94'
        assert m['verified_through_2_2']and r['cleared']and r['all_six_stages']and r['deaths']==0 and r['frames']==frames and r['polls']==frames-1
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and not m['config']['record']
        i=json.loads((p/'ordinary-identity.json').read_text());assert i['selected']==3 and i['variant']==variant and i['mode']==0 and i['outlinesOff']==1
        exact={n:(p/n).read_bytes()==(before/n).read_bytes()for n in STREAMS}
        assert all(exact.values()),exact
        t=rows(p/'trace.csv');tail=[x for x in t if x['world']=='1'and x['level']=='2'and x['engine']=='8'and x['mode']=='1'and x['task']=='3']
        assert len(t)==frames and len(tail)>=25 and int(tail[-25]['x'])==40 and int(tail[-1]['x'])==70
        proofs.append(dict(name=name,mapper='mmc3',revision='D',identity=i,result=r,
          handoff_sha256=sha(hpath),whole_nine_CSVs_literal_to_C=exact,
          files={x.name:dict(bytes=x.stat().st_size,sha256=sha(x))for x in p.iterdir()if x.is_file()},
          arsenal_complete=False,source_perfect=False,final_recording=False))
    result=dict(status='PASS_ACTUAL_D_BILL_AND_LANCE_FULL_FIXED_CLEARS_NINE_STREAMS_LITERAL_TO_C',
      script_sha256=sha(__file__),proofs=proofs,goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],sha256=sha(out))))
if __name__=='__main__':main()
