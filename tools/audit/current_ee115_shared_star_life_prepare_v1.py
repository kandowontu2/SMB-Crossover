"""Fresh finite missing Star/1-Up cells; existing real-source campaigns/guards.

Preparation only. No native launch, ROM/runtime/source copies, or old receipt
retagging. The three CV3 variants need Star only; their life cells already have
native evidence. All other missing identities exercise Star then physical1Up.
"""
from pathlib import Path
import argparse, hashlib, json, re, sys, time

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import current_shared_star_life_remaining_prepare_v3 as prior
import current_shared_star_life_reward_prepare_v4 as original_source
from current_shared_star_reward_model_v4 import Model,metadata,IDENTITIES as REWARD_IDS
from observe_chip_committed_write import lua

EXPECTED='ee1152a49deae31e82d202159310fa3719cbcfd85de571fd1b9ac15a1cd2a7b3'
MATRIX=R/'docs/qa/all37-powerup-native-coverage-2026-10-28.json'
MATRIX_SHA='41168d1c642f9561e55e3d4ed17cc50b8acd14ff2a8d0ca6d1f420979a09f113'
FIXTURE=R/'tests/current-ee115-shared-star-life-v1.lua'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')


def fixture():
    old=R/'tests/current-shared-star-life-rewards-v4.lua'
    text=old.read_text()
    a="expiryAt=updates;screenshot='03-star-expired.png';phase='life-setup';age=0;event('natural-star-expiry')"
    z="expiryAt=updates;screenshot='03-star-expired.png';phase=C.need_life and'life-setup'or'complete';done=not C.need_life;age=0;event('natural-star-expiry')"
    assert text.count(a)==1
    text=text.replace(a,z)
    # Exact reward helper is inert for owners with no resource-changing drops.
    text=text.replace("local rewardCfg=assert(C.rewards)","local rewardCfg=C.rewards or{order={},targets={}}")
    assert text.count('emu.write(')==2 and 'removeMemoryCallback'not in text
    if FIXTURE.exists():assert FIXTURE.read_text()==text,'Never revise a prepared fixture'
    else:FIXTURE.write_text(text,newline='\n')
    guard_start='-- All callback registration is startup-static.'
    guard_end='emu.addEventCallback(function()\n if not entered'
    base=(R/'tests/current-shared-star-life-vic-v2.lua').read_text()
    assert text[text.index(guard_start):text.index(guard_end)]==base[base.index(guard_start):base.index(guard_end)]
    return old


def namespace():
    ns=original_source.compiled()
    ns['EXPECTED']=EXPECTED
    class Empty:
        def start(self,a):pass
        def event(self,*a):pass
        def write(self,*a):pass
        def finish(self):return dict(credits=[],provenance_events=[],resource_awards=0,physical_collections=0)
    cfgs={}
    def make(b,identity,q):
        if identity not in REWARD_IDS:return Empty()
        _,char,_,variant=ns['BASE'][identity]
        cfg=metadata(b,identity,prior.resource_fields(identity),char,variant)
        strings=set(re.findall(r"['\"]([A-Za-z_][A-Za-z_0-9]*)['\"]",(R/'tools/audit/current_shared_star_reward_model_v4.py').read_text()))
        names=(strings&set(b['syms']))|{p['name']for p in prior.resource_fields(identity)}
        cfgs[identity]=cfg
        return Model(cfg,{n:ns['address'](b,n)for n in names},q.get)
    ns['reward_make']=make
    return ns,cfgs


def prepare(b,ns,cfgs,identity,out,source,original_fixture):
    assert not out.exists(),'Never replace bound readies/native observations'
    out.mkdir(parents=True)
    hooks,extra=ns['hooks_for'](b)
    reward=cfgs.get(identity)
    if reward:hooks=dict(hooks,**reward['hooks'])
    menu,char,vname,variant=ns['BASE'][identity]
    text=FIXTURE.read_text();fields=prior.resource_fields(identity)
    names=set(ns['ALLOWED'])|set(ns['BANS'])|set(ns['MOTION'])|{p['name']for p in fields}
    names|=set(re.findall(r"['\"]([A-Za-z_][A-Za-z_0-9]*)['\"]",text))&set(b['syms'])
    names|=set(re.findall(r'\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))
    if vname:names.add(vname)
    ram={n:ns['address'](b,n)for n in names}
    for n in re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",text):assert n in ram,n
    scope='Fresh current-ROM native preparation: mature Star2 actual collection, protected Goomba contact/defeat, natural expiry/music restoration; '+('physical1Up3 and delayed actual life increment/popup cleanup, inventory conservation.'if identity not in ['grant','sypha','alucard']else'Star only: prior native life evidence is separate and not retagged.')
    cfg=dict(ROM_sha256=EXPECTED,identity=identity,character=char,menu=menu,variant_name=vname,variant=variant,mode=1,
             hooks=hooks,ram=ram,navigation=ns['navigation'](b['raw'],lambda n:ns['location'](b,n),menu),resources=fields,
             rewards=reward,need_life=identity not in ['grant','sypha','alucard'],motion=ns['MOTION'],
             setup_allowed={n:True for n in ns['ALLOWED']},resource_bans={n:True for n in ns['BANS']},
             star_music=64,extra_life_sfx=extra,scope=scope,dma_store_return=ns['address'](b,'PostDmaMaskEnable'),
             smc=[ns['address'](b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[ns['address'](b,'FarcallJmpTarget_SMC')+2],
             metatiles={n:dict(bank=(ns['location'](b,n)-16)//8192,offset=(ns['location'](b,n)-16)%8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']})
    put(out/'config.json',cfg);put(out/'source-controls.json',source)
    preflight="local C=CURRENT_SHARED_STAR_LIFE;assert(type(C.mode)=='number'and C.mode==1 and type(C.resources)=='table'and type(C.resources[1])=='table');for _,p in ipairs(C.resources)do assert(type(C.ram[p.name])=='number'and type(p.index)=='number'and type(p.count)=='number')end\n"
    (out/'run.lua').write_text('CURRENT_SHARED_STAR_LIFE='+lua(cfg)+'\n'+preflight+'dofile([=['+FIXTURE.as_posix()+']=])\n',newline='\n')
    rom=Path(b['path']) if 'path'in b else R/'build/roster-20261028-fixes.nes'
    argv=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out/'native'),str(out/'run.lua'),str(rom),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
    paths={Path(__file__),FIXTURE,original_fixture,prior.OLD,Path(prior.__file__),Path(original_source.__file__),
           R/'tools/audit/current_shared_star_reward_model_v4.py',R/'tools/audit/current_shared_star_rewards_v4.lua',
           R/'tools/audit/run_mesen_isolated.py',R/'tools/run_mesen.py',R/'tools/audit/capture_budget.py',
           R/'tools/audit/current_roster_compact_11_v1.py',R/'tools/audit/observe_chip_committed_write.py',
           MATRIX,rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl')}
    paths|={out/n for n in ['config.json','source-controls.json','run.lua','command.json']}
    for n in ['collision.s','mario_source.s','game.s','common.s','reset.s','inventory.s','inventory_data.inc','inventory_drops.s','cv3.s','cv3_items.s','remaining_weapons.s','x5_mario3.s']:
        p=R/'src'/n
        if p.is_file():paths.add(p)
    put(out/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,ROM_sha256=EXPECTED,
        identity=identity,mode=1,source_calls=source['full_GameLoop_calls'],need_star=True,need_life=cfg['need_life'],scope=scope,
        source_only='Fresh complete GameLoop campaign on actual current ROM; not native menu/audio/render evidence.',
        setup='Only legal map/actor/position/motion at genuine GameLoop+5 NmiDisableFF with no NMI/IRQ; no acquired resources, Star, lives, health, damage or outcome writes.',
        guard_literal_exact=True,caps=dict(wall_frames=3500,updates=1800,host_seconds=1200,files=64,bytes=2000000000,PNGs=4),
        runtime='ROOT approved isolated worker required; live human GUI settings are not a functional input. No new runtime/settings tree.',
        gaps='Mature actor component only; natural reveal/rise/drop randomness, audio waveform, every frame/pixel, life rollover/death reacquisition and Easy differences remain separate.',
        bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)]))
    return dict(identity=identity,path=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),source_calls=source['full_GameLoop_calls'],command=str(out/'command.json'),native_run=False)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--identity',action='append',help='Subset pilot, otherwise all27 frozen-matrix missing Star cells')
    ap.add_argument('--output',type=Path,default=R/'build/current-ee115-shared-star-life-v1')
    a=ap.parse_args();assert sha(MATRIX)==MATRIX_SHA
    matrix=json.loads(MATRIX.read_text());missing=matrix['actionable_remaining']['shared_missing_native_collection']['PowerUpType2']
    identities=a.identity or missing
    assert len(missing)==27 and set(identities)<=set(missing)
    rom=R/'build/roster-20261028-fixes.nes';assert sha(rom)==EXPECTED
    old=fixture();ns,cfgs=namespace();b=ns['scoped_load'](rom);hooks,_=ns['hooks_for'](b)
    a.output.mkdir(parents=True,exist_ok=True);readies=[];held={}
    for identity in identities:
        if(a.output/identity).exists():raise AssertionError(('Existing profile',identity))
        start=time.monotonic()
        try:
            source=ns['campaign'](b,identity,1,hooks)
            source.update(ROM_sha256=EXPECTED,fresh_current_campaign=True)
            rec=prepare(b,ns,cfgs,identity,a.output/identity,source,old);readies.append(rec)
            print(json.dumps(dict(identity=identity,source_pass=True,seconds=round(time.monotonic()-start,2),**{k:v for k,v in rec.items()if k!='identity'})),flush=True)
        except Exception as e:
            held[identity]=dict(native_run=False,source_pass=False,error=repr(e))
            put(a.output/(identity+'-source-negative.json'),dict(held[identity],ROM_sha256=EXPECTED))
            print(json.dumps(dict(identity=identity,**held[identity])),flush=True)
    batch=a.output/('prepared-batch-'+('-'.join(identities)if a.identity else'all27')+'.json')
    assert not batch.exists()
    put(batch,dict(status='SOURCE_PREPARED_NOT_NATIVE',ROM_sha256=EXPECTED,matrix_snapshot_sha256=MATRIX_SHA,readies=readies,held=held,
                   no_native_launch=True,no_old_receipt_retag=True,no_game_source_changes=True))
    print(json.dumps(dict(batch=str(batch),sha256=sha(batch),prepared=len(readies),held=len(held),native_run=False)))


if __name__=='__main__':main()
