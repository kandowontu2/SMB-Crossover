"""Source-only exact reward accounting; retain real CV3 life-reset negatives."""
from pathlib import Path
import hashlib
import json
import re
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import current_shared_star_life_remaining_prepare_v3 as prior
from current_shared_star_reward_model_v4 import Model,metadata,IDENTITIES

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')


def compiled():
    assert sha(prior.OLD)=='3be0314a1c8411abde5baa4fcc12de05b1f3305d72bb6d5e577efe35f95acc56'
    text=prior.change(prior.OLD.read_text())
    pairs=[
        ("    trace=[];original=NesMPU.step", "    trace=[];original=NesMPU.step\n    reward=reward_make(b,identity,q)"),
        ("        original(c)","        reward.event(c.pc,bank,c.a,c.x,c.y,phase,hits)\n        start=len(q.m.writes);at=c.pc\n        original(c)\n        for address_written,value in q.m.writes[start:]:reward.write(address_written,value,at,bank)"),
        ("        initial=snapshot();lives=", "        initial=snapshot();reward.start(initial);lives="),
        ("    return dict(passed=True,native_run=False,identity=identity,full_GameLoop_calls=calls,real_source_hooks=hits,events=trace,", "    return dict(passed=True,native_run=False,identity=identity,full_GameLoop_calls=calls,real_source_hooks=hits,events=trace,reward_provenance=reward.finish(),")]
    for a,z in pairs:
        assert text.count(a)==1,a
        text=text.replace(a,z)
    ns={'__file__':str(prior.OLD),'__name__':'_reward_source_v4'}
    exec(compile(text,str(prior.OLD),'exec'),ns)
    ns['resources']=prior.resource_fields
    return ns


def main():
    out=R/'build/current_shared_star_life_rewards_v4.json'
    assert not out.exists(),'Never overwrite a completed source packet'
    ns=compiled();rom=R/'build/mega_proto_body_palette_9ea.nes'
    assert sha(rom)==ns['EXPECTED']
    b=ns['scoped_load'](rom);hooks,_=ns['hooks_for'](b)
    active={};cfgs={};passes={};held={}
    def make(bundle,identity,q):
        _,char,vname,variant=ns['BASE'][identity]
        cfg=metadata(bundle,identity,prior.resource_fields(identity),char,variant)
        strings=set(re.findall(r"['\"]([A-Za-z_][A-Za-z_0-9]*)['\"]",(R/'tools/audit/current_shared_star_reward_model_v4.py').read_text()))
        names=(strings & set(bundle['syms']))|{p['name']for p in prior.resource_fields(identity)}
        ram={n:ns['address'](bundle,n)for n in names}
        model=Model(cfg,ram,q.get);active[identity]=model;cfgs[identity]=cfg
        return model
    ns['reward_make']=make
    for identity in IDENTITIES:
        try:
            passes[identity]=ns['campaign'](b,identity,1,hooks)
            print(json.dumps(dict(identity=identity,source_pass=True,native_run=False)),flush=True)
        except Exception as e:
            model=active.get(identity)
            held[identity]=dict(source_pass=False,native_run=False,error=repr(e),
                exact_observed_credits=model.credits if model else [],
                exact_observed_provenance=model.events if model else [])
            print(json.dumps(dict(identity=identity,source_pass=False,error=repr(e),native_run=False)),flush=True)
    paths=[Path(__file__),R/'tools/audit/current_shared_star_reward_model_v4.py',prior.OLD,Path(prior.__file__),
           rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),
           R/'build/current_cv3_life_gain_counterexample_v1.json']
    put(out,dict(ROM_sha256=ns['EXPECTED'],native_run=False,source_pass=passes,held=held,
        source_writer_metadata=cfgs,bindings=[dict(path=str(p),sha256=sha(p))for p in paths],
        scope='Only exact real defeat or physical collection writers update the conserved expected resource element. Spawn is not collection. Original whole-resource invariant remains strict outside exact credits. Genuine CV3 life-gain reset must remain a negative. No native preparation or result yet.'))
    print(json.dumps(dict(proof=str(out),sha256=sha(out),source_pass=len(passes),source_held=len(held),native_run=False)),flush=True)


if __name__=='__main__':main()
