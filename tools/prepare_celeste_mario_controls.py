"""Actual reproduced-MG vs linked Celeste leaf CPU differential controls."""
from pathlib import Path
import argparse,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from verify_native_relocation import NesMPU
UP=Path('C:/Users/kando/Documents/ChatGPT/SNES Ports/upstream-nes')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

class NativeMemory(list):
    def __init__(self,raw):
        super().__init__([0]*65536);self.raw=raw;self.banks=[0,5,62,63]
        for w,b in enumerate(self.banks):self.page(w,b)
    def page(self,w,b):
        self.banks[w]=b;list.__setitem__(self,slice(0x8000+w*8192,0xa000+w*8192),self.raw[16+b*8192:16+(b+1)*8192])
    def __setitem__(self,a,v):
        if isinstance(a,int)and 0x5114<=a<=0x5117:self.page(a-0x5114,v&127)
        list.__setitem__(self,a,v)

class Native:
    def __init__(self):
        self.rom=ROOT/'build/celeste-native-reference.nes'
        if hasattr(Native,'_reference'):
            raw,self.s,self.post_start,self.post_stop=Native._reference
            self.m=NativeMemory(raw);return
        self.m=NativeMemory(self.rom.read_bytes());self.s={}
        for line in (ROOT/'build/celeste-native-reference.lst').read_text(errors='replace').splitlines():
            if z:=re.match(r'^([0-9A-F]{5})\s+([A-Za-z_][\w]*):',line):self.s[z[2]]=int(z[1],16)
        for fn in ['0000-07FF.65s','6000-7FFF.65s']:
            for name,value in re.findall(r'^\s*(\w+)\s*=\s*\$([0-9a-fA-F]+)\b',(UP/fn).read_text(errors='replace'),re.M):self.s[name]=int(value,16)
        self.s['SavedJoypad1Bits']=self.s['SavedJoypadBits']
        data=self.m.raw[16+5*8192:16+6*8192]
        self.post_start=0xa003+data.index(bytes([32])+self.s['PlayerMovementSubs'].to_bytes(2,'little'))
        self.post_stop=0xa000+data.index(bytes([32])+self.s['ScrollHandler'].to_bytes(2,'little'),self.post_start-0xa000)
        Native._reference=(self.m.raw,self.s,self.post_start,self.post_stop)
    def get(self,n):return self.m[self.s[n]]
    def put(self,**d):
        for n,v in d.items():self.m[self.s[n]]=v
    def call(self,n,bank=5,stop=None):
        address=self.s[n]
        if address<0xe000:self.m.page((address-0x8000)//8192,bank)
        c=NesMPU(memory=self.m,pc=address);c.sp=0xfd;c.stPushWord(0x5aff)
        for _ in range(100000):
            if c.pc==0x5b00 or(stop and c.pc==self.s[stop]):return c
            c.step()
        raise AssertionError(('Native timeout',n,hex(c.pc),self.m.banks))
    def caller_post_move(self):
        self.m.page(1,5);c=NesMPU(memory=self.m,pc=self.post_start);c.sp=0xfd
        for _ in range(5000):
            if c.pc==self.post_stop:return
            c.step()
        raise AssertionError(('Native caller continuation timeout',hex(c.pc)))

MAP={'PlayerXSpd':'Player_X_Speed','Player_X_MoveForce':'CmKernelXFrac','SprObject_X_MoveForce':'CmPosXFrac',
 'PlayerAnimTimerSet':'PlayerAnimTimerSet',
 'PlayerXPos':'Player_X_Position','PlayerXPage':'Player_PageLoc','PlayerYSpd':'Player_Y_Speed',
 'Player_X_Scroll':'Player_X_Scroll','CrouchingFlag':'CrouchingFlag',
 'Player_Y_MoveForce':'CmVelYFrac','Player_YMF_Dummy':'CmPosYFrac','PlayerYPos':'Player_Y_Position','PlayerYHi':'Player_Y_HighPos',
 'Player_XSpeedAbsolute':'Player_XSpeedAbsolute','Player_State':'CmState','PlayerFacingDir':'PlayerFacingDir',
 'PlayerDashTimer':'CmDashTimer','PlayerDashReadyTimer':'CmDashReady','PlayerDashDir':'CmDashDir',
 'CurDoubleJump':'CmDashStock','BInputTimer':'CmBBuffer','FireballIntervalTimer':'CmCooldown',
 'JumpInputTimer':'CmJumpBuffer','JumpLeniencyTimer':'CmCoyote','WallJumpLeniencyTimer':'CmWallGrace',
 'WallKickTimer':'CmWallKick','JumpIntervalTimer':'CmJumpInterval','JumpSwimTimer':'CmJumpTime',
 'Player_HP':'CmStaminaHi','Player_HPLo':'CmStaminaLo','SpeedBoosterSpeedAdder':'CmBoost','SpeedBoosterTimer':'CmRunMeter',
 'VerticalForce':'CmGravity','VerticalForceDown':'CmFallForce'}

def fresh(b,tier=0):
    n=Native();q=Arena(b,0)
    q.put(MarioVariant=4,NumberofLives=3,AreaType=1,AreaAddrsLOffset=5,WorldNumber=0,GamePauseStatus=0,TimerControl=0)
    q.invoke('CmInit');q.put(CmTier=tier,Player_X_Position=96,Player_PageLoc=1,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,PlayerFacingDir=1,Player_MovingDir=1,Player_CollisionBits=255)
    n.put(PlayerXPos=96,PlayerXPage=1,PlayerYPos=176,PlayerYHi=1,Player_State=0,PlayerFacingDir=1,Player_MovingDir=1,
      Player_CollisionBits=255,CurDoubleJump=1,MaxDoubleJump=1,PrevFrameDoubleJump=1,holdingenemyslot=255,ridingenemyslot=255,
      Player_MaxHP=2,Player_HP=2,Player_HPLo=99,DefaultFallingVForce=0x50,VerticalForceDown=0x50,VerticalForce=0x29,
      GameEngineSubroutine=8,PlayerSize=0,WallGrip_Acquired=2 if tier else 0,CelesteDash_Acquired=2 if tier>=2 else 0,
      AreaType=1,JumpIntervalTimer=0)
    return n,q

def step(n,q,pad,wall=0,floor=True):
    n.call('TimersAndPseudoRandomRoutine',0,'BackToNMI')
    q.put(TimerControl=n.get('TimerControl'))
    lr=pad&3;ud=pad&12
    if n.get('Player_State')==0 and ud&4 and lr:lr=ud=0
    n.put(SavedJoypadBits=pad,A_B_Buttons=pad&192,Left_Right_Buttons=lr,Up_Down_Buttons=ud)
    q.put(SavedJoypadBits=pad,A_B_Buttons=pad&192,Left_Right_Buttons=lr,Up_Down_Buttons=ud)
    n.call('PlayerAbilitySubs');n.call('PlayerMovementSubs');n.caller_post_move()
    q.invoke('CmMovement')
    # Typed flat support owns only the same post-motion native landing fields.
    # This does not claim complete native/host terrain geometry equivalence.
    if floor and n.get('PlayerYPos')>=176 and n.get('PlayerYSpd')<128:
        state=0
        if n.get('Player_State')==6 and(n.get('PlayerDashReadyTimer')or n.get('PlayerDashDir')<5):state=6
        n.put(PlayerYPos=176,Player_State=state,PlayerYSpd=0,Player_Y_MoveForce=0)
        q.put(Player_Y_Position=176,Player_State=0,Player_Y_Speed=0,CmVelYFrac=0)
    n.put(PlayerFootBlockPhysics=1 if n.get('WallKickTimer')else 0)
    if wall:
        n.put(Player_CollisionBits=255^wall)
        n.m[0x44]=wall;n.m[0x46]=0
        n.call('ContSChk',8,'ContSChk_SkipClinging')
    q.put(Player_CollisionBits=255^wall)
    q.invoke('CmAfterBG')
    n.call('ProcDash',10);q.invoke('CmWeapons')
    n.put(PreviousA_B_Buttons=pad&192)
    dif={name:[n.get(name),q.get(host)]for name,host in MAP.items()if n.get(name)!=q.get(host)}
    return dif

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    b=scoped_load(a.rom);rows=[]
    scripts=[('walk-release-reverse',[1]*110+[0]*12+[2]*110+[0]*12,0),
      ('jump-tap',[1]*5+[129]+[1]*55,0),('jump-hold',[129]*30+[1]*35,0),
      ('air-brake',[129]*8+[128]*20+[130]*20+[0]*20,0),
      ('run-meter-jump',[1]*125+[129]*27+[1]*40,0),
      ('crouch-release',[1]*30+[4]*20+[1]*30,0),
      ('dash-retarget',[65]+[10]*3+[9]*3+[1]*30,2)]
    scripts += [(f'dash-{direction}',[direction|64]+[direction]*30,2)for direction in [0,1,2,4,8,5,6,9,10]]
    scripts += [('dash-buffered-jump',[65]+[1]*4+[129]*24+[1]*30,2)]
    for name,inputs,tier in scripts:
        n,q=fresh(b,tier)
        for i,pad in enumerate(inputs):
            dif=step(n,q,pad)
            if dif:
                report=dict(passed=False,case=name,update=i+1,pad=pad,first_difference=dif,ROM_sha256=sha(a.rom))
                a.output.write_text(json.dumps(report,indent=2)+'\n');raise AssertionError(report)
        rows.append(dict(case=name,updates=len(inputs)))
    for name,y,state,inputs in [('native-air-water-A-buffer',96,2,[129]*12+[1]*8+[129]*12+[0]*20),
      ('native-water-surface',18,2,[129]*8+[1]*20+[0]*20),
      ('native-ground-water-launch',176,0,[129]*8+[1]*20+[0]*20)]:
        n,q=fresh(b,2)
        n.put(SwimmingFlag=1,AreaType=0,Player_State=state,PlayerYPos=y,PlayerYSpd=1)
        q.put(SwimmingFlag=1,AreaType=0,Player_State=state,CmState=state,Player_Y_Position=y,Player_Y_Speed=1)
        q.invoke('CmEnsure') # genuine loaded-scene reset precedes typed swim entry
        q.put(CmTier=2,Player_State=state,CmState=state,Player_Y_Position=y,Player_Y_Speed=1)
        for i,pad in enumerate(inputs):
            dif=step(n,q,pad,floor=False)
            if dif:
                report=dict(passed=False,case=name,update=i+1,pad=pad,first_difference=dif,ROM_sha256=sha(a.rom))
                a.output.write_text(json.dumps(report,indent=2)+'\n');raise AssertionError(report)
        rows.append(dict(case=name,updates=len(inputs)))
    n,q=fresh(b);n.put(EnemyStompVerticalForce=0x80)
    n.call('SBnce',0);q.invoke('CmBounce')
    stomp={k:[n.get(k),q.get(MAP[k])]for k in ['PlayerYSpd','Player_Y_MoveForce','VerticalForce','VerticalForceDown','JumpSwimTimer','Player_State']if n.get(k)!=q.get(MAP[k])}
    assert not stomp,stomp
    rows.append(dict(case='native-stomp-default',updates=1))
    for side in (1,2):
        for name,inputs,stam in [('wall-stamina',[8|side]*305,(2,99)),
          ('wall-jump-up',[128|8|side]+[side]*45,(2,99)),
          ('wall-jump-away',[128|(side^3)]+[side^3]*45,(2,99)),
          ('wall-jump-clamp',[128|8|side]+[side]*45,(0,20))]:
            n,q=fresh(b,1)
            n.put(Player_State=2,PlayerYPos=80,PlayerYSpd=1,Player_HP=stam[0],Player_HPLo=stam[1],
              WallJumpLeniencyTimer=10,SideCollisionSide=side,PlayerFacingDir=side,Player_MovingDir=side)
            q.put(Player_State=2,CmState=2,Player_Y_Position=80,Player_Y_Speed=1,CmStaminaHi=stam[0],CmStaminaLo=stam[1],
              CmWallGrace=10,CmWallSide=side,PlayerFacingDir=side,Player_MovingDir=side)
            for i,pad in enumerate(inputs):
                dif=step(n,q,pad,wall=side if name=='wall-stamina' else 0,floor=False)
                if dif:
                    report=dict(passed=False,case=name,side=side,update=i+1,pad=pad,first_difference=dif,ROM_sha256=sha(a.rom))
                    a.output.write_text(json.dumps(report,indent=2)+'\n');raise AssertionError(report)
            rows.append(dict(case=name,side=side,updates=len(inputs),stamina_initial=list(stam)))
    for name,y,vy,coyote,inputs in [('coyote',80,1,5,[1]*2+[129]*25+[1]*20),
      ('buffered-landing',168,3,0,[129]+[1]*40)]:
        n,q=fresh(b);n.put(Player_State=2,PlayerYPos=y,PlayerYSpd=vy,JumpLeniencyTimer=coyote)
        q.put(Player_State=2,CmState=2,Player_Y_Position=y,Player_Y_Speed=vy,CmCoyote=coyote)
        for i,pad in enumerate(inputs):
            dif=step(n,q,pad,floor=name=='buffered-landing')
            if dif:
                report=dict(passed=False,case=name,update=i+1,pad=pad,first_difference=dif,ROM_sha256=sha(a.rom))
                a.output.write_text(json.dumps(report,indent=2)+'\n');raise AssertionError(report)
        rows.append(dict(case=name,updates=len(inputs)))
    proof=dict(passed=True,native_run=False,ROM_sha256=sha(a.rom),original_ROM_sha256=sha(ROOT/'build/celeste-native-reference.nes'),cases=rows,
      scope='Actual assembled original timers/PlayerAbilitySubs/PlayerMovementSubs/ProcDash versus linked leaf; typed normal flat support adapter.',
      limits=['No native PPU/camera/whole host GameLoop qualification.','No shell/grapple/other-RPG abilities/slopes; dedicated admitted Celeste mode only.'],
      bindings=[dict(path=str(f),sha256=sha(f))for f in [Path(__file__),a.rom,a.rom.with_suffix('.dbg'),ROOT/'build/celeste-native-reference.nes',
        ROOT/'build/celeste-native-reference.lst',UP/'0000-07FF.65s',UP/'6000-7FFF.65s']])
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(rows),updates=sum(q['updates']for q in rows))))
if __name__=='__main__':main()
