"""Freeze surgical own P0/name adoption; shared source and readiness exact."""
from pathlib import Path
import hashlib,json,re,shutil,zipfile
R=Path(__file__).resolve().parents[2];P=R/'build/cf-cold-warm-source-v3';O=R/'build/cf-cold-warm-palette-source-v1';J=O/'joint';D=R/'docs/qa/checkpoints/2026-10-31/cf-cold-warm-palette-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

def main():
 assert not(O/'handoff.json').exists()and not D.exists();files={Path(__file__)}
 for p in[P/'handoff.json',R/'build/contra-force-palette-names-qualified-v1/handoff.json',O/'source-stage.json']:
  q=json.loads(p.read_text());files.add(p)
  for f,h in q['bindings'].items():assert sha(f)==h,('immutable input',f);files.add(Path(f))
 stage=json.loads((O/'source-stage.json').read_text());assert stage['candidate']==sha(J/'candidate.nes')=='ef2f11e232ec878c277245c3802bcf8a415415e38507c26feefaef3744c1bee1'
 receipts=[]
 for n in['cf-cold-warm-palette-parser-controls-v1','contra-force-cold-warm-palette-rebind-v1','contra-force-cold-warm-palette-rebind-isr-v1']:
  p=R/'build'/n/'controls.json';q=json.loads(p.read_text());assert q['passed'],p;files.add(p);receipts.append(dict(path=str(p),sha256=sha(p)))
  for f,h in q['bindings'].items():assert sha(f)==h,('exact consumer input',f);files.add(Path(f))
 for p in J.rglob('*'):
  if p.is_file()and p.suffix.lower()in['.s','.asm','.inc','.cfg','.chr','.rle','.dep','.d','.o','.bin']:files.add(p)
 for line in(J/'candidate.dbg').read_text().splitlines():
  if line.startswith('file\t'):
   p=Path(re.search(r'name="([^"]+)"',line).group(1));p=p if p.is_absolute()else R/p;assert p.is_file(),p;files.add(p)
 files|=set(O.glob('*.json'))|{J/n for n in['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','source-stage.json']}
 tools={Path(__file__),R/'tools/audit/prepare_cf_cold_warm_palette_source_v1.py',R/'tools/audit/cf_cold_warm_palette_parser_controls_v1.py'};files|=tools
 api=json.loads((P/'integration-api.json').read_text());api.update(candidate=stage['candidate'],parent=stage['parent'],source_stage=str(J/'source-stage.json'),actual_link_recipe=str(O/'final-link.json'),own_P0_name_source='e82eafd5f921793c7eebde4cefde7ab2f46ffc223c027b45d7712b1394114547',source_controls=receipts)
 api['remaining']=['Pre-load genuine ROM name18 fallback and correct readyCF preview path remain unimplemented','P1 yellow-shot fairness proposal unadopted; no sharedmailbox/NMI hook','CF/BTpending/current66readiness exact; no native/install/admission']
 api['own_rows_added']={'17':'Actual source idle portrait also queues originalP0','18':'Authenticated RAM3 full16char BURNS/SMITH/IRON/BEANS; ROM-only pre-load fallback stillneeded','26':'Bounded native3F10 length4 universalBG+original37/12/0F; fullqueue defersdirty','29':'Dirty P0 retry, noP1 heartbeat','30':'A0 nativeHUD names; actual A1/Y30 after30B native lives text appends7B blackBG/originalP0,37Btotal','32':'Genuine native worldP3 area policy without world recolor'}
 save(O/'integration-api.json',api)
 proof=dict(source=True,passed=True,candidate=stage['candidate'],parent=stage['parent'],ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,admitted=False,own_CF_source='e82eafd5f921793c7eebde4cefde7ab2f46ffc223c027b45d7712b1394114547',actual_rebuilt_objects=stage['actual_rebound_four_objects'],changed_bytes=2693,exact_changed_envelopes=stage['exact_changed_envelopes'],all_parent_linkedPCs_exact=True,shared_Main_BW_BT_17B_42B_helpers_byteexact=True,all_other_ROM_CHR_header_Quick_Ar_FF_BW_images_and_cookies_exact=True,no_new_state_spans_shared_P1_or_NMI_hook=True,
  actual_CF_parser_classes=4,actual_CF_Main=128,pending_Start_blocks_observed=4,explicit_future_frontend_identity_projection_only=True,no_guest_RAM_Ready_cookie_physics_preload=True,
  own_actual_PPU=16,own_fullqueue_retry=4,own_menu_HUD=16,own_actual_WriteGameText_late30=4,own_world_index=4,own_lagNMI_IRQ_seams=20,own_completed_normalNMI_flushes=5,source_controls=receipts,remaining=api['remaining'])
 save(O/'freeze-proof.json',proof)
 (O/'HANDOFF.txt').write_text('''Surgical own CF P0/name source child of frozen8f0a.

Candidate ef2f11e232ec878c277245c3802bcf8a415415e38507c26feefaef3744c1bee1.
Uses exact e82e own four producers/two assets; source cold/warm policy141b
is retained. Only2693 bytes change: two16B expected fingerprint constants
and the24KB source carrier. All current linkedPCs, header, otherCHR, shared
Main/BW/BT source and17+42B cold helpers, existing host images/cookies stay
exact. No cfg span, state, NMI/mailbox/P1 or readiness addition.

Own actual rows18/26/29/30/32 now implement fullsource names, boundedP0,
dirty retry, real late lives text and nativeworld policy. Source portrait17
queues originalP0. Lives30 follows genuine30B text with7B black universal+
originalbodyP0, total37B. Exact producer/queue/nativeconsumer/sourceAPI
details are in the bound e82e packet and integration-api.json.

Targeted current source tests pass:16 actualPPU body/background cases,
4 fullqueue retries,16menu/HUD,4actual WriteGameText late30 consumers,
4native worldindices,20declared real lagNMI/IRQ entryseams and5completed
normalNMI flushes. Four parser cohorts first prove pending Start blocks,
then explicitly project only future frontend identity31 to actual native
ready-block/ChkContinue/fullparser/entrance/128Main. No guestRAM/Ready/cookie/
physics is preloaded; this is NOT natural-ready-menu or admission proof.

CF and BT remainpending;66 existing readiness exact. ROM-only pre-load name18
fallback and future readyCF preview stillneed sourcejoin. YellowP1 shot
ownership/fairness is separate and unadopted. Root owns native/install.
All actual build/link commands and guarded outputs are bound. No fullROM
in source-only.zip; exact replayable source/dependencies are included.
''',encoding='utf-8')
 files|={O/n for n in['integration-api.json','freeze-proof.json','HANDOFF.txt']}
 archive=O/'source-only.zip';members=[];ext={'.s','.asm','.inc','.cfg','.chr','.rle','.dep','.d','.py','.json','.txt','.patch','.md','.lua'}
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(files):
   if p.suffix.lower()in ext or p.suffix.lower()=='.bin'and p.stat().st_size<=65536:
    rel=p.relative_to(R).as_posix();z.write(p,rel);members.append(rel)
 files.add(archive)
 out=dict(source=True,status='FROZEN_PENDING_CF_COLD_WARM_P0_NAMES_SOURCE',candidate=stage['candidate'],parent=stage['parent'],joint=str(J),source_stage=str(J/'source-stage.json'),ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,admitted=False,publication_allowed=False,source_archive_members=len(members),bindings={str(p.resolve()):sha(p)for p in sorted(files)})
 save(O/'handoff.json',out)
 for f,h in out['bindings'].items():assert sha(f)==h,('postfreeze',f)
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for n in z.namelist():assert hashlib.sha256(z.read(n)).hexdigest()==sha(R/n),n
 D.mkdir(parents=True)
 for n in['handoff.json','source-only.zip','integration-api.json','freeze-proof.json','HANDOFF.txt']:shutil.copyfile(O/n,D/n)
 for row in receipts:
  p=Path(row['path']);q=json.loads(p.read_text());compact={k:v for k,v in q.items()if k not in['cohorts','checks','rows','vectors','bindings']};compact.update(full_receipt=str(p),sha256=sha(p));save(D/(p.parent.name+'.json'),compact)
 save(D/'receipt.json',dict(source=True,candidate=out['candidate'],handoff=sha(O/'handoff.json'),verified_bindings=len(files),archive_members=len(members),bindings={str(p.resolve()):sha(p)for p in sorted(D.iterdir())}))
 owned=tools|set(D.iterdir())|{D/'owned-files.txt'};(D/'owned-files.txt').write_text('\n'.join(p.relative_to(R).as_posix()for p in sorted(owned))+'\n')
 print(json.dumps(dict(handoff=str(O/'handoff.json'),SHA256=sha(O/'handoff.json'),candidate=out['candidate'],bindings=len(files),archive_members=len(members),checkpoint=str(D),receiptSHA256=sha(D/'receipt.json'))))
if __name__=='__main__':main()
