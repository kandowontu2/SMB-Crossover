"""Small genuine Z2 mature-reward/ability preparations. Never launches Mesen."""
from pathlib import Path
import argparse,hashlib,json,re,sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from current_roster_compact_11_v1 import lua,navigation

R=Path(__file__).resolve().parents[2];B=R/'build';FIXTURE=R/'tools/audit/current_zelda2_earned_v1.lua'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:dict(path=str(Path(p).resolve()),bytes=Path(p).stat().st_size,sha256=sha(p))
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n',newline='\n')
ACTOR='Enemy_Flag Enemy_ID Enemy_State Enemy_BoundBoxCtrl Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_Y_HighPos Enemy_X_Speed Enemy_Y_Speed Enemy_Y_MoveForce Enemy_MovingDir Enemy_SprAttrib EnemyOffscrBitsMasked Enemy_CollisionBits MmEnemyHealthLo MmEnemyHealthHi MmEnemyFlash RgEnemyStun PowerUpType InvPickupOwner InvPickup InvPickupSaveLo'.split()
ENV='Block_Buffer_1 MmSolidTerrain MmBrickHealth ScrollLock ScreenLeft_X_Pos ScreenLeft_PageLoc ScreenRight_X_Pos ScreenRight_PageLoc ScrollThirtyTwo AreaParserTaskNum Player_X_Position Player_PageLoc MmOldX Player_Y_Position Player_Y_HighPos Player_State PlayerFacingDir Player_MovingDir Player_CollisionBits Player_X_Speed Player_Y_Speed Player_X_MoveForce Player_Y_MoveForce MmVX MmVY MmXFraction MmYFraction'.split()
DROP='Z2DropKind Z2DropX Z2DropPage Z2DropY Z2DropVY Z2DropFraction Z2DropAge'.split()
FINAL='Z2Hp Z2Mp Z2ExpLo Z2ExpHi Z2LevelsLo Z2LevelsHi Z2Containers Z2LearnedSpells Z2Tech Z2ActiveSpells Z2Selection Z2HpPending Z2MpPending Z2ExpPendingLo Z2ExpPendingHi Z2UiState Z2UiCursor Z2PanelActive Z2PanelPending GamePauseStatus Z2CachedPose Player_X_Position Player_Y_Position Player_State'.split()
FORBIDDEN='InvAmmo InvOwnedLo InvOwnedHi InvSelected Z2Hp Z2Mp Z2ExpLo Z2ExpHi Z2LevelsLo Z2LevelsHi Z2Containers Z2LearnedSpells Z2Tech Z2ActiveSpells Z2Selection Z2HpPending Z2MpPending Z2ExpPendingLo Z2ExpPendingHi Z2EnemyHp Z2EnemyExpReceipt Z2ShotKind Z2AttackStage Z2AttackTimer Z2HurtTimer Z2CachedPose Z2Variant PlayerStatus PlayerSize NumberofLives GuestPowerupActive GuestPowerupTarget CheatInvincible MmDeathFlag SavedJoypadBits SavedJoypad1Bits'.split()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--expected-sha256',required=True);p.add_argument('--mode',type=int,choices=[0,1],required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--baseline-negative',action='store_true');a=p.parse_args()
    rom=a.rom.resolve();assert sha(rom)==a.expected_sha256;out=a.output.resolve();assert out.is_relative_to(B)and not out.exists()
    b=scoped_load(rom);text=FIXTURE.read_text();allowed=set(ACTOR+ENV+DROP);assert not allowed&set(FORBIDDEN)
    assert text.count('emu.write(')==2 and 'removeMemoryCallback'not in text and not re.search(r'\b(?:and|or)\d',text)
    names=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))|allowed|set(FORBIDDEN+FINAL)
    names|={'CurrentBank','CurrentBankC','Sprite0HitDetectFlag','NmiDisable','Mirror_PPUMASK','DisableScreenFlag'}
    needed=set(re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",text))|allowed|set(FORBIDDEN+FINAL)|{'CurrentBank','CurrentBankC','Sprite0HitDetectFlag','NmiDisable','Mirror_PPUMASK','DisableScreenFlag'}
    ram={n:address(b,n)for n in names if n in b['syms']and(address(b,n)<8192 or 0x5c00<=address(b,n)<0x8000)};assert not needed-set(ram),sorted(needed-set(ram))
    assert all(at<8192 or 0x5c00<=at<0x8000 for at in ram.values()),'Actual compiled RAM aliases only'
    assert not {ram[n]for n in allowed}&{ram[n]for n in FORBIDDEN},'No forbidden alias under another name'
    hooks={};copies=[]
    def hook(key,n,delta=0,size=3,owner=None):
        at=location(b,n)+delta;pc=address(b,n)+delta;bank=(at-16)//8192;banks=[bank];bs=list(b['raw'][at:at+size])
        if bank==127:
            owner=owner or n;start=location(b,owner);length=int(b['syms'][owner]['size'],0);clone=16+125*8192+(address(b,owner)&8191)
            assert length>0 and b['raw'][start:start+length]==b['raw'][clone:clone+length]
            assert b['raw'][16+125*8192+(pc&8191):16+125*8192+(pc&8191)+size]==bytes(bs);banks=[125,127];copies.append(owner)
        hooks[key]=dict(pc=pc,banks=banks,bytes=bs,source_symbol=n,delta=delta)
        return hooks[key]
    for key,n in [('NmiEntry','NonMaskableInterrupt'),('IrqEntry','IrqScrollSplit')]:hook(key,n)
    assert b['raw'][location(b,'GameLoop'):location(b,'GameLoop')+5]==bytes([169,255,141,address(b,'NmiDisable')&255,address(b,'NmiDisable')>>8]);hook('GameLoopOwned','GameLoop',5)
    for key,n,op in [('GameLoopFinish','GameLoop',96),('NmiReturn','NonMaskableInterrupt',64),('IrqReturn','IrqScrollSplit',64)]:
        d=int(b['syms'][n]['size'],0)-1;assert b['raw'][location(b,n)+d]==op;hook(key,n,d,1)
    post=location(b,'PostDmaMaskEnable');mirror=address(b,'Mirror_PPUMASK');load=bytes([165,mirror])if mirror<256 else bytes([173,mirror&255,mirror>>8])
    assert b['raw'][post-3:post]==b'\x8d\x14\x40'and b['raw'][post:post+len(load)+3]==load+b'\x8d\x01\x20';hook('DmaComplete','PostDmaMaskEnable',len(load),owner='OAMandReadJoypad')
    actual=dict(Collect='Z2CollectPickupGate',Reward='Z2CollectReward',Cast='Z2TryCast',Level='Z2LevelUp',Damage='Z2Damage',Hit='Z2HitEnemy',Award='Z2AwardEnemy',Jar='Z2JarPickup',EXP='Z2QueueExp')
    for k,n in actual.items():hook(k,n)
    panel=[]
    for n,name,pending,delta in [('Z2PanelTick','panel-open',1,0),('Z2PanelSync','panel-close',2,-2)]:
        at=location(b,n);length=int(b['syms'][n]['size'],0);raw=b['raw'][at:at+length];hits=[i for i in range(length-2)if raw[i:i+3]==b'\x8d\x14\x40'];assert len(hits)==1
        d=hits[0];request=address(b,n)+d+3
        if pending==1:
            assert raw[d+3:d+5]==b'\xa9\x00';h=hook('PanelOpenComplete',n,d+5);complete='PanelOpenComplete'
        else:
            target=address(b,'Z2PanelAttributesRestore');assert raw[d+3:d+6]==bytes([32,target&255,target>>8]);h=hook('PanelCloseComplete','Z2PanelAttributesRestore');complete='PanelCloseComplete'
        panel.append(dict(name=name,request_pc=request,request_bytes=[141,20,64],bank=(at-16)//8192,pending=pending,stack_delta=delta,complete_hook=complete))
    control=B/'zelda2_easy_glove_controls.json';z=json.loads(control.read_text());assert z['passed']and not z['native_run']and z['parent_sha256']=='ee1152a49deae31e82d202159310fa3719cbcfd85de571fd1b9ac15a1cd2a7b3'
    for item in z['bindings']:assert sha(item['path'])==item['sha256']
    source=Path(z['fixed_source_campaigns'][a.mode]['path']);s=json.loads(source.read_text());assert s['passed']and s['mode']==a.mode
    if a.baseline_negative:assert a.mode==0 and a.expected_sha256==z['parent_sha256']
    else:assert a.expected_sha256==z['candidate_sha256']and s['ROM_sha256']==a.expected_sha256
    rewards=[]
    for row in s['rows']:
        if row['name'].startswith('reward-'):
            rewards.append(dict(reward=int(row['name'].split('-')[1],16),prepared=row['prepared']))
    assert [q['reward']for q in rewards]==[192,193,194,195,196,197,198,199,200,201,202,203,204,203,204,203,204,203,204,205]
    scope='Controlled mature actors derived from actual raw0 first/raw1 later Z2PreparePickupGate. Real collision grants C0..CD, actual contact deficits, all eight paid Select spells and complete effects, Up/Down thrusts, Glove brick, jars, earned combat/50+200+200 EXP bags, paid Attack/Magic/Life purchases and real pause page. No learned/HP/MP/EXP/level/tech/selection/shot/death outcomes seeded. No reveal/rise/natural-drop producer, all-stat maxima, area-reset/persistence/campaign/everypose/allpixel/audio-fidelity/60Hz claim. Seven selected screenshots need independent actual image review.'
    cfg=dict(ROM_sha256=a.expected_sha256,mode=a.mode,ram=ram,hooks=hooks,owner_hooks=list(actual),panel_dma=panel,setup_allowed={n:True for n in allowed},forbidden={n:True for n in FORBIDDEN},final_fields=FINAL,rewards=rewards,spell_costs=list(b['raw'][location(b,'SpellCosts'):location(b,'SpellCosts')+64]),navigation=navigation(b['raw'],lambda n:location(b,n),4),dma_store_return=address(b,'PostDmaMaskEnable'),smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']},scope=scope)
    out.mkdir();put(out/'config.json',cfg);(out/'run.lua').write_text('CURRENT_ZELDA2_EARNED='+lua(cfg)+'\ndofile([=['+FIXTURE.as_posix()+']=])\n',newline='\n')
    argv=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out/'native'),'--emulator','C:/Mesen2/Mesen.exe',str(out/'run.lua'),str(rom),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.removeSpriteLimit=false','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
    parent=R/'tools/audit/current_rygar_powerups_v1.lua';old=parent.read_text();start='-- All callback registration is startup-static.';end='emu.addEventCallback(function()\n if not entered'
    guard=old[old.index(start):old.index(end)];assert len(guard.encode())==4058
    # These literal mechanical predicates remain untouched inside the narrowly
    # owner-extended guard. No deadline/write/destination/E3 condition widened.
    for literal in ['pending and mask&24==0','i<=256 and v==pending.source[i]','pending.writes==256 and mask&24==0','line>=241 and line<=260 or line==-1 and dot<=274','hw[i]~=want','NMI AXY/SP restored','NMI five SMC operands restored','Actual foreground banks restored']:
        assert literal in text,literal
    checks=dict(source_only=True,native_run=False,Lua_VM_executed=False,all_literal_dynamic_RAM_compiled=True,whole_cloned_owners=sorted(set(copies)),strict_parent_guard_sha256=hashlib.sha256(guard.encode()).hexdigest(),owner_extension_only='Two actual blanked foreground pause transfers, each exact PC/bank/request bytes, SP and real completion. NMI E008 unchanged. Every256 unmasked source/write/destination byte and E3 physical encoding remains strict.',baseline_expected_negative=a.baseline_negative,source_campaign=bind(source),source_controls=bind(control),no_tested_resource_seed_aliases=True)
    put(out/'source-controls.json',checks)
    paths=[Path(__file__),FIXTURE,parent,R/'tools/audit/current_zelda2_earned_cpu_v1.py',control,source,B/'zelda2_easy_glove_build.json',rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl')]
    paths += [R/'tools/audit'/n for n in ['link_pit_rygar_sophia_audit_cpu.py','check_tmnt_render_oa.py','verify_native_relocation.py','current_roster_compact_11_v1.py','final_inventory_compact_capture_v1.py','run_mesen_isolated.py','capture_budget.py']]+[R/'tools/run_mesen.py']
    paths += [out/n for n in ['config.json','run.lua','source-controls.json','command.json']]
    ready=out/'prepared-not-run.json';put(ready,dict(status='PREPARED_DO_NOT_RUN',passed=False,native_run=False,goal_complete=False,ROM_sha256=a.expected_sha256,character=4,variant=1,numeric_mode=a.mode,baseline_expected_Glove_FALSE=a.baseline_negative,mechanics_source_qualified=True,Lua_VM_executed=False,caps=dict(updates=5000,wall_frames=8000,host_seconds=1200,files=64,bytes=2000000000,PNGs=8),scope=scope,bindings=[bind(p)for p in dict.fromkeys(paths)]))
    z=json.loads(ready.read_text());assert all(sha(p['path'])==p['sha256']for p in z['bindings'])
    print(json.dumps(dict(prepared=True,native_run=False,ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),command=str(out/'command.json'))))

if __name__=='__main__':main()
