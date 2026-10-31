"""Real ISR cuts through source-owned late lives callback/mapper/borrowed SFC."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];P=Path(__file__).with_name('smb2_late_lives_controls_v1.py')
s=P.read_text(encoding='utf-8').split('def main():',1)[0].replace("J=R/'build/smb2-late-lives-palette-v4/joint'","J=R/'build/smb2-late-lives-palette-v6/joint'")
ns={'__file__':str(P),'__name__':'_actual_late_source_defs'};exec(compile(s,str(P),'exec'),ns)
A,C,M,J=map(ns.get,['A','C','M','J']);O=R/'build/smb2-late-lives-isr-v1';assert not O.exists();O.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clone(m):
 import copy
 return copy.deepcopy(m,{id(m.bundle):m.bundle,id(m.ROM_banks):m.ROM_banks,id(m.lab):m.lab})
m=ns['seed'](J);M.put(m,OperMode=1,ScreenRoutineTask=6,NmiDisable=255,BackgroundColorCtrl=0,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=30,S2PaletteAck=0)
neg=json.loads((R/'build/smb2-late-lives-controls-v1/controls.json').read_text())['checks']['reproduced_native_3721_pending_ROM3_then_text_overwrite'];at=m.lab['VRAM_Buffer1'];m.ram[at:at+30]=bytes(neg['after_actual_native_lives_text']['buffer'][:30]);m.ram[at+30]=0
# Start with genuine native C88, exercising both pending C mapper seams.
m.page(2,88);m.set('CurrentBankC',216);base=clone(m);z=C.invoke(m,'S2MenuStatus',A=1,X=87,Y=30,P=0x30);reference=list(m.ram[at:at+38]);ranges=[(74,m.lab['S2MenuStatus'],m.lab['S2MenuStatus']+71),(80,m.lab['S2TextStatusC'],m.lab['S2TextStatusC']+162)]
sites=sorted(set((tags[(pc-32768)//8192]&127,pc)for tags,pc in z['trace']if pc>=32768 and any(tags[(pc-32768)//8192]==bank|128 and lo<=pc<hi for bank,lo,hi in ranges)))
q=dict(passed=False,native=False,rows=[])
try:
 for bank,pc in sites:
  for kind in['NMI','IRQ']:
   m=clone(base);done=[False]
   def cut(c):
    if done[0]or c.pc!=pc or m.tags[(pc-32768)//8192]!=bank|128:return
    done[0]=True;regs=(c.pc,c.a,c.x,c.y,c.p,c.sp);maps=m.tags[:];shadow=[m.get('CurrentBank'),m.get('CurrentBankC')];smc=bytes(m.ram[0x15a:0x17b]);live=bytes(m.ram[0x101+c.sp:512]);scratch=bytes(m.ram[m.lab['R0']:m.lab['R0']+8]);pending=maps[2]!=shadow[1]
    if pending:assert m[c.pc]in[0x8c,0x8d]and m[c.pc+1]==0x16 and m[c.pc+2]==0x51,('genuine pending C publisher',kind,pc,m[c.pc])
    if kind=='NMI':c.nmi()
    else:
     assert not c.p&4;m.ram[0x5204]=128;c.irq()
    for _ in range(100000):
     if(c.pc,c.sp)==(regs[0],regs[5]):break
     m.pc=c.pc;assert m[c.pc]!=0;c.step()
    else:raise AssertionError('actual vector bounded')
    expected=maps[:]
    if kind=='NMI'and pending:expected[2]=shadow[1]
    assert(c.pc,c.a,c.x,c.y,c.p,c.sp)==regs and m.tags==expected and[m.get('CurrentBank'),m.get('CurrentBankC')]==shadow and bytes(m.ram[0x15a:0x17b])==smc and bytes(m.ram[0x101+c.sp:512])==live and bytes(m.ram[m.lab['R0']:m.lab['R0']+8])==scratch,(kind,pc,regs,m.tags,expected)
   zz=C.invoke(m,'S2MenuStatus',A=1,X=87,Y=30,P=0x30,hook=cut);assert done[0]and list(m.ram[at:at+38])==reference and m.tags==base.tags
   A.interrupt(m,0);assert list(m.vram[0x3f11:0x3f14])==[1,22,39]and m.vram[0x3f00]==15
   q['rows'].append(dict(bank=bank,pc=pc,kind=kind,CPU=zz['CPU']))
 q['passed']=True
except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
finally:
 paths={Path(__file__),P,J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',Path(A.__file__),Path(M.__file__),Path(C.__file__)}
 q.update(cases=len(q['rows']),sites=len(sites),all_AXYP_SP_livepage1_SMC33_scratch_maps_and_real_PPU=True,bindings={str(p.resolve()):sha(p)for p in paths});p=O/'controls.json';p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=q['passed'],error=q.get('error'),cases=len(q['rows']),path=str(p),sha256=sha(p))),flush=True)
