"""Profile Water Shield on the real populated1-1, with journaled initial equipment."""
from pathlib import Path
import collections,hashlib,importlib.util,json,statistics,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-water-live-profile-hb'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
FIXTURE=r'''local char=__CHARACTER_ID__
local frame=0
local writes=assert(io.open(OUTPUT..'authored-setup.csv','w'))
writes:write('frame,address,value,memType\n')
local rawWrite=emu.write
function emu.write(a,v,t)
 writes:write(table.concat({frame,a,v,t},',')..'\n');writes:flush()
 return rawWrite(a,v,t)
end
dofile(__BOOTSTRAP_PATH__)
ROSTER_CONFIG={out=OUTPUT,character=char}
ORDINARY_PROFILE=__PROFILE_CONFIG__
dofile(__PROFILER_PATH__)
local f=assert(io.open(OUTPUT..'populated-frame.csv','w'))
f:write('frame,world,level,engine,x,y,power,selected,water,visible,expand,radius,enemies,lag,actualDMA\n')
local dma,expandStart=0,nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
emu.addMemoryCallback(function()dma=dma+1 end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 local choose=char==1 and frame==80 or char==9 and(frame==100 or frame==120 or frame==140)
 local enemies,visible=0,0
 for i=0,5 do
 local flag,kind,state=r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i)
 if flag>0 and flag<128 and state&32==0 and(kind<0x15 or kind==0x2d or kind==0x33)and(kind~=6 or state<2)and r('EnemyOffscrBitsMasked',i)==0 then enemies=enemies+1 end
end
 for i=0,9 do if r('RgShotType',i)==17 and r('SsHidden',i)==0 then visible=visible+1 end end
 if frame>=730 and enemies>0 and visible==8 and not expandStart then expandStart=frame end
 emu.setInput({right=choose or frame>=730 and not expandStart,down=char==9 and frame==80,start=frame==200,
  b=frame>=560 and frame<565 or expandStart and frame>=expandStart+8 and frame<expandStart+13},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  assert(r('SelectedCharacter')==char and r('CrossoverBehaviorVersion')==1,'Actual Hard shield user')
  assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('GameEngineSubroutine')==8,'Real initial1-1 world')
  w('PlayerStatus',1);w('InvOwnedLo',129,char);w('InvOwnedHi',0,char)
  w('InvSelected',7,char);w('InvAmmo',112,char*16+7);w('InvDirty',1)
 end
 if frame>=550 then
  local water,visible,enemies=0,0,0
  for i=0,9 do if r('RgShotType',i)==17 then water=water+1;if r('SsHidden',i)==0 then visible=visible+1 end end end
  for i=0,5 do
 local flag,kind,state=r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i)
 if flag>0 and flag<128 and state&32==0 and(kind<0x15 or kind==0x2d or kind==0x33)and(kind~=6 or state<2)and r('EnemyOffscrBitsMasked',i)==0 then enemies=enemies+1 end
end
  f:write(table.concat({frame,r('WorldNumber'),r('LevelNumber'),r('GameEngineSubroutine'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('PlayerStatus'),r('InvSelected',char),water,visible,r('SsWaterExpand'),r('SsWaterRadius'),enemies,r('NmiDisable')>=128 and1 or0,dma},',')..'\n');f:flush()
 end
 dma=0
 if frame==1500 then writes:close();f:close();print('POPULATED_WATER_DIAGNOSTIC_COMPLETE');emu.stop(0)end
end,emu.eventType.endFrame)
'''.replace('and1','and 1').replace('or0','or 0')
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 private=V/'root49-lag-combined-i';assert sha(private/'build-review.json')=='55c241370c34437410747a9762d3a11c4c7f52bb5d50e1e45a067360cff9ddbe'
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('populated_gq_image',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
 original=V/'root49-current-f-samus-exclusive-profile-bj/profile-actual-ram-return.lua';assert sha(original)=='69876d2888b8461512b4129537fa4f30919dc09d2a9bdab0437be9a1a24c47b5'
 text=original.read_text(encoding='utf-8')
 anchor='local function snapshot()';assert text.count(anchor)==1
 insert="""local function counts()
 local water,visible,enemies=0,0,0
 for i=0,9 do if r('RgShotType',i)==17 then water=water+1;if r('SsHidden',i)==0 then visible=visible+1 end end end
 for i=0,5 do
 local flag,kind,state=r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i)
 if flag>0 and flag<128 and state&32==0 and(kind<0x15 or kind==0x2d or kind==0x33)and(kind~=6 or state<2)and r('EnemyOffscrBitsMasked',i)==0 then enemies=enemies+1 end
end
 return water,visible,enemies
end
"""
 text=text.replace(anchor,insert+anchor)
 text=text.replace("local s=emu.getState()\n return {frame=frame", "local s=emu.getState();local water,visible,enemies=counts()\n return {water=water,visible=visible,enemies=enemies,expand=r('SsWaterExpand'),radius=r('SsWaterRadius'),frame=frame")
 text=text.replace("local t={name=string.format('%q',q.name)","local t={water=q.entry.water,visible=q.entry.visible,enemies=q.entry.enemies,expand=q.entry.expand,radius=q.entry.radius,name=string.format('%q',q.name)")
 profiler=J/'profile.lua';profiler.write_text(text,encoding='utf-8');base=J/'noop.lua';base.write_text('return function()return{}end\n',encoding='utf-8')
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+250000000<100000000000
 preparation=dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),private_I_build_review_sha256=sha(private/'build-review.json'),profiler_original_sha256=sha(original),profiler_sha256=sha(profiler),helper_sha256=sha(helper),workspace_before=used,phase_cap=250000000,reserve=50000000,global_cap=100000000000,predecessor_GQ_sha256='a9bcb2d32bfb4ef4fd26e5a15768f421132189cab6998fcc9f4462f9b12bad94',preparer_sha256=sha(R/'tools/audit/prepare_roster49_water_live_hb.py'),scope='Authored equipment only at550 plus explicitHard bootstrap60; all emulator writes journaled. Player/world/terrain/actors are natural unmodified1-1. Real public menu/buttons, orbit maturation before movement, halt at first real native-eligible enemy then actualB expansion; strict enemy admission includes offscreen/goomba/bowser/bullet kinds. Diagnostic live populated scenes; not natural item acquisition, route completion, source-perfect behavior or universal FPS proof. Native scope times subtract real IRQ/NMI and are nested, not additive independent shares.')
 (J/'preparation.json').write_text(json.dumps(preparation,indent=2)+'\n',encoding='utf-8')
 assert sha(V/'root49-water-enemy-filter-gy/build-review-ha.json')=='6eedbf9da2b36e9c77fae68200d63b4308c611af1511becb0bf6a197900144d6'
 groups=[]
 for revision in ['H','I','J']:
  for mapper in ['mmc3','mmc5']:
   rom=(cp.parent if revision=='H'else private/'source/build'if revision=='I'else V/'root49-water-enemy-filter-gy/source/build')/f'smb-crossover-{mapper}.nes';image=im.Image(rom)
   specs={'GameLoop':('GameLoop',None),'SpecialWeapons':('SpecialWeapons',None),'Orbit':('Orbit','SpecialWeapons'),'WaterCollisionCandidate':('WaterCollisionCandidate','SpecialWeapons'),'Bridge':('Bridge','SpecialWeapons'),'EnsureWaterScale':('EnsureWaterScale','SpecialWeapons'),'SpecialDrawShots':('SpecialDrawShots',None),'SpecialDrawWaterShot':('SpecialDrawWaterShot',None),'WeaponEnemies':('Enemies','MegaManWeapons'),'WeaponBlocks':('Blocks','MegaManWeapons'),'AudioUpdate':('AudioUpdate',None)}
   hooks={n:image.hook(label,scope=scope)for n,(label,scope)in specs.items()};hooks.update(NMI=image.hook('NonMaskableInterrupt'),IRQ=image.hook('IrqScrollSplit'),NMI_END=image.hook('NonMaskableInterrupt',delta='last'),IRQ_END=image.hook('IrqScrollSplit',delta='last'))
   pc=image.ram['FarcallJmpTarget_SMC']+3;ret=image.hook('FarCallCommon',delta=pc-image.ram['FarCallCommon'])
   for char in [1,9]:
    assert workspace_bytes(J)+18000000+50000000<250000000
    assert workspace_bytes(R)+18000000<100000000000
    stem=f'{revision}-{mapper}-{char}';folder=J/stem;folder.mkdir();fixture=folder/'component.lua'
    profile=dict(hooks=hooks,ram=image.ram,ram_return=ret,start_frame=550,stop_frame=1450,base_policy=base.as_posix())
    replacements={'__CHARACTER_ID__':str(char),'__BOOTSTRAP_PATH__':im.lua((R/'tests/menu-bootstrap.lua').as_posix()),'__PROFILE_CONFIG__':im.lua(profile),'__PROFILER_PATH__':im.lua(profiler.as_posix())}
    fixture_text=FIXTURE
    for token,value in replacements.items():
     assert fixture_text.count(token)==1,token
     fixture_text=fixture_text.replace(token,value)
    assert all(token not in fixture_text for token in replacements)
    assert 'ORDINARY_PROFILE=' in fixture_text
    fixture.write_text(fixture_text,encoding='utf-8')
    command=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder/'native'),str(fixture),str(rom),'--timeout','180']
    (folder/'binding.json').write_text(json.dumps(dict(ROM_sha256=sha(rom),fixture_sha256=sha(fixture),profile=profile,command=command),indent=2)+'\n',encoding='utf-8')
    with(folder/'host.log').open('wb')as log:q=subprocess.run(command,cwd=R,stdout=log,stderr=subprocess.STDOUT)
    group=dict(revision=revision,mapper=mapper,character=char,exit=q.returncode,ROM_sha256=sha(rom),scopes={},coverage={})
    p=folder/'native/ordinary-profile.jsonl'
    if p.exists():
     records=[json.loads(line)for line in p.read_text().splitlines()];bins=collections.defaultdict(list)
     for z in records:
      assert z['exclusive_cycles']>=0
      phase='expand'if z['expand']else'orbit';population='populated'if z['enemies']else'empty';shape='full8'if z['visible']==8 else'partial'
      bins[(z['name'],phase,population,shape)].append(z['exclusive_cycles'])
     for key,v in bins.items():group['scopes']['/'.join(key)]=dict(samples=len(v),average=statistics.mean(v),median=statistics.median(v),maximum=max(v))
     for phase in ['orbit','expand']:
      group['coverage'][phase]=len(bins.get(('SpecialWeapons',phase,'populated','full8'),[]))
    groups.append(group);(J/'partial.json').write_text(json.dumps(groups,indent=2)+'\n',encoding='utf-8');print(stem,q.returncode,group['coverage'],flush=True)
 (J/'review.json').write_text(json.dumps(dict(status='POPULATED_WATER_NATIVE_PROFILE_EVIDENCE_COVERAGE_REVIEW_REQUIRED',preparation_sha256=sha(J/'preparation.json'),groups=groups,goal_complete=False),indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
