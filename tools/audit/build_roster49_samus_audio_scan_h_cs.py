"""Private MMC3 port of the already-used MMC5 Metroid flag-scan replacement."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-samus-audio-scan-h'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not H.exists();H.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-head-axis-g/manifest.json';assert sha(cp)=='feacfe9cf513d6c57dde8a4f2990e0bbd6c14ecda533d971747ad0011cee0fd0';c=json.loads(cp.read_text())
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);assert total+300000000<80000000000
 for n,h in c['source_hashes'].items():
  assert sha(R/n)==sha(Path(c['source_directory'])/n)==h,n
  p=H/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
 for n,h in c['generated11'].items():
  assert sha(R/'build/generated'/n)==h
  p=H/'source/build/generated'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'build/generated'/n,p)
 p=H/'source/tools/prepare_guest_audio.py';s=p.read_text();a=s.index('        0x14dd:(');z=s.index('\n    }',a);old=s[a:z]
 assert "'.if ::MAPPER_MMC5'" in old and 'span(0x14dd,0x14ef)'in old
 s=s[:a]+'''        0x14dd:([
                 '  .byte $f0,$07,$0a,$b0,$0d,$c8,$c8,$d0,$f9,$a0,$10,$38,$ea,$ad',
                 '  .word '+flags_word,'  .byte $ea,$60'],18),'''+s[z:]
 s=s.replace('# MMC3 retains its previous bytes. Tests compare actual compiled routines,','# Both mappers use the same flag-scan replacement. Tests compare routines,')
 p.write_text(s)
 with(H/'prepare.log').open('wb')as log:q=subprocess.run([sys.executable,str(p)],cwd=H/'source',stdout=log,stderr=subprocess.STDOUT)
 assert q.returncode==0,'Private generated audio preparation'
 changed=[n for n,h in c['generated11'].items()if sha(H/'source/build/generated'/n)!=h];assert set(changed)=={f'guest-audio/metroid{k}.inc'for k in [0,1,2,4,5]},changed
 driver=V/'root49-sophia-head-axis-d/build.py';shutil.copyfile(driver,H/'build.py')
 pre=dict(script_sha256=sha(__file__),checkpoint_G_sha256=sha(cp),source_hashes={n:sha(H/'source'/n)for n in c['source_hashes']},generated11={n:sha(H/'source/build/generated'/n)for n in c['generated11']},changed_sources=['tools/prepare_guest_audio.py'],changed_generated=changed,original_special=old,build_driver_sha256=sha(driver),workspace_before=total,phase_cap=300000000,reserve=50000000,global_cap=80000000000,scope='Private same-size MMC3 flag-scan optimization. MMC5 and both baselines must stay literal G. Not installed, no native fidelity or ordinary-clear claim.',main_changed=False)
 (H/'preparation.json').write_text(json.dumps(pre,indent=2)+'\n')
 rows=[]
 for mp in ['mmc3','mmc5']:
  for baseline in [False,True]:
   stem='smb-crossover-'+mp+('-baseline'if baseline else'')
   with(H/(stem+'.log')).open('wb')as log:q=subprocess.run([sys.executable,str(H/'build.py'),'--mapper',mp]+(['--baseline']if baseline else[]),cwd=R,stdout=log,stderr=subprocess.STDOUT)
   assert q.returncode==0,(mp,baseline)
   p=H/'source/build'/(stem+'.nes');before=(cp.parent/p.name).read_bytes();after=p.read_bytes();assert len(before)==len(after)
   delta=[dict(offset=i,old=a,new=b)for i,(a,b)in enumerate(zip(before,after))if a!=b]
   if baseline or mp=='mmc5':assert not delta
   else:
    assert delta and all(0x14dd<=(z['offset']-16)%8192<0x14ef for z in delta),delta
   rows.append(dict(mapper=mp,baseline=baseline,changed_bytes=len(delta),delta=delta,artifacts={ext:dict(path=str(p.with_suffix('.'+ext).relative_to(R)),sha256=sha(p.with_suffix('.'+ext)),bytes=p.with_suffix('.'+ext).stat().st_size)for ext in ['nes','dbg','lbl','map']}))
   print(stem,len(delta),'changed bytes',flush=True)
 assert [n for n,h in c['source_hashes'].items()if pre['source_hashes'][n]!=h]==['tools/prepare_guest_audio.py']
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h
 out=H/'build-review.json';out.write_text(json.dumps(dict(status='PASS_PRIVATE_H_SAME_SIZE_SCAN_BUILD_MMC5_AND_BASELINES_LITERAL_G',preparation_sha256=sha(H/'preparation.json'),builds=rows,main_changed=False,native_validation_pending=True,goal_complete=False),indent=2)+'\n');print('REVIEW',sha(out))
if __name__=='__main__':main()
