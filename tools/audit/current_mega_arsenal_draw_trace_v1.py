"""Finite source-CPU actual Knuckle body/render caller trace; no native inference."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import current_mega_arsenal_prepare_v1 as parent
from check_tmnt_render_oa import address,location

def main():
    rom=R/'build/bill_early_cache.nes';assert parent.sha(rom)==parent.EXPECTED
    b=parent.scoped_load(rom);invoke0=parent.Arena.invoke;rows=[];active=None;pending=[]
    names=['DrawMetasprite','SmFreezeNativeFlashDone','MetaspriteRenderLoop','MmReserveBegin','MmReserveFinish']
    hooks={(address(b,n),(location(b,n)-16)//8192):n for n in names}
    def invoke(q,name,*args,**kw):
        nonlocal active,pending
        if name!='GameLoop' or q.get('InvSelected',1)!=3:return invoke0(q,name,*args,**kw)
        source_step=parent.NesMPU.step
        def snapshot(cpu,event):
            ptr=q.get('R0')+256*q.get('R1')
            return dict(event=event,PC=cpu.pc,bank=q.m.banks[(cpu.pc-0x8000)//8192],Cbank=q.m.banks[2],
                        SP=cpu.sp,A=cpu.a,X=cpu.x,Y=cpu.y,P=cpu.p,ptr=ptr,header=q.m[ptr],
                        R0_7=[q.get('R0',i) for i in range(8)],OAMoffset=q.get('CurrentOAMOffset'),
                        rotation=q.get('GuestOamRotationActive'),bodyStart=q.get('RgOamPlayerStart'),
                        hpPointer=[q.get('HpNativeDrawLo'),q.get('HpNativeDrawHi')])
        def step(cpu):
            nonlocal active,pending
            shot=next((i for i in range(10) if q.get('RgShotType',i)==11 and q.get('RgShotAge',i)<=6),None)
            if shot is not None:
                if active is None:
                    active=dict(shot_age=q.get('RgShotAge',shot),events=[]);rows.append(active)
                k=q.m.banks[(cpu.pc-0x8000)//8192] if cpu.pc>=0x8000 else -1
                n=hooks.get((cpu.pc,k))
                if n:
                    row=snapshot(cpu,n);active['events'].append(row)
                    if n=='MetaspriteRenderLoop':
                        sp=cpu.sp;ret=(q.m[256+(sp+1)%256]+256*q.m[256+(sp+2)%256]+1)&65535
                        pending.append(dict(pc=ret,sp=(sp+2)&255,row=row))
                for old in pending[:]:
                    if old['pc']==cpu.pc and old['sp']==cpu.sp:
                        old['row']['return']=snapshot(cpu,'actual-caller-continuation')
                        pending.remove(old)
            source_step(cpu)
        parent.NesMPU.step=step
        try:return invoke0(q,name,*args,**kw)
        finally:parent.NesMPU.step=source_step;active=None;pending=[]
    parent.Arena.invoke=invoke
    try:proof=parent.campaign(b,0)
    finally:parent.Arena.invoke=invoke0
    assert proof['passed'] and rows
    out=R/'build/current-9ea-mega-knuckle-draw-source-v1.json'
    out.write_text(json.dumps(dict(source_CPU_only=True,native_match_claim=False,ROM_sha256=parent.EXPECTED,
        full_GameLoop_calls=proof['complete_GameLoop_calls'],rows=rows,tool_sha256=parent.sha(Path(__file__)),
        limitation='Genuine full CPU campaign and immediate source return observations; original native item03 has no saved hardware OAM/CHR, so actual first wrong owner still needs passive native evidence.'),indent=2)+'\n')
    print(json.dumps(dict(output=str(out),sha256=parent.sha(out),rows=len(rows),render_calls=[dict(age=r['shot_age'],calls=[e for e in r['events'] if e['event']=='MetaspriteRenderLoop']) for r in rows[:4]])))

if __name__=='__main__':main()
