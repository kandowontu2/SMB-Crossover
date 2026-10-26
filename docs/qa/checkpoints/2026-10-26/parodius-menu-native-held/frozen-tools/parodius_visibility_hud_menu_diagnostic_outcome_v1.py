"""Freeze actual failed-start evidence and exact prefix; never retry."""
from pathlib import Path
import argparse,hashlib,json,collections
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['run','old-run','ready','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);run=json.loads((a.run/'lifecycle-proof.json').read_text());assert not run['passed']and run['runner_exit']==1
 first=json.loads((a.run/'first-init-start-mismatch.json').read_text());assert first['ppu']==dict(scanline=-1,frame=278,cpu=8249090,cycle=0)
 assert first['hardware256']==first['exact_source256']==first['current_source_RAM256']and len(first['hardware256'])==256
 assert first['DMA_write_count']==173 and not first['DMA_complete']and first['DMA_still_pending']and first['mask']==30 and first['hardware_OAMADDR']==first['software_OAMADDR']==173
 assert first['DMA_last_write']==dict(scanline=260,frame=278,cpu=8249090,cycle=340)
 assert first['DMA_start']==dict(scanline=257,frame=278,cpu=8248743,cycle=322)
 frames=sorted(a.old_run.glob('frame-*.argb'));assert [f.name for f in frames]==[f'frame-{i:06}.argb'for i in range(150,278)]
 for f in frames:assert f.read_bytes()==(a.run/f.name).read_bytes()
 for n in ['inputs.csv','trace.csv','body-writes.jsonl','completed-loop-motion.csv','completed-loop-motion.json']:
  if n.endswith('jsonl'):assert list(map(json.loads,(a.old_run/n).read_text().splitlines()))==list(map(json.loads,(a.run/n).read_text().splitlines()))
  else:assert(a.old_run/n).read_bytes()==(a.run/n).read_bytes(),n
 rows=[json.loads(s)for s in(a.run/'oam-bus.jsonl').read_text().splitlines()];oldrows=[json.loads(s)for s in(a.old_run/'oam-bus.jsonl').read_text().splitlines()]
 normalized=[x for x in rows if x['kind']not in ['lifecycle-init-parser-entry','lifecycle-init-start-before-assertion']];assert normalized==oldrows
 parser=[x for x in rows if x['kind']=='lifecycle-init-parser-entry'];assert len(parser)==7
 assert len({(x['SP'],x['return_word'])for x in parser})==1
 commands=[]
 for i,x in enumerate(parser[:-1]):
  data=x['packet128'];size=(data[2]&63)or 256;repeat=bool(data[2]&64);consumed=3+(1 if repeat else size)
  assert x['pointer']+consumed==parser[i+1]['pointer']
  commands.append(dict(index=i,pointer=x['pointer'],PPU_address=(data[0]<<8)|data[1],control=data[2],repeat=repeat,vertical=bool(data[2]&128),payload=data[3:consumed],payload_bytes=size,encoded_bytes=consumed,actual_start=x['ppu'],next_entry=parser[i+1]['ppu'],observed_CPU_cycles_until_next_entry=parser[i+1]['ppu']['cpu']-x['ppu']['cpu']))
 assert parser[-1]['packet128'][0]==0 and sum(x['encoded_bytes']for x in commands)==62
 assert commands[1]['payload']==commands[5]['payload']and commands[1]['PPU_address']==commands[5]['PPU_address']==0x3f11
 (a.output/'actual-packet.json').write_text(json.dumps(dict(commands=commands,terminator=parser[-1],one_JSR_call_six_commands=True,parser_CPU_cycles=parser[-1]['ppu']['cpu']-parser[0]['ppu']['cpu'],terminator_to_DMA_start_cycles=first['DMA_start']['cpu']-parser[-1]['ppu']['cpu']),indent=2)+'\n')
 prefix=dict(passed=True,comparison_only=True,raw_ARGB_exact=len(frames),actual_frames=[150,277],inputs_trace_bodywrite_motion_exact=True,all_original_bus_rows_exact=True,new_readonly_rows=8,previous_failure_retained=True,no_outcome_retagging=True)
 (a.output/'prefix-equivalence.json').write_text(json.dumps(prefix,indent=2)+'\n')
 report=ROOT/'docs/qa/parodius-hud-menu-diagnostic-native-2026-10-25.txt'
 manifest={str(f.resolve()):sha(f)for base in [a.run,a.old_run]for f in base.rglob('*')if f.is_file()}
 for f in [a.ready/'proof.json',a.ready/'manifest.json',Path(__file__),report]:manifest[str(f.resolve())]=sha(f)
 for f in a.output.iterdir():
  if f.is_file():manifest[str(f.resolve())]=sha(f)
 (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 proof=dict(passed=False,native_run=True,native_worker_released=True,launches=1,retries=0,ROM_sha256=run['ROM_sha256'],readiness_sha256=sha(a.ready/'proof.json'),script_sha256=sha(a.run/'run.lua'),original_failed_component_receipt_sha256=sha(a.run/'lifecycle-proof.json'),first_actual_start_snapshot_sha256=sha(a.run/'first-init-start-mismatch.json'),actual_failure_PPU=first['ppu'],actual_DMA_start=first['DMA_start'],actual_DMA_bytes_written=173,actual_OAMADDR=173,mask=30,hardware_source_current256_exact=True,late_real_DMA=True,completion_accounting_false_positive=False,visible_pixel_corruption_proven=False,actual_terminal_components=0,required_terminal_components=5,prefix_equivalence=prefix,actual_packet_sha256=sha(a.output/'actual-packet.json'),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),tool_sha256=sha(Path(__file__)),limits='ONE authorized diagnostic stops at unchanged predicate. Actual173 writes/pending DMA prove incomplete transfer at pre-render start; byte identity is already exact and later transfer/portrait pixels remain unobserved. No visible corruption or game clearance. Source-only narrower queue optimization may follow; no native retries/death/area/body/adoption.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=proof['manifest_sha256'],bindings=len(manifest)),indent=2))


if __name__=='__main__':main()
