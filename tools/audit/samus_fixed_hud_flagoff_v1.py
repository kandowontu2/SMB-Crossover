"""Two sparse ordinary source-overlay builds; no packer/emulator/primary writes."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[2];B=R/'build';P='samus_fixed_hud_current4a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
EXPECTED=dict(mmc3='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb',mmc5='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')

def main():
 handoff=B/(P+'_handoff.json');assert sha(handoff)=='6c0cfe26bee48671b38c8cd70044e7c9a51293d4b7acd948ddc7621b304599b8'
 h=json.loads(handoff.read_text());assert all(sha(q['path'])==q['sha256']for q in h['bindings'])
 watched=[R/'src/entrypoint.s',R/'src/remaining_weapons.s',R/'tools/reference/pack_chr.py',R/'chr/mmc5/sprites_enemies.chr',R/'chr/characters/packed-mmc3.chr',R/'chr/characters/packed-mmc5.chr',R/'chr/characters/packed-mmc5-expanded.chr',B/'smb-crossover-mmc5-expanded.nes',handoff]
 before={str(p):sha(p)for p in watched};z=json.loads((B/(P+'_build.json')).read_text());rows=[];outputs=[]
 # Canonical builder's real flagoff policy excludes the expanded-only mirror
 # postprocessor. It asserts2MiB input and must NOT be forced onto these768KiB
 # ordinary builds. Keep its genuine DBG/LBL/MAP and same final metadata checks.
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
    suffix={'-m':'.map','-Ln':'.lbl','-o':'.nes'}[arg];cmd.extend([arg,str(out.with_suffix(suffix))]);i+=2;continue
   cmd.append(arg);i+=1
  assert not any(v.startswith('ENABLE_MMC5_EXPANDED=')for v in cmd)
  assert cmd[-2:]==z['command'][-2:],'Reuse exact sparse main/entrypoint with all genuine leaf aliases'
  result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
  log=out.with_suffix('.build.log');log.write_text(result.stdout+result.stderr);assert result.returncode==0,result.stdout+result.stderr
  raw=out.read_bytes();assert len(raw)==786448 and raw==baseline.read_bytes()
  actual=(raw[6]>>4)|(raw[7]&240)|((raw[8]&15)<<8);assert actual==(4 if mapper=='mmc3'else 5)
  assert len(raw)==16+raw[4]*16384+raw[5]*8192
  labels={v[2].lstrip('.'):int(v[1],16)for line in out.with_suffix('.lbl').read_text().splitlines()if len(v:=line.split())==3}
  assert 'SamusFixedHudRecord'not in labels and'SamusFixedMissileHud'not in labels
  metadata=dict(output=str(out),sha256=sha(out),bytes=len(raw),mapper=actual,expanded=False,extra_chr_sha256=None)
  mp=out.with_suffix('.build.json');mp.write_text(json.dumps(metadata,indent=2)+'\n',newline='\n')
  outputs.extend([out,out.with_suffix('.dbg'),out.with_suffix('.lbl'),out.with_suffix('.map'),log,mp])
  rows.append(dict(mapper=mapper,passed=True,baseline=str(baseline),baseline_sha256=EXPECTED[mapper],output=str(out),sha256=sha(out),bytes=len(raw),whole_binary_exact=True,compiled_expanded_helper_absent=True,command=cmd,expanded_flag='not defined; actual source default0',postprocessor='Canonical flagoff branch: expanded-only CV3 mirror intentionally NOT invoked; no other postprocessor applies. Real compiler/linker DBG/LBL/MAP and header/mapper/size checks emitted.',metadata_sha256=sha(mp)))
 assert before=={str(p):sha(p)for p in watched}
 assert all(sha(q['path'])==q['sha256']for q in h['bindings'])
 proof=dict(passed=True,source_only=True,native_run=False,addendum_to_handoff_sha256=sha(handoff),candidate_expanded_sha256=h['ROM_sha256'],ordinary_binary_cases=rows,source_overlay_reused_without_edits=True,no_packer_main=True,no_source_runtime_tree_copies=True,canonical_and_frozen_inputs_unchanged=before,bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in [Path(__file__),R/'tools/build_mmc5_expanded.py',R/'tools/prepare_cv3_dmc_mirror.py',R/'smb1base.cfg',B/(P+'_build.json'),handoff,*outputs]])
 p=B/(P+'_flagoff.json');assert not p.exists();p.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
 print(json.dumps(dict(passed=True,proof_sha256=sha(p),bindings=len(proof['bindings']),cases=[dict(mapper=x['mapper'],sha256=x['sha256'])for x in rows])))
if __name__=='__main__':main()
