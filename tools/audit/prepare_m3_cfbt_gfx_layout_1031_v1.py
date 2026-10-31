"""Stage2: source-linked byte-identical M3 prefix/67EA/RODATA layout experiment."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from prepare_cv3_dmc_mirror import prepare
P=R/'build/m3-cfbt-source-join-v1';C=P/'joint'
O=R/'build/m3-cfbt-gfx-layout-v1';J=O/'joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,q):write(p,json.dumps(q,indent=2)+'\n')
def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)
def od(p,flag):return subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),flag,str(p)],text=True,capture_output=True,check=True).stdout
def labels(p):return{m[2]:int(m[1],16)for m in re.finditer(r'^al ([0-9A-Fa-f]+) \.([^\s]+)',p.read_text(),re.M)}
def main():
 assert not O.exists();qualified=json.loads((P/'qualification.json').read_text());assert qualified['passed']
 for n,h in qualified['bindings'].items():assert sha(n)==h,n
 assert qualified['candidate']==sha(C/'candidate.nes')=='79634f4581f223293a86d2bae28a0cc8ad05949a24f29695433b806eccf6a4b3'
 link=json.loads((P/'final-link.json').read_text())['command'];objects=[Path(x)for x in link if x.endswith('.o')];assert len(objects)==86
 census=[]
 for p in objects:
  text=od(p,'--dump-segments');segs={m[1]:int(m[2])for m in re.finditer(r'Name:\s*"([^"]*)"(?:(?!Name:)[\s\S])*?Size:\s+(\d+)',text)}
  assert len(segs)==int(re.search(r'Count:\s+(\d+)',text)[1])
  imports=re.findall(r'Name:\s*"([^"]+)"',od(p,'--dump-imports'))
  assert segs.get('RODATA',0)==0 and not any(n.startswith('__RODATA_')for n in imports),p
  census.append(dict(path=str(p),sha256=sha(p),segments=segs,imports=imports))
 assert next(q for q in census if q['path']==str(C/'main.o'))['segments']['M3_GFX']==0x13fd
 shutil.copytree(C,J)
 def rt(s):return s.replace(str(C),str(J)).replace(C.as_posix(),J.as_posix())
 for p in J.rglob('*'):
  if p.is_file()and p.suffix in['.s','.inc','.cfg']:write(p,rt(p.read_text(encoding='utf-8')))
 paths=['src/smb3_mario_art.inc','src/smb3_mario_world_art.inc','smb3plus_float_data.s'];art=J/paths[0];s=art.read_text()
 s=once(s,'.segment "M3_GFX"','.segment "M3_GFX_PREFIX"')
 s=once(s,'MbChrOffsets:.byte 0,4,4,244,0,248,252\n .res 74,$ea','MbChrOffsets:.byte 0,4,4,244,0,248,252\n ; Preserve granted CF A91 AE97..<AEDA. No worker in this stage.\n.segment "RODATA"\n .res 7,$ea');write(art,s)
 for n in paths[1:]:
  p=J/n;write(p,once(p.read_text(),'.segment "M3_GFX"','.segment "RODATA"'))
 stale=[]
 for p in J.rglob('*'):
  if p.suffix in['.s','.inc']and re.search(r'\.segment\s+"M3_GFX"',p.read_text(encoding='utf-8')):stale.append(str(p))
 assert not stale,stale
 cfg=J/'private.cfg';s=cfg.read_text()
 s=once(s,'    X5_NEW_5B: start=$c000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$5b;',
  '    X5_NEW_5B: start=$c000,size=$e97,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5b;\n    CF_P1_RESTORE_ROM_MEM:start=$ae97,size=$43,type=ro,file=%O,fill=yes,fillval=$ea,bank=$5b;\n    X5_NEW_5B_AFTER_CF:start=$ceda,size=$1126,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5b;')
 s=once(s,'    M3_GFX:load=X5_NEW_5B,type=ro,define=yes;','    M3_GFX_PREFIX:load=X5_NEW_5B,type=ro,define=yes;')
 s=once(s,'    RODATA:   load = PRGLow,            type = ro,  define   = yes;','    RODATA:load=X5_NEW_5B_AFTER_CF,type=ro,define=yes; # Source-owned M3 suffix; all86 parent objects audited empty.')
 s=once(s,'ROGUE_AUDIO_UPPER_RAW_0:load=X5_NEW_5B,type=ro,start=$d400,optional=yes;','ROGUE_AUDIO_UPPER_RAW_0:load=X5_NEW_5B_AFTER_CF,type=ro,start=$d400,optional=yes;')
 s=once(s,'SYMBOLS {','SYMBOLS {\n    __M3_GFX_LOAD__:type=export,value=__M3_GFX_PREFIX_LOAD__;\n    __M3_GFX_RUN__:type=export,value=__M3_GFX_PREFIX_RUN__;\n    __M3_GFX_SIZE__:type=export,value=__M3_GFX_PREFIX_SIZE__+$43+__RODATA_SIZE__;');write(cfg,s)
 logs=[]
 def run(n,cmd):
  guard=validate(cmd,J,cwd=R);z=subprocess.run(cmd,cwd=R,text=True,capture_output=True);p=O/(n+'.json');save(p,dict(command=cmd,validation=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));logs.append(p);assert z.returncode==0,(n,z.stderr)
 cmd=[rt(x)for x in json.loads((P/'main-build.json').read_text())['command']];run('main-build',cmd)
 cmd=[rt(x)for x in link];run('final-link',cmd);prepare(R,J/'candidate.nes')
 assert (J/'candidate.nes').read_bytes()==(C/'candidate.nes').read_bytes(),'Layout experiment changed product bytes'
 old,new=[scoped_load(p/'candidate.nes')for p in[C,J]];count=0
 for n,sym in old['syms'].items():
  if'val'not in sym:continue
  assert n in new['syms']and address(old,n)==address(new,n),('Old resolved symbol moved',n);count+=1
 before,after=[labels(p/'candidate.lbl')for p in[C,J]]
 for n in['__M3_GFX_LOAD__','__M3_GFX_RUN__','__M3_GFX_SIZE__']:assert before[n]==after[n],n
 assert [after[n]for n in['__M3_GFX_LOAD__','__M3_GFX_RUN__','__M3_GFX_SIZE__']]==[0xc000,0xc000,0x13fd]
 assert after['__M3_GFX_PREFIX_SIZE__']==0xe97 and after['__RODATA_SIZE__']==0x523 and after['__RODATA_LOAD__']==0xceda
 metadata_exceptions={'__RODATA_LOAD__','__RODATA_RUN__','__RODATA_SIZE__'}
 for n,v in before.items():
  if n not in metadata_exceptions:assert after.get(n)==v,('LBL public/address moved',n,v,after.get(n))
 segtext=od(J/'main.o','--dump-segments');segs={m[1]:int(m[2])for m in re.finditer(r'Name:\s*"([^"]*)"(?:(?!Name:)[\s\S])*?Size:\s+(\d+)',segtext)}
 assert int(re.search(r'Count:\s+(\d+)',segtext)[1])==len(segs)==256 and'M3_GFX'not in segs and segs['M3_GFX_PREFIX']==0xe97 and segs['RODATA']==0x523
 begin=16+91*8192+0xe97;assert new['raw'][begin:begin+67]==bytes([234])*67
 q=dict(passed=True,status='BYTE_IDENTICAL_SOURCE_LAYOUT_ALL_PCS_AND_LEGACY_METADATA_PRESERVED',candidate=sha(J/'candidate.nes'),parent=sha(C/'candidate.nes'),source=True,native=False,installed=False,source_only=True,binary_patch=False,changed_ROM_bytes=0,all_old_resolved_DBG_symbols_exact=count,legacy_M3_metadata=[0xc000,0xc000,0x13fd],all_old_LBL_values_exact_except_unconsumed_RODATA_metadata=sorted(metadata_exceptions),actual_main_segments=256,all86_parent_objects_RODATA_zero_no_imports=True,aggregate_SIZE_expression='__M3_GFX_PREFIX_SIZE__+$43+__RODATA_SIZE__',prefix_gap_suffix_bytes=[0xe97,67,0x523],CF67_worker_absent=True,remaining331_ability_bytes_untouched=True,all_Stage1_controls_apply_by_exact_program_byte_identity=True,no_new_native_claim=True,
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'qualification.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'main.o',cfg,*[J/n for n in paths],*logs]})
 save(O/'parent-object-census.json',census);q['bindings'][str((O/'parent-object-census.json').resolve())]=sha(O/'parent-object-census.json');save(O/'source-stage.json',q);print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))
if __name__=='__main__':main()
