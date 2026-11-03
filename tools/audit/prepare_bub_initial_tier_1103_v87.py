"""Owner-only native initial tier, preserving warm source upgrades and stack."""
import hashlib,json,subprocess
from pathlib import Path
import check_bub_head_projection_1102_v56 as H
import check_bub_head_interrupts_1102_v57 as I
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-initial-tier-1103-v87'
PIN='cc7b9bddfd39c62fadb5c1afc34bc82361432eab5a8a8e5b5a18bde184813a4e'

def main():
    O.mkdir(exist_ok=True);_,old,route,q,p,prior=H.bundle();assert sha(R/'build/bub-head-root-candidate-1103-v81/bub-source-head.nes')==PIN
    image=bytearray(prior);start=p['labels']['BbHeadEnd'];assert start==0xb320
    init=q['labels']['BbNativeInit'];region=image[init-0xa000:init-0xa000+40]
    needle=bytes.fromhex('a900a2009d00c09d00c19d00c29d00c3');assert region.count(needle)==1
    at=init+region.index(needle);back=at+4;status=H.address(old,'PlayerStatus')
    source=f'.setcpu "6502"\n.segment "CODE"\n lda #0\n sta ${status:04x}\n ldx #0\n jmp ${back:04x}\n'
    (O/'initial-tier.s').write_text(source)
    (O/'initial-tier.cfg').write_text(f'MEMORY{{M:start=${start:04x},size=10,file=%O;}}SEGMENTS{{CODE:load=M,type=ro;}}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[str(cc/'ca65.exe'),str(O/'initial-tier.s'),'-o',str(O/'initial-tier.o')],[str(cc/'ld65.exe'),'-C',str(O/'initial-tier.cfg'),str(O/'initial-tier.o'),'-o',str(O/'initial-tier.bin')]]:
        z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
    code=(O/'initial-tier.bin').read_bytes();assert len(code)==10 and code==bytes([169,0,141])+status.to_bytes(2,'little')+bytes([162,0,76])+back.to_bytes(2,'little')
    assert image[start-0xa000:start-0xa000+10]==bytes([255])*10
    image[start-0xa000:start-0xa000+10]=code
    image[at-0xa000:at-0xa000+4]=bytes([76])+start.to_bytes(2,'little')+bytes([234])
    raw=bytearray(old['raw']);art=raw[1048592+441*1024:1048592+442*1024]
    cookie=bytes([167,39,1])+hashlib.sha256(image+art).digest()[:13]
    for i,page in enumerate(H.H.H.PAGES):raw[1048592+page*1024:1048592+(page+1)*1024]=image[i*1024:(i+1)*1024]
    raw[q['cookie_offset']:q['cookie_offset']+16]=cookie;new=dict(old,raw=bytes(raw))
    scenarios=[]
    for identity in [0,1]:
        seeds=[H.Q.Q.fresh(b,route,identity)for b in [old,new]]
        for mode in ['warm','cold-state','new-life']:
            for native in [0,1,2]:
                pair=[H.N.fork(m)for m in seeds];outs=[]
                for m in pair:
                    H.N.put(m,PlayerStatus=native)
                    actor=0x42 if identity else 0x2e;m.ram[2][actor+2]=7
                    if mode=='cold-state':m.ram[2][0x304]=0
                    if mode=='new-life':m.ram[2][0x307]=1
                    outs.append(H.N.invoke(m,'HuFresh',a=83,x=7,y=109,p=0x71))
                a,z=pair
                assert H.N.get(a,'PlayerStatus')==native and H.N.get(z,'PlayerStatus')==(native if mode=='warm' else 0)
                assert bytes(a.ram[2][:0x1000])==bytes(z.ram[2][:0x1000])
                aa=bytearray(a[0x200:0x800]);zz=bytearray(z[0x200:0x800]);aa[status-0x200]=zz[status-0x200]=0;assert aa==zz
                assert [outs[0][k]for k in ['A','X','Y','P','minimum_SP']]==[outs[1][k]for k in ['A','X','Y','P','minimum_SP']]
                assert a.rawtags==z.rawtags and bytes(a[3:11])==bytes(z[3:11]) and bytes(a[0x15a:0x17b])==bytes(z[0x15a:0x17b])
                scenarios.append(dict(identity=identity,mode=mode,inherited_native_tier=native,new_native_tier=H.N.get(z,'PlayerStatus'),minimum_SP=outs[1]['minimum_SP']))
    # All newly reached instructions execute at the unchanged old clear-loop
    # stack depth. Exercise genuine native IRQ and FF lag NMI at each point.
    actual=H.N.NesMPU;counts={};observed=[]
    for identity in [0,1]:
        for pc in [at,start,start+2,start+5,start+7]:
            for kind in ['IRQ','lagNMI']:
                injected=False
                class Trace(actual):
                    def step(self):
                        nonlocal injected
                        m=self.memory
                        if not injected and m.rawtags[1]==3 and self.pc==pc:
                            injected=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc);before=I.state(m);audio=I.audio(m);maps=m.rawtags[:];skipped=H.N.get(m,'NmiSkipped');lag,regular=I.I.path(m);lh=rh=0
                            self.irq()if kind=='IRQ'else self.nmi()
                            for _ in range(100000):
                                if (self.pc,self.sp)==(regs[5],regs[4]):break
                                assert m[self.pc]!=0;lh+=int(self.pc==lag);rh+=int(self.pc==regular);super().step()
                            else:raise AssertionError('ISR bound')
                            assert (self.a,self.x,self.y,self.p&0xef,self.sp,self.pc)==(*regs[:3],regs[3]&0xef,*regs[4:])
                            assert I.state(m)==before and I.audio(m)==audio and maps==m.rawtags
                            assert (lh,rh)==((0,0)if kind=='IRQ'else(1,0))
                            if kind=='lagNMI':assert H.N.get(m,'NmiSkipped')==(skipped+1)&255
                            counts[kind]=counts.get(kind,0)+1;observed.append([identity,pc,kind,regs[4]])
                        return super().step()
                m=H.Q.Q.fresh(new,route,identity);m.ram[2][0x304]=0;H.N.put(m,PlayerStatus=1,NmiDisable=255)
                H.N.NesMPU=Trace
                try:H.N.invoke(m,'HuFresh',a=83,x=7,y=109,p=0x21)
                finally:H.N.NesMPU=actual
                assert injected and H.N.get(m,'PlayerStatus')==0
    (O/'private-image.bin').write_bytes(image)
    rom=O/'bub-initial-tier.nes';rom.write_bytes(raw)
    parent=R/'build/bub-head-root-candidate-1103-v81/bub-source-head.nes'
    rom.with_suffix('.lbl').write_bytes(parent.with_suffix('.lbl').read_bytes());rom.with_suffix('.dbg').write_text('')
    out=dict(passed=True,private_probe=True,installed=False,fully_qualified=False,parent_ROM_SHA256=PIN,ROM_SHA256=sha(rom),cookie=cookie.hex(),candidate=rom.relative_to(R).as_posix(),bytes=10,remaining_source_gap=528,hook_CPU=at,leaf_CPU=start,stack_growth=0,scenarios=scenarios,new_instruction_IRQs=counts,interrupt_contexts=observed,source='Original initialization still clears the same source state; native initial tier0 now agrees with sourceflags0 after cold/new-life. Warm same-life Fresh preserves both original upgrades and native tier. Inherited tier1 was observed from actual SMB2 menu preview, not a Bub earned pickup.',remaining=['Exact-new-hash Mesen earned mushroom/flower and both routes.','Parent head nested audio/IRQ qualification and plainbrick variant still pending.'],bindings={str(f.relative_to(R)):sha(f)for f in [Path(__file__),O/'initial-tier.s',O/'initial-tier.bin',O/'private-image.bin',R/'build/bub-head-status-history-1103-v86/bub-history/capture/status-writes.json',H.O/'head-projection-v55.json',H.O/'head-projection-v60-NMI-I1.json']})
    (O/'proposal.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['scenarios','interrupt_contexts','bindings']}))

if __name__=='__main__':main()
