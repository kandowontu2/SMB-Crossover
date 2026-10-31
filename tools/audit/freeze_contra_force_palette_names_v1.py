"""Freeze own CF P0/name/status source successor; no shared cold/readiness claim."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];P=R/'build/contra-force-palette-names-cart-v2';K=R/'build/contra-force-palette-names-kernel-v3';O=R/'build/contra-force-palette-names-qualified-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();bindings={};inputs=[P/'source-stage.json',K/'build-proof.json',R/'build/contra-force-palette-names-controls-v2/controls.json',R/'build/contra-force-palette-names-isr-v1/controls.json']
 for p in inputs:
  d=json.loads(p.read_text());assert d['passed']
  for f,h in d['bindings'].items():assert sha(f)==h,f;bindings[f]=h
  bindings[str(p.resolve())]=sha(p)
 api=json.loads((R/'build/contra-force-lifecycle-qualified-v1/api-and-scope.json').read_text());api.update(status='SOURCE_BODY_PALETTE_NAMES_PRESENTATION_LIFECYCLE_PENDING_YELLOW_SHOT_P1',candidate=sha(P/'joint/candidate.nes'),joint=str((P/'joint').resolve()),source_stage=str(P/'source-stage.json'),kernel=str(K),kernel_producer='tools/audit/prepare_contra_force_palette_names_kernel_v3.py',cart_producer='tools/audit/prepare_contra_force_palette_names_cart_v2.py')
 producers=[P/'joint'/n for n in ['cf-loader.s','cf-guard.s','cf-carrier.s','cf-retire.s','cf-stream.bin','cf-cookie.bin']];api['actual_six_cart_producers']={str(p.resolve()):sha(p)for p in producers}
 api['service_rows'].update({'18':'Own authenticated source menu16-char BURNS/SMITH/IRON/BEANS, original native charset, no pending-star; current pre-load menu still needs ROM FmQueueName/no RAM entry.','26':'Forced bounded3F10/4 body palette with exact original37/12/0F and native BackgroundColorCtrl/AreaType universal value, fullqueue sets dirty/no writes.','29':'Dirty palette retry; no yellowP1 heartbeat yet.','30':'ActualA0 HUD7-char names preserving originalXY/A; actualA1/Y30 late originalWriteGameText appends black lives/originalP0 AFTER30B native text.','32':'Exact genuine native13B worldP3-index policy using AreaType/R0/Y, no P2/P3 recolor.'})
 api['presentation_palette']='Portrait17 queues original P0, then authentic body renderer. Actual original WriteGameText natural typed30 on this cart outputs37B with complete black/lives packet after the native30B message for all4classes.'
 api['new_code']='370B appended ownA3 BC47..<BDB9. No new state/CHR/shared hook/lease. DDB8 last-life and all prior C2 bodymeta remain exact. ExistingA1 freeBF10..<C000240B; A3 tailBDB9..<BFE0551B can be split by routine boundary for future UNADOPTED598B P1 plan.'
 api['pending']=['Natural cold/shared menu→load/ensure/readiness owned by sibling; sibling8f0a lifecycle uses older141bpayload until this source is adopted','Exact yellow-shot P1 whole-object policy still unadopted; source loan-requiring objects remain hidden','Pre-load ROM-only menu preview/name must stay genuine nativeCF menu paths','No native emulator/whole-level admission claim']
 (O/'api-and-scope.json').write_text(json.dumps(api,indent=2)+'\n')
 negative=[R/'build/contra-force-palette-names-kernel-v1/negative.json',R/'build/contra-force-palette-names-controls-v1/controls.json']
 files={Path(__file__),*inputs,*producers,*negative,O/'api-and-scope.json',R/'build/contra-force-lifecycle-qualified-v1/handoff.json'}
 for root in [P,K]:files|={p for p in root.rglob('*')if p.is_file()and p.suffix in ['.s','.inc','.cfg','.dep','.json']}
 for n in ['contra_force_host_render_v4.s','contra_force_a2_router_v6.s','contra_force_host_palette_names_v2.s']:files.add(R/'tools/reference'/n)
 for n in ['prepare_contra_force_palette_names_kernel_v3.py','prepare_contra_force_palette_names_cart_v2.py','contra_force_palette_names_controls_v2.py','contra_force_palette_names_isr_v1.py']:files.add(R/'tools/audit'/n)
 z=O/'source-delta-only.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as a:
  for p in sorted(files):a.write(p,p.relative_to(R).as_posix())
 for p in files|{z}:bindings[str(p.resolve())]=sha(p)
 for f,h in bindings.items():assert sha(f)==h,f
 out=dict(passed=True,native=False,ready=False,candidate=api['candidate'],source_stage=str(P/'source-stage.json'),API=api,source_delta_zip_sha256=sha(z),source_delta_zip_members=len(files),source_delta_zip_bytes=z.stat().st_size,retained_negatives=[str(p)for p in negative],bindings=bindings)
 p=O/'handoff.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),candidate=api['candidate'],bindings=len(bindings),members=len(files),bytes=z.stat().st_size)),flush=True)
if __name__=='__main__':main()
