"""Read-only source/evidence ledger. Never launches an emulator or edits old receipts."""
from pathlib import Path
import argparse, hashlib, json, re
from final_item_matrix import FAMILIES, ROSTER, source_ref
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
CURRENT='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

# Source-adapted rewards. IDs are scoped to the named family, never global IDs.
CUSTOM={
 'mario':['mushroom: Super','flower: Fire','invincibility star','1-up'],
 'pit':['mushroom: tier1','flower: tier2/cap','invincibility star','1-up'],
 'rygar':['mushroom: tier1','flower: tier2/cap','invincibility star','1-up'],
 'scrooge':['mushroom: tier1','flower: tier2/cap','invincibility star','1-up'],
 'darkwing':['$22 health+1','$23 health full4','$24 gas+10','$25 gas+1','$26 Arrow','$27 Heavy','$28 Thunder','invincibility star','1-up'],
 'z2':['$c0 Jump','$c1 Downthrust','$c2 Upthrust','$c3 Fairy','$c4 Shield','$c5 Life','$c6 Fire','$c7 Reflect','$c8 Spell','$c9 Thunder','$ca Glove','$cb HP container','$cc MP container','$cd restoration','HP/MP jars','EXP/level1..8','invincibility star','1-up'],
 'cv3':['$d0 health','variant-specific subweapon/power rewards','invincibility star','1-up'],
 'kirby':['mushroom heal+2/cap6','flower full health','invincibility star','1-up','14 Kirby enemy copies (Kirby only)'],
 'chip':['mushroom heal+1/cap3','flower full health','brick crate','invincibility star','1-up'],
 'm3':['$d1 Super','$d2 Fire','$d3 Raccoon','$d4 Frog','$d5 Tanooki','$d6 Hammer','invincibility star','1-up'],
 'vic':['power capsule','six-cell selection: Speed/Missile/Double/Laser/Option/Shield','invincibility star','1-up'],
 'parodius':['capsule4','roulette5','Gold6','Blue Bomb7','Big8','Red charge9','White1-up10','variant-specific seven-cell equipment program','invincibility star'],
 'tmnt':['food32/64/cap128','gear1 Shuriken','gear2 Triple','gear3 Boomerang','gear4 Kiai','same gear+20/cap99','replacement20/autoselect','invincibility star','1-up'],
 'mac':['mushroom health+24/cap96','flower punch-star+1/cap3','SMB invincibility star (distinct from punch-stars)','1-up'],
 'mike':['$81 heart container/cap22/full heal','$82 Shooting Star','$83 Super Nova','$84 Bat','$85 Sling','$86 Fire','$87 Mirror','$88 Cross','$89 Bola','$8a Spikes','$8b Ball','$8c Laser','$8d Mega','10-ammo/refill/drop cycle','invincibility star','1-up'],
 'roll':['mushroom/flower full HP+EN/cap28','small/large HP capsule2/10','small/large EN capsule2/10','invincibility star','1-up']}
EXTRA_USES={
 'pit':'Hammer active window/hit both facings at all tiers; tier2 temporary flight60/exhaust/release/ground recharge; tier0/1 refusal.',
 'rygar':'Disk extension40/64/88, hit, retraction/catch, both facings; air/crouch/edge/pool controls.',
 'scrooge':'Cane/pogo ground rebound, enemy hit, release and protection. Tier does not grant a separate cane ability.',
 'z2':'Acquire/cast all eight spells; native MP cost/refusal/expiry and world effects; up/downthrust, glove, HP/MP/EXP levels, panel selection. Reward art alone is insufficient.',
 'kirby':'Kirby: inhale priority, swallow/copy, all14 copy attacks, spit, inflate, drop/recover/expiry. Meta: sword/guard/combos only; shared food is not shared combat.',
 'tmnt':'Each acquired gear: selection, volley cost, hit, full pool/refusal, cleanup. Authentic boomerang catch may refund to100..102; test readable HUD rather than invent a stricter cap.',
 'mac':'Real punch/star uppercut cost, stamina exhaustion/recovery, injury/death/life reset; SMB star boundaries separately.',
 'roll':'Broom/pellet/charged energy cost, zero-energy refusal/free pellet, HP/EN isolation/caps, earned drop age/fade/expiry, damage/death reset.',
 'parodius':'Each variant equipment/bell program, capsule wrap/refusal, roulette, Bomb/Red charge consumption, Big expiry, Gold/White life/caps; crowded body visibility remains open.',
 'vic':'Six-cell meter wrap/refusal, Missile/Double/Laser, Option count2, Shield loss, pickup/use/pool cleanup; distinct from Parodius.'}
CANON={
 'megaman':'Mega Man','proto':'Proto Man','samus':'Samus','bill':'Bill','lance':'Lance','bass':'Bass','roll':'Roll','ryu':'Ryu',
 'mario':'Mario','luigi':'Luigi','link':'Link','zelda2':'Zelda II Link','simon':'Simon','grant':'Grant','sypha':'Sypha','alucard':'Alucard',
 'pit':'Pit','rygar':'Rygar','scrooge':'Scrooge','darkwing':'Darkwing','sophia':'Sophia','kirby':'Kirby','meta':'Meta Knight',
 'mac':'Little Mac','mike':'Mike Jones','mario3':'SMB3 Mario','luigi3':'SMB3 Luigi','vic':'Vic Viper','octopus':'Octopus','twinbee':'TwinBee','pentarou':'Pentarou',
 'leonardo':'Leonardo','raphael':'Raphael','michelangelo':'Michelangelo','donatello':'Donatello','chip':'Chip','dale':'Dale'}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 rom=D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq/candidate.nes';source=rom.parent/'source'
 assert sha(rom)==CURRENT;b=scoped_load(rom);bindings={};evidence=[]
 def bind(path,expected=None):
  path=Path(path);h=sha(path);assert expected is None or expected==h,(str(path),expected,h)
  bindings[str(path.resolve())]=dict(path=str(path.resolve()),sha256=h,bytes=path.stat().st_size);return h
 def read(path):bind(path);return json.loads(Path(path).read_text(encoding='utf-8'))
 def add(identity,mode,track,path,romhash,scope,setup,**extra):
  assert identity in {r[0]for r in ROSTER};assert mode in ['easy','hard','unspecified']
  q=dict(id='E%03d'%len(evidence),identity=identity,actual_mode=mode,track=track,receipt=str(Path(path)),receipt_sha256=bind(path),ROM_sha256=romhash,current731=romhash==CURRENT,scope=scope,setup=setup,**extra);evidence.append(q);return q
 for ext in ['.nes','.dbg','.lbl','.map']:bind(rom.with_suffix(ext))
 read(D/'mm-proto-clean-menu-candidates-v1/freeze-v1/receipt.json')
 old=read(D/'final-item-matrix-v1/current84-matrix-v1/matrix.json')
 items_index=read(D/'native-probes-qa-v2/items-v1/proof.json');mode_audits={}
 for run in items_index['runs']:
  folder=D/'native-probes-qa-v2/items-v1/fixtures'/run['name'];script=folder/'run.lua';bind(script,run['frozen_fixture_sha256'])
  text=script.read_text(encoding='utf-8');literal=re.findall(r'\["hard"\]\s*=\s*(true|false)\b',text);assert literal==['true'if run['name'].endswith('-hard')else'false'],(run['name'],literal)
  for dep in run.get('dependencies',[]):bind(dep['frozen'],dep['sha256']);text+='\n'+Path(dep['frozen']).read_text(encoding='utf-8')
  assert any('assert('in line and "r('CrossoverBehaviorVersion')==(C.hard and 1 or 0)"in line for line in text.splitlines()),run['name']
  mode_audits[run['name']]=dict(script=str(script),script_sha256=sha(script),literal=literal[0],mode_from_executed_passed_assertion=int(literal[0]=='true'),not_a_new_native_read=True)
 legacy_index=read(D/'native-probes-qa-v2/legacy-physical-summary-v1/proof.json')
 legacy_modes={}
 for run in legacy_index['runs']:
  bind(run['run'],run['run_sha256']);bind(run['fixture'],run['fixture_sha256']);text=Path(run['run']).read_text();fixture=Path(run['fixture']).read_text()
  assert re.findall(r'\["hard"\]\s*=\s*(true|false)\b',text)==['true']
  assert any('assert('in line and "r('CrossoverBehaviorVersion')==(C.hard and 1 or 0)"in line for line in fixture.splitlines())
  legacy_modes[CANON[run['identity']]]=dict(script=run['run'],script_sha256=run['run_sha256'],literal='true',mode_from_executed_passed_assertion=1,not_a_new_native_read=True)
 for e in old['evidence']:
  bind(e['receipt'],e['receipt_sha256']);bind(e['parent_receipt'])
  mature=e['kind'].startswith('mature-actor')
  extra={k:e[k]for k in ['item_ids','declared_ability_item_ids','declared_attack_ids','copy_powers']if k in e}
  has_declared_use=bool(e.get('declared_ability_item_ids')or e.get('copy_powers'))
  q=add(e['identity'],e['mode'],'B'if mature else'A+B'if has_declared_use else'A',e['receipt'],e['ROM_sha256'],e['kind'],
   'Mature actor/resource setup at guarded engine boundary; actual collision/transform/controller use; NO reveal/rise.'if mature else'Real head/block reveal/full native rise; world/player/resource arenas staged; mature actor repositioned for contact. M3 form gallery uses controlled native RNG input. Not unassisted acquisition.',**extra)
  q['mode_evidence']=legacy_modes[e['identity']]if mature else mode_audits[Path(e['receipt']).parent.name]
 # Never import the stale current84 matrix mode labels as difficulty proof.
 correction=read(D/'current84-abilities-v1/mode-correction-v1/proof.json')
 for run in correction['affected_receipts']:
  if run['group']not in ['current220_progression','current84_progression']:continue
  bind(run['path'],run['proof_sha256'])
  add(CANON[run['family']],'easy','A',run['path'],run['ROM_sha256'],
      'Historical physical progression/cap/use; actual mode0 from the passed RAM assertion. Declared Hard is withdrawn, not relabeled as a fresh run.',
      'World/head-block fixture and post-rise contact placement; no tier injection.',declared_mode=run['declared_mode'],withdrawn_hard_label=run['hard_label_withdrawn'],mode_correction_sha256=sha(D/'current84-abilities-v1/mode-correction-v1/proof.json'))
 for rel in ['current84-abilities-v1/aggregate-v1/proof.json']:
  agg=read(D/rel)
  for run in agg['runs']:
   folder=Path(run['folder']);bind(folder/'proof.json',run['hashes']['proof.json'])
   add(CANON[run['family']],'easy','A+B',folder/'proof.json',agg['ROM_sha256'],
       'Acquired-tier progression plus31 distinct family ability plans across three identities. Duplicate declared-Hard runs remain actual Easy.',
       'World/target arenas staged; post-rise contact placement; no tier/fuel/ability-state injection.',declared_mode=run['mode'],withdrawn_hard_label=run['mode']=='hard',mode_correction_sha256=sha(D/'current84-abilities-v1/mode-correction-v1/proof.json'))
 agg=read(D/'current529-mode-native-v1/aggregate-v1/proof.json')
 for run in agg['runs']:
  folder=Path(run['folder']);z=read(folder/'proof.json');assert z['native']['actual_mode_readback']==1
  add(CANON[run['family']],'hard','A+B'if run['suite']=='abilities'else'A',folder/'proof.json',agg['ROM_sha256'],
      'Fresh numeric Hard: physical0→1→2 (plus cap in progression),60 committed transform updates; acquired ability plans10Pit/12Rygar/9Scrooge in abilities.',
      'Staged world/Goomba/motion; post-rise collision placement; no tier/inventory/fuel/reach/pogo writes.',suite=run['suite'],actual_mode_readback=1)
 agg=read(D/'final-tmnt-items-v1/aggregate-v1/proof.json')
 for run in agg['runs']:
  fp=Path(run['folder'])/'proof.json';bind(fp,run['proof_sha256'])
  add(CANON[run['identity']],run['mode'],'A+B',fp,agg['ROM_sha256'],
      '30 physical pickups/475 counted defeats/19 source drops/8 injuries per profile; all4 gear acquired/use/cap and authentic100..102 boomerang catch.',
      'Staged world/enemy introductions; actual RNG advances/defeats (no counter/RNG writes); post-rise block contact alignment after150 updates.',actual_mode_readback=run['actual_mode'])
 agg=read(D/'final-mac-items-v3/qualification.json')
 for mode,run in agg['results'].items():
  fp=D/'final-mac-items-v3'/('native-easy-pilot-v1'if mode=='easy'else'native-hard-v1')/'proof.json';bind(fp,run['proof_sha256'])
  add('Little Mac',mode,'A+B',fp,agg['ROM_sha256'],'Real injury-earned HP depletion, five physical pickups/full48 rise, star cap/use/stamina/injury/death reset.',
      'World/enemies staged; no resources/item actors/contact teleport.',actual_mode_readback=run['actual_mode'])
 agg=read(D/'final-roll-items-v1/aggregate-single-owner4c70-v1/proof.json')
 for run in agg['runs']:
  fp=Path(run['folder'])/'proof.json';bind(fp,run['proof_sha256'])
  add('Roll',run['mode'],'A+B',fp,agg['ROM_sha256'],'36-step physical/earned-drop HP/EN/caps/cost/refusal/star/1-up/expiry/death lifecycle; fade was still missing at this ROM.',
      'Staged world/enemies; real injuries/attacks/defeats/RNG; no resource/outcome writes or mature-item shortcuts.',actual_mode_readback=run['actual_mode'],visual_limit='Later fade evidence is separately bound; no retagging.')
 fade=read(D/'roll-fade-current9e0e-v1/final-packet-v2/proof.json')
 for mode in ['easy','hard']:
  add('Roll',mode,'B',D/'roll-fade-current9e0e-v1/final-packet-v2/proof.json',fade['combined_candidate'],
      'Current-parent calm earned-orb fade/art plus matched idle cost controls; not the old full36-step lifecycle.',
      'Separate captured source/PPU epochs; crowded visibility limits remain open.')
 for rel,ids,scope in [
  ('ryu-sophia-native-v1/qualification-proof.json',['Ryu','Sophia'],'Ryu actual mature ninjitsu pickup during Slash and primary refusal; Sophia missile free1/2/3 reservation/cost. Not full acquisition.'),
  ('kirby-chip-native-v1/qualification-proof.json',['Kirby','Chip','Dale'],'Bounded copy/crate legal-fall/contact controls; no hypothetical off-page Kirby guard adopted.'),
  ('samus-wave-combined220-v1/native-v1/proof.json',['Samus'],'16 legal staged Wave use/collision/pool cases; Hard mature-item grant, Easy equipment/tier setup. No block rise.')]:
  z=read(D/rel);romhash=z.get('ROM_sha256')
  if rel.startswith('samus-'):
   build=read(D/'samus-wave-combined220-v1/build-proof.json');romhash=build['ROM_sha256']
  assert re.fullmatch('[0-9a-f]{64}',romhash),romhash
  for identity in ids:add(identity,'unspecified','B',D/rel,romhash,scope,'Controlled native-boundary component; inspect receipt modes/seed disclosure before reuse; unspecified does not fill an Easy/Hard cell.')
 # Ordinary routes are an independent R lane, not every-item certification.
 for rel in ['current3cee-eight-routes-final-v1/proof.json','current3cee-remaining27-final-v1/proof.json']:
  agg=read(D/rel)
  for run in agg['profiles']:
   key=run['case'].rsplit('-',1)[0];identity=CANON[key];fp=Path(run['direct'])/'proof.json';bind(fp,run['direct_proof_sha256'])
   add(identity,'hard'if run['actual_numeric_mode']==1 else'easy','R',fp,agg['ROM_sha256'],
       'Zero-death1-1 discovery+independent direct-PPU replay and movable1-2. Ordinary starting-form route, not all items/ability/audio fidelity.',
       'Natural route controller; retained evidenced controller retries for Bill/Simon.',power_status_transitions=run.get('power_status_transitions',[]),source_request_events=run.get('request_store_events',[]))
 agg=read(D/'root-chip-hud-playthroughs-v1/native/proof.json')
 for run in agg['runs']:
  fp=D/'root-chip-hud-playthroughs-v1/native'/(run['identity']+'-easy-direct')/'proof.json';read(fp)
  add(CANON[run['identity']],'easy','R',fp,agg['ROM_sha256'],'Zero-death1-1 and independent actual-PPU replay; bounded crates/HUD route observations.','Natural controller route; no all-food/all-throw certificate.')
 mario=D/'mario-flower731-east-v1/native-result-freeze-v1/proof.json';z=read(mario);assert z['passed'] and z['ROM_sha256']==CURRENT
 bind(D/'mario-flower731-east-v1/native-proof.json')
 add('Mario','easy','A+B',mario,CURRENT,'Physical mushroom→flower, two60-update transforms; actual Goomba fireball contact1898, neutral drain1899..1944, both slots clear1906/1911. Narrow current component.','Staged legal world/target; actual physical collection/use; no Hard/full-route/star/1-up/waveform claim.',actual_mode_readback=0,reward_keys=['mushroom','flower'],declared_use_keys=['Fireball->Goomba','shot-pool-drain'])
 rows=[]
 for identity,slot,char,var,val,family in ROSTER:
  f=FAMILIES[family];refs=[source_ref(source,*s,b)for s in f['sources']]
  for r in refs:bind(r['path'])
  policy={m:f[m]for m in ['easy','hard']}
  if identity=='Mario':policy['hard']='Independent mushroom→Super / flower→Fire; non-increasing pickup refuses transformation.'
  if identity=='Luigi':
   policy['hard']='Shared guest sequential0→1→2; not Mario independent-type rule.'
   refs += [source_ref(source,'guest_powerups.s','GuestBeginPowerup',b),source_ref(source,'guest_powerups.s','GuestPowerupUpdate',b)]
  inventory=[]
  if family in ['mm','samus','bill','link','simon','bass','ryu','sophia']:
   for item in range(1,b['raw'][location(b,'InvItemCount')+char]+1):
    idx=char*16+item;ptr=b['raw'][location(b,'InvNameLo')+idx]+256*b['raw'][location(b,'InvNameHi')+idx];g=b['segs'][b['syms']['InvNameLo']['seg']];off=int(g['ooffs'],0)+ptr-int(g['start'],0)
    inventory.append(dict(id=item,UI_name=b['raw'][off:off+7].decode('ascii').strip(),cost=b['raw'][location(b,'InvCosts')+idx],initial_ammo=b['raw'][location(b,'InvInitialAmmo')+idx],max_ammo=b['raw'][location(b,'InvMaxAmmo')+idx]))
  required=CUSTOM.get(family,['mushroom/flower legacy tiers','Hard inventory rewards and refill/energy','invincibility star','1-up'])[:]
  if identity=='Meta Knight':required=[q for q in required if not q.startswith('14 Kirby')];refs=[source_ref(source,'kirby_core.s','KbHealPickup',b),source_ref(source,'meta_knight.s','MkWeapons',b)]
  if family=='cv3':required[1]={'Grant':'$d1 Dagger / $d2 Axe / $d3 Holy Water','Sypha':'$d5 Fire / $d6 Ice / $d7 Lightning','Alucard':'$d4 power repeat/cap2; bat'}[identity]
  cells={}
  for mode in ['easy','hard']:
   applicable_inventory=inventory if mode=='hard'or family in ['bass','ryu','sophia'] else []
   ev=[e for e in evidence if e['identity']==identity and e['actual_mode']==mode]
   reward_cells=[]
   descriptions=[dict(description='Inventory '+str(q['id'])+': '+q['UI_name'],item_id=q['id'])for q in applicable_inventory]
   descriptions += [dict(description=t,item_ids=[int(v,16)for v in re.findall(r'\$([0-9a-f]{2})\b',t)])for t in required]
   for req in descriptions:
    ids=req.get('item_ids',[req['item_id']]if'item_id'in req else[])
    reward_cells.append(dict(**req,
       current731_physical_component_evidence=[e['id']for e in ev if e['current731']and any(req['description'].startswith(k+':')for k in e.get('reward_keys',[]))],
       historical_exact_item_A=[e['id']for e in ev if'A'in e['track']and ids and all(i in e.get('item_ids',[])for i in ids)],
       historical_exact_item_declared_use=[e['id']for e in ev if ids and all(i in e.get('declared_attack_ids',[])+e.get('declared_ability_item_ids',[])for i in ids)],
       scope_only_components=[e['id']for e in ev if e['track']!='R'and not e.get('item_ids')],
       current731_complete_A=False,current731_complete_use=False,
       unresolved='Exact-ID links mean only the declared historical assertion; scope-only components require their detailed chronology. Current731 per-reward complete assertions remain unrun, except narrow Mario component keys explicitly recorded in its evidence.'))
   if identity=='Kirby':
    for power in range(1,15):reward_cells.append(dict(description='Kirby copy'+str(power),copy_power=power,historical_exact_acquire_declared_use=[e['id']for e in ev if power in e.get('copy_powers',[])],current731_complete_A=False,current731_complete_use=False))
   cells[mode]=dict(policy=policy[mode],required_pickups=required,selectable_acquired_inventory=applicable_inventory,
      reward_use_cells=reward_cells,
      required_forms=f['forms'],required_refill_caps=f['refill'],required_use=f['use']+'; '+EXTRA_USES.get(family,''),
      A_physical_evidence=[e['id']for e in ev if'A'in e['track']],B_controlled_or_acquired_use_evidence=[e['id']for e in ev if'B'in e['track']],R_ordinary_routes=[e['id']for e in ev if e['track']=='R'],
      current731_components=[e['id']for e in ev if e['current731']],current731_all_required_A_pass=False,current731_all_required_B_pass=False,
      current731_observed_use_components=[dict(evidence=e['id'],assertions=e.get('declared_use_keys',[]))for e in ev if e['current731']and e.get('declared_use_keys')],
      remaining='Current731 exact required rewards, all use/refusal/pool/contact/cleanup/graphics assertions are untested except explicitly referenced narrow current components; historical evidence remains reusable design/context, not a current native pass.')
  rows.append(dict(identity=identity,slot=slot,character=char,variant_symbol=var,variant=val,family=family,source=refs,modes=cells,
      unspecified_mode_components=[e['id']for e in evidence if e['identity']==identity and e['actual_mode']=='unspecified']))
 assert len(rows)==37 and len({r['identity']for r in rows})==37
 groups=[
  dict(identities=ids,shared_source_owner=owner,must_keep_separate=difference,native_coverage_from_equivalence=False)
  for ids,owner,difference in [
   (['Mega Man','Proto Man'],'InventoryCollect/Grant MM row','Variant body/shield/shot art and firing behavior'),
   (['Bill','Lance'],'InventoryCollect/Grant Contra row','Native body/weapon graphics and selected projectile appearance'),
   (['Chip','Dale'],'CdHealPickup/crate owner','Body/facing/crate geometry and throws'),
   (['SMB3 Mario','SMB3 Luigi'],'M3PhysicalPowerup/6form dispatch','Body art and movement/power poses'),
   (['Leonardo','Raphael','Michelangelo','Donatello'],'TnFood/TnPickup/TnWeapons gear rules','Four weapons/body sprites/hits/HUD and cold variant state'),
   (['Octopus','TwinBee','Pentarou'],'Parodius bell reward/admission','Each native equipment program, body/gun art/scale and overload'),
   (['Kirby','Meta Knight'],'KbHealPickup food ONLY','Kirby copies/inflate versus Meta sword/guard; no shared combat claim'),
   (['Grant','Sypha','Alucard'],'CV3 health/replacement infrastructure ONLY','Unique subweapons/magic/bat and audio/graphics'),
   (['Pit','Rygar','Scrooge'],'Guest60-update transformation clock ONLY','Hammer/flight, disk and cane/pogo all distinct'),
   (['Mario','Luigi'],'SMB/guest pickup infrastructure','Hard Mario independent-type policy differs from Luigi sequential progression')]]
 plan=[
  dict(priority=1,unit='Static observer + current731 three progressive families',max_profiles=6,max_cases=62,track='A+B',
       reuse='final_item_abilities_run.py plus separately versioned static-return observer; 10Pit/12Rygar/9Scrooge plans ×2 actual numeric modes.',
       setup='Cold select; valid initialized world/enemies at GameLoop; retain real0→1→2 item acquisitions. Do not seed tiers/fuel/pogo. Existing post-rise actor alignment remains disclosed.',
       gate='Fresh compiled hooks, static callback inventory/mock negatives, then separately reviewed native grant; actual mode readback,60transform updates, hit/cost/exhaust/refusal/cleanup, actual CHR/OAM/RGB/5SMC/SP/banks.'),
  dict(priority=2,unit='Controlled inventory weapon galleries',max_profiles=20,max_cases=172,track='B',
       reuse='054d legacy mature-item/attack module and current source numeric inventory tables; split every profile at16 cases.',
       setup='Complete valid native-boundary player/weapon/pool/actor state; explicitly seed inventory/ammo/tier only for use controls. Every seed logged, no acquisition claim. Isolate unrelated damage; separate actual injury cases.',
       gate='Each item selected/used through production input, both-facing representative graphics, cost/refusal/full pool/hit/cleanup; passive/Rush/armor/screw/reflection get specific source-owned effect cases, not generic shot counter.'),
  dict(priority=3,unit='Missing physical owners and mode gates',max_profiles=12,max_cases=48,track='A',
       reuse='Qualified Mario731 physical block path + historical native-items-core; prioritize LuigiHard, Easy MM/Proto/Samus/Contra/Link/Simon, Vic/three Parodius actual reward graphics.',
       setup='Real head/legal shot reveal→full rise→no premature grant→contact→transform; disclose player/arena setup and any post-rise placement. Natural RNG bounded waiting; controlled RNG gallery explicitly separate.',
       gate='At most4 selected physical rewards/profile; any unavailable reward remains missing, never replaced with seeded status or called every-item complete.'),
  dict(priority=4,unit='Special/custom ability and restoration galleries',max_profiles=24,max_cases=192,track='A or B recorded per case',
       reuse='054d Kirby/CV3/Z2/Mike/M3,529TMNT,8ffMac,9bacRoll qualified family modules; max8 source-specific cases/profile, next batch only after review.',
       setup='Keep natural physical prefix where already finite; use explicit seeded B fixtures for rare spell/copy/equipment mechanics, with real native dispatch and no fabricated acquisition.',
       gate='Z2 all8MP costs/world effects; Kirby14copies; M3all6form controls; Mikeall10weapons; custom health/caps/food/star/1up and damage/death; each family HUD/source-art checks. No full current coverage until actual receipts exist.')]
 result=dict(passed=True,kind='read_only_coverage_index_not_native_qualification',ROM_sha256=CURRENT,ROM_path=str(rom),source_root=str(source),
      identities=37,difficulty_cells=74,current731_complete_all_required_A_cells=0,current731_complete_all_required_B_cells=0,
      native_launches=0,goal_complete=False,rows=rows,evidence=evidence,source_equivalence_groups=groups,capped_fixture_reuse_plan=plan,
      mode_correction=dict(receipt=str(D/'current84-abilities-v1/mode-correction-v1/proof.json'),sha256=sha(D/'current84-abilities-v1/mode-correction-v1/proof.json'),affected_old_runs=18,withdrawn_hard_labels=9,actual_old_mode='Easy0; 31 distinct old ability plans repeated, not62 distinct plans or six mode cells.'),
      lanes=dict(A='Actual physical block/drop/reveal/rise/contact/transform. Setup and post-rise placement disclosed; seeded resources do not become earned depletion.',B='Controlled fully initialized native-boundary use/graphics/contact/cost/pool/exhaust/refusal/cleanup, or actual acquired ability component. Seeds explicit; no acquisition claim.',R='Ordinary route observations; generic PlayerStatus/request stores are not reward ownership, every weapon, waveform or full sprite fidelity.'),
      limits=['Every old receipt keeps its actual ROM; current source similarity is not current native evidence.','No global audio/source-fidelity, all-pose or no-flicker closure. Current Octopus/Sophia/Mega first-eight exclusion and tiny HUD readability limits remain open.','The old054d26MODEprofiles are12identities×2 plus Kirbycopy×2, not26identities. The combined two054d corpora contain22identities/34modecells.','Fresh731 MarioEasy is a narrow physical/use component, not Hard/star/1up/fullroute certification.','Original Parodius area aggregateFALSE and unencountered natural pending-fullHUD/nonemptyBuffer2 overlap remain unchanged.'])
 assert all(re.fullmatch('[0-9a-f]{64}',e['ROM_sha256'])for e in evidence)
 bind(Path(__file__));bind(ROOT/'tools/audit/final_item_matrix.py');bind(ROOT/'tools/audit/check_tmnt_render_oa.py');bind(ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py')
 for r in rows:
  for s in r['source']:bind(s['path'])
 for name in ['InventoryCollect','InventoryGrant','GuestBeginPowerup','GuestPowerupUpdate']:
  if name in b['syms']:result.setdefault('linked_shared_owners',[]).append(dict(symbol=name,cpu_address=address(b,name),bank=(location(b,name)-16)//8192))
 (a.output/'ledger.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 lines=['Current731 powerup/ability coverage ledger','',f'ROM {CURRENT}. Read-only index:37 identities/74 difficulty cells. Zero complete all-required current A or B cells. No native launches.',
 'A = physical lifecycle; B = controlled/acquired actual-engine use; R = ordinary route. Historical source equivalence is not native coverage.',
 'Fresh MarioEasy physical mushroom→flower→Goomba use/drain is current. Earlier84/220 declaredHard labels were withdrawn: actualEasy. Fresh529 Hard replacements remain historical.',
 '', 'Identity | Easy A/B/R references | Hard A/B/R references | Current731 references']
 for r in rows:
  def short(m):
   c=r['modes'][m];return '/'.join(','.join(c[k])or'-'for k in ['A_physical_evidence','B_controlled_or_acquired_use_evidence','R_ordinary_routes'])
  lines.append(r['identity']+' | '+short('easy')+' | '+short('hard')+' | '+','.join(e for m in ['easy','hard']for e in r['modes'][m]['current731_components']))
 lines+=['','Prioritized finite remaining work']
 for z in plan:lines +=[f"{z['priority']}. {z['unit']}: cap{z['max_profiles']} profiles/{z['max_cases']} cases; track{z['track']}.",z['setup'],z['gate']]
 lines+=['','Required family assertions (complete source links, item IDs/costs and per-mode lists are in ledger.json)']
 for r in rows:lines +=[r['identity']+': '+r['modes']['hard']['required_use']+' Pickups: '+', '.join(r['modes']['hard']['required_pickups'])+'.']
 lines+=['','Limits']+result['limits']
 (a.output/'ledger.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 bind(a.output/'ledger.json');bind(a.output/'ledger.txt')
 manifest=dict(passed=True,bindings=list(bindings.values()));(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 proof=dict(passed=True,native_launches=0,ROM_sha256=CURRENT,ledger_sha256=sha(a.output/'ledger.json'),text_sha256=sha(a.output/'ledger.txt'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bindings),identities=len(rows),mode_cells=74,evidence_records=len(evidence),goal_complete=False)
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))

if __name__=='__main__':main()
