"""Exact installed Mini: exclusive cycle/mapper profile of bounded busy CPU arenas."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

from prepare_mini_mario_native_power_1103_v56 import N, bundle, address, location

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'build/mini-two-fireballs-1103'
ROM=SOURCE/'mini-empty-draw.nes'
PIN='244734bbc2690b4e97e654cc72f8f153bedbe3fcc799f714e9508784e4f33af4'


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def labels(p):return {name:int(pc,16)for pc,name in
                      re.findall(r'^al ([\da-fA-F]+) \.(\w+)$',p.read_text(),re.M)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    assert digest(ROM)==PIN
    b=bundle(ROM.read_bytes())
    marker={'MiniScene':N.get}
    names=defaultdict(list)
    hooks={}
    watched=set('GameCoreRoutine GameRoutines GuestGameRoutinesBridge PlayerCtrlRoutine PlayerMovementSubs EnemiesAndLoopsCore RunNormalEnemies EnemyToBGCollisionDet NormalEnemyOffscreenBits NormalEnemyBoundBox EnemiesCollision PlayerEnemyCollision Mmc5GroundGoombaTerrain PlayerBGCollision BlockBufferCollision CrossoverSourceSideProbe CrossoverSourceFootProbe BillBGHeadConsumer GuestPostEnemyCollision PlayerGfxHandler AreaParserTaskHandler ProcLoopCommand DrawAllMetasprites SamusFreezeDrawAll DrawBrickDebris WorldFirebarAdmission KbOamPriority RlSpecialDrawDispatch X5BounceUiDispatch ScrollHandler GetPlayerOffscreenBits RelativePlayerPosition'.split())
    for name,row in b['syms'].items():
        if 'seg' not in row or 'val' not in row:continue
        seg=b['segs'].get(row['seg'],{})
        if 'ooffs' not in seg:continue
        pc=address(b,name)
        if pc<0x8000:continue
        k=((location(b,name)-16)//8192,pc)
        names[k].append(name)
        if name in watched:hooks[k]=name
    for name,pc in labels(SOURCE/'mini-zero.lbl').items():
        names[3,pc].append(name)
        if name in ('MiniStep','MiniHostMain','MiniHostDraw','MiniNativeTile','MiniNativeDraw'):
            hooks[3,pc]=name
    for name,pc in labels(SOURCE/'render.lbl').items():
        if name in ('MiniBackground','BackgroundGuard','ProbeFloor','ProbeSides','MiniDrawGate'):
            hooks[20,pc]=name;names[20,pc].append(name)
    m=N.fresh(b)
    N.put(m,SelectedCharacter=41,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,
          Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160)
    N.invoke(m,'MiniScene')
    assert m.ram[2][0x300]==1
    seed=m
    base=N.NesMPU

    def map_tag(bus,pc):
        if pc<0x8000:return -1
        return bus.rawtags[(pc-0x8000)//8192]&127

    def run(name,x,y,enemy_offsets,tile,freeze=False):
        m=N.fork(seed)
        camera=x-95
        def array(n,i,value):m[address(b,n)+i]=value
        def cell(px,py,value):
            key='Block_Buffer_2' if px&256 else 'Block_Buffer_1'
            m[address(b,key)+((px>>4)&15)+(py&0xf0)-32]=value
        N.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,OperMode_Task=3,
              GameEngineSubroutine=8,PlayerStatus=0,PlayerSize=1,Player_X_Position=x&255,
              Player_PageLoc=x>>8,Player_Y_Position=y,Player_Y_HighPos=1,
              PlayerFacingDir=1,Player_State=0 if y==176 else 2,AreaType=1,
              ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,
              ScreenRight_X_Pos=(camera+255)&255,ScreenRight_PageLoc=(camera+255)>>8,
              EnemyDataOffset=0,AreaParserTaskNum=7,FrameCounter=3,
              TimerControl=int(freeze),SavedJoypadBits=0x41,SavedJoypad1Bits=0x41,
              VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
        for px in range(camera&~255,(camera&~255)+512,16):
            for py in (192,208,224):cell(px,py,0x54)
        if tile:
            cell((x+12)&~15,(y+24)&~15,tile)
        m[address(b,'GameTimerDisplay')]=4
        for i,d in enumerate(enemy_offsets):
            ex=x+d
            for n,v in [('Enemy_Flag',1),('Enemy_ID',6),('Enemy_State',0),
                        ('Enemy_X_Position',ex&255),('Enemy_PageLoc',ex>>8),
                        ('Enemy_Y_Position',176),('Enemy_Y_HighPos',1),
                        ('Enemy_MovingDir',2),('Enemy_X_Speed',0xf8),
                        ('Enemy_BoundBoxCtrl',9)]:
                array(n,i,v)
        if tile==0x51:
            N.put(m,Block_State=1,Block_X_Position=(x+8)&255,
                  Block_PageLoc=x>>8,Block_Y_Position=(y+24)&~15)

        pcs=Counter();far=Counter();banks=Counter()
        counts=Counter();inclusive=Counter()
        stack=[]
        def word(at):return m[at]|m[at+1]<<8
        class Trace(base):
            def step(self):
                pc=self.pc;start=self.processorCycles;sp=self.sp
                while stack and (pc,sp)==stack[-1][:2]:
                    _,_,label,at=stack.pop()
                    inclusive[label]+=start-at
                k=map_tag(m,pc),pc
                label=hooks.get(k)
                if label:
                    ret=(word(0x101+sp)+1)&65535
                    stack.append((ret,(sp+2)&255,label,start));counts[label]+=1
                if pc==0x15a:
                    ret=(word(0x101+sp)+1)&65535
                    target=word(0x16c)
                    far[self.a&127,target,map_tag(m,ret),ret]+=1
                super().step()
                delta=self.processorCycles-start;pcs[k]+=delta;banks[k[0]]+=delta
        N.NesMPU=Trace
        try:ret=N.invoke(m,'GameCoreRoutine',a=0,x=0,y=0)
        finally:N.NesMPU=base
        assert sum(pcs.values())==ret['CPU']
        def near(bank,pc):
            if (bank,pc)in names:return names[bank,pc]
            # Only closest known symbol is useful as an address hint; local
            # labels are not assumed to own every following instruction.
            before=[p for k,p in names if k==bank and p<=pc and pc-p<48]
            return names[bank,max(before)] if before else []
        return dict(scene=name,x=x,y=y,enemy_offsets=enemy_offsets,mutated_metatile=tile,
                    cycles=ret['CPU'],minimum_SP=ret['minimum_SP'],
                    farcall_entries=sum(far.values()),
                    farcall_trampoline_exclusive=sum(v for (k,p),v in pcs.items() if k==-1 and 0x15a<=p<0x17b),
                    banks=banks.most_common(20),
                    top_pcs=[(k,hex(pc),v,near(k,pc))for(k,pc),v in pcs.most_common(24)],
                    farcalls=[dict(bank=k,target=hex(t),target_label=near(k,t),caller_bank=cb,
                                   caller_return=hex(r),caller_label=near(cb,r),calls=v)
                              for(k,t,cb,r),v in far.most_common()],
                    completed_routine_cycles=inclusive.most_common(),
                    routine_entries=counts.most_common(),
                    terminal={k:N.get(m,k)for k in ('Player_State','GameEngineSubroutine','Player_X_Position','Player_Y_Position')})

    scenes=[
        run('flat-no-enemy',448,176,(),0),
        run('ground-five-Goombas',1910,176,(-48,-24,20,42,68),0),
        run('air-four-Goombas',2031,149,(-30,-11,21,54),0),
        run('air-pipe-four-Goombas',729,131,(-35,-7,26,58),0x10),
        run('air-brick-two-Goombas',1518,140,(-19,45),0x51)]
    report=dict(passed=True,ROM_sha256=PIN,source_CPU_only=True,ROM_written=False,
                scope='Actual linked GameCoreRoutine and mapper transport. Explicit source-active arena/terrain/enemies; no NMI/DMA/raster or controller-rate qualification. Inclusive routine totals may overlap; source PC cycle bins are exclusive. Enemy parser intentionally set to no-spawn state7.',
                scenes=scenes,bindings={str(p.relative_to(ROOT)):digest(p)for p in
                                        (Path(__file__),SOURCE/'mini-zero.lbl',SOURCE/'render.lbl')})
    (a.output/'profile.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps([{k:r[k]for k in ('scene','cycles','farcall_entries','farcall_trampoline_exclusive','completed_routine_cycles')}for r in scenes]))


if __name__=='__main__':main()
