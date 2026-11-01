"""Freeze the completed portions of the still-ungranted carrier audit."""
from pathlib import Path
import hashlib,json,zipfile

R=Path(__file__).resolve().parents[2]
O=R/'build/karnov-carrier-closure-1101-v4'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

def main():
 q=json.loads((O/'closure.json').read_text())
 assert q['passed'] and not q['carrier_granted']
 assert q['Arthur']['source_views']==201 and q['Arthur']['original_fast_and_clipped_emitter_cases']==603
 assert q['special_and_HUD_overrides']['closed'] and q['special_and_HUD_overrides']['upper2_domain']==[0,1,2]
 assert q['FF_body_pairing']['class_tier_pose_facing_cases']==432
 assert len(q['physical_publisher_calls']['callers'])==43 and not q['physical_publisher_calls']['closed']
 assert len(q['retained_shadow_writer_inventory']['sites'])==202 and len(q['sources'])==669
 for p,h in q['bindings'].items():assert sha(p)==h,p
 text='''# Karnov CHR carrier closure v4: allocation still denied

**Carrier granted: false. No ROM or nightly changed.** This packet advances
the frozen v3 design with genuine source CPU evidence. Ordinary retained-window
ownership and remaining high3 loader bounds remain explicit gates.

## Completed checks

- Arthur: actual original ArCacheEnsure/ArCacheLoad forced-blank CPU load,
  250342 cycles,7485 buffered PPU reads. All201 nonempty descriptors and21
  empty keys checked from actual RAM2 output. Headers use868..876; common
  windows877..880.603 original fast/clipped/crowded emitter cases retain the
  same page bounds. Canonical page0..8/15 validation and255 no-publish close
  fallback/header concerns. Warm cache check performs no new PPU reads.
- Independent special/HUD overrides: all4 Special-upper writers,8 generic
  Special setter callers and18 HUD-upper writers retain the inductive low2
  bit domain0..2. ANY retained low byte then remains below768, including
  active/pending/death/pause states. Actual X5PublishChr passed all768 upper
  and low combinations;512 genuine Special setter cases passed. Numeric
  literal aliases for the two upper fields are only their ABI declarations.
- Final Fantasy: actual original FwLoad reads16400 bytes through PPUDATA,
  then432 class/tier/pose/facing cases execute genuine FfSetPose/FfPublishChunk
  and the exact native PlayerBankReady alias-store prefix. All pairs stay
  within759..787, including26 low251/252 cases with correct upper2 bits.
  Source shot-draw restore/PublishOnly owners restore body0. The selected22
  lag guard suppresses ordinary CHR commits while a Main frame is busy.
- Source catalogue:669 exact non-Karnov declared units read in memory or by
  current hash.202 named shadow/Sm alias mutations and43 direct/macro generic
  physical-publisher callsites catalogued. Every declared legal upper argument
  has an owner; actual six CV3 upper tables contain1/2 only and all six Roll
  pool upper values are1. High3 typed ranges refer to the frozen v3 receipt.

## What still prevents allocation

The catalogue is not a complete compiled executable/indirect writer proof.
Complete the ordinary CurrentCHRBank/X5ChrMode window0..11 induction across
character/alternate admission, lives, scene resets and Zelda2 pause restoration.
Bind every private copied image and numeric/indirect alias to that ownership
model; a textual writer search alone cannot do this. Frozen debug retains
symbols/segments/source IDs but omits instruction spans.

Extend the declared FF body-pairing evidence to actual Main and every relevant
normal/lag NMI/IRQ publication seam, including all windows and later native
stores. The source guard and correct432 declared pairs are useful positive
evidence, not that complete Main proof.

Audit the exact forced-blank loader control-flow/index bounds next:

| Owner | Exact mapper | Required legal source range |
|---|---|---|
| Quick | current-character-quick-cold-v12/joint/quick/loader.s:QwMapPage | index0..8, pages884..892 |
| FF | contra-force-p1-coherent-cart-v2/joint/loader.s:FwMapPage | destinationC0/C4/..DC, pages893..900 |
| Bowser | bowser-current64-v3/joint/bowser/copy.s:BwMapPage | destinationC0/C4/..DC, pages927..934 |
| BT | bt-cf-coherent-source-1031-v1/joint/bt/loader.s:BtMapPage | destinationC0/C4/..DC, pages919..926 |
| CF | contra-force-projectile-contact-1031-v3/joint/cf-loader.s:CfMapSourcePage | index0..23, pages935..958 |

The full source paths are build-relative. Arthur881..883 and FF893..900 were
exercised by actual loaders here. Other row ranges above are required next
checks, not newly granted assumptions. Root must bind the eventual integrated
candidate to these frozen inputs and review21 deliberately unread mutable
Karnov-host source units. No active root output was read by this producer.

## Binding and scope

Actual CPU executable is frozen85 f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1.
Exact source catalogue is inherited from the frozen e8d35a95 menu/health v3
packet; its other CHR resources match frozen85 outside Karnov399..411.
This is source CPU evidence, not native gameplay, final-current Main stack or
nightly qualification. No donor ROM, dependency tree, executable ROM copy,
per-frame fixture/capture or emulator output is included.
'''
 (O/'HANDOFF.md').write_text(text,encoding='utf-8')
 source=[R/'tools/audit/audit_karnov_carrier_closure_1101_v4.py',Path(__file__).resolve()]
 files=source+[O/'closure.json',O/'HANDOFF.md']
 save(O/'handoff.json',dict(passed=True,frozen=True,carrier_granted=False,root_modified=False,installed=False,native=False,
  resolved=['Arthur201 cache headers/fallbacks','Special/HUD override upper-bit retention','Declared FF body/native-alias pairing'],
  remaining_gates=q['remaining_gates'],source_ROM_sha256=q['source_ROM_sha256'],frozen_inventory_ROM_sha256=q['frozen_inventory_ROM_sha256'],
  bindings={str(p.resolve()):sha(p)for p in files}))
 files.append(O/'handoff.json');z=O/'source-and-proof.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as out:
  for p in files:out.write(p,p.relative_to(R).as_posix())
 result=dict(passed=True,carrier_granted=False,path=z.as_posix(),sha256=sha(z),bytes=z.stat().st_size,members=len(files),
  source_files={p.relative_to(R).as_posix():sha(p)for p in source},root_modified=False,installed=False)
 save(O/'publication.json',result);print(json.dumps(result))

if __name__=='__main__':main()
