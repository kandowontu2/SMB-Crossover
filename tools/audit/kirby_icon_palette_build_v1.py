"""Private eight-attribute Kirby world-icon/shell palette repair; never install."""
from pathlib import Path
import hashlib,json,re,subprocess,difflib,sys
R=Path(__file__).resolve().parents[2];B=R/'build';sys.path.insert(0,str(R/'tools'))
from prepare_cv3_dmc_mirror import prepare
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_audio_fallback_oc import qualified
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
SHA='bdf9ca2bfe69ee93ca85f1b5e5319e474d9f01aa641c79a58cd9bd602253c40e';P='kirby_world_icon_palette';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n')
def command(original,out,entry,mapper=None):
 cmd=[];i=0
 while i<len(original):
  arg=original[i]
  if arg in['-m','-Ln','-o']:cmd.extend([arg,str(out.with_suffix({'-m':'.map','-Ln':'.lbl','-o':'.nes'}[arg]))]);i+=2;continue
  if arg=='--ld-args':cmd.extend([arg,'--dbgfile,'+str(out.with_suffix('.dbg'))]);i+=2;continue
  if arg in['--asm-define','-D']and mapper:
   value=original[i+1];name=value.split('=',1)[0]
   if name=='ENABLE_MMC5_EXPANDED':i+=2;continue
   if name in['MAPPER_MMC3','MAPPER_MMC5']:value=name+'='+str(int(name=='MAPPER_'+mapper.upper()))
   cmd.extend([arg,value]);i+=2;continue
  if arg=='-C'and mapper:cmd.extend([arg,str(R/'smb1base.cfg')]);i+=2;continue
  cmd.append(str(entry)if i==len(original)-1 else arg);i+=1
 return cmd
def link(cmd,out):
 p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);out.with_suffix('.build.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stdout+p.stderr
def main():
 parent=B/'cv3_life_gain_watch.nes';assert sha(parent)==SHA;out=B/(P+'.nes');assert not out.exists()
 source=R/'src/kirby_copy_icons.inc';raw=source.read_bytes();text=raw.decode();assert'\r\n'in text
 changed=[]
 for icon,count in[(1,2),(6,2),(8,4)]:
  pattern=rf'(KbIcon{icon}:\r\n\.byte )([^\r\n]+)';matches=list(re.finditer(pattern,text));assert len(matches)==1;m=matches[0];values=[int(v)for v in m.group(2).split(',')];assert values[0]==count*4
  for part in range(count):
   at=2+part*4;old=values[at];assert old&3==0;values[at]=(old&252)|1;changed.append(dict(icon=icon,record_offset=at,old=old,new=values[at]))
  text=text[:m.start(2)]+','.join(str(v)for v in values)+text[m.end(2):]
 leaf=B/(P+'_icons.inc');leaf.write_bytes(text.encode());ag=B/(P+'_kirby.s');original=(R/'src/kirby.s').read_bytes();needle=b'.include "kirby_copy_icons.inc"';assert original.count(needle)==1;ag.write_bytes(original.replace(needle,b'.include "'+leaf.name.encode()+b'"'))
 entry=B/(P+'_entrypoint.s');er=(R/'src/entrypoint.s').read_bytes();needle=b'.include "kirby.s"';assert er.count(needle)==1;entry.write_bytes(er.replace(needle,b'.include "'+ag.name.encode()+b'"'))
 template=json.loads((B/'cv3_life_gain_watch_build.json').read_text())['command'];cmd=command(template,out,entry);link(cmd,out);prepare(R,out)
 old,new=parent.read_bytes(),out.read_bytes();delta=[i for i,(a,b)in enumerate(zip(old,new))if a!=b];ob,nb=scoped_load(parent),scoped_load(out)
 allowed={location(ob,'KbIcon'+str(z['icon']))+z['record_offset']:z for z in changed};assert len(old)==len(new)and set(delta)==set(allowed)and len(delta)==8
 for at,z in allowed.items():assert old[at]==z['old']and new[at]==z['new']and old[at]&252==new[at]&252
 qo,qn=qualified(parent),qualified(out);assert not{k:(v,qn.get(k))for k,v in qo.items()if qn.get(k)!=v}
 patch=B/(P+'_implementation.patch');patch.write_text(''.join(difflib.unified_diff(raw.decode().splitlines(True),leaf.read_bytes().decode().splitlines(True),fromfile='src/kirby_copy_icons.inc',tofile='src/kirby_copy_icons.inc')),encoding='utf-8',newline='')
 ordinary=[]
 for mapper,want in[('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
  dest=B/(P+'_'+mapper+'_flagoff.nes');assert not dest.exists();c=command(template,dest,entry,mapper);link(c,dest);assert sha(dest)==want;ordinary.append(dict(mapper=mapper,sha256=want,whole_exact=True,command=c))
 paths=[Path(__file__),parent,parent.with_suffix('.dbg'),source,R/'src/kirby.s',R/'src/entrypoint.s',leaf,ag,entry,patch,out,out.with_suffix('.dbg'),out.with_suffix('.lbl'),out.with_suffix('.map'),out.with_suffix('.cv3-mirror.json'),R/'tools/prepare_cv3_dmc_mirror.py']
 receipt=B/(P+'_build.json');put(receipt,dict(passed=True,source_only=True,native_run=False,parent_sha256=SHA,candidate_sha256=sha(out),changed_bytes=8,changed_banks=sorted({(i-16)//8192 for i in delta}),changes=changed,all_other_ROM_header_CHR_bytes_exact=True,all_existing_qualified_symbols_exact=True,old_qualified_symbols=len(qo),new_RAM=0,code_changes=0,CPU_cycle_delta=0,ordinary=ordinary,source_overlay={'src/kirby_copy_icons.inc':str(leaf)},command=cmd,bindings={str(p):sha(p)for p in paths}));print(json.dumps(dict(passed=True,ROM_sha256=sha(out),receipt=str(receipt),sha256=sha(receipt),changed_bank=(delta[0]-16)//8192)))
if __name__=='__main__':main()
