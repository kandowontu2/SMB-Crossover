"""Export one additional whole native frame; keep the run's total at eight."""
from pathlib import Path
import csv,hashlib,json
from current_roster_compact_11_v1 import records,png
R=Path(__file__).resolve().parents[2]
def main():
 o=R/'build/verification/kamikaze-mario-upgrades-easy-v2';r=json.loads((o/'result.json').read_text());assert r['passed']and len(r['markers'])==7
 rows=list(csv.DictReader((o/'trace.csv').open()));first=next(i for i,row in enumerate(rows)if row['power']=='2')
 row=next(row for row in rows[first+90:]if row['power']=='2'and row['engine']=='8'and row['yHigh']=='1'and int(row['y'])>80)
 ordinal=int(row['captured']);p=o/'flower-whole-frame.png';assert not p.exists()
 for meta,raw in records(o/'captures.nesppuv1'):
  if meta['full_ordinal']==ordinal and meta['kind']==1:
   assert meta['stamp']['ppu_frame']==int(row['ppu_frame'])
   png(p,[raw]);break
 else:raise AssertionError(('Missing full frame',ordinal))
 d=dict(source='Exact lossless actual PPU full-frame record',requested_trace_row=row,record=meta,PNG_SHA256=hashlib.sha256(p.read_bytes()).hexdigest(),total_selected_whole_frames=8,script_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (o/'flower-frame-review-source.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(frame=row['frame'],full_ordinal=ordinal,PNG_SHA256=d['PNG_SHA256'])))
if __name__=='__main__':main()
