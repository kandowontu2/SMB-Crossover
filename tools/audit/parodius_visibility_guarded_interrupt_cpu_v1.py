"""Actual lag-NMI/IRQ at every selector instruction boundary, CPU-only."""
from pathlib import Path
import argparse,hashlib,json
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ['rom','body-config','output']:ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=scoped_load(a.rom)
    rr=list(json.loads(a.body_config.read_text())['body_sources'].values())
    cases=[(next(r for r in rr if r['bank']==bank),rotation,flip)for bank,rotation,flip in [(76,244,0),(76,236,0),(76,244,1),(117,244,0),(116,244,0)]]
    smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2]
    fields=['SmPosePtr','SmPosePtr+1','R0','R1','R3','CurrentOAMOffset','RgOamRotation','VvTemp','VvTemp2','PnDrawFrame']
    def get(q,n):return q.get(n.split('+')[0],1 if '+'in n else 0)
    def setup(rec,rotation,flip):
        ref=rec['refs'][0];q=Arena(b,18)
        q.put(VvVariant=ref['variant'],PnPool=ref['pool'],PnFrame=ref['frame'],CurrentOAMOffset=12,RgOamRotation=rotation,GuestOamRotationActive=1,ObjectVerticalFlip=flip,Player_Y_Position=120,DisableScreenFlag=0,InvHudActive=0,NmiDisable=255,VRAM_Buffer_AddrCtrl=0,Mirror_PPUCTRL=0xa0,Sprite0HitDetectFlag=1)
        q.array('SmPosePtr',[rec['pointer']&255,rec['pointer']>>8]);q.m.page(1,77);q.set('CurrentBank',205);q.m.page(2,rec['bank']);q.set('CurrentBankC',rec['bank']|128);q.m.writes=[]
        c=NesMPU(memory=q.m,pc=address(b,'PnBodyOrderBankStub'));c.sp=0xfd;c.p=0x30;c.a=rec['bank']|128;c.x=73;c.y=19;c.stPushWord(0x5aff)
        return q,c
    rows=[]
    for rec,rotation,flip in cases:
        q,c=setup(rec,rotation,flip);trace=[]
        while c.pc!=0x5b00:
            assert len(trace)<1000;trace.append(c.pc);c.step()
        expected=[get(q,n)for n in fields]
        for kind in ['nmi','irq']:
            for boundary in range(len(trace)):
                q,c=setup(rec,rotation,flip)
                for _ in range(boundary):c.step()
                pc,sp=c.pc,c.sp;regs=(c.a,c.x,c.y,c.p);five=[q.m[i]for i in smc];shadow=q.get('CurrentBankC');bank=q.m.banks[2];before=c.processorCycles
                getattr(c,kind)();steps=0
                while not(c.pc==pc and c.sp==sp):
                    assert steps<60000,(kind,'interrupt timeout',hex(c.pc),q.m.banks)
                    c.step();steps+=1
                assert steps>0,(kind,'not admitted',boundary)
                assert(c.a,c.x,c.y,c.p)==regs,(kind,'foreground AXYP',boundary,regs,(c.a,c.x,c.y,c.p))
                assert [q.m[i]for i in smc]==five and q.get('CurrentBankC')==shadow and q.m.banks[2]==bank
                elapsed=c.processorCycles-before
                for _ in range(1000):
                    if c.pc==0x5b00:break
                    c.step()
                else:raise AssertionError('Foreground did not finish')
                assert [get(q,n)for n in fields]==expected and q.m.banks[1]==77 and q.m.banks[2]==rec['bank']
                rows.append(dict(record=rec['label'],bank=rec['bank'],rotation=rotation,flip=flip,interrupt=kind,boundary=boundary,pc=pc,SP=sp,interrupt_CPU_cycles=elapsed))
    (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
    q=dict(passed=True,native_run=False,component_only=True,ROM_sha256=sha(a.rom),tool_sha256=sha(Path(__file__)),actual_compiled_interrupt_cases=len(rows),NMI_cases=sum(r['interrupt']=='nmi'for r in rows),IRQ_cases=sum(r['interrupt']=='irq'for r in rows),fiveSMC_exact=True,foreground_AXYP_SP_restored=True,actual_C_shadow_bank_restored=True,resumed_selector_graphics_fields_exact=True,cases_sha256=sha(a.output/'cases.json'),limits='Cleared synthetic audio/IRQ state, compiled lag NMI and actual IRQ handler; instruction-boundary ownership proof only. No PPU scanline/IRQ31 timing, real DMC/audio maximum, native controller or constant frame-rate verdict. Complete DrawAll liveness and actual gameplay remain separate.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
