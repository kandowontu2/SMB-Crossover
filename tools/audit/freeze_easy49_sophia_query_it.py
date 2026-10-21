"""Freeze a measured private query optimization for contextual integration."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=V/'root49-sophia-query-perf-ip';P=V/'agent49-e-sophia-union-a/source-e'
G=V/'ryu49-head-status-bridge-g';sys.path.insert(0,str(G));s=importlib.util.spec_from_file_location('query_it_bus',G/'check.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec=lambda p:dict(path=Path(p).relative_to(R).as_posix(),bytes=Path(p).stat().st_size,sha256=sha(p))


def main():
 out=D/'implementation-component-freeze-it.json';assert not out.exists()
 prep=json.loads((D/'preparation.json').read_text());assert len(prep['source_catalog'])==449
 for n,h in prep['source_catalog'].items():assert sha(D/'source'/n)==h,n
 check=json.loads((D/'compiled-is.json').read_text());assert check['status']=='PASS_EXACT_COMPILED_QUERY_ABI_AND_MEASURED_CYCLE_REDUCTION'
 assert all(m['cases']==6656 and m['cycle_deltas']=={'-31':6656}for m in check['maps'])
 maps=[]
 for mapper,expected in [('mmc3','0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146'),('mmc5','34858561f4825dcc96cdd5fd46872f9230890c93af95351720c8536155f5cbbd')]:
  filename='smb-crossover-'+mapper+'.nes';old=g.Image(P/'build'/filename);im=g.Image(D/'source/build'/filename)
  assert old.ram==im.ram
  assert old.raw[:16]==im.raw[:16]and old.raw[16+524288:]==im.raw[16+524288:]
  assert sha(D/'source/build'/('smb-crossover-'+mapper+'-baseline.nes'))==expected
  audio={}
  for a in old.segs.values():
   n=a['name']
   if not a.get('size')or'ooffs'not in a:continue
   if any(x in n for x in ['AUDIO','MUSIC','DPCM','SMCCODE'])and n!='REMAINING_AUDIO':
    b=next(x for x in im.segs.values()if x['name']==n)
    assert (a['start'],a['size'],a['ooffs'])==(b['start'],b['size'],b['ooffs']),n
    assert old.raw[a['ooffs']:a['ooffs']+a['size']]==im.raw[b['ooffs']:b['ooffs']+b['size']],n
    audio[n]=a['size']
  for n in ['NonMaskableInterrupt','IrqScrollSplit','MegaManVineAnchor']:assert old.hook(n)==im.hook(n)
  maps.append(dict(mapper=mapper,artifacts={e:rec(D/'source/build'/('smb-crossover-'+mapper+'.'+e))for e in ['nes','lbl','map','dbg']},baseline=rec(D/'source/build'/('smb-crossover-'+mapper+'-baseline.nes')),oldRAM_literal=True,header_CHR_literal=True,audio_DPCM_SMC_literal=audio,NMI_IRQ_Vine_literal=True))
 record=dict(status='FROZEN_PRIVATE_EXACT_QUERY_OPTIMIZATION_COMPILED_COMPONENT',utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),preparation=rec(D/'preparation.json'),source_catalog=prep['source_catalog'],compiled=rec(D/'compiled-is.json'),maps=maps,CPU_cycles_saved_per_query=31,source_changes=['src/sophia_source_terrain.s'],main_changed=False,accepted_release=False,goal_complete=False,retained_host_negatives=[rec(D/'compiled-ir.json'),rec(D/'build-mmc3.log'),rec(D/'build-mmc5.log')],qualification='Compiled standalone query evidence only. All registers/RAM/ordered semantic writes match; exactly3 old discarded GetBlockBufferAddr JSR/PHA cells are individually decoded. Actual integrated native caller/ISR, frames and route lag remain required. No universal lag claim.')
 out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(freeze=rec(out),status=record['status'],cycles_saved=31)))


if __name__=='__main__':main()
