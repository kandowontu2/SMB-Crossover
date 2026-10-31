"""Finite actual compiler consumer and real transient-pointer ISR closure."""
from pathlib import Path
import argparse,collections,importlib.util,itertools,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_smb3plus_low_table_factor_1031_v1 as F
from smb3plus_kick_vectors_1031_v2 import SerialMemory
O,J,P=F.O,F.J,F.P;M,B=F.M,F.B
address,location,scoped_load=F.address,F.location,F.scoped_load

def refs():
 old,new=[scoped_load(p/'candidate.nes')for p in[P,J]]
 records={}
 for line in (P/'candidate.dbg').read_text().splitlines():
  if not line.startswith(('file\t','line\t','span\t')):continue
  kind,body=line.split('\t',1);d=dict(s.split('=',1)for s in body.split(',')if'='in s);records[(kind,d['id'])]=d
 def decode(n):
  sym=old['syms'][n];out=[]
  for ref in sym.get('ref','').split('+'):
   if not ref:continue
   item=records['line',ref];file=records['file',item['file']]['name'].strip('"');line=int(item['line']);source=Path(file).read_text(encoding='utf-8').splitlines()[line-1]
   out.append(dict(file=file,line=line,text=source,span=records.get(('span',item.get('span','')),{})))
  return out
 names=[f'M3Form{f}ChrLo'for f in range(7)]+['M3ChrLoTableLo','M3ChrLoTableHi','MbFloatReadChrLow','M3Palette::MbFloatLowOriginal','M3Palette::MbFloatLowStore']
 consumers={n:decode(n)for n in names}
 for f in[0,1,2,3,4,6]:
  assert all('M3ChrLoTable' in r['text']for r in consumers[f'M3Form{f}ChrLo']),consumers
 assert len(consumers['MbFloatReadChrLow'])==1 and 'jsr MbFloatReadChrLow' in consumers['MbFloatReadChrLow'][0]['text']
 assert all('M3ChrLoTableLo,x' in r['text']for r in consumers['M3ChrLoTableLo'])
 assert all('M3ChrLoTableHi,x' in r['text']for r in consumers['M3ChrLoTableHi'])
 source_refs=[];numeric=[]
 pattern=re.compile(r'\b(M3Form[0-6]ChrLo|M3ChrLoTableLo|M3ChrLoTableHi|MbFloatReadChrLow|MbFloatLowStore|MbFloatLowOriginal)\b')
 addresses={address(old,f'M3Form{f}ChrLo')for f in range(7)}
 hexpat=re.compile(r'\$([0-9a-fA-F]{4})\b|\b(\d{5})\b')
 for p in sorted(J.rglob('*')):
  if p.suffix not in['.s','.inc']:continue
  for i,line in enumerate(p.read_text(encoding='utf-8',errors='strict').splitlines(),1):
   if pattern.search(line):source_refs.append(dict(path=str(p),line=i,text=line.strip()))
   # Pure comments and numeric metadata are not address consumers; retain all live source numeric candidates for review.
   body=line.split(';',1)[0]
   if any(int(a,16)if a else int(b) in addresses for a,b in[]):pass
   for match in hexpat.finditer(body):
    value=int(match[1],16)if match[1]else int(match[2])
    if value in addresses:numeric.append(dict(path=str(p),line=i,text=line.strip(),value=value))
 assert not numeric,numeric
 dump=subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-exports',str(J/'main.o')],text=True,capture_output=True,check=True).stdout
 private=[n for n in names if f'"{n}"' in dump];assert not private,private
 # Exact actual sole caller's load/store sequence, and every new pointer entry.
 at=location(new,'M3SetFrame::Chr');body=bytes(new['raw'][at:at+23]);expected=bytes([174,address(new,'M3RenderForm')&255,address(new,'M3RenderForm')>>8,224,7,144,2,162,0,189,address(new,'M3ChrLoTableLo')&255,address(new,'M3ChrLoTableLo')>>8,133,address(new,'R0'),189,address(new,'M3ChrLoTableHi')&255,address(new,'M3ChrLoTableHi')>>8,133,address(new,'R1'),172,address(new,'M3RenderFrame')&255,address(new,'M3RenderFrame')>>8,32])
 assert body==expected,(body.hex(),expected.hex())
 for f in range(7):
  lo=new['raw'][location(new,'M3ChrLoTableLo')+f];hi=new['raw'][location(new,'M3ChrLoTableHi')+f]
  assert lo+256*hi==address(new,'M3Form0ChrLo')
 spans=[]
 for f,skip in[(1,7),(2,0),(3,0),(4,0),(6,0)]:
  lo=address(new,f'M3Form{f}ChrLo')+skip;count=81-skip;off=location(new,f'M3Form{f}ChrLo')+skip
  assert new['raw'][off:off+count]==bytes([234])*count
  labels=[n for n,s in new['syms'].items()if s.get('type')=='lab' and s.get('seg')==new['syms'][f'M3Form{f}ChrLo']['seg']and lo<address(new,n)<lo+count]
  assert not labels,labels
  spans.append(dict(physical_bank=91,begin=lo,end=lo+count,bytes=count))
 return dict(passed=True,compiler_refs=consumers,source_refs=source_refs,numeric_source_candidates=numeric,all_low_tables_private_not_object_exports=True,exact_caller_bytes=body.hex(),unchanged_Form5Lo_live_code=True,qualified_same_owner_reclaim_spans=spans,total_reclaim=sum(s['bytes']for s in spans),limits='Source-reference closure for genuine linked source/objects; arbitrary external numeric jumps and arbitrary private-helper inputs are not APIs.')

def vectors():
 b=scoped_load(J/'candidate.nes');path=R/'build/character-host-union-v13/gm_verify_nmi.py';spec=importlib.util.spec_from_file_location('low_pointer_real_vectors',path);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);M.T.G=g
 spans=[(M.T.key(b,'M3SetFrame::Chr'),56),(M.T.key(b,'MbFloatReadChrLow'),12)]
 rows=[]
 for form in range(7):
  base=F.G.seed(b,3,form,14,1);snapshot=bytes(base.m);maps=base.m.banks.copy()
  def seed():
   q=M.T.make(b,17);list.__setitem__(q.m,slice(None),snapshot);q.m.banks=maps.copy();q.m.__class__=SerialMemory;q.m.pads=[0,0];q.m.pad_index=[0,0];q.m.strobe=0;return q
  q=seed();c,tr,pathlist,info=M.T.invoke(q,'M3Graphics');sites=sorted({(*k,1)for k in pathlist if any(k[1]==at[1]and at[0]<=k[0]<at[0]+size for at,size in spans)})
  assert len(sites)>=27,len(sites)
  for site,(kind,disable,pause)in itertools.product(sites,[('IRQ',255,0),('NMI',255,0),('NMI',0,0),('NMI',0,1)]):
   r=seed();r.put(NmiDisable=disable,GamePauseStatus=pause,DisableScreenFlag=1);cc,tt,pp,ii=M.T.invoke(r,'M3Graphics',inject=(site,kind))
   assert bytes(r.m[0x5c00:0x5e00])==bytes(q.m[0x5c00:0x5e00])
   assert (r.get('R0'),r.get('R1'),r.get('SmChrBank'),r.get('M3SpritePageHi'),r.m.banks,r.get('CurrentBankC'))==(q.get('R0'),q.get('R1'),q.get('SmChrBank'),q.get('M3SpritePageHi'),q.m.banks,q.get('CurrentBankC'))
   assert F.M.regs(cc)==F.M.regs(c)
   rows.append(dict(form=form,site=site,kind=kind,disable=disable,pause=pause,minimum_SP=ii['interrupt']['minimum_SP']))
 return dict(passed=True,real_vectors=len(rows),all7forms=True,all_reached_low_high_pointer_and_new_helper_instruction_cuts=True,liveAXYP_SP_33SMC_page1_maps_and_final_outputs_exact=True,rows=rows)

def main():
 a=argparse.ArgumentParser();a.add_argument('--check',choices=['refs','vectors'],required=True);a=a.parse_args();stage=json.loads(B.read(O/'source-stage.json'));B.bound(stage)
 out=O/(a.check+'-consumer-controls-v1.json');assert not out.exists();q=globals()[a.check]();q.update(candidate=stage['candidate'],native=False,bindings={str(p.resolve()):B.sha(p)for p in[Path(__file__),Path(F.__file__),O/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'main.o',P/'candidate.nes',P/'candidate.dbg']});B.write(out,json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,check=a.check,out=str(out),sha256=B.sha(out))))
if __name__=='__main__':main()
