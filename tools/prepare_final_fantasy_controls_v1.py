"""Sparse compiled FF component controls; no native emulator/shared build.

Execute real6502 leaf code and pinned genuine host CHR publisher/draw loop.
No NMI/PPU timing, campaign, live selection or source Flash bytecode equality.
"""
from pathlib import Path
import json,re,subprocess,hashlib,itertools,math,sys
from fractions import Fraction
from PIL import Image
from py65.devices.mpu6502 import MPU
from prepare_rogue_dawn_art_v1 import Memory,call
from prepare_final_fantasy_component_v1 import ROOT,OUT,bind,sha
from prepare_final_fantasy_component_v1 import BODY,PURPLE
sys.path.insert(0,str(ROOT/'tools/audit'))
from verify_native_relocation import NesMPU
HOST=ROOT/'build/sunny-integrated-final'
EXPECTED={'nes':'55e874822160c3ab20f9ccfbca8b46cfe3b71c00bc4466a9fa8c5789bf7c0217',
          'dbg':'db5d78ec8114f76c3b8e5e9eebddf060d7cdc40a510009cde0b2c79d651c66fb',
          'lbl':'e49ca54fa7920bb9ce333b0bf8d8900d2c5357d2323dc52a0e7c2d1f28ef3afd'}
RAM='''SelectedCharacter NumberofLives AreaType AreaAddrsLOffset WorldNumber SavedJoypadBits
 Player_State PlayerStatus PlayerSize CrouchingFlag RgCrouch MmSliding SmBall MmOnVine MmUnderwater
 MmFrictionYActive MmOldX MmVX MmVY MmXFraction MmYFraction InjuryTimer Player_X_Position
 Player_PageLoc Player_Y_Position Player_Y_HighPos Player_Y_Speed PlayerFacingDir SwimmingFlag
 Player_X_Scroll Player_X_Speed Player_XSpeedAbsolute Square1SoundQueue Square2SoundQueue
 MmDeathFlag MmDeathAge TimerControl GamePauseStatus GameEngineSubroutine CrossoverBehaviorVersion
 KillPlayer BlockBufferColli_Head BlockBufferColli_Side Player_Rel_XPos Player_Pos_ForScroll SmPosePtr SmChrBank
 ObjectMetasprite Player_SprAttrib PlayerOutlinesOff R0 R1 R2 R3 R4 R5 R6 R7 CurrentBankC
 X5SetPhysicalChr CurrentCHRBank X5ChrMode ReloadCHRBank X5WideChrActive
 MetaspriteRenderLoop CurrentOAMOffset GuestOamRotationActive RgOamRotation ScreenLeft_X_Pos ScreenLeft_PageLoc
 CurrentBank IrqScrollSplit IrqNewScroll IrqPPUCTRL NextBank_SMC SafecallA_SMC SafereturnA_SMC FarcallJmpTarget_SMC
'''.split()
def labels(path):
    out={}
    for line in path.read_text().splitlines():
        m=re.match(r'al ([0-9A-Fa-f]+) \.(\S+)',line)
        if m:out[m[2]]=int(m[1],16)
    return out
def build():
    for ext,h in EXPECTED.items():assert sha(HOST.with_suffix('.'+ext).read_bytes())==h
    s=labels(HOST.with_suffix('.lbl'));dbg=HOST.with_suffix('.dbg').read_text()
    constants={}
    for name in ['A_Button','B_Button','Up_Dir','Down_Dir','Sfx_BigJump','Sfx_Fireball',
                 'Sfx_PowerUpGrab','Sfx_PipeDown_Injury','METASPRITE_SAMUS_BODY']:
        m=re.search(r'^sym[^\n]*name="'+name+r'"[^\n]*val=0x([0-9A-Fa-f]+)',dbg,re.M)
        assert m,name
        constants[name]=int(m[1],16)
    mmc=(ROOT/'src/mmc5.s').read_text()
    macros='\n'.join(re.search(r'\.macro '+n+r'\b[\s\S]*?\.endmacro',mmc)[0]for n in ['BankPRGC','_BANK_INNER'])
    pre='\n'.join(f'{n}=${s[n]:04x}'for n in RAM)+'\n'+ '\n'.join(f'{n}=${v:x}'for n,v in constants.items())
    pre+='\n.macpack longbranch\nENABLE_CROSSOVER=1\nMMC5_PRG_ROM=$80\nMMC5_PRG_BANK_C=$5116\nFF_FIRST_CHR=756\n'+macros+'\n'
    (OUT/'component.s').write_text(pre+'.include "final_fantasy.s"\n')
    (OUT/'component.cfg').write_text('MEMORY { K:start=$AA00,size=$1600,bank=62,file=%O; A:start=$D000,size=$1000,bank=93,file="'+str((OUT/'art.bin').resolve()).replace('\\','/')+'"; C:start=$BD000,size=$8000,file="'+str((OUT/'chr.bin').resolve()).replace('\\','/')+'"; }\nSEGMENTS { FINAL_FANTASY_CORE:load=K,type=ro; FINAL_FANTASY_ART:load=A,type=ro; FINAL_FANTASY_CHR:load=C,type=ro; }\n')
    cc=ROOT/'tools/Windows/cc65/bin'
    subprocess.run([str(cc/'ca65.exe'),'-g','-I',str(ROOT/'src'),str(OUT/'component.s'),'-o',str(OUT/'component.o')],check=True)
    subprocess.run([str(cc/'ld65.exe'),'-C',str(OUT/'component.cfg'),'-o',str(OUT/'component.bin'),'-Ln',str(OUT/'component.lbl'),
                    '--dbgfile',str(OUT/'component.dbg'),str(OUT/'component.o')],check=True)
    s.update(labels(OUT/'component.lbl'));s.update(constants)
    return (OUT/'component.bin').read_bytes(),(OUT/'art.bin').read_bytes(),s
def memory(code,data,s):
    m=Memory(bytes(65536));rom=HOST.with_suffix('.nes').read_bytes()
    m[0x8000:0xa000]=rom[16+126*8192:16+127*8192]
    m[0xa000:0xc000]=rom[16+62*8192:16+63*8192]
    m[0xc000:0xe000]=rom[16+93*8192:16+94*8192]
    m[0xe000:]=rom[16+127*8192:16+128*8192]
    m[0xaa00:0xaa00+len(code)]=code;m[0xd000:0xd000+len(data)]=data
    for n,v in dict(SelectedCharacter=22,NumberofLives=2,AreaType=1,AreaAddrsLOffset=0,WorldNumber=0,
                    Player_Y_Position=160,Player_Y_HighPos=1,Player_X_Position=120,Player_PageLoc=0,
                    PlayerFacingDir=1,PlayerOutlinesOff=1,GameEngineSubroutine=8).items():m[s[n]]=v
    return m
def invoke(m,s,name,**kw):return call(m,s[name],**kw)
def setv(m,s,**kw):
    for n,v in kw.items():m[s[n]]=v
def v(m,s,n):return m[s[n]]
def s16(n):return n-65536 if n&32768 else n
def velocity(m,s,name):return s16(m[s[name]+1]|m[s[name]+2]<<8)
def art_records(data):
    # Actual link addresses are read from exported lookup tables in tests below.
    return json.loads((OUT/'assets.json').read_text())
def source_pixels(fact,face,shadow):
    if fact['kind']=='body':
        im=Image.open(ROOT/'chr/characters/final-fantasy-prototype-poses.png').convert('RGBA')
        n=fact['source'];x=(n['source_frame']-1)*48;y=(n['variant']*2+n['tier'])*48
        im=im.crop((x,y,x+48,y+48));colors=BODY[n['variant']]
    else:
        im=Image.open(ROOT/'reference/crossover2/images/39.png').convert('RGBA')
        x,y,w,h=fact['source']['rect'];im=im.crop((x,y,x+w,y+h))
        colors={'fire':[(216,40,0),(252,116,96),(252,252,252)],
                'ice':[(0,90,255),(63,191,255),(255,255,255)],
                'bolt':[(175,127,0),(248,184,0),(255,255,255)]}[fact['kind']]
    result={};cyan=[(0,66,90),(0,140,140),(0,239,222)]
    for y in range(im.height):
        for x in range(im.width):
            rgba=im.getpixel((x,y));rgb=rgba[:3]
            if not rgba[3]or rgb==PURPLE:continue
            if rgb==(0,0,0):
                if shadow:continue
                value,palette=1,3
            elif rgb in cyan:value,palette=cyan.index(rgb)+1,2
            else:
                rgb=(63,191,255)if rgb==(60,188,252)else rgb
                rgb=(240,208,176)if rgb==(255,192,128)else rgb
                value=colors.index(rgb)+1;palette={'body':0,'fire':1,'ice':2,'bolt':2}[fact['kind']]
            px=x-16 if fact['kind']=='body'else x-im.width//2
            py=y-12 if fact['kind']=='body'else y-im.height//2
            if face==2:px=(15-px)if fact['kind']=='body'else(-1-px)
            result[px,py]=(value,palette)
    return result
def pattern_pixels(chrdata,page,parts):
    result={}
    for t,attr,x,y in parts:
        start=page*1024+(t&63)//2*32
        for yy in range(16):
            for xx in range(8):
                sy=15-yy if attr&128 else yy;sx=7-xx if attr&64 else xx
                a=start+(sy//8)*16+sy%8
                value=(chrdata[a]>>(7-sx)&1)|((chrdata[a+8]>>(7-sx)&1)<<1)
                if value:result[x+xx,y+yy+1]=(value,attr&3)
    return result
def actual_host_draw(m,s,code,offset):
    # Genuine bank4 render path. No synthetic implementation, NMI or PPU.
    rom=HOST.with_suffix('.nes').read_bytes();saved=bytes(m[0xa000:0xc000])
    m[0xa000:0xc000]=rom[16+4*8192:16+5*8192]
    setv(m,s,CurrentOAMOffset=0,GuestOamRotationActive=0,RgOamRotation=0,
         R0=s['FfRenderBuffer']&255,R1=s['FfRenderBuffer']>>8,R3=0,R4=128,R5=0,
         R6=(128+offset)&255,R7=1+(128+offset)//256)
    c=invoke(m,s,'MetaspriteRenderLoop')
    oam=[tuple(m[i:i+4])for i in range(0x200,0x200+v(m,s,'CurrentOAMOffset'),4)]
    m[0xa000:0xc000]=saved
    return oam,c.processorCycles
def run_trace(m,pc,inject=None,**kw):
    c=NesMPU(memory=m,pc=pc);c.a=kw.get('a',0);c.x=kw.get('x',0);c.y=kw.get('y',0);c.p=kw.get('p',0x30);c.sp=253
    c.stPushWord(0x5aff);trace=[];done=False
    for _ in range(30000):
        if c.pc==0x5b00:
            assert c.sp==253
            return c,trace
        if c.pc==inject and not done:
            saved=(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp);live=bytes(m[0x101+c.sp:0x200]);c.irq();done=True
            for _ in range(300):
                c.step()
                if c.pc==saved[0]:break
            assert (c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp)==saved,('IRQ context',saved,c.pc)
            assert bytes(m[0x101+c.sp:0x200])==live,'Live caller stack'
        trace.append(c.pc);assert m[c.pc]!=0,('BRK',hex(c.pc));c.step()
    raise AssertionError(('No leaf return',hex(c.pc)))
def main():
    proof=dict(passed=False,native=False,host_integration=False)
    try:
        code,data,s=build();rom=HOST.with_suffix('.nes').read_bytes()
        assert len(code)<=5632 and len(data)<=4096
        assert set(rom[16+62*8192+0xa00:16+63*8192])=={255},'Pinned CORE tail'
        assert set(rom[16+93*8192+0x1000:16+94*8192])=={255},'Pinned ART tail'
        assert set(rom[16+1048576+756*1024:16+1048576+788*1024])=={0},'Pinned CHR reservation bytes'
        # Persistent initialization, life gain/wrap, loss, and area reset isolation.
        life=0
        for variant,power,old,new,area in itertools.product(range(4),range(3),[0,1,2,127,255],[0,1,2,3,128,255],[0,1]):
            m=memory(code,data,s);setv(m,s,FfVariant=variant);invoke(m,s,'FfEnsure')
            setv(m,s,FfPower=power,FfEarned=2,FfHealCharges=3,FfLife=old,NumberofLives=new,AreaAddrsLOffset=area)
            m[0x5c70]=77;before=bytes(m)
            invoke(m,s,'FfEnsure');loss=((new-old)&255)>=128
            assert v(m,s,'FfPower')==(0 if loss else power)
            assert v(m,s,'FfVariant')==variant and m[0x5fc0]==before[0x5fc0]and m[0x5fd0]==before[0x5fd0]
            if area or loss:assert m[0x5c70]==0
            life+=1
        physics=[]
        for variant,face,water in itertools.product(range(4),[1,2],[0,1]):
            m=memory(code,data,s);setv(m,s,FfVariant=variant,SwimmingFlag=water);invoke(m,s,'FfEnsure')
            start=v(m,s,'Player_X_Position');setv(m,s,SavedJoypadBits=face)
            for t in range(60):invoke(m,s,'FfMovement')
            position=v(m,s,'Player_X_Position')+256*v(m,s,'Player_PageLoc')+m[s['MmXFraction']+1]/256
            expected=start+(1 if face==1 else -1)*(45 if water else 100)
            assert abs((position-expected)%65536)<1/128 or abs(position-expected)<1/128,('X',position,expected)
            # Genuine launch, no release cut, reverse in air, gravity family.
            setv(m,s,Player_X_Position=120,Player_PageLoc=0,Player_Y_Position=180,Player_State=0,
                 SavedJoypadBits=128|face,FfPrevious=face)
            invoke(m,s,'FfMovement');assert v(m,s,'Player_State')==1
            trace=[]
            for t in range(16):
                setv(m,s,SavedJoypadBits=2 if face==1 else 1)
                invoke(m,s,'FfMovement');trace.append(velocity(m,s,'MmVY'))
                assert (velocity(m,s,'MmVX')<0)==(face==1)
                expected=-1344+math.floor((t+2)*(Fraction(80,3)if water else Fraction(448,9)))
                assert trace[-1]==expected,('source gravity',trace[-1],expected)
            physics.append(dict(variant=variant,face=face,water=water,gravity_trace=trace))
        actions=[]
        for variant,direction in itertools.product(range(4),[0,4,8,12]):
            m=memory(code,data,s);setv(m,s,FfVariant=variant,FfPower=2,FfEarned=2,FfHealCharges=2)
            # Ensure before setting earned state, as actual first pickup/movement does.
            invoke(m,s,'FfEnsure');setv(m,s,FfPower=1,FfEarned=2,FfHealCharges=2)
            setv(m,s,FfFresh=64,SavedJoypadBits=64|direction)
            invoke(m,s,'FfActionTick')
            expected=0 if direction==12 or(variant in [0,3]and direction)else(1 if variant in [0,3]or(variant==1 and not direction)else 2)
            assert v(m,s,'FfAction')==expected,(variant,direction,v(m,s,'FfAction'),expected)
            setv(m,s,FfFresh=0)
            for t in range(1,49):invoke(m,s,'FfActionTick')
            assert v(m,s,'FfAction')==0
            if variant==1 and direction==8:
                assert v(m,s,'FfPower')==2 and v(m,s,'FfHealCharges')==1
            actions.append(dict(variant=variant,direction=direction,initial_action=expected))
        items=[]
        for variant,mode in itertools.product(range(4),range(2)):
            m=memory(code,data,s);setv(m,s,FfVariant=variant,CrossoverBehaviorVersion=mode);invoke(m,s,'FfEnsure')
            # Typed consumer inputs; no native physical collection claim.
            for food,want in [(0,1),(1,2),(0,2),(1,2)]:
                c=invoke(m,s,'FfPickup',a=food);assert c.p&1 and v(m,s,'FfPower')==want
            assert v(m,s,'FfEarned')==2 and v(m,s,'FfHealCharges')==(3 if variant==1 else 0)
            before=bytes(m[0x5c00:0x6000]);c=invoke(m,s,'FfPickup',a=2)
            assert not c.p&1 and bytes(m[0x5c00:0x6000])==before
            invoke(m,s,'FfInjuryStart');assert v(m,s,'FfPower')==1 and v(m,s,'FfHurt')==90
            invoke(m,s,'FfInjuryStart');assert v(m,s,'FfPower')==1
            for tick in range(90):invoke(m,s,'FfMovement')
            assert v(m,s,'FfHurt')==0
            if variant==1:
                setv(m,s,FfFresh=64,SavedJoypadBits=72)
                invoke(m,s,'FfActionTick');setv(m,s,FfFresh=0)
                for tick in range(30):invoke(m,s,'FfActionTick')
                assert v(m,s,'FfPower')==2 and v(m,s,'FfHealCharges')==2
                # Cap cannot consume charges; dead cannot start Heal.
                for tick in range(18):invoke(m,s,'FfActionTick')
                setv(m,s,FfFresh=64);invoke(m,s,'FfActionTick')
                assert v(m,s,'FfAction')==0 and v(m,s,'FfHealCharges')==2
                setv(m,s,FfPower=1,MmDeathFlag=1);invoke(m,s,'FfActionTick')
                assert v(m,s,'FfAction')==0 and v(m,s,'FfHealCharges')==2
            items.append(dict(variant=variant,mode=mode,pickup_consumers=4,protection_updates=90,white_earned_heal=variant==1))
        projectile_cases=[]
        for kind,face,slot in itertools.product(range(1,5),[1,2],[0,12,24]):
            m=memory(code,data,s);invoke(m,s,'FfEnsure')
            x=s['FfProjectile']+slot;m[x]=kind;m[x+4]=128;m[x+5]=0;m[x+7]=125;m[x+8]=face
            frames=[];positions=[]
            for tick in range(1,29):
                invoke(m,s,'FfWeapons');frames.append(m[x+1]);positions.append(m[x+4]+256*m[x+5]+m[x+6]/256)
                if kind==1:
                    assert positions[-1]==128+(1 if face==1 else -1)*3.75*tick
                    assert frames[-1]==math.floor(tick*1000/1980)%3
                else:
                    live=tick<(27 if kind==2 else 23)
                    assert bool(m[x])==live
                    if live:assert frames[-1]==math.floor(tick*1000/4500)
            projectile_cases.append(dict(kind=kind,face=face,slot=slot,first_frames=frames[:8],expires_after=0 if kind==1 else(27 if kind==2 else 23)))
        clocks=0
        for fire,moderate in itertools.product([0,1,979,980,1000,1979],[0,1,3499,3500,4499]):
            m=memory(code,data,s);invoke(m,s,'FfEnsure')
            for n,value in [('FfFireClock',fire),('FfModerateClock',moderate)]:m[s[n]]=value&255;m[s[n]+1]=value>>8
            invoke(m,s,'FfWeapons')
            assert v(m,s,'FfFireClock')+(m[s['FfFireClock']+1]<<8)==(fire+1000)%1980
            assert v(m,s,'FfModerateClock')+(m[s['FfModerateClock']+1]<<8)==(moderate+1000)%4500
            assert v(m,s,'FfClock')==int(fire+1000>=1980)|(int(moderate+1000>=4500)<<1)
            clocks+=1
        for field,value in [('TimerControl',1),('GamePauseStatus',1),('GameEngineSubroutine',7),('MmDeathFlag',1)]:
            m=memory(code,data,s);invoke(m,s,'FfEnsure');setv(m,s,**{field:value})
            before=bytes(m);invoke(m,s,'FfWeapons')
            assert bytes(m[:256]+m[512:])==before[:256]+before[512:]
            clocks+=1
        # Typed grounded/instant-landing admission stress, not a natural route
        # or complete Main. Ground state is explicitly supplied each iteration.
        m=memory(code,data,s);invoke(m,s,'FfEnsure');setv(m,s,FfVariant=2)
        live_max=0
        for tick in range(720):
            # New B every31updates, cancel cast with genuine fresh ground A.
            phase=tick%31;direction=[0,8,4][(tick//31)%3]
            setv(m,s,SavedJoypadBits=(64|direction)if phase==0 else(128 if phase==30 else 0),Player_State=0)
            invoke(m,s,'FfMovement');invoke(m,s,'FfWeapons')
            kinds=[m[s['FfProjectile']+i]for i in [0,12,24]];live_max=max(live_max,sum(bool(k)for k in kinds))
            assert not(2 in kinds and 3 in kinds)
        contacts=0
        for variant,tier,face,enemy in itertools.product([0,1,3],[0,2],[1,2],range(6)):
            for tx,ty in [(134,166),(135,166),(150,190),(151,190),(104,166),(120,166),(200,220)]:
                m=memory(code,data,s);invoke(m,s,'FfEnsure')
                setv(m,s,FfVariant=variant,FfPower=tier,FfAction=1,PlayerFacingDir=face,
                     FfTargetX=tx,FfTargetPage=0,FfTargetY=ty,FfTargetW=1,FfTargetH=1)
                c=invoke(m,s,'FfEnemyContact',a=255,x=enemy)
                rx=135 if face==1 else 105
                want=rx<=tx<rx+16 and 166<=ty<191
                assert bool(c.p&1)==want,('melee overlap',variant,face,tx,ty,want)
                if want:
                    assert v(m,s,'FfDamage')==({0:75,1:25,3:10}if tier==0 else{0:150,1:50,3:25})[variant]
                    c=invoke(m,s,'FfEnemyContact',a=255,x=enemy);assert not c.p&1
                    invoke(m,s,'FfForgetEnemy',x=enemy);c=invoke(m,s,'FfEnemyContact',a=255,x=enemy);assert c.p&1
                contacts+=1
        for kind,slot,tier,enemy,dy in itertools.product(range(1,5),[0,12,24],[0,2],range(6),[-25,-1,0,1,23,24,120]):
            m=memory(code,data,s);invoke(m,s,'FfEnsure');at=s['FfProjectile']+slot
            m[at]=kind;m[at+4]=128;m[at+7]=125;m[at+10]=tier
            setv(m,s,FfTargetX=128,FfTargetPage=0,FfTargetY=(125+dy)&255,FfTargetW=1,FfTargetH=1)
            c=invoke(m,s,'FfEnemyContact',a=slot,x=enemy)
            top={1:116,2:5,3:101,4:101}[kind];height={1:19,2:240,3:49,4:49}[kind]
            want=top<=125+dy<top+height
            assert bool(c.p&1)==want,('spell collision',kind,dy,want)
            if want:assert v(m,s,'FfDamage')=={1:100,2:150,3:100,4:25}[kind]+(50 if tier==2 else 0)
            contacts+=1
        # Unrelated-owner movement/weapon entry must not touch any RAM.
        foreign=0
        for identity in [0,1,2,3,5,8,13,20,21,23,255]:
            m=memory(code,data,s);setv(m,s,SelectedCharacter=identity)
            before=bytes(m)
            for name in ['FfEnsure','FfMovement','FfWeapons']:invoke(m,s,name)
            assert bytes(m[:256]+m[512:])==before[:256]+before[512:]
            foreign+=1
        # Every body/spell entry/chunk/facing/shadow reconstructs original indexed
        # pixels from the actual generated descriptor; full host OAM loop follows.
        assets=art_records(data);chrdata=(ROOT/'chr/characters/final-fantasy.chr').read_bytes();render=0;cost=[];drawcost=[];hardware=0;complete_cost=[]
        for fact in assets['source_cells']:
            rec=assets['records'][fact['record']]
            for facing,shadow in itertools.product([1,2],[0,1]):
                m=memory(code,data,s);setv(m,s,FfSlot=facing,PlayerOutlinesOff=shadow)
                parts=[];pixels={};whole_selector=0;whole_draw=0
                for chunk in range(rec['chunks']):
                    c=invoke(m,s,'FfRenderChunk',a=fact['entry'],x=chunk,y=0)
                    assert c.p&1
                    assert v(m,s,'FfRenderBuffer')<=60 and v(m,s,'FfRenderBuffer')%4==0
                    offset=s16(v(m,s,'FfRenderYOffset')|m[s['FfRenderYOffset']+1]<<8)
                    local=[]
                    for i in range(0,v(m,s,'FfRenderBuffer'),4):
                        t,attr,dy,dx=m[s['FfRenderBuffer']+1+i:s['FfRenderBuffer']+5+i]
                        dx=dx-256 if dx&128 else dx;dy=dy-256 if rec['kind']=='body'and dy&128 else dy
                        parts.append((t,attr,dx,dy+offset));local.append((t,attr,dx,dy))
                    page=v(m,s,'FfRenderPage');invoke(m,s,'FfPublishChunk')
                    assert v(m,s,'CurrentCHRBank')==(756+page)&255
                    assert v(m,s,'X5ChrMode')==0x80|((756+page)>>8)
                    pixels.update(pattern_pixels(chrdata,page,[(t,a,x,y+offset)for t,a,x,y in local]))
                    oam,cycles=actual_host_draw(m,s,code,offset);drawcost.append(cycles)
                    whole_selector+=c.processorCycles;whole_draw+=cycles
                    expected_oam=[]
                    # Loop emits descriptor parts backwards, exactly as host.
                    for t,attr,dx,dy in reversed(local):
                        x,y=128+dx,128+offset+dy
                        expected_oam.append((y,t,attr,x)if 0<=x<256 and 0<=y<256 else None)
                    assert len(oam)==len(expected_oam)
                    for row,expect in zip(oam,expected_oam):
                        if expect is None:assert row[0]==248
                        else:assert row==expect,('actual host OAM',fact['entry'],chunk,row,expect)
                    hardware+=1
                    cost.append(c.processorCycles)
                assert len(parts)<=fact['parts']
                expected=source_pixels(fact,facing,shadow)
                assert pixels==expected,('source indexed pixel/geometry',fact['entry'],facing,shadow,len(pixels),len(expected),
                                         list(set(pixels.items())^set(expected.items()))[:3])
                assert all(t<64 for t,_,_,_ in parts)
                complete_cost.append(dict(entry=fact['entry'],kind=fact['kind'],face=facing,outline_off=shadow,
                                          parts=len(parts),chunks=rec['chunks'],selector_cycles=whole_selector,host_draw_cycles=whole_draw))
                render+=1
        # True complete IRQ instruction stream at every distinct leaf PC on
        # representative movement/cast/three-projectile/chunk paths. No raster
        # or NMI model: this proves IRQ ABI/state preservation only.
        irq=[]
        for name,scenario,kwargs in [
            ('FfMovement','jump',dict(p=0x30)),('FfMovement','cast',dict(p=0x71)),
            ('FfWeapons','three',dict(p=0x38)),('FfRenderChunk','bolt',dict(a=156,x=2,y=3,p=0x39))]:
            m=memory(code,data,s);invoke(m,s,'FfEnsure')
            setv(m,s,CurrentBank=190,CurrentBankC=221,IrqNewScroll=173,IrqPPUCTRL=0x91,FfSlot=1)
            for j,n in enumerate(['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']):
                m[s[n]+1]=31+j
            m[s['FarcallJmpTarget_SMC']+2]=0xa7
            if scenario=='jump':setv(m,s,SavedJoypadBits=130,Player_State=0)
            if scenario=='cast':setv(m,s,FfVariant=2,FfAction=2,FfAge=29,FfSpell=2)
            if scenario=='three':
                for j,kind in zip([0,12,24],[1,2,3]):
                    at=s['FfProjectile']+j;m[at]=kind;m[at+4]=128;m[at+7]=125;m[at+8]=1
            image=bytes(m);base=Memory(image);c,trace=run_trace(base,s[name],**kwargs)
            relevant=sorted({pc for pc in trace if 0xaa00<=pc<0xaa00+len(code)})
            ignore=set(range(256,512))|{0x2005,0x2006,0x5128,0x5204}
            def state(q,c):return((c.a,c.x,c.y,c.p&0xcf,c.sp),bytes(q[i]for i in range(65536)if i not in ignore))
            expected=state(base,c)
            for pc in relevant:
                q=Memory(image);cc,_=run_trace(q,s[name],inject=pc,**kwargs)
                assert state(q,cc)==expected,('full IRQ leaf',name,hex(pc))
            irq.append(dict(caller=name,scenario=scenario,distinct_instruction_boundaries=len(relevant)))
        # FullRAM side-effect boundary and actual owned-path costs, not a free
        # profile claim. R0..R7 are declared render outputs/transient scratch.
        owned_cost=[]
        host_allowed=set()
        for n in RAM:
            if n in ['KillPlayer','BlockBufferColli_Head','BlockBufferColli_Side','IrqScrollSplit','MetaspriteRenderLoop','X5SetPhysicalChr']:continue
            host_allowed.add(s[n])
        for n,length in [('MmVX',3),('MmVY',3),('MmXFraction',2),('MmYFraction',2),('SmPosePtr',2),('CurrentCHRBank',4),('X5ChrMode',4)]:
            host_allowed.update(range(s[n],s[n]+length))
        allowed=set(range(0x5c00,0x5c80))|set(range(0x5fc1,0x5fcf))|set(range(256,512))|host_allowed|{0x5116}
        for variant,phase in itertools.product(range(4),['stand','walk','jump','melee','prepare','cast']):
            m=memory(code,data,s);setv(m,s,FfVariant=variant);invoke(m,s,'FfEnsure')
            if phase=='walk':setv(m,s,SavedJoypadBits=1)
            if phase=='jump':setv(m,s,SavedJoypadBits=129)
            if phase=='melee':setv(m,s,FfAction=1,FfAge=7)
            if phase=='prepare':setv(m,s,FfAction=2,FfAge=8,FfSpell=1)
            if phase=='cast':setv(m,s,FfAction=2,FfAge=29,FfSpell=1)
            before=bytes(m);cycles={}
            for name in ['FfMovement','FfWeapons','FfGraphics','FfDraw']:
                c=invoke(m,s,name);cycles[name]=c.processorCycles
                assert all(i in allowed for i in m.writes),('undeclared leaf RAM',name,[(hex(i),m[i])for i in m.writes if i not in allowed][:4])
            assert all(m[i]==before[i]for i in range(65536)if i not in allowed)
            owned_cost.append(dict(variant=variant,phase=phase,cycles=cycles,total_leaf_cycles=sum(cycles.values())))
        invalid=0
        for entry,chunk,window in [(158,0,0),(255,0,0),(0,255,0),(0,0,4)]:
            m=memory(code,data,s);setv(m,s,FfSlot=1)
            c=invoke(m,s,'FfRenderChunk',a=entry,x=chunk,y=window);assert not c.p&1 and v(m,s,'FfRenderBuffer')==0;invalid+=1
        for slot in range(36):
            m=memory(code,data,s);m[s['FfProjectile']+slot]=1
            c=invoke(m,s,'FfProjectileEntry',x=slot);assert bool(c.p&1)==(slot in [0,12,24]);invalid+=1
        for kind in range(1,5):
            for frame in [5,6,255]:
                m=memory(code,data,s);m[s['FfProjectile']]=kind;m[s['FfProjectile']+1]=frame
                c=invoke(m,s,'FfProjectileEntry',x=0)
                assert bool(c.p&1)==(frame<{1:3,2:6,3:5,4:5}[kind]);invalid+=1
        publication=0
        for page,window,dirty in itertools.product(range(32),range(4),range(2)):
            m=memory(code,data,s);setv(m,s,FfRenderPage=page,FfTemp2=window,ReloadCHRBank=dirty)
            for i in range(4):m[s['CurrentCHRBank']+i]=11;m[s['X5ChrMode']+i]=0x80
            invoke(m,s,'FfPublishChunk')
            for i in range(4):
                assert m[s['CurrentCHRBank']+i]==(((756+page)&255)if i==window else 11)
                assert m[s['X5ChrMode']+i]==((0x80|((756+page)>>8))if i==window else 0x80)
            publication+=1
        selectors=0
        for variant,tier,pose,face in itertools.product(range(4),range(3),range(1,19),[1,2]):
            m=memory(code,data,s);setv(m,s,FfVariant=variant,FfPower=tier,PlayerFacingDir=face)
            invoke(m,s,'FfSetPose',a=pose);want=bytes(m[s['FfRenderBuffer']:s['FfRenderBuffer']+61]);page=v(m,s,'FfRenderPage')
            setv(m,s,FfSlot=face)
            invoke(m,s,'FfRenderChunk',a=variant*36+(18 if tier==2 else 0)+pose-1,x=0,y=0)
            assert bytes(m[s['FfRenderBuffer']:s['FfRenderBuffer']+61])==want and v(m,s,'FfRenderPage')==page
            selectors+=1
        # Sparse source-only ROM overlay, no dispatch/menu hook. Both original
        # full host debug and component-only debug remain explicitly separate.
        sparse=bytearray(rom)
        sparse[16+62*8192+0xa00:16+62*8192+0xa00+len(code)]=code
        sparse[16+93*8192+0x1000:16+93*8192+0x1000+len(data)]=data
        sparse[16+1048576+756*1024:16+1048576+788*1024]=chrdata
        candidate=OUT/'candidate.nes';candidate.write_bytes(sparse)
        changed=[i for i,(a,b)in enumerate(zip(rom,sparse))if a!=b]
        assert all(16+62*8192+0xa00<=i<16+63*8192 or 16+93*8192+0x1000<=i<16+94*8192 or
                   16+1048576+756*1024<=i<16+1048576+788*1024 for i in changed)
        proof.update(passed=True,host=EXPECTED,source_only=True,CORE_bytes=len(code),ART_bytes=len(data),
                     source_life_cases=life,physics_cases=len(physics),physics=physics,action_cases=actions,
                     rendered_entry_facing_shadow_cases=render,render_chunk_cycles=[min(cost),max(cost)],
                     genuine_host_OAM_chunk_cases=hardware,host_draw_chunk_cycles=[min(drawcost),max(drawcost)],
                     typed_item_injury_cases=items,projectile_timelines=projectile_cases,reachable_max_live_projectiles=live_max,
                     contact_receipt_cases=contacts,foreign_owner_cases=foreign,
                     IRQ_abi_controls=irq,finite_owned_cost=owned_cost,invalid_admission_cases=invalid,
                     complete_physical_publication_cases=publication,source_pose_selector_cases=selectors,
                     shared_animation_phase_and_pause_cases=clocks,complete_art_cost=complete_cost,
                     sparse_candidate=bind(candidate),sparse_changed_bytes=len(changed),
                     source_model_scope='Rational60Hz equations, typed native consumer inputs, compiled leaves; no Flash VM/original-ROM golden or complete host Main.',
                     admission_stress_scope='720 typed grounded/instant-landing updates; supplied ground state, not natural flight/landing.',
                     outputs=[bind(OUT/p)for p in ['component.bin','art.bin','component.lbl','component.dbg']])
    except Exception as e:
        proof['error']=repr(e);raise
    finally:(OUT/'controls.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:proof[k]for k in ['passed','CORE_bytes','ART_bytes','source_life_cases','rendered_entry_facing_shadow_cases']}))
if __name__=='__main__':main()
