"""Private exact-span native eligibility filter for special weapon batches."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';P=V/'root49-lag-combined-i';J=V/'root49-water-enemy-filter-gy'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not J.exists();J.mkdir()
 assert sha(P/'build-review.json')=='55c241370c34437410747a9762d3a11c4c7f52bb5d50e1e45a067360cff9ddbe'
 prep=json.loads((P/'preparation.json').read_text(encoding='utf-8'))
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+200000000<100000000000
 for n,h in prep['source_hashes'].items():
  p=P/'source'/n;assert sha(p)==h
  d=J/'source'/n;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
 for n,h in prep['generated11'].items():
  p=P/'source/build/generated'/n;assert sha(p)==h
  d=J/'source/build/generated'/n;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
 source=J/'source/src/special_weapons.s';text=source.read_text(encoding='utf-8');start=text.index('EnemyCandidates:');end=text.index('  lda SsBodyStop',start)
 old=text[start:end];assert old.count('inc SsEnemies')==1 and old.endswith('  jpl EnemyCandidates\n')
 new='''EnemyCandidates:
  lda Enemy_Flag,x
  beq EnemyNext
  bmi EnemyNext                  ; Bowser duplicate is not another target.
  lda Enemy_State,x
  and #$20
  bne EnemyNext
  lda Enemy_ID,x
  cmp #$15
  bcc EnemyFound
  cmp #Bowser
  beq EnemyFound
  cmp #BulletBill_CannonVar
  bne EnemyNext
EnemyFound:
  ; The unchanged native Enemies consumer rejects this exact field before
  ; preparing any target box. One batch admission avoids eight pointless
  ; bridge/farcall/scans while an active actor is still outside its bounds.
  lda EnemyOffscrBitsMasked,x
  bne EnemyNext
  inc SsEnemies
EnemyNext:
  dex
  bpl EnemyCandidates
  jmp EnemyCandidatesDone
  .res 50-(*-EnemyCandidates),$ea
EnemyCandidatesDone:
'''
 source.write_text(text[:start]+new+text[end:],encoding='utf-8');shutil.copyfile(P/'build.py',J/'build.py')
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),parent_review_sha256=sha(P/'build-review.json'),parent_source_hashes=prep['source_hashes'],generated11=prep['generated11'],old_loop=old,new_loop=new,candidate_source_sha256=sha(source),workspace_before=used,phase_cap=200000000,reserve=50000000,global_cap=100000000000,scope='Only privateI special-enemy batch admission gains the same EnemyOffscrBitsMasked rejection already in its unchanged native Enemies consumer. Exact50B scan span; no new RAM/CHR, no source hitbox or damage changes. Actual native/control/source validation remains pending.'),indent=2)+'\n',encoding='utf-8')
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('enemy_gy_image',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
 builds=[]
 for mapper in ['mmc3','mmc5']:
  for baseline in [False,True]:
   stem='smb-crossover-'+mapper+('-baseline'if baseline else'');args=[sys.executable,str(J/'build.py'),'--mapper',mapper]+(['--baseline']if baseline else[])
   with(J/(stem+'.log')).open('wb')as log:q=subprocess.run(args,cwd=R,stdout=log,stderr=subprocess.STDOUT)
   assert q.returncode==0,(mapper,baseline)
   before=P/'source/build'/(stem+'.nes');after=J/'source/build'/before.name;a=before.read_bytes();b=after.read_bytes();assert len(a)==len(b)
   if baseline:assert a==b;span=None;foreign=None
   else:
    ai,bi=im.Image(before),im.Image(after);assert ai.ram==bi.ram
    span=ai.hook('EnemyCandidates','SpecialWeapons')['rom_offset'];endspan=ai.hook('EnemyNext','SpecialWeapons')['rom_offset']+3;assert endspan-span==50
    assert a[:span]==b[:span]and a[endspan:]==b[endspan:]
    foreign=0
    for s in ai.data['sym']:
     if 'seg'not in s or 'val'not in s:continue
     seg=ai.segs[s['seg']]
     if 'ooffs'not in seg:continue
     off=seg['ooffs']+s['val']-seg['start']
     if span<=off<endspan:continue
     scope=ai.scopes.get(s.get('scope'),{});rows=[z for z in bi.data['sym']if z.get('name')==s['name']and z.get('val')==s['val']and z.get('seg')==s['seg']]
     # Scope IDs can change when a new label is added; exported/global and
     # named proc entries are checked by their native scope/name below.
     if s.get('scope')==1:
      t=bi.sym(s['name']);assert t['val']==s['val'];foreign+=1
   builds.append(dict(mapper=mapper,baseline=baseline,changed_bytes=sum(x!=y for x,y in zip(a,b)),allowed_span_offset=span,foreign_global_addresses_equal=foreign,artifacts={e:dict(path=str(after.with_suffix('.'+e).relative_to(R)),sha256=sha(after.with_suffix('.'+e)),bytes=after.with_suffix('.'+e).stat().st_size)for e in ['nes','dbg','lbl','map']}));print(stem,builds[-1]['changed_bytes'],flush=True)
 out=J/'build-review.json';out.write_text(json.dumps(dict(status='PASS_PRIVATE_EXACT50B_BATCH_FILTER_BUILD_NATIVE_VALIDATION_PENDING',preparation_sha256=sha(J/'preparation.json'),builds=builds,main_changed=False,installed=False,goal_complete=False),indent=2)+'\n',encoding='utf-8');print('BUILD',sha(out),flush=True)
if __name__=='__main__':main()
