"""Private actual-source NrGate compaction on frozen f56a; no native/install."""
from pathlib import Path
import configparser,difflib,hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[1];B=R/'build';OV=B/'nr-router-compact-v1-overlay'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not OV.exists();(OV/'src').mkdir(parents=True)
    parent=B/'celeste-small-chr-v2.nes';assert sha(parent)=='f56a0e154c86c2bcc3577bd99e48dfab71ee61282defa6d16963a2c73e4487c9'
    old=(R/'src/new_roster_dispatch.s').read_text();s=old
    macro=re.search(r'\.macro NrGate Name,Ice,City,Sunny,Legacy\n.*?\.endmacro',s,re.S)[0]
    new='''.macro NrGate Name,Ice,City,Sunny,Legacy
.proc Name
 ; Save A in the EXISTING farcall operand before using Y as the selector.
 ; Current semantics only:20/21/23, every other ID takes exact legacy target.
 sta SafecallA_SMC+1
 php
 tya
 pha
 lda SelectedCharacter
 sec
 sbc #20
 cmp #9
 bcs LegacyRoute
 tay
 lda TargetLo,y
 sta FarcallJmpTarget_SMC+1
 lda TargetHi,y
 sta FarcallJmpTarget_SMC+2
 lda TargetBank,y
 jmp NrTableColdFinish
LegacyRoute:
 pla
 tay
 plp
 lda #<Legacy
 sta FarcallJmpTarget_SMC+1
 lda #>Legacy
 sta FarcallJmpTarget_SMC+2
 lda #.bank(Legacy)|$80
 jmp FarCallCommon
TargetLo:.byte <Ice,<City,<Legacy,<Sunny,<Legacy,<Legacy,<Legacy,<Legacy,<Legacy
TargetHi:.byte >Ice,>City,>Legacy,>Sunny,>Legacy,>Legacy,>Legacy,>Legacy,>Legacy
TargetBank:.byte .bank(Ice)|$80,.bank(City)|$80,.bank(Legacy)|$80,.bank(Sunny)|$80
 .byte .bank(Legacy)|$80,.bank(Legacy)|$80,.bank(Legacy)|$80,.bank(Legacy)|$80,.bank(Legacy)|$80
 .assert *-Name=80,error,"Roster router body must be80B"
 .res 17,$ff                  ; unexecuted; preserve genuine next public PC
 .assert *-Name=97,error,"Roster router original public slot"
.endproc
.endmacro'''
    s=s.replace(macro,new)
    before='.assert * <= $ae00,lderror,"Roster dispatcher overlaps Rogue auxiliary reservation"'
    after='''.assert * = $ad9b,lderror,"Frozen f56a gate end changed"
.proc NrTableColdFinish
 sta NextBank_SMC+1
 pla
 tay
 plp
 ; Genuine existing continuation: first STA is performed above, then actual
 ; LDA CurrentBank overwrites A/N/Z before any caller-live consumer.
 jmp FarCallCommon+3
.endproc
.assert * = $ada4,lderror,"Same-bank cold finish must be9B"
.assert * <= $ae00,lderror,"Roster dispatcher overlaps Rogue auxiliary reservation"'''
    assert s.count(before)==1;s=s.replace(before,after)
    (OV/'src/new_roster_dispatch.s').write_text(s,encoding='utf-8',newline='\n')
    (OV/'smb1base-mmc5-expanded.cfg').write_bytes((R/'smb1base-mmc5-expanded.cfg').read_bytes())
    (B/'nr_router_compact_v1.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='a/src/new_roster_dispatch.s',tofile='b/src/new_roster_dispatch.s')),encoding='utf-8')
    results={}
    for mode in['expanded','mmc3','mmc5']:
        out=B/('nr-router-compact-v1'+(''if mode=='expanded'else'-'+mode)+'.nes')
        cmd=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(OV),'--output',str(out)]
        if mode!='expanded':cmd+=['--flag-off',mode]
        q=subprocess.run(cmd,cwd=R,capture_output=True,text=True);results[mode]=dict(command=cmd,exit=q.returncode,stdout=q.stdout,stderr=q.stderr)
        (B/'nr_router_compact_build_v1.json').write_text(json.dumps(results,indent=2)+'\n')
        assert q.returncode==0,(mode,q.stdout,q.stderr)
    expected={'mmc3':'d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb','mmc5':'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'}
    assert {k:sha(B/('nr-router-compact-v1-'+k+'.nes'))for k in expected}==expected
    newrom=(B/'nr-router-compact-v1.nes').read_bytes();oldrom=parent.read_bytes();ds={k:sum(a!=b for a,b in zip(oldrom[16+k*8192:16+(k+1)*8192],newrom[16+k*8192:16+(k+1)*8192]))for k in range(128)};ds={k:v for k,v in ds.items()if v}
    assert set(ds)=={124}and newrom[:16]==oldrom[:16]and newrom[1048592:]==oldrom[1048592:],ds
    # Independent ca65 assembly of the exact standard staged entrypoint.
    cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini');defs={k:v for d in cfg.values()for k,v in d.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
    dep=B/'nr_router_compact_v1.d';cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-I',str(OV/'src'),'-I',str(R/'src'),'-I',str(R),'--bin-include-dir',str(OV),'--bin-include-dir',str(R),'--create-full-dep',str(dep),'-o',str(B/'nr_router_compact_v1.o')]
    for k,v in defs.items():cmd+=['-D',k+'='+v]
    cmd+=[str(B/'nr-router-compact-v1-objects/entrypoint.s')];q=subprocess.run(cmd,cwd=R,capture_output=True,text=True);assert q.returncode==0,q.stderr
    deps={}
    for word in re.split(r'(?<!\\)\s+',dep.read_text().split(':\t',1)[1].strip().removesuffix(':')):
        f=Path(word.replace('\\ ',' '));f=(f if f.is_absolute()else R/f).resolve();assert f.is_file();deps[str(f)]=sha(f)
    assert str((OV/'src/new_roster_dispatch.s').resolve())in deps and str((R/'src/new_roster_dispatch.s').resolve())not in deps
    proof=dict(passed=True,source_only=True,native_run=False,parent_sha256=sha(parent),ROM_sha256=sha(B/'nr-router-compact-v1.nes'),DBG_sha256=sha(B/'nr-router-compact-v1.dbg'),LBL_sha256=sha(B/'nr-router-compact-v1.lbl'),diff_by_bank=ds,CHR_header_RAM_unchanged=True,ordinary=expected,actual_ASM_dependencies=deps,independent_ca65_command=cmd,source_leaf_sha256=sha(OV/'src/new_roster_dispatch.s'),source_preimage_sha256=sha(R/'src/new_roster_dispatch.s'),builder_sha256=sha(__file__))
    (B/'nr_router_compact_layout_v1.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='actual_ASM_dependencies'},indent=2))

if __name__=='__main__':main()
