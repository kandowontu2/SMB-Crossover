"""Remaining34 identity Star/1-Up source campaigns and small readies; no native."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
from current_roster_compact_11_v1 import BASE
OLD=R/'tools/audit/current_shared_star_life_prepare_v1.py'
FIXTURE=R/'tests/current-shared-star-life-vic-v2.lua'
NEW=R/'tests/current-shared-star-life-remaining-v3.lua'
WHITELIST=tuple(n for n in BASE if n not in ['mario','mac','vic'])
assert len(WHITELIST)==34
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')


def resource_fields(identity):
    out=[dict(name=n,index=0,count=c)for n,c in [('PlayerStatus',1),('PlayerSize',1),('InvOwnedLo',12),('InvOwnedHi',12),('InvSelected',12),('InvAmmo',192)]]
    extra={
        'roll':[('RlHealth',1),('RlEnergy',1)],
        'darkwing':[('DwHealth',1),('DwGas',1),('DwAdaptor',1)],
        'kirby':[('KbHealth',1),('KbCopy',1)],'meta':[('KbHealth',1),('KbCopy',1)],
        'chip':[('CdHealth',1)],'dale':[('CdHealth',1)],
        'mike':[('JnHealth',1),('JnMaxHearts',1),('JnOwnedTier',1),('JnSelected',1),('JnAmmo',10)]}
    if identity in ['grant','sypha','alucard']:extra[identity]=[('Cv3Health',3),('Cv3Hearts',3),('Cv3Subweapon',3),('Cv3Power',3)]
    if identity in ['leonardo','raphael','michelangelo','donatello']:extra[identity]=[('TnHealth',4),('TnEquipment',4),('TnAmmo',4)]
    if identity in ['octopus','twinbee','pentarou']:extra[identity]=[('PnBellFlags',1),('PnPunch',1),('PnAux',1),('PnSkin',1),('PnType',1)]
    out.extend(dict(name=n,index=0,count=c)for n,c in extra.get(identity,[]))
    return out


def change(text):
    pairs=[("PILOTS = ('mario', 'mac', 'vic')",'PILOTS = '+repr(WHITELIST)),
        ("fixture=R/'tests/current-shared-star-life.lua'","fixture=R/'tests/current-shared-star-life-remaining-v3.lua'"),
        ("    y=q.get('Player_Y_Position')-8;assert 24<=y<=200","    y=q.get('Player_Y_Position')-8;assert 24<=y<=200\n    world=q.get('VvObjX')-8+q.get('ScreenLeft_X_Pos')+256*q.get('ScreenLeft_PageLoc') if character==18 else q.get('Player_X_Position')+256*q.get('Player_PageLoc')"),
        ("Enemy_BoundBoxCtrl=3 if kind==46 else 9,Enemy_X_Position=q.get('Player_X_Position'),\n        Enemy_PageLoc=q.get('Player_PageLoc')","Enemy_BoundBoxCtrl=3 if kind==46 else 9,Enemy_X_Position=world&255,\n        Enemy_PageLoc=(world>>8)&255"),
        ("assert snapshot()==initial,('No health/tier/inventory outcome changes',identity,phase,calls)","assert snapshot()==initial,('No health/tier/inventory outcome changes',identity,phase,calls,[(i,a,z)for i,(a,z)in enumerate(zip(initial,snapshot()))if a!=z])"),
        ("    print(json.dumps(dict(prepared=True","    if False:print(json.dumps(dict(prepared=True")]
    for a,b in pairs:assert text.count(a)==1,a;text=text.replace(a,b)
    return text


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-root',type=Path,required=True);a=ap.parse_args()
    out=a.output_root.resolve();assert out.is_relative_to(R/'build')and not out.exists(),'One fresh small metadata batch, no source/runtime cloning or evidence overwrite'
    assert sha(OLD)=='3be0314a1c8411abde5baa4fcc12de05b1f3305d72bb6d5e577efe35f95acc56'
    assert sha(FIXTURE)=='5efbd82610fcf84b3233fb78bb97f41243bbe421c251d65487999ae128f7a4fd'
    assert NEW.read_bytes()==FIXTURE.read_bytes(),'Completed pilot fixture and Vic coordinate correction remain byte exact'
    ns={'__file__':str(Path(__file__).resolve()),'__name__':'_remaining_shared_star_life'}
    exec(compile(change(OLD.read_text()),str(OLD),'exec'),ns);ns['resources']=resource_fields
    b=ns['scoped_load'](R/'build/mega_proto_body_palette_9ea.nes');hooks,_=ns['hooks_for'](b)
    sources={};negatives={};out.mkdir()
    for identity in WHITELIST:
        try:
            source=ns['campaign'](b,identity,1,hooks);sources[identity]=source
            print(json.dumps(dict(source_pass=True,native_run=False,identity=identity,full_GameLoop_calls=source['full_GameLoop_calls'])),flush=True)
        except Exception as e:
            negatives[identity]=dict(passed=False,native_run=False,error=repr(e),resource_fields=resource_fields(identity))
            print(json.dumps(dict(source_pass=False,native_run=False,identity=identity,error=repr(e))),flush=True)
    aggregate=out/'source-controls-aggregate.json';put(aggregate,dict(ROM_sha256=ns['EXPECTED'],native_run=False,whitelist=WHITELIST,source_pass=sources,source_negatives=negatives,
        scope='Fresh per-identity complete source campaigns. Health/private inventory fields use explicit owners. Original shared conservation remains strict; failures are retained without automatically treating legitimate earned rewards as product defects.'))
    original=ns['campaign']
    def completed_source(bundle,identity,mode,actual_hooks):
        assert bundle['raw']==b['raw']and actual_hooks==hooks and mode==1 and identity in sources
        return sources[identity]
    ns['campaign']=completed_source
    pilots=[R/'build/current-ab221-mario-hard-star-life-v1/prepared-not-run.json',R/'build/current-ab221-mac-hard-star-life-v1/prepared-not-run.json',R/'build/current-ab221-vic-hard-star-life-v2/prepared-not-run.json',R/'docs/qa/shared-star-life-currentab221e-native-2026-10-27.json']
    for name in ['current-ab221-mario-hard-star-life-v1','current-ab221-mac-hard-star-life-v1','current-ab221-vic-hard-star-life-v2']:
        pilots.append(R/'build'/name/'native/result.json')
    assert all(p.is_file()for p in pilots)
    readies=[]
    for identity in sources:
        child=out/identity;argv=sys.argv;sys.argv=[str(Path(__file__).resolve()),'--identity',identity,'--output',str(child)]
        try:ns['main']()
        finally:sys.argv=argv
        ready=child/'prepared-not-run.json';z=json.loads(ready.read_text())
        paths={Path(p['path'])for p in z['bindings']}|{OLD,FIXTURE,NEW,Path(__file__).resolve(),aggregate,*pilots}
        z.update(successor='Remaining-identity owner metadata; exact qualified shared fixture including Vic native-coordinate placement',original_pilot_native='Inherited only as observer-method provenance, not a new identity native result',native_run=False)
        z['bindings']=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)];put(ready,z)
        readies.append(dict(identity=identity,path=str(ready),sha256=sha(ready),bindings=len(z['bindings']),source_calls=sources[identity]['full_GameLoop_calls']))
    ns['campaign']=original
    result=out/'prepared-batch.json';put(result,dict(status='SOURCE_ONLY_PREPARED_NO_NATIVE',ROM_sha256=ns['EXPECTED'],native_run=False,readies=readies,source_negative_identities=list(negatives),
        aggregate=dict(path=str(aggregate),sha256=sha(aggregate)),caps_per_profile=dict(frames=3500,updates=1800,PNG=4,files=64,bytes=2000000000),
        no_source_runtime_ROM_copies=True,shared_fixture=dict(path=str(NEW),sha256=sha(NEW)),producer=dict(path=str(Path(__file__).resolve()),sha256=sha(__file__))))
    print(json.dumps(dict(batch=str(result),sha256=sha(result),source_pass=len(sources),source_negative=len(negatives),native_run=False)),flush=True)


if __name__=='__main__':main()
