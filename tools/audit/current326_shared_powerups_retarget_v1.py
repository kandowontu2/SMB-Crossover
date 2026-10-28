"""Additive current326 readies from frozen shared/ship inputs. Never launch native.

All mechanics/fixtures/caps remain literal. The only changed executable family
is classic LinkEasy; rerun its complete source component on the current ROM.
Other source controls remain openly inherited ee115 evidence, supported by the
exact15-byte layout and mode/character admission proof, not retagged campaigns.
"""
from pathlib import Path
from types import SimpleNamespace
import hashlib,inspect,json,sys

R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import current_ee115_shared_star_life_prepare_v1 as shared
import current_ee115_classic_tiers_prepare_v1 as classic

CURRENT='32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
PARENT='ee1152a49deae31e82d202159310fa3719cbcfd85de571fd1b9ac15a1cd2a7b3'
ROM=R/'build/zelda2_easy_glove.nes'
OUT=R/'build/current326-shared-powerups-v1'
OLD=R/'build/current-ee115-shared-powerups-prepared-handoff-v1.json'
OLD_SHA='3406b6f24eb0b8cda68b26abeec0a0d8bdb2ce40f4dfbc4ec7c58c42057c915d'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:dict(path=str(Path(p).resolve()),bytes=Path(p).stat().st_size,sha256=sha(p))
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n',newline='\n')


def check_binding(q):
    p=Path(q['path']);assert p.stat().st_size==q['bytes']and sha(p)==q['sha256'],p


def actual_config(b,cfg):
    checked=0
    for n,v in cfg['ram'].items():assert address(b,n)==v,('Actual RAM',n);checked+=1
    for n,h in cfg['hooks'].items():
        sym=h['source_symbol'];delta=h.get('source_delta',0);off=location(b,sym)+delta
        assert address(b,sym)+delta==h['pc']and(off-16)//8192 in h['banks'],('Actual hook location',n)
        assert list(b['raw'][off:off+len(h['bytes'])])==h['bytes'],('Actual hook bytes',n)
        for bank in h['banks']:
            start=16+bank*8192+(h['pc']&8191)
            assert list(b['raw'][start:start+len(h['bytes'])])==h['bytes'],('Actual permitted physical bank',n,bank)
        checked+=1
    for n,p in cfg['metatiles'].items():
        off=location(b,n);assert(p['bank'],p['offset'])==((off-16)//8192,(off-16)%8192)
        checked+=1
    expected=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2]
    assert cfg['smc']==expected and cfg['dma_store_return']==address(b,'PostDmaMaskEnable')
    return checked+6


def link_campaign(b):
    ns,_=shared.namespace();ns['EXPECTED']=CURRENT
    original=ns['actor']
    def actor(q,kind,slot,pickup,character):
        original(q,kind,slot,pickup,character)
        assert character==4 and kind==46 and pickup in [0,1]
        q.set('Enemy_Y_Position',q.get('Player_Y_Position')+8,slot)
    ns['actor']=actor
    env=dict(classic.__dict__);env['shared']=SimpleNamespace(EXPECTED=CURRENT)
    exec(compile(inspect.getsource(classic.campaign),str(Path(__file__)),'exec'),env)
    z=env['campaign'](b,ns,'link')
    assert z['passed']and z['ROM_sha256']==CURRENT
    z.update(actual_current_source_campaign=True,prior_corrected_actor_scope='Same Linkv2 legalY184 mature flower placement; all assertions/controllers unchanged.',
             current_helper_cost='The15B Glove repair adds22CPU per reached classicLinkEasy eligibility call; cadence remains a new native gate.')
    return z


def profile(b,oldready,out,kind,layout,fresh_link=None):
    assert not out.exists(),'Never overwrite earlier/native readies'
    old=json.loads(oldready.read_text());assert old['native_run']is False and old['ROM_sha256']==PARENT
    for q in old['bindings']:check_binding(q)
    parent=oldready.parent;cfg=json.loads((parent/'config.json').read_text());assert cfg['ROM_sha256']==PARENT
    fields=actual_config(b,cfg)
    newcfg=dict(cfg,ROM_sha256=CURRENT)
    assert {k:v for k,v in newcfg.items()if k!='ROM_sha256'}=={k:v for k,v in cfg.items()if k!='ROM_sha256'}
    out.mkdir();put(out/'config.json',newcfg)
    run=(parent/'run.lua').read_text();assert run.count(PARENT)==1
    changed=run.replace(PARENT,CURRENT);assert changed.replace(CURRENT,PARENT)==run
    (out/'run.lua').write_text(changed,newline='\n')
    command=json.loads((parent/'command.json').read_text());oldrom=None
    for item in command['argv']:
        if str(item).lower().endswith('.nes'):oldrom=Path(item)
    assert oldrom and sha(oldrom)==PARENT
    replacements={str(parent/'native'):str(out/'native'),str(parent/'run.lua'):str(out/'run.lua'),str(oldrom):str(ROM)}
    oldargs=list(command['argv']);command['argv']=[replacements.get(x,x)for x in oldargs]
    assert sum(x!=y for x,y in zip(oldargs,command['argv']))==3
    put(out/'command.json',command)
    oldsource=parent/'source-controls.json'
    if oldsource.is_file():sourceparent=bind(oldsource)
    else:sourceparent=None
    source=dict(passed=True,source_CPU_only=True,ROM_sha256=CURRENT,source_parent_ROM_sha256=PARENT,
        inherited_source_controls=sourceparent,actual_current_config_fields_checked=fields,
        current_layout=bind(layout),kind=kind,
        source_equivalence_scope='Only changed code is EasyWhipEligible::Link and its helper. Entry requires SelectedCharacter4 + Easy0. All HardStar/Life, Hard normalized rewards, Hard ships and other six classic identities reject before this changed branch. This is explicit source/layout inheritance, not a fresh full-campaign claim.',
        fresh_current_Link_campaign=fresh_link,
        native_run=False,guard_controller_scene_plan_caps_and_typed_preflight_byte_exact=True)
    if fresh_link:
        assert cfg['identity']=='link'and cfg['mode']==0
        oldsourcejson=json.loads(oldsource.read_text())
        for k in ['pickups','primary','full_GameLoop_calls']:
            assert fresh_link[k]==oldsourcejson[k],('Current Link mechanism',k)
        source['source_equivalence_scope']='Fresh actual current complete LinkEasy campaign, same corrected actor/controller and full growth/primary/cleanup assertions. Source cost changes disclosed; native PPU/cadence still unrun.'
    put(out/'source-controls.json',source)
    remap={str((parent/n).resolve()):out/n for n in ['config.json','run.lua','command.json','source-controls.json']}
    remap.update({str(oldrom.resolve()):ROM,str(oldrom.with_suffix('.dbg').resolve()):ROM.with_suffix('.dbg'),str(oldrom.with_suffix('.lbl').resolve()):ROM.with_suffix('.lbl')})
    paths={Path(remap.get(q['path'],q['path']))for q in old['bindings']}
    paths|={Path(__file__),oldready,parent/'config.json',parent/'run.lua',parent/'command.json',layout,OLD,ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),R/'build/zelda2_easy_glove_build.json'}
    if oldsource.is_file():paths.add(oldsource)
    paths|={out/n for n in ['config.json','run.lua','command.json','source-controls.json']}
    new=dict(old);new.update(ROM_sha256=CURRENT,native_run=False,passed=False,status='PREPARED_DO_NOT_RUN',current_retarget_only=True,
        parent_ready=bind(oldready),parent_source_ROM_sha256=PARENT,parent_results_not_retagged=True,
        unchanged_fixture_controller_caps_and_assertions=True,actual_current_config_fields_checked=fields,
        current_source_qualification=bind(out/'source-controls.json'),
        source_qualification_scope='Fresh LinkEasy full source component where changed; otherwise explicit unchanged-path source inheritance from ee115. No native outcome transferred.',
        bindings=[bind(p)for p in sorted(paths)])
    # Old status fields describing ee115 campaign completion stay contextual;
    # the current qualification receipt above states precisely what ran.
    put(out/'prepared-not-run.json',new)
    for q in new['bindings']:check_binding(q)
    return dict(kind=kind,identity=cfg.get('identity',['vic','octopus','twinbee','pentarou'][cfg.get('variant',0)]),
                mode=cfg['mode'],ready=bind(out/'prepared-not-run.json'),command=bind(out/'command.json'),bindings=len(new['bindings']),current_fields_checked=fields)


def main():
    assert sha(OLD)==OLD_SHA and sha(ROM)==CURRENT and not OUT.exists()
    b=scoped_load(ROM);oldrom=R/'build/roster-20261028-fixes.nes';a=oldrom.read_bytes();d=[i for i,(x,y)in enumerate(zip(a,b['raw']))if x!=y]
    site=location(b,'EasyWhipEligible::Link');tail=16+22*8192+0x1ff4
    assert len(d)==15 and set(d)==set(range(site,site+3))|set(range(tail,tail+12))
    assert b['raw'][site:site+3]==b'\x20\xf4\xbf'and a[tail:tail+12]==b'\xff'*12
    OUT.mkdir();layout=OUT/'current-layout.json'
    put(layout,dict(passed=True,source_only=True,parent_ROM_sha256=PARENT,current_ROM_sha256=CURRENT,changed_bytes=15,changed_bank=22,
        oldPCs_and_hook_RAM_fields_checked_perprofile=True,changed_admission=dict(character=4,mode=0,valid_variant0='Classic return behavior identical, +22CPU per admission',variant1='ZeldaII corrected exclusion'),
        inherited_source_not_retagged=True,header_CHR_NMI_IRQ_allotherbanks_exact=True))
    fresh=link_campaign(b);put(OUT/'fresh-current-link-source.json',fresh)
    recs=[]
    for q in json.loads(OLD.read_text())['profiles']:
        oldready=Path(q['ready']);assert sha(oldready)==q['ready_sha256']
        name=q['profile']
        kind='star-life'if'star-life'in name else'classic-tiers'if'classic'in name else'normalized-mushroom'
        recs.append(profile(b,oldready,OUT/(kind+'-'+q['identity']),kind,layout,fresh if kind=='classic-tiers'and q['identity']=='link'else None))
    for name in ['octopus','twinbee','pentarou']:
        oldready=R/f'build/current-ee115-{name}-hard-earned-v2/prepared-not-run.json'
        assert oldready.is_file(),'Use the qualified completed-case phasev2, never oldv1'
        recs.append(profile(b,oldready,OUT/('ship-'+name),'earned-ship',layout))
    assert len(recs)==39 and len([r for r in recs if r['kind']=='earned-ship'])==3
    handoff=OUT/'handoff.json'
    put(handoff,dict(status='CURRENT326_SOURCE_PREPARED_NATIVE_UNRUN',native_run=False,current_ROM_sha256=CURRENT,parent_ROM_sha256=PARENT,
        profiles=recs,shared_profiles=36,ship_profiles=3,total_bindings_verified=sum(q['bindings']for q in recs),
        current_layout=bind(layout),actual_current_Link_source=bind(OUT/'fresh-current-link-source.json'),
        native_runtime='ROOT owns all launches, unchanged private isolated worker/capture gate. No source/runtime/ROM copies or live human settings dependency.',
        prior_readies_and_results_unchanged=True,source_inheritance_explicit=True,
        owned_files=[bind(Path(__file__))],new_outputs='Only compact perprofile config/run/command/source-qualification/ready files and this one layout/currentLink receipt; old fixtures reused literally. No new fixture/framework/capture/native launch.'))
    print(json.dumps(dict(handoff=str(handoff),sha256=sha(handoff),profiles=len(recs),bindings=sum(q['bindings']for q in recs),fresh_Link_Main=fresh['full_GameLoop_calls'],native_run=False)))


if __name__=='__main__':main()
