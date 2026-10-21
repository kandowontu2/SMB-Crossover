from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];O=R/'build/verification/root49-sophia-block-shift-hn'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=O/'foreign-review-ht.json';assert not out.exists();groups=[]
 for name in ['baseline','megaman-block-alignment','link-block-alignment','simon-adjacent-blocks','samus-solid-blocks','sophia-collision-equivalence']:
  for mapper in ['mmc3','mmc5']:
   rom=O/'source/build'/f'smb-crossover-{mapper}.nes';folder=O/f'foreign-{mapper}-{name}'
   args=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),str(R/'tests'/(name+'.lua')),str(rom),'--timeout','180']
   (O/f'foreign-{mapper}-{name}-command.json').write_text(json.dumps(args),encoding='utf-8')
   with(O/f'foreign-{mapper}-{name}-host.log').open('wb')as log:q=subprocess.run(args,cwd=R,stdout=log,stderr=subprocess.STDOUT)
   groups.append(dict(mapper=mapper,test=name,exit=q.returncode,rom_sha256=sha(rom),files={str(p.relative_to(O)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in folder.rglob('*')if p.is_file()}))
   print(name,mapper,q.returncode,flush=True)
 out.write_text(json.dumps(dict(status='PASS_12_UNCHANGED_NATIVE_BOOT_BLOCK_ALIGNMENT_AND_SOPHIA_PROJECTILE_CONTROLS'if all(g['exit']==0 for g in groups)else'RETAINED_FOREIGN_NATIVE_FAILURE',script_sha256=sha(__file__),groups=groups),indent=2),encoding='utf-8')
 print('FOREIGN',sha(out),flush=True)
if __name__=='__main__':main()
