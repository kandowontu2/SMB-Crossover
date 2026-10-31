"""Freeze the actual two-form Bowser WIP, its genuine producers and controls."""
from pathlib import Path
import difflib,hashlib,json,re,shutil,sys,zipfile

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from check_tmnt_render_oa import load,address
P=R/'build/peach-palette-fix-1030-v1'
O=R/'build/bowser-current64-v3';J=O/'joint'
C=R/'docs/qa/checkpoints/2026-10-31/bowser-current64-functional-source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

CONTROL_DIRS=[
 'bowser-current64-cold-controls-v1','bowser-current64-body-geometry-v1',
 'bowser-current64-host-checks-v1','bowser-current64-fire-contact-v1',
 'bowser-current64-menu-controls-v1','bowser-current64-router-controls-v1',
 'bowser-current64-foreign-main-v1','bowser-current64-vectors-v1',
 'bowser-current64-benj-controls-v1']

def deps(p):
    text=p.read_text(encoding='utf-8').split('\n\n')[0].replace('\\\n',' ')
    if ':\t' not in text:return []
    text=text.split(':\t',1)[1]
    return [Path(x.replace('\\ ',' ')) for x in re.split(r'(?<!\\)\s+',text.strip()) if x]

def main():
    assert not (O/'handoff.json').exists() and not C.exists()
    original=json.loads((O/'source-stage.json').read_text())
    assert original['candidate']=='95295fa6b15518b3813cad8609d833755bb92ba1e7eff3e39a60c9003f9f1ce1'
    manifests=[P/'handoff.json',R/'build/bowser-source-core-v5/handoff.json',
               R/'build/bowser-split-workers-v2/handoff.json',R/'build/bowser-functional-host-v9/handoff.json']
    files={Path(__file__)}
    for p in manifests:
        q=json.loads(p.read_text());files.add(p)
        for f,h in q['bindings'].items():
            assert sha(f)==h,('frozen predecessor binding',f)
            files.add(Path(f))
    controls=[]
    for name in CONTROL_DIRS:
        p=R/'build'/name/'controls.json'
        if not p.exists():p=p.parent/'menu-palette-controls.json'
        q=json.loads(p.read_text())
        assert q['passed'],p
        for f,h in q.get('bindings',{}).items():
            assert sha(f)==h,('control binding',f)
            files.add(Path(f))
        files.add(p);controls.append(dict(path=str(p),sha256=sha(p)))
    # Real final link producers, not copied historic joint/*-build.json logs.
    command=json.loads((O/'final-link.json').read_text())['command']
    objects={Path(x)for x in command if x.endswith('.o')}
    assert J/'main.o' in objects and J/'union.o' in objects
    files|=objects
    # DBG file records are the actual transitive source producers for every
    # linked object, including components whose inherited dependency file is
    # absent or has a historical name.
    for line in (J/'candidate.dbg').read_text().splitlines():
        if line.startswith('file\t'):
            p=Path(re.search(r'name="([^"]+)"',line).group(1))
            p=p if p.is_absolute()else R/p
            assert p.is_file(),('actual DBG source',p)
            files.add(p)
    for obj in objects:
        for suffix in ['.dep','.d']:
            dep=obj.with_suffix(suffix)
            if dep.exists():
                files.add(dep)
                for src in deps(dep):
                    p=src if src.is_absolute()else R/src
                    assert p.exists(),('actual source dependency',p)
                    files.add(p)
    # Complete private source/assets. Copied historic command/closure JSON are
    # deliberately not identified as the actual recipes for this successor.
    source_ext={'.s','.asm','.inc','.c','.h','.cfg','.chr','.rle','.dep','.d'}
    files|={p for p in J.rglob('*')if p.is_file() and p.suffix.lower() in source_ext}
    files|={p for p in O.iterdir()if p.is_file() and p.suffix=='.json'}
    files|={J/n for n in ['candidate.nes','candidate.dbg','candidate.lbl','candidate.map',
        'candidate.cv3-mirror.json','bowser.bin','ram3.bin','ff-cookie.bin','code.bin','data.bin']}
    files|={p for p in (J/'bowser').iterdir()if p.is_file()}
    files|={p for p in (J/'bt').iterdir()if p.is_file()}
    files.add(R/'build/bowser-split-workers-v2/root-grant-and-partition.json')
    files.add(R/'build/bowser-resource-closure-v1/proposal.json')
    # Include all own derivation/fixture predecessors so the concrete negatives
    # are replayable without rewriting any frozen candidate or expectation.
    patterns=['prepare_bowser_*','bowser_*controls*','bowser_*checks*',
              'bowser_*geometry*','bowser_*contact*','bowser_*main*',
              'bowser_*vectors*','bowser_functional_vector_diagnostic_v1.py']
    own_tools=set()
    for pattern in patterns:own_tools|=set((R/'tools/audit').glob(pattern+'.py'if '.'not in pattern else pattern))
    own_tools|={Path(__file__)};files|=own_tools
    files|=set((R/'tools/reference').glob('bowser_*'))
    negatives=[]
    for parent in R.glob('build/bowser-*'):
        if not parent.is_dir():continue
        for p in parent.glob('*.json'):
            try:q=json.loads(p.read_text())
            except (ValueError,UnicodeError):continue
            if isinstance(q,dict) and (q.get('passed')is False or q.get('returncode',0)!=0):
                files.add(p);negatives.append(dict(path=str(p),sha256=sha(p),
                    error=q.get('error',q.get('stderr',''))))
    save(O/'retained-negatives.json',dict(status='RETAINED',negatives=negatives,
        fixture_pause_correction='v2 changed GamePauseStatus then compared resumed movement to unpaused completion. v3 compares against the same suspended caller under the same condition; strict real ISR restoration assertions remain.',
        known_prior_product_fixes='Actual status recursion, stale second cookie publisher, right-facing palette bit and SMB1 left anchor were fixed in new source successors; prior candidates remain immutable.'))
    b=load(J/'candidate.nes');old=load(P/'joint/candidate.nes')
    actual=[]
    for name,start,end in [('BW_ROM_LOAD',0xbf20,0xc000),('BW_ROM_COPY',0xb523,0xb600),
        ('BW_ROM_CHECK',0xb529,0xb600),('BW_ROM_ROUTER',0xb22b,0xb300),
        ('BW_ROM_AUX',0xb334,0xb400),('BW_ROM_PREVIEW',0xb534,0xb600)]:
        segment=next(s for s in b['segs'].values()if s['name'].strip('"')==name)
        used=int(segment['size'],0);assert int(segment['start'],0)==start and start+used<=end
        actual.append(dict(segment=name,start=start,end=end,used=used,granted=end-start))
    assert sum(x['used']for x in actual)==1197
    assert sum(x['granted']for x in actual)==1281
    for n in ['ram3.bin','ff-cookie.bin','code.bin','data.bin']:
        assert sha(J/n)==sha(P/'joint'/n)
    native_sources=['entrypoint.s','src/character_select.s','screen_render.s','src/mmc5.s',
        'src/full_roster_menu.s','src/full_roster_menu_art.inc','union.s',
        'src/new_roster_dispatch.s','private.cfg']
    patch=[]
    for name in native_sources:
        oldpath=P/'joint'/name;newpath=J/name
        oldtext=oldpath.read_text(encoding='utf-8')if oldpath.exists()else ''
        patch.extend(difflib.unified_diff(oldtext.splitlines(True),newpath.read_text(encoding='utf-8').splitlines(True),fromfile='installed-f56/'+name,tofile='bowser-current64/'+name))
    (O/'source.patch').write_text(''.join(patch),encoding='utf-8')
    hooks=dict(candidate=original['candidate'],joint=str(J),native=False,
        variant=dict(menu_slot=26,SelectedCharacter=27,FmAlts_mask=8,SMB3=0,SMB1=8),
        menu='MenuResolveCharacter -> BwMenuResolve -> FwMuxMenuResolve -> S2MenuResolve -> QwMenuResolve -> ArGenResolve; family27 retired before selected store.',
        acquisition='Native InitScreen -> BwScene -> genuine S2InitScreenPrepare first, then selected27 forcedblank BwLoad + raw3 BwConstruct; native Ic/Sunny/QwBoot remain once.',
        source_fields=dict(raw_RAM_bank=3,source_state=0xbe00,source_ready=0xbe26,HP=0xbe29,tier=0xbe28,shots=0xbe80,persistent=0xbf80,cookie=0xbfe0),
        geometry='SMB3 source standing12 8x16 parts, SMB1 source7; native logical16x32 collision with original40/48px art overhang. PlayerFacingDir1 right,2 left.',
        palettes=dict(P0=[0x1a,0x30,0x27],world='native area backdrop preserved; overworld22, lives0F'),
        body_CHR=dict(SMB1=824,SMB3=[825,826],hardware_window=0),
        observations=['Real cold select/lives body','Natural native parser/entrance','Walk/jump/source breath→two flames','native item/contact/death where finite'],
        no_claims=['No native test yet','No full1-1 qualification','No perfect boss campaign/extended attacks/original SMB3 audio','Inherited FF419 render deadline not fixed'])
    hooks['labels']={n:address(b,n)for n in ['BwLoad','BwScene','BwMenuResolve','BwCheck','BwServiceVeneers',
        'BwBtResolve','BwStartFlags','BwConstruct','BwMovement','BwGraphics','BwWeaponTail',
        'BwDrawShots','BwSpawnFire','BwInjury','BwPickup','BwColors','BwStatusName']}
    save(O/'native-smoke-API.json',hooks)
    save(O/'freeze-proof.json',dict(passed=True,source=True,native=False,candidate=original['candidate'],
        parent=sha(P/'joint/candidate.nes'),resident=actual,resident_used=1197,resident_granted=1281,
        resident_headroom=84,fullcookie16=True,valid_last_buffered_copy_readback=True,
        FF_Quick_Arthur_payloads_unchanged=True,all_old_public_dispatch_PCs_preserved=True,
        private_GmOnlyRare_moves=4,actual_importers_reassembled=True,source_controls=controls,
        actual_producer_recipes=[str(p)for p in O.glob('*build.json')]+[str(O/'final-link.json')],
        current64_rebase='Actual installed f56 source, genuine BmFresh/BmColors groups regenerated46; Peach3 constants163027 retained. This private66 candidate is current64+Bowser2, no fbef SMB3+ adoption.'))
    stage=dict(original,status='FUNCTIONAL_SOURCE_WIP_NATIVE_PENDING',joint=str(J),
        original_installed_parent=sha(P/'joint/candidate.nes'),ready=66,source_controls_pass=True,
        installed=False,publication_allowed=False,source_proof=str(O/'freeze-proof.json'))
    # The actual Benj consumer receipt binds the builder's canonical joint
    # stage. Preserve it byte-for-byte; publish completion in a new manifest.
    save(O/'verified-source-stage.json',stage)
    note='''Bowser two-form functional SOURCE WIP, installed64 rebase v3, native pending.

This actual cart is installed f56 Benj64 + SMB3/SMB1 Bowser,66 ready identities.
Current native Main/source callbacks are genuinely recompiled. BmFresh/BmColors
are retained through46 freshly regenerated groups; variants5/6 and the corrected
Peach163027 constants are preserved. No fbef SMB3+ graphics are adopted.
The additional Benj receipt proves7Select variants,48 palettes,240 old palette
pairs and160 actual native Main updates; old Bowser v9 remains immutable.

Both forms complete genuine select/Start/native Ic+Sunny+QwBoot, full native
InitializeArea/ScreenRoutines/parser/entrance and120 complete Main updates.
Source movement, native terrain and source continuation each run once, and
original source breath produces friendly flames that reach genuine native
HandleEnemyFBallCol/defeat/scoring/SFX or native Bowser HP. Mature native items,
source HP/injury protection, two-player life/area persistence and native death
were exercised.26 original pose/facing metadata tuples are exact. All menus
and Start masks preserve foreign identities/flags.282 curated foreign Main
pairs preserve registers/state/OAM/maps with0..32CPU added. Shared27/33 resolver
has4736 row pairs,1024 full-cookie poison pairs,18432 targets and272 real vectors.
The own live-vector receipt is additionally bound, including legal mapper gaps,
normal/lag/pause NMI, IRQ, all33SMC, borrowed pairs and live page1 restoration.

This is a playable NPC-source adaptation, not a claim that donors had playable
Bowser. Native logical16x32 terrain retains progression while40/48px original
art overhangs it. Source1 has original down-only gravity, authored1px walking
and original mouth timing; source3 retains original fixed-point movement,
jump/gravity/breath/pound pose. Two friendly flames use original SMB1 art and
source speeds. Perfect campaign balance, extended boss attacks and original
SMB3 audio are deferred WIP extras. No native, full1-1 or cadence claim; lag is
accepted by user priority. Existing FF419 render deadline remains unresolved.

Only the six granted A-view islands are used:1197/1281B,84B fragmented headroom.
Bowser body824..<827, carrier927..<935, temporal rawRAM3 family27. No new global
RAM/ZP/resident allocation. Full8KB buffered copy/readback and16B cookie publish
valid last, retirement before owner publication. All FF/Quick/Arthur payloads
and cookies remain byte-exact. BT is still pending; its B020 genuine table is
shared through a resolver only, and callback AXYP passes through unchanged.

Authoritative producer commands are build/bowser-current64-v3/*build.json
and final-link.json. Copied joint historic build logs are NOT current recipes.
Every compiler/link invocation was guarded by private_build_outputs_v1. Replay
only into a new output root after validating every output/dependency/cfg file.
source.patch + native-smoke-API.json provide root composition and finite smoke
hooks. All previous failures remain separately bound. No install performed.
'''
    (O/'HANDOFF.txt').write_text(note,encoding='utf-8')
    files|={O/n for n in ['HANDOFF.txt','source.patch','retained-negatives.json',
        'native-smoke-API.json','freeze-proof.json','source-proof.json',
        'verified-source-stage.json']};files.add(J/'source-stage.json')
    for item in controls:
        q=json.loads(Path(item['path']).read_text())
        for f,h in q.get('bindings',{}).items():assert sha(f)==h,('post-freeze consumer binding',f)
    for f,h in original['bindings'].items():assert sha(f)==h,('actual source stage binding',f)
    assert all(p.is_file()for p in files),[str(p)for p in files if not p.is_file()]
    # Source archive contains true input sources/assets/recipes and hash proofs,
    # never full ROMs, objects or copied emulator recordings.
    archive=O/'source-only.zip';members=[]
    archive_ext=source_ext|{'.py','.json','.txt','.patch','.md','.lua'}
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in sorted(files):
            if p.suffix.lower()in archive_ext or p.name in ['cookie.bin','ff-cookie.bin']:
                rel=p.relative_to(R).as_posix();z.write(p,rel);members.append(rel)
    files.add(archive)
    result=dict(status='FROZEN_CURRENT64_PLUS_BOWSER_TWO_FORM_SOURCE_NATIVE_PENDING',source=True,
        candidate=original['candidate'],joint=str(J),source_stage=str(J/'source-stage.json'),
        parent=sha(P/'joint/candidate.nes'),native=False,installed=False,admitted=False,
        publication_allowed=False,ready=66,Bowser_forms=2,resident_used=1197,
        resident_granted=1281,resident_headroom=84,source_archive_members=len(members),
        FF_gameplay_deadline419_fixed=False,bindings={str(p.resolve()):sha(p)for p in sorted(files)})
    save(O/'handoff.json',result)
    for p,h in result['bindings'].items():assert sha(p)==h,p
    with zipfile.ZipFile(archive)as z:
        assert z.testzip()is None
        for name in z.namelist():assert hashlib.sha256(z.read(name)).hexdigest()==sha(R/name),name
    C.mkdir(parents=True)
    for n in ['handoff.json','source-only.zip','HANDOFF.txt','source.patch','freeze-proof.json','source-proof.json',
              'native-smoke-API.json','retained-negatives.json']:
        shutil.copyfile(O/n,C/n)
    for item in controls:
        p=Path(item['path']);q=json.loads(p.read_text())
        compact={k:v for k,v in q.items()if k not in ['rows','vectors','cohorts','checks','bindings']}
        compact.update(full_receipt=str(p),full_receipt_sha256=sha(p))
        save(C/(p.parent.name+'.json'),compact)
    receipt=dict(status=result['status'],candidate=result['candidate'],handoff=sha(O/'handoff.json'),
        verified_bindings=len(files),source_archive_members=len(members),
        bindings={str(p.resolve()):sha(p)for p in sorted(C.iterdir())})
    save(C/'receipt.json',receipt)
    owned=[p.relative_to(R).as_posix()for p in sorted(own_tools)]
    owned += [p.relative_to(R).as_posix()for p in (R/'tools/reference').glob('bowser_*')]
    owned += [p.relative_to(R).as_posix()for p in sorted(C.iterdir())]
    owned.append((C/'owned-files.txt').relative_to(R).as_posix())
    (C/'owned-files.txt').write_text('\n'.join(sorted(set(owned)))+'\n',encoding='utf-8')
    print(json.dumps(dict(handoff=str(O/'handoff.json'),SHA256=sha(O/'handoff.json'),
        candidate=result['candidate'],bindings=len(files),archive_members=len(members),
        checkpoint=str(C),checkpoint_sha256=sha(C/'receipt.json'))))

if __name__=='__main__':main()
