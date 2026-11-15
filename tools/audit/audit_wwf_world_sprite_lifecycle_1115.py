"""Current WWF real cold/publishers/natural sprites/freeze lifecycle, no files."""
from collections import Counter,deque
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import replay_wwf_world_sprite_images_current_1115 as Factory
import check_shared_world_sprite_images_1114 as Source
import check_wwf_role_palette_1110 as Packet

W,N=Factory.W,Factory.N


def digest(data):return sha256(data).hexdigest()


def inspect(raw,key):
    config=Factory.bindings(raw,key);b=dict(W.Symbols.bundle(),raw=raw)
    assert digest(Path(Packet.__file__).read_bytes())=='e2dd226442ead7fea8969f60fe309658bcac77cf5be65e147a6cc2dc9d3e3c22'
    expected=Packet.cookies(raw,b);at=W.location(b,'WfCookieC')
    assert len(expected)==96 and raw[at:at+96]==expected,'All six complete source-derived WWF cookies'
    images=Packet.private_images(raw,b)
    packet=dict(all6_cookie_SHA256=digest(expected),selected_cookie=expected[16*config['role']:16*(config['role']+1)].hex(),
        A1_SHA256=digest(images[0]),base_C2_SHA256=digest(images[1]),A3_SHA256=digest(images[2]),
        metadata_SHA256=digest(images[4]),all_body_pages_SHA256=digest(images[5]))
    banks=W.address(b,'CurrentCHRBank');modes=W.address(b,'X5ChrMode')
    pub=W.address(b,'X5SetPhysicalChr');pubbank=(W.location(b,'X5SetPhysicalChr')-16)//8192|128
    names=('WfMovement','WfGraphics','WfDrawBody','WfBuildPose','WfMapBodyPage','WfColdBody','WfColdPortrait','WfAuthC2')
    labels={(W.address(b,n),(W.location(b,n)-16)//8192|128):n for n in names if n in b['syms']}
    ctx=dict(cpu=None,pc=-1,phase='cold-menu-constructor',Main=0)
    writes=Counter();first={};publishers=Counter();pubfirst={};calls=Counter();entries={};recent=deque(maxlen=12);arenas=[]
    baseCPU=N.NesMPU;originalCold=Source.cold
    def state(m):
        return dict(Main=ctx['Main'],phase=ctx['phase'],selected=N.get(m,'SelectedCharacter'),role=N.get(m,'FmGroups')&7,
            x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),
            native=N.get(m,'Player_State'),engine=N.get(m,'GameEngineSubroutine'),power=N.get(m,'PlayerStatus'),
            active=N.get(m,'GuestPowerupActive'),age=N.get(m,'GuestPowerupAge'),lives=N.get(m,'NumberofLives'))
    class CPU(baseCPU):
        def step(self):
            m=self.memory;ctx.update(cpu=self,pc=self.pc)
            tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if m[self.pc]==0x20:
                recent.append(dict(tag=tag,PC=self.pc,target=m[self.pc+1]+256*m[self.pc+2]))
            if(self.pc,tag)in labels and N.get(m,'SelectedCharacter')==29:
                name=labels[(self.pc,tag)];calls[name]+=1
                code=bytes(m[self.pc+i]for i in range(12));at=W.location(b,name)
                assert code==raw[at:at+12],'Actual current named WWF entry bytes'
                entries.setdefault((name,tag),dict(name=name,tag=tag,PC=self.pc,bytes=code.hex()))
            if self.pc==pub and tag==pubbank:
                sig=(ctx['phase'],self.y,((self.x&3)<<8)|self.a)
                publishers[sig]+=1
                pubfirst.setdefault(sig,dict(state=state(m),PC=self.pc,tag=tag,A=self.a,X=self.x,Y=self.y,
                    bytes=bytes(m[self.pc+i]for i in range(12)).hex(),recent_JSR=list(recent)))
            return super().step()
    class Bus(W.ControllerBus):
        def __setitem__(self,at,value):
            if isinstance(at,int)and(modes<=at<modes+12 or banks<=at<banks+12 or at in(0x5101,0x5130)or 0x5120<=at<=0x5127):
                pc=ctx['pc'];tag=self.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
                sig=(ctx['phase'],tag,pc,at,value&255)
                writes[sig]+=1
                if sig not in first:
                    assert len(first)<1024,'Bounded unique actual CHR writer identities'
                    first[sig]=dict(state=state(self),PC=pc,tag=tag,address=at,value=value&255,
                        instruction=bytes(self[pc+i]for i in range(3)).hex()if pc>=0 else'',recent_JSR=list(recent))
            return super().__setitem__(at,value)
    def cold(image,identity):
        m=originalCold(image,identity,Bus);arenas.append(m);ctx['phase']='Goomba-and-mature-Mushroom';return m
    def snapshot(m):
        return dict(state=state(m),modes=list(m[modes:modes+12]),software=list(m[banks:banks+12]),
            latched=list(m.chr_latches[:8]),palette=list(m.vram[0x3f00:0x3f20]),
            visible_OAM=sum(m[0x200+4*i]<240 for i in range(64)))
    with patch.object(Source,'Factory',Factory),patch.object(Source,'cold',cold),patch.object(N,'NesMPU',CPU),patch.object(W.UI.F,'NesMPU',CPU):
        route=Source.run(raw,key);assert route['passed'],route
        m=arenas[0];snapshots=[dict(event='mature-image-endpoint',**snapshot(m))]
        ctx['phase']='ordinary-mushroom-collector';pickup=None;freeze=0;recovered=None;resumed=0;before_calls=calls['WfMovement']
        for tick in range(700):
            ctx['Main']=tick
            s=state(m)
            assert s['selected']==29 and s['role']==config['role']and s['lives']==2,'Ordinary selected wrestler alive'
            if s['active']:
                if pickup is None:pickup=s;snapshots.append(dict(event='real-powerup-freeze',**snapshot(m)))
                ctx['phase']='real-60-tick-freeze';pad=0;freeze+=1
            elif pickup:
                if recovered is None:recovered=s;snapshots.append(dict(event='recovered',**snapshot(m)));before_calls=calls['WfMovement']
                ctx['phase']='post-pickup-resumed';pad=0
                resumed=calls['WfMovement']-before_calls
                if resumed>=25:break
            else:pad=1 if s['x']<401 else 0
            m.controller_pad=pad;Source.Frames.frame(m,whole_pass=True)
        else:raise AssertionError(('Natural post-image collector/freeze continuation bound',state(m),pickup,freeze))
        snapshots.append(dict(event='25-real-WfMovement-entries-after-recovery',**snapshot(m)))
        assert pickup and recovered and freeze==60 and resumed>=25 and N.get(m,'PlayerStatus')==1
    rows=[dict(**first[k],count=v)for k,v in sorted(writes.items())]
    pubs=[dict(**pubfirst[k],count=v,window=k[1],physical_page=k[2])for k,v in sorted(publishers.items())]
    # Counts stay finite; output detailed writer bodies once, never per frame.
    unique_pcs={};phase_counts=Counter()
    for row in rows:
        ident=(row['tag'],row['PC'],row['address']);phase_counts[(row['state']['phase'],row['address'])]+=row['count']
        unique_pcs.setdefault(ident,dict(tag=row['tag'],PC=row['PC'],address=row['address'],instruction=row['instruction'],recent_JSR=row['recent_JSR']))
    return dict(passed=True,ROM_SHA256=Factory.PIN,identity=key,metadata=Factory.metadata(raw,key),
        source_reconstruction=packet,native_page_SHA256={str(p):digest(raw[1048592+p*1024:1048592+(p+1)*1024])for p in(16,17)},
        actual_entries=list(entries.values()),entry_counts=dict(calls),actual_physical_publishers=pubs,
        unique_writer_instructions=list(unique_pcs.values()),writer_phase_counts=[dict(phase=k[0],address=k[1],count=v)for k,v in sorted(phase_counts.items())],
        route_source_receipt_SHA256=route['source_receipt_SHA256'],route_Main=route['source_Main_passes'],route_shots=route['shots'],
        freeze_ticks=freeze,resumed_WfMovement_entries=resumed,snapshots=snapshots,
        gameplay_seeds=0,outputs=0,Mesen_run=False,renderer=False,
        scope='Actual CPU writer/OAM/mapper lifecycle on exact current bytes. PNG API fixtures and initial latch fixture are not native images or pixel acceptance.')


if __name__=='__main__':
    raw=Factory.ROM.read_bytes();results=[]
    def forbid(*args,**kwargs):raise RuntimeError('WWF audit attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Native,'run',forbid):
        for key in Factory.IDENTITIES:
            q=inspect(raw,key);q['audit_receipt_SHA256']=digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());results.append(q)
            print(json.dumps(dict(WWF_source=q),separators=(',',':')),flush=True)
    print(json.dumps(dict(passed=True,identities=list(Factory.IDENTITIES),receipts=[q['audit_receipt_SHA256']for q in results],
        actual_current_bytes_captured_once=True,outputs=0,Mesen_run=False),separators=(',',':')),flush=True)
