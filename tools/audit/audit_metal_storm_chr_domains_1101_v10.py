"""Exact current upper1 tables and source-owned CHR consumer domain inventory."""
from pathlib import Path
import ast,collections,hashlib,json,re,zipfile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/metal-storm-chr-closure-1101-v10';V9=ROOT/'build/metal-storm-coexistence-1101-v9';V8=ROOT/'build/metal-storm-resource-host-1101-v8'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
TARGETS=set([247,248,249,250]+list(range(494,503))+list(range(827,832)))
def main():
 currentpath=OUT/'current-consumer-inputs.json';cur=json.loads(currentpath.read_text());oldpath=ROOT/'build/karnov-carrier-final-1101-v6/finite-writer-domains.json';old=json.loads(oldpath.read_text());closurepath=ROOT/'build/karnov-carrier-closure-1101-v4/closure.json';closure=json.loads(closurepath.read_text());sources={};texts={}
 def read(path):
  path=Path(path).as_posix()
  if path in texts:return texts[path]
  ref=old['source_bindings'].get(path,closure['sources'].get(path));assert ref,path;p=Path(path)
  if p.exists()and sha(p)==ref['sha256']:data=p.read_bytes();origin='hash-verified-live'
  else:
   with zipfile.ZipFile(ROOT/'build/_recovery/legacy-sources-2026-10-31.zip')as z:data=z.read('objects/'+ref['sha256'])
   origin='one-exact-indexed-object-in-memory'
  assert hashlib.sha256(data).hexdigest()==ref['sha256'];sources[path]=dict(sha256=ref['sha256'],bytes=len(data),origin=origin);texts[path]=data.decode();return texts[path]
 def named(name):
  p=next(p for p in closure['sources']if Path(p).name==name);return read(p)
 env=dict(PROTO_CHR_FIRST=256,PROTO_HURT_BANK_OFFSET=11)
 assert 'PROTO_CHR_FIRST=256'in named('protoman.s')
 def val(t):
  t=re.sub(r'\$([0-9a-f]+)',r'0x\1',t,flags=re.I)
  if t.startswith('.lobyte('):return val(t[8:-1])&255
  if t.startswith('.hibyte('):return val(t[8:-1])>>8
  if t.startswith('<'):return val(t[1:])&255
  n=ast.parse(t,mode='eval').body
  def v(n):
   if isinstance(n,ast.Constant):return n.value
   if isinstance(n,ast.Name):return env[n.id]
   if isinstance(n,ast.BinOp)and isinstance(n.op,ast.Add):return v(n.left)+v(n.right)
   raise AssertionError(ast.dump(n))
  return v(n)
 tables={};domains={};clauses={}
 def table(text,name):
  m=re.search(r'(?m)^'+name+r':\s*(.*)',text);assert m,name;rest=m[1]+'\n'+text[m.end():];lines=[];values=[]
  for line in rest.splitlines():
   line=line.split(';',1)[0].strip()
   if not line:continue
   if not line.startswith('.byte '):break
   lines.append(line);values.extend(val(x.strip())for x in line[6:].split(','))
  assert values,name
  if name in cur['current_table_bytes']:
   actual=bytes.fromhex(cur['current_table_bytes'][name]['hex']);assert bytes(values)==actual,(name,len(values),len(actual))
  tables[name]=dict(count=len(values),values=values,source_clause='\n'.join(lines),current_linked_match=name in cur['current_table_bytes']);return values
 proto=named('protoman_art.inc');domains['ProtoMan body']=[256+x for x in table(proto,'ProtoPoseChrLo')];assert table(proto,'ProtoPoseChrHi')==[1]*27
 dw=named('darkwing_art.inc');domains['Darkwing body']=[256+x for x in table(dw,'DwPoseBankLo')];assert 'DW_WEAPON_CHR=302'in dw;domains['Darkwing weapons']=[302,303]
 z=named('zelda2_link_art.inc');domains['ZeldaII body']=[lo+256*hi for lo,hi in zip(table(z,'Z2PoseChrLo'),table(z,'Z2PoseChrHi'))];domains['ZeldaII weapon']=[335]
 domains['Kirby body']=[256+x for x in table(named('kirby_art.inc'),'KbBodyChr')];domains['MetaKnight body']=[256+x for x in table(named('meta_knight_art.inc'),'MkBodyChr')]
 cd=named('chip_dale_art.inc');domains['ChipDale body']=[lo+256*hi for lo,hi in zip(table(cd,'CdPoseChrLo'),table(cd,'CdPoseChrHi'))]
 assert re.search(r'CdWorldChr\s*=\s*425',cd);domains['ChipDale world']=[425]
 cv=named('cv3_art.inc')
 for variant in range(1,4):
  for face in'RL':
   base=f'Cv3V{variant}Chr{face}';domains[base]=[lo+256*hi for lo,hi in zip(table(cv,base+'Lo'),table(cv,base+'Upper'))]
 domains['CV3 weapons']=[518,519,520,521,522,523]
 roll=named('roll_art.inc');lo=table(roll,'RlPoolChrLo');hi=table(roll,'RlPoolChrHi');domains['Roll body/effect']=[256*h+((l+delta)&255)for l,h in zip(lo,hi)for delta in[0,2,3]]
 vic=read(next(p for p in old['source_bindings']if p.endswith('/vic_render.s')));body=vic.split('VvBodyChr:',1)[1].split('.popseg',1)[0]
 expected={2:382,3:384,45:386,46:388,47:390,48:392};assert '.repeat 49,I'in body and'.byte <380'in body
 for key,n in expected.items():assert re.search(r'\.e?l?s?e?if I='+str(key)+r'\s+\.byte <'+str(n),body)or re.search(r'\.if I='+str(key)+r'\s+\.byte <'+str(n),body)
 domains['VicViper body']=[expected.get(i,380)for i in range(49)];clauses['Vic body source']=body
 domains['VicParodius HUD']=[394,395,396,397,398]
 thtable=read(next(p for p in closure['sources']if p.endswith('/thomas-native-render/tables.s')));load=table(thtable,'ThLoadCHR');domains['Thomas cold carrier']=[256+x for x in load];assert 511 in domains['Thomas cold carrier']
 thmeta=ROOT/'build/thomas-platform-chr/metadata.bin';meta=thmeta.read_bytes();assert hashlib.sha256(meta).hexdigest()=='121d84a9c8744d463db9ecf95d05a124e3404c2b97dee8e7c5a8735968c56c84'
 windows=list(meta[1110:1278]);assert len(windows)==168 and set(windows)==set(range(6));assert bytes(windows).hex()==cur['current_table_bytes']['ThPoseWindows']['hex'];domains['Thomas body windows']=[434+x for x in windows];domains['Thomas cold body']=[434]
 wf=read(next(p for p in old['source_bindings']if p.endswith('/wwf-roster-native-1101-v1/runtime.s')));mapper=wf.split('WfMapBodyPage:',1)[1].split('\nWfDrawBody:',1)[0];clauses['WWF all-byte mapper']=mapper
 assert all(t in mapper for t in['cmp #58','sbc #58','cmp #18','sbc #18','adc #<629','adc #<442','adc #<546'])
 def wfpage(a):return 546+a if a<58 else 442+a-58 if a<76 else 512+((117+a-76)&255)
 domains['WWF every input byte']=[wfpage(a)for a in range(256)]
 assert {p for p in domains['WWF every input byte']if p>>8==1}==set(range(442,460))
 # The current header-authenticated Karnov sources exclusively consume these
 # named assigned pages; new HUD1019..1023 is NOT available to Metal.
 domains['Karnov assigned actor/art/HUD']=list(range(399,412))+list(range(1019,1024))
 overlaps={name:sorted(set(pages)&TARGETS)for name,pages in domains.items()if set(pages)&TARGETS};assert not overlaps,overlaps
 typed=[]
 for c in old['typed_callers']:
  text=read(c['path']);lines=text.splitlines();line=c['line'];assert 'X5SetPhysicalChr'in lines[line-1],(c['path'],line)
  typed.append(dict(**c,source_clause='\n'.join(lines[max(0,line-16):line+3]),current_500_501_502_exclusion='Upper2/3 excludes500..502 regardless low byte.'if 1 not in c['upper_domain']else'Actual current source/table domains above; WWF covers all256 inputs.'))
 assert len(typed)==43
 # Keep the existing classification's zero/indirect/stack alias closure as
 # an explicitly inherited proof. New ROM snippets are examined separately.
 assert old['passed']and old['compiled_writers']==845 and not old['unclassified']
 menu_paths=[ROOT/'build/menu-wwf-compact-1101-v1/character_select.s',ROOT/'build/doki-current-component-1101-v1/menu/full_roster_menu.s',ROOT/'build/bt-ready-menu-1031-v2/joint/src/cf_menu_body.inc',ROOT/'build/bt-ready-menu-1031-v2/joint/src/game.s',ROOT/'build/bt-ready-menu-1031-v2/joint/src/reset.s']
 menu={str(p.resolve()):dict(sha256=sha(p),bytes=p.stat().st_size)for p in menu_paths}
 queue=menu_paths[0].read_text();full=menu_paths[1].read_text();cf=menu_paths[2].read_text();game=menu_paths[3].read_text();reset=menu_paths[4].read_text()
 clauses['Native menu queue']=queue.split('.proc QueueSelection',1)[1].split('.endproc',1)[0]
 clauses['Native clear before restore']=full.split('.proc FmNativePrepare',1)[1].split('.endproc',1)[0]
 clauses['Earlier CF retirement']=cf.split('.proc FmCfRestoreP1',1)[1].split('.endproc',1)[0]
 clauses['Lag NMI decision']=reset.split('  lda NmiDisable',1)[1].split('ContinueNMI:',1)[0]
 clauses['Actual owner-specific lag guard']=game.split('.proc MaaLagChrGuard',1)[1].split('.endproc',1)[0]
 assert clauses['Native clear before restore'].index('X5ClearChrModes')<clauses['Native clear before restore'].index('sta CurrentCHRBank,x')
 assert not any(t.lower()in clauses['Earlier CF retirement'].lower()for t in['CurrentCHRBank','X5ChrMode','X5WideChrActive'])
 result=dict(passed=True,global_CHR_consumer_closure=False,native=False,installed=False,resource_granted=False,current_ROM_sha256=cur['current_ROM_sha256'],proposed_pages=sorted(TARGETS),exact_source_domains={name:dict(physical_pages=sorted(set(pages)),entries=len(pages))for name,pages in domains.items()},current_linked_tables=tables,typed_callers=typed,source_clauses=clauses,source_bindings=sources,menu_source_bindings=menu,inherited_compiled_writer_inventory=dict(ROM=old['current_ROM_sha256'],writers=845,unclassified=old['unclassified'],current_bytes_exact=831,current_changed_records=cur['changed_inherited_writers']),not_free_even_inside_CV3_gap=[511],candidate500_501_502_source_domains_disjoint=True,remaining_gates=['Actual publication/clear/native-Mario lag-NMI instruction seams','Current funding replacement instructions in12CHAR_SELECT records and new Karnov scoped owner must be bound before final global closure','Root resource grant; no blank-byte inference'],scope='Exact current native table bytes and finite source-owned domains tighten the old upper1<768 bound. Does not itself claim whole-image/global closure or allocate500..502.',bindings={str(p.resolve()):sha(p)for p in[Path(__file__),currentpath,oldpath,closurepath,V9/'source-stage.json',V8/'ownership.json',thmeta]+menu_paths})
 (OUT/'source-domains.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,typed_callers=len(typed),actual_tables=len(tables),domains=len(domains),source_objects_read=len(sources),all_proposed_disjoint=True,Thomas511_owned=True,global_closed=False)))
if __name__=='__main__':main()
