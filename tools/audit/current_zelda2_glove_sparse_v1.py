"""Sparse expanded-only Z2 exclusion from the legacy Link Easy probe. No native."""
from pathlib import Path
import configparser,difflib,hashlib,json,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
from check_tmnt_audio_fallback_oc import qualified

R=Path(__file__).resolve().parents[2];B=R/'build';PREFIX='zelda2_easy_glove'
BASE=B/'roster-20261028-fixes.nes';EXPECTED='ee1152a49deae31e82d202159310fa3719cbcfd85de571fd1b9ac15a1cd2a7b3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:dict(path=str(Path(p).resolve()),bytes=Path(p).stat().st_size,sha256=sha(p))

def main():
    assert sha(BASE)==EXPECTED
    old=scoped_load(BASE);original=(R/'src/easy_lsr.s').read_text()
    token='Link:\n  lda MmBulletType\n  cmp #14\n';assert original.count(token)==1
    text=original.replace(token,'Link:\n .if ::ENABLE_MMC5_EXPANDED\n  jsr Z2LegacyEasyProbeType\n .else\n  lda MmBulletType\n .endif\n  cmp #14\n')
    token='.endproc\n.popseg';assert text.count(token)==1
    helper='''.endproc
 .if ::ENABLE_MMC5_EXPANDED
; Link-only entry. Valid variant0/1: preserve original type/C for classic,
; return type0 for ZeldaII so its real sword point is never replaced by a
; legacy whip rectangle. X/Y/RAM unchanged; original caller does CMP#14.
.proc Z2LegacyEasyProbeType
  lda Z2Variant
  eor #1
  lsr a
  bcc Done
  lda MmBulletType
Done:rts
.endproc
 .endif
.popseg'''
    text=text.replace(token,helper)
    end=address(old,'EasyWhipProbeRadius')+int(old['syms']['EasyWhipProbeRadius']['size'],0)
    assert end==0xbff4 and old['raw'][16+22*8192+0x1ff4:16+23*8192]==bytes([255])*12
    leaf=B/(PREFIX+'_easy_lsr.s')
    if leaf.exists():assert leaf.read_text()==text
    else:leaf.write_text(text,newline='\n')
    ep=B/(PREFIX+'_entrypoint.s');raw=(R/'src/entrypoint.s').read_bytes();token=b'.include "easy_lsr.s"';assert raw.count(token)==1
    ep.write_bytes(raw.replace(token,('.include "'+leaf.name+'"').encode()))
    main=B/(PREFIX+'_main.c');main.write_bytes((R/'src/main.c').read_bytes())
    cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini');defs={k:v for s in cfg.values()for k,v in s.items()}
    outputs=[]
    for mapper,expanded,cfgname,suffix,expect in [(5,1,'smb1base-mmc5-expanded.cfg','',None),(3,0,'smb1base.cfg','_mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),(5,0,'smb1base.cfg','_mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        out=B/(PREFIX+suffix+'.nes')
        d=dict(defs);d.update(MAPPER_MMC3=str(int(mapper==3)),MAPPER_MMC5=str(int(mapper==5)),ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED=str(expanded))
        cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(R/cfgname),'--ld-args','--dbgfile,'+str(out.with_suffix('.dbg')),'--include-dir',str(R),'--asm-include-dir',str(B),'--asm-include-dir',str(R/'src'),'--asm-include-dir',str(R),'--bin-include-dir',str(R),'-m',str(out.with_suffix('.map')),'-Ln',str(out.with_suffix('.lbl')),'-o',str(out)]
        for k,v in d.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
        cmd += [str(main),str(ep)]
        if not out.exists():
            z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);out.with_suffix('.build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,z.stdout+z.stderr
            if expanded:prepare(R,out)
        if expect:assert sha(out)==expect,('Ordinary exact',out,sha(out))
        outputs.append(dict(ROM=bind(out),command=cmd,ordinary_whole_exact=bool(expect)))
    new=scoped_load(B/(PREFIX+'.nes'));diff=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y]
    site=location(old,'EasyWhipEligible::Link');tail=16+22*8192+0x1ff4
    assert set(diff)==set(range(site,site+3))|set(range(tail,tail+12)) and len(diff)==15
    assert address(new,'Z2LegacyEasyProbeType')==0xbff4 and int(new['syms']['Z2LegacyEasyProbeType']['size'],0)==12
    before,after=qualified(BASE),qualified(B/(PREFIX+'.nes'))
    moves={str(k):[v,after.get(k)]for k,v in before.items()if after.get(k)!=v};assert not {k:v for k,v in moves.items()if 'LOCAL-MACRO_SYMBOL-'not in k},moves
    patch=B/(PREFIX+'.patch');patch.write_text(''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile='ee115/src/easy_lsr.s',tofile='private/src/easy_lsr.s')),newline='\n')
    proof=B/(PREFIX+'_build.json');assert not proof.exists()
    paths=[Path(__file__),BASE,BASE.with_suffix('.dbg'),BASE.with_suffix('.lbl'),leaf,ep,main,patch,R/'src/easy_lsr.s',R/'src/entrypoint.s',R/'src/main.c',R/'smb1base-mmc5-expanded.cfg',R/'smb1base.cfg',R/'build_options.ini']
    proof.write_text(json.dumps(dict(passed=True,native_run=False,installed=False,parent_sha256=EXPECTED,candidate_sha256=sha(B/(PREFIX+'.nes')),outputs=outputs,changed_bytes=15,changed_bank=22,old_qualified_PCs_exact=True,macro_symbol_moves=moves,header_CHR_RAM_cfg_NMI_IRQ_allotherbanks_exact=True,placement=dict(helper_pc=0xbff4,bytes=12,actual_old_FF_bytes=12),source_scope='Only Link branch of existing eligibility: valid Z2Variant0 keeps original type/C; variant1 returns type0 and existing native CMP14 rejects. No character5/foreign branch change. All caller addresses and RAM layouts retained.',bindings=[bind(p)for p in paths]),indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=True,proof=str(proof),sha256=sha(proof),candidate=sha(B/(PREFIX+'.nes')))))

if __name__=='__main__':main()
