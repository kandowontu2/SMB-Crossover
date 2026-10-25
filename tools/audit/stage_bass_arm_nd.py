"""Create a bounded source overlay; preserve every unrelated physical CHR byte."""
from pathlib import Path
import re,shutil,json,hashlib
R=Path(__file__).resolve().parents[2];O=R/'build/verification/new-roster-1-1-nd/bass-final-overlay-v3';O.mkdir(exist_ok=False)
(O/'src').mkdir();(O/'chr/characters').mkdir(parents=True)
base=O.parent/'bass-arm-build-v3/overlay';special=O.parent/'bass-special-arm/overlay'
for folder,names in[(base,('src/bass_metasprites.inc','chr/characters/crossover-expanded.chr')),(special,('src/bass_special_poses.inc','src/bass_special_pose_ids.inc','chr/characters/special-bass-body.chr'))]:
 for n in names:shutil.copyfile(folder/n,O/n)
for n in('expanded.s','special_weapons.s'):shutil.copyfile(R/'src'/n,O/'src'/n)
entry=(R/'src/entrypoint.s').read_text()
for mapper in('mmc3','mmc5','mmc5-expanded'):
 name=f'chr/characters/packed-{mapper}.chr'
 entry=entry.replace('"'+name+'"','"'+(O/name).as_posix()+'"')
(O/'src/entrypoint.s').write_text(entry)
shutil.copyfile(R/'smb1base-mmc5-expanded.cfg',O/'smb1base-mmc5-expanded.cfg')
first=0xd1+len((R/'chr/characters/crossover-roster-high.chr').read_bytes())//1024
normal=(O/'chr/characters/crossover-expanded.chr').read_bytes();oldnormal=(R/'chr/characters/crossover-expanded.chr').read_bytes();body=(O/'chr/characters/special-bass-body.chr').read_bytes()
report={}
for mapper in('mmc3','mmc5'):
 text=(R/f'src/chr_map_{mapper}.inc').read_text().split('ChrPhysicalMap:\n')[1].split('.popseg')[0]
 mapping=[int(s.strip(),0)for line in text.splitlines()if'.byte'in line for s in line.split('.byte')[1].split(',')]
 assert len(mapping)==256
 replacements={b:normal[(b-first)*1024:(b-first+1)*1024]for b in range(224,231)}
 replacements.update({b:body[i*1024:(i+1)*1024]for i,b in enumerate(list(range(244,256))+[0x72,0x73])})
 path=R/f'chr/characters/packed-{mapper}.chr';before=path.read_bytes();after=bytearray(before)
 for b,data in replacements.items():
  assert len(data)==1024 and all(j in replacements for j,p in enumerate(mapping)if p==mapping[b]),('Shared physical bank',b)
  start=mapping[b]*1024
  if b in range(224,231):assert before[start:start+1024]==oldnormal[(b-first)*1024:(b-first+1)*1024]
  after[start:start+1024]=data
 (O/path.relative_to(R)).write_bytes(after)
 touched={mapping[b]for b in replacements}
 assert all(before[i:i+1024]==after[i:i+1024]for i in range(0,len(before),1024)if i//1024 not in touched)
 if mapper=='mmc5':
  expanded=(R/'chr/characters/packed-mmc5-expanded.chr').read_bytes();new=bytearray(expanded)
  for b,data in replacements.items():
   start=mapping[b]*1024;assert expanded[start:start+1024]==before[start:start+1024];new[start:start+1024]=data
  (O/'chr/characters/packed-mmc5-expanded.chr').write_bytes(new)
 report[mapper]=dict(physical_banks=sorted(touched),length_unchanged=len(before)==len(after),sha256=hashlib.sha256(after).hexdigest())
# Reapply the existing optional-outline metadata after source regeneration.
for filename,prefix in(('bass_metasprites.inc','XgBASS'),('bass_special_poses.inc','SsBass')):
 path=O/'src'/filename;text=path.read_text()
 def table(name):return[v.strip()for v in re.search(r'^'+name+r':\n\s+\.byte ([^\n]+)',text,re.M)[1].split(',')]
 banks=[int(v[1:],16)if v.startswith('$')else int(v)for v in table(prefix+'Banks')]
 aliases=dict(re.findall(r'^(\w+) = (\w+)$',text,re.M));contexts={}
 for side in('Left','Right'):
  for label,bank in zip(table(prefix+side+'Lo'),banks):
   label=label.lstrip('<>')
   while label in aliases:label=aliases[label]
   contexts.setdefault(label,set()).add(bank)
 packed=(O/'chr/characters/packed-mmc5.chr').read_bytes();lines=[];current=None
 for line in text.splitlines():
  m=re.fullmatch(r'(\w+):',line)
  if m:current=m[1]
  m=re.fullmatch(r'(\s*\.byte MetaspriteVramOffset\{\$([0-9a-f]+)\}, \{SPRITE_BANK_0\}, \$)([0-9a-f]+)(,.*)',line)
  if m and current in contexts:
   tile=int(m[2],16);attr=int(m[3],16)&~4;black=attr&3==3
   for bank in contexts[current]:
    data=packed[mapping[bank]*1024+tile*16:mapping[bank]*1024+tile*16+32]
    black&=any(data)and not any(data[8:16]+data[24:32])
   if black:attr|=4
   line=m[1]+f'{attr:02x}'+m[4]
  lines.append(line)
 path.write_text('\n'.join(lines)+'\n')
(O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
