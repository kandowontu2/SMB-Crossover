"""Compiled helper ABI, exact cell override, and individually bound stack cells."""
from pathlib import Path
import collections,hashlib,importlib.util,itertools,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'root49-sophia-block-shift-hn'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=O/'compiled-abi-hs.json';assert not out.exists()
 p=V/'agent49-samus-bill-arsenal-a/palette_native_model_cu.py';s=importlib.util.spec_from_file_location('sophia_hs_model',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 groups=[]
 for mapper in ['mmc3','mmc5']:
  before=m.q.Image(R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h'/f'smb-crossover-{mapper}.nes')
  after=m.q.Image(O/'source/build'/f'smb-crossover-{mapper}.nes');assert before.ram==after.ram;L=before.ram
  def ix(n,i=0):
   a=L[n]+i;return a if a<2048 else a-0x6000+2048
  oldpc=before.hook('InitBlock_XY_Pos')['address'];newpc=after.hook('SophiaHeadBlockOrigin')['address']
  histogram=collections.Counter();count=0;override=0;digest=hashlib.sha256()
  for character,attack,head,P,slot,page in itertools.product(range(14),[0,1],[0,128],[0,1,2,0xcf],[0,1],[0,1,2]):
   n=count;raw=bytearray(bytes((i*31+n)&255 for i in range(256))*40)
   values={'SelectedCharacter':character,'MmBlockAttack':attack,'SmCeilingHit':head,'RgTempX':(page*79+17)&255,'RgTempPage':page,
    'Player_X_Position':(page*113+249)&255,'Player_PageLoc':page,'Player_Y_HighPos':1,'SmHeadX':240,'SmHeadPage':page}
   for k,v in values.items():raw[ix(k)]=v
   raw[0x1ee]=0xff;raw[0x1ef]=3
   regs=[n&255,slot,(n*19)&255,P,0xed];banks={0x8000:62,0xa000:9,0xc000:13,0xe000:63}
   a=m.execute(before,raw,regs,banks,oldpc,0x400,0xef)
   b=m.execute(after,raw,regs,banks,newpc,0x400,0xef)
   for key in ['regs','banks','selector','ports']:assert a[key]==b[key],(mapper,n,key)
   expected=bytearray(a['ram'])
   # Two exact cells after the helper's PHP/PHA overwrite its inner JSR pair.
   expected[0x1ed]=a['regs'][3]|0x30;expected[0x1ec]=a['regs'][0]
   admitted=character==11 and attack==0 and head==128
   if admitted:
    override+=1
    expected[ix('Block_X_Position',slot)]=values['RgTempX']&0xf0
    expected[ix('Block_PageLoc',slot)]=page;expected[ix('Block_PageLoc2',slot)]=page
   assert b['ram']==expected,(mapper,n,'complete10240RAM')
   assert b['trace'][2:2+len(a['trace'])]==a['trace'],(mapper,n,'old ordered native writes')
   first=b['trace'][:2]
   assert [(z[3],z[4])for z in first]==[(0x1ed,(newpc+2)>>8),(0x1ec,(newpc+2)&255)]
   tail=b['trace'][2+len(a['trace']):]
   expected_tail=[(0x1ed,a['regs'][3]|0x30),(0x1ec,a['regs'][0])]
   if admitted:expected_tail.extend([(L['Block_X_Position']+slot,values['RgTempX']&0xf0),(L['Block_PageLoc']+slot,page),(L['Block_PageLoc2']+slot,page)])
   assert[(z[3],z[4])for z in tail]==expected_tail
   histogram[b['cycles']-a['cycles']]+=1;digest.update(b['ram']);count+=1
  groups.append(dict(mapper=mapper,cases=count,source_origin_overrides=override,cycle_delta=dict(histogram),digest=digest.hexdigest()))
  print(mapper,count,override,dict(histogram),flush=True)
 out.write_text(json.dumps(dict(status='PASS_EXACT_COMPILED_AXYP_RAM_WRITES_BANKS_WITH_ONLY_THREE_ADMITTED_ORIGIN_FIELDS_AND_TWO_BOUND_STACK_CELLS',script_sha256=sha(__file__),model_sha256=sha(p),groups=groups,limits=['Authored compiled entry controls; real native rendering/jumps/sound queues separately verified.','Only two specifically addressed popped PHP/PHA stack cells differ; their exact values are asserted. No whole-page mask.','This is a helper call ABI and ordered-write proof; no complete-game NMI/IRQ or waveform identity theorem.']),indent=2),encoding='utf-8')
 print('COMPILED',sha(out),flush=True)
if __name__=='__main__':main()
