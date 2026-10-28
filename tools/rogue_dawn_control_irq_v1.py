"""Real frozen host ISR seams in a declared in-memory Rogue CPU composition.

No linked candidate/native/PPU claim. No ROM file or shared source is changed.
"""
from pathlib import Path
import argparse,hashlib,itertools,json,sys
import rogue_dawn_control_controls_v1 as control
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import Memory,address
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--host',type=Path,default=R/'build/sunny-integrated-final.nes');p.add_argument('--output',type=Path,default=R/'build/rogue-dawn-control-v1/irq-controls.json');a=p.parse_args()
    raw=control.ref.ROM.read_bytes();compiled=control.build(a.output.parent);code,aux,data,labels,callbacks=compiled
    host=scoped_load(a.host);image=bytearray(host['raw'])
    def place(bank,pc,value):
        at=16+bank*8192+(pc&8191);image[at:at+len(value)]=value
    place(124,0xb000,code);place(124,0xae00,aux);place(94,0xd300,data)
    bundle=dict(host,raw=bytes(image));rows=[]
    smc=[address(bundle,k)+d for k,d in [('NextBank_SMC',1),('SafecallA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2),('SafereturnA_SMC',1)]]
    for action,pad,startx,world,names in [(0,128,128,control.World(),['RdControlStep','RdControlDispatch','RdControlAdvance','RdStartJump']),
      (1,129,128,control.World(right=132),['RdC_DA25','RdC_DA68','RdControlPhysics'])]:
        for name,kind,lag in itertools.product(names,['IRQ','NMI'],[False,True]):
            state=control.state(4,action,x=startx,y=96 if action else 144)
            if action:state.update({0x301:15,0x302:4,0x303:16,0x305:12,0x306:13,0x308:252,0x314:24})
            q=control.Runner(raw,compiled,True,world,state);old=q.m
            q.m=Memory(bundle);q.m[0x5c00:0x5c80]=old[0x5c00:0x5c80];q.m[0x5fb0:0x5fb8]=old[0x5fb0:0x5fb8]
            for n,v in [('SelectedCharacter',2),('RdVariant',1),('NmiDisable',255 if lag else 0),('DisableScreenFlag',1),('Sprite0HitDetectFlag',0),('OperMode',1),('GameEngineSubroutine',8)]:
                if n=='RdVariant':q.m[0x5fee]=v
                else:q.m[address(bundle,n)]=v
            q.m.page(1,124);q.m.page(2,94);q.m[address(bundle,'CurrentBank')]=252;q.m[address(bundle,'CurrentBankC')]=222
            q.set(0x12,pad);q.set(0x14,pad);q.set(0x2d,0)
            c=NesMPU(memory=q.m,pc=labels['RdControlStep']);c.sp=0xc0;c.p=0x71;c.stPushWord(0x5aff);fired=False;low=c.sp
            inverse={v:k for k,v in callbacks.items()}
            def snapshot():return(c.a,c.x,c.y,c.p&207,c.sp,c.pc,tuple(q.m.banks),q.m[address(bundle,'CurrentBank')],q.m[address(bundle,'CurrentBankC')],bytes(q.m[z]for z in smc),bytes(q.m[0x101+c.sp:0x200]),bytes(q.m[0x5c00:0x5c80]),bytes(q.m[0x5fb0:0x5fc0]))
            for _ in range(100000):
                if c.pc==0x5b00:break
                if not fired and c.pc==labels[name]and q.m.banks[1]==124:
                    fired=True;before=snapshot()
                    if kind=='NMI':c.nmi()
                    else:c.stPushWord(c.pc);c.stPush(c.p&~c.BREAK|c.UNUSED);c.p|=c.INTERRUPT;c.pc=address(bundle,'IrqScrollSplit')
                    for _ in range(50000):
                        low=min(low,c.sp);c.step()
                        if c.pc==before[5]and c.sp==before[4]:break
                    else:raise AssertionError(('ISR timeout',name,kind,hex(c.pc)))
                    assert snapshot()==before,(name,kind,'ISR ABI mismatch')
                if c.pc in inverse:q.callback(c,inverse[c.pc])
                else:c.step()
                low=min(low,c.sp)
            else:raise AssertionError(('control timeout',name,kind,hex(c.pc)))
            assert fired and c.sp==192
            rows.append(dict(entry=name,kind=kind,lag=lag,source_action=action,minimum_SP=low,AXY_realP_PC_SP_A_C_shadows_fiveSMC_liveStack_owned_state_exact=True))
    proof=dict(passed=True,native_run=False,host_ROM_sha256=sha(a.host),in_memory_CPU_image_sha256=hashlib.sha256(image).hexdigest(),CORE_bytes=len(code),AUX_bytes=len(aux),rows=rows,
      scope=__doc__,limits=['In-memory declared component placement, not a whole linked build/native or visible rendering/deadline test.','Host draw/geometry boundaries use the separately source-qualified callback model. IRQ/NMI code is the actual frozen host ISR.','Real6502 flags compared include N,V,D,I,Z,C. B/U are py65 virtual status-image bits.'],
      bindings=[control.ref.binding(f)for f in [Path(__file__),a.host,a.host.with_suffix('.dbg'),R/'tools/rogue_dawn_control_controls_v1.py',R/'src/rogue_dawn_control.s',a.output.parent/'control.bin',a.output.parent/'aux.bin']])
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,seams=len(rows),minimum_SP=min(r['minimum_SP']for r in rows))))
if __name__=='__main__':main()
