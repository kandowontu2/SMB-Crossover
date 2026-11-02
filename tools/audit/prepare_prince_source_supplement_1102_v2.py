"""Compact extension checkpoint, retaining the prior frozen source ZIP."""
from pathlib import Path
import hashlib,json,zipfile
import recover_prince_core_1101_v1 as B
R,O=B.R,B.O
SOURCES=[
 'tools/reference/prince_lzss_decoder_1102_v1.s',
 'tools/reference/prince_host_point_1102_v1.s',
 'tools/reference/prince_host_render_1102_v1.s',
 *['tools/audit/'+n for n in [
 'check_prince_mac_pad_ingress_1102_v2.py','measure_prince_lossless_storage_1102_v1.py',
 'recover_prince_fall_contact_1102_v2.py','check_prince_fall_contact_1102_v2.py',
 'check_prince_fall_sequence_1102_v2.py','measure_prince_fall_storage_1102_v2.py',
 'audit_prince_actor_writes_1102_v1.py','check_prince_host_point_1102_v1.py',
 'check_prince_motion_envelope_1102_v1.py','recover_prince_landing_1102_v3.py',
 'check_prince_landing_1102_v3.py','check_prince_landing_sequence_1102_v3.py',
 'recover_prince_contact_1102_v4.py','check_prince_contact_1102_v4.py',
 'check_prince_contact_sequence_1102_v4.py','check_prince_host_render_1102_v1.py',
 'check_prince_contact_point_1102_v2.py','measure_prince_host_storage_1102_v3.py',
 'audit_prince_room_raster_1102_v1.py','prepare_prince_source_supplement_1102_v2.py']],
 'docs/qa/prince-source-core-1101-v1.md']
RECEIPTS=['resident-pad-ingress-v2.json','resident-pad-consumers-v2.json',
 'fall-contact-recovery.json','fall-contact-CPU.json','fall-contact-sequence-CPU.json',
 'fall-lossless-storage-cost.json','actor-writer-authority.json','motion-envelope.json',
 'landing-recovery.json','landing-CPU.json','landing-sequence-CPU.json',
 'contact-recovery.json','contact-CPU.json','contact-sequence-CPU.json',
 'contact-point-CPU.json','host-render-CPU.json','host-private-layout.json',
 'host-lossless-storage-cost.json','source-room-raster.json']


def main():
 files={n:(R/n).read_bytes()for n in SOURCES};thin={}
 for n in RECEIPTS:
  q=json.loads((O/n).read_text());q.pop('instructions',None);q.pop('sequences',None)
  if n=='motion-envelope.json':
   for row in q['rows']:row.pop('trace')
  thin[n]=q
 files['receipts/supplement-proofs.json']=json.dumps(thin,separators=(',',':')).encode()
 parent=O/'source-checkpoint.zip';assert hashlib.sha256(parent.read_bytes()).hexdigest()=='2d9ec3124b61ccfb8a06fe616206d09ca5d0fd8d2b97a014a778db2d98b62e21'
 for n in ['common-cold-1102-v1.json','roster-rebase-1102-v3.json']:
  file=R/'docs/qa/allocations'/n;files[file.relative_to(R).as_posix()]=file.read_bytes()
 manifest=dict(source_checkpoint_only=True,ROM_DBG_not_included=True,requires_frozen_parent_checkpoint_SHA256=hashlib.sha256(parent.read_bytes()).hexdigest(),explicit_commit_files=SOURCES,receipt_source_files=RECEIPTS,large_generated_tables_omitted=['recovery.instructions','CPU.sequences','motion-envelope.rows.trace'],members={n:dict(bytes=len(v),SHA256=hashlib.sha256(v).hexdigest())for n,v in files.items()},scope='Exact original landing/ledge/fullcontact/HP closure, compact branch relocation, native point/renderer CPU/ISR qualification and lossless payload measurement. World/update/camera/health/combat callback bindings and native identity remain incomplete. Original donor and existing repository dependencies are required; no trees are bundled.')
 files['manifest.json']=json.dumps(manifest,indent=2).encode();target=O/'source-supplement-v2.zip'
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for n,v in files.items():z.writestr(n,v)
 assert target.stat().st_size<100000
 with zipfile.ZipFile(target)as z:
  assert z.testzip()is None
  for n,v in files.items():assert z.read(n)==v
 q=dict(passed=True,bytes=target.stat().st_size,SHA256=hashlib.sha256(target.read_bytes()).hexdigest(),members=len(files),ZIP=target.relative_to(R).as_posix(),explicit_commit_files=SOURCES,ROM_DBG_not_included=True)
 (O/'source-supplement-v2-manifest.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
