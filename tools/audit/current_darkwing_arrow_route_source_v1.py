"""Finite typed-pipe real GameLoop proof; not a captured native scene/replay.

Only the disclosed initial map/player scene is authored. After initialization,
the controller supplies buttons; native recovery, collection, gas, selection,
shot, arrow actor, jump and collision code own all outcomes. No Mesen launch.
"""
from pathlib import Path
import argparse
import hashlib
import json

from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU
from current_rygar_powerups_prepare_v1 import setup as base_scene

ROOT = Path(__file__).resolve().parents[2]
ROM = ROOT/'build/mega_proto_body_palette_9ea.nes'
EXPECTED = 'ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2'
POLICY = ROOT/'tools/playthroughs/current_roster_darkwing_arrow_v1.lua'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def world(q, n='Player'):
    return q.get(n+'_X_Position')+256*q.get(n+'_PageLoc')


def block(q, x, y):
    if y < 32 or y >= 240:
        return 0
    return q.get('Block_Buffer_1', (x//256)%2*208+(y-32)//16*16+(x%256)//16)


def arrow(q):
    for i in range(10):
        if q.get('RgShotType',i) != 6:
            continue
        actor=q.get('RgShotImpact',i)-1
        if (0 <= actor <= 5 and q.get('Enemy_Flag',actor)==1
                and q.get('Enemy_ID',actor)==0x26
                and q.get('Enemy_State',actor)&0x7f==0x20|i):
            return i


class Controller:
    """Review mirror of the Lua recovery state machine, one poll per update."""
    def __init__(self):
        self.phase='route';self.origin=self.ground=None;self.transitions=[]

    def change(self,q,phase):
        if self.phase != phase:
            self.phase=phase
            self.transitions.append(dict(phase=phase,x=world(q),y=q.get('Player_Y_Position'),
                gas=q.get('DwGas'),adaptor=q.get('DwAdaptor'),mode=q.get('DwMode')))

    def buttons(self,q):
        x,y=world(q),q.get('Player_Y_Position');grounded=q.get('Player_State')==0
        pipe=block(q,x+32,y-20)
        if self.phase=='route' and x>450 and grounded and q.get('Player_X_Speed')==0 and 0x10<=pipe<0x16:
            self.origin=x;self.ground=y;self.change(q,'acquire')
        if self.phase!='route' and x>self.origin+64:
            self.change(q,'route')
        if self.phase=='route':
            return 1
        bits=1
        if self.phase=='acquire':
            if q.get('DwAdaptor')==2 and q.get('DwGas')>=3:
                self.change(q,'select-release')
            else:
                item=None
                for i in range(6):
                    if (q.get('Enemy_Flag',i)==1 and q.get('Enemy_ID',i)==0x2e
                            and q.get('Enemy_State',i)>=128 and q.get('InvPickupOwner',i)==12
                            and q.get('InvPickup',i)==0x26):
                        item=q.get('Enemy_X_Position',i)+256*q.get('Enemy_PageLoc',i);break
                return 1 if item is None or x<item-4 else 2 if x>item+8 else 0
        if self.phase=='select-release':
            if q.get('DwMode')==1:self.change(q,'fire-release')
            elif not q.get('DwPrevious')&32:self.change(q,'select-press')
        if self.phase=='select-press':
            bits|=32
            if q.get('DwMode')==1:bits&=~32;self.change(q,'fire-release')
            return bits
        if self.phase=='fire-release':
            if arrow(q) is not None:self.change(q,'jump-release')
            elif not q.get('DwPrevious')&64:self.change(q,'fire-press')
        if self.phase=='fire-press':
            bits|=64
            for i in range(10):
                t=q.get('RgShotType',i)
                if t in (5,6) or t==8 and q.get('RgShotImpact',i)==2:
                    bits&=~64;self.change(q,'attach');break
            return bits
        if self.phase=='attach':
            if arrow(q) is not None:self.change(q,'jump-release')
            return bits
        if self.phase=='jump-release':
            if not q.get('DwPrevious')&128:self.change(q,'jump-hold');bits|=128
            return bits
        if self.phase=='jump-hold':
            bits|=128
            if grounded and y<self.ground-4:
                self.ground=y;bits&=~128;self.change(q,'jump-release')
            elif grounded and arrow(q) is None:
                bits&=~128;self.change(q,'acquire')
            return bits
        return bits


def scene(b):
    q=Arena(b,12)
    q.put(DarkwingVariant=1,CrossoverBehaviorVersion=0,PlayerStatus=0,OperMode_Task=3,AreaType=1)
    q.array('GameTimerDisplay',[3,9,9])
    q.invoke('DwInventoryInit')
    base_scene(q,dict(kind='idle',face=1,hit=False))
    q.put(Player_X_Position=209,Player_PageLoc=2,MmOldX=209,Player_Y_Position=176,
        ScreenLeft_X_Pos=120,ScreenLeft_PageLoc=2,ScreenRight_X_Pos=119,ScreenRight_PageLoc=3)
    # Typed 64px pipe face736..767/top144, floor208. This is an authored
    # source-CPU scene, not a reconstruction of unlogged native block RAM.
    for row in range(7,11):
        for x,value in [(736,0x10 if row==7 else 0x14),(752,0x11 if row==7 else 0x15)]:
            q.set('Block_Buffer_1',value,(x//256)%2*208+row*16+(x%256)//16)
    assert (q.get('DwHealth'),q.get('DwGas'),q.get('DwAdaptor'),q.get('DwMode'))==(4,0,0,0)
    return q


def campaign(b,toolkit):
    q=scene(b);controller=Controller();rows=[];owners={};events=[];tick=0
    names=['DwScroogeMovement','DwScroogePhysics','DwRecovery','DwRecovery::Spawn',
        'MarioSourcePowerupCollision','DwCollectPickup','DwGiveItem','DwLaunch','DwShotInit',
        'DwAttachArrow','DwArrowActor','DwHangUpdate','DwValidateArrow']
    at={(address(b,n),(location(b,n)-16)//8192):n for n in names}
    original=NesMPU.step
    def step(cpu):
        bank=q.m.banks[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else -1
        name=at.get((cpu.pc,bank))
        if name:
            owners[name]=owners.get(name,0)+1
            if name in ['DwRecovery::Spawn','DwGiveItem','DwLaunch','DwShotInit','DwAttachArrow']:
                events.append(dict(update=tick,owner=name,PC=cpu.pc,bank=bank,A=cpu.a,X=cpu.x,
                    x=world(q),y=q.get('Player_Y_Position'),gas=q.get('DwGas'),adaptor=q.get('DwAdaptor'),mode=q.get('DwMode')))
        original(cpu)
    NesMPU.step=step
    try:
        for tick in range(600 if toolkit else 180):
            bits=controller.buttons(q)if toolkit else 1|(128 if tick%60<40 else 0)
            q.put(SavedJoypadBits=bits)
            _,writes=q.invoke('GameLoop')
            row=dict(update=tick,buttons=bits,phase=controller.phase,x=world(q),y=q.get('Player_Y_Position'),
                state=q.get('Player_State'),vy=q.get('Player_Y_Speed'),previous=q.get('DwPrevious'),
                gas=q.get('DwGas'),adaptor=q.get('DwAdaptor'),mode=q.get('DwMode'),hang=q.get('DwHang'),
                arrow=arrow(q),shots=[q.get('RgShotType',i)for i in range(10)])
            rows.append(row)
            assert q.get('GameEngineSubroutine')==8 and q.get('MmDeathFlag')==0,('No modeled death',row)
            ptr=address(b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0)
            q.invoke('SamusFreezeUpdateScreen');q.put(VRAM_Buffer1=0,VRAM_Buffer1_Offset=0)
            if toolkit and world(q)>817:break
    finally:NesMPU.step=original
    result=dict(owners=owners,events=events,transitions=controller.transitions,updates=len(rows),
        maximum_x=max(r['x']for r in rows),minimum_y=min(r['y']for r in rows),rows=rows)
    if toolkit:
        assert result['maximum_x']>817,('Toolkit typed-pipe route did not clear',result)
        assert owners.get('DwGiveItem')==1 and owners.get('DwRecovery::Spawn')==1
        assert any(r['adaptor']==2 and r['gas']==10 for r in rows)
        assert any(r['mode']==1 and r['gas']==7 for r in rows)
        assert any(r['arrow']is not None for r in rows)
        assert any(r['state']==0 and r['y']<176 for r in rows)
    else:
        assert result['maximum_x']<=721 and 124<=result['minimum_y']<=127, (result['maximum_x'],result['minimum_y'],rows[:4],rows[-4:])
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert not a.output.exists() and sha(ROM)==EXPECTED
    b=scoped_load(ROM)
    baseline=campaign(b,False);toolkit=campaign(b,True)
    proof=dict(passed=True,source_CPU_only=True,native_run=False,ROM_sha256=EXPECTED,
        ROM=str(ROM),tool_sha256=sha(Path(__file__)),policy_sha256=sha(POLICY),
        scope=__doc__,typed_scene=dict(player=[721,176],camera=632,pipe=[736,767,144,207],floor=208),
        baseline=baseline,toolkit=toolkit,
        limits='Python review mirror of Lua state machine; one poll per source update. Not native RAM/map, Lua execution, callback timing, PPU/art, input lag, actual recovery availability, or 1-1 clear proof. Native watchdog/8000 cap unchanged.')
    a.output.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=True,path=str(a.output),sha256=sha(a.output),baseline_updates=baseline['updates'],toolkit_updates=toolkit['updates'],maximum_x=toolkit['maximum_x'])))


if __name__=='__main__':main()
