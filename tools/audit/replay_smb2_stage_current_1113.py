"""Current SMB2/Doki ordinary-input full-stage coverage, stdout only."""
import argparse
from hashlib import sha256
import json

import replay_bowsers_current_1113 as Base

PIN=Base.PIN
NAMES=('SMB2 MARIO','SMB2 LUIGI','SMB2 TOAD','SMB2 PEACH','IMAJIN','LINA','PAPA','MAMA')


def once(text,before,after):
    assert text.count(before)==1,before
    return text.replace(before,after,1)


def controller(raw,variant,*,jump_hold=8,enemy_gap=72,source_edges=False,injury_trace=False,pit_trace=False,last_pit_settle=False,runup=False):
    assert 0<=variant<8 and jump_hold in (8,24) and enemy_gap in (48,72) and sha256(raw).hexdigest()==PIN
    text=Base.controller(raw,0)
    assert sha256(text.encode()).hexdigest()=='0be5c10a092f5214821a033b4bbf8e7028847febacc92abb8853ed77d3af0c46'
    b=dict(Base.W.Symbols.bundle(),raw=raw)
    for name,at in (('S2Variant',0x5fe3),('S2Health',0x5f98),('S2Ready',0x5f9b)):
        assert Base.W.address(b,name)==at,(name,'Actual linked state address')
    skipped=Base.W.address(b,'NmiSkipped')
    text=once(text,'local identity,expectedRom,gameOffset,attrs=0,',f'local identity,expectedRom,gameOffset,attrs={variant},')
    text=once(text,"health=work(0xbe29),ready=work(0xbe26)","health=read(0x5f98),ready=read(0x5f9b),variant=read(0x5fe3)")
    text=once(text,"identity=identity==0 and 'SMB3 BOWSER'or'SMB1 BOWSER'",'identity=smb2Names[identity+1],idle=smb2Idle')
    text=once(text,"r('SelectedCharacter')==27 and r('FmAlts')&8==identity*8,'Retain selected Bowser identity'",
        "r('SelectedCharacter')==25 and read(0x5fe3)==identity,'Retain selected SMB2/Doki identity'")
    text=once(text,"s.ready==183,'Original Bowser runtime remains live'","s.ready==178,'Original SMB2/Doki runtime remains live'")
    text=once(text,"'No Bowser death or life loss'","'No SMB2/Doki death or life loss'")
    text=once(text,"'Bowser clears non-shortcut1-1 then25 grounded quiet underground1-2 updates'",
        "'SMB2/Doki clears non-shortcut1-1 then25 grounded quiet underground1-2 updates'")
    if jump_hold!=8:
        text=once(text,'if jump then hold=7;a=true end',f'if jump then hold={jump_hold-1};a=true end')
    if enemy_gap!=72:
        text=once(text,'if gap>0 and gap<72 then jump=true end',f'if gap>0 and gap<{enemy_gap} then jump=true end')
    if source_edges:
        text=once(text,'elseif grounded and not lastA then','elseif grounded and read(0x5c4f)&128==0 then')
    text=once(text," if s.world==0 and s.level==0 and s.engine==4 and s.x>=3140 then flag=true end",f'''
 if updates==1 then
  smb2Idle.start=s;smb2Idle.start_skipped=read({skipped});pad=0;return
 elseif updates<=49 then
  assert(active()and s.x==smb2Idle.start.x and s.health>0,'Ordinary neutral opening stays alive and stationary')
  for slot=0,5 do assert(read(F.Enemy_Flag+slot)==0,'No actors in empty-scene idle window')end
  if updates==49 then
   smb2Idle.finish=s;smb2Idle.Main_updates=48
   smb2Idle.physical_frames=frames-smb2Idle.start.frame
   smb2Idle.skipped_NMI=(read({skipped})-smb2Idle.start_skipped)&255
  end
  pad=0;return
 end
 if s.world==0 and s.level==0 and s.engine==4 and s.x>=3140 then flag=true end''')
    text=once(text," for _=1,2 do press(1)end\n assert(r('CrossoverMenuIndex')==26 and r('SelectedCharacter')==27,'Actual grid reaches Bowser')\n if identity==1 then press(32)end\n assert(r('FmAlts')&8==identity*8,'Actual Select resolves Bowser alternate')",
        " assert(r('CrossoverMenuIndex')==24 and r('SelectedCharacter')==25,'Actual grid reaches SMB2')\n for _=1,identity do press(32)end\n assert(read(0x5fe3)==identity,'Actual Select resolves SMB2/Doki identity')")
    text='local smb2Names={'+','.join(json.dumps(name)for name in NAMES)+'}\nlocal smb2Idle={}\n'+text
    if last_pit_settle:
        text=once(text,'local smb2Idle={}',"local smb2Idle={}\nlocal smb2Gap={stage='approach',age=0}")
        text=once(text,'idle=smb2Idle','idle=smb2Idle,last_pit=smb2Gap')
        point=" assert(s.world==0 and s.level==0,'Expected ordinary1-1 before flagpole')"
        text=once(text,point,point+'''
 if smb2Gap.stage=='approach'and s.x>=2416 and s.x<2448 then
  smb2Gap.stage='settle';smb2Gap.entry=s;hold=0;lastA=false
 end
 if smb2Gap.stage=='settle'then
  smb2Gap.age=smb2Gap.age+1;assert(smb2Gap.age<120,'Settle naturally on the left final-pit stair')
  -- Original air inertia keeps moving under neutral input. Countersteer
  -- while airborne so the ordinary landing stays on the left stair.
  local velocity=read(0x5c20);if velocity>=128 then velocity=velocity-256 end
  if s.x>2420 then pad=2 elseif s.x<2412 then pad=1
  elseif velocity>0 then pad=2 elseif velocity<0 then pad=1 else pad=0 end
  if read(0x5c3f)==0 then pad=0 end
  if read(0x5c3f)==0 and read(0x5c4f)&128==0 and read(0x5c20)==0 then
   smb2Gap.stage='launch';smb2Gap.launch=s;smb2Gap.age=0;pad=129
  end
  return
 elseif smb2Gap.stage=='launch'then
  smb2Gap.age=smb2Gap.age+1;assert(smb2Gap.age<160,'Ordinary jump from left stair crosses final pit')
  pad=smb2Gap.age<24 and 129 or 1
  if s.x>=2496 and read(0x5c3f)==0 then
   smb2Gap.stage='complete';smb2Gap.landing=s;hold=0;lastA=false
  end
  return
 end''')
        if runup:
            text=once(text,"smb2Gap.stage='launch';smb2Gap.launch=s;smb2Gap.age=0;pad=129",
                "smb2Gap.stage='runup';smb2Gap.runup=s;smb2Gap.age=0;pad=1")
            text=once(text," elseif smb2Gap.stage=='launch'then",''' elseif smb2Gap.stage=='runup'then
  smb2Gap.age=smb2Gap.age+1;assert(smb2Gap.age<90,'Ordinary runup stays on the left stair')
  pad=1
  if s.x>=2434 and read(0x5c3f)==0 and read(0x5c4f)&128==0 then
   smb2Gap.stage='launch';smb2Gap.launch=s;smb2Gap.age=0;pad=129
  end
  return
 elseif smb2Gap.stage=='launch'then''')
    if pit_trace:
        text=once(text,'local smb2Idle={}','local smb2Idle={}\nlocal smb2PitTrace={}\nlocal smb2PitCount=0')
        text=once(text,'idle=smb2Idle','idle=smb2Idle,pit_observations=smb2PitTrace')
        text=once(text,' local s=state()',''' local s=state()
 if s.x>=2350 and s.x<=2490 and updates%3==0 and smb2PitCount<64 then
  smb2PitCount=smb2PitCount+1
  local q=state();q.sourceAir=read(0x5c3f);q.sourceVY=read(0x5c2a);q.sourceHeld=read(0x5c4f);q.sourceFresh=read(0x5c4e);q.sourceYPage=read(0x5c1a)
  q.plannedA=lastA;q.plannedHold=hold;q.timerControl=read(0x074a);q.pad=pad
  q.ahead16=tile(s.x+16,math.min(232,s.y+32));q.ahead24=tile(s.x+24,math.min(232,s.y+40));q.below=tile(s.x+8,math.min(232,s.y+32))
  smb2PitTrace[tostring(smb2PitCount)]=q
 end''')
    if injury_trace:
        pc=Base.W.address(b,'S2InjuryStart');at=Base.W.location(b,'S2InjuryStart')-16
        object_offset=Base.W.address(b,'ObjectOffset')
        text=once(text,'local smb2Idle={}','local smb2Idle={}\nlocal smb2Injuries={}\nlocal smb2InjuryCount=0')
        text=once(text,'idle=smb2Idle','idle=smb2Idle,injury_entries=smb2Injuries')
        text+=f'''
emu.addMemoryCallback(guard(function()
 local where=emu.convertAddress({pc})
 if not game or r('SelectedCharacter')~=25 or not where or where.memType~=emu.memType.nesPrgRom or where.address~={at} then return end
 assert(smb2InjuryCount<8,'Bounded original injury entry observations')
 smb2InjuryCount=smb2InjuryCount+1
 local q=state();q.slot=read({object_offset});q.sourceY=read(0x5c0a);q.sourceAir=read(0x5c3f);q.sourceVY=read(0x5c2a);q.actors={{}}
 for slot=0,5 do
  if read(F.Enemy_Flag+slot)~=0 then
   q.actors[tostring(slot)]={{id=read(F.Enemy_ID+slot),flag=read(F.Enemy_Flag+slot),state=read(F.Enemy_State+slot),x=read(F.Enemy_X_Position+slot)+256*read(F.Enemy_PageLoc+slot),y=read({Base.W.address(b,'Enemy_Y_Position')}+slot)}}
  end
 end
 smb2Injuries[tostring(smb2InjuryCount)]=q
end),emu.callbackType.exec,{pc})
'''
    Base.LuaRuntime().compile(text)
    assert not any(word in text for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return text


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant',type=int,choices=range(8),default=4)
    p.add_argument('--metadata',action='store_true')
    p.add_argument('--jump-hold',type=int,choices=(8,24),default=8)
    p.add_argument('--injury-trace',action='store_true')
    p.add_argument('--enemy-gap',type=int,choices=(48,72),default=72)
    p.add_argument('--source-edges',action='store_true',help='Wait until the real source held-A bit is released before another jump.')
    p.add_argument('--pit-trace',action='store_true',help='Bounded read-only third-pit observations in the receipt, no files.')
    p.add_argument('--last-pit-settle',action='store_true',help='Land on the last left stair before making the ordinary pit jump.')
    p.add_argument('--runup',action='store_true',help='After landing, run to the actual left stair edge before the pit jump.')
    args=p.parse_args()
    assert Base.check(Base.ROM)['ROM_sha256']==PIN
    text=controller(Base.ROM.read_bytes(),args.variant,jump_hold=args.jump_hold,enemy_gap=args.enemy_gap,source_edges=args.source_edges,injury_trace=args.injury_trace,pit_trace=args.pit_trace,last_pit_settle=args.last_pit_settle,runup=args.runup)
    summary=dict(ROM_SHA256=PIN,identity=NAMES[args.variant],jump_hold=args.jump_hold,enemy_gap=args.enemy_gap,source_edges=args.source_edges,script_SHA256=sha256(text.encode()).hexdigest(),native_run=not args.metadata)
    if not args.metadata:
        script=Base.OUT/'controller.lua';script.write_text(text,encoding='utf-8',newline='\n')
        q=Base.run(script,Base.ROM,Base.OUT/'capture',PIN,240)
        summary.update(passed=q['passed'],receipt_SHA256=q['receipt_SHA256'],receipt=q['receipt'],outputs_written=q['outputs_written'])
        print(json.dumps(summary,separators=(',',':')),flush=True)
        assert Base.check(Base.ROM)['ROM_sha256']==PIN
        assert q['passed'],'SMB2/Doki full-stage qualification failed'
    else:print(json.dumps(summary,separators=(',',':')),flush=True)


if __name__=='__main__':main()
