"""Freeze the actual 58-ready source cohort; no native or installation."""
from pathlib import Path
import argparse,json,zipfile
import prepare_functional_roster_smb2_v1 as B
R=B.R;O=B.O;N=B.N

def verify(p):
 d=json.loads(Path(p).read_text())
 for name,h in d.get('bindings',{}).items():assert B.sha(name)==h,name
 assert d.get('passed',True),p
 return d

def main():
 a=argparse.ArgumentParser();a.add_argument('--cohort',type=Path,required=True);args=a.parse_args()
 assert not(O/'handoff.json').exists()
 for p in [O/'source-stage.json',O/'source-contract.json',O/'menu-controls-v2/result.json',O/'dispatch-controls-v6/result.json',O/'dispatch-isr-v1/result.json',args.cohort]:verify(p)
 for p in [B.P.parent/'handoff.json',B.S/'handoff.json',B.L/'handoff.json',R/'build/smb2-current-unlock-cold-v15/handoff.json']:B.verify(p)
 assert B.sha(N/'candidate.nes')=='68cbe3207ef4123c8351c760ed04c804eeaa8d9d5aa2a76b7395d60c6c541ab3'
 negatives=[dict(file=str(O/'dispatch-controls/result.json'),cause='Anonymous genuine FF JMP-table slot had no standalone label; fixed fixture recognizes exact same physical opcode bytes.'),dict(file=str(O/'dispatch-controls-v2/result.json'),cause='Already-classified relocated Roll farcall operands were compared again as static page1; v3 applies the same exact transport exception consistently.'),dict(file=str(O/'dispatch-controls-v3/result.json'),cause='Old Sunny direct callback correctly returned to caller sentinel; endpoint helper had not modeled a completed direct-return callback.'),dict(file=str(O/'dispatch-controls-v4/result.json'),cause='Runtime endpoint source patch did not persist through generated import chain.'),dict(file='tools/audit/functional_roster_smb2_dispatch_v5.py',cause='Preflight caught omitted replacement application; v6 applies the source replacement before execution.'),dict(file=str(O/'menu-controls/result.json'),cause='Fixture expected old Quick identity zero; actual already-ready Quick correctly retains bit20.')]
 (O/'retained-negatives.json').write_text(json.dumps(negatives,indent=2)+'\n',encoding='utf8')
 text='''# Genuine SMB2 current shared-source join

Candidate68cbe3207ef4123c8351c760ed04c804eeaa8d9d5aa2a76b7395d60c6c541ab3
is a source-linked successor of ready54 08f1. Actual linked80-profile menu
and10,240Start/A all-flag cases measure58ready/22pending: SMB2Mario,Luigi,
Toad,Peach become selectable. All54 previous profiles remain ready.

Actual current source joins corrected S2v15 own callback ancestry, v14LateUI,
v12 originalaudio/worldSFX and relocatedRoll producers. Service19 retains
genuine JnResetDispatch before S2MainScene. Actual forcedblank InitScreen
independently reaches S2InitScreenPrepareÃ¢â€ â€™QwSceneInitÃ¢â€ â€™Ar/Fw/nativeMove once.
Menu retirement goes S2MenuResolveÃ¢â€ â€™QwMenuResolveÃ¢â€ â€™ArGenResolve; post-Ic Fresh
retains genuine Ic/Sunny/QwBoot and reaches sole S2ColdInit via typedrow15.

The no-growth shared transport occupies five formerly owned5-byte islands
behind unchanged36public11-byte prologues. A79 remains2591/2592B. Existing
index clamp/multiply/restore/realFarCallCommon is reused. Only helpers retain
their97-byte capsules; the ORA16 replacement is limited to privateY0..15.
Full source ownership/prologue/actualdependency contracts are bound.

CPU checks include32,768foreign all-flag Movement/Fresh pairs,9,216all36
foreign ingress cases,2,304actual S2 table deliveries, and1,296realnormal/
lagNMI+IRQ cuts at the new transport/33SMC/mapper seams. Foreign callback
identity, ordered application writes, flags, livepage1, maps and caches are
preserved; relocatedRoll is matched by genuine linked symbols. Shared
endpoint CPU changesÃ¢Ë†â€™2..+14; no additional resident mapper entry occurs there.
Actual current54 wholeMain/caller regression passes496pairs. Main cost
changes+187..683CPU (Bill+284idle/walk,+415jump); foreignNMI adds133CPU.
These acceptedWIP costs are disclosed, not a performance-parity claim.
Active lifecycle/source/audio checks are in the bound cohort handoff.

The corrected natural cohort follows real titleStartÃ¢â€ â€™allnative area-parser/
screen/entrance tasks, actual normalNMI serialcontroller sampling, then source
movement/world/scroll/end exactlyonce. Earnedhealth,shrinking/protection,
lifting,throwing/native defeat and1Up controls are bound. DMCrate/fetch/length
and duration are CPU-model observations; they are not a native waveform,
bus-steal or PPUdeadline proof. Earlier shortened-parser and prebusy-counter
fixture failures remain bound in the peer negative history.

Root's410RCR/Chip source fixes and all Quick/Arthur/FF RAM code/data/cookies
remain exact. Actual final127 source produces119/120 and genuine125 clone.
No new lease, canonical/sharedsource edit, native launch or Downloads install.
Arthur/Quick severe lag remains an accepted WIP concern, with no constant60Hz
claim. This source stage awaits root native review; no full1-1/allupgrades
or complete admission claim is made for the new SMB2 characters.

This stage retains old menu marker/preview presentation: root is separately
fixing Quick/Arthur stars, previewgrid/facing and bluepanel attributes. Goku's
source-qualified portrait record0Ã¢â€ â€™1 is a separate leaf, not silently included
here. Moving Goku is unchanged/correct; the new Arthur/GokuSelect/Battletoads
roster request is later work and changes no80-identity truth in this packet.

Preparation/link commands and output-preflight.json describe actual outputs.
source-closure.json binds574actual inputs/56linkedobjects; original producer
handoffs retain derivation authority for unchanged copied source objects.
All frozen parents were reverified after compilation. No inherited Lua in
joint is a prepared or granted native run for this image.
'''
 (O/'HANDOFF.md').write_text(text,encoding='utf8',newline='\n')
 tools=[R/'tools/audit'/n for n in ['prepare_functional_roster_smb2_v1.py','functional_roster_smb2_menu_v1.py','functional_roster_smb2_menu_v2.py','functional_roster_smb2_dispatch_v1.py','functional_roster_smb2_dispatch_v2.py','functional_roster_smb2_dispatch_v3.py','functional_roster_smb2_dispatch_v4.py','functional_roster_smb2_dispatch_v5.py','functional_roster_smb2_dispatch_v6.py','functional_roster_smb2_dispatch_isr_v1.py','functional_roster_smb2_source_contract_v1.py','freeze_functional_roster_smb2_v1.py','private_build_outputs_v1.py']]
 dependencies=json.loads((O/'source-closure.json').read_text())['bindings']
 receipts=[B.P.parent/'handoff.json',B.S/'handoff.json',B.L/'handoff.json',R/'build/smb2-current-unlock-cold-v15/handoff.json',args.cohort.resolve()]
 cohort=json.loads(args.cohort.read_text());external=[Path(p)for p in cohort.get('bindings',{})if Path(p).is_relative_to(R)]
 files=set(p.resolve()for p in O.rglob('*')if p.is_file())|set(tools)|set(receipts)|set(Path(p)for p in dependencies)|set(external)
 archive=O/'source-only.zip'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(files):
   if p.suffix.lower()in ['.s','.inc','.cfg','.py','.json','.md','.patch','.diff','.dep','.d','.lua']and p!=archive:z.write(p,p.relative_to(R).as_posix())
 files.add(archive)
 d=dict(status='FROZEN_SOURCE_READY58_NATIVE_REVIEW_REQUIRED',candidate=B.sha(N/'candidate.nes'),parent=B.sha(B.P/'candidate.nes'),ready=58,pending=22,profiles=80,newly_ready=['SMB2Mario','SMB2Luigi','SMB2Toad','SMB2Peach'],previous54_preserved=True,source=True,native=False,installed=False,shared_capsule_publicPCs_and_owned_spans_preserved=True,Quick_Arthur_FF_RAM_images_exact=True,root_RCR_Chip_fixes_exact=True,source_cohort=str(args.cohort.resolve()),limits=['Actual CPU/source/controller/mapper/audio model, no native run on this cart.','New SMB2 full1-1/earned-all-items/campaign/native audio-PPU qualification remains open.','Root new UI/facing marker/preview leaf and Goku portrait correction not included; no new Battletoads identity claim.'],bindings={str(p.resolve()):B.sha(p)for p in sorted(files)})
 (O/'handoff.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
 print(json.dumps(dict(candidate=d['candidate'],handoff=B.sha(O/'handoff.json'),bindings=len(d['bindings']),source_archive_bytes=archive.stat().st_size,ready=58)))
if __name__=='__main__':main()
