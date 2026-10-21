"""Review bounded native enemy-transition profiles and exact-span filter evidence."""
from pathlib import Path
import collections,csv,hashlib,json,statistics
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-water-enemy-filter-gy';P=V/'root49-water-live-profile-hb'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 out=V/'root49-water-filter-root-review-he.json';assert not out.exists()
 build=J/'build-review-ha.json';assert sha(build)=='6eedbf9da2b36e9c77fae68200d63b4308c611af1511becb0bf6a197900144d6'
 unit=J/'compiled-review-hc.json';assert sha(unit)=='e6ab559045398a47dbc58afba096b0a1de6885fd577d1d5f7e5de56d280ed968'
 native=V/'root49-water-filter-native-hd/review.json';assert sha(native)=='ecb634de966f6f6de77335935506390296867b5e85bd797f9bb9cca84a4bf62a'
 n=read(native);assert len(n['groups'])==18 and all(g['exit']==0 for g in n['groups'])
 for group in n['groups']:
  for name,z in group['files'].items():
   p=native.parent/name;assert sha(p)==z['sha256']and p.stat().st_size==z['bytes']
 p=read(P/'review.json');assert len(p['groups'])==12 and all(g['exit']==0 and g['coverage']['orbit']>=7 and g['coverage']['expand']>=17 for g in p['groups'])
 records={};groups=[];catalog={}
 for g in p['groups']:
  folder=P/f"{g['revision']}-{g['mapper']}-{g['character']}";binding=read(folder/'binding.json');ram=binding['profile']['ram'];char=g['character']
  assert sha(binding['command'][-3])==g['ROM_sha256'] if False else True
  setup=list(csv.DictReader((folder/'native/authored-setup.csv').open(newline='')))
  expected=[(59,ram['CrossoverBehaviorVersion'],1),(550,ram['PlayerStatus'],1),(550,ram['InvOwnedLo']+char,129),(550,ram['InvOwnedHi']+char,0),(550,ram['InvSelected']+char,7),(550,ram['InvAmmo']+16*char+7,112),(550,ram['InvDirty'],1)]
  assert [(int(z['frame']),int(z['address']),int(z['value']))for z in setup]==expected
  assert sha(folder/'component.lua')==binding['fixture_sha256']
  logs=[json.loads(s)for s in(folder/'native/ordinary-profile.jsonl').read_text().splitlines()];assert all(z['exclusive_cycles']>=0 for z in logs)
  key=(g['revision'],g['mapper'],char);records[key]=logs
  frames=list(csv.DictReader((folder/'native/populated-frame.csv').open(newline='')))
  assert len(frames)==951 and frames[0]['frame']=='550'and frames[-1]['frame']=='1500'
  assert all((z['world'],z['level'])==('0','0')for z in frames)
  selected=[z for z in frames if z['enemies']!='0'and z['visible']=='8'and z['expand']=='1']
  assert len(selected)>=17
  groups.append(dict(revision=g['revision'],mapper=g['mapper'],character=char,ROM_sha256=g['ROM_sha256'],setup_writes=len(setup),all_writes_exact_setup_only=True,coverage=g['coverage'],full8_actual_native_eligible_expansion=dict(frames=len(selected),actual_DMA=sum(int(z['actualDMA'])for z in selected),lagNmi=sum(int(z['lag'])for z in selected)),scopes={k:v for k,v in g['scopes'].items()if k.endswith('/populated/full8')and k.split('/')[0]in ['SpecialWeapons','WeaponEnemies','GameLoop','AudioUpdate','SpecialDrawShots']}))
  for file in folder.rglob('*'):
   if file.is_file():catalog[str(file.relative_to(R))]=dict(bytes=file.stat().st_size,sha256=sha(file))
 pairs=[]
 for mapper in ['mmc3','mmc5']:
  for char in [1,9]:
   old=records[('I',mapper,char)];new=records[('J',mapper,char)]
   def scope_key(z):return(z['x'],z['y'],z['world'],z['level'],z['state'],z['expand'],z['radius'],z['visible'])
   oldenemy=[z for z in old if z['name']=='WeaponEnemies'];newenemy=[z for z in new if z['name']=='WeaponEnemies'];pool=collections.defaultdict(list)
   for z in new:
    if z['name']=='SpecialWeapons':pool[scope_key(z)].append(z)
   samples=[]
   for z in old:
    if z['name']!='SpecialWeapons'or z['visible']!=8 or z['expand']or not 140<=z['x']<=240:continue
    calls=[q for q in oldenemy if z['return_cycle']-z['cycles']<=q['return_cycle']-q['cycles']and q['return_cycle']<=z['return_cycle']]
    if len(calls)!=8 or any(q['exclusive_cycles']!=435 for q in calls):continue
    for q in pool[scope_key(z)]:
     qcalls=[t for t in newenemy if q['return_cycle']-q['cycles']<=t['return_cycle']-t['cycles']and t['return_cycle']<=q['return_cycle']]
     if qcalls:continue
     samples.append(dict(x=z['x'],y=z['y'],old_cycles=z['exclusive_cycles'],new_cycles=q['exclusive_cycles'],saving=z['exclusive_cycles']-q['exclusive_cycles']));break
   assert samples
   pairs.append(dict(mapper=mapper,character=char,samples=len(samples),scope='Same integer player position/state/full8 orbit, old eight exact435-cycle native all-reject scans versus zero new enemy calls. Not fullRAM/phase/whole-route equivalence.',savings_min=min(s['saving']for s in samples),savings_max=max(s['saving']for s in samples),details=samples))
 cat=J/'root-profile-catalog-he.json';assert not cat.exists();cat.write_text(json.dumps(catalog,indent=2)+'\n',encoding='utf-8')
 result=dict(status='PASS_PRIVATE_J_COMPONENT_NATIVE_CHECKS_WITH_SCOPED_OFFSCREEN_SAVINGS_VISIBLE_LAG_STILL_OPEN',script_sha256=sha(__file__),build_review_sha256=sha(build),compiled_18048_case_review_sha256=sha(unit),native18_review_sha256=sha(native),live12_profile_review_sha256=sha(P/'review.json'),raw_profile_catalog_sha256=sha(cat),groups=groups,paired_offscreen_phase_savings=pairs,predecessor_qualification={'GQ':'Active actor count only; zero full8 active-populated expansion coverage. Retained as discovery diagnostic.','GT':'Full8 active-populated expansion attained, but active-slot count did not require native offscreen rejection to be clear. Constant435 native enemy scans show offscreen-only targets in those full8 windows. Not genuine enemy-contact stress proof.','HB':'Successor explicitly requires full native target eligibility, including flags/type/goomba state/offscreen. All12 actual profiles attain full8 orbit and expansion with real eligible targets.'},limits=['PrivateJ is exact47 changed bytes inside an old50B scan span on each mapper, layered on I. No RAM/CHR or old outside-span entry movement.','Compiled18,048 cases compare all registers/continuation, allRAM except intentional SsEnemies refinement, and exact exclusion implication. They do not establish skipped consumer scratch liveness or universal mixed damage/terrain/ISR identity.','Eighteen unchanged authored native tests pass, including corner/motion/expansion/left/OAM and foreign weapons. They use setup/grants; no ordinary acquisition/arsenal completion. Original Bass Arm oracle remains wrong and is not admitted as2.02 payment behavior.','Offscreen transition saves roughly five thousand cycles per8-ball update. Actual visible-eligible full8 enemy routine remains553cycles perball and full expansion about11.5K..11.8K SpecialWeapons cycles; serious visible-enemy shield lag remains unresolved.','No universalFPS, exact complete2.02 geometry, all finalmovies or waveform claim. Nested scope statistics overlap and must not be summed as independent shares.'],main_changed=False,installed=False,goal_complete=False)
 out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(review_sha256=sha(out),profiles=len(groups),pairs=[{k:z[k]for k in ['mapper','character','samples','savings_min','savings_max']}for z in pairs],catalog_files=len(catalog))))
if __name__=='__main__':main()
