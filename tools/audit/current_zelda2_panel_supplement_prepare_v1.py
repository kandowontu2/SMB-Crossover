"""Earn C0/50EXP, hold real panel display epochs and prepare three delayed PNGs."""
from pathlib import Path
import hashlib,inspect,json,re,sys
import current_zelda2_earned_cpu_v1 as source
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from current_roster_compact_11_v1 import lua

R=Path(__file__).resolve().parents[2];B=R/'build';ROM=B/'zelda2_easy_glove.nes';EXPECTED='32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:dict(path=str(Path(p).resolve()),bytes=Path(p).stat().st_size,sha256=sha(p))
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n',newline='\n')

PASSIVE=r'''
local journal=assert(io.open(OUTPUT..'panel-display-events.jsonl','w'))
local journalRows,journalBytes=0,0
local panelRequest,frameStart,lastEnable,displayPictures=nil,nil,nil,{}
local function stamp()
 local s=emu.getState();return{wall=wall,update=updates,frame=s['ppu.frameCount'],line=s['ppu.scanline'],dot=s['ppu.cycle'],cpu=s['cpu.cycleCount'],pc=s['cpu.pc'],bank=bank(s['cpu.pc']),NMI=not not nmi,mask=mask,mirror=r('Mirror_PPUMASK'),disable=r('DisableScreenFlag'),pending=r('Z2PanelPending'),active=r('Z2PanelActive'),page=r('Z2PanelPage'),cursor=r('Z2PanelCursor'),origin=r('Z2PanelOrigin'),reload=r('ReloadCHRBank'),physical11=physical[11],source11=r('CurrentCHRBank',11),mode11=r('X5ChrMode',11),DMAs=dmas}
end
local function note(kind,value)
 if not entered then return end
 local row=stamp();row.kind=kind;if value~=nil then row.write_value=value;if kind=='mask-off'or kind=='mask-enable'then row.mask=value end;if kind=='actual-512B-write'then row.new_physical11=value+256*upper end end;local s=json(row)..'\n';journalRows=journalRows+1;journalBytes=journalBytes+#s
 assert(journalRows<=2400 and journalBytes<=1048576,'Finite panel observability journal');journal:write(s)
end
local function cells()
 local out={};local origin=r('Z2PanelOrigin')
 for row=0,13 do for col=0,13 do local x=(origin+col)&63;local at=0x2000+(x//32)*1024+(row+8)*32+x%32;out[#out+1]=emu.read(at,emu.memType.nesPpuDebug)end end
 return out
end
local function same(a,b)if not(a and b)or #a~=#b then return false end;for i,v in ipairs(a)do if b[i]~=v then return false end end;return true end
local function stateReady(a)
 if r('GamePauseStatus')&1==0 or r('Z2PanelActive')~=1 or r('Z2PanelPending')~=0 or r('Z2PanelPage')~=a.page or r('Z2PanelOrigin')~=9 or r('DisableScreenFlag')~=0 or r('Mirror_PPUMASK')&24==0 or physical[11]~=395 then return false end
 return same(cells(),a.expected)
end
local function awaitPicture(page,name)
 assert(not panelRequest and not displayPictures[name],'One real panel picture request')
 panelRequest={page=page,name=name,expected=C.panel_expected[tostring(page)],requested=stamp(),epochs={}}
 for _=1,150 do if displayPictures[name]then return end;tick(0)end
 note('picture-timeout');assert(false,'No completed physical panel display '..name)
end
hook('PanelUnblankReturn',function()note('panel-publication-RTS-entry')end)
hook('NmiReturn',function()if entered and(panelRequest or r('Z2PanelActive')~=0 or r('Z2PanelPending')~=0)then note('NMI-RTI-entry')end end)
emu.addMemoryCallback(function(_,v)
 if entered then
  if panelRequest or r('Z2PanelActive')~=0 or r('Z2PanelPending')~=0 then note(v&24==0 and'mask-off'or'mask-enable',v)end
  if v&24~=0 then lastEnable=stamp();lastEnable.mask=v end
 end
end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function(_,v)if entered and(panelRequest or r('Z2PanelActive')~=0 or r('Z2PanelPending')~=0)then note('actual-512B-write',v)end end,emu.callbackType.write,0x512b)
emu.addEventCallback(function()
 if panelRequest and stateReady(panelRequest)then frameStart={state=stamp(),tiles=cells()}else frameStart=nil end
end,emu.eventType.startFrame)
emu.addEventCallback(function()
 local a=panelRequest
 if not a then return end
 if frameStart and stateReady(a)and same(frameStart.tiles,a.expected)and lastEnable and lastEnable.physical11==395 and lastEnable.pending==0 and lastEnable.page==a.page and lastEnable.active==1 and lastEnable.mask&24~=0 then
  local now=stamp();a.epochs[#a.epochs+1]={start=frameStart.state,finish=now,enable=lastEnable}
  -- takeScreenshot can expose the prior complete image. Require THREE
  -- qualified start/end epochs with the same source-derived whole panel.
  if #a.epochs>=3 and now.frame>a.epochs[1].finish.frame+1 then
   assert(images<8,'At most8 selected actual images');local f=assert(io.open(OUTPUT..a.name,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1
   a.capture=now;a.actual_tiles=cells();a.palette={};for i=0,31 do a.palette[i+1]=emu.read(0x3f00+i,emu.memType.nesPpuDebug)end
   a.CHR={};for i=0,11 do a.CHR[i+1]=physical[i]end;a.hardware_OAM={};for i=0,255 do a.hardware_OAM[i+1]=emu.read(i,emu.memType.nesSpriteRam)end
   assert(a.palette[6]==0x30 and a.palette[8]==0x0f,'Actual source panel white/black palette ownership')
   displayPictures[a.name]=a;screenshots[a.name]=a;note('completed-panel-picture');panelRequest=nil
  end
 else a.epochs={}end
end,emu.eventType.endFrame)
'''

CAMPAIGN=r'''local function campaign()
 begin('cold-settle');for _=1,30 do tick()end
 assert(r('Z2Hp')==127 and r('Z2Mp')==127 and r('Z2Containers')==51 and r('Z2LearnedSpells')==0,'Genuine initial Z2 record')
 injury(16);begin('physical-raw0-C0');scene();actor(46,112,184,5);local before=snap();local collect=counts.Collect or 0
 transaction(function()for n,v in pairs(C.rewards[1].prepared)do w(n,v,5)end end)
 wait(function()return r('Enemy_Flag',5)==0 and r('Z2HpPending')==0 end,160)
 assert((counts.Collect or 0)==collect+1 and r('Z2LearnedSpells')==2 and r('Z2Hp')==127,'Actual raw0 C0 and real mushroom healing');record(taskName,before)
 begin('physical-earned-spell-page');open_panel();if r('Z2UiState')&1~=0 then edge(1)end
 wait(function()return r('Z2PanelPage')==0 and r('Z2PanelPending')==0 end,60)
 awaitPicture(0,'01-earned-spells-visible.png')
 edge(128);wait(function()return r('GamePauseStatus')&1==0 and r('Z2PanelActive')==0 and r('Z2PanelPending')==0 end,60)
 assert(r('Z2Mp')==127 and(counts.Cast or 0)==0,'Panel navigation never casts or seeds MP')
 drop(0x8a);assert(exp()==50,'Real mature EXP bag earned the first level')
 begin('physical-earned-level-page');wait(function()return r('GamePauseStatus')&1~=0 and r('Z2PanelActive')==1 and r('Z2PanelPending')==0 and r('Z2PanelPage')==1 end,80)
 assert(r('Z2UiCursor')==2 and r('Z2Hp')==127,'Real Life purchase category after earned mushroom healing')
 awaitPicture(1,'02-earned-level-visible.png')
 level(2);wait(function()return r('GamePauseStatus')&1==0 and r('Z2PanelActive')==0 and r('Z2PanelPending')==0 end,80)
 assert(exp()==0 and r('Z2LevelsLo')==64 and r('Z2LevelsHi')==128 and r('Z2Hp')==127 and(counts.Level or 0)==1,'Actual50EXP Life upgrade and genuine full restoration')
 drop(0x8b);assert(exp()==100,'Actual physical100EXP bag');level(1)
 wait(function()return r('GamePauseStatus')&1==0 and r('Z2PanelPending')==0 end,80)
 assert(exp()==0 and r('Z2LevelsLo')==72,'Actual100EXP Magic purchase')
 drop(0x8d);assert(exp()==500,'Actual physical500EXP bag');level(0)
 -- Native B defers the next affordable Life, then Magic option. The
 -- unspent300 EXP remains real; no deferred-mask or EXP write is allowed.
 for _=1,10 do
  tick(0)
  if r('GamePauseStatus')&1~=0 then
   wait(function()return r('Z2PanelActive')==1 and r('Z2PanelPending')==0 end,80);edge(64)
  end
 end
 wait(function()return r('GamePauseStatus')&1==0 and r('Z2PanelActive')==0 and r('Z2PanelPending')==0 end,80)
 assert(exp()==300 and r('Z2LevelsLo')==73 and(counts.Level or 0)==3,'Actual500EXP Attack purchase, exact retained300 and three genuine paid upgrades')
 begin('completed-world-restore');local n=wall
 repeat tick(0)until wall>=n+5 and physical[11]==r('Z2PanelChr')and mask&24~=0 and r('ReloadCHRBank')==0
 local old=C.panel_expected_backup;local actual=cells();for i=1,196 do assert(actual[i]==r('Z2PanelTiles',i-1),'Exact real backed-up world tile restored')end
 request_image('03-after-paid-level-world');tick(0);record(taskName,snap());journal:close();desired=0;done=true
end
'''

SOURCE_BODY='''        for _ in range(30):update()
        scene(q);actor(q,6,112,168);hp=q.get('Z2Hp');update();update();assert q.get('Z2Hp')==hp-16,('real deficit',snapshot(q),{n:q.get(n)for n in ['Z2HurtTimer','InjuryTimer','GuestInvulTicks','TimerControl','GamePauseTimer','Enemy_CollisionBits']})
        q.set('Enemy_Flag',0);wait(lambda:q.get('Z2HurtTimer')==0,60)
        scene(q);actor(q,46,112,184,5);q.set('PowerUpType',0,5);q.invoke('Z2PreparePickupGate',x=5)
        assert q.get('InvPickup',5)==192 and q.get('InvPickupSaveLo',5)==1
        wait(lambda:q.get('Enemy_Flag',5)==0 and q.get('Z2HpPending')==0,160);assert q.get('Z2Hp')==127 and q.get('Z2LearnedSpells')==2
        open_panel()
        if q.get('Z2UiState')&1:edge(1)
        wait(lambda:q.get('Z2PanelPage')==0 and not q.get('Z2PanelPending'),60)
        rows.append(dict(name='earned-spell-page',state=snapshot(q),tiles=panel_tiles(q,b)))
        close_panel();assert q.get('Z2Mp')==127
        drop(0x8a);assert q.get('Z2ExpLo')==50
        wait(lambda:q.get('GamePauseStatus')&1 and q.get('Z2PanelActive')and not q.get('Z2PanelPending')and q.get('Z2PanelPage')==1,60)
        rows.append(dict(name='earned-stats-page',state=snapshot(q),tiles=panel_tiles(q,b)))
        level(2);wait(lambda:not q.get('GamePauseStatus')&1 and not q.get('Z2PanelActive')and not q.get('Z2PanelPending'),60)
        assert q.get('Z2ExpLo')==0 and q.get('Z2LevelsLo')==64 and q.get('Z2Hp')==127
        drop(0x8b);assert q.get('Z2ExpLo')==100;level(1)
        wait(lambda:not q.get('GamePauseStatus')&1 and not q.get('Z2PanelPending'),60);assert q.get('Z2ExpLo')==0 and q.get('Z2LevelsLo')==72
        drop(0x8d);assert q.get('Z2ExpLo')+256*q.get('Z2ExpHi')==500;level(0)
        for _ in range(10):
            update()
            if q.get('GamePauseStatus')&1:
                wait(lambda:q.get('Z2PanelActive')and not q.get('Z2PanelPending'),60);edge(64)
        wait(lambda:not q.get('GamePauseStatus')&1 and not q.get('Z2PanelActive')and not q.get('Z2PanelPending'),60)
        assert q.get('Z2ExpLo')+256*q.get('Z2ExpHi')==300 and q.get('Z2LevelsLo')==73
'''

def panel_tiles(q,b):
    memory=list(q.m[:0x8000]);banks=list(q.m.banks);tiles=[]
    try:
        for i in range(196):
            q.put(Z2PanelIndex=i,Z2PanelRow=i//14,Z2PanelCol=i%14);c,_=q.invoke('Z2PanelTile');tiles.append(c.a)
    finally:
        q.m[:0x8000]=memory
        for i,v in enumerate(banks):q.m.page(i,v)
    assert all(v>=192 for v in tiles),'Every panel cell uses the genuine last1KB font'
    return tiles

def main():
    assert sha(ROM)==EXPECTED;b=scoped_load(ROM)
    parent=B/'current-z2glove-zelda2-easy-earned-v1';ready=parent/'prepared-not-run.json';old=json.loads(ready.read_text());assert all(sha(q['path'])==q['sha256']for q in old['bindings'])
    base=R/'tools/audit/current_zelda2_earned_v1.lua';text=base.read_text();first=text.index('local function campaign()');last=text.index('local co=coroutine.create(campaign)',first)
    original=text[first:last];text=text[:first]+PASSIVE+'\n'+CAMPAIGN+text[last:]
    # Close journal only at final stop, since later NMI/endFrame observers may
    # still fire after the final Main requested completion.
    text=text.replace("record(taskName,snap());journal:close();desired=0;done=true","record(taskName,snap());desired=0;done=true")
    marker="local f=assert(io.open(OUTPUT..'result.json','w'));";assert text.count(marker)==1;text=text.replace(marker,"journal:close();"+marker)
    fixture=R/'tools/audit/current_zelda2_panel_supplement_v1.lua';assert not(B/'current-z2glove-zelda2-panel-supplement-v1').exists();fixture.write_text(text,newline='\n')
    # Exact unchanged helpers/guards outside one declared campaign replacement
    # and the additive readonly display observation/serializer close.
    reverse=text.replace(PASSIVE+'\n'+CAMPAIGN.replace("record(taskName,snap());journal:close();desired=0;done=true","record(taskName,snap());desired=0;done=true"),original).replace('journal:close();'+marker,marker)
    assert reverse==base.read_text()
    assert text.count('emu.write(')==2 and 'removeMemoryCallback'not in text and not re.search(r'\b(?:and|or)\d',text)
    body=inspect.getsource(source.campaign);a=body.index('        for _ in range(30):update()');e=body.index('    finally:NesMPU.step=original',a);body=body[:a]+SOURCE_BODY+body[e:]
    env=dict(vars(source));env.update(panel_tiles=panel_tiles,EXPECTED=EXPECTED);exec(compile(body,str(Path(__file__))+'::actual-earned-source','exec'),env)
    campaign=env['campaign'](b,0);assert campaign['passed'];pages={str(i):next(r['tiles']for r in campaign['rows']if r['name']==n)for i,n in [(0,'earned-spell-page'),(1,'earned-stats-page')]}
    out=B/'current-z2glove-zelda2-panel-supplement-v1';assert not out.exists();out.mkdir()
    cfg=json.loads((parent/'config.json').read_text());cfg['panel_expected']=pages
    needed=set(re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",text))|{'Z2PanelPage','Z2PanelCursor','Z2PanelOrigin','Z2PanelChr','Z2PanelTiles','CurrentCHRBank','X5ChrMode','ReloadCHRBank'}
    for n in needed:cfg['ram'][n]=address(b,n)
    n='Z2PanelUnblank';d=int(b['syms'][n]['size'],0)-1;at=location(b,n)+d;assert b['raw'][at]==96
    cfg['hooks']['PanelUnblankReturn']=dict(pc=address(b,n)+d,banks=[(at-16)//8192],bytes=[96],source_symbol=n,delta=d)
    cfg['scope']='Supplement only: actual mature raw0/C0 healing, actual50/100/500EXP bags, three paid first Life/Magic/Attack levels and real B deferral with unspent300EXP, real pause/spell/stats control, exact full panel tiles/physicalfont395 across three qualified completed start/end epochs, delayed screenshots and world restoration. Bag100/500 are complete staged mature actors accepted by the genuine four-denomination collection table; natural DropRoll only selects50/200, so this is not natural emergence/drop coverage. No seeded learned/HP/MP/EXP/levels/outcomes; no native result before launch. Existing20-reward/eight-spell gallery remains separate and immutable.'
    put(out/'config.json',cfg);(out/'run.lua').write_text('CURRENT_ZELDA2_EARNED='+lua(cfg)+'\ndofile([=['+fixture.as_posix()+']=])\n',newline='\n')
    cmd=json.loads((parent/'command.json').read_text());cmd['argv']=[str(out/'native')if v==str(parent/'native')else str(out/'run.lua')if v==str(parent/'run.lua')else v for v in cmd['argv']];put(out/'command.json',cmd)
    proof=out/'source-controls.json';put(proof,dict(passed=True,native_run=False,Lua_VM_executed=False,ROM_sha256=EXPECTED,actual_source_campaign=campaign,reverse_exact_helpers_and_strict_guards=True,three_complete_panel_epochs_required=True,physical_font=395,expected_panel_cells_per_page=196,readonly_journal_caps=dict(rows=2400,bytes=1048576),screenshot_count=3,baseline_images_are_NOT_panel_visual_pass=True,source_limits='CPU actual complete GameLoop + genuine tile producer; cannot prove native display timing or actual PNG pixels. Panel pixel checker must run on new native output.'))
    paths={Path(q['path'])for q in old['bindings']if Path(q['path'])not in{parent/'config.json',parent/'run.lua',parent/'command.json',parent/'source-controls.json'}}
    paths|={Path(__file__),fixture,ready,proof,*[out/n for n in ['config.json','run.lua','command.json']],R/'chr/characters/zelda2-pause-font.chr'}
    rp=out/'prepared-not-run.json';put(rp,dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,ROM_sha256=EXPECTED,numeric_mode=0,variant=1,source_qualified=True,Lua_VM_executed=False,scope=cfg['scope'],caps=dict(wall=8000,updates=5000,PNG=8,files=64,bytes=2000000000,journal_bytes=1048576),bindings=[bind(p)for p in sorted(paths)]))
    assert all(sha(q['path'])==q['sha256']for q in json.loads(rp.read_text())['bindings'])
    print(json.dumps(dict(ready=str(rp),sha256=sha(rp),source_GameLoops=campaign['GameLoop_calls'],bindings=len(paths),command=str(out/'command.json'))))

if __name__=='__main__':main()
