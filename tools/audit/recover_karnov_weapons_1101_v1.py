"""Recover original single/double/triple fireball and boomerang updates."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from recover_karnov_actor_1101_v1 import ROM,EXPECTED,graph,emit
from private_build_outputs_v1 import validate
B=R/'build/karnov-original-source-1101-v1';O=R/'build/karnov-original-weapons-1101-v1'
LO,HI=0xaab2,0xad5a
DISPATCH={0xaab6:9,0xac0f:4,0xac48:8}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
write=lambda p,t:p.write_text(t,encoding='utf-8',newline='\n')


def main():
    O.mkdir(exist_ok=True);S=O/'source';S.mkdir(exist_ok=True);assert not(O/'source-stage.json').exists()
    raw=ROM.read_bytes();assert sha(ROM)==EXPECTED
    m,code,tables,external,ram,reads=graph(raw,lo=LO,hi=HI,dispatch=DISPATCH,extra_bank=(1,11))
    write(S/'original_weapon.inc',emit(m,code,tables,False,lo=LO,hi=HI));write(S/'portable_weapon.inc',emit(m,code,tables,True,lo=LO,hi=HI))
    bank=raw[16+11*8192:16+12*8192];(O/'original-bank11.bin').write_bytes(bank)
    extern='KrDispatch=$c831\n'+''.join(f'KrExternal_{a:04X}=${a:04x}\n'for a in external)
    write(S/'reproduce.s','.setcpu "6502"\n'+extern+''' .segment "BANK"
 .incbin "../original-bank11.bin",0,$ab2
 .include "original_weapon.inc"
 .incbin "../original-bank11.bin",$d5a,$2000-$d5a
''')
    write(S/'reproduce.cfg','MEMORY { BANK:start=$a000,size=$2000,file=%O; }\nSEGMENTS { BANK:load=BANK,type=ro; }\n')
    cm,ccode,ctables,cexternal,cram,creads=graph(raw,lo=0xc2b7,hi=0xc2c7,dispatch={});assert not cexternal and not creads
    write(S/'portable_clear.inc',emit(cm,ccode,ctables,True,lo=0xc2b7,hi=0xc2c7))
    imports=''.join(f'.ifndef KrExternal_{a:04X}\nKrExternal_{a:04X}='+('Kr_C2B7'if a==0xc2b7 else f'${a:04x}')+'\n.endif\n'for a in external)
    write(S/'combined.s',' .include "portable.s"\n'+imports+'''.segment "CODE"
 .include "portable_weapon.inc"
 .include "portable_clear.inc"
.export KrWeaponFrame,KrCombinedEnd
KrWeaponFrame:
 lda KrPointer
 sta KrSaved0
 lda KrPointer+1
 sta KrSaved1
 jsr Kr_AAB2
KrWeaponResult:
 php
 pha
 lda KrSaved0
 sta KrPointer
 lda KrSaved1
 sta KrPointer+1
 pla
 plp
 rts
KrCombinedEnd:
''')
    write(S/'combined.cfg',(B/'source/portable.cfg').read_text())
    cc=R/'tools/Windows/cc65/bin';commands=[]
    for mode in ['reproduce','combined']:
        for command in [[cc/'ca65.exe','-g','-I',S,'-I',B/'source',S/(mode+'.s'),'-o',O/(mode+'.o')],[cc/'ld65.exe','-C',S/(mode+'.cfg'),O/(mode+'.o'),'-o',O/(mode+'.bin'),'--dbgfile',O/(mode+'.dbg'),'-Ln',O/(mode+'.lbl')]]:
            command=list(map(str,command));guard=validate(command,O,cwd=S);q=subprocess.run(command,cwd=S,capture_output=True,text=True);commands.append(dict(command=command,guard=guard,returncode=q.returncode,stderr=q.stderr));assert q.returncode==0,q.stderr
    assert(O/'reproduce.bin').read_bytes()==bank;save(O/'build-commands.json',commands)
    refs=[Path(__file__),R/'tools/audit/recover_karnov_actor_1101_v1.py',ROM,B/'assembly.json',B/'CPU-controls.json',O/'reproduce.bin',O/'combined.bin',O/'combined.dbg',O/'build-commands.json',*[p for p in S.iterdir()if p.is_file()]]
    report=dict(passed=True,source=True,native_port=False,installed=False,donor_sha256=EXPECTED,original_bank11_8KiB_exact=True,semantic_weapon_span=[LO,HI],recovered_instructions=len(code),relocated_pointer_words=len(tables),original_external_calls={f'{a:04X}':[f'{p:04X}'for p in pcs]for a,pcs in external.items()},included_original_clear_helper=[0xc2b7,0xc2c7],remaining_callbacks=['C81D','C3D8'],original_data_reads=list(reads),RAM_fields={f'{a:04X}':v for a,v in ram.items()},scope='Original nine-projectile slots: ordinary/super-fireball updates and four-phase boomerang return, with original catch/reuse versus miss/revert behavior. Assembled beside original controller and original clear helper; CPU differential and actual caller order are qualified separately. Host contacts/rendering/pickups/audio remain required.',bindings={str(p.resolve()):sha(p)for p in refs})
    save(O/'assembly.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['bindings','RAM_fields']}))


if __name__=='__main__':main()
