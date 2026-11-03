"""Private head contact lifetime, getter ABI and actual BG policy checks."""
import collections,hashlib,json,re,subprocess
from pathlib import Path
from py65.devices.mpu6502 import MPU
import measure_bub_head_projection_1102_v55 as H
from check_tmnt_render_oa import location
O,Q,N,address,R,sha=H.O,H.Q,H.N,H.address,H.R,H.sha

def bundle():
    _,old,route,q=H.G.bundles();p=json.loads((O/'head-projection-v55.json').read_text())
    for name,digest in p['bindings'].items():assert sha(R/name)==digest,name
    image=(O/'head-projection-v55-image.bin').read_bytes();raw=bytearray(old['raw'])
    for i,page in enumerate(H.H.PAGES):raw[1048592+page*1024:1048592+(page+1)*1024]=image[i*1024:(i+1)*1024]
    raw[q['cookie_offset']:q['cookie_offset']+16]=bytes.fromhex(p['cookie'])
    assert hashlib.sha256(raw).hexdigest()==p['memory_ROM_SHA256']
    return old,dict(old,raw=bytes(raw)),route,q,p,image

def main():
    old,b,route,q,p,image=bundle();actual=N.NesMPU;source_trace=[];capture=None;holding=None;watched=0
    def sample(m):return tuple(m.ram[2][a]for a in[0x3c8,0x3c9,0x382,0x3cb])
    bg=address(b,'PlayerBGCollision');head=address(b,'HuHead');calls=collections.Counter()
    names={(((location(b,n)-16)//8192)|128,address(b,n)):n for n in ['PlayerHeadCollision','HuDraw','HuHead','BillHeadConsumer','BillBGHeadConsumer','CrossoverHeadProbe']}
    class Trace(actual):
        def step(self):
            nonlocal capture,holding,watched
            m=self.memory;bank=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else None
            name=names.get((bank,self.pc))
            if name:calls[name]+=1
            if self.pc==bg and bank==254 and m.ram[2][0x3ef]and capture is None:capture=N.fork(m)
            if bank==3 and self.pc==p['labels']['BbHeadCapture']:
                holding=sample(m)
            if holding is not None:
                assert sample(m)==holding,('Pending metadata overwritten',hex(self.pc),bank,sample(m),holding)
                watched+=1
                if self.pc==head and bank==207:holding=None
            if bank==3 and 0xa100<=self.pc<q['labels']['BbCodeEnd']:
                source_trace.append((self.pc,self.a,self.x,self.y,self.p,self.sp))
            return actual.step(self)
    N.NesMPU=Trace
    try:
        paired=0;cycles=[]
        fields=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','Player_Y_Speed','NumberofLives','Player_X_Scroll','ScreenLeft_X_Pos','ScreenLeft_PageLoc']
        for identity in [0,1]:
            for direction,jump in [(0,False),(1,False),(2,False),(1,True),(2,True)]:
                pair=[Q.Q.fresh(bb,route,identity)for bb in[old,b]]
                for m in pair:Q.L.E.main_fields(m)
                for epoch in range(25):
                    outs=[];traces=[]
                    for m in pair:
                        keys=direction|(128 if jump and epoch==1 else 0)
                        N.put(m,FrameCounter=epoch,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                        source_trace.clear();outs.append(N.invoke(m,'GameCoreRoutine',x=0,y=0));traces.append(list(source_trace))
                    a,z=pair
                    assert traces[0]==traces[1],(identity,direction,jump,epoch,'original instruction AXYP/SP')
                    assert bytes(a.ram[2][:1024])==bytes(z.ram[2][:1024]),(identity,direction,jump,epoch,'full source state')
                    assert[N.get(a,n)for n in fields]==[N.get(z,n)for n in fields]
                    assert[outs[0][n]for n in['A','X','Y','P']]==[outs[1][n]for n in['A','X','Y','P']]
                    assert bytes(a[3:11])==bytes(z[3:11])and bytes(a[0x15a:0x17b])==bytes(z[0x15a:0x17b])and a.rawtags==z.rawtags
                    cycles.append(outs[1]['CPU']-outs[0]['CPU']);paired+=1
        # The no-pending branch is the actual old getter for every input Y.
        getter=0
        for identity in[0,1]:
            seeds=[Q.Q.fresh(bb,route,identity)for bb in[old,b]]
            for y in range(256):
                pair=[N.fork(m)for m in seeds];outs=[]
                for m in pair:
                    m[3:11]=[19,37,55,73,91,109,127,145]
                    outs.append(N.invoke(m,'HuHead',a=83,x=7,y=y,p=0x71))
                assert [outs[0][k]for k in['A','X','Y','P']]==[outs[1][k]for k in['A','X','Y','P']]
                assert bytes(pair[0][3:11])==bytes(pair[1][3:11])and pair[0].ram[2][:1024]==pair[1].ram[2][:1024]and pair[0].rawtags==pair[1].rawtags
                getter+=1
        # Real whole Main stages the contact before drawing/BG. Watch every
        # executed instruction until its sole actual HuHead query consumes it.
        calls.clear();watched=0
        m,cell=H.H.arena(b,route,0)
        for epoch in range(17):
            N.put(m,FrameCounter=epoch,SavedJoypadBits=128 if epoch else 0,SavedJoypad1Bits=128 if epoch else 0,VRAM_Buffer1_Offset=0)
            N.invoke(m,'GameCoreRoutine',x=0,y=0)
        assert capture is not None and watched>0 and calls['PlayerHeadCollision']==1
        assert calls['HuHead']==calls['BillBGHeadConsumer']==calls['BillHeadConsumer']==calls['CrossoverHeadProbe']==17,calls
        live_calls=dict(calls);exclusions=[]
        for identity in [0,1]:
            for policy in ['ordinary','water','bounce','hurt']:
                m=N.fork(capture);m.ram[2][0x300]=identity;N.put(m,AreaType=0 if policy=='water'else 1,BlockBounceTimer=1 if policy=='bounce'else 0,GuestHurtTicks=1 if policy=='hurt'else 0,VRAM_Buffer1_Offset=0)
                source=bytes(m.ram[2][:0x300]);before=calls['PlayerHeadCollision']
                N.invoke(m,'PlayerBGCollision',x=0,y=0)
                assert calls['PlayerHeadCollision']-before==(policy=='ordinary'),(identity,policy,calls)
                assert m.ram[2][0x3ef]==0 and bytes(m.ram[2][:0x300])==source
                exclusions.append(dict(identity=identity,policy=policy,native_head_calls=calls['PlayerHeadCollision']-before))
        # Constructor/new-life actually clears the former telemetry byte.
        lifecycle=[]
        for identity in[0,1]:
            m=Q.Q.fresh(b,route,identity);m.ram[2][0x3ef]=0xf5;m.ram[2][0x3c8]=159;m.ram[2][0x3c9]=157
            m.ram[2][0x304]=0;N.invoke(m,'HuFresh',x=0,y=0)
            assert m.ram[2][0x3ef]==0 and m.ram[2][0x304]==167
            lifecycle.append(dict(identity=identity,cold_or_newlife_pending_zero=True))
    finally:N.NesMPU=actual
    # Source-bound compiled store census. The full index domain only overlaps
    # these cells at the already bounded init/snapshot/six-slot token loops.
    bases={'BB_VECTORS':0xa000,'BB_IMPORTS':0xa080,'BB_CODE':0xa100,'BB_HOST':0xb540,'BB_ACTOR_HOLE':0xa071,'BB_BOX_HOLE':0xa0b0,'BB_SOUND_HOLE':0xb53a,'BB_VISIBLE_ADMISSION':0xa074,'CODE':0xb2b5}
    cc=R/'tools/Windows/cc65/bin/ca65.exe';domains=[];bindings={}
    for role,src in [('source',R/'build/bub-upgrades-root-1102-v47/component.s'),('native',R/'build/bub-upgrades-root-1102-v56/native.s'),('head',O/'head-projection-v55.s')]:
        listing=O/f'head-writers-v56-{role}.lst';obj=O/f'head-writers-v56-{role}.o'
        z=subprocess.run([str(cc),str(src),'-l',str(listing),'-o',str(obj)],capture_output=True,text=True);assert z.returncode==0,z.stderr
        bindings[str(src.relative_to(R))]=sha(src);bindings[str(listing.relative_to(R))]=sha(listing)
        segment=None
        for line in listing.read_text().splitlines():
            match=re.match(r'^([0-9a-fA-F]{6})r?\s+\d+\s+(.*)$',line)
            if not match:continue
            off=int(match[1],16);text=match[2].split(';',1)[0];seg=re.search(r'\.segment\s+"([^"]+)"',text)
            if seg:segment=seg[1]
            if not re.match(r'^[0-9a-fA-F]{2}(?:\s|$)',text):continue
            ins=re.search(r'\b(sta|stx|sty|inc|dec|asl|lsr|rol|ror)\s+(.+)',text,re.I)
            if not ins or ins[2].strip().lower()=='a':continue
            pc=bases[segment]+off;op=image[pc-0xa000];mn,mode=MPU.disassemble[op]
            # Two native instructions are now exact source-funded JMP hooks.
            if role=='native'and(q['labels']['BbNativeCeilingHit']<=pc<q['labels']['BbNativeCeilingHit']+7 or pc==48760):continue
            assert mn.lower()==ins[1].lower(),(role,hex(pc),mn,ins[1])
            assert mode not in ['inx','iny','ind']
            width=2 if mode in ['zpg','zpx','zpy']else 3;operand=int.from_bytes(image[pc-0xa000+1:pc-0xa000+width],'little')
            lo=operand;hi=operand+(255 if mode in ['abx','aby']else 0)
            targets=[n for n in[0xc3c8,0xc3c9,0xc382,0xc3cb,0xc3ef]if lo<=n<=hi]
            if targets:domains.append(dict(role=role,CPU=pc,op=mn,mode=mode,operand=operand,targets=targets,source=text.strip()))
    assert not any(x['role']=='source'for x in domains)
    for row in domains:
        if row['mode']in['abx','aby']:
            assert row['operand']==0xc300 or row['operand']==0xc380 or 0xc320<=row['operand']<=0xc329,row
        elif row['role']=='native':assert row['operand']in[0xc3c8,0xc3c9,0xc3cb],row
    out=dict(passed=True,CPU_only=True,ROM_written=False,installed=False,qualified=False,memory_ROM_SHA256=p['memory_ROM_SHA256'],
        no_contact_paired_Main=paired,complete_original_instruction_AXYP_SP_trace_exact=True,no_contact_full_source_state_and_native_AXYP_SMC_maps_exact=True,
        extra_CPU_per_Main=[min(cycles),max(cycles)],no_pending_actual_getter_AXYP_R0_R7_maps_cases=getter,
        actual_source_contact_to_HuHead_instructions_watched=watched,actual_17_Main_caller_counts=live_calls,
        ordinary_native_guards=exclusions,lifecycle=lifecycle,compiled_writer_domains=domains,
        bounded_writer_indices=['Init STA C300,X iterates0..255 and clears pending before readyA7.','Snapshot STA C380,X startsX3/decrements through0; only C380..C383.','All native proxy token Y=16*slot; loops/admission capslot<6, so C320..C379.','Direct native writes C3C8/C3C9/C3CB are solely the ceiling sweep; no later movement/draw/import writes.','Compiled original source has no possible store to these five cells even with all256 X/Y values.'],
        remaining=['Actual IRQ/FF lag-NMI/nested audio full-state replay at new head/bump native path.','Real Mesen earned block emergence/collection and both actor fullstage regression.'],
        bindings={**bindings,**{str(f.relative_to(R)):sha(f)for f in[Path(__file__),Path(H.__file__),O/'head-projection-v55.json',O/'head-projection-v55-image.bin',R/'src/collision.s',R/'src/megaman_environment.s',R/'src/bill_bg_empty.s']}})
    (O/'head-projection-v56-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in['passed','qualified','no_contact_paired_Main','extra_CPU_per_Main','no_pending_actual_getter_AXYP_R0_R7_maps_cases','actual_source_contact_to_HuHead_instructions_watched','ordinary_native_guards','lifecycle']}))

if __name__=='__main__':main()
