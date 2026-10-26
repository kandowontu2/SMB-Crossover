"""Private two-edit common mixer step, independently usable on installed3b."""
from pathlib import Path
import argparse,difflib,json,shutil,subprocess,sys,traceback
from smb3_host_current3b_cpu_v1 import D,R,sha,put
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

PARENTS={'current3b':(D/'root-current-roster-composition-v1','3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'),'hot6':(D/'smb3-host-hot6-v2','64ccd5038c26cabd3c57c4c3ed13b1fe467b275238610f3a227ceaa48e1ac2b6')}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',choices=PARENTS,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();base,parent=PARENTS[a.parent];o=a.output.resolve();assert not o.is_relative_to(R);o.mkdir(parents=True,exist_ok=False)
 try:
  assert sha(base/'candidate.nes')==parent;manifest=json.loads((base/'source-manifest.json').read_text());src=o/'source';src.mkdir()
  for name,h in manifest.items():
   assert sha(base/'source'/name)==h,name;f=src/name;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(base/'source'/name,f)
  changes=[];patch=[]
  def edit(name,edits):
   f=src/name;raw=f.read_bytes();nl='\r\n'if b'\r\n'in raw else'\n';s=raw.decode().replace('\r\n','\n')
   for old,new in edits:assert s.count(old)==1,(name,old,s.count(old));s=s.replace(old,new)
   out=s.replace('\n',nl).encode();f.write_bytes(out);changes.append(dict(path=name,before=sha(base/'source'/name),after=sha(f),old_CRLF=raw.count(b'\r\n'),new_CRLF=out.count(b'\r\n'),old_bareLF=raw.count(b'\n')-raw.count(b'\r\n'),new_bareLF=out.count(b'\n')-out.count(b'\r\n')));patch.extend(difflib.unified_diff(raw.decode().splitlines(True),out.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
  edit('src/guest_audio.s',[('.proc GuestAudioBegin\n  lda SelectedCharacter\n  cmp #CHARACTER_BASS\n  beq :+','.proc GuestAudioBegin\n  lda SelectedCharacter\n  cmp #CHARACTER_PIT\n  bcs :+')])
  # Keep all eight original macro scopes. Only the per-channel admission
  # moves; this avoids synthetic aliases or unrelated macro renumbering.
  old='''  lda #(1 << (I / 4))
  and GuestMixMask
  beq Next
  lda GuestExpansionApu+I'''
  new=''' .if I = 0
  lda #1
  and GuestMixMask
  beq ::X5ExpansionOutputChannel2
 .elseif I = 4
::X5ExpansionOutputChannel2:
  lda #2
  and GuestMixMask
  beq ::X5ExpansionOutputDone
 .endif
  lda GuestExpansionApu+I'''
  tail='''  ; Match the old exhausted loop's A/X/Y and all flags, including carry.
  ldx #8
  ldy #1
  cpx #8
  rts
.endproc'''
  replacement='''::X5ExpansionOutputDone:
  ; Match the old exhausted loop's A/X/Y and all flags, including carry.
  ldx #8
  ldy #1
  cpx #8
  rts
  ; Unreachable capacity retains every following real function entry.
  .res 371-(*-::GuestExpansionFlush),$ea
.endproc'''
  edit('src/mmc5_sfx.s',[(old,new),(tail,replacement)])
  (o/'implementation.patch').write_bytes(''.join(patch).encode());put(o/'source-manifest.json',{str(f.relative_to(src)).replace('\\','/'):sha(f)for f in src.rglob('*')if f.is_file()})
  cmd=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(src),'--output',str(o/'candidate.nes')];r=subprocess.run(cmd,cwd=R,capture_output=True,text=True);put(o/'build-command.json',dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,r.stdout+r.stderr
  if a.parent=='hot6':
   cmd=[sys.executable,str(R/'tools/prepare_smb3_dmc_mirrors.py'),'--source',str(src),'--rom',str(o/'candidate.nes')];r=subprocess.run(cmd,cwd=R,capture_output=True,text=True);put(o/'mirror-command.json',dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,r.stdout+r.stderr
  before,after=(scoped_load(q/'candidate.nes')for q in [base,o]);diff=[]
  assert before['raw'][:16]==after['raw'][:16]and before['raw'][16+128*8192:]==after['raw'][16+128*8192:]
  for bank in range(128):
   n=sum(x!=y for x,y in zip(before['raw'][16+bank*8192:16+(bank+1)*8192],after['raw'][16+bank*8192:16+(bank+1)*8192]))
   if n:diff.append(dict(bank=bank,bytes=n))
  assert [r['bank']for r in diff]==[29],diff
  missing=[];moved=[]
  lo=address(before,'GuestExpansionFlush');hi=address(before,'GuestExpansionSweepClock')
  for name,s in before['syms'].items():
   if name not in after['syms']:missing.append(name);continue
   if s.get('val')!=after['syms'][name].get('val'):
    at=address(before,name);assert lo<=at<hi,('Moved symbol outside changed implementation',name,s,after['syms'][name]);moved.append(dict(name=name,before=s['val'],after=after['syms'][name]['val']))
  assert not missing,missing
  for name in ['GuestAudioBegin','GuestAudioFinish','GuestAudioNativeFlush','GuestExpansionFlush','GuestExpansionSweepClock','GuestExpansionSweepTarget','BassAudioBegin']:
   assert address(before,name)==address(after,name)and before['syms'][name].get('size')==after['syms'][name].get('size'),name
  put(o/'layout.json',dict(passed=True,source_only=True,native_run=False,parent_name=a.parent,parent_directory=str(base).replace('\\','/'),parent_ROM_sha256=parent,ROM_sha256=sha(o/'candidate.nes'),changes=changes,changed_banks=diff,header_all_CHR_and_all_other_banks_exact=True,old_symbols_removed=missing,genuine_private_moved_symbols=moved,all_public_entrypoints_and_function_spans_preserved=True,new_RAM_bytes=0,cache_implemented=False,proof_pending=True,checker_sha256=sha(__file__)))
  print(json.dumps(dict(passed=True,parent=a.parent,ROM_sha256=sha(o/'candidate.nes'),changed_banks=diff,moved_private_symbols=len(moved))))
 except Exception as e:put(o/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
