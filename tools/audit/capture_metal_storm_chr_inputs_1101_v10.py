"""One scoped current-debug/ROM read for shared CHR500..502 consumer closure."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/metal-storm-chr-closure-1101-v10';CUR=ROOT/'build/kirby-owner-main-1101-v2'
PIN='c864e46a';sha=lambda b:hashlib.sha256(b).hexdigest()
NAMES='NonMaskableInterrupt MaaLagChrGuard BankSwitchCHR X5SetPhysicalChr X5ClearChrModes X5SetSpecialChr X5PublishChr X5ColdInit ChrPhysicalMap CHRBankInitValues GameLoop PauseSkip AudioUpdate FmNativePrepare QueueSelection FmCfRestoreP1 DrawSelectionPreview GameLoop FamilyMainCommit MarioVariant NmiDisable NmiSkipped CurrentBank CurrentBankC CurrentCHRBank X5ChrMode X5SpecialChrUpper X5HudChrUpper X5WideChrActive SsChrActive SsChrPhysical InvHudActive InvHudPhysical ReloadCHRBank DisableScreenFlag Mirror_PPUCTRL Mirror_PPUMASK SelectedCharacter'.split()
TABLES=dict(ProtoPoseChrLo=27,ProtoPoseChrHi=27,DwPoseBankLo=71,Z2PoseChrLo=27,Z2PoseChrHi=27,KbBodyChr=122,MkBodyChr=90,CdPoseChrLo=60,CdPoseChrHi=60,RlPoolChrLo=6,RlPoolChrHi=6,ThLoadCHR=16,ThPoseWindows=168)
TABLES.update({f'Cv3V{i}Chr{f}{s}':n for i,n in[(1,41),(2,43),(3,34)]for f in'RL'for s in['Lo','Upper']})
def main():
 OUT.mkdir(exist_ok=True);raw=(CUR/'candidate.nes').read_bytes();pin=sha(raw);assert pin.startswith(PIN),pin
 previous=OUT/'current-consumer-inputs.json'
 if previous.exists():
  q=json.loads(previous.read_text());assert q['current_ROM_sha256']==pin;segs=q['segments'];syms=q['syms'];debughash=q['current_debug_sha256'];debugbytes=q['debug_bytes'];reused=True
 else:
  debug=(CUR/'candidate.dbg').read_bytes();debughash=sha(debug);debugbytes=len(debug);reused=False;segs={};syms={};allnames=set(NAMES)|set(TABLES)
  for line in debug.decode().splitlines():
   if not line.startswith(('sym\t','seg\t')):continue
   z=dict(x.split('=',1)for x in line[4:].split(',')if'='in x)
   if line.startswith('seg\t'):segs[z['id']]=z
   elif 'val'in z and z['name'].strip('"')in allnames:
    name=z['name'].strip('"')
    if name not in syms or z.get('type')=='lab':syms[name]=z
 assert all(n in syms for n in NAMES),(set(NAMES)-set(syms))
 byname={s['name'].strip('"'):s for s in segs.values()}
 # ld65 ooffs is relative to each segment's declared output file. WRAM
 # images are real sideoutputs, never offsets in the complete cartridge.
 images={(CUR/'candidate.nes').resolve():raw};imagebind={}
 def image(g):
  p=Path(g.get('oname','"'+str(CUR/'candidate.nes')+'"').strip('"')).resolve()
  assert p.is_relative_to(CUR.resolve()),p
  if p not in images:images[p]=p.read_bytes()
  imagebind[str(p)]=dict(sha256=sha(images[p]),bytes=len(images[p]),retained_copy=False)
  return p,images[p]
 oldpath=ROOT/'build/karnov-carrier-final-1101-v6/finite-writer-domains.json';old=json.loads(oldpath.read_text());writers=[];mismatches=[];external=[]
 for w in old['writers']:
  s=byname.get(w['segment']);r=dict(segment=w['segment'],offset=w['offset'],PC=w['PC'],old_bytes=w['bytes'],source=w['source'],rule=w['rule'])
  if s is None or'ooffs'not in s:r['unresolved']='Segment is not a current nativeROM region';external.append(r);continue
  at=int(s['ooffs'],0)+w['offset'];pc=int(s['start'],0)+w['offset'];assert pc==w['PC'],(w['segment'],pc,w['PC'])
  path,data=image(s);now=data[at:at+len(bytes.fromhex(w['bytes']))];r.update(file=str(path),file_offset=at,current_bytes=now.hex(),unchanged=now.hex()==w['bytes'])
  (writers if r['unchanged']else mismatches).append(r)
 def loc(name):
  s=syms[name];g=segs[s['seg']];return int(g['ooffs'],0)+int(s['val'],0)-int(g['start'],0)
 spans=[]
 # These are executable snippets only, not entire PRG pages or debug graphs.
 for name,size in[('NonMaskableInterrupt',63),('MaaLagChrGuard',16),('BankSwitchCHR',160),('X5SetPhysicalChr',20),('X5ClearChrModes',28),('FmNativePrepare',40),('GameLoop',12)]:
  at=loc(name);path,data=image(segs[syms[name]['seg']]);assert path==(CUR/'candidate.nes').resolve();spans.append(dict(name=name,PC=int(syms[name]['val'],0),offset=at,size=size,hex=data[at:at+size].hex()))
 tables={};missing=[]
 for name,n in TABLES.items():
  if name not in syms or'seg'not in syms[name]or'ooffs'not in segs[syms[name]['seg']]:missing.append(name);continue
  at=loc(name);path,data=image(segs[syms[name]['seg']]);tables[name]=dict(PC=int(syms[name]['val'],0),file=str(path),file_offset=at,count=n,hex=data[at:at+n].hex())
 q=dict(passed=True,native=False,installed=False,resource_granted=False,global_CHR_consumer_closure=False,current_ROM_sha256=pin,installed_parent_ROM_sha256=sha(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()),current_debug_sha256=debughash,debug_bytes=debugbytes,reused_captured_debug=reused,debug_copy_retained=False,segments=segs,syms=syms,readonly_image_inputs=imagebind,unchanged_inherited_writers=writers,changed_inherited_writers=mismatches,unresolved_inherited_writers=external,native_spans=spans,current_table_bytes=tables,unresolved_table_symbols=missing,current_owner_link=json.loads((CUR/'owner-link.json').read_text()),scope='Single root-authorized current linked debug pass; corrected output namespaces are authenticated against their actual current nativeROM or small WRAM sideoutput. Full currentROM/debug and complete sideoutput images are read in memory only and not retained. Inherited writer mismatches remain explicit review inputs, not a grant.',bindings={str(p.resolve()):sha(p.read_bytes())for p in[Path(__file__),oldpath,CUR/'owner-link.json']})
 (OUT/'current-consumer-inputs.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,ROM=pin,segments=len(segs),unchanged_inherited=len(writers),changed_inherited=len(mismatches),unresolved_inherited=len(external),tables=len(tables),unresolved_tables=missing)))
if __name__=='__main__':main()
