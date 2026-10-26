"""Compare only the two proposed short raw bootstrap diagnostics; retain faults."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,hashlib,json,statistics
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False);data={};summary={}
 for label in['baseline','candidate']:
  f=a.prepared/label;result=json.loads((f/'diagnostic-result.json').read_text());assert result['diagnostic_complete']and result['frames']==220
  raw=[json.loads(v)for v in(f/'bootstrap-events.jsonl').read_text().splitlines()];data[label]=raw
  entries={r['DMA']['id']:r['DMA']for r in raw if r['kind']=='DMA-start'};complete=[r for r in raw if r['kind']=='DMA-complete'];bad=[r for r in complete if not r['exact']]
  assert len(complete)==result['DMAs']and len(bad)==result['hardware_mismatch_DMAs'];assert all(r['transferred']==256 and len(r['source'])==len(r['hardware'])==256 for r in complete)
  costs=defaultdict(list)
  for r in raw:
   if r['kind']=='routine-return':costs[r['name']].append(r['inclusive_CPU_cycles'])
  releases=[r for r in raw if r['kind']=='Main-release'];assert all(r['writerBank']==126 and r['writerPC']==0x8355 for r in releases)
  summary[label]=dict(result=result,exit=json.loads((f/'exit.json').read_text()),kind_counts=dict(Counter(r['kind']for r in raw)),raw_jsonl_sha256=sha(f/'bootstrap-events.jsonl'),Main_release_banks=sorted({r['writerBank']for r in releases}),inclusive_costs={n:dict(calls=len(v),mean=statistics.mean(v),p95=sorted(v)[int((len(v)-1)*.95)],max=max(v))for n,v in costs.items()},first_bad=dict(start=entries[bad[0]['DMA']],complete=bad[0],actual_write256=[r for r in raw if r['kind']=='DMA2004'and r['DMA']==bad[0]['DMA']])if bad else None)
 kinds=sorted({r['kind']for rr in data.values()for r in rr});comparison={}
 for kind in kinds:
  x=[r for r in data['baseline']if r['kind']==kind];y=[r for r in data['candidate']if r['kind']==kind]
  differences=[dict(index=i,baseline=u,candidate=v)for i,(u,v)in enumerate(zip(x,y))if u!=v]
  comparison[kind]=dict(baseline_rows=len(x),candidate_rows=len(y),exact=x==y,different_rows=len(differences),first_differences=differences[:3])
 result=dict(diagnostic_analysis_complete=True,game_or_hardware_equality_pass=all(q['result']['passed']for q in summary.values()),all_raw_events_ordered_semantically_exact=data['baseline']==data['candidate'],by_kind=comparison,cases=summary,checker_sha256=sha(__file__),limits='Raw faults are retained with all256 source/hardware bytes and writes. No equality byte masks, causal shortcut, source optimization, campaign, ability or projectile-visibility qualification. Inclusive profile costs overlap nested callees and are not exclusive/additive. Memory packet snapshots can include unconsumed bytes; all differences are retained.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(diagnostic_analysis_complete=True,hardware_equality_pass=result['game_or_hardware_equality_pass'],all_raw_events_exact=result['all_raw_events_ordered_semantically_exact'],proof_sha256=sha(a.output/'proof.json')),indent=2))
if __name__=='__main__':main()
