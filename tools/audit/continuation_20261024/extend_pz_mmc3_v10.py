from pathlib import Path
import importlib.util,re,json
D=Path(__file__).resolve().parent;base=D/'extend_pz_mmc3_v9.py';spec=importlib.util.spec_from_file_location('v9',base);v9=importlib.util.module_from_spec(spec);spec.loader.exec_module(v9)
def apply(source):
 v9.apply(source);records=[]
 for name in ('roll_art.inc','parodius_art.inc','parodius_death_art.inc'):
  p=source/'src'/name;t=p.read_text()
  def record(m):
   try:a=[int(v.strip().replace('$','0x'),0)for line in m[2].splitlines()for v in line.split('.byte',1)[1].split(',')]
   except (ValueError,IndexError):return m[0]
   if not a or a[0]%4 or len(a)!=a[0]+1:return m[0]
   old=a.copy()
   for i in range(1,len(a),4):
    tile=a[i]
    if tile&1:
     assert tile>=128,(name,m[1],tile)
     a[i]=(0xc0 if tile<192 else 0x80)|(tile&62);a[i+1]|=16
    else:a[i]=tile|1
   records.append(dict(file=name,label=m[1].split(':')[0],parts=a[0]//4,source_values=old,MMC3_values=a))
   return m[1]+'\n .byte '+','.join(map(str,a))+'\n'
  t=re.sub(r'(^[A-Za-z_][A-Za-z_0-9]*:\s*)(\.byte [^\n]+\n(?:[ \t]*\.byte [^\n]+\n)*)',record,t,flags=re.M);p.write_text(t)
 assert sum(r['parts']for r in records)==786+1487+52
 (source.parent/'literal-aux67-conversion.json').write_text(json.dumps(records,indent=2))
