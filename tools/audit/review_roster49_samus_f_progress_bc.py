"""Rehash current Samus evidence; distinguish seeded components from real routes."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-a';T=V/'root49-current-f-samus-passives-bc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def main():
    out=V/'root49-samus-f-progress-review-bc.json';assert not out.exists()
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
    c=json.loads(cp.read_text())
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    adoption=T/'adoption-e.json';assert sha(adoption)=='a7257a8807f1a2301e4136571fdb5d3871c13abb40cfe8222edb17f4bd8e28fd'
    a=json.loads(adoption.read_text());assert sha(R/'tests/samus-passives-202.lua')==a['adopted_fixture_sha256']
    assert sha(T/'thaw-d-review.json')==a['private_review_sha256']and sha(T/'adoption-preparation-e.json')==a['preparation_sha256']
    setup=json.loads((T/'preparation.json').read_text())
    assert sha(T/'original-samus-passives-202.lua')==setup['dependencies']['tests/samus-passives-202.lua']
    actual=[]
    for g in a['groups']:
        assert g['exit']==0
        assert sha(T/f"adopted-e-{g['mapper']}-host.log")==g['host_log_sha256']
        for n,h in g['files'].items():assert sha(T/n)==h,n
        diag=json.loads((T/f"adopted-e-{g['mapper']}/smb-crossover-{g['mapper']}-samus-thaw-result.json").read_text())
        assert diag['frame']==690 and diag['hp']==35 and diag['timer']==0 and diag['flag']!=0 and diag['state']&32==0
        log=(T/f"adopted-e-{g['mapper']}/smb-crossover-{g['mapper']}-samus-passives-202.log").read_text()
        assert 'PASS first-freeze no damage, actual thaw hit75-to35, native frozen platform, and acquired Screw Attack contact protection/defeat'in log
        actual.append(dict(mapper=g['mapper'],second_hit=diag))
    src=R/'reference/crossover2/extracted/scripts/com/smbc/enemies/Enemy.as';s=src.read_text()
    assert 'function checkAttackProps'in s and 'function confirmedHitProj'in s
    packets={};traces={};injuries={}
    for tag in ['m','n','o','p']:
        p=R/f'build/roster-through-2-2/root49-f-samus-route-{tag}-2-v0-mmc3';m=json.loads((p/'manifest.json').read_text());rr=json.loads((H/f'native-result-{tag}.json').read_text())
        assert sha(p/'manifest.json')==rr['manifest_sha256']and sha(H/f'native-{tag}.log')==rr['host_log_sha256']
        assert m['rom_sha256']==sha(p/'smb-crossover-mmc3.nes')=='ae0f981a8846238185d2d69549accf69f68b779832cafa7dd35bc431b00b09ca'
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and not m['config']['record']
        assert m['config']['character']==2 and m['config']['variant']==0 and m['config']['mapper']=='mmc3'
        identity=json.loads((p/'current-c-identity.json').read_text());assert identity==dict(character=2,behavior=0,marioVariant=0,billVariant=0,outlinesOff=1)
        tr=rows(p/'trace.csv');inj=rows(p/'actual-injury-b.csv');traces[tag]=tr;injuries[tag]=inj
        packets[tag]=dict(result=m.get('result'),last_pose=tr[-1],files={q.name:dict(bytes=q.stat().st_size,sha256=sha(q))for q in p.iterdir()if q.is_file()},preparation_sha256=sha(H/f'preparation-{tag}.json'),native_result_sha256=sha(H/f'native-result-{tag}.json'))
    boss=rows(R/'build/roster-through-2-2/root49-f-samus-route-m-2-v0-mmc3/live-boss-m.csv')
    hp=[];previous=None
    for z in boss:
        if z['hp']!=previous:hp.append((int(z['frame']),int(z['hp'])));previous=z['hp']
    assert hp[:4]==[(21001,120),(21037,80),(21046,40),(21054,0)],hp[:4]
    control_dead=next(z for z in boss if z['frame']=='21054')
    assert control_dead['actors'].split(';')[0]=='0:1:6:35:2165:117:0'
    dead=next(z for z in injuries['m']if z['event']=='EndFrame'and z['frame']=='21055'and z['slot']=='0')
    assert dead['id']=='6'and int(dead['estate'])&32 and dead['flag']=='1'
    assert not any(z['event']=='InjurePlayer'and int(z['frame'])>21000 for z in injuries['m'])
    n=packets['n']['result'];assert n['stage_entries']['1-0']==22020 and n['frames']==24385 and n['failure']=='death'
    plant=next(z for z in injuries['o']if z['event']=='EndFrame'and int(z['frame'])>24350 and z['slot']=='0'and(z['flag']=='0'or z['id']!='13'or int(z['estate'])&32))
    assert int(plant['frame'])<24620
    p=next(z for z in injuries['p']if z['event']=='InjurePlayer'and z['slot']==z['owner']and z['frame']=='24886')
    assert p['id']=='13'and p['slot']=='2'and p['ex']=='1848'and p['ey']=='152'and p['playerY']=='134'
    prefix_checks=[]
    for before,after,count in [('m','n',21200),('n','o',24350),('o','p',24680)]:
        assert traces[before][:count]==traces[after][:count]
        prefix_checks.append(dict(before=before,after=after,literal_physical_rows=count))
    report=dict(status='PASS_ROOT_SAMUS_F_FOUR_STAGE_PROGRESS_AND_SOURCE_CORRECT_COMPONENTS',script_sha256=sha(__file__),checkpoint_sha256=sha(cp),production_sources_rehashed=len(c['source_hashes']),
      test_adoption_sha256=sha(adoption),primary_Enemy_source_sha256=sha(src),component_results=actual,
      component_scope='Hard authored arena/ownership, real Ice projectiles. First freeze preserves lazy0HP; second hit thaws and proves75-to35 damage. Native frozen support/no-injury and authored Screw contact protection/defeat; no natural pickup or source bitmap claim.',
      packets=packets,boss_damage_transitions=hp[:4],native_boss_defeat=dead,controller_defeat_snapshot=control_dead,
      observer_epoch='capture writes frame+1; EndFrame world0 sampled on even previous frame, hence odd labeled rows. Exact controller row21054 has defeated native actor, observer row21055 confirms.',
      first_2_1_plant_native_defeat=plant,second_plant_contact=p,literal_prefixes=prefix_checks,
      qualifications=['M and O stop on controller guards; N and P are actual deaths. None is a full route or final recording.',
        'Old35HP-first-freeze and private75HP-initialized assumptions remain archived. Native first-freeze health0 was probed; second-hit damage assertion adds coverage rather than merely accepting0.',
        'Samus route is Easy on MMC3. Seeded component tests are Hard on both maps. No full arsenal, full historical73-failure suite, audiovisual/source geometry or lag completion claim.'],
      goal_complete=False,production_ROM_changed=False)
    out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],sha(out),flush=True)
if __name__=='__main__':main()
