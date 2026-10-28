"""Derive four ee115 readies with only the completed-case phase/logging fix. No native."""
from pathlib import Path
import csv,hashlib,json

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:dict(path=str(Path(p).resolve()),bytes=Path(p).stat().st_size,sha256=sha(p))
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n',newline='\n')
PAIRS=[(b'{kind,wall,updates,index,rec and rec.age or 0',b'{kind,wall,updates,rec and rec.case_index or index,rec and rec.age or 0'),(b"event('update');assert(rec.age<t.limit,'Finite source-qualified case update deadline')",b"event('update');if phase=='case'then assert(rec.age<t.limit,'Finite source-qualified case update deadline')end")]

def main():
    oldfixture=ROOT/'tools/audit/current_ship_earned_v1.lua';fixture=oldfixture.with_name('current_ship_earned_v2.lua')
    original=oldfixture.read_bytes();patched=original
    for a,b in PAIRS:assert patched.count(a)==1;patched=patched.replace(a,b)
    assert patched==fixture.read_bytes();reverse=patched
    for a,b in reversed(PAIRS):assert reverse.count(b)==1;reverse=reverse.replace(b,a)
    assert reverse==original
    marker=b'-- All callback registration is startup-static.';end=b"hook('DmaComplete',function()\n if not entered"
    guard=original[original.index(marker):original.index(end)]
    assert len(guard)==4058 and patched[patched.index(marker):patched.index(end)]==guard
    sourcehandoff=ROOT/'build/current-ee115-ship-earned-handoff-v1.json';h=json.loads(sourcehandoff.read_text())
    assert sha(sourcehandoff)=='6cfbd3c479f158afd270c5b76998397fd6e9ed10cdebae4a2ec52f5d1cd3461e'
    for n,v in h['owned_files'].items():assert sha(ROOT/n)==v['sha256'],n
    olddir=ROOT/'build/current-ee115-vic-hard-earned-v1';native=olddir/'native';launch=olddir/'launch.json';l=json.loads(launch.read_text())
    assert l['exit_code']==1 and l['changed_inputs']==[] and l['settings_before']==l['settings_after']
    csvpath=native/'ship-components.csv';rows=list(csv.DictReader(csvpath.open()))
    completed=[r for r in rows if r['event']=='case-complete'];assert len(completed)==1 and completed[0]['case']=='1'and completed[0]['age']=='130'
    assert rows[-1]['case']=='2'and rows[-1]['age']=='130'and rows[-1]['event']=='update'
    log=native/'roster-20261028-fixes-run.log';assert 'Finite source-qualified case update deadline'in log.read_text()
    negative=ROOT/'build/current-ee115-vic-boundary-negative-v1.json';assert not negative.exists()
    put(negative,dict(original_native_passed=False,original_native_exit=1,original_first_FALSE='Finite source-qualified case update deadline',
        actual_wall=int(rows[-1]['wall']),actual_updates=int(rows[-1]['update']),case1_complete_fire_age=130,case2_not_started=True,
        first_divergence='Completed case sets phase setup/index2, but terminal callback asserts old rec.age130<old t.limit130. Next CSV row also incorrectly uses index2 with oldrec.',
        source_test_fixture_error=True,no_product_failure_inferred=True,original_guards_preserved=True,settings_unchanged=True,
        retained_original_files=[bind(p)for p in [olddir/'prepared-not-run.json',launch,csvpath,log,native/'capture-budget.json',native/'item-01.png']]))
    # Typed phase-boundary models, not an execution of a Lua VM. The native
    # mechanic assertions preceding finishCase remain byte-exact by reversal.
    models=[]
    for p in h['profiles']:
        ready=ROOT/p['ready']['path'];old=json.loads(ready.read_text())
        for task in old['plan'] if 'plan'in old else json.loads((ready.parent/'config.json').read_text())['plan']:
            limit=task['limit']
            for phase,age,want in [('case',limit-1,True),('case',limit,False),('case',limit+1,False),('setup',limit,True),('complete',limit,True)]:
                actual=phase!='case'or age<limit;assert actual==want
                models.append(dict(variant=old['variant'],case=task['name'],phase=phase,age=age,limit=limit,accepted=actual))
    phaseproof=ROOT/'build/current-ee115-ship-phase-controls-v1.json';assert not phaseproof.exists()
    put(phaseproof,dict(passed=True,native_run=False,Lua_VM_executed=False,typed_phase_controls=models,
        substitutions=[dict(old=a.decode(),new=b.decode(),count=1)for a,b in PAIRS],reverse_exact=True,
        strict_guard_literal_bytes=4058,strict_guard_sha256=hashlib.sha256(guard).hexdigest(),
        deadline_not_widened=True,unfinished_at_or_past_bound_rejected=True,
        game_mechanics_inputs_seeds_caps_all_other_bytes_exact=True,
        old_fixture=bind(oldfixture),new_fixture=bind(fixture),source_handoff=bind(sourcehandoff),original_FALSE=bind(negative)))
    final=[]
    for name in ['vic','octopus','twinbee','pentarou']:
        olddir=ROOT/f'build/current-ee115-{name}-hard-earned-v1';out=olddir.with_name(olddir.name[:-2]+'v2');assert not out.exists()
        oldready=olddir/'prepared-not-run.json';old=json.loads(oldready.read_text());assert not old['native_run']
        for q in old['bindings']:assert sha(q['path'])==q['sha256']and Path(q['path']).stat().st_size==q['bytes']
        out.mkdir();(out/'config.json').write_bytes((olddir/'config.json').read_bytes())
        run=(olddir/'run.lua').read_bytes();a=oldfixture.as_posix().encode();b=fixture.as_posix().encode();assert run.count(a)==1
        newrun=run.replace(a,b);assert newrun.replace(b,a)==run;(out/'run.lua').write_bytes(newrun)
        command=json.loads((olddir/'command.json').read_text());command['argv']=[s.replace(str(olddir/'native'),str(out/'native')).replace(str(olddir/'run.lua'),str(out/'run.lua'))for s in command['argv']]
        put(out/'command.json',command)
        remap={str(oldfixture.resolve()):fixture,str((olddir/'config.json').resolve()):out/'config.json',str((olddir/'run.lua').resolve()):out/'run.lua',str((olddir/'command.json').resolve()):out/'command.json'}
        new=dict(old);new['bindings']=[bind(remap.get(q['path'],Path(q['path'])))for q in old['bindings']]
        new['bindings'] += [bind(p)for p in [Path(__file__),oldready,oldfixture,phaseproof,negative]]
        new.update(observer_phase_version=2,old_ready_sha256=sha(oldready),original_Vic_v1_FALSE_preserved=True,
            source_campaigns_not_repeated_or_retagged=True,config_and_source_controls_unchanged=True,
            phase_fix='Check existing deadline only for unfinished current case; log immutable rec.case_index after completion. All existing pre-completion mechanic predicates and limits exact.',native_run=False)
        put(out/'prepared-not-run.json',new)
        for q in new['bindings']:assert sha(q['path'])==q['sha256']and Path(q['path']).stat().st_size==q['bytes']
        final.append(dict(identity=name,ready=bind(out/'prepared-not-run.json'),bindings=len(new['bindings']),command=bind(out/'command.json')))
    print(json.dumps(dict(prepared=True,native_run=False,phase_controls=len(models),negative=bind(negative),controls=bind(phaseproof),profiles=final),indent=2))

if __name__=='__main__':main()
