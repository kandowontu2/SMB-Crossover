"""Current declared-source consumer inventory; never grant from empty bytes."""
from pathlib import Path
import hashlib,json,re,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
P=R/'build/karnov-host-resource-base-1101-v1';O=R/'build/karnov-combat-carrier-design-1101-v3'
ARCHIVE=R/'build/_recovery/legacy-sources-2026-10-31.zip'
PIN='e8d35a95ffe8e396dc1d8b32ca78d57d376fc14de9a2f4b37754012448fde09a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 assert sha(P/'candidate.nes')==PIN,'Use a terminal current base'
 b=scoped_load(P/'candidate.nes');text=(P/'candidate.dbg').read_text();files=[]
 for line in text.splitlines():
  if line.startswith('file\t'):
   q=dict(re.findall(r'(\w+)=("[^"\n]*"|[^,\n]+)',line));p=Path(q['name'].strip('"'))
   if p.suffix.lower()in['.s','.inc']:files.append((p,int(q['size'])))
 refs=[];missing=[];changed=[];writers=[];fetched={}
 # Read exact indexed objects in memory only. No historical tree is restored.
 with zipfile.ZipFile(ARCHIVE)as z:
  idx={q['path']:q for q in json.loads(z.read('index.json'))}
  def get(p):
   if p in fetched:return fetched[p]
   if p.is_file():data=p.read_bytes();origin='live'
   elif p.is_relative_to(R/'build')and p.relative_to(R/'build').as_posix()in idx:
    row=idx[p.relative_to(R/'build').as_posix()];data=z.read('objects/'+row['sha256']);assert hashlib.sha256(data).hexdigest()==row['sha256'];origin='indexed-recovery'
   else:return None
   fetched[p]=(data,origin);return fetched[p]
  for p,size in dict(files).items():
   got=get(p)
   if got is None:missing.append(p.as_posix());continue
   data,origin=got
   if len(data)!=size:changed.append(dict(path=p.as_posix(),compiled_bytes=size,current_bytes=len(data)));continue
   source=data.decode('utf-8',errors='replace');lines=source.splitlines();hits=[]
   for i,line in enumerate(lines):
    bare=line.split(';',1)[0].strip()
    if bare.startswith(('.import','.export',';')):continue
    if re.search(r'(?:\b(?:farcall|jsr|jmp|\w+Far)\b.*X5(?:SetPhysicalChr|SetSpecialChr))|(?:\bsta\s+(?:X5ChrMode|X5SpecialChrUpper|X5HudChrUpper|CurrentCHRBank|SsChrPhysical|InvHudPhysical))|(?:\bsta\s+\$51(?:30|2[0-9a-b]))',bare,re.I):
     # Retain a compact source clause and preceding five instructions only.
     hits.append(dict(line=i+1,clause='\n'.join(lines[max(0,i-5):i+2])))
   if hits:writers.append(dict(path=p.as_posix(),origin=origin,sha256=hashlib.sha256(data).hexdigest(),sites=hits))
   refs.append(dict(path=p.as_posix(),origin=origin,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
  def readbuild(name):
   got=get(R/'build'/name);assert got,name
   return got[0].decode()
  # These are genuine indexed-source Bowser/Battletoads tables, not a newer
  # canonical replacement. Their actual symbols still exist in this image.
  bw=readbuild('bowser-playable-jump-v1/joint/bowser/host.s')
  assert 'adc #<825\nBwGfxPage:'in bw and 'ldx #3'in bw
  bt=readbuild('bt-current-cf-component-v2/joint/bt/art.s')
  assert 'BtPosePages:.byte 0,0,0,0,1,1,1,2,2,2,3,3'in bt
  skin=readbuild('arthur-expanded-host-v1/joint/skin.s')
  assert 'cmp #$84'in skin and 'lda #2\n sta $5130'in skin
  archive_refs=[dict(path=p.as_posix(),sha256=hashlib.sha256(v[0]).hexdigest())for p,v in fetched.items()if v[1]=='indexed-recovery']
 def table(n,count):at=location(b,n);return b['raw'][at:at+count]
 closed=[]
 def record(owner,pages,evidence):
  pages=sorted(set(pages));assert not set(pages)&{1019,1020}
  closed.append(dict(owner=owner,pages=pages,evidence=evidence))
 # Actual emitted low/high arrays, every pool, body and weapon/pickup domain.
 for kind in['Body','Special','Pickup']:
  low=table('PnPool'+kind+'Lo',18);high=table('PnPool'+kind+'Hi',18)
  record('Parodius '+kind,[a+256*z for a,z in zip(low,high)],'All18 actual compiled pool entries; legal PnPool0..17. Source canonical table differs and is intentionally not used.')
 record('Parodius HUD',[396,397,398],'PnHudGate: variant1..3 plus395; high1.')
 record('Final Fantasy',range(756,788),'Actual FfRenderChunk masks descriptor pageAND31; FfPublishChunk carries756+relative through high2/3.')
 record('Gimmick',[816,818],'Actual publisher has two constant pages816 and818; upper3.')
 dk=table('DkPosePages',9);assert min(dk)==0 and max(dk)==3
 record('Donkey Kong',list(820+x for x in dk)+[823],'DK_FIRST_CHR820; all9 actual compiled DkPosePages0..3; fixedshot/menu3.')
 dp=table('DpPosePage',66);assert min(dp)==0 and max(dp)==6
 record('Dragon Power',list(788+x for x in dp)+[795],'DP_FIRST_CHR788; all66 actual compiled DpPosePage entries0..6, reserved effects≤7.')
 gb=table('XgPITBanks',252);assert min(gb)==213 and max(gb)==216
 record('GB Pit',[808+(x-213)for x in gb]+[812],'All252 actual compiled four-power pose banks213..216 remap to808..811; original alternate pose3 uses812.')
 maa=table('MaaPages',49);assert min(maa)==45 and max(maa)==47
 record('MAAA',[768+x for x in maa],'All49 actual compiled MaaPages45..47; mode83. The63-entry typed frame map indexes these49 records.')
 record('SMB2/Doki',range(796,808),'S2_FIRST_CHR796; nativecharacter0..3 andsize0/1; independent object pages804..807.')
 record('Bowser',[824,825,826],'Actual indexed-source BwDrawPage: SMB1fixed824, SMB3 actual9-entry page table0/1+825; cold824/825.')
 record('Battletoads',range(915,919),'Actual12-entry BtPosePages only0..3, fixed915 base and upper3.')
 record('Benj Toad/Peach',range(901,915),'BmSelect legal52pose indices→>>3 at most6; base901, Peach adds7.')
 # Separately linked private CF symbols are not present in the host debug.
 # Its exact current linked module has156 legal page entries and checked192
 # frame index; projectiles use a single fixed968 page.
 cfmeta=R/'build/contra-force-p1-kernel-v1/body-meta.s';cfrender=R/'build/contra-force-scroll-publisher-1031-v2/kernel/render.s'
 ct=cfmeta.read_text();values=list(map(int,re.search(r'^CfBodyPage: \.byte ([0-9,]+)$',ct,re.M)[1].split(',')));assert len(values)==156 and min(values)==0 and max(values)==8
 rt=cfrender.read_text();assert 'cpx #192'in rt and 'lda CfBodyFrameIndex,x'in rt and 'adc #$bf'in rt and 'lda #$c8'in rt
 record('Contra Force',list(959+x for x in values)+[968],'Exact private native render source:192 checkedframes→156page entries0..8; shots fixed968.')
 # Source-level field bounds above are useful positive evidence, but this is
 # not a complete transitive proof across every copied execution image and
 # persistent per-window shadow/override transition.
 uncertain=[dict(consumer='ArCachePublishFast and201 descriptor headers',source='build/arthur-physical-clock-v1/joint/arthur/cache-runtime.s:40',reason='Descriptor field1 is loaded via(R0),Y and published with mode83 by ArCachePublishFast lines173..185. Next: decode/check every201 cache descriptor header and fallback input path from actual current carrier; source table rootsC000/C094/C128. Nominal ARTHUR_CHR868..880 emission is insufficient.'),dict(consumer='X5WidePublication/X5Direct0..11',source='build/bt-ready-menu-1031-v2/joint/src/mmc5_expanded.s',reason='Generic physical publisher accepts all1024pages from retained CurrentCHRBank/X5ChrMode. Need transitive ownership proof for all copied kernels and scene/death/pause transitions; no silent safe-range assumption.'),dict(consumer='X5Write4 special override',source='build/bt-ready-menu-1031-v2/joint/src/mmc5_expanded.s',reason='SsChrActive selects independent SsChrPhysical+X5SpecialChrUpper. Parodius table closed above; every other live effect producer and override cancellation has not been fully catalogued.'),dict(consumer='X5Write8 HUD override',source='build/bt-ready-menu-1031-v2/joint/src/mmc5_expanded.s',reason='InvHudActive selects independent InvHudPhysical+X5HudChrUpper. Parodius known pages closed; all menu/pause/scene ownership transitions remain to close.'),dict(consumer='Private RAM atlas execution images',source='CHR carriers ARTHUR_CACHE_EXEC,QW_STREAM,FF_STREAM,BT_STREAM,BW_STREAM,CF_CARRIER',reason='Bowser/BT/CF/FF typed selector ranges examined, but complete reachable-code publication inventory for every copied image and inactive-window stale shadow is not independently proved here. Source file writer grep cannot replace that proof.')]
 # The current target and old snapshot retain exact all other CHR bytes;
 # only Karnov's existing399..411 allocation is excluded from this comparison.
 old=(R/'build/doki-current-component-1101-v1/candidate.nes').read_bytes();lo=1048592
 assert b['raw'][lo:lo+399*1024]==old[lo:lo+399*1024]and b['raw'][lo+412*1024:]==old[lo+412*1024:]
 result=dict(passed=True,audit_only=True,current_ROM_sha256=PIN,carrier_granted=False,complete_other_owner_closure=False,proposed_pages=[1019,1020],closed_selector_groups=closed,uncertain_consumers=uncertain,declared_source_files=len(files),examined_unique_sources=len(refs),unavailable_declared_sources=missing,changed_since_compiled=changed,source_writer_inventory=writers,indexed_source_refs=archive_refs,all_other_CHR_exact_to_frozen85=True,limits=['This is a conservative incomplete catalogue, not a carrier allocation.','The owner-specific ranges are proofs of those legal typed producers only. Generic publisher field values and every cross-scene override writer need a full transitive catalogue.','No source tree or ROM was restored/copied; indexed objects were read into memory.'],bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'candidate.nes',P/'candidate.dbg',cfmeta,cfrender,R/'build/doki-current-component-1101-v1/candidate.nes']},source_refs=refs)
 (O/'other-consumer-closure.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(passed=True,carrier_granted=False,groups=len(closed),writers=len(writers),missing=len(missing),changed=len(changed),sources=len(refs))))

if __name__=='__main__':main()
