"""Test the source-correct first-freeze expectation without changing other assertions."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-passives-bc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=H/'source-b-review.json';assert not out.exists()
    old=json.loads((H/'old-mmc3-result.json').read_text());assert old['exit']==1
    assert 'FAIL Ice deals forty damage then freezes' in(H/'old-mmc3-host.log').read_text()
    p=json.loads((H/'preparation.json').read_text());original=H/'original-samus-passives-202.lua';assert sha(original)==p['dependencies']['tests/samus-passives-202.lua']
    enemy=R/'reference/crossover2/extracted/scripts/com/smbc/enemies/Enemy.as';assert sha(enemy)==p['dependencies'][str(enemy.relative_to(R)).replace('\\','/')]
    source=enemy.read_text();assert 'if(this.checkAttackProps(param1))'in source
    assert 'addStatusEffect(_loc2_.getStatusEffectFromValue(this,param1));\n            return false;'in source
    s=original.read_text();needle="r('MmEnemyHealthLo')==35,'Ice deals forty damage then freezes the 75-HP Goomba for six seconds'"
    assert s.count(needle)==1
    s=s.replace(needle,"r('MmEnemyHealthLo')==75 and r('MmEnemyHealthHi')==0,'Source first Ice hit freezes without ordinary damage;75HP remains for six seconds'")
    s=s.replace('PASS real Ice Beam damage, six-second freeze, native frozen-enemy platform, and acquired Screw Attack contact protection/defeat','PASS source first-freeze without damage, six-second freeze, native frozen-enemy platform, and acquired Screw Attack contact protection/defeat')
    src=H/'source-b';src.mkdir();body=src/'passives.lua';body.write_text(s)
    wrapper=src/'run.lua';wrapper.write_text('dofile('+json.dumps((R/'tests/menu-bootstrap.lua').as_posix())+')\ndofile('+json.dumps(body.as_posix())+')\n')
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text());assert sha(cp)==p['checkpoint_sha256']
    groups=[]
    for mapper in ['mmc3','mmc5']:
        for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
        o=H/f'source-b-{mapper}';o.mkdir()
        q=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(o),str(wrapper),str(cp.parent/f'smb-crossover-{mapper}.nes'),'--timeout','60'],cwd=R,capture_output=True,text=True)
        log=H/f'source-b-{mapper}-host.log';log.write_text(q.stdout+q.stderr)
        g=dict(mapper=mapper,exit=q.returncode,host_log_sha256=sha(log),files={str(f.relative_to(H)):sha(f)for f in o.iterdir()if f.is_file()});groups.append(g)
        (H/f'source-b-{mapper}-result.json').write_text(json.dumps(g,indent=2)+'\n')
    result=dict(status='PASS_SOURCE_CORRECT_FIRST_FREEZE_AND_UNCHANGED_REMAINING_PASSIVE_ASSERTIONS'if all(g['exit']==0 for g in groups)else'RETAINED_NEXT_SOURCE_B_PASSIVE_FAILURE',
      script_sha256=sha(__file__),original_sha256=sha(original),body_sha256=sha(body),wrapper_sha256=sha(wrapper),enemy_source_sha256=sha(enemy),groups=groups,
      exact_change='First Ice hit HP35 expectation becomes exact75/Hi0 because Enemy.checkAttackProps adds FREEZE and returnsfalse before confirmedHitProj calls takeDamage; only explanatory PASS text also changes. Every timer, immobility, platform and Screw assertion remains.',
      shared_test_modified=False,main_changed=False,goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],sha(out),flush=True)
if __name__=='__main__':main()
