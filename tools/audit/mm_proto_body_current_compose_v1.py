"""Sparse source build of held OAMf1 plus accepted Proto palette2082; no native."""
from pathlib import Path
import hashlib,json,subprocess,sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_audio_fallback_oc import qualified

R=Path(__file__).resolve().parents[2];B=R/'build'
BASE='8487c439ded9bc6274e1dc8f8e051494fa96ee518553d9c2f382eccf2e71d0e6'
OAM='f1dd0c2390d4f27c373797b695e44b56b94cd12c74d47c2a14d36bc8f34f470f'
CURRENT='2082c19a7364920f828e97f70040d37f1f7059bde1ea136b5c2c4532324abf36'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')

def main():
 baseline=B/'bass_corner_current.nes';donor=B/'mm_body_reserve.nes';current=B/'smb-crossover-mmc5-expanded.nes'
 assert[sha(p)for p in[baseline,donor,current]]==[BASE,OAM,CURRENT]
 frozen=json.loads((B/'mm_body_reserve_handoff.json').read_text());result=json.loads((B/'mm_body_reserve_result.json').read_text())
 leaves=result['sparse_leaves'];assert len(leaves)==4
 for z in leaves.values():assert sha(z['path'])==z['sha256']
 for p in[donor,donor.with_suffix('.dbg'),donor.with_suffix('.lbl'),B/'mm_body_reserve.cfg']:
  assert sha(p)==frozen['artifacts'][str(p)]['sha256']
 original={n:sha(R/n)for n in list(leaves)+['src/entrypoint.s','smb1base-mmc5-expanded.cfg','src/x5_palette.s','src/proto_palette_ack.s']}
 entry=(R/'src/entrypoint.s').read_text()
 for name,z in leaves.items():
  token='.include "'+Path(name).name+'"';assert entry.count(token)==1;entry=entry.replace(token,'.include "'+Path(z['path']).name+'"')
 cfg=(R/'smb1base-mmc5-expanded.cfg').read_text()
 additions=[('    METASPRITE: load = PRGA_04, type = ro;\n','    MM_BODY_RESERVE: load=PRGA_04,type=ro,start=$bf33;\n'),('    MM_BASIC_REMAINDER: load=X5_NEW_42_TAIL,type=ro,start=$b9a8;\n','    MM_BODY_PARTIAL: load=X5_NEW_42_TAIL,type=ro,start=$b9c0;\n')]
 for anchor,line in additions:assert cfg.count(anchor)==1 and line not in cfg;cfg=cfg.replace(anchor,anchor+line)
 ep=B/'mm_body_current_entrypoint.s';ep.write_text(entry)
 conf=B/'mm_body_current.cfg';conf.write_text(cfg)
 c=B/'mm_body_current_main.c';c.write_bytes((R/'src/main.c').read_bytes())
 command=[v.replace('mm_body_reserve.','mm_body_current.').replace('mm_body_reserve_main.c','mm_body_current_main.c').replace('mm_body_reserve_entrypoint.s','mm_body_current_entrypoint.s')for v in result['build_command']]
 assert str(conf)in command and str(ep)in command and str(c)in command
 assert not any(str(p)in command for p in[donor,donor.with_suffix('.dbg'),donor.with_suffix('.lbl'),B/'mm_body_reserve.cfg',B/'mm_body_reserve_entrypoint.s'])
 process=subprocess.run(command,cwd=R,capture_output=True,text=True);(B/'mm_body_current_build.log').write_text(process.stdout+process.stderr);assert process.returncode==0,process.stdout+process.stderr
 sys.path.insert(0,str(R/'tools'));from prepare_cv3_dmc_mirror import prepare
 out=B/'mm_body_current.nes';prepare(R,out)
 old=baseline.read_bytes();oa=donor.read_bytes();now=current.read_bytes();actual=out.read_bytes()
 od={i for i,(x,y)in enumerate(zip(old,oa))if x!=y};pd={i for i,(x,y)in enumerate(zip(old,now))if x!=y}
 assert len(od)==856 and len(pd)==115 and not od&pd
 expected=bytearray(now)
 for i in od:expected[i]=oa[i]
 assert actual==expected,'Canonical source compile must reproduce complete literal disjoint union'
 assert{n:sha(R/n)for n in original}==original and[sha(p)for p in[baseline,donor,current]]==[BASE,OAM,CURRENT]
 def diff(a,z):
  d={k:sum(x!=y for x,y in zip(a[16+k*8192:16+(k+1)*8192],z[16+k*8192:16+(k+1)*8192]))for k in range(128)};return{k:v for k,v in d.items()if v}
 qo,qf,qc,qn=[qualified(p)for p in[baseline,donor,current,out]]
 for n,v in qc.items():assert qn.get(n)==(qf[n]if n in qo and qf.get(n)!=qo[n]else v),n
 proof=dict(passed=True,source_only=True,native_run=False,installed=False,parent_sha256=CURRENT,held_OAM_sha256=OAM,original8487=BASE,candidate_sha256=sha(out),literal_disjoint_union=True,OAM_bytes=856,palette_bytes=115,overlap=0,changed_vs_current=diff(now,actual),changed_vs8487=diff(old,actual),all_current_symbols_follow_exact_OAM_moves=True,current_symbols=len(qc),source_inputs=original,reused_sparse_leaves=leaves,command=command,outputs={str(p):sha(p)for p in[out,out.with_suffix('.dbg'),out.with_suffix('.lbl'),out.with_suffix('.map'),ep,conf,c]},limitations='No new native or renderer CPU run. Existing f1 CPU/source/native evidence remains exact old-ROM scope; this proves actual compiled composition only. Powered Proto native still pending.',tool_sha256=sha(__file__))
 put(B/'mm_body_current_result.json',proof);print(json.dumps({k:proof[k]for k in['passed','candidate_sha256','changed_vs_current','changed_vs8487']},indent=2))

if __name__=='__main__':main()
