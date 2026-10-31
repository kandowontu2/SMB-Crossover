"""Freeze the private contact/lives/jump successor, with unchanged parent proofs."""
from pathlib import Path
import difflib,hashlib,json,re,shutil,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from check_tmnt_render_oa import load,address,location
P=R/'build/bowser-current64-v3';O=R/'build/bowser-playable-jump-v1';J=O/'joint'
C=R/'docs/qa/checkpoints/2026-10-31/bowser-playable-contact-jump-source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
CONTROL_DIRS=['bowser-playable-contact-controls-v1','bowser-playable-natural-expiry-v1',
 'bowser-playable-cold-controls-v1','bowser-playable-body-geometry-v1',
 'bowser-playable-fire-contact-v1','bowser-playable-lives-vectors-v3',
 'bowser-playable-loader-controls-v1']

def main():
 assert not(O/'handoff.json').exists()and not C.exists()
 parent=json.loads((P/'handoff.json').read_text());stage=json.loads((O/'source-stage.json').read_text())
 assert stage['candidate']==sha(J/'candidate.nes')=='c6635815711a624a02c4337cd9f1830ca9c43b14a824f2ea51963f796ad98c2a'
 files={Path(__file__),P/'handoff.json'}
 for manifest in[parent,stage]:
  for f,h in manifest['bindings'].items():assert sha(f)==h,('pre-freeze binding',f);files.add(Path(f))
 controls=[]
 for name in CONTROL_DIRS:
  p=R/'build'/name/'controls.json';q=json.loads(p.read_text());assert q['passed'],p
  files.add(p);controls.append(dict(path=str(p),sha256=sha(p)))
  for f,h in q['bindings'].items():assert sha(f)==h,('actual consumer binding',f);files.add(Path(f))
 route=R/'build/bowser-playable-route-analysis-v3/analysis.json';r=json.loads(route.read_text())
 assert r['route_clear']and r['next_area_Main']==25 and r['completed_Main']==4326
 assert all(row['HP']>0 for row in r['rows'])and r['rows'][-1]['HP']==2
 for f,h in r['bindings'].items():assert sha(f)==h,f;files.add(Path(f))
 files.add(route)
 # Bind all actual new source/object/command inputs, and inherited transitive
 # producers through the immutable current64 handoff. No old output is replayed.
 for p in J.rglob('*'):
  if p.is_file()and p.suffix.lower()in['.s','.asm','.inc','.cfg','.chr','.rle','.dep','.d','.o']:files.add(p)
 for p in O.glob('*.json'):files.add(p)
 for line in(J/'candidate.dbg').read_text().splitlines():
  if line.startswith('file\t'):
   p=Path(re.search(r'name="([^"]+)"',line).group(1));p=p if p.is_absolute()else R/p
   assert p.is_file(),p;files.add(p)
 files|={J/n for n in['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','candidate.cv3-mirror.json','bowser.bin','ram3.bin','ff-cookie.bin','code.bin','data.bin','source-stage.json']}
 files|={p for p in(J/'bowser').iterdir()if p.is_file()}
 tools={Path(__file__)}|set((R/'tools/audit').glob('bowser_playable_*.py'))|{R/'tools/audit/prepare_bowser_playable_jump_v1.py'}
 files|=tools
 negatives=[]
 for root in R.glob('build/bowser-*'):
  for p in root.glob('*.json'):
   try:q=json.loads(p.read_text())
   except(ValueError,UnicodeError):continue
   if isinstance(q,dict)and(q.get('passed')is False or q.get('returncode',0)!=0 or q.get('route_clear')is False):
    files.add(p);negatives.append(dict(path=str(p),sha256=sha(p),error=q.get('error',q.get('endpoint',q.get('stderr','')))))
 save(O/'retained-negatives.json',dict(negatives=negatives,
  lives_fixture_corrections='v1 generic helper X7/Y91 was not the actual native portrait caller X=E9/Y0. v2 then compared old/new distinct program+cookie images across candidates; v3 preserves each original image and compares the native callback/foreign banks. Assertions on AXYP, OAM, live vectors and all33SMC remain.',
  route_fixture_correction='v2 stopped at X3266 while native engine5 was still tallying/raising flag. v3 keeps240 active same-X watchdog and240 automatic-without-task/timer/object/music-progress watchdog; native task progress reaches genuine1-2.'))
 b=load(J/'candidate.nes');old=load(P/'joint/candidate.nes')
 residents=[]
 for name,limit in[('BW_ROM_LOAD',224),('BW_ROM_COPY',221),('BW_ROM_CHECK',215),('BW_ROM_ROUTER',213),('BW_ROM_AUX',204),('BW_ROM_PREVIEW',204)]:
  seg=next(v for v in b['segs'].values()if v['name'].strip('"')==name)
  used=int(seg['size'],0);assert used<=limit;residents.append(dict(name=name,start=int(seg['start'],0),used=used,granted=limit))
 assert sum(x['used']for x in residents)==1223 and sum(x['granted']for x in residents)==1281
 for n in ['ram3.bin','ff-cookie.bin','code.bin','data.bin']:assert sha(J/n)==sha(P/'joint'/n)
 # Complete common/menu/Main/current64 inputs remain byte-identical. The only
 # cartridge edits are the own portrait island, expected cookie constants and
 # the source-produced code carrier; assertions are also in the actual builder.
 for n in ['entrypoint.s','union.s','src/new_roster_dispatch.s','src/character_select.s','src/mmc5.s','screen_render.s','private.cfg']:
  assert(J/n).read_bytes()==(P/'joint'/n).read_bytes(),('unrelated own/current64 source',n)
 for n in ['BwColdPrepare','BwColdDraw','BwStatus','BwMovement','BwGraphics','BwScene','BwMenuResolve','BwServiceVeneers','BwStartFlags','BwBtResolve']:
  assert(address(b,n),location(b,n))==(address(old,n),location(old,n)),n
 lo=address(b,'Bw1Gravity')-0xa000;hi=address(b,'BwCoreEnd')-0xa000
 assert(J/'bowser.bin').read_bytes()[lo:hi]==(P/'joint/bowser.bin').read_bytes()[lo:hi]
 patch=[]
 for n in ['host.s','cold.s','core.s']:
  patch.extend(difflib.unified_diff((P/'joint/bowser'/n).read_text().splitlines(True),(J/'bowser'/n).read_text().splitlines(True),fromfile='frozen9529/bowser/'+n,tofile='playable-c663/bowser/'+n))
 (O/'source.patch').write_text(''.join(patch),encoding='utf-8')
 api=json.loads((P/'native-smoke-API.json').read_text());api.update(candidate=stage['candidate'],joint=str(J),parent=parent['candidate'],native=False,
  geometry='SMB3 standing11 8x16 parts (other original poses up to12), SMB1 standing7; native16x32 collision. Lives only+8Y, nativePlayerY restored. Select/gameplay unchanged.',
  injuries='Native service6 returns HP, then ForceInjury reaches service5; native interval8 protection expires naturally after149 measured wholeMain; death only HP0.',
  source1_jump='Explicit playable A-edge -3 initial velocity, rise80 vs originalNPC -2/rise37; original falling/gravity/fraction bytes unchanged.',
  source_CPU_route=dict(form='SMB1',updates=4326,endpoint='real1-2+25controlledMain',deaths=0,HP=2,pipes=[32,48,64,64]),
  no_claims=['No native test of this exact successor yet','SourceCPU route is not a native1-1 claim','No perfect campaign/extended attacks/original SMB3 audio','Inherited FF419 deadline not fixed'])
 save(O/'native-smoke-API.json',api)
 save(O/'freeze-proof.json',dict(passed=True,source=True,native=False,candidate=stage['candidate'],parent=parent['candidate'],controls=controls,route=dict(path=str(route),sha256=sha(route)),
  resident=residents,resident_used=1223,resident_granted=1281,headroom=58,portrait_used=203,portrait_granted=204,
  changed_ROM_bytes=81,all_other_sources_and_current64_payloads_exact=True,original_falling_gravity_fraction_bytes_exact=True,all_public_PCs_preserved=True,
  actual_new_lives_flags=256,actual_new_lives_vectors=864,all16_cookie_poison_flag_pairs=1024,
  unchanged_shared_proof_reuse='Parent9529 shared transport/menu/foreign/vector receipts stay bound; shared instructions/maps/entries/targets are byte-identical, only own expected fingerprint is updated. New actual loader/cold/Main/pose/fire/contact/lives proofs bindc663.'))
 save(O/'verified-source-stage.json',dict(stage,status='FUNCTIONAL_CONTACT_LIVES_JUMP_SOURCE_NATIVE_PENDING',source_controls_pass=True,installed=False,publication_allowed=False))
 note='''Private current64+Bowser2 SOURCE WIP, exact c6635815 successor of frozen9529.

The native status caller treated tier0 as death before service5. Status now
returns actual sourceHP; 128 real allflag injury-status/ForceInjury paths and
protected recontacts pass. Repeated source contacts reach death only atHP0.
The prior90 was a native interval timer, approximately1890updates. Genuine
native8 intervals now expire naturally after149 wholeMain in measured cold
cohorts, with a real second contact loweringHP. No timer result is injected.

Only lives portraits move8px down inside the genuine own draw call, with
nativePlayerY restored afterward. Selection/gameplay coordinates, native
palettes and original7/11standing parts are unchanged. The new helper fits
203/204B and passes256flags/864realnormal/lag/pause/legalIRQ cases including
all33SMC, livepage1, rawmaps and returnedAXYP/SP. Two fixture negatives remain.

OriginalNPC SMB1 Bowser -2jump rose37px and could not cross actual48/64px
pipes. Explicit playable A-edge -3 now rises80px; all literal falling/gravity/
fraction instructions are byte-exact. Ordinary-input sourceCPU traversal
clears the32/48/64/64px pipes, gaps/stairs, completes native flag/timer/castle
logic and reaches genuine1-2 plus25controlledMain:4326wholeMain, no deaths,
HP2. The old240same-X automatic-tally fixture failure remains. New fixture
keeps240active-same-X and240automatic-without-any-task/timer/object/music-
progress watchdogs. This is a sourceCPU route, not a native campaign claim.

Actual cold/menu/Start/fullparser/entrance and120Main per form, all26 original
pose/facing tuples,36 native firecontact cases, updated full8KBloader/readback
and1024all16cookiepoison flag pairs pass. The unchanged parent shared/menu/
foreign proofs are bound separately; no fictional rerun on altered inputs.

Only81 own ROMbytes differ from9529. Resident1223/1281B,58B fragmented spare;
no new grant/globalRAM/ZP/CHR. Header, foreignCHR, current64 source/publicPCs,
Benj7variants/Peachconstants, FF/Quick/Arpayloads/cookies are byte-exact. Old
9529 native evidence and all source/fixture negatives stay immutable. Exact
successor native review and installation remain root-owned. Lag is accepted
WIP; extended boss attacks, originalSMB3audio/perfectcampaign are deferred.
Inherited FF419 render deadline is not fixed. No install performed.
'''
 (O/'HANDOFF.txt').write_text(note,encoding='utf-8')
 files|={O/n for n in['source.patch','retained-negatives.json','native-smoke-API.json','freeze-proof.json','verified-source-stage.json','HANDOFF.txt']}
 files.add(O/'source-stage.json')
 archive=O/'source-only.zip';ext={'.s','.asm','.inc','.cfg','.chr','.rle','.dep','.d','.py','.json','.txt','.patch','.md','.lua'};members=[]
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(files):
   if p.suffix.lower()in ext or p.name in['cookie.bin','ff-cookie.bin']or p==J/'bowser.bin':
    rel=p.relative_to(R).as_posix();z.write(p,rel);members.append(rel)
 files.add(archive)
 result=dict(source=True,status='FROZEN_CURRENT64_BOWSER_CONTACT_LIVES_PLAYABLE_JUMP_SOURCE',candidate=stage['candidate'],parent=parent['candidate'],joint=str(J),source_stage=str(J/'source-stage.json'),ready=66,native=False,installed=False,admitted=False,publication_allowed=False,resident_used=1223,resident_granted=1281,resident_headroom=58,source_archive_members=len(members),FF419_fixed=False,bindings={str(p.resolve()):sha(p)for p in sorted(files)})
 save(O/'handoff.json',result)
 for f,h in result['bindings'].items():assert sha(f)==h,('post-freeze binding',f)
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for n in z.namelist():assert hashlib.sha256(z.read(n)).hexdigest()==sha(R/n),n
 C.mkdir(parents=True)
 for n in['handoff.json','source-only.zip','HANDOFF.txt','source.patch','native-smoke-API.json','freeze-proof.json','retained-negatives.json']:
  shutil.copyfile(O/n,C/n)
 for item in controls:
  p=Path(item['path']);q=json.loads(p.read_text());compact={k:v for k,v in q.items()if k not in['rows','vectors','cohorts','bindings','flags','contacts','expiry','UI']}
  compact.update(full_receipt=str(p),full_receipt_sha256=sha(p));save(C/(p.parent.name+'.json'),compact)
 save(C/'source-route-summary.json',dict(source_CPU=True,native=False,route_clear=True,full_receipt=str(route),sha256=sha(route),updates=4326,HP=2,next_area_Main=25,pipes=[32,48,64,64]))
 save(C/'receipt.json',dict(status=result['status'],candidate=result['candidate'],handoff=sha(O/'handoff.json'),bindings={str(p.resolve()):sha(p)for p in sorted(C.iterdir())},verified_bindings=len(files),archive_members=len(members)))
 owned=[str(p.relative_to(R)).replace('\\','/')for p in sorted(tools|set(C.iterdir()))]+[str((C/'owned-files.txt').relative_to(R)).replace('\\','/')]
 (C/'owned-files.txt').write_text('\n'.join(owned)+'\n',encoding='utf-8')
 print(json.dumps(dict(handoff=str(O/'handoff.json'),SHA256=sha(O/'handoff.json'),candidate=result['candidate'],bindings=len(files),archive_members=len(members),checkpoint=str(C),checkpoint_sha256=sha(C/'receipt.json'))))
if __name__=='__main__':main()
