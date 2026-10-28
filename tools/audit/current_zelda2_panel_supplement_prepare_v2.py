"""Correct only logical-vs-physical world lease restoration after the earned panels."""
from pathlib import Path
import hashlib,json
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from current_roster_compact_11_v1 import lua

R=Path(__file__).resolve().parents[2];B=R/'build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:dict(path=str(Path(p).resolve()),bytes=Path(p).stat().st_size,sha256=sha(p))
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n',newline='\n')
OLD="repeat tick(0)until wall>=n+5 and physical[11]==r('Z2PanelChr')and mask&24~=0 and r('ReloadCHRBank')==0"
NEW="repeat tick(0)until wall>=n+5 and worldLease and physical[11]==worldLease.physical11 and r('CurrentCHRBank',11)==worldLease.source11 and r('X5ChrMode',11)==worldLease.mode11 and r('Z2PanelChr')==worldLease.source11 and r('Z2PanelMode')==worldLease.mode11 and mask&24~=0 and r('ReloadCHRBank')==0 and lastEnable and lastEnable.NMI and lastEnable.physical11==worldLease.physical11"
HOOK="""local worldLease,observedWorldLeases=nil,{}
emu.addMemoryCallback(function(_,v)
 if entered and nmi and v&24~=0 and r('Z2PanelActive')==0 and r('Z2PanelPending')==0 and r('ReloadCHRBank')==0 then
  assert(physical[11]==emu.getState()['mapper.chrBanks11'],'Actual published world font')
  local source,mode=r('CurrentCHRBank',11),r('X5ChrMode',11);local owner=stamp();owner.mask=v
  observedWorldLeases[source..':'..mode]={source11=source,mode11=mode,physical11=physical[11],owner=owner}
 end
end,emu.callbackType.write,0x2001)
hook('PanelOpenComplete',function()
 if not entered then return end
 assert(not nmi and not irq and r('NmiDisable')==255 and r('Z2PanelActive')==1 and r('Z2PanelPending')==1 and mask&24==0,'Actual exclusive panel-open owner')
 assert(r('CurrentCHRBank',11)==r('Z2PanelChr')and r('X5ChrMode',11)==r('Z2PanelMode'),'Genuine panel backup matches current source/mode')
 local source,mode=r('Z2PanelChr'),r('Z2PanelMode');local prior=observedWorldLeases[source..':'..mode]
 assert(prior and prior.owner.NMI,'Matching source/mode had an actual visible NMI world-font lease')
 worldLease={source11=source,mode11=mode,physical11=prior.physical11,previousVisible=prior.owner,openOwner=stamp()};note('actual-pre-panel-world-lease')
end)
"""

def main():
    parent=B/'current-z2glove-zelda2-panel-supplement-v1';rp=parent/'prepared-not-run.json';old=json.loads(rp.read_text());assert all(sha(q['path'])==q['sha256']for q in old['bindings'])
    negative=B/'zelda2_panel_supplement_v1_negative.json';n=json.loads(negative.read_text());assert not n['original_native_passed']and n['first_failing_phase']=='completed-world-restore';assert all(sha(q['path'])==q['sha256']for q in n['bindings'])
    launch=json.loads((parent/'launch.json').read_text());assert launch['exit_code']==1 and not launch['changed_inputs']and launch['settings_before']==launch['settings_after']
    fixture=R/'tools/audit/current_zelda2_panel_supplement_v1.lua';text=fixture.read_text();assert text.count(OLD)==1;text=text.replace(OLD,NEW)
    marker="hook('PanelUnblankReturn',function()note('panel-publication-RTS-entry')end)";assert text.count(marker)==1;text=text.replace(marker,HOOK+marker)
    tail="request_image('03-after-paid-level-world');tick(0);record(taskName,snap());desired=0;done=true";newtail="request_image('03-after-paid-level-world');tick(0);record(taskName,snap(),{worldLease=worldLease,restoredHardware=stamp()});desired=0;done=true";assert text.count(tail)==1;text=text.replace(tail,newtail)
    reverse=text.replace(newtail,tail).replace(HOOK+marker,marker).replace(NEW,OLD);assert reverse==fixture.read_text()
    newfixture=R/'tools/audit/current_zelda2_panel_supplement_v2.lua';assert not newfixture.exists();newfixture.write_text(text,newline='\n')
    rom=B/'zelda2_easy_glove.nes';b=scoped_load(rom);assert sha(rom)==old['ROM_sha256'];assert b['raw'][location(b,'ChrPhysicalMap')+7]==3
    mapping=[]
    for mode,source,want in [(0,7,3),(129,139,395)]:
        q=Arena(b,4);q.put(Z2Variant=1,X5WideChrActive=1);q.set('X5ChrMode',mode,11);q.set('CurrentCHRBank',source,11);q.invoke('X5PublishChr')
        upper=0;actual=None;ordered=[]
        for at,v in q.m.writes:
            if at==0x5130:upper=v&3
            if at==0x512b:actual=v+256*upper
            if at in [0x5130,0x512b]:ordered.append([at,v])
        assert actual==want;mapping.append(dict(source=source,mode=mode,actual_physical11=actual,ordered_final_publication=ordered))
    # Typed mirror of the new readonly predicate; not a Lua/native execution.
    good=dict(lease=True,physical=3,source=7,mode=0,savedsource=7,savedmode=0,mask=30,reload=0,NMI=True,enablephysical=3)
    def accepts(z):return z['lease']and z['physical']==3 and z['source']==7 and z['mode']==0 and z['savedsource']==7 and z['savedmode']==0 and z['mask']&24!=0 and z['reload']==0 and z['NMI']and z['enablephysical']==3
    assert accepts(good);controls=[]
    for field,value in [('lease',False),('physical',7),('physical',395),('source',139),('mode',129),('savedsource',139),('savedmode',129),('mask',0),('reload',1),('NMI',False),('enablephysical',395)]:
        z=dict(good);z[field]=value;assert not accepts(z);controls.append(dict(field=field,value=value,rejected=True))
    out=B/'current-z2glove-zelda2-panel-supplement-v2';assert not out.exists();out.mkdir()
    cfg=json.loads((parent/'config.json').read_text());cfg['ram']['Z2PanelMode']=address(b,'Z2PanelMode');assert cfg['ram']['Z2PanelMode']==0x5d86
    cfg['scope']+=' V2 observer-only: final restore uses actual pre-panel physical lease plus exact saved logical/mode source, actual last NMI enable and five-wall delay; same bounds, panel display/font/pixel requirements and original acquired mechanics.'
    put(out/'config.json',cfg);(out/'run.lua').write_text('CURRENT_ZELDA2_EARNED='+lua(cfg)+'\ndofile([=['+newfixture.as_posix()+']=])\n',newline='\n')
    cmd=json.loads((parent/'command.json').read_text());cmd['argv']=[str(out/'native')if v==str(parent/'native')else str(out/'run.lua')if v==str(parent/'run.lua')else v for v in cmd['argv']];put(out/'command.json',cmd)
    source=out/'source-controls.json';put(source,dict(passed=True,native_run=False,Lua_VM_executed=False,ROM_sha256=sha(rom),original_false=bind(negative),source_campaign_reused_unchanged=bind(parent/'source-controls.json'),full_mechanics_controller_seed_guard_caps_reverse_exact=True,actual_assembled_X5PublishChr_cases=mapping,typed_observer_negatives=controls,new_compiled_alias=dict(name='Z2PanelMode',address=cfg['ram']['Z2PanelMode']),strict_font395_three_epoch_pixel_contract_unchanged=True,substitutions=[dict(old=OLD,new=NEW),dict(insert_before=marker,readonly_hook=HOOK),dict(old=tail,new=newtail)]))
    paths={Path(q['path'])for q in old['bindings']if Path(q['path'])not in{fixture,parent/'config.json',parent/'run.lua',parent/'command.json',parent/'source-controls.json'}}
    paths|={Path(__file__),newfixture,fixture,rp,negative,source,*[out/v for v in ['config.json','run.lua','command.json']]}
    z=dict(old);z.update(scope=cfg['scope'],parent_ready_sha256=sha(rp),original_native_FALSE_preserved=True,observer_only_physical_lease_correction=True,bindings=[bind(p)for p in sorted(paths)])
    ready=out/'prepared-not-run.json';put(ready,z);assert all(sha(q['path'])==q['sha256']for q in z['bindings'])
    print(json.dumps(dict(ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),command=str(out/'command.json'))))

if __name__=='__main__':main()
