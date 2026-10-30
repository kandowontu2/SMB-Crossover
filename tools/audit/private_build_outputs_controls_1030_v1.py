"""Exercise real historical output escapes and explicit safe cc65 recipes."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import private_build_outputs_v1 as G
O=R/'build/private-output-guard-controls-1030-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists();O.mkdir();rows=[];files={Path(__file__),Path(G.__file__)}
    def check(name,cmd,want):
        try:r=G.validate(cmd,O,cwd=R)
        except G.UnsafeBuildOutput as e:
            assert not want,(name,str(e));rows.append(dict(name=name,rejected=True,reason=str(e)))
        else:
            assert want,(name,r);rows.append(dict(name=name,rejected=False,outputs=r['outputs']))
    old=R/'build/arthur-expanded-ready-v2/joint/main-build-v3.json'
    h=json.loads(old.read_text());cmd=h['command'];files.add(old)
    check('actual_old_Arthur_main_outputs',cmd,False)
    safe=cmd[:]
    for flag,name in[('-o','safe-main.o'),('--create-full-dep','safe-main.dep')]:
        i=safe.index(flag);safe[i+1]=str(O/name)
    check('same_real_sources_private_object_and_dep',safe,True)
    bad=safe[:];bad[bad.index('--create-full-dep')+1]=str(R/'build/arthur-expanded-ready-v2/joint/main.dep')
    check('private_object_but_frozen_dep',bad,False)
    cfg=O/'safe.cfg';cfg.write_text('MEMORY { A:start=$a000,size=$2000,type=ro,file=%O; B:start=$c000,size=$2000,type=rw,file="'+(O/'ram3.bin').as_posix()+'"; }\n',newline='\n')
    linker=R/'tools/Windows/cc65/bin/cl65.exe'
    link=[str(linker),'-C',str(cfg),'-o',str(O/'candidate.nes'),'-Ln',str(O/'candidate.lbl'),
          '-m',str(O/'candidate.map'),'--ld-args','--dbgfile,'+str(O/'candidate.dbg'),str(O/'safe-main.o')]
    check('private_ROM_DBG_LBL_map_and_RAM3',link,True)
    bad=link[:];bad[bad.index('--ld-args')+1]='--dbgfile,'+str(R/'build/current-character-composition-v2/joint/candidate.dbg')
    check('private_ROM_but_frozen_DBG',bad,False)
    badcfg=O/'unsafe-sidefile.cfg';badcfg.write_text('MEMORY { A:start=$a000,size=$2000,type=rw,file="'+(R/'build/current-character-composition-v2/joint/ram3.bin').as_posix()+'"; }\n',newline='\n')
    bad=link[:];bad[bad.index('-C')+1]=str(badcfg)
    check('private_ROM_but_frozen_cfg_RAM3',bad,False)
    check('implicit_compiler_output',link+[str(R/'src/source.s')],False)
    check('opaque_response_file',safe+['@hidden-options.rsp'],False)
    files|={cfg,badcfg}
    recovered=[]
    for folder in['arthur-expanded-ready-v2','celeste-menu-name-arthur-v2','arthur-expanded-host-v1','current-character-composition-v2']:
        p=R/'build'/folder/('source-stage-handoff-v2.json'if folder=='current-character-composition-v2'else'handoff.json')
        h=json.loads(p.read_text());count=0
        for n,v in h['bindings'].items():assert sha(n)==v,n;count+=1
        files.add(p);recovered.append(dict(folder=folder,verified_bindings=count,receipt_sha256=sha(p)))
    proof=dict(passed=True,native=False,compiler_executed=False,cases=rows,
        restored_original_packets=recovered,source_object_and_ROM_bindings_exact=True,
        bindings={str(p.resolve()):sha(p)for p in sorted(files)})
    (O/'controls.json').write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=True,cases=len(rows),restored_packet_bindings=sum(x['verified_bindings']for x in recovered))),flush=True)


if __name__=='__main__':main()
