"""Bind all actual F35 DMA epochs and compare only the valid pre-divergence5354 prefix."""
from pathlib import Path
import argparse,csv,hashlib,json
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=lambda p:[json.loads(s)for s in Path(p).read_text().splitlines()]


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['run','old-run','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 new=rows(a.run/'epochs.jsonl');old=rows(a.old_run/'epochs.jsonl')
 before=lambda data:{q['start']['frame']:q for q in data if q['start']['frame']<=514}
 np,op=before(new),before(old);assert set(np)==set(op)
 fields=['start','start_hardware','start_hardware_exact_source','dma_finished_before_start','chr_banks','palette','mask','game_generation','source_generation']
 comparisons=[]
 for n in sorted(op):
  x,y=op[n],np[n];different=[k for k in fields if x.get(k)!=y.get(k)]
  # Publication timing may change from the added foreground cancellation cost;
  # compare actual bytes/owner identity separately from timestamp differences.
  for k in ['data_writes','complete','oam_address','writer_callback_pc','writer_bank','writer_instruction']:
   if x['dma'][k]!=y['dma'][k]:different.append('dma.'+k)
  if x['dma']['publication']['oam']!=y['dma']['publication']['oam']:different.append('source_OAM256')
  comparisons.append(dict(frame=n,fields_differing=different,baseline_DMA=x['dma']['id'],candidate_DMA=y['dma']['id'],
                          baseline_DMA_PPU=x['dma']['ppu'],candidate_DMA_PPU=y['dma']['ppu'],
                          baseline_publication=x['dma']['publication']['id'],candidate_publication=y['dma']['publication']['id']))
 assert all(not q['fields_differing'] for q in comparisons)
 trace=[]
 for r in [a.old_run,a.run]:
  with(r/'trace.csv').open()as f:trace.append([q for q in csv.DictReader(f)if int(q['frame'])<=514])
 assert trace[0]==trace[1]and len(trace[0])==514
 # Every actual visible/live or init epoch remains bound. This is not an
 # extrapolated baseline cadence comparison after the real HUD divergence.
 summaries=[]
 for e in new:
  d=e['dma'];assert e['start_hardware_exact_source']and e['dma_finished_before_start']and d['data_writes']==256 and d['complete']
  assert len(e['start_hardware'])==len(d['publication']['oam'])==256
  last=d['last_data_write'];source=d['publication'];body=source.get('body');family=body and body['source'].get('body_family','live')
  summaries.append(dict(frame=e['start']['frame'],start=e['start'],DMA=d['id'],DMA_write=d['ppu'],last_DMA_data_write=last,
                        completed256=True,exact256=True,completion_margin_CPU=e['start']['cpu']-last['cpu'],
                        OAMADDR=d['oam_address'],PPUMASK=e['mask'],publication=source['id'],source_generation=e.get('source_generation'),
                        game_generation=e.get('game_generation'),physical_CHR=e['chr_banks'][0],body_family=family,
                        actual_body_source=body and body['source']['label']))
 (a.output/'prefix-comparisons.json').write_text(json.dumps(comparisons,indent=2)+'\n')
 (a.output/'actual-DMA-epochs.json').write_text(json.dumps(summaries,indent=2)+'\n')
 margins=sorted(summaries,key=lambda q:q['completion_margin_CPU'])
 native=json.loads((a.run/'native-result.json').read_text());life=json.loads((a.run/'lifecycle-native-result.json').read_text())
 q=dict(passed=True,native_run=False,classification='Offline actual native epoch/cadence aggregation, not a replacement sixth receipt',
        exact_trace_prefix_rows=514,pre_divergence_actual_epoch_comparisons=len(comparisons),baseline_prefix_last_frame=514,
        baseline_is_failed_and_partial=True,no_post_divergence_baseline_performance_claim=True,
        total_actual_epochs=len(new),exact_completed256_epochs=len(summaries),worst_completion_margins=margins[:8],
        actual_wall_frames=native['wall'],actual_updates=native['updates'],actual_active_DMAs=native['DMAs'],
        actual_publications=native['publications'],actual_NMIs=native['nmis'],actual_min_SP=native['min_sampled_SP'],
        actual_deaths=life['deaths'],actual_new_life_updates=life['new_life_updates'],actual_Buffer2_flushes=life['actual_Buffer2_flushes'],
        actual_pending_Buffer2_holds=life['pending_Buffer2_holds'],
        files={f.name:sha(f)for f in a.output.iterdir()if f.is_file()},
        bindings={str(r/n):sha(r/n)for r in [a.run,a.old_run]for n in ['epochs.jsonl','trace.csv']},tool_sha256=sha(Path(__file__)),
        limits='Actual oneEasy0Oct1death2200. All recorded completed visible DMA epochs checked; CPU cycle margins are observations, not a hardware DMC worst-case or global60Hz proof. Baseline stopped813and its firstvisible intendedHUDdivergence515 bounds strictsame-input comparison to514. Area/Hard/Buffer2pendingoverlap remain unqualified; original aggregateFALSE remains unchanged.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['worst_completion_margins','bindings']},indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()
