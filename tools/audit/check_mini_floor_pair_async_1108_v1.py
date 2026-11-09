"""Real IRQ and FF lag-NMI cuts in the Mini floor worker at native caller depth."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_mini_floor_pair_fast_1108_v1 as F
import check_mini_lift_admission_async_1108_v1 as A


N, CPU = F.N, A.CPU
MANIFEST = F.R/'build/mini-floor-pair-fast-1108/proof.json'


def floor_state(c):
    m = c.memory
    fields = ('Player_Y_Position','Player_Y_HighPos','Player_Y_Speed','Player_Y_MoveForce',
              'Player_State','StompChainCounter','Player_CollisionBits','GameEngineSubroutine',
              'Up_Down_Buttons','Square1SoundQueue','Square2SoundQueue','CoinTallyFor1Ups',
              'JumpspringAnimCtrl','ChangeAreaTimer')
    buffers = tuple(F.F.address(m.bundle,n) for n in ('Block_Buffer_1','Block_Buffer_2'))
    return (tuple(N.get(m,n) for n in fields),tuple(bytes(m[p:p+208]) for p in buffers))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--manifest',type=Path,default=MANIFEST)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(exist_ok=True)
    manifest=json.loads(args.manifest.read_text())
    patch,=manifest['patches']
    site=patch['file_offset']
    old,new=(bytes.fromhex(patch[k]) for k in ('old_hex','new_hex'))
    assert len(old)==len(new)==36
    all_builds={}
    for build,(folder,pin) in F.INPUTS.items():
        source_rom=F.R/'build'/folder/'candidate.nes'
        raw=source_rom.read_bytes()
        assert F.F.sha(raw)==pin and raw[site:site+36]==old
        image=raw[:site]+new+raw[site+36:]
        digest=F.F.sha(image)
        assert digest==manifest['comparisons'][build]['memory_only_SHA256']
        b=F.F.bundle(image)
        idle,game_loop,game_core=(F.F.address(b,n) for n in ('IdleLoop','GameLoop','GameCoreRoutine'))
        boot_jsr,stop=0xe339,idle+12
        stats=Counter();nested={};outcomes={};min_isr=255;min_foreground=255
        scenarios=(('pipe_air',0x11,0,0,0,True,False),
                   ('ground_down',0x54,0x54,4,0,True,False),
                   ('pipe_down',0x10,0x11,4,0,False,True),
                   ('spring_floor',0x67,0,0,0,False,True),
                   ('side_coin',0x11,0,0,0xc2,True,True))
        if manifest.get('floor_mask')==0xa8:
            scenarios+=(('decorative_pipe_air',0x13,0,0,0,True,False),
                        ('decorative_pipe_down',0x12,0x13,4,0,False,True))

        def handler(c,kind,role):
            nonlocal min_isr
            m=c.memory;at=(c.pc,c.sp);snapshot=(A.live(c),floor_state(c))
            before_writes=len(m.writes);skipped=N.get(m,'NmiSkipped')
            if kind=='lag_FF':
                assert N.get(m,'NmiDisable')==255
                c.nmi()
            else:
                assert not c.p&4
                c.irq()
                assert (A.tags(c),c.pc)==(254,0x8000)
            visits=0;m.in_handler=True
            for _ in range(16000):
                if (c.pc,c.sp)==at:
                    break
                min_isr=min(min_isr,c.sp)
                if kind=='lag_FF':
                    assert c.pc!=regular
                    visits+=c.pc==lag
                    if not c.p&4:
                        k=(A.tags(c),c.pc)
                        if k not in nested or c.sp<nested[k].sp:
                            nested[k]=A.clone(c)
                assert m[c.pc],(kind,role,at,hex(c.pc))
                CPU.step(c)
            else:
                raise AssertionError(('bounded ISR',kind,role,at,hex(c.pc)))
            m.in_handler=False
            assert (A.live(c),floor_state(c))==snapshot,(build,kind,role,at)
            assert visits==(kind=='lag_FF')
            assert N.get(m,'NmiSkipped')==(skipped+(kind=='lag_FF'))&255
            assert not any(0x200<=a<0x304 or a==0x4014 for a,_ in m.writes[before_writes:])
            stats[kind,role]+=1

        def complete(c):
            for _ in range(35000):
                if c.pc==stop:
                    return A.final(c),floor_state(c)
                assert c.memory[c.pc],hex(c.pc)
                CPU.step(c)
            raise AssertionError(('bounded native return',build,hex(c.pc)))

        N.Bus=A.Bus
        try:
            seed=F.F.fixture(b,0,False,False)
            lag,regular=A.lag_pcs(seed)
            assert bytes(seed[boot_jsr:boot_jsr+3])==bytes((0x20,idle&255,idle>>8))
            assert bytes(seed[idle+9:idle+12])==bytes((0x20,game_loop&255,game_loop>>8))
            for scenario,left,right,down,side,accept,want_fallback in scenarios:
                base=N.fork(seed);F.setup(base,758,112,left,right,down=down,side=side)
                N.put(base,NmiDisable=255)
                reached=set();samples=[];returns=[];entries={};fallback=[False];floor=[]

                class Trace(CPU):
                    def step(self):
                        nonlocal min_foreground
                        tag,pc=A.tags(self),self.pc
                        if tag==254 and pc in (game_loop,game_core):
                            entries[pc]=self.sp
                        if tag==148 and pc==0xbe34:
                            lo=base[0x100+((self.sp+1)&255)]
                            hi=base[0x100+((self.sp+2)&255)]
                            floor.append((1+lo+256*hi,self.sp+2))
                        if floor and tag==148 and (pc,self.sp)==floor[0]:
                            returns.append(bool(self.p&1));floor.clear()
                        if tag==254 and pc==0x9b5b:
                            fallback[0]=True
                        role=('new_floor' if tag==148 and 0xbe34<=pc<0xbe58 else
                              'native_feet' if floor and tag==254 and 0x9586<=pc<=0x95d7 else None)
                        if role and (tag,pc) not in reached:
                            reached.add((tag,pc));min_foreground=min(min_foreground,self.sp)
                            for kind in ('IRQ','lag_FF'):
                                fork=A.clone(self)
                                handler(fork,kind,role)
                                if role=='new_floor':samples.append(fork)
                        return CPU.step(self)

                c=Trace(memory=base,pc=idle);c.sp,c.p=255,0x31;c.stPushWord(boot_jsr+2)
                for _ in range(35000):
                    if c.pc==stop:
                        break
                    assert base[c.pc],hex(c.pc)
                    c.step()
                else:
                    raise AssertionError(('native GameLoop bound',build,scenario,hex(c.pc)))
                assert entries=={game_loop:250,game_core:248} and c.sp==252
                assert returns==[accept] and fallback[0]==want_fallback,(build,scenario,returns,fallback)
                expected=A.final(c),floor_state(c)
                assert all(complete(fork)==expected for fork in samples),(build,scenario,'resume')
                outcomes[scenario]=dict(distinct_reached=len(reached),resumed=len(samples),
                                        accepted=returns[0],native_fallback=fallback[0])
        finally:
            N.Bus=A.BASE_BUS
        for cut in nested.values():
            handler(cut,'nested_IRQ','lag_handler')
        assert min_isr>0x7a and outcomes
        all_builds[build]=dict(parent_SHA256=pin,memory_only_SHA256=digest,scenarios=outcomes,
            exact_entries=dict(GameLoop=250,GameCoreRoutine=248),min_foreground_SP=min_foreground,
            min_ISR_SP=min_isr,cuts={kind:{role:n for (k,role),n in stats.items() if k==kind}
                                  for kind in ('IRQ','lag_FF','nested_IRQ')},
            binding_SHA256=F.F.sha(source_rom.read_bytes()))
        print(json.dumps({build:all_builds[build]}),flush=True)
    report=dict(passed=True,source_CPU_only=True,ROM_written=False,comparisons=all_builds,
                scope='Actual GameLoop, all reached floor instructions and native foot probe PCs. '
                      'Real IRQ/FF/nested vectors, watched floor/scratch/WRAM/OAM/maps and matched full returns. '
                      'No native video cadence qualification.',
                bindings={str(p):F.F.sha(p.read_bytes()) for p in (args.manifest,Path(__file__),Path(A.__file__))})
    (out/'proof.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
