"""Conservative101-name evidence inventory; one authorized JSON, no build files."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json,re

R=Path(__file__).resolve().parents[2]
OUT=R/'docs/qa/character-status-sheet-data-1116.json'
CURRENT='cb95eb8dff9929c8162e019d5e3f33e45b570946f5281c07584a9f11cacdba07'
LEGACY='docs/qa/current-roster-progress-2026-10-27.json'
LEGACY_SHA='bd99b4ee9143380aabf12da8ee1e56beda5a1491abe26c92e6c789afecaaa0a7'
ACCESS='docs/character-select-access.md'
CHECKLIST='docs/qa/expanded-roster-next-native-checklist-1114.md'
SUPPLEMENTAL=('docs/qa/thomas-oneup-lift-1113.md','docs/qa/sonic-vol2-delivery-1111.md','docs/qa/karnov-five-current-native-1113.md')
H=lambda x:sha256(x).hexdigest()

OLD_NAMES=dict(zip(
    'mario luigi megaman proto samus bill lance link zelda2 simon grant sypha alucard pit rygar scrooge darkwing bass roll ryu sophia kirby meta chip dale mac mike mario3 luigi3 vic octopus twinbee pentarou leonardo raphael michelangelo donatello'.split(),
    ['MARIO','LUIGI','MEGA MAN','PROTO MAN','SAMUS ARAN','BILL RIZER','LANCE BEAN','LINK','ZELDA II LINK','SIMON BELMONT','GRANT','SYPHA','ALUCARD','PIT','RYGAR','SCROOGE MCDUCK','DARKWING DUCK','BASS','ROLL','RYU HAYABUSA','SOPHIA III','KIRBY','META KNIGHT','CHIP','DALE','LITTLE MAC','MIKE JONES','SMB3 MARIO','SMB3 LUIGI','VIC VIPER','OCTOPUS','TWINBEE','PENTAROU','LEONARDO','RAPHAEL','MICHELANGELO','DONATELLO'],strict=True))


def clean(name):
    name=name.replace('**','').strip().upper().replace('.','')
    return {'SMB1 TOAD':'TOAD','SMB1 PEACH':'PEACH'}.get(name,name)


def build():
    sources={p:(R/p).read_bytes()for p in(ACCESS,CHECKLIST,LEGACY)+SUPPLEMENTAL}
    assert H(sources[LEGACY])==LEGACY_SHA,'Protected progress file changed'
    access=sources[ACCESS].decode('utf-8-sig');check=sources[CHECKLIST].decode('utf-8-sig')
    legacy=json.loads(sources[LEGACY]);assert len(legacy['rows'])==len(OLD_NAMES)==37
    rows=[]
    for line_no,line in enumerate(access.splitlines(),1):
        found=re.match(r'^\|\s*([1-4])\s*\|\s*([1-8])\s*\|\s*(.*?)\s*\|$',line)
        if not found:continue
        row,col,choices=found.groups()
        for presses,name in re.findall(r'\*\*(\d+):\*\*\s*([^;|]+)',choices):
            rows.append(dict(name=name.strip(),menu_row=int(row),menu_column=int(col),select_presses=int(presses),
                playable_status='STARTABLE_DOCUMENTED',goal_status='IN_PROGRESS',
                stage_status='UNKNOWN',stage_build='',stage_scope='',
                **{k+'_status':'UNKNOWN'for k in('M','F','L','S')},
                **{k+'_build':''for k in('M','F','L','S')},
                **{k+'_scope':'Natural acquisition not located in reviewed sources; not a failure claim.'for k in('M','F','L','S')},
                abilities_status='OPEN',abilities_scope='Complete intended ability set is not certified by startup or a stage pass.',
                art_status='OPEN',art_scope='Full per-character animation/palette/OAM review remains open.',
                audio_status='OPEN',audio_scope='SFX/music queue values are not an audible-fidelity acceptance test.',
                performance_status='OPEN_UNMEASURED',performance_scope='No current enemy-free native idle/walk acceptance located here; stage frame ratios are not an idle benchmark.',
                next_action='Retain versioned stage proof; locate natural-item evidence before new tests, then qualify remaining abilities/audio/art/lag.',
                evidence_paths=[ACCESS],source_fields=dict(menu_line=line_no)))
    assert len(rows)==101 and len({r['name']for r in rows})==101
    byname={r['name']:r for r in rows}
    for i,old in enumerate(legacy['rows']):
        row=byname[OLD_NAMES[old['identity']]];passes=[]
        for mode in('easy','hard'):
            p=old.get(mode,{})
            if p.get('status','').startswith('cleared'):
                passes.append(dict(mode=mode,build=p.get('native_ROM_sha256','unrecorded'),scope=p['status'],
                    native_result_sha256=p.get('native_result_sha256'),frames=p.get('frames'),carry_forward=p.get('carry_forward')))
        assert passes,(old['identity'],'No retained stage pass')
        row.update(stage_status='EARLIER',stage_build='; '.join(dict.fromkeys(p['build']for p in passes)),
            stage_scope='; '.join(p['mode'].title()+': '+p['scope']for p in passes))
        row['evidence_paths'].append(LEGACY);row['source_fields'].update(legacy_identity=old['identity'],legacy_json_pointer=f'/rows/{i}',legacy_native_passes=passes)
        if 'powerups'in old:row['source_fields']['legacy_powerup_fixture']=old['powerups']
    added={}
    for line_no,line in enumerate(check.splitlines(),1):
        if not line.startswith('| '):continue
        cells=[v.strip()for v in line.strip('|').split('|')]
        if len(cells)!=3 or cells[0].startswith('Added identities'):continue
        names=[clean(n)for n in cells[0].split(';')]
        assert all(n in byname for n in names),(line_no,names)
        for name in names:
            assert name not in added and name not in OLD_NAMES.values(),name
            added[name]=line_no;row=byname[name]
            row['source_fields'].update(checklist_line=line_no,checklist_stage=cells[1],checklist_items_and_limits=cells[2])
            row['evidence_paths'].append(CHECKLIST)
            for path in re.findall(r'`([^`]+\.md)`',' '.join(cells[1:])):
                p='docs/qa/'+path if'/'not in path else path
                if (R/p).is_file():row['evidence_paths'].append(p)
    assert len(added)==64 and set(added)|set(OLD_NAMES.values())==set(byname)

    configured=set()
    def assign(names,stage,items=None,stage_scope=None,note=None,next_action=None):
        for name in names.split(';'):
            name=clean(name);row=byname[name];assert name in added and name not in configured,name
            configured.add(name);row.update(stage_status='EARLIER',stage_build=stage,
                stage_scope=stage_scope or'Native1-1 pass retained on named earlier build; exact grounding/return scope is in the checklist source field.')
            for key,value in(items or{}).items():
                row[key+'_status']='EARLIER';row[key+'_build']=value
                row[key+'_scope']='Genuine native acquisition recorded on this earlier build; individual credit/return and policy limits remain in the linked evidence.'
            if note:row['notes']=note
            if next_action:row['next_action']=next_action

    assign('SMB1 Toad;SMB1 Peach;Kamikaze Mario','421',dict.fromkeys('MFLS','91dc'))
    assign('SuperMaaa Mario','Oct29 Easy',dict.fromkeys('MFLS','91dc'),note='Star follows real shrink to power0; Flower allows original state6 emerging collection. Hard/full abilities remain separate.')
    assign('Celeste Mario','a7ccbaaa',dict.fromkeys('MFLS','00bb'))
    assign('Mario the Tank','421',{'M':'7ec9'},next_action='Retain historical M/boots; qualify intended powered combat/terrain and genuine F/S/L separately.')
    assign('Mini Mario','9826',{'M':'9826','F':'9826','L':'1327','S':'1327'},note='Existing fixed helper lefts560/688/864 and manual Flower1203 are unchanged; helper inventory has centers/initial tops.')
    assign('Mega Giant Mario','677aad54',next_action='Retain earlier stage proof; bind natural-item and complete giant ensemble evidence.')
    assign('Rogue Dawn','cb95',{'M':'cb95','F':'cb95','L':'1327','S':'1327'},next_action='Investigate confirmed1-2 HUD issue; qualify other seven gear acquisitions, Bomb brick/enemy effects and missile impacts.')
    assign('GB Pit','1daca /82',dict.fromkeys('MFLS','cb95'),next_action='Retain current four stock pickups; qualify remaining powered abilities, Star expiry/protected hits, audio/art/performance.')
    assign('Ryan','1daca',note='Stage tier increase is not a complete natural-item proof.')
    assign('Mr Gimmick','cf7',dict.fromkeys('MFLS','7a80'),note='Native full route has8 genuine star-support events; source0 support count is not substituted for native8.')
    assign('Donkey Kong','571',dict.fromkeys('MFLS','571'),note='Earned-M stage includes8 barrels/no injury.1UP has25 returned Main snapshots but24 strictly post-credit DK moves.')
    assign('Doc Louis','421',note='Existing actor28 at left3096/center3104/Y64 had no support event; assistance is not claimed.')
    assign('Getsu Fuma','c6ab5610',{'M':'c6ab5610','F':'c6ab5610'})
    assign('Karnov','7ef',{'M':'7ef','F':'7ef'},note='Five real pickups include Boots/Bomb/Ladder. Bomb arming/blast is not an enemy Bomb kill; natural S/L remain open.')
    assign('Quick Man','aa501128',{'M':'aa501128','L':'aa501128','S':'aa501128'},note='Existing no-growth policy refills health; physical Flower is not claimed by supplying kind1 to a fixture.')
    assign('Shinobi','6f319d20',note='Exact earlier full pass/no helpers. Later source preservation is not a new native route.')
    assign('Thomas','65ee94ca',dict.fromkeys('MFLS','65ee94ca'),note='M/F/S full route and L/Downloads repeat are separate native runs; not one uninterrupted all-item route.')
    assign('Metal Storm','8fc57b8b',dict.fromkeys('MFLS','00bb'),note='Immediate original armor/weapon policy; no60-growth requirement. Earned81 projectile/native Goomba defeat is specifically covered.')
    assign('Mike Tyson','33d2c7a7',stage_scope='Hard1-1 earlier native4861 physical frames; not a current build pass.')
    assign('Alex','4cbd0191',stage_scope='Earlier native1-1 route6018 physical frames; not a current build pass.')
    assign('Jay McCray','1327',dict.fromkeys('MFLS','1327'),note='Full Status+Size0 publication repaired; actual brick51/debris/noise, private82 Flower, usable pistol defeat and credit are covered. Original full arsenal remains open.')
    assign('Steve Hermann','62ba',dict.fromkeys('MFLS','7ef'),note='Four-stock route closed by combat chase; old death-before-Star controller negatives are not reopened.')
    assign('SMB3 Toad;SMB3 Peach','421')
    assign('Popo;Nana','a7ccbaaa',{'M':'a7ccbaaa'},note='Earlier natural route tier0→1; independent F/S/L and additional original abilities remain unqualified here.')
    assign('FF Fighter;FF White Mage;FF Black Mage;FF Thief','a5c54d76',dict.fromkeys('MFS','ae66'))
    for name in('FF FIGHTER','FF WHITE MAGE','FF BLACK MAGE','FF THIEF'):
        byname[name].update(L_status='EARLIER',L_build='571'if name=='FF FIGHTER'else'ae66',L_scope='Actual delayed INC2→3 and at least25 post-writer owner entries; Thief pending entry is not a completed Main or grounded endpoint.')
    assign('Sunny','16a9de64',{'M':'16a9de64','F':'16a9de64','L':'bc5','S':'bc5'})
    assign('Rash;Zitz','91dc',dict.fromkeys('MSL','91dc'),note='Mushroom food heals8 capped47 and retains power0. Later question blocks may remain M; no invented Flower progression.')
    assign('SMB2 Mario;SMB2 Luigi;SMB2 Toad;SMB2 Peach;Imajin;Lina;Papa;Mama','12397',{'M':'7ef','F':'12397','L':'421','S':'421'},note='Mature natural pickups/vegetable combat, hidden1UP and Star are each covered for all8; no sibling identity transfer.')
    byname['SMB2 LUIGI']['stage_build']='421'
    assign('Bub;Bob','f88',dict.fromkeys('MFLS','67'),note='Stock L counts25 later worker entries, not a new completed-Main-return claim; Star flash/native world palette repair has six reviewed PNGs.')
    assign('Sonic;Super Sonic','a2',{'M':'c4568faf4f472d4d6c3915c9b4258d5c04d6dcbb562b3e5602a5d580bb3046a2','L':'a2'},note='Current package uses Master System motor/ring policy; Sonic3 fidelity remains a later gap. Native rings0 are preserved; source five rings are a conditional fixture, not a native requirement.')
    assign('SMB3 Bowser;SMB1 Bowser','6a3',dict.fromkeys('MFLS','6a3'),note='Signed earned-life snapshot repair preserves upgrades until legitimate next-area reset; actual life3 full routes and separate tier2 Star routes are retained.')
    assign('Donkey Kong Jr','7c0f',note='Full public stage uses13 unchanged native helpers. Older private first-M helper/head bridge and seeded effects are not public acquisition proof.',next_action='Qualify ordinary natural M/F/L/S access using current public helper inventory; no private336-helper bridge promotion.')
    byname['DONKEY KONG JR'].update(M_status='FIXTURE_OR_PRIVATE_ONLY',M_scope='Older private first-M route requires undelivered336 helper/head bridge; seeded fixtures do not close natural acquisition.')
    assign('Hulk Hogan;Ted DiBiase;Bam Bam Bigelow;Honky Tonk Man;Randy Savage;Andre the Giant','8fc57b8b',dict.fromkeys('MFLS','7a80'),note='Six separate stage and natural-item identities; not a representative transplanted to siblings.')
    assign('Excitebike','91dc',dict.fromkeys('MFLS','91dc'),note='Star uses real moving-actor feedback; prior static-head/chase negatives retained. No helpers.')
    assign('Prince Persia','7fb',dict.fromkeys('MFS','7fb'),note='Earlier earned-M/F sword route and Star passed. Hidden1UP reach/2-1 ledge investigation remains distinct from repaired5F/60 head query.',next_action='Finish genuine natural1UP access; retain earned sword/full-route proofs and investigate remaining target loss/fidelity issues.')
    assign('Burns;Smith;Iron;Beans','421',next_action='Address overwhelming enemy-free idle/walk lag with a materially funded checked transport plan; natural weapons/items and remaining abilities stay separate.')
    assign('Arthur','d8a87050',{'F':'379590 (flower/torch)'},note='Source lance/native defeat and a separate earned torch are covered; other weapons and S/L remain open.')
    assign('Goku','f205 cited;22d09909 Hard',note='Retain authenticated helper/camera policy; natural powerup ensemble and Easy remain separate.')
    assert configured==set(added),(sorted(set(added)-configured),sorted(configured-set(added)))
    byname['THOMAS']['evidence_paths'].append(SUPPLEMENTAL[0])
    byname['KARNOV']['evidence_paths'].append(SUPPLEMENTAL[2])
    for name in('SONIC','SUPER SONIC'):byname[name]['evidence_paths'].append(SUPPLEMENTAL[1])

    # Explicit latest root bindings, not automatic promotion of a C row.
    overrides=[]
    def current(name,field,build,status,scope,source):
        row=byname[name];row[field+'_status']=status;row[field+'_build']=build;row[field+'_scope']=scope
        row['source_fields'].setdefault('root_current_overrides',[]).append(source)
        overrides.append(dict(name=name,field=field,status=status,build=build,source=source))
    current('ROGUE DAWN','stage','cb95','CURRENT','Actual Downloads36683/private7132 exactd11ef5cb: full flag/castle/entrance then25 living grounded1-2;40/177,lives2,power1.','Root latest directive +canonical Rogue row')
    for k in'MF':current('ROGUE DAWN',k,'cb95','CURRENT','Actual36683/private7132 exact5b4fb48d: genuine tanks/credit, usable earned missile,25 balanced workers; no transfer from a fixture.','Root latest directive +canonical Rogue row')
    current('MINI MARIO','stage','9826','CURRENT_PRESERVED','Actual21549/private89875 exactf95e3631 full1-1/25 grounded1-2; explicitly preserved by current cb952-byte Rogue update.','Root explicit current Mini full/two-shot preservation')
    for k in'MF':current('MINI MARIO',k,'9826','CURRENT_PRESERVED','Actual21549 exact531922c1: real M/F,60/credit/+25,2 shot spawns/third reject,107 cores+motion/four bounces; preserved into cb95.','Root explicit current Mini full/two-shot preservation')
    for name in('SONIC','SUPER SONIC'):
        current(name,'stage','a2','CURRENT_PRESERVED','Actual Downloads45911/private2047: real flag/castle/entrance then25 living grounded original1-2 returns; source policy plus typed preservation through9826/cb95.','Root explicit current Sonic L/full preservation')
        current(name,'L','a2','CURRENT_PRESERVED','Actual27306/private84495: genuine hidden head/eight timer0 gravity updates/full nativeC0 collector/erase/cue64/delayed INC2→3/+25; actual native ring resources retained.','Root explicit current Sonic L/full preservation')
    for k in'MFLS':
        scope={'M':'Actual25403/b12c4a74: real head/birth/maturity/physicalC1/erase/credit/all60/+25.',
               'F':'Actual25403/ea21d298: genuine M→F/physicalC1/erase/credit/all60/tier2/+25.',
               'L':'Actual65170/59057e82: original kind27 arrow triggers hidden60; real full maturity/positive1x9/C1/erase/popup11/INC2→3/cue64/+25.',
               'S':'Root actual35493 PASS76fb: latest genuine Star proof; full receipt is root-owned, not inferred from older pending prose.'}[k]
        current('GB PIT',k,'cb95','CURRENT',scope,'Root latest explicit GBPit M/F/L/S current override; Star35493/76fb supersedes pending sentence')

    byname['ROGUE DAWN']['art_status']='OPEN_KNOWN_ISSUE'
    byname['ROGUE DAWN']['art_scope']='Two coherent moving-missile PNGs reviewed; root now confirms a separate1-2 HUD issue. Wider art/facing review remains open.'
    for name,detail in{
        'MINI MARIO':'Exact GBC6x6 artwork/4x4 collision authenticated and user-requested unchanged; two-shot images checked, wider art remains separate.',
        'PRINCE PERSIA':'Earlier opening/player packet fixes and specific images checked; complete art/facing/animation review remains open.',
        'DONKEY KONG':'Earlier native Goomba/Mushroom/barrel coexistence images corrected by temporal window7; full visual ensemble remains open.',
        'MR GIMMICK':'Earlier corrected mushroom/Goomba images and11 ROM pattern pairs checked; complete original-star/art review remains open.',
        'CELESTE MARIO':'Two earlier00bb RAM PNGs reviewed coherent; wider animation/art review remains open.',
        'BUB':'Six paired earlier67 Star-flash PNGs checked across Bub/Bob; not complete art review.',
        'BOB':'Six paired earlier67 Star-flash PNGs checked across Bub/Bob; not complete art review.',
        'SONIC':'Standing/portrait and specific native pictures checked; current SMS motor is not Sonic3 visual/ability fidelity.',
        'SUPER SONIC':'Gold standing sheet/portrait checked; complete Super/Sonic3 visual fidelity remains open.'}.items():
        byname[name].update(art_status='PARTIAL',art_scope=detail)
    for name in('HULK HOGAN','TED DIBIASE','BAM BAM BIGELOW','HONKY TONK MAN','RANDY SAVAGE','ANDRE THE GIANT'):
        byname[name].update(art_status='PARTIAL',art_scope='Each of six wrestlers has earlier native590 Goomba/Mushroom pattern/image coverage; whole original animation/palette ensemble remains open.')
    for name in('SONIC','SUPER SONIC'):
        byname[name]['abilities_scope']='Master System motor/ring behavior currently used; broader intended abilities and Sonic3 fidelity remain open.'
        byname[name]['next_action']='Qualify ordinary natural F/S under actual ring/upgrade policy; retain current L/full and earlier M/ring-loss evidence.'
    for name in('RASH','ZITZ'):
        byname[name].update(performance_status='OPEN_PARTIAL_IMPROVEMENT',performance_scope='Earlier native bc5/ACE timing improves but retains missed-input/catch-up frames; no zero-lag acceptance.')
    for name in('BURNS','SMITH','IRON','BEANS'):
        byname[name].update(performance_status='OPEN_SEVERE_MEASURED',performance_scope='Earlier actual421 bare clocks all4 show30Hz; Burnsbc5 idle48Main/96physical with71/95 read-miss frames, Right16/32 with23/31 misses. Current cb95 source Main56226; no optimization shipped.')
        byname[name]['evidence_paths']+=['docs/qa/contra-force-idle-native-root-1115.md','docs/qa/contra-force-current-readonly-1116.md']
    byname['KIRBY'].update(stage_status='EARLIER',stage_build='571; legacy8487c439 Hard',stage_scope='Native571 green-shell/full1-1 and red catch; green1-2 endpoint was falling, not25 grounded. Older controlled1-2 remains separately versioned.',abilities_status='PARTIAL',abilities_scope='Four close-inhale cases plus native green-shell/full1-1 and red catch covered; complete copied arsenal remains open.')
    byname['KIRBY']['evidence_paths'].append('docs/qa/kirby-current-native-1114.md')
    byname['BASS']['fixture_notes']='Protected progress describes9 mature-actor collection fixtures/7 paid uses/effects, not full natural reveal/rise or all item properties; no M/F/L/S completion inferred.'

    for row in rows:
        row['evidence_paths']=list(dict.fromkeys(row['evidence_paths']))
        row['evidence_refs']=[dict(path=p,locator=('line '+str(row['source_fields']['menu_line'])if p==ACCESS else
            'line '+str(row['source_fields']['checklist_line'])if p==CHECKLIST and'checklist_line'in row['source_fields']else
            row['source_fields'].get('legacy_json_pointer','')if p==LEGACY else''))for p in row['evidence_paths']]
        assert row['stage_status']in('CURRENT','CURRENT_PRESERVED','EARLIER','UNKNOWN')
        assert all(row[k+'_status']in('CURRENT','CURRENT_PRESERVED','EARLIER','FIXTURE_OR_PRIVATE_ONLY','UNKNOWN')for k in'MFLS')
        assert row['name']in byname and row['goal_status']=='IN_PROGRESS'
    assert sum(r['stage_status']=='CURRENT'for r in rows)==1
    assert sum(r['stage_status']=='CURRENT_PRESERVED'for r in rows)==3
    assert all((R/p).read_bytes()==data for p,data in sources.items()),'Input source changed during inventory'
    counts={field:dict(Counter(r[field+'_status']for r in rows))for field in('stage','M','F','L','S','performance')}
    out=dict(schema_version=1,as_of='2026-11-16',owning_build_SHA256=CURRENT,rows_count=len(rows),
        scope='Read-only status inventory for Google Sheets; no new gameplay/native tests. Evidence is versioned, not an all-character current-ROM certification.',
        status_legend=dict(CURRENT='Actual native witness on current cb95 for this exact scope.',CURRENT_PRESERVED='Explicit root preservation/rebinding from the named earlier native build; not a fresh cb95 run.',EARLIER='Native receipt exists on a named earlier build; C in the checklist does not promote it to latest.',FIXTURE_OR_PRIVATE_ONLY='Only diagnostic/seeded or unpublished-private evidence; does not close current natural acquisition.',UNKNOWN='Not located or not qualified in the reviewed compact sources; not proof of a defect, absence of all history, or permission to repeat closed work.'),
        source_precedence=['Root explicit current overrides recorded below','Canonical expanded-roster checklist','Protected37-identity progress for earlier stage evidence','Menu access for101 exact names/Select positions and documented startability only'],
        sources=[dict(path=p,SHA256=H(data),role='protected read-only37'if p==LEGACY else'canonical added64'if p==CHECKLIST else'exact101 names/menu access'if p==ACCESS else'supplementary versioned native-item receipt')for p,data in sources.items()],
        root_current_overrides=overrides,counts=counts,
        sheet_columns=['name','menu_row','menu_column','select_presses','playable_status','goal_status','stage_status','stage_build','stage_scope','M_status','M_build','M_scope','F_status','F_build','F_scope','L_status','L_build','L_scope','S_status','S_build','S_scope','abilities_status','abilities_scope','art_status','art_scope','audio_status','audio_scope','performance_status','performance_scope','next_action','evidence_paths'],
        global_limits=['All101 names are documented startable; startup is not stage/item completion.','Earlier stage clears are across different ROMs/difficulties, not101 fresh cb95 routes.','A natural-item pass does not certify expiry/protected hits/all properties or the complete donor arsenal.','Queued sound/music bytes are not audible-fidelity acceptance.','Do not infer physical lag/cadence from source cycles or full-stage frame ratios.','Existing helper policy/coordinates live in helper-platform-inventory-1101.md; no helpers are added/moved by this inventory.','Character-access recent-limits prose can predate later canonical repairs; canonical/root evidence takes precedence.','Unknown means evidence not located here; locate retained proofs before starting a new test.'],
        protected_progress_SHA256_before_after=LEGACY_SHA,no_build_files_ROM_emulator_capture_or_Sheet_changes=True,rows=rows)
    out['receipt_SHA256']=H(json.dumps(out,sort_keys=True,separators=(',',':')).encode())
    return out


if __name__=='__main__':
    out=build();encoded=json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n'
    assert len(encoded.encode())<500_000
    OUT.write_text(encoded,encoding='utf-8',newline='\n')
    assert H((R/LEGACY).read_bytes())==LEGACY_SHA
    assert not(R/'build/character-status-sheet-data-1116').exists()
    print(json.dumps(dict(passed=True,rows=len(out['rows']),counts=out['counts'],file=str(OUT.relative_to(R)),bytes=len(encoded.encode()),file_SHA256=H(OUT.read_bytes()),receipt_SHA256=out['receipt_SHA256'],protected_progress_unchanged=True,generated_build_files=0),separators=(',',':')),flush=True)
