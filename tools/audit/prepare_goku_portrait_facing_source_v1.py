"""Genuine one-immediate Goku cold-portrait facing correction.

Gameplay/source horizontal, attack and projectile routines remain untouched.
"""
from pathlib import Path
import difflib,json,shutil,subprocess,sys,hashlib
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address,location
import dragon_power_art_v1 as A
from PIL import Image
P=R/'build/functional-roster-smb2-v1/joint';OLD=R/'build/character-host-union-v13'
O=R/'build/goku-portrait-facing-source-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 assert not O.exists();O.mkdir()
 source=R/'build/dragon-power-flagpole-v3/admission.inc';original=source.read_text()
 old='Life:\n jsr DpEnsure\n lda #0\n sta DpRenderIndex'
 new='Life:\n jsr DpEnsure\n lda #1                 ; original standing record facing right\n sta DpRenderIndex'
 assert original.count(old)==1;changed=original.replace(old,new)
 (O/'admission.inc').write_text(changed,newline='\n')
 (O/'source.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),changed.splitlines(True),fromfile=source.as_posix(),tofile=(O/'admission.inc').as_posix())),newline='\n')
 entry=(OLD/'dp-component.s').read_text();anchor='"build/dragon-power-flagpole-v3/admission.inc"';assert entry.count(anchor)==1
 (O/'dp-component.s').write_text(entry.replace(anchor,'"'+(O/'admission.inc').as_posix()+'"'),newline='\n')
 commands=json.loads((OLD/'build-proof.json').read_text())['commands'];cc=next(c[:]for c in commands if c[-1]==str(OLD/'dp-component.s'))
 for flag in ['-o','--create-full-dep','--create-dep']:
  if flag in cc:cc[cc.index(flag)+1]=str(O/Path(cc[cc.index(flag)+1]).name)
 cc[-1]=str(O/'dp-component.s')
 cfg=(P/'private.cfg').read_text().replace(str(P),str(O)).replace(P.as_posix(),O.as_posix());(O/'private.cfg').write_text(cfg,newline='\n')
 link=json.loads((P.parent/'final-link.json').read_text())['command'][:]
 for i,x in enumerate(link):
  if x==str(OLD/'dp-component.o'):link[i]=str(O/'dp-component.o')
 for flag in ['-o','--dbgfile','-Ln','-m']:
  if flag in link:link[link.index(flag)+1]=str(O/Path(link[link.index(flag)+1]).name)
 for flag in ['-C','--config']:
  if flag in link:link[link.index(flag)+1]=str(O/'private.cfg')
 assert str(O/'dp-component.o')in link
 validations=[validate(c,O,cwd=R)for c in [cc,link]];(O/'output-preflight.json').write_text(json.dumps(validations,indent=2)+'\n')
 for name,c in [('compile',cc),('link',link)]:
  validate(c,O,cwd=R);z=subprocess.run(c,cwd=R,text=True,capture_output=True)
  (O/(name+'.json')).write_text(json.dumps(dict(command=c,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n');assert z.returncode==0,z.stderr
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,O/'candidate.nes')
 a,b=[load(p/'candidate.nes')for p in [P,O]]
 diffs=[i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y]
 assert len(diffs)==1 and (a['raw'][diffs[0]],b['raw'][diffs[0]])==(0,1),diffs
 pc=address(a,'DpAdmissionPortrait');at=location(a,'DpAdmissionPortrait');assert at<=diffs[0]<at+40
 # Every symbol value and all source moving/attack behavior remain exact.
 assert all(int(s['val'],0)==int(b['syms'][n]['val'],0)for n,s in a['syms'].items()if n in b['syms'])
 facts=[];ims=[];rgb=(R/'tools/NEXXT/nes.pal')
 if not rgb.is_file():rgb=next((R/'tools').rglob('nes.pal'))
 pal=rgb.read_bytes();roles=[[0x36,0x26,0x04],[0x30,0x36,0x0f]]
 for face,label in [(0,'left'),(64,'right')]:
  px,oam,cy=A.pixels(0,face);facts.append(dict(source_face_attribute=face,orientation=label,source_OAM=oam.hex(),source_CPU=cy,pixels=hashlib.sha256(json.dumps(sorted(px.items())).encode()).hexdigest(),opaque=len(px)))
  xs=[p[0]for p in px];ys=[p[1]for p in px];x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
  im=Image.new('RGBA',(x1-x0+1,y1-y0+1))
  for (x,y),(v,role)in px.items():n=roles[role][v-1];im.putpixel((x-x0,y-y0),tuple(pal[n*3:n*3+3])+(255,))
  im.save(O/('source-standing-'+label+'.png'));ims.append(im)
 sheet=Image.new('RGBA',(96,96),(40,48,64,255))
 for i,im in enumerate(ims):im=im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST);sheet.alpha_composite(im,(i*48+4,4))
 sheet.save(O/'source-standing-both.png')
 d=dict(passed=True,native=False,parent=sha(P/'candidate.nes'),candidate=sha(O/'candidate.nes'),only_ROM_change=dict(file_offset=diffs[0],physical_PRG=(diffs[0]-16)//8192,PC=pc+(diffs[0]-at),old=0,new=1),all_symbol_values_exact=True,gameplay_movement_body_and_attack_bytes_exact=True,portrait_record=1,original_source=sha(A.O.D.ROM),source_pixel_witness=facts,source_palette='Original executable-renderer roles: body36/26/04; head30/36/0F; no nativeRGB installation claim.',bindings={str(p.resolve()):sha(p)for p in [Path(__file__),source,OLD/'dp-component.s',O/'admission.inc',O/'dp-component.s',O/'source.patch',O/'candidate.nes',O/'candidate.dbg',P/'candidate.nes']})
 (O/'source-proof.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items()if k not in ['bindings','source_pixel_witness']}))
if __name__=='__main__':main()
