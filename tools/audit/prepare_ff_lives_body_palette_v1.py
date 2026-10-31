"""Own FF lives-only P0 producer; preserve frozen remap+S2 source."""
from pathlib import Path
import difflib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address,location
P=R/'build/arthur-goku-smb2-palette-v1';Q=R/'build/functional-roster-coherent62-v4'
O=R/'build/ff-lives-body-palette-v1';J=O/'joint'
def main():
 assert not O.exists();assert B.sha(P/'handoff.json')=='93cf798479a206ea7ee1e08d503c8357fbee211b85d468d1b471313ab5592482'
 packet=json.loads(B.read(P/'handoff.json'));B.bound(packet)
 shutil.copytree(P/'joint',J)
 def rt(s):return s.replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix())
 for p in J.rglob('*'):
  if p.is_file()and p.suffix in ['.s','.inc','.cfg']:B.write(p,rt(B.read(p)))
 patch=[]
 def change(rel,t):
  p=J/rel;old=B.read(p);B.write(p,t);patch.extend(difflib.unified_diff(old.splitlines(True),t.splitlines(True),fromfile='frozen3721/'+rel,tofile='lives-body-only/'+rel))
 t=B.read(J/'loader.s');anchor=' .byte "RETHGIF ","M ETIHW ","M KCALB ","  FEIHT "\n .res 52-(*-FwHudNames),$ea'
 assert t.count(anchor)==1
 replacement=''' .byte "RETHGIF ","M ETIHW ","M KCALB ","  FEIHT "
; Only class*8 +0..6 reads the32B table above. This19B helper occupies
; its explicit previously unused20B own padding, preserving every old PC.
FwLivesBodyColors:
 php
 pha
 txa
 pha
 tya
 pha
 jsr FwCheck                 ; all16 cookie bytes before any RAM3 ACK access
 lda #2                      ; cold force: no authenticated-state writes
 bcc :+
 lda #1                      ; valid force: queue body and commit ACK on success
:pha
 jmp FwPaletteMapC           ; genuine saved-context C mapper/queue/restore
 .res 52-(*-FwHudNames),$ea'''
 t=t.replace(anchor,replacement)
 assert t.count(' jsr FwForceColors')==1;t=t.replace(' jsr FwForceColors',' jsr FwLivesBodyColors')
 t='.import FwPaletteMapC\n'+t;change('loader.s',t)
 t=B.read(J/'ff-palette.s');change('ff-palette.s','.export FwPaletteMapC\n'+t)
 recipes=[]
 for name in ['loader','ff-palette']:
  c=json.loads(B.read(Q/(name+'-build.json')))['command'][:];c[1:1]=['-I',str(J),'-I',str(J/'src')]
  for flag in ['-o','--create-full-dep','--create-dep']:
   if flag in c:c[c.index(flag)+1]=str(J/Path(c[c.index(flag)+1]).name)
  c[-1]=str(J/(name+'.s'));recipes.append((name+'-build',c))
 link=json.loads(B.read(P/'final-link.json'))['command'][:]
 for n in ['loader','ff-palette']:
  old=str(Q/'joint'/(n+'.o'));assert link.count(old)==1;link[link.index(old)]=str(J/(n+'.o'))
 for flag in ['-o','-Ln','-m','--dbgfile','--mapfile','-C']:
  if flag in link:link[link.index(flag)+1]=str(J/Path(link[link.index(flag)+1]).name)
 k=link.index('--ld-args')+1;v=link[k].split(',')
 for i in range(1,len(v),2):v[i]=str(J/Path(v[i]).name)
 link[k]=','.join(v);recipes.append(('final-link',link))
 B.write(O/'output-preflight.json',json.dumps([dict(step=n,validation=validate(c,J,cwd=R))for n,c in recipes],indent=2)+'\n')
 for n,c in recipes:
  validate(c,J,cwd=R);z=subprocess.run(c,cwd=R,text=True,capture_output=True);B.write(O/(n+'.json'),json.dumps(dict(command=c,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n');assert z.returncode==0,(n,z.stderr)
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,J/'candidate.nes')
 a,b=[load(x/'joint/candidate.nes')for x in [P,O]];d=[i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y]
 pad=location(a,'FwHudNames')+32;call=location(a,'FwLivesColors')+10
 assert a['raw'][pad:pad+20]==bytes([234])*20
 assert address(a,'FwPaletteMapC')==address(b,'FwPaletteMapC')
 assert b['raw'][location(b,'FwPaletteMapC'):location(b,'FfHostPaletteAEnd')]==a['raw'][location(a,'FwPaletteMapC'):location(a,'FfHostPaletteAEnd')]
 assert all(pad<=i<pad+20 or call<=i<call+3 for i in d),(d,pad,call)
 assert all(int(v['val'],0)==int(b['syms'][n]['val'],0)for n,v in a['syms'].items()if n in b['syms']), 'old PCs moved'
 for n in ['ram3.bin','ff-cookie.bin','code.bin','data.bin']:assert B.sha(J/n)==B.sha(P/'joint'/n)
 B.write(O/'source.patch',''.join(patch));q=dict(source=True,native=False,candidate=B.sha(J/'candidate.nes'),parent=B.sha(P/'joint/candidate.nes'),changed_bytes=len(d),changed_file_offsets=d,old_PCs_exact=True,full_payloads_cookies_header_CHR_exact=True,no_new_lease=True,own_padding=dict(file_offset=pad,bytes=20,source='FwHudNames .res52; index=(variant&3)*8, seven reads =>0..30'),
  behavior='Actual lives retains native30Btext and queues only7B black-backdrop/sourceP0 command, with full16cookie guarded ACK and exact native C/map/AXYP restoration.',bindings={str(p.resolve()):B.sha(p)for p in[Path(__file__),P/'handoff.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',O/'source.patch',O/'output-preflight.json']})
 B.write(O/'source-stage.json',json.dumps(q,indent=2)+'\n');B.write(J/'source-stage.json',json.dumps(q,indent=2)+'\n');B.bound(packet)
 print(json.dumps({k:v for k,v in q.items()if k!='bindings'}),flush=True)
if __name__=='__main__':main()
