"""Freeze the reviewed Tank source component; discard its duplicate ROM/debug."""
from pathlib import Path
import hashlib,json,re,shutil,sys,zipfile
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_source_1101_v1 import O,COMMIT,sha

def write(name,value):
 p=O/name;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(value,indent=2)+'\n' if not isinstance(value,str)else value)

def main():
 source=O/'source'
 identity=json.loads((O/'donor-identity.json').read_text())
 build=json.loads((O/'author-reproduction.json').read_text())
 cpu=json.loads((O/'rules-CPU-controls.json').read_text())
 assert build['passed']and cpu['passed']and build['changed_bytes']==0
 assert build['donor_sha256']==cpu['donor_sha256']==identity['donor_sha256']
 assert build['source_commit']==cpu['source_commit']==COMMIT
 own=['tools/audit/prepare_mario_tank_source_1101_v1.py','tools/audit/build_mario_tank_source_1101_v1.py','tools/audit/check_mario_tank_rules_1101_v1.py','tools/audit/freeze_mario_tank_source_1101_v1.py','tools/reference/mario_tank_rules_1101_v1.inc']
 for name,expected in cpu['bindings'].items():
  if name.startswith('tools/'):assert sha((R/name).read_bytes())==expected,(name,'stale CPU proof')
 inputs=[]
 for path in sorted(source.rglob('*')):
  if path.is_file():
   data=path.read_bytes();inputs.append(dict(path=path.relative_to(source).as_posix(),bytes=len(data),sha256=sha(data),Git_blob_SHA1=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()))
 write('source-inputs.json',dict(repository=identity['source_repository'],commit=COMMIT,inputs=inputs,reproduction='49 runtime assembly modules from author CMake graph; exact complete released-ROM identity, zero changed bytes.'))
 # Only concrete integration leaves are duplicated in the publication packet.
 # Full build graph is recoverable by its exact pinned paths and blob hashes.
 spans={
  'src/collision.s':[(291,327),(393,429),(950,1055),(1100,1161),(1220,1289),(1347,1373),(1400,1572),(1980,2134)],
  'src/tiles/brick.s':[(120,195),(199,270)],
  'src/objects/powerup.s':[(1,67)],
  'src/objects/fireball_bubble.s':[(1,59)],
  'src/sprite_render.s':[(230,276)],
  'src/screen_render.s':[(310,365)],
  'src/reset.s':[(153,179)],
  'src/gamecore.s':[(145,182)],
  'src/player.s':[(824,975),(978,1158),(1190,1241)],
  'inc/constants.inc':[(216,231)],
  'inc/metasprite.inc':[(1,140)],
 }
 excerpts=[]
 for name,ranges in spans.items():
  data=(source/name).read_text();lines=data.splitlines()
  for first,last in ranges:
   text='\n'.join(lines[first-1:last])+'\n'
   excerpts.append(dict(path=name,first_line=first,last_line=min(last,len(lines)),whole_file_sha256=sha((source/name).read_bytes()),text=text))
 write('original-hooks.json',dict(repository=identity['source_repository'],commit=COMMIT,excerpts=excerpts))
 body=(source/'chr/sprites_mario.chr').read_bytes();assert len(body)==4096
 (O/'mario-body.chr').write_bytes(body)
 donorbody=build['runtime_inputs']['chr/sprites_mario.chr'];assert sha(body)==donorbody
 symbols={}
 for line in (O/'rules.lbl').read_text().splitlines():
  m=re.fullmatch(r'al\s+([0-9A-Fa-f]+)\s+\.(Mt\w+)',line)
  if m and m[2]in['MtTileChecks','MtCellAction','MtContactPolicy','MtInjuryBlocked','MtPickupCycle','MtCollectUpgrade','MtWearBootsFlash','MtRulesEnd']:symbols[m[2]]=int(m[1],16)-0xc000
 assert symbols['MtRulesEnd']==197
 facts=[
  'AleFunky Mario the Tank1.0.2a, released2024-08-19; original disassembly doppelganger, ca65 port threecreepio, base changes jroweboy, inspiration Doogtoons.',
  'The author IPS replaces the Fire Flower icon with Lightning Boots. Native statuses remain small0, big1, boots2; the stale memory.inc comment suggesting status3 is incorrect.',
  'Small->big still uses native growth. A subsequent mushroom/flower pickup changes big1->boots2. Pickup erasure,1000points and pickup SFX are outer native owners.',
  'The boots pickup alternates four palette numbers every2frames. The recovered source contains no separate worn-boot-only flashing routine.',
  'Boots contact routes the ordinary enemy defeat effect after native collision prechecks, with the donor1000point award. ForceInjury ignores boots2; native death, exits and transitions still need their own host ownership.',
  'Boots head and side collisions destroy nonprotected cells, using native clearing/debris/50point/brick-shatter SFX. One RemovedTile budget per completed game update prevents multiple destructive writes; this is not a global frame or NMI flag.',
  'Destruction is not restricted to ordinary brick metatiles. The donor can also erase question/item blocks, without ordinary item release once boots are active. Preserve the authenticated protected-tile classification; never run destruction on support/foot probes.',
  'The donor still allows native B fireballs at status2. Boots do not replace jump/run/swim physics:1664 actual PlayerPhysicsSub cases produce identical AXYP/RAM for native big1 versus boots2.',
 ]
 adaptations=[
  'MtCellAction replaces the donor selector\'s caller-frame-discarding TXS with a returning action ABI. Never transplant that TXS across a host farcall.',
  'MtContactPolicy returns the original contact branch decision in carry. Native enemy defeat/score/SFX remain explicit host effect owners.',
  'MtWearBootsFlash applies the donor pickup palette cadence to a separately masked worn-boot OAM part, as requested by the user. Actual masked boot art, facing/pose mapping, palette and sprite budget remain integration work.',
 ]
 gates=[
  'No roster admission, host code/RAM/CHR lease, Main dispatch, options behavior or installed nightly changes are made by this component.',
  'Admit Tank identity before these helpers. Other roster characters can also use native PlayerStatus2 and must not acquire Tank immunity/destruction.',
  'Bind terrain probes, protected metatile attributes, native effect/score/SFX/VRAM queues and one-per-update RemovedTile state to actual host ownership. Do not transplant donor79A, four-brick arrays or R8 blindly.',
  'Every callback must honor host scratch and stack contracts. Observed standalone peak is9stack bytes including entryJSR for MtCellAction; this is not a host Main/ISR reserve proof.',
  'Real native opening, head/side/block/powerup/contact hazards, scrolling, underwater, pause/death/flag/lives scenes and both difficulty settings remain to qualify after integration.',
  'The linked user YouTube short was identified by primary references but its frames were not visually reviewed. Flashing cadence here is proven from reproduced original source/CPU, not a claimed video review.',
 ]
 report=dict(passed=True,stage='SOURCE_COMPONENT_ONLY',complete=False,playable_integration=False,host_mutated=False,native_emulator_run=False,donor=identity,author_build_receipt='author-reproduction.json',CPU_receipt='rules-CPU-controls.json',source_commit=COMMIT,
  code=dict(bytes=197,synthetic_test_origin='C000',host_lease_granted=False,entry_offsets=symbols),RAM_allocated=0,
  assets=dict(boots_pickup=dict(path='boots-pickup.chr',bytes=64,sha256=sha((O/'boots-pickup.chr').read_bytes()),source_bank=20,source_offset=896),mario_body=dict(path='mario-body.chr',bytes=4096,sha256=sha(body))),
  original_facts=facts,explicit_adaptations=adaptations,integration_gates=gates,
  import_contract=dict(fields=['PlayerStatus','RemovedTile','StarInvincibleTimer','Enemy_SprAttrib','GameEngineSubroutine(zp)','FrameCounter(zp)','ObjectOffset(zp)','PowerUpType(zp)'],scratch='R2 for pickup/worn flash; native palette callback also owns its normal R0/VRAM queue effects.',callbacks=dict(MtCheckClimb='Actual native metatile attribute classification; A preserved, X and flags as original.',MtGetPlayerColors='Native queued player palette update, no direct PPU writes.',MtSetPRout='Native growth/engine-routine transition, original A/Y contract.')),
  proofs=dict(exact_donor_build=True,objects=49,test_counts={k:v for k,v in cpu.items()if k.endswith('_cases')},measured_leaf_bounds=cpu['measured_leaf_bounds']),
  primary_sources=['https://romhackplaza.org/romhacks/mario-the-tank-nes','https://alefunky.dev/hacks/mario-the-tank/','https://www.smbarena.com/hack?id=3692&p=0','https://github.com/AleFunky/mariothetank/tree/'+COMMIT,'https://www.youtube.com/shorts/_v0GDYD8c28'],
  verification_scope='Source and assembled CPU only; no host claims. All test fixtures in memory and aggregate receipts only; no capture/video/per-frame files.',
  reproduced_ROM_retained=False,publication_exclusions=['Donor/full PRG ROM','author full debug','49 object files','whole author source tree','downloaded IPS'],
  source_files={name:sha((R/name).read_bytes())for name in own})
 # The discovery receipt predates the exact build; preserve it historically,
 # and make the later resolution explicit instead of silently rewriting it.
 report['discovery_identity_limit_superseded_by']='author-reproduction.json proves the earlier source-vs-patch identity open item: exact SHA and0 changed bytes.'
 write('handoff.json',report)
 prose='# Mario the Tank source component\n\nThe original release is reproduced byte-for-byte. The independently assembled197-byte rules module is ready for host integration review; Tank is not added to the roster by this work.\n\n'
 prose+='Donor SHA256: `'+build['donor_sha256']+'` (131088bytes, mapper4). The donor was reconstructed from the author IPS and an existing local SMB World ROM, normalizing only its16-byte header to the author-required base. No donor ROM download was used.\n\n'
 for title,items in [('Verified original behavior',facts),('Deliberate adaptations',adaptations),('Remaining integration gates',gates)]:
  prose+='## '+title+'\n\n'+'\n'.join('- '+item for item in items)+'\n\n'
 prose+='The strongest receipts are `author-reproduction.json` and `rules-CPU-controls.json`; `original-hooks.json` preserves exact source coordinates. Runtime input paths and Git blob hashes in `source-inputs.json` allow the declared compiler graph to be recovered without checking out unrelated tools.\n'
 write('handoff.md',prose)
 members={name:(R/name).read_bytes()for name in own}
 for name in['donor-identity.json','author-reproduction.json','author-commands.json','rules-CPU-controls.json','rules-assembly.json','source-inputs.json','original-hooks.json','handoff.json','handoff.md','rules.bin','rules.s','rules.cfg','rule-bindings.s','rules.lbl','boots-pickup.chr','mario-body.chr']:
  members['proof/'+name]=(O/name).read_bytes()
 packet=O/'source-and-proof.zip'
 with zipfile.ZipFile(packet,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for name,data in sorted(members.items()):
   info=zipfile.ZipInfo(name,date_time=(2026,11,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
 with zipfile.ZipFile(packet)as z:assert z.testzip()is None and len(z.namelist())==len(members)
 # Preserve sources and exact recipes, but release disposable complete ROM,
 # objects and full author debug before announcing a frozen source packet.
 discarded=[]
 author=O/'author-build'
 if author.exists():
  assert author.resolve().parent==O.resolve()and author.is_dir()and not author.is_symlink()
  discarded=[dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=sha(p.read_bytes()))for p in sorted(author.rglob('*'))if p.is_file()]
  shutil.rmtree(author)
 receipt=dict(passed=True,frozen=True,packet=dict(path=packet.relative_to(R).as_posix(),bytes=packet.stat().st_size,sha256=sha(packet.read_bytes()),members=len(members)),handoff_sha256=sha((O/'handoff.json').read_bytes()),source_files=report['source_files'],discarded_generated=dict(files=len(discarded),bytes=sum(p['bytes']for p in discarded),manifest=discarded),limits=dict(bytes=256000000,files=1000),no_further_source_edits=True)
 files=[p for p in O.rglob('*')if p.is_file()];receipt['retained_output_before_freeze_receipt']=dict(files=len(files),bytes=sum(p.stat().st_size for p in files))
 write('freeze.json',receipt);print(json.dumps({k:v for k,v in receipt.items()if k not in['discarded_generated','source_files']}))

if __name__=='__main__':main()
