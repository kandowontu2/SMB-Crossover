"""Mike-only contact/collector/erase chronology correction; never launches native."""
from pathlib import Path
import copy, difflib, inspect, json, re
from types import SimpleNamespace
from current326_shared_powerups_retarget_v1 import actual_config
import current_ee115_normalized_mushrooms_prepare_v1 as old
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU
from observe_chip_committed_write import lua

R=Path(__file__).resolve().parents[2]
ROM=R/'build/zelda2_easy_glove.nes'
EXPECTED='32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
PARENT=R/'build/current326-shared-powerups-v1/normalized-mushroom-mike'
OLD_FIXTURE=R/'tests/current-ee115-normalized-mushrooms-v2.lua'
FIXTURE=R/'tests/current326-normalized-mike-v3.lua'
OUT=R/'build/current326-normalized-mike-v3'
sha=old.sha;put=old.put

def metadata(b,name,delta=0,size=3):
    off=location(b,name)+delta
    return dict(pc=address(b,name)+delta,banks=[(off-16)//8192],bytes=list(b['raw'][off:off+size]),source_symbol=name,source_delta=delta)

def erase_site(b):
    at=location(b,'JnPickupDispatch');size=int(b['syms']['JnPickupDispatch']['size'],0)
    raw=b['raw'][at:at+size];target=address(b,'EraseEnemyObject');needle=bytes([0x20,target&255,target>>8])
    assert raw.count(needle)==1
    offset=raw.index(needle)+3
    assert raw[offset-5:offset+3]==bytes([0x8a,0x48])+needle+bytes([0x68,0xaa,0xa9])
    return offset

def source(b,after):
    ns,_=old.shared.namespace();instances=[];Arena=ns['Arena']
    def arena(*args):
        q=Arena(*args);instances.append(q);return q
    ns['Arena']=arena
    env=dict(old.__dict__);env['shared']=SimpleNamespace(EXPECTED=EXPECTED)
    exec(compile(inspect.getsource(old.campaign),str(Path(__file__))+'::unchanged_actual_campaign','exec'),env)
    names=['GameLoop','JnPickupDispatch','JnCollectPickup','EraseEnemyObject','MarioSourcePowerupCollision']
    at={(address(b,n),(location(b,n)-16)//8192):n for n in names}
    at[(address(b,'JnPickupDispatch')+after,(location(b,'JnPickupDispatch')-16)//8192)]='JnPickupDispatch::AfterActualErase'
    original=NesMPU.step;events=[];calls=0
    def step(c):
        nonlocal calls
        q=instances[-1];bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
        n=at.get((c.pc,bank))
        if n=='GameLoop':calls+=1
        elif n and c.x==5:
            events.append(dict(Main=calls,owner=n,PC=c.pc,bank=bank,X=c.x,SP=c.sp,
                live=q.get('Enemy_Flag',5),ID=q.get('Enemy_ID',5),state=q.get('Enemy_State',5),pickup=q.get('InvPickup',5),owner_id=q.get('InvPickupOwner',5),
                health=q.get('JnHealth'),maximum=q.get('JnMaxHearts'),status=q.get('PlayerStatus'),saved_X_on_stack=q.m[256+(c.sp+1)%256]))
        original(c)
    NesMPU.step=step
    try:campaign=env['campaign'](b,ns,'mike')
    finally:NesMPU.step=original
    names=[x['owner']for x in events]
    assert names==['JnPickupDispatch','JnCollectPickup','EraseEnemyObject','JnPickupDispatch::AfterActualErase'],events
    contact,collect,erase,returned=events
    assert contact['live']==collect['live']==erase['live']==1 and returned['live']==0
    assert contact['health']==collect['health']==6 and erase['health']==returned['health']==8
    assert contact['maximum']==collect['maximum']==3 and erase['maximum']==returned['maximum']==4
    assert returned['saved_X_on_stack']==5 and all(e['Main']==31 and e['pickup']==129 and e['owner_id']==16 for e in events)
    assert campaign['full_GameLoop_calls']==151 and campaign['passed']
    def physical(e):return e['X']==5 and e['live']!=0 and e['ID']==46 and e['state']>=128 and e['pickup']==129 and e['owner_id']==16
    negatives=[]
    for key,value in [('X',4),('live',0),('ID',6),('state',0),('pickup',130),('owner_id',12)]:
        bad=dict(contact);bad[key]=value;assert not physical(bad);negatives.append(dict(changed=key,value=value,rejected=True))
    assert physical(contact)
    return dict(passed=True,native_run=False,source_CPU_only=True,Lua_VM_executed=False,ROM_sha256=EXPECTED,GameLoop_calls=calls,
        unchanged_real_reward_campaign=campaign,ordered_actual_source_events=events,
        original_native_oracle_would_fail=dict(MarioSourcePowerupCollision_calls=0,original_requires_one=True,collector_expects_already_erased=False,original_requires_already_erased=True),
        negative_contact_controls=negatives,
        limits='Actual assembled complete GameLoop151 calls with original actor scene/raw0 Prepare and genuine reward grant; no PPU/NMI/Lua-VM or serialized native register reconstruction. Old native log proves observer assertion before benefit execution, not a game reward failure.')

def fixture():
    text=OLD_FIXTURE.read_text();changed=text
    substitutions=[
      ('local pickups,ownerCalls,rec=0,0,{}','local pickups,ownerCalls,erasures,rec=0,0,0,{}'),
      ("if entered and phase=='collect'then assert(pickups==1 and s['cpu.x']==5 and r('Enemy_Flag',5)==0,'Actual native erase -> genuine private collector');ownerCalls=ownerCalls+1 end",
       "if entered and phase=='collect'then assert(pickups==1 and s['cpu.x']==5 and r('Enemy_Flag',5)~=0,'Genuine Mike collector precedes native erase');ownerCalls=ownerCalls+1;event('genuine-pre-erase-collector',r('JnHealth'))end"),
      ("assert(ownerCalls==1 and r('Enemy_Flag',5)==0,'One physical normalized reward and actual owning collector');values(C.after)",
       "assert(ownerCalls==1 and erasures==1 and r('Enemy_Flag',5)==0,'One physical normalized reward, real collector and completed native erase');values(C.after)"),
      ('pickups=pickups,collector_calls=ownerCalls,record=rec','pickups=pickups,collector_calls=ownerCalls,native_erase_returns=erasures,record=rec')]
    for a,z in substitutions:assert changed.count(a)==1;changed=changed.replace(a,z)
    marker="hook('GameLoopFinish',function()"
    assert changed.count(marker)==1
    new="""hook('NativeEraseReturn',function(s)
 if not entered or phase~='collect'then return end
 assert(pickups==1 and ownerCalls==1 and s['cpu.x']==5 and r('Enemy_Flag',5)==0,'Genuine Mike successful collector then actual EraseEnemyObject return')
 assert(emu.read(256+(s['cpu.sp']+1)%256,emu.memType.nesDebug)==5,'Actual pending saved pickupX at native PLA')
 erasures=erasures+1;rec.erase_update=updates;event('actual-native-erase-return',r('JnHealth'))
end)
"""
    changed=changed.replace(marker,new+marker)
    a='-- All callback registration is startup-static.'
    z='emu.addEventCallback(function()if not entered then emu.setInput(menu(),0)else emu.setInput(input(),0)end end,emu.eventType.inputPolled)'
    assert changed[changed.index(a):changed.index(z)+len(z)]==text[text.index(a):text.index(z)+len(z)]
    assert changed.count('emu.write(')==2 and 'removeMemoryCallback'not in changed
    assert re.search(r'local function input\(\).*?end\n',changed).group()==re.search(r'local function input\(\).*?end\n',text).group()
    # The complete old scene/input/menu and all before/after/final predicates
    # remain literal; only the owning contact/collector/erase observations move.
    if FIXTURE.exists():assert FIXTURE.read_text()==changed
    else:FIXTURE.write_text(changed,newline='\n')
    return text,changed

def main():
    ready=PARENT/'prepared-not-run.json'
    assert sha(ready)=='f493d97ae24a56fdf95ab7a4b5da427a796fdeac12031483b8c6436549e27134'
    prior=json.loads(ready.read_text())
    for e in prior['bindings']:assert sha(e['path'])==e['sha256']
    assert sha(ROM)==EXPECTED and not OUT.exists()
    launch=json.loads((PARENT/'launch.json').read_text())
    assert launch['exit_code']==1 and launch['changed_inputs']==[] and launch['settings_before']==launch['settings_after']
    log=PARENT/'native/zelda2_easy_glove-run.log';csv=PARENT/'native/normalized-mushroom.csv'
    assert 'FAIL Actual native erase -> genuine private collector'in log.read_text()
    assert not (PARENT/'native/result.json').exists() and 'physical-normalized-pickup'not in csv.read_text()
    b=scoped_load(ROM);after=erase_site(b);proof=source(b,after)
    before,changed=fixture();cfg=json.loads((PARENT/'config.json').read_text());newcfg=copy.deepcopy(cfg)
    newcfg['hooks']['PhysicalPickup']=metadata(b,'JnPickupDispatch')
    newcfg['hooks']['NativeEraseReturn']=metadata(b,'JnPickupDispatch',after)
    fields=actual_config(b,newcfg)
    for key in cfg:
        if key!='hooks':assert cfg[key]==newcfg[key]
    assert all(newcfg['hooks'][k]==v for k,v in cfg['hooks'].items()if k!='PhysicalPickup')
    OUT.mkdir();put(OUT/'config.json',newcfg);put(OUT/'source-controls.json',proof)
    patch=OUT/'observer-only.patch';patch.write_text(''.join(difflib.unified_diff(before.splitlines(True),changed.splitlines(True),fromfile=str(OLD_FIXTURE),tofile=str(FIXTURE))),newline='\n')
    generated=(PARENT/'run.lua').read_text();start=generated.index('\n');suffix=generated[start:]
    assert suffix.count(OLD_FIXTURE.as_posix())==1
    suffix=suffix.replace(OLD_FIXTURE.as_posix(),FIXTURE.as_posix())
    (OUT/'run.lua').write_text('CURRENT_NORMALIZED_MUSHROOM='+lua(newcfg)+suffix,newline='\n')
    command=json.loads((PARENT/'command.json').read_text());oldargs=command['argv'];newargs=[str(OUT/'native')if x==str(PARENT/'native')else str(OUT/'run.lua')if x==str(PARENT/'run.lua')else x for x in oldargs]
    assert sum(a!=b for a,b in zip(oldargs,newargs))==2;command['argv']=newargs;put(OUT/'command.json',command)
    paths={Path(e['path'])for e in prior['bindings']}|{Path(__file__),FIXTURE,OLD_FIXTURE,ready,PARENT/'launch.json',log,csv,R/'src/mike_jones_dispatch.s',R/'src/mike_jones_pickups.s',R/'src/collision.s',R/'src/mario_source.s',R/'tools/audit/current326_shared_powerups_retarget_v1.py'}
    paths|={OUT/n for n in ['config.json','run.lua','command.json','source-controls.json','observer-only.patch']}
    rec=dict(prior);rec.update(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,source_calls=151,
        original_native_FALSE=dict(path=str(PARENT),ready_sha256=sha(ready),exit_code=1,no_native_result=True,reason='Observer assumes legacy erase-before-collector. Actual Mike private collector runs before erase and bypasses MarioSourcePowerupCollision.'),
        source_qualification_scope='Fresh actual326 complete151Main original earned reward campaign plus real owner/stack/erase order; no native outcome inferred.',
        correction='Mike-only PhysicalPickup now genuine JnPickupDispatch entry; CollectOwner checks still-live private actor, NativeEraseReturn observes actual post-JSR EraseEnemyObject/pre-PLA with savedX5. Existing postcollection exact benefit and all hardware/scene/input/cap predicates unchanged; one extra erase count required.',
        changed_config_hooks=['PhysicalPickup','NativeEraseReturn'],all_other_config_equal=True,actual_current_config_fields_checked=fields,
        current_source_qualification=dict(path=str(OUT/'source-controls.json'),sha256=sha(OUT/'source-controls.json')),
        bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)])
    put(OUT/'prepared-not-run.json',rec)
    assert all(sha(e['path'])==e['sha256']for e in rec['bindings'])
    print(json.dumps(dict(prepared=True,native_run=False,ready=str(OUT/'prepared-not-run.json'),sha256=sha(OUT/'prepared-not-run.json'),bindings=len(rec['bindings']),source_calls=151,actual_order=proof['ordered_actual_source_events'],command=str(OUT/'command.json'),owned_new_files=[str(Path(__file__)),str(FIXTURE)])))

if __name__=='__main__':main()
