"""Stage1: genuine cumulative e54 M3 source graft onto immutable final9b."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/m3-cfbt-source-join-plan-v2'
C=R/'build/bt-native-world-source-v2/joint'
E=R/'build/smb3plus-low-table-factor-host-1031-v4/joint'
A=R/'build/bowser-playable-jump-v1/joint'
O=R/'build/m3-cfbt-source-join-v1';J=O/'joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,q):write(p,json.dumps(q,indent=2)+'\n')
def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)
def main():
 assert not O.exists();plan=json.loads((P/'plan.json').read_text())
 for n,h in plan['bindings'].items():assert sha(n)==h,n
 assert sha(P/'plan.json')=='a5cb014739e567565930c7e399c492128d0a03932edbad57cf777a0d76f9eb39'
 assert sha(C/'candidate.nes')==plan['source_base']and sha(E/'candidate.nes')==plan['cumulative_M3']
 recipes=json.loads((P/'actual-recipes.json').read_text());shutil.copytree(C,J)
 roots=[C,R/'build/bt-current-cf-component-v2/joint',R/'build/cf-bt-shared-transport-v3/joint',E,R/'build/smb3plus-current66-source-1031-v2/joint']
 def rt(s):
  for root in roots:s=s.replace(str(root),str(J)).replace(root.as_posix(),J.as_posix())
  return s
 for p in J.rglob('*'):
  if p.is_file()and p.suffix in['.s','.inc','.cfg']:write(p,rt(p.read_text(encoding='utf-8')))
 for n in plan['M3_modules']:write(J/n,rt((E/n).read_text(encoding='utf-8')))
 for n in plan['helpers']+['smb3plus-chr.s']:write(J/n,rt((E/n).read_text(encoding='utf-8')))
 for n in['toad-smb3plus-body.chr','peach-smb3plus-body.chr']:shutil.copyfile(E/n,J/n)
 names=J/'src/new_roster_dispatch.s';s=names.read_text();s=once(s,'  lda #28\n  clc\n  adc M3Variant\n  jmp NameIndex\n','  jmp MbMenuNameSelect\n  .res 6,$ea\n');write(names,s)
 menu=J/'src/character_select.s';s=menu.read_text();s=once(s,'  lda M3Variant\n  eor #1\n  sta M3Variant\n','  inc M3Variant\n  lda M3Variant\n  and #3\n  sta M3Variant\n')
 s=once(s,'  .res 12,$ea\nGbPitNavContinue:','  .res 9,$ea ; Genuine four-identity M3 cycle within existing span.\nGbPitNavContinue:');write(menu,s)
 entry=J/'entrypoint.s';s=entry.read_text()
 for n in plan['helpers']:
  assert f'.include "{n}"'not in s;s+='\n.include "'+n+'"\n'
 write(entry,s)
 cfg=J/'private.cfg';s=cfg.read_text();assert 'CF_CHR_POST:start=$f2400,size=$dc00' in s and'SMB3PLUS_BODY_CHR:'not in s
 m=re.search(r'^\s*BENJ_MARIO_CHR:[^\n]+\n',s,re.M);assert m;s=s[:m.end()]+'    SMB3PLUS_BODY_CHR:load=CF_CHR_POST,type=ro,start=$f2400;\n'+s[m.end():];write(cfg,s)
 assert (J/'union.s').read_text()==rt((C/'union.s').read_text())
 assert (J/'src/full_roster_menu.s').read_text()==rt((C/'src/full_roster_menu.s').read_text())
 assert 'M3_GFX_PREFIX'not in s and'CF_P1_RESTORE_ROM_MEM'not in s
 logs=[]
 def run(n,cmd):
  guard=validate(cmd,J,cwd=R);z=subprocess.run(cmd,cwd=R,text=True,capture_output=True)
  p=O/(n+'.json');save(p,dict(command=cmd,validation=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));logs.append(p);assert z.returncode==0,(n,z.stderr)
 for n in['main','union']:
  cmd=[rt(x)for x in recipes[n]['command']]
  cmd[1:1]=['-I',str(J),'-I',str(J/'src'),'--bin-include-dir',str(J)]
  cmd[-1]=str(J/('entrypoint.s'if n=='main'else'union.s'))
  for flag in['-o','--create-full-dep','--create-dep','-l','--listing']:
   if flag in cmd:cmd[cmd.index(flag)+1]=str(J/(n+'.o'if flag=='-o'else n+'.dep'if'dep'in flag else n+'.lst'))
  if not any(x in cmd for x in['--create-full-dep','--create-dep']):cmd[1:1]=['--create-full-dep',str(J/(n+'.dep'))]
  run(n+'-build',cmd)
 cmd=[rt(x)for x in recipes['M3_CHR']['command']];run('chr-build',cmd)
 cmd=[rt(x)for x in recipes['link']['command']]
 assert cmd.count(str(J/'main.o'))==1 and cmd.count(str(J/'union.o'))==1
 cmd.append(str(J/'smb3plus-chr.o'));run('final-link',cmd);prepare(R,J/'candidate.nes')
 old,ancestor,source,new=[scoped_load(p/'candidate.nes')for p in[C,A,E,J]]
 expected=bytes(y if x!=y else z for x,y,z in zip(ancestor['raw'],source['raw'],old['raw']))
 assert new['raw']==expected,'Source child differs from exact disjoint oracle; never use oracle bytes to construct product'
 ch=16+128*8192
 assert new['raw'][:16]==old['raw'][:16]and new['raw'][ch:ch+969*1024]==old['raw'][ch:ch+969*1024]and new['raw'][ch+1019*1024:]==old['raw'][ch+1019*1024:]
 for bank in[119,120,125,127]:
  lo=16+bank*8192;assert new['raw'][lo:lo+8192]==old['raw'][lo:lo+8192]
 for n in['bt/cache.bin','bt/cookie.bin','bowser.bin','bowser/cookie.bin','cf-stream.bin','cf-cookie.bin','ram3.bin','code.bin','data.bin','ff-cookie.bin']:
  assert sha(C/n)==sha(J/n),n
 census=json.loads((P/'actual-object-census.json').read_text());exports=set()
 for row in census:
  for n in row['exports']:
   if n in old['syms']and'val'in old['syms'][n]:
    assert n in new['syms']and address(old,n)==address(new,n),('Current source export moved',n);exports.add(n)
 # Every qualified e54 M3 entry/data/helper address survives exactly; source-private
 # old66 rewritten palette labels were already explicitly retired in e54.
 for n,sym in source['syms'].items():
  if sym.get('type')=='lab'and(n.startswith(('M3','Mb'))or n in['MbChrOffsets']):
   assert n in new['syms']and address(new,n)==address(source,n),('Qualified M3 PC moved',n)
 delta=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
 q=dict(status='GENUINE_CUMULATIVE_M3_ON_FINAL_CFBT_SOURCE_CONTROLS_PENDING',source=True,native=False,installed=False,candidate=sha(J/'candidate.nes'),base=sha(C/'candidate.nes'),cumulative_M3=sha(E/'candidate.nes'),source_only=True,binary_overlay=False,exact_disjoint_source_oracle=True,changed_bytes=len(delta),old_resolved_object_exports_exact=len(exports),all_qualified_M3_PCs_exact=True,header_fixed_DMC_other_CHR_exact=True,all_parent_CF_BT_BW_Quick_Ar_FF_images_cookies_exact=True,compressed46group_union_preserved=True,whole_M3_GFX_retained=True,CF67_worker_absent=True,remaining331_ability_bytes_untouched=True,
  limitations=['No new native claim. Source controls must rebind to this final hash.','CF/BT remain pending; inherited menus/lifecycle/source32/B020223 contracts preserved.','Donor ground-pound/custom stomp delay/special art/kick SFX remain unfinished.'],
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'plan.json',P/'actual-recipes.json',P/'actual-object-census.json',C.parent/'handoff.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',cfg,entry,names,menu,J/'union.s',J/'src/full_roster_menu.s',*[J/n for n in plan['M3_modules']+plan['helpers']],J/'smb3plus-chr.s',J/'toad-smb3plus-body.chr',J/'peach-smb3plus-body.chr',*logs]})
 save(O/'source-stage.json',q);print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))
if __name__=='__main__':main()
