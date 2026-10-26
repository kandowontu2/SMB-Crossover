"""Prepare one current3b eight-case Samus Hard gallery; no native execution."""
from pathlib import Path
import argparse, ast, hashlib, json, re, shutil, sys
from final_samus_hard_gallery_source_v1 import SHA, PARENT, ROOT, D, TraceArena, OWNER_NAMES
from final_item_abilities_run import lua
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_item_abilities_current731_prepare_v1 import protocol, dma_mocks, OLD_DMA
from final_item_abilities_static_prepare_v2 import core_tests, old_core
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from parodius_visibility_hud_static_startup_v1 import MOCK
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def cases():
 def t(kind,face=1,**kw):return dict(kind=kind,face=face,**kw)
 return [
  dict(case=1,name='starting-short',owned=0,status=0,native_type=1,tasks=[t('free'),t('contact',2),t('up'),t('pool',2)]),
  dict(case=2,name='long-beam',owned=129,status=1,native_type=2,tasks=[t('free'),t('contact',2),t('block'),t('pool',2)]),
  dict(case=3,name='Morph-bombs',owned=131,status=1,tasks=[t('morph-deny',owned=129),t('bombs',2)]),
  dict(case=4,name='missile-Special',owned=133,status=1,native_type=2,tasks=[t('missile-select',stock=2),t('free',stock=2,keepSelection=True),t('missile-paid',stock=2,keepSelection=True),t('missile-empty',2,stock=0,keepSelection=True),t('missile-pool',2,stock=2,keepSelection=True)]),
  dict(case=5,name='Ice',owned=137,status=1,tasks=[t('ice-thaw'),t('ice-break',2)]),
  dict(case=6,name='Wave',owned=145,status=1,native_type=3,tasks=[t('wave-up',center=254),t('wave-up',2,center=258),t('wave-contact'),t('wave-block',2)]),
  dict(case=7,name='Varia',owned=161,status=1,tasks=[t('firebar'),t('firebar',2),t('ordinary-hurt'),t('firebar-no-varia',2,owned=129)]),
  dict(case=8,name='Screw',owned=193,status=1,tasks=[t('screw'),t('screw',2)]),
 ]

def compose(cfg):
 base=(ROOT/'tools/audit/final_item_matrix_progressive.lua').read_text()
 prefix=base[:base.index('local function seed()')]
 assert prefix.count("assert(n~='PlayerStatus','Power tiers must be acquired');")==1
 prefix=prefix.replace("assert(n~='PlayerStatus','Power tiers must be acquired');",'')
 assert OLD_DMA in prefix;prefix=prefix.replace(OLD_DMA,(ROOT/'tools/audit/final_item_abilities_dma731_v1.lua').read_text()+'\n')
 core=(ROOT/'tools/audit/final_item_abilities_static_return_v1.lua').read_text()
 mechanics=(ROOT/'tools/audit/final_samus_hard_gallery_native_v1.lua').read_text()
 guards=base[base.index('local saved=nil'):base.index('emu.addEventCallback(function()\n if not entered then emu.setInput')]
 end=base[base.index('emu.addEventCallback(function()\n wall=wall+1'):]
 before="local f=assert(io.open(OUTPUT..'native-progressive.json','w'));f:write(json({passed=true,goal_complete=false,family=C.family,hard=C.hard,cases=records,updates=updates,nmis=nmis,minSP=minSP,apuWrites=apuWrites,irq_scroll_stores=irqStores,hardware_chr_checks=chrChecks,complete_dma_checks=dmaChecks,scope='Actual head-bump/reveal/native full rise; explicit post-rise collision placement; cold selection and source-owned transformation/use. No campaign claim'}));f:close();emu.stop(0)"
 after="local f=assert(io.open(OUTPUT..'native-samus-gallery.json','w'));f:write(json({passed=true,goal_complete=false,lane='B controlled abilities',acquisition=false,actual_mode_readback=r('CrossoverBehaviorVersion'),family=C.family,hard=C.hard,cases=records,updates=updates,nmis=nmis,minSP=minSP,apuWrites_includingDMAController=apuWrites,irq_scroll_stores=irqStores,hardware_chr_checks=chrChecks,complete_dma_checks=dmaChecks}));f:close();emu.stop(0)"
 assert end.count(before)==1;end=end.replace(before,after).replace("wall<9000,'Bounded progressive fixture '","wall<12000,'Bounded eight-case Samus gallery '")
 captures=(ROOT/'tools/audit/final_item_abilities_pit731_ppu_v1.lua').read_text()
 inputs="emu.addEventCallback(function()if not entered then emu.setInput(menu(),0)else emu.setInput(samusInput(),0)end end,emu.eventType.inputPolled)\n"
 return 'FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+(ROOT/'tools/audit/final_item_abilities_failure.lua').read_text()+'\n'+prefix+core+'\n'+mechanics+'\n'+guards+inputs+captures+'\n'+end+'\nFINAL_ITEM_ABILITIES_STATIC_INSTALL_RETURNS()\n',guards

def cpu_added(b):
 rows=[];palettes={}
 for owned in [0,129,131,133,137,145,161,193]:
  q=TraceArena(b);q.put(PlayerStatus=0 if not owned else 1,DisableScreenFlag=0);q.set('InvOwnedLo',owned,2);q.invoke('GetPlayerColors')
  length=q.get('VRAM_Buffer1_Offset');packet=[q.get('VRAM_Buffer1',i)for i in range(length+1)]
  assert length==19 and packet[-1]==0
  # Validate every command exactly as the native parser will read it.
  at=0
  while packet[at]:n=packet[at+2]&63;assert n>0;at+=3+(1 if packet[at+2]&64 else n)
  assert at==length;palettes[str(owned)]=packet
  rows.append(dict(kind='complete-GetPlayerColors-initial-state',owned=owned,packet=packet,calls=q.calls))
 # Source exact freeze and thaw: emitted Ice, complete real dispatch and hit core.
 for break_it in [False,True]:
  q=TraceArena(b);q.set('InvOwnedLo',137,2);q.put(A_B_Buttons=64,PreviousA_B_Buttons=0);q.invoke('ProcFireball_Bubble')
  for _ in range(3):q.put(A_B_Buttons=0,InvFresh=0);q.invoke('ProcFireball_Bubble')
  world=q.get('RgShotX',9)+256*q.get('RgShotPage',9)-6
  for n,v in [('Enemy_Flag',1),('Enemy_ID',6),('Enemy_State',0),('Enemy_X_Position',world&255),('Enemy_PageLoc',world>>8),('Enemy_Y_Position',q.get('RgShotY',9)-8),('Enemy_Y_HighPos',1),('Enemy_BoundBoxCtrl',9)]:q.set(n,v)
  q.invoke('ProcFireball_Bubble');assert q.get('AvFrozen')+256*q.get('AvFrozenHi')==360 and q.get('RgShotType',9)==0
  if break_it:
   # B first releases, then a real new edge spawns at the unchanged muzzle.
   q.put(A_B_Buttons=64,PreviousA_B_Buttons=0);q.invoke('ProcFireball_Bubble')
   for _ in range(10):q.put(A_B_Buttons=0,InvFresh=0);q.invoke('ProcFireball_Bubble')
   assert q.get('AvFrozen')+256*q.get('AvFrozenHi')==0
  else:
   for _ in range(360):q.put(A_B_Buttons=0,InvFresh=0);q.invoke('ProcFireball_Bubble')
   assert q.get('AvFrozen')+256*q.get('AvFrozenHi')==0 and q.get('RgEnemyStun')==q.get('LsrFrozenPose')==0
  rows.append(dict(kind='complete-emission-contact-Ice-'+('break'if break_it else'thaw'),calls=q.calls))
 # Native three-bomb attempts and unchanged source timer/cleanup, no outcome seed.
 q=TraceArena(b);q.set('InvOwnedLo',131,2);q.put(SmBall=1)
 for _ in range(4):q.put(A_B_Buttons=64,PreviousA_B_Buttons=0);q.invoke('ProcFireball_Bubble')
 assert sum(q.get('SmBombAge',i)>0 for i in range(3))==3
 for _ in range(90):q.put(A_B_Buttons=0,InvFresh=0);q.invoke('ProcFireball_Bubble')
 assert sum(q.get('SmBombAge',i)>0 for i in range(3))==0
 rows.append(dict(kind='complete-three-bomb-pool-refusal-expiry',calls=q.calls))
 # Authenticate the proposed renderer hooks through actual complete DrawAll.
 for n in ['DrawAllMetasprites','DrawMetasprite','MetaspriteRenderLoop','SamusDrawShots::Draw','RemainingDraw::ArtPointer']:
  if n not in OWNER_NAMES:OWNER_NAMES.append(n)
 for owned,attack in [(0,True),(129,True),(137,True),(145,True),(161,False),(193,False)]:
  q=TraceArena(b);q.set('InvOwnedLo',owned,2);q.put(PlayerStatus=0 if not owned else 1)
  if attack:q.put(A_B_Buttons=64,PreviousA_B_Buttons=0);q.invoke('ProcFireball_Bubble')
  q.invoke('PlayerGfxHandler');q.invoke('DrawAllMetasprites')
  names={z['owner']for c in q.calls for z in c['entries']};assert {'DrawAllMetasprites','DrawMetasprite','MetaspriteRenderLoop','SamusDrawShots'}<=names
  if attack and owned!=137:assert 'SamusDrawShots::Draw'in names
  if attack and owned==137:assert 'RemainingDraw::ArtPointer'in names
  rows.append(dict(kind='complete-body-effect-renderer-gateways',owned=owned,attack=attack,calls=q.calls))
 for owned in [129,133]:
  for stock in [0,19,20]:
   q=TraceArena(b);q.set('InvOwnedLo',owned,2);q.set('InvAmmo',stock,34);q.invoke('RemainingRefill')
   assert q.get('InvAmmo',34)==(min(20,stock+2)if owned&4 else stock)
   rows.append(dict(kind='complete-owned-missile-refill2-cap20',owned=owned,before=stock,after=q.get('InvAmmo',34),calls=q.calls))
 for enemy in [17,45]:
  q=TraceArena(b);q.set('InvOwnedLo',137,2);q.put(A_B_Buttons=64,PreviousA_B_Buttons=0);q.invoke('ProcFireball_Bubble')
  for _ in range(3):q.put(A_B_Buttons=0,InvFresh=0);q.invoke('ProcFireball_Bubble')
  world=q.get('RgShotX',9)+256*q.get('RgShotPage',9)-6
  for n,v in [('Enemy_Flag',1),('Enemy_ID',enemy),('Enemy_State',0),('Enemy_X_Position',world&255),('Enemy_PageLoc',world>>8),('Enemy_Y_Position',q.get('RgShotY',9)-8),('Enemy_Y_HighPos',1),('Enemy_BoundBoxCtrl',9)]:q.set(n,v)
  q.invoke('ProcFireball_Bubble');assert q.get('AvFrozen')+256*q.get('AvFrozenHi')==0
  assert 'SamusHardEnemyAdmission'in {z['owner']for z in q.calls[-1]['entries']}
  rows.append(dict(kind='complete-Ice-contact-resistance',enemy=enemy,frozen=0,calls=q.calls,scope='CPU spatial hit and real property owner; not a fully initialized native boss encounter.'))
 return dict(passed=True,cases=len(rows),rows=rows,scope='Actual compiled isolated full getters/gateways. Palette packets are declared initial-state seeds; freeze/control results are not native or PPU results.'),palettes

def phase_models(LuaRuntime,script):
 """Actual finalizer bodies with explicit synthetic postconditions, not emulation."""
 anchor='local function hook(n,fn)\n'
 assert script.count(anchor)==1
 instrumented=script.replace(anchor,anchor+' if TEST_HOOKS then TEST_HOOKS[n]=fn end\n')
 assert instrumented.replace(anchor+' if TEST_HOOKS then TEST_HOOKS[n]=fn end\n',anchor)==script
 pre=MOCK+'''\nL={};OUTPUT='mock/';TEST_HOOKS={};mem={};emu.memType.nesPrgRom=6
 emu.read=function(a,t)return mem[a]or 0 end
 emu.write=function()error('Phase models never run fixture seed writes')end
 emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end
 '''
 common="""
entered=true;done=false;phase='run';age=90;wall=500;updates=10;taskIndex=1;index=1
current={t={kind=KIND,face=1},q={case=2,name='mock',native_type=2,tasks={{kind=KIND}}},stage={spawns={{}},debits={},draws={['native:1']=1},hits=1,damageCalls=1,freezes=0,thaws=0,freezeSteps=0,bodyProtects=0,blockCalls=0,bombAttempts=0,bombRefusals=0,boosts=0,firebarCalls=0,injuries=0,sourceSfx={{kind='Square1SoundQueue',value=C.beam_sfx},{kind='SmSfx',value=14},{kind='AvAudioRequest',value=C.screw_sfx},{kind='AvAudioRequest',value=C.missile_sfx}}}}
mem[L.CrossoverBehaviorVersion]=1
"""
 cases=[
  ('short-expiry','free',"current.q.case=1;current.stage.shortExpiry=true",True),
  ('missing-short-expiry','free',"current.q.case=1",False),
  ('real-contact','contact','',True),('missing-contact','contact','current.stage.hits=0',False),
  ('terrain-query','block','current.stage.blockCalls=1',True),('missing-terrain-query','block','',False),
  ('wave-terrain-bypass','wave-block','',True),('wrong-Wave-terrain-call','wave-block','current.stage.blockCalls=1',False),
  ('wave-real-page','wave-up','current.stage.waveMoves=4;current.stage.pageCrossings=1',True),
  ('missing-Wave-page','wave-up','current.stage.waveMoves=4;current.stage.pageCrossings=0',False),
  ('noMorph-refusal','morph-deny','age=25;mem[L.SmCrouch]=1',True),
  ('wrong-noMorph-ball','morph-deny','age=25;mem[L.SmCrouch]=1;mem[L.SmBall]=1',False),
  ('three-bombs-refusal-boost-contact','bombs','age=170;current.stage.bombAttempts=4;current.stage.bombRefusals=1;current.stage.boosts=1;current.stage.ballDraw=true;current.stage.explosionDraw=true',True),
  ('missing-bomb-refusal','bombs','age=170;current.stage.bombAttempts=4;current.stage.bombRefusals=0;current.stage.boosts=1',False),
  ('missile-selected','missile-select','age=85;current.stage.selected=2;mem[L.InvSelected+2]=2;for i,v in ipairs(C.missile_hud_name)do mem[0x2023+i-1]=v end',True),
  ('wrong-missile-selection','missile-select','age=85;current.stage.selected=0',False),
  ('two-missiles-sourceZero','missile-paid','age=115;current.stage.debits={{},{}};current.stage.spawns={{},{}};current.stage.sourceZeroWitness={}',True),
  ('missing-missile-sourceZero','missile-paid','age=115;current.stage.debits={{},{}};current.stage.spawns={{},{}}',False),
  ('empty-missile-refusal','missile-empty','age=30;current.stage.spawns={}',True),
  ('empty-missile-wrong-spawn','missile-empty','age=30',False),
  ('shared-pool-refusal','pool','age=12;current.stage.spawns={};mem[L.SmShotType]=2;mem[L.SmShotType+1]=2;mem[L.SmShotType+2]=2',True),
  ('shared-pool-wrong-spawn','pool','age=12',False),
  ('Ice360-thaw','ice-thaw','age=400;current.stage.freezes=1;current.stage.thaws=1;current.stage.freezeSteps=360',True),
  ('Ice359-rejected','ice-thaw','age=400;current.stage.freezes=1;current.stage.thaws=1;current.stage.freezeSteps=359',False),
  ('Ice-break-before-damage','ice-break','current.stage.freezes=1;current.stage.breaks=1',True),
  ('Ice-break-no-contact','ice-break','current.stage.freezes=1;current.stage.breaks=1;current.stage.hits=0',False),
  ('Varia-source-protection','firebar','age=45;current.stage.firebarCalls=11;mem[L.PlayerStatus]=1;mem[L.InvOwnedLo+2]=161;mem[L.SmChrBank]=C.varia_stand_chr',True),
  ('Varia-wrong-ownership','firebar','age=45;current.stage.firebarCalls=11;mem[L.PlayerStatus]=1;mem[L.InvOwnedLo+2]=129;mem[L.SmChrBank]=C.varia_stand_chr',False),
  ('native-hurt-drain-recover','ordinary-hurt','current.stage.injuries=1',True),
  ('native-hurt-wrong-owned','ordinary-hurt','current.stage.injuries=1;mem[L.InvOwnedLo+2]=161',False),
  ('Screw-contact-land','screw','current.stage.bodyProtects=1;current.stage.flipDraw=true',True),
  ('Screw-no-protection-rejected','screw','',False),
 ]
 result=[]
 for name,kind,body,want in cases:
  rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(pre+instrumented+common.replace('KIND',lua(kind))+body+"\nlocal ok,e=pcall(TEST_HOOKS.finish);TEST_PHASE_OK=ok;TEST_PHASE_ERROR=tostring(e);TEST_PHASE_PASSED=current.stage.passed")
  got=bool(rt.globals().TEST_PHASE_OK);assert got==want,(name,rt.globals().TEST_PHASE_ERROR)
  if want:assert rt.globals().TEST_PHASE_PASSED is True,name
  result.append(dict(name=name,passed=True,expected='accept'if want else'reject'))
 return dict(passed=True,models=result,synthetic_not_native=True,original_body_reverse_exact_after_mock_export=True)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);p.add_argument('--lua-root',required=True,type=Path);a=p.parse_args()
 assert not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True,exist_ok=False)
 sourcepacket=D/'final-samus-hard-gallery-source-v1/freeze-v1';verify_manifest(sourcepacket/'manifest.json');assert sha(sourcepacket/'proof.json')=='7111694cb49852a96060c4fedfe30ebb482a507e3e1df9029165bce43a5a42fa'
 b=scoped_load(PARENT/'candidate.nes');assert sha(PARENT/'candidate.nes')==SHA
 cpu,palettes=cpu_added(b);put(a.output/'additional-CPU-controls.json',cpu)
 plans=cases();assert len(plans)==8;put(a.output/'plans.json',plans)
 def record(ptr,bank):
  pos=16+bank*8192+ptr%8192;n=b['raw'][pos];assert n%4==0 and n<=252
  return dict(address=ptr,bank=bank,bytes=list(b['raw'][pos:pos+n+1]))
 def named(n):return record(address(b,n),(location(b,n)-16)//8192)
 bodybank=(location(b,'SmP0_STANDRight')-16)//8192;body={}
 for table,count in [('SamusPose',3*address(b,'SAMUS_POSE_COUNT')),('SamusCrouch',6)]:
  for face in ['Right','Left']:
   for i in range(count):
    ptr=b['raw'][location(b,table+face+'Lo')+i]+256*b['raw'][location(b,table+face+'Hi')+i]
    body[str(bodybank)+':'+str(ptr)]=record(ptr,bodybank)
 native=[]
 for i in range(18):
  row=[]
  for face in ['Right','Left']:
   ptr=b['raw'][location(b,'SamusDrawShots::Weapon'+face+'Lo')+i]+256*b['raw'][location(b,'SamusDrawShots::Weapon'+face+'Hi')+i]
   row.append(record(ptr,bodybank))
  native.append(row)
 shared=[]
 for i in range(address(b,'AvArtRightHi')-address(b,'AvArtRightLo')):
  row=[]
  for face in ['Right','Left']:
   ptr=b['raw'][location(b,'AvArt'+face+'Lo')+i]+256*b['raw'][location(b,'AvArt'+face+'Hi')+i]
   row.append(record(ptr,b['raw'][location(b,'AvArtBanks')+i]&127))
  shared.append(row)
 mechanics=(ROOT/'tools/audit/final_samus_hard_gallery_native_v1.lua').read_text()
 base=(ROOT/'tools/audit/final_item_matrix_progressive.lua').read_text()
 names=set(re.findall(r"hook\('([^']+)'",mechanics+base))
 # Ignore old progression mechanics discarded by compose; add literal guard hooks.
 names=set(re.findall(r"hook\('([^']+)'",mechanics))|{'NonMaskableInterrupt','NmiReturn','IrqScrollSplit','RosterOamReady','finish'}
 hooks={}
 for n in names-{'finish','NmiReturn'}:
  pos=location(b,n);hooks[n]=dict(address=address(b,n),physical_bank=(pos-16)//8192,bytes=list(b['raw'][pos:pos+3]))
 for n,parent in [('finish','GameLoop'),('NmiReturn','NonMaskableInterrupt')]:
  delta=int(b['syms'][parent]['size'],0)-1;pos=location(b,parent)+delta;assert b['raw'][pos]in[0x60,0x40]
  hooks[n]=dict(address=address(b,parent)+delta,physical_bank=(pos-16)//8192,bytes=[b['raw'][pos]])
 pos=location(b,'IrqScrollSplit');irq=[address(b,'IrqScrollSplit')+i for i in range(int(b['syms']['IrqScrollSplit']['size'],0)-2)if b['raw'][pos+i:pos+i+3]==b'\x8d\x05\x20']
 clear_ranges=[dict(name=n,bytes=address(b,end)-address(b,n))for n,end in [('SamusRamStart','SamusRamEnd'),('AvRamStart','AvRamEnd'),('SpecialRamStart','SpecialRamEnd')]]
 clear_scalars=['GuestBodyNow','GuestBodyPrev','GuestHurtTicks','GuestHurtKind','GuestInvulTicks','GuestFlickerPhase','GuestLegacyHurt','InjuryTimer','PlayerChangeSizeFlag','GuestPowerupActive','GuestPowerupAge','TimerControl','InvPrevious','InvFresh','SavedJoypadBits','SavedJoypad1Bits','A_B_Buttons','PreviousA_B_Buttons','GamePauseStatus','GamePauseTimer','CheatInvincible','MmDeathFlag','MmJumpReleased','MmFrictionYActive','SmCeilingHit','SmSourceJumped','CrouchingFlag','InvRefill','InvRefillTick','InvRefillRemain','SmFreezeRenderState','SmFreezePalettePending','SmFreezeLastBlue','SmFreezePaletteControl']
 arrays=['RgShotType','RgShotX','RgShotPage','RgShotY','RgShotYHigh','RgShotDir','RgShotAge','RgShotFracX','RgShotFracY','RgShotVXLo','RgShotVXHi','RgShotVYLo','RgShotVYHi','RgShotHits','RgShotImpact','XgShotAim','RgShotHitsNow']
 ptr=b['raw'][location(b,'InvNameLo')+34]+256*b['raw'][location(b,'InvNameHi')+34];g=b['segs'][b['syms']['InvNameLo']['seg']];namepos=int(g['ooffs'],0)+ptr-int(g['start'],0)
 q=TraceArena(b);q.set('InvOwnedLo',161,2);q.invoke('PlayerGfxHandler');varia=q.get('SmChrBank')
 cfg=dict(family='samus',character=2,slot=2,hard=True,mode_value=1,cases=plans,ram={},hooks=hooks,irq_scroll_stores=irq,dma_protocol=protocol(b),native_effect_base=address(b,'METASPRITE_SAMUS_BEAM_1'),native_bomb_base=address(b,'METASPRITE_SAMUS_BOMB_1'),ball_pose_low=address(b,'SM_POSE_BALL1'),flip_pose_low=address(b,'SM_POSE_FLIP1'),native_effect_records=native,shared_effect_records=shared,body_records=body,legacy_chr=list(b['raw'][location(b,'ChrPhysicalMap'):location(b,'ChrPhysicalMap')+256]),wave=list(b['raw'][location(b,'SamusWeapons::WaveTable'):location(b,'SamusWeapons::WaveTable')+256]),clear_ranges=clear_ranges,clear_scalars=clear_scalars,shared_arrays=arrays,palette_packets=palettes,varia_stand_chr=varia,beam_sfx=address(b,'Sfx_Fireball'),missile_sfx=address(b,'AV_SFX_SAMUSSHOOTMISSILE'),screw_sfx=address(b,'AV_SFX_SAMUSSCREWATTACK'),missile_hud_name=list(b['raw'][namepos:namepos+7]),art={n:dict(address=address(b,n),bank=(location(b,n)-16)//8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']},smc_fields=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
 probe,_=compose(cfg);used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",probe));used.update(clear_scalars+arrays+[q['name']for q in clear_ranges]+['Sprite_Data'])
 cfg['ram']={n:address(b,n)for n in used if n in b['syms']};script,guards=compose(cfg)
 direct=set(re.findall(r"\b[wr]\('([A-Za-z_][A-Za-z_0-9]*)'",script));assert not direct-set(cfg['ram']),direct-set(cfg['ram'])
 out=a.output/'native';out.mkdir()
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2((PARENT/'candidate.nes').with_suffix(ext),out/('candidate'+ext))
 put(out/'config.json',cfg);(out/'run.lua').write_text(script,encoding='utf-8');(out/'inherited-NMI-stack-APU-guards.lua').write_text(guards,encoding='utf-8')
 assert sha(out/'inherited-NMI-stack-APU-guards.lua')=='6ab7cd71f41f441f4d4d752e2412f83c2b16da06b9e10d3cdf05180c63bf5fdf'
 assert "w('CrossoverBehaviorVersion'"not in script
 sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 ret=core_tests(LuaRuntime,old_core((ROOT/'tools/audit/final_item_abilities_native.lua').read_text()),(ROOT/'tools/audit/final_item_abilities_static_return_v1.lua').read_text())
 dma=dma_mocks(LuaRuntime,(ROOT/'tools/audit/final_item_abilities_dma731_v1.lua').read_text(),dict(dma_protocol=cfg['dma_protocol']))
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.memType.nesPrgRom=6;emu.write=function()error("Unexpected startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end');rt.execute(script)
 count=rt.eval('#callbacks');assert rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')and rt.eval('#events[emu.eventType.endFrame]')==2
 rt.execute('emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
 for frame in [1,2,3]:rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.startFrame);runevents(emu.eventType.endFrame)")
 assert rt.eval('#callbacks')==count
 # Exact actual controller function, finite branch/edge probes. No emulator.
 test="""
current={t={kind='bombs',face=2},stage={}};phase='run'
for _,p in ipairs({{5,'down',true},{10,'down',false},{15,'down',true},{30,'b',true},{40,'b',true},{50,'b',true},{60,'b',true},{64,'b',false},{146,'up',true}})do age=p[1];assert(not not samusInput()[p[2]]==p[3])end
current.t.kind='missile-select';for _,p in ipairs({{5,'start',true},{20,'right',true},{65,'start',true},{70,'start',false}})do age=p[1];assert(not not samusInput()[p[2]]==p[3])end
current.t.kind='missile-paid';for _,p in ipairs({{5,true},{8,false},{45,true},{48,false}})do age=p[1];assert(not not samusInput().select==p[2])end
current.t.kind='ice-break';current.stage.freezeAge=9;age=33;assert(not samusInput().b);age=34;assert(samusInput().b);age=37;assert(not samusInput().b)
current.t.kind='screw';age=5;assert(samusInput().a and samusInput().left and not samusInput().right);age=14;assert(not samusInput().a)
current.t.kind='wave-up';age=5;assert(samusInput().b and samusInput().up)
current.t.kind='firebar';age=5;assert(next(samusInput())==nil)
"""
 rt2=LuaRuntime(unpack_returned_tuples=True);rt2.execute(MOCK+'\nL={};OUTPUT="mock/";emu.memType.nesPrgRom=6;emu.write=function()error("Unexpected startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end');rt2.execute(script+test);assert rt2.eval('#callbacks')==count
 phases=phase_models(LuaRuntime,script);put(a.output/'phase-models.json',phases)
 put(a.output/'static-controls.json',dict(passed=True,source_only=True,actual_Lua=rt.eval('_VERSION'),callbacks=count,dispatcher_last=True,endFrame_callbacks=2,no_startup_emulated_writes=True,post_startup_API_registration_forbidden=True,return_models=ret,DMA_models=dma,controller_probes=24,phase_models=len(phases['models']),original_guard_sha256=sha(out/'inherited-NMI-stack-APU-guards.lua'),CPU_source_cases=cpu['cases']))
 runtime=D/'current3b112-bass-semantic-cleanup-ready-v1/emulator';isolated=a.output/'emulator';isolated.mkdir()
 for q in runtime.iterdir():
  if q.is_file():shutil.copy2(q,isolated/q.name)
 settings=json.loads((isolated/'settings.json').read_bytes().decode('utf-8-sig'))
 for k,v in dict(RemoveSpriteLimit=False,AdaptiveSpriteLimit=False,RandomizeCpuPpuAlignment=False,RandomizeMapperPowerOnState=False,PpuExtraScanlinesBeforeNmi=0,PpuExtraScanlinesAfterNmi=0,DisableSprites=False,DisableBackground=False).items():assert settings['Nes'][k]==v
 assert settings['Emulation']['RunAheadFrames']==0 and settings['Emulation']['EmulationSpeed']==100
 env=dict(emulator=str(isolated/'Mesen.exe'),emulator_sha256=sha(isolated/'Mesen.exe'),core_sha256=sha(isolated/'MesenCore.dll'),worker_settings_sha256=sha(isolated/'settings.json'),user_settings_context_sha256=sha(Path('C:/Mesen2/settings.json')),Nes=settings['Nes'],Emulation=settings['Emulation'],actual_command_overrides=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
 put(a.output/'environment.json',env)
 seed=dict(lane='B',acquisition=False,numeric_mode=1,owner=2,boundary='Actual cold-selected Hard Samus GameLoop entry/task3/engine8',case_count=8,subphase_count=sum(len(q['tasks'])for q in plans),seeds=['Complete logical+visible two-page arena/floor/question block where declared; player position/velocity/fractions/facing/input history and complete actor pools/drops initialized.','PlayerStatus and native owned flags are explicit controlled legal-state seeds, not item pickups. No raw mode/RNG/contact-outcome/damage writes; the complete actor seed initializes native uncached health0, then real owners alone change health.','Missile stock2/0 per subphase; empty/refusal has clean drops. Actual funded InventorySpend debit-to0 witness required.','Complete GetPlayerColors-generated packet seeds initial visual palette; actual NMI consumes it. It is not counted as acquired/native palette producer execution.','Complete native Goomba targets aligned to actual emitted effect/spin; post-InitShortFirebar state exact source fields. Single hurt hazard retired only after observed native injury, with real injury outcome/recovery untouched.'],native_required=['Actual fresh input/selection, source emission/cost/contact/freeze/expiry/landing/hurt recovery and source art admission.','All original guard fields/caps plus complete raw PPU and actual256DMA timing.'],CPU_only_negatives=['Screw missing-spin/owned/ground/Bowser exclusion; native spin+ordinary Goomba contact runs bothfacings.','Missile Morph refusal and source refill2/cap20; no extra native Morph/missile subprofile.','Ice Lakitu/Bowser resistance remains source rule, not natively qualified by this eight-case first gallery.'],limits=['No acquisition/physical rise/transform/Hard random pool/BALANCE/new characters/campaign/waveform/global60Hz/no-flicker claim.','Varia existing suitless third-form policy differs from pinned2.02 palettes and remains explicit.','Original 8-case source plan is unchanged; the native-vs-CPU subphase map here narrows which controls can be claimed from a future run.'])
 put(a.output/'seed-policy.json',seed)
 report=ROOT/'docs/qa/final-samus-hard-gallery-prepared-v2-2026-10-26.txt'
 report.write_text('Samus Hard eight-case native preparation\n26 October 2026. No native launch or grant.\n\nExact target '+SHA+'\nFrozen source/ROM/debug: '+str(PARENT)+'\nNative-ready output: '+str(a.output)+'\n\nEight B cases /'+str(seed['subphase_count'])+' finite subphases: Short, Long, Morph/bombs, Missile Special, Ice, Wave, Varia, Screw. Actual numeric Hard1 cold-menu readback is mandatory. Easy three tiers and historical receipts stay separate. Native controlled seeds do not prove acquisition.\n\nThe frozen source plan contributes27 full gateway cases/229 complete actual CPU calls. This preparation adds'+str(cpu['cases'])+' actual CPU cases: complete GetPlayerColors packets for8 legal starting records, real emitted Ice contact/thaw360 and second-hit freeze removal, independent3-bomb refusal/expiry, plus6 complete PlayerGfxHandler/DrawAll renderer gateways. No mechanics stubs or emulator are used.\n\nFull Lua5.4 startup,24 actual input probes,32 finalizer positive/negative models,8 fixed-return order/nesting/PC/SP/bank models and13 strict physical-DMA models pass. All callbacks are installed before one final0..FFFF dispatcher; no runtime API registration. Source mock export is reverse-exact and is absent from the native script. Original IRQ31/NMI/A-C/5SMC/SP/APU guard text SHA6ab7cd71f41f441f4d4d752e2412f83c2b16da06b9e10d3cdf05180c63bf5fdf is literal unchanged.\n\nE005 is pre-transfer. Exact actual8-byte post-DMA protocol completes at E008 after the genuine LDA/before STA2001. Every raw256 source/hardware byte and actual2004 ordinal/mask precedes unchanged strict checks. Full actual PPU/index and per-event images are mandatory; art pointer/CHR agreement alone is not opaque-pixel visibility. Current legacy ChrPhysicalMap is explicitly used for Samus body epochs.\n\nComplete B setup at GameLoop entry initializes scene/floor/question cells, motion/fractions/previous input/facing, actor/pool/drop/resource state and one full compiled GetPlayerColors-derived palette packet. Buffer1 must first be genuinely empty; no queued producer is discarded. The packet is a declared visual initialization seed, not a claim that native acquisition invoked that producer. The complete actor setup initializes native uncached health0. There are no raw mode/RNG/contact-outcome writes or post-contact HP/damage forcing. Target Goombas are legal falling actors aligned to actual emitted source effects/body. Firebar state matches post-InitShortFirebar. The single hurt hazard retires only after real injury admission; actual injury drain/recovery remains native. See seed-policy.json for exact native-vs-CPU subphase scope.\n\nActual fresh-controller paused missile selection is separate from live Select missile Special. B remains beam. Missile stock2/0 is declared; actual one-unit debit-to0 plus separate clean refusal are mandatory, not indefinite zero after earned credits. Morph requires actual fresh Down/release/Down and exit; three independent bombs must refuse the fourth, boost, contact, emit body/explosion art/SFX and expire. Ice requires actual first nondamaging freeze, position STOP,360 committed decrements/thaw and second-hit break/damage. Wave must cross actual world pages, bypass query versus normal Long terrain and hit/expire. Varia must protect real firebar contacts yet ordinary contact and a noVaria firebar control must hurt/recover. Screw requires one actual protected body attack, bound flip-art emission, native sound request and landing cleanup.\n\nNegative Screw Bowser/no-spin/noownership/ground admission, missile Morph refusal and Ice resistant targets are source/CPU scope only, not extra native actors or campaign claims in this first gallery. Native both-facing subphases are specifically listed, not an exhaustive cross product. Varia keeps the existing suitless third-form policy difference from pinned2.02 palettes. Tiny HUD/body eight-sprite visibility, all acquisition/items/Hard random drops, full waveform/listening fidelity and universal timing remain open.\n\nStable one-shot command (requires a separate ROOT-grant.json tied to final ready hash):\npython -B tools/audit/final_samus_hard_gallery_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant\nNo retry, automatic other mode, settings/source/default/Git changes or worker reservation. Source-only draft generation attempts are retained separately and are not native failures.\n',encoding='utf-8')
 files={Path(q['path'])for q in json.loads((sourcepacket/'manifest.json').read_text())['bindings']};files.add(sourcepacket/'proof.json');files.add(Path('C:/Mesen2/settings.json'))
 files.add(report)
 files.update(q for q in a.output.rglob('*')if q.is_file())
 roots=[Path(__file__),ROOT/'tools/audit/final_samus_hard_gallery_run_v1.py'];seen=set()
 while roots:
  q=roots.pop()
  if q in seen:continue
  seen.add(q);files.add(q)
  for node in ast.walk(ast.parse(q.read_text(encoding='utf-8-sig'))):
   mods=[node.module]if isinstance(node,ast.ImportFrom)else[z.name for z in node.names]if isinstance(node,ast.Import)else[]
   for n in mods:
    if n:
     dep=ROOT/'tools/audit'/(n.split('.')[0]+'.py')
     if dep.is_file():roots.append(dep)
 for n in ['final_samus_hard_gallery_native_v1.lua','final_item_abilities_static_return_v1.lua','final_item_abilities_dma731_v1.lua','final_item_matrix_progressive.lua','final_item_abilities_pit731_ppu_v1.lua','final_item_abilities_failure.lua','final_item_abilities_native.lua']:files.add(ROOT/'tools/audit'/n)
 files.add(Path(sys.modules[LuaRuntime.__module__].__file__))
 files.add(Path(sys.modules['lupa'].__file__))
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(files,key=str)]))
 command='python -B tools/audit/final_samus_hard_gallery_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant'
 proof=dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,profile='samus-hard',mode_value=1,maximum_cases=8,maximum_launches=1,maximum_owned_workers=1,retry=False,source_plan_sha256=sha(sourcepacket/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),output=str(out),script_sha256=sha(out/'run.lua'),environment=env,source_controls_sha256=sha(a.output/'static-controls.json'),stable_command=command,source_freeze_sha256=sha(PARENT/'ROOT-source-readiness.json'),report_sha256=sha(report))
 put(a.output/'proof.json',proof);verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),script_sha256=sha(out/'run.lua'),stable_command=command),indent=2))

if __name__=='__main__':main()
