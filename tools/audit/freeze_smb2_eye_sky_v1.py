"""Freeze minimal S2 palette/eye source closure, retaining exact negatives."""
from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_ff_joint_source_v1 import validate
from finalize_ff_current_component_v3 import dependencies
O=R/'build/smb2-eye-sky-v3';J=O/'joint';P=R/'build/functional-roster-coherent62-v4'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):assert not p.exists();p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
 assert not(O/'handoff.json').exists();files=validate(P/'handoff.json','bb581aad7a4224cd35b83e056fe880cbd49c5cfcf04bfa637b00ea146bc01ab6')
 proofs=[O/'source-proof.json',R/'build/smb2-eye-sky-controls-v1/controls.json',R/'build/smb2-eye-role-audit-v2/audit.json',R/'build/smb2-eye-role-audit-v1/audit.json',R/'build/smb2-sky-negative-v1/consumer-proposal.json']
 for p in proofs:
  h=json.loads(p.read_text());assert h['passed'],p
  for name,digest in h.get('bindings',{}).items():assert sha(name)==digest,name;files.add(Path(name))
  files.add(p)
 for n in['component','asset']:
  files|=set(dependencies(J/(n+'.dep')));files|={J/(n+'.dep'),J/(n+'.o'),O/(n+'-build.json')}
 c=json.loads((O/'final-link.json').read_text())['command'];files|={Path(v)for v in c if v.endswith('.o')}
 files|={p for p in O.rglob('*')if p.is_file()};files|={Path(__file__),R/'tools/audit/prepare_smb2_eye_sky_v1.py',R/'tools/audit/prepare_smb2_eye_sky_v2.py',R/'tools/audit/prepare_smb2_eye_sky_v3.py',R/'tools/audit/smb2_eye_sky_controls_v1.py',R/'tools/audit/private_build_outputs_v1.py',R/'tools/prepare_cv3_dmc_mirror.py'}
 for d in['smb2-eye-sky-v1','smb2-eye-sky-v2']:
  for name in['component-build.json','asset-build.json','final-link.json']:
   p=R/'build'/d/name
   if p.is_file():files.add(p)
 files|={R/'build/smb2-sky-negative-v1/negative.json',R/'build/smb2-sky-negative-v1/consumer-proposal.json'}
 summary='''This private source successor of final62 408acae repairs two specific SMB2 presentation defects. It is not a native or publication receipt.

The real original SMB2 ApplyPalette -> UpdatePPUFromBufferNMI consumer proves that the only nontransparent eye-mask index used by all256 current body entries is index2, NES16 red (21 original world/selector cases). Eye56 moves that bitplane to native P2 index1, whose NES16 is preserved in all actual tested native area, Bowser, select and lives cases. Eye attributes1/65 become2/66. Body P0, four body quads, all positions/priority and total5 sprites remain exact; max3 body sprites per scanline. Blank58 and all original object art remain untouched. No white/black mask or palette approximation is introduced.

The retained sky negative shows that native bulk3F00=0F was never followed by selected S2's native background restore. The original S2 queue already wrote3F11 only; there was no offending S2 3F10 write to remove. The repaired helper clones the actual native BackgroundColorCtrl-or-AreaType selection and8 exact BackgroundColors bytes. It emits3F10 length4: native universal + original3 body shades. Full normalNMI restores the true canonical3F00, with ground/water22 and lives/underground/castle0F (other native controls exact). P1/P2/P3 stay unchanged.

Private ABI retirement: S2PalettePointerC, physical118 B89E..<B8CB, had zero imports across every actual parent final-link object. Recompiling the whole actual component with its definition/export removed and final linking proves no local/live unresolved consumer. Its45B now hold41B helper +4B pad. S2MainPalette retains74B and next public S2MainSpawn BD00. Original StarInvincibleTimer, published-ROM palette and successful-ACK guards are unchanged. A full queue defers with ACK invalid; no write/canary overrun. This does not claim a newly repaired star/area-transition palette policy.

Source qualification: 256 original-color/priority poses;96 actual scene/GetPlayerColors->normalNMI cases;85 queue offsets/canaries;8 genuine cold selected/lives/entrance cohorts,167Main each +64 controlledMain total;82 real IRQ/lagNMI cuts preserve AXYP/SP/live page1/all33SMC/raw mappings. All other ROM/CHR/header bytes and public PCs exact;205 changed bytes are confined to the reviewed own spans/eye data. No native launch performed.

The existing inherited S2MainPalette introductory comment still describes the old three-color-only queue/unfinished-eye state; this README and the actual linked implementation/controls supersede that old comment. No source was edited after compilation to change frozen provenance.

Rebase: copy ONLY own smb2_roster_palette_v2.s, smb2_roster_main_v2.s, smb2_roster_art.inc into the final owner's actual S2 include precedence, and compile actual component producer. Replace original SMB2_ROSTER_CHR asset producer with own asset.s/eye-red.chr (12KB physical796..<808; only6 eye-pattern pages change). No cfg memory/segment split is added: private.cfg differs only output filenames. Recompile/link genuine current producers, retain all current common/menu/remap/FF/Quick/Arthur fixes. Run the obligatory final125 CV3 DMC mirror producer exactly as current parent. Old build logs are historical, not safe replay instructions; validate all new outputs first.

Retained preparation negatives: v1 ca65 `.res` could not resolve the proc label as a constant until a local byte-count label was used; v2 linked but the broad debug-name checker collided with generic local Color/NativeBackgroundColors names. v3 gives its new locals unique names, all old exported/public addresses remain exact. Neither negative wrote a frozen/shared output.
'''
 readme=O/'README.txt';assert not readme.exists();readme.write_text(summary,encoding='utf-8',newline='\n');files.add(readme)
 controls=json.loads((R/'build/smb2-eye-sky-controls-v1/controls.json').read_text());h=dict(passed=True,native=False,installed=False,parent_handoff=str(P/'handoff.json'),parent_ROM=sha(P/'joint/candidate.nes'),candidate=str(J/'candidate.nes'),candidate_sha256=sha(J/'candidate.nes'),actual_own_producers=[str(J/'smb2'/n)for n in['smb2_roster_palette_v2.s','smb2_roster_main_v2.s','smb2_roster_art.inc']]+[str(J/'asset.s'),str(J/'eye-red.chr')],actual_producer_recipes=[str(O/n)for n in['component-build.json','asset-build.json','final-link.json']],no_CFG_split_growth=True,source_diff=str(O/'source.patch'),source_proof=str(O/'source-proof.json'),controls=str(R/'build/smb2-eye-sky-controls-v1/controls.json'),limits=['Source CPU only; no native OAM/PPU hardware timing or final publication claim.','Existing star/published-ROM/ACK guards unchanged; no broader palette policy claim.','Original vegetable P1 role is unchanged; no newly claimed all-object palette solution.'],bindings={str(p.resolve()):sha(p)for p in sorted(files)if p.is_file()})
 save(O/'handoff.json',h)
 for name,digest in h['bindings'].items():assert sha(name)==digest,name
 print(json.dumps(dict(handoff=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),candidate=h['candidate_sha256'],bindings=len(h['bindings']))),flush=True)
if __name__=='__main__':main()
