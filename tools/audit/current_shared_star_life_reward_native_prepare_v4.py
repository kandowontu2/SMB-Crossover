"""Prepare only four exact-reward Star/1-Up profiles; never execute native."""
from pathlib import Path
import hashlib
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import current_shared_star_life_remaining_prepare_v3 as prior
import current_shared_star_life_reward_prepare_v4 as source
from current_shared_star_reward_model_v4 import metadata
from current_roster_compact_11_v1 import BASE

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
ALLOWED=('zelda2','simon','darkwing','ryu')
FIXTURE=R/'tests/current-shared-star-life-rewards-v4.lua'
HELPER=R/'tools/audit/current_shared_star_rewards_v4.lua'
PROOF=R/'build/current_shared_star_life_rewards_v4.json'


def fixture():
    base=R/'tests/current-shared-star-life-remaining-v3.lua'
    assert sha(base)=='5efbd82610fcf84b3233fb78bb97f41243bbe421c251d65487999ae128f7a4fd'
    text=base.read_text();helper=HELPER.read_text()
    pairs=[('local function resourcesSame()',helper+'\nlocal function resourcesSame()'),
           (" if done then\n  assert(not pending", " if done then\n  reward_finish()\n  assert(not pending"),
           ('goal_complete=false,scope=C.scope','reward_credits=rewardCredits,reward_provenance=rewardEvents,goal_complete=false,scope=C.scope')]
    for a,z in pairs:assert text.count(a)==1,a;text=text.replace(a,z)
    reverse=text
    for a,z in reversed(pairs):assert reverse.count(z)==1;reverse=reverse.replace(z,a)
    assert reverse==base.read_text(),'Only exact credits/provenance/final accounting added'
    if FIXTURE.exists():assert FIXTURE.read_text()==text,'Never mutate prepared fixture'
    else:FIXTURE.write_text(text,newline='\n')
    assert 'removeMemoryCallback'not in text and text.count('emu.write(')==2
    return pairs


def main():
    out=R/'build/current-ab221-shared-star-life-rewards-v4'
    assert not out.exists(),'No evidence overwrites'
    assert sha(PROOF)=='c0f368805db0295350d010145efaf90f46a448e52f626b68bfdabe6a10bb1379'
    proof=json.loads(PROOF.read_text());assert set(proof['source_pass'])==set(ALLOWED)
    assert set(proof['held'])=={'grant','sypha','alucard'}
    changes=fixture();text=prior.change(prior.OLD.read_text())
    old="fixture=R/'tests/current-shared-star-life-remaining-v3.lua'"
    assert text.count(old)==1;text=text.replace(old,"fixture=R/'tests/current-shared-star-life-rewards-v4.lua'")
    old='hooks=hooks,ram=ram,navigation=';assert text.count(old)==1
    text=text.replace(old,'hooks=hooks,ram=ram,rewards=reward_cfg(b,a.identity),navigation=')
    ns={'__file__':str(Path(__file__)),'__name__':'_rewards_native_v4'}
    exec(compile(text,str(prior.OLD),'exec'),ns);ns['resources']=prior.resource_fields
    original_hooks=ns['hooks_for']
    current={}
    def cfg(b,identity):
        _,character,_,variant=BASE[identity]
        z=metadata(b,identity,prior.resource_fields(identity),character,variant)
        assert z==proof['source_writer_metadata'][identity]
        return z
    def hooks(b):
        old,sfx=original_hooks(b);new=cfg(b,current['identity'])
        assert not set(old)&set(new['hooks'])
        return dict(old,**new['hooks']),sfx
    def completed(bundle,identity,mode,actual_hooks):
        assert identity in ALLOWED and mode==1 and hashlib.sha256(bundle['raw']).hexdigest()==proof['ROM_sha256']
        old,_=original_hooks(bundle)
        assert actual_hooks==dict(old,**cfg(bundle,identity)['hooks'])
        return proof['source_pass'][identity]
    ns['reward_cfg']=cfg;ns['hooks_for']=hooks;ns['campaign']=completed
    out.mkdir();readies=[]
    for identity in ALLOWED:
        current['identity']=identity;child=out/identity;argv=sys.argv
        sys.argv=[str(Path(__file__)),'--identity',identity,'--output',str(child)]
        try:ns['main']()
        finally:sys.argv=argv
        path=child/'prepared-not-run.json';z=json.loads(path.read_text())
        extra={Path(__file__),prior.OLD,Path(prior.__file__),Path(source.__file__),
            HELPER,R/'tools/audit/current_shared_star_reward_model_v4.py',PROOF,
            R/'build/current_cv3_life_gain_counterexample_v1.json',
            R/'docs/qa/cv3-earned-equipment-life-gain-2026-10-27.txt',
            R/'build/current-ab221-shared-star-life-remaining-v3/prepared-batch.json'}
        paths={Path(p['path'])for p in z['bindings']}|extra
        z.update(reward_scope='Exact genuine defeat/collection writer PC/bank/old/new/item/amount credits only; all other original health/inventory conservation and hardware guards retained. Native actual write-callback semantics still require separately authorized execution.',
            native_run=False,source_pass_identity=identity,held_CV3='Actual 1-Up loss remains a product negative; excluded from these four preparations.',
            inherited_source_proof=dict(path=str(PROOF),sha256=sha(PROOF)))
        z['bindings']=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)]
        put(path,z);readies.append(dict(identity=identity,path=str(path),sha256=sha(path),bindings=len(z['bindings']),command=str(child/'command.json')))
    put(out/'prepared-batch.json',dict(status='SOURCE_QUALIFIED_NATIVE_UNRUN',native_run=False,
        ROM_sha256=proof['ROM_sha256'],readies=readies,
        fixture=dict(path=str(FIXTURE),sha256=sha(FIXTURE)),helper=dict(path=str(HELPER),sha256=sha(HELPER)),
        exact_reversible_fixture_changes=[dict(before=a,after=z if len(z)<500 else 'Literal shared reward helper inserted before resourcesSame')for a,z in changes],
        source_proof=dict(path=str(PROOF),sha256=sha(PROOF)),
        original_v3_unchanged=True,CV3_genuine_product_negative_retained=True,
        no_source_runtime_ROM_copies=True))
    print(json.dumps(dict(batch=str(out/'prepared-batch.json'),sha256=sha(out/'prepared-batch.json'),readies=len(readies),native_run=False)))


if __name__=='__main__':main()
