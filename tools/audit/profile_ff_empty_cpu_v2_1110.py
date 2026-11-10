"""Instruction-cycle profile of genuine cold-menu FF idle/walk; stdout only.

No actor, terrain, position, stat or renderer grant follows the ordinary menu
seed. Normal NMI is the established logical scheduler, not a cadence model.
"""
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_ff_head_lifetime_irq_1110 as L

W, N, Fix = L.W, L.N, L.Fix
LIFETIME_PIN = '6f9923f55828fed58d3098d479b437d2bd55822dffe37bf2228bc069203586ae'
FF_POINTS = {
    0xaa15:'FfEnsure',0xaabc:'FfMovement',0xae93:'FfActionTick',0xaf8d:'FfAllocate',
    0xb030:'FfWeapons',0xb12e:'FfAnimationTick',0xb3d0:'FfGraphics',
    0xb498:'FfVisible',0xb4a3:'FfRenderChunk',0xb5ff:'FfPublishChunk',
    0xa300:'FfHostDrawShots',0xa4d8:'FfHostCompact',0xa552:'FfHostRenderChunk',
    0xa606:'FfHostCullChunk',0xa661:'FfHostDecodeFx',0xb900:'FfHostMovement',
    0xb932:'FfHostRead',0xb988:'FfHostHead',0xb9fe:'FfHostFeet',
    0xba1e:'FfHostSide',0xba4c:'FfHostWall',0xba9d:'FfHostAfterTerrain',
    0xbad7:'FfHostBox',0xb620:'FfNewHeadRead',0xb670:'FfNativePipePriority',
    0xbb47:'FfSnapshotPreviousX',0xb68b:'FfMuxPacket'}


def point(m, pc):
    return (m.rawtags[(pc-0x8000)//8192] if pc >= 0x8000 else -1, pc)


def state(m):
    return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
        y=N.get(m,'Player_Y_Position'),engine=N.get(m,'GameEngineSubroutine'),
        lives=N.get(m,'NumberofLives'),camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc'),
        enemy_flags=[N.get(m,'Enemy_Flag',i) for i in range(6)],
        gear=m[0x5fc5],earned=m[0x5fc6],action=m[0x5c03])


class Profile:
    def __init__(self,m):
        self.m=m;self.cycles=Counter();self.instructions=Counter();self.entries=Counter()
        self.inclusive=Counter();self.callers=defaultdict(Counter);self.rows=[]
        self.names={(3,pc):name for pc,name in FF_POINTS.items()}
        self.labels=defaultdict(lambda:defaultdict(list))
        for name,s in m.bundle['syms'].items():
            if 'seg' not in s:continue
            try:at=W.address(m.bundle,name);loc=W.location(m.bundle,name)
            except (ValueError,KeyError):continue
            if not 0<=at<=0xffff or loc<16:continue
            tag=-1 if at<0x8000 else ((loc-16)//8192)|128
            if name.startswith('Ff') and 0xa000<=at<0xc000:tag=3
            self.labels[tag][at].append(name)
            if name in ('GameLoop','ReadJoypads','PlayerBGCollision','DrawAllMetasprites',
                'MetaspriteRenderLoop','FarCallCommon','FwCheck','FwCallEnter','FwLoad',
                'FwHostGraphics','FwHostMovement','FfHostHead','FwHostHead','FwPaletteTick',
                'ScrollHandler','FfHostWeapons','EnemyGraphicsEngine','SoundEngine') or (
                    tag==3 and name.startswith('Ff') and '::' not in name and 'size' in s):
                self.names[tag,at]=name
        for pc,name in FF_POINTS.items():self.labels[3][pc].append(name)

    def execute(self,c,stop):
        frames=[];last=None
        for _ in range(300000):
            for i in range(len(frames)-1,-1,-1):
                goal,begin,name=frames[i]
                if (c.pc,c.sp)==goal:
                    self.inclusive[name]+=c.processorCycles-begin
                    del frames[i]
            if (c.pc,c.sp)==stop:
                assert not frames,frames
                return c.processorCycles
            here=point(self.m,c.pc)
            name=self.names.get(here)
            if name:
                self.entries[name]+=1
                if last:self.callers[name][last]+=1
                ret=self.m[0x100+((c.sp+1)&255)]+256*self.m[0x100+((c.sp+2)&255)]+1
                frames.append(((ret,(c.sp+2)&255),c.processorCycles,name))
            before=c.processorCycles
            assert self.m[c.pc],('BRK',here)
            c.step()
            delta=c.processorCycles-before
            self.cycles[here]+=delta;self.instructions[here]+=1;last=here
        raise AssertionError(('CPU bound',hex(c.pc)))

    def summary(self):
        banks=Counter();buckets=Counter()
        for (tag,pc),cycles in self.cycles.items():
            banks[tag]+=cycles;buckets[tag,pc&0xffc0]+=cycles
        total=sum(banks.values());count=len(self.rows)
        def label(tag,pc):
            candidates=[p for p in self.labels[tag] if p<=pc]
            if not candidates:return []
            at=max(candidates)
            return [f'{n}+{pc-at:X}' for n in self.labels[tag][at]][:4]
        return dict(updates=count,total_cycles=total,mean_cycles=total/count,
            min_cycles=min(r['cycles'] for r in self.rows),max_cycles=max(r['cycles'] for r in self.rows),
            banks=[dict(tag=t,cycles=v,mean=v/count,share=v/total) for t,v in banks.most_common(10)],
            hot_64byte_regions=[dict(tag=t,PC=f'{p:04X}',cycles=v,mean=v/count,share=v/total,
                nearest_symbol=label(t,p)) for (t,p),v in buckets.most_common(14)],
            hot_entries=[dict(name=n,count=v,inclusive_cycles=self.inclusive[n],
                mean_inclusive=self.inclusive[n]/v,
                entry_predecessors=[dict(tag=t,PC=f'{p:04X}',count=a) for (t,p),a in self.callers[n].most_common(4)])
                for n,v in sorted(self.entries.items(),key=lambda z:self.inclusive[z[0]],reverse=True)[:24]],
            NMI_cycles=dict(mean=sum(r['NMI_cycles'] for r in self.rows)/count,
                minimum=min(r['NMI_cycles'] for r in self.rows),maximum=max(r['NMI_cycles'] for r in self.rows)),
            first=self.rows[0],last=self.rows[-1],
            empty_actor_updates=count,
            hot_instruction_PCs=[dict(tag=t,PC=f'{p:04X}',cycles=v,executions=self.instructions[t,p],
                nearest_symbol=label(t,p)) for (t,p),v in self.cycles.most_common(8)])


def normal_nmi(m):
    N.put(m,NmiDisable=0)
    c=N.NesMPU(memory=m,pc=0x5b00);c.sp,c.p=224,0x31
    smc=bytes(m[0x15a:0x17b]);c.nmi()
    for _ in range(200000):
        if (c.pc,c.sp)==(0x5b00,224):break
        assert m[c.pc];c.step()
    else:raise AssertionError('NMI bound')
    assert bytes(m[0x15a:0x17b])==smc
    return c.processorCycles


def main():
    assert sha256(Path(L.__file__).read_bytes()).hexdigest()==LIFETIME_PIN
    raw=W.ROM.read_bytes();assert sha256(raw).hexdigest()==W.PIN
    image,kernel,cookie,*_=Fix.proposal(raw);assert sha256(image).hexdigest()==L.PIN
    # Suppress evidence-snapshot allocations only; the real cold loader/menu runs intact.
    with patch.object(L,'sample',lambda *a,**k:None):
        m,cold,_=L.cold_menu(image,0,cookie,kernel)
    idle=W.address(m.bundle,'IdleLoop');results={}
    for phase,pad,length in (('idle_empty',0,32),('walking_empty',1,48)):
        profile=Profile(m)
        for update in range(length):
            before=state(m)
            assert not any(before['enemy_flags']),('empty scene unavailable',phase,update,before)
            assert (before['engine'],before['lives'],before['gear'],before['earned'],before['action'])==(8,2,0,0,0),before
            assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            m.controller_pad=pad;W.clear_logs(m);nmi_cycles=normal_nmi(m)
            c=N.NesMPU(memory=m,pc=idle);c.sp,c.p=255,0x31;c.stPushWord(0xe33b)
            cycles=profile.execute(c,(idle+12,252))
            after=state(m)
            assert not any(after['enemy_flags']),('enemy spawned',phase,update,after)
            assert after['lives']==2 and after['engine']==8 and not m.blocked
            profile.rows.append(dict(update=update,pad=pad,before=before,after=after,cycles=cycles,NMI_cycles=nmi_cycles))
        row=profile.summary();results[phase]=row
        print(json.dumps(dict(event='actual_empty_profile',phase=phase,result=row)),flush=True)
    assert results['idle_empty']['first']['before']['x']==results['idle_empty']['last']['after']['x']
    assert results['walking_empty']['last']['after']['x']-results['walking_empty']['first']['before']['x']>=64
    print(json.dumps(dict(passed=True,source_CPU_only=True,Mesen_run=False,output_files=0,
        candidate_SHA256=L.PIN,kernel_SHA256=sha256(kernel).hexdigest(),cold=cold,
        normal_NMI_scheduler=True,DMA_stalls_modeled=False,IRQ_injected=False,
        idle=results['idle_empty']['mean_cycles'],walking=results['walking_empty']['mean_cycles'],
        scope='Actual processorCycles instruction profile of real empty 1-1 FF Fighter menu/idle/walk with normal logical NMI. Excludes physical DMA stalls, scanline IRQs, audio output and cadence; inclusive entries overlap by nesting.')),flush=True)


if __name__=='__main__':main()
