"""Proposed v49 typed cold, staged prefix, readback and full zeroing proof."""
from pathlib import Path
import contextlib,hashlib,io,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_sunny_rebase_1102_v54 as M
import check_prince_collision_services_1102_v56 as C
O=C.O


def main():
 base,_,_,_=M.bundle();C.H.W.PIN=M.PIN
 source=R/'tools/audit/check_prince_cold_worker_1102_v19.py';text=source.read_text();changes={
  'b=W.scoped_load(C.E.C.BASE)':'b=PROVIDED_BASE',
  '795,291]':'795,291,514]',
  'cold-pool-v19.bin':'cold-pool-v57.bin',
  'cold-worker-v19':'cold-worker-v57',
  'cold-decoder-v19':'cold-decoder-v25',
  'cold-worker-layout-v19.json':'cold-link-storage-v57.json',
  'native-runtime-v18.bin':'native-runtime-v49.bin',
  'native-metadata-v18.bin':'native-metadata-v49.bin',
  'expected=C.host(b)':'expected=HOST_SUCCESSOR(b)',
  'physical_spare=44032-len(payload)':'physical_spare=45056-len(payload)',
  'base_ROM_SHA256=C.E.C.PIN':'base_ROM_SHA256=SUCCESSOR_PIN',
  'C.E.C.BASE]':'SUCCESSOR_BASE]',
  "O/'cold-worker-CPU-v19.json'":"O/'collision-cold-CPU-v58.json'",
  'cold_worker_active=True':'cold_worker_active=True;prefix_cuts=set()',
  "if c.pc==life['PpHostInit']:original_init+=1":"""if 0xc65f<=c.pc<0xc678:
    prefix_cuts.add(c.pc)
    assert original_init==0 and not m.ram[2][0x1fe0]and not m.ram[3][0x1fe0]and c.p&4 and N.get(m,'DisableScreenFlag')and not N.get(m,'Mirror_PPUMASK')&24 and m[0x2001]==0
    if c.pc==0xc65f and activation=='audio-prefix':m.corrupt_at=corruption
   if c.pc==life['PpHostInit']:original_init+=1""",
  'distinct_cold_worker_instruction_PC=len(worker_cuts)':'distinct_cold_worker_instruction_PC=len(worker_cuts),distinct_staged_prefix_instruction_PC=len(prefix_cuts)',
  "('decoded-metadata-readback',(2,0x800),'metadata-output')":"('decoded-metadata-readback',(2,0x800),'metadata-output'),('audio-prefix-destination-readback',(2,0x780),'audio-prefix')",
 }
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 env=dict(__file__=str(source),__name__='prince_collision_cold_v58',PROVIDED_BASE=base,HOST_SUCCESSOR=C.host,SUCCESSOR_PIN=M.PIN,SUCCESSOR_BASE=M.BASE);exec(compile(text,str(source),'exec'),env)
 try:
  with contextlib.redirect_stdout(io.StringIO()):env['main']()
 except AssertionError:
  import traceback
  frame=sys.exc_info()[2]
  while frame.tb_next:frame=frame.tb_next
  local=frame.tb_frame.f_locals;machine=local.get('m');metadata=local.get('metadata',b'')
  negative=dict(qualified=False,failing_assertion=text.splitlines()[frame.tb_lineno-1],positive=local.get('positive'),metadata_differences=[dict(CPU=0xc800+i,expected=a,actual=z)for i,(a,z)in enumerate(zip(metadata,machine.ram[2][0x800:]))if a!=z]if machine else [],storage_receipt_SHA256=hashlib.sha256((O/'cold-link-storage-v57.json').read_bytes()).hexdigest(),storage_streams=json.loads((O/'cold-link-storage-v57.json').read_text())['decoded_images'])
  (O/'collision-cold-negative-v58.json').write_text(json.dumps(negative,indent=2)+'\n');print('Proposed cold failure:',negative['failing_assertion'],negative['metadata_differences'][:5]);raise
 file=O/'collision-cold-CPU-v58.json';q=json.loads(file.read_text());assert q['passed']and q['positive']['distinct_staged_prefix_instruction_PC']>0
 q.update(private_proposal_only=True,new_execution_granted=False,physical_pool_pages=44,live_metadata_end=0xdfce,shared_clock_untouched=[0xdfd0,0xdfd3],qualified_fixture_SHA256=hashlib.sha256(text.encode()).hexdigest(),proposed_staged_prefix_PC_half_open=[0xc65f,0xc678],audio_code_copy_and_readback_half_open=[0xc780,0xc800],scope='Actual current16a9 native instructions execute proposed44carrier worker and three lossless streams, then position-independent stagedC65F prefix copies/readbacks128B C780 audio code before source zeroing/constructor. Every prefix instruction runs uninitialized, SEI, forcedblank and both headers invalid. Five corruption cases including audio readback fail closed; complete resulting live source/code state equals genuine fresh constructor. Execution extensions remain proposals, not admitted; no shared manager/auth mutation, ROM, menu, emulator or fullstage/install claim.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'collision-services-CPU-v56.json',O/'cold-link-storage-v57.json',O/'native-runtime-v49.bin',O/'native-metadata-v49.bin',O/'native-state-v49.bin',O/'quiet-audio-code-proposal-v48.json']});file.write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps({k:q[k]for k in ['passed','base_ROM_SHA256','physical_spare','positive','cold_guard_rejections','proposed_staged_prefix_PC_half_open','audio_code_copy_and_readback_half_open']}))


if __name__=='__main__':main()
