"""Two private ordinary builds using the actual sparse Proto source overlay."""
from pathlib import Path
import json,subprocess
from current_mega_arsenal_prepare_v1 import sha

R=Path(__file__).resolve().parents[2];B=R/'build';P='proto_normal_palette_ack_9ea'
EXPECTED={'mmc3':'d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb',
          'mmc5':'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'}

def main():
    proof_path=B/(P+'_build.json');z=json.loads(proof_path.read_text())
    assert z['candidate_sha256']=='cb8fce744c3f95aaf11e1e52b605535dce8a301bb7a7ca5d7a73c186c79ebc62'
    assert all(sha(p)==v for p,v in z['bindings'].items())
    watched=[R/'src/entrypoint.s',R/'src/proto_palette_ack.s',B/'smb-crossover-mmc5-expanded.nes',B/'bill_early_cache.nes',B/(P+'.nes')]
    before={str(p):sha(p)for p in watched};rows=[];outputs=[]
    builder=(R/'tools/build_mmc5_expanded.py').read_text()
    assert "else:options.pop('ENABLE_MMC5_EXPANDED',None)"in builder
    assert "if flag:\n  from prepare_cv3_dmc_mirror import prepare\n  prepare(root,out)"in builder
    for mapper in ['mmc3','mmc5']:
        baseline=B/f'mm_body_adoption_{mapper}_flagoff.nes';assert sha(baseline)==EXPECTED[mapper]
        out=B/(P+'_'+mapper+'_flagoff.nes');assert not out.exists();cmd=[];i=0;old=z['command']
        while i<len(old):
            arg=old[i]
            if arg in ['--asm-define','-D']:
                value=old[i+1];name=value.split('=',1)[0]
                if name=='ENABLE_MMC5_EXPANDED':i+=2;continue
                if name=='MAPPER_MMC3':value='MAPPER_MMC3='+str(int(mapper=='mmc3'))
                if name=='MAPPER_MMC5':value='MAPPER_MMC5='+str(int(mapper=='mmc5'))
                cmd.extend([arg,value]);i+=2;continue
            if arg=='-C':cmd.extend([arg,str(R/'smb1base.cfg')]);i+=2;continue
            if arg=='--ld-args':cmd.extend([arg,'--dbgfile,'+str(out.with_suffix('.dbg'))]);i+=2;continue
            if arg in ['-m','-Ln','-o']:
                cmd.extend([arg,str(out.with_suffix({'-m':'.map','-Ln':'.lbl','-o':'.nes'}[arg]))]);i+=2;continue
            cmd.append(arg);i+=1
        assert cmd[-2:]==old[-2:] and not any(v.startswith('ENABLE_MMC5_EXPANDED=')for v in cmd)
        p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        log=out.with_suffix('.build.log');log.write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
        raw=out.read_bytes();assert raw==baseline.read_bytes() and len(raw)==786448
        actual=(raw[6]>>4)|(raw[7]&240)|((raw[8]&15)<<8);assert actual==(4 if mapper=='mmc3'else 5)
        assert len(raw)==16+raw[4]*16384+raw[5]*8192
        assert 'ProtoFixAndAcknowledgePalette'not in out.with_suffix('.lbl').read_text()
        outputs.extend([out,out.with_suffix('.dbg'),out.with_suffix('.lbl'),out.with_suffix('.map'),log])
        rows.append(dict(mapper=mapper,passed=True,sha256=sha(out),whole_binary_exact=True,baseline=str(baseline),command=cmd,
                         expanded_flag='Not defined; actual source default0',postprocessor='Canonical flagoff policy excludes expanded-only mirror. Actual linker output/header/mapper checked.'))
    assert before=={str(p):sha(p)for p in watched}
    result=dict(passed=True,source_only=True,native_run=False,expanded_candidate_sha256=z['candidate_sha256'],cases=rows,
                sparse_overlay_reused=True,no_packer_or_primary_writes=True,protected_inputs_unchanged=before,
                bindings={str(p):sha(p)for p in [Path(__file__),proof_path,R/'tools/build_mmc5_expanded.py',R/'tools/prepare_cv3_dmc_mirror.py',R/'smb1base.cfg',*outputs]})
    out=B/(P+'_flagoff.json');assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=True,proof=str(out),sha256=sha(out))))

if __name__=='__main__':main()
