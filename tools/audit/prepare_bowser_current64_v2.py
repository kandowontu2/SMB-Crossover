"""Genuine frozen Bowser v9 source rebase onto the installed Peach/Benj64."""
from pathlib import Path
import difflib,hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/peach-palette-fix-1030-v1';V=R/'build/bowser-functional-host-v9'
BASE=R/'build/coherent62-lives-fixes-v1/joint'
O=R/'build/bowser-current64-v2';J=O/'joint';D=J/'bowser';BT=J/'bt'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,s):write(p,json.dumps(s,indent=2)+'\n')

def main():
 assert not O.exists()
 for p in [P/'handoff.json',V/'handoff.json']:
  q=json.loads(p.read_text())
  for name,h in q['bindings'].items():assert sha(name)==h,(p,name)
 assert sha(P/'joint/candidate.nes')=='f56e55cd69b93821e66548848305cf9822e2ac0e8a25752d7192332cded53b78'
 shutil.copytree(P/'joint',J)
 for name in ['bowser','bt']:shutil.copytree(V/'joint'/name,J/name)
 def relocate(s):
  for root in [P/'joint',V/'joint']:
   s=s.replace(str(root),str(J)).replace(root.as_posix(),J.as_posix())
  return s
 # Apply only actual v9 native source changes against the common dfdb source.
 # Current parent changes in unrelated regions (Benj Select/native physics,
 # Peach palette, CHR assets) survive and cannot be silently overwritten.
 def graft(name):
  a=(BASE/name).read_text(encoding='utf-8');v=(V/'joint'/name).read_text(encoding='utf-8');s=(P/'joint'/name).read_text(encoding='utf-8')
  al=a.splitlines(True);vl=v.splitlines(True)
  for op,lo,hi,nlo,nhi in reversed(difflib.SequenceMatcher(a=al,b=vl,autojunk=False).get_opcodes()):
   if op=='equal':continue
   old=''.join(al[lo:hi]);new=''.join(vl[nlo:nhi])
   if not old:
    before=''.join(al[max(0,lo-2):lo]);after=''.join(al[lo:lo+2]);needle=before+after
    assert s.count(needle)==1,('insert closure',name,lo)
    s=s.replace(needle,before+new+after,1)
   else:
    if s.count(old)==1:s=s.replace(old,new,1)
    else:
     for count in [2,4,8,16]:
      prefix=''.join(al[max(0,lo-count):lo]);needle=prefix+old
      if s.count(needle)==1:
       s=s.replace(needle,prefix+new,1);break
     else:raise AssertionError(('edit closure',name,lo,old[:90]))
  write(J/name,relocate(s))
 for name in ['entrypoint.s','src/character_select.s','screen_render.s','src/mmc5.s',
              'src/full_roster_menu.s','src/full_roster_menu_art.inc','src/new_roster_dispatch.s']:
  graft(name)
 # The private v9 split layout is the dfdb layout plus exactly the granted
 # Bowser/BT partitions. Add the current genuine Benj CHR segment to its
 # retained14KB memory owner; no old resource or endpoint is moved.
 cfg=relocate((V/'joint/private.cfg').read_text(encoding='utf-8'))
 assert 'BENJ_MARIO_CHR:'not in cfg
 cfg=cfg.replace('SEGMENTS {','SEGMENTS {\n BENJ_MARIO_CHR:load=BENJ_RETAINED_CHR_MEM,type=ro,start=$e1400;\n',1)
 write(J/'private.cfg',cfg)
 # Recompute every original target's (high,real bank) from actual f56 symbols,
 # including BmFresh/BmColors; do not carry old compressed metadata forward.
 b=load(P/'joint/candidate.nes');s=(P/'joint/union.s').read_text(encoding='utf-8')
 targets=re.findall(r'<([A-Za-z0-9_]+)',s[s.index('HuLo:'):s.index('HuHi:')]);assert len(targets)==144
 assert targets[15]=='BmFresh' and targets[26]=='BmColors'
 groups={};indices=[]
 for t in targets:
  pair=(address(b,t)>>8,((location(b,t)-16)//8192)|128)
  groups.setdefault(pair,[])
  if t not in groups[pair]:groups[pair].append(t)
  indices.append(list(groups).index(pair))
 reps=[members[0]for members in groups.values()];assert len(reps)==46
 text='HuLo:\n .byte '+','.join('<'+t for t in targets)+'\n'
 text+='HuPairIndex:\n .byte '+','.join(map(str,indices))+'\n'
 text+='HuPairHi:\n .byte '+','.join('>'+t for t in reps)+'\n'
 text+='HuPairBank:\n .byte '+','.join('.lobyte(.bank('+t+')|$80)'for t in reps)+'\n'
 for i,t in enumerate(targets):
  rep=reps[indices[i]]
  text+=f'.assert >{t}=>{rep},lderror,"Actual64 pair high{i}"\n.assert .bank({t})=.bank({rep}),lderror,"Actual64 pair bank{i}"\n'
 s=(V/'joint/union.s').read_text(encoding='utf-8');a=s.index('HuLo:');z=s.index('HuExtendedBT:',a)
 write(J/'union.s',s[:a]+text+s[z:])
 for p in J.rglob('*'):
  if p.is_file()and p.suffix.lower()in['.s','.inc','.cfg']:write(p,relocate(p.read_text(encoding='utf-8')))
 cc=R/'tools/Windows/cc65/bin'
 def run(name,c):
  proof=validate(c,J,cwd=R)
  x=subprocess.run(c,cwd=R,text=True,capture_output=True)
  save(O/(name+'.json'),dict(command=c,validation=proof,returncode=x.returncode,stdout=x.stdout,stderr=x.stderr))
  assert x.returncode==0,(name,x.stderr)
 def asm(folder,name):
  run(folder.name+'-'+name+'-build',[str(cc/'ca65.exe'),'--cpu','6502x','-g','-I',str(D),'-I',str(J),'-I',str(J/'src'),'-I',str(R),'--create-full-dep',str(folder/(name+'.dep')),'-o',str(folder/(name+'.o')),str(folder/(name+'.s'))])
 for name in ['host','core','art','image-tail','load','copy','check','retire','router','preview','cold','stream']:asm(D,name)
 for name in ['core','art','api','loader','router','preview','stream']:asm(BT,name)
 for name in ['main','union']:
  c=json.loads((P/(name+'-build.json')).read_text())['command'][:]
  c[1:1]=['-I',str(J),'-I',str(J/'src'),'--bin-include-dir',str(J)]
  for flag in ['-o','--create-full-dep','--create-dep']:
   if flag in c:c[c.index(flag)+1]=str(J/(name+'.o'if flag=='-o'else name+'.dep'))
  c[-1]=str(J/('entrypoint.s'if name=='main'else'union.s'));run(name+'-build',c)
 c=json.loads((P/'final-link.json').read_text())['command'][:]
 oldmain=str(P/'joint/main.o');oldunion=str(P/'joint/consumer-18.o')
 assert c.count(oldmain)==1 and c.count(oldunion)==1
 c[c.index(oldmain)]=str(J/'main.o');c[c.index(oldunion)]=str(J/'union.o')
 for flag in ['-o','-Ln','-C','-m','--dbgfile','--mapfile']:
  if flag in c:c[c.index(flag)+1]=str(J/Path(c[c.index(flag)+1]).name)
 if '--ld-args'in c:
  at=c.index('--ld-args')+1;v=c[at].split(',')
  for i in range(1,len(v),2):v[i]=str(J/Path(v[i]).name)
  c[at]=','.join(v)
 c += [str(D/(n+'.o'))for n in ['host','core','art','image-tail','load','copy','check','retire','router','preview','cold','stream']]
 c += [str(BT/(n+'.o'))for n in ['core','art','api','loader','router','preview','stream']]
 run('initial-link',c)
 image=(J/'bowser.bin').read_bytes();assert len(image)==8192
 (D/'cookie.bin').write_bytes(bytes([167,27,0,5])+hashlib.sha256(image).digest()[:12])
 for n in ['check','load','stream']:asm(D,n)
 run('final-link',c);prepare(R,J/'candidate.nes')
 nb=load(J/'candidate.nes');nr=nb['raw'];pr=b['raw'];vr=(V/'joint/candidate.nes').read_bytes()
 assert nr[:16]==pr[:16]
 assert nr[514822:514825]==pr[514822:514825]==bytes.fromhex('163027')
 for name in ['ram3.bin','ff-cookie.bin','code.bin','data.bin']:
  assert sha(J/name)==sha(P/'joint'/name)==sha(V/'joint'/name),name
 assert sha(J/'bowser.bin')==sha(V/'joint/bowser.bin')
 assert sha(D/'cookie.bin')==sha(V/'joint/bowser/cookie.bin')
 # Current Benj code/art/state/default callbacks remain genuinely installed.
 for name in ['BmFresh','BmColors','KmNextVariant']:
  assert address(nb,name)==address(b,name)and location(nb,name)==location(b,name),name
 for name in re.findall(r'^\.export\s+([^\n]+)',(P/'joint/union.s').read_text(),re.M):
  for n in name.split(','):
   n=n.strip()
   assert address(nb,n)==address(b,n)and location(nb,n)==location(b,n),n
 for i in range(36):
  off=location(b,'HuEntryBase')+i*16
  assert pr[off:off+11]==nr[off:off+11],i
 # Bound physical donor assets outside owned Bowser/BT streams are unchanged.
 chrstart=16+128*8192
 for page in range(1024):
  if page in range(824,827)or page in range(915,935):continue
  at=chrstart+page*1024;assert nr[at:at+1024]==pr[at:at+1024],('foreign CHR',page)
 public_changes=[n for n,z in b['syms'].items()if n in nb['syms']and z.get('val')!=nb['syms'][n].get('val')]
 save(O/'source-proof.json',dict(passed=True,source=True,native=False,candidate=sha(J/'candidate.nes'),
  parent=sha(P/'joint/candidate.nes'),Bowser_v9=sha(V/'joint/candidate.nes'),ready=66,
  actual_original_targets=targets,pair_groups=len(reps),indices=indices,
  imported_groups=[dict(high=p[0],raw_bank=p[1],members=members)for p,members in groups.items()],
  source_Benj_callbacks=True,Peach_constants_exact=True,FF_Quick_Arthur_payload_cookie_exact=True,
  Bowser_v9_payload_cookie_exact=True,all36_entry_prologues_and_common_public_PCs_exact=True,
  genuine_union_input_replaced=oldunion,actual_source_only_changes=True,changed_symbol_names=public_changes))
 q=dict(source=True,status='CURRENT64_PLUS_BOWSER_TWO_SOURCE_CONTROLS_PENDING',candidate=sha(J/'candidate.nes'),
  parent=sha(P/'joint/candidate.nes'),parent_handoff=sha(P/'handoff.json'),Bowser_v9_handoff=sha(V/'handoff.json'),
  joint=str(J),native=False,installed=False,admitted=False,ready=66,publication_allowed=False,
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'handoff.json',V/'handoff.json',O/'source-proof.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'private.cfg',J/'bowser.bin',D/'cookie.bin']})
 save(O/'source-stage.json',q);save(J/'source-stage.json',q)
 print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))
if __name__=='__main__':main()
