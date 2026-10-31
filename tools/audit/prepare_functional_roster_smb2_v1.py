"""Source-compose corrected SMB2 producer and real shared ingress on ready54.

Pass the frozen corrected own-producer directory. Every actual compiler and
linker destination is validated below this new private packet before running.
"""
from pathlib import Path
import argparse,difflib,hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address
P=R/'build/functional-roster-ready54-v1/joint';Q=R/'build/current-character-quick-ui-v13/joint'
S=R/'build/smb2-current-unlock-source-v13';L=R/'build/smb2-current-unlock-late-v14'
O=R/'build/functional-roster-smb2-v1';N=O/'joint'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(p):
 d=json.loads(Path(p).read_text());v=d['bindings']
 if isinstance(v,dict):
  for n,h in v.items():assert sha(n)==h,n
 else:
  for x in v:assert sha(x['path'])==x['sha256'],x['path']
 return d
def sub(t,a,b):assert t.count(a)==1,(a,t.count(a));return t.replace(a,b)
def patch_union(t):
 t='.import S2ServiceVeneers,S2BoundaryLateUI\n'+t
 t=sub(t,'::HuQClass:\n cmp #9\n jmp HuQDecide','::HuQClass:\n cmp #25\n jmp HuS2Decide')
 edits={
 'HuStatus':'::HuS2Decide:\n beq HuS2High\n jmp HuS2Foreign',
 'HuBounce':'::HuS2Foreign:\n cmp #9\n jmp HuQDecide',
 'HuWorldPalette':'::HuS2High:\n lda #>S2ServiceVeneers\n bne HuS2StoreHigh\n nop',
 'HuPowerup':'::HuS2StoreHigh:\n sta FarcallJmpTarget_SMC+2\n bne HuS2Bank',
 'HuWeaponTail':'::HuS2Bank:\n lda #.lobyte(.bank(S2ServiceVeneers)|$80)\n jmp HuExtendedSet'}
 for name,body in edits.items():
  a=t.index('.proc '+name+'\n');z=t.index('.endproc',a);part=t[a:z]
  part=sub(part,' .res 5,$ff',body);t=t[:a]+part+t[z:]
 a=t.index('.proc HuLateUiDirect\n');z=t.index('.endproc',a)
 part=sub(t[a:z],'HuTailFar ResetPalStar','HuTailFar S2BoundaryLateUI');t=t[:a]+part+t[z:]
 t+='\n.assert .hibyte(S2ServiceVeneers)<>0,lderror,"S2 genuine page-high branch"\n'
 return t
def patch_only(t):
 # Only these private gates supply Y=0..15; source P is restored by
 # GmNrFinish before any actual worker. Move the existing Rare JMP onto
 # Quick's existing JMP, so the accepted Quick path falls straight into it.
 t=sub(t,' cmp #22\n beq Rare\n cmp #32\n beq Rare',' cmp #25\n beq Rare\n cmp #22\n beq Rare\n cmp #32\n beq Rare')
 t=sub(t,'Legacy:\n tya\n clc\n adc #16\n tay\nOwn:','Legacy:\n tya\n ora #16\n tay\nOwn:')
 t=sub(t,'::GmOnlyRare:\nRare:jmp HuOnlyRare\n','')
 # Scope-local Rare references above become the genuine global relocated
 # symbol. This does not change the independent GmNrIndex::Rare hash path.
 a=t.index('::GmOnlyCommon:\n');z=t.index('.endscope',a)
 part=t[a:z];part=part.replace('beq Rare','beq GmOnlyRare');t=t[:a]+part+t[z:]
 t=sub(t,' beq GmOnlyLegacy\n jmp GmOnlyRare\n',' beq GmOnlyLegacy\n::GmOnlyRare:\n jmp HuOnlyRare\n')
 return t
def main():
 p=argparse.ArgumentParser();p.add_argument('--producer',type=Path,required=True);a=p.parse_args();D=a.producer.resolve()
 assert not O.exists();verify(P.parent/'handoff.json');verify(S/'handoff.json');verify(L/'handoff.json');verify(D/'handoff.json')
 # This is the corrected v15 semantics, not the rejected v13/v14 reset-chain.
 host=(D/'smb2/smb2_roster_host_v5.s').read_text()
 assert 'S2TypedTail S2TypedScene,JnResetDispatch'in host or ' farcall JnResetDispatch'in host
 assert ' farcall QwMenuResolve'in host and ' farcall QwSceneInit'in host
 O.mkdir();shutil.copytree(P,N)
 sources=[Q,P,S,L,D]
 def retarget(t):
  for old in sources:t=t.replace(str(old),str(N)).replace(old.as_posix(),N.as_posix())
  return t
 for f in N.rglob('*'):
  if f.is_file()and f.suffix in['.s','.inc','.cfg']:
   x=f.read_text();y=retarget(x)
   if x!=y:f.write_text(y,newline='\n')
 # Genuine producer-owned native boundary/Roll sources, with root's three
 # current410-byte source fixes explicitly protected from replacement.
 protected={'river_city_required_ink_v1.inc','river_city_shared_palette_art.inc','chip_dale_render.s'}
 for f in(S/'src').glob('*'):
  if f.is_file():assert f.name not in protected;shutil.copyfile(f,N/'src'/f.name)
 (N/'smb2').mkdir(exist_ok=True)
 for folder in[S/'smb2',D/'smb2']:
  for f in folder.glob('*'):
   if f.is_file():shutil.copyfile(f,N/'smb2'/f.name)
 for name in['component.s','nmi-c82.s','gm-nmi.s','entrypoint.s']:
  f=D/name if(D/name).is_file()else S/name
  (N/name).write_text(retarget(f.read_text()),newline='\n')
 (N/'private.cfg').write_text(retarget((D/'private.cfg').read_text()),newline='\n')
 changed=[]
 def edit(relative,fn):
  f=N/relative;before=f.read_text();after=fn(before);f.write_text(after,newline='\n')
  changed.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='ready54/'+relative,tofile='SMB2/'+relative))
 edit('union.s',patch_union)
 edit('src/new_roster_dispatch.s',patch_only)
 edit('src/character_select.s',lambda t:sub(t,'farcall QwMenuResolve,jmp','farcall S2MenuResolve,jmp'))
 edit('screen_render.s',lambda t:sub(t,'farcall QwSceneInit ;','farcall S2InitScreenPrepare ;'))
 edit('src/full_roster_menu.s',lambda t:sub(t,' lda $5fe3\n and #3\n clc\n adc #10\n bne Pending',' lda $5fe3\n and #3\n clc\n adc #10\n clc\n rts'))
 # Existing main recipe auto-imports native symbols; explicit source imports
 # make the actual new lifecycle pointer operands unambiguous.
 f=N/'entrypoint.s';f.write_text(f.read_text()+'\n.import S2MenuResolve,S2InitScreenPrepare\n',newline='\n')
 (O/'shared-source.patch').write_text(''.join(changed),newline='\n')
 commands=[]
 def add(log,name,source=None):
  c=[retarget(x)for x in json.loads(log.read_text())['command']]
  c[1:1]=['-I',str(N/'src'),'-I',str(N/'smb2'),'-I',str(N)]
  if source:c[-1]=str(N/source)
  # Output basenames are copied from genuine recipes, but never inherited
  # destinations. This covers object+dep even when the input was read-only.
  for flag in['-o','--create-full-dep','--create-dep']:
   if flag in c:c[c.index(flag)+1]=str(N/Path(c[c.index(flag)+1]).name)
  commands.append((c,name));return c
 add(D/'component-build.json','component-build','component.s')
 add(S/'nmi-c82-build.json','nmi-c82-build','nmi-c82.s')
 add(S/'gm-nmi-build.json','gm-nmi-build','gm-nmi.s')
 add(S/'main-build.json','main-build','entrypoint.s')
 union_logs=[]
 for f in S.glob('consumer-*-build.json'):
  c=json.loads(f.read_text())['command']
  if Path(c[-1]).name=='union.s':union_logs.append(f)
 assert len(union_logs)==1,union_logs
 uc=add(union_logs[0],'union-build','union.s');old_union=json.loads(union_logs[0].read_text())['command'];old_union=old_union[old_union.index('-o')+1]
 link=[retarget(x)for x in json.loads((D/'final-link-build.json').read_text())['command']]
 # Other relocated Roll/common importers are real immutable peer objects.
 # Only Main, union, common and owned S2 objects are newly compiled here.
 for i,x in enumerate(link):
  original=json.loads((D/'final-link-build.json').read_text())['command'][i]
  if original.endswith('.o'):
   if original==old_union:link[i]=uc[uc.index('-o')+1]
   elif Path(original).name not in['main.o','component.o','gm-nmi.o','nmi-c82.o','dmc-clones.o']:link[i]=original
 link=[x for x in link if not x.endswith('dmc-clones.o')]
 first=link[:];commands.append((first,'first-link'))
 validations=[dict(step=n,validation=validate(c,N,cwd=R))for c,n in commands]
 (O/'output-preflight.json').write_text(json.dumps(validations,indent=2)+'\n')
 def run(c,name):
  validate(c,N,cwd=R);z=subprocess.run(c,cwd=R,text=True,capture_output=True)
  (O/(name+'.json')).write_text(json.dumps(dict(command=c,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n');assert z.returncode==0,(name,z.stderr)
 for c,name in commands:run(c,name)
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,N/'candidate.nes');fixed=(N/'candidate.nes').read_bytes()[16+127*8192:16+128*8192];(N/'final127.bin').write_bytes(fixed)
 # Real source-produced 119/120 clones are rebound to this exact final127.
 f=S/'dmc-clones.s';ds=f.read_text();ds=ds.replace(str(S/'final127.bin').replace('\\','/'),str(N/'final127.bin').replace('\\','/'))
 assert ds.count((N/'final127.bin').as_posix())==9
 (N/'dmc-clones.s').write_text(ds,newline='\n')
 cc=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'-g','-o',str(N/'dmc-clones.o'),str(N/'dmc-clones.s')];run(cc,'dmc-clones-build')
 run(link+[str(N/'dmc-clones.o')],'final-link');prepare(R,N/'candidate.nes')
 assert(N/'candidate.nes').read_bytes()[16+127*8192:16+128*8192]==fixed
 for name in['code.bin','data.bin','ram3.bin']:assert(N/name).read_bytes()==(P/name).read_bytes(),name
 for name in protected:assert sha(N/'src'/name)==sha(P/'src'/name),name
 old,new=[load(x/'candidate.nes')for x in[P,N]]
 h=address(old,'HuEntryBase')
 for i in range(36):
  # The exact established11-byte public prologue is unchanged. Its private
  # padding island has the only new service lookup code.
  bank=79;at=16+bank*8192+(h+i*16&8191)
  assert old['raw'][at:at+11]==new['raw'][at:at+11],i
 assert address(new,'HuEnd')<=0xc000
 d=dict(status='SOURCE_LINKED_SMB2_SHARED_INGRESS_CPU_PENDING',candidate=sha(N/'candidate.nes'),parent=sha(P/'candidate.nes'),producer_handoff=sha(D/'handoff.json'),native=False,installed=False,
  intended_ready=58,protected_RCR_Chip_sources_exact=True,Quick_Arthur_FF_payloads_exact=True,all36_Hu_public11B_prologues_exact=True,all_new_producers_private=True,
  rejection='v13/v14 TypedScene QwSceneInit ancestry was wrong; corrected producer must retain genuine JnResetDispatch. Actual InitScreen independently calls S2InitScreenPrepare.',
  bindings={str(f.resolve()):sha(f)for f in[Path(__file__),P.parent/'handoff.json',S/'handoff.json',L/'handoff.json',D/'handoff.json',O/'shared-source.patch',O/'output-preflight.json']})
 (O/'source-stage.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
 verify(P.parent/'handoff.json');verify(S/'handoff.json');verify(L/'handoff.json');verify(D/'handoff.json')
if __name__=='__main__':main()
