"""Compact final owning-source closure; never changes the tested cartridge."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_kirby_owner_main_1101_v2 as K
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
O=K.O
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert sha(O/'candidate.nes')==K.PIN
    new=qualified(O/'candidate.nes');old=K.baseline_bundle(new)
    proofs={};validated=0
    for name in ['owner-link.json','Main-CPU.json','foreign-body-CPU.json','body-guards-CPU.json']:
        p=O/name;q=json.loads(p.read_text());assert q['passed'] and q['ROM_sha256']==K.PIN
        for ref,digest in q['bindings'].items():assert sha(ref)==digest,(name,ref);validated+=1
        proofs[name]=sha(p)
    b74=16+74*8192
    allowed=[('source weapons island including one exact pad',b74,b74+3005)]
    at=location(new,'KbWeaponsDispatch');body=new['raw'][at:at+int(new['syms']['KbWeaponsDispatch']['size'],0)]
    operand=body.index(bytes([0x4c,address(new,'KbWeapons')&255,address(new,'KbWeapons')>>8]))+at+1
    allowed.append(('relocated KbWeaponsDispatch JMP operand',operand,operand+2))
    at=location(new,'KbBodyDispatch');size=int(new['syms']['KbBodyDispatch']['size'],0)
    assert size==64 and address(new,'KbBodyDispatch')==0xabdc
    allowed.append(('entire funded A/P preserving KbBodyDispatch source guard',at,at+size))
    at=location(new,'S2BoundaryBody');before=old['raw'][at:at+49];after=new['raw'][at:at+49]
    assert before[:11]==after[:11] and before[29:]==after[29:]
    target=address(new,'KbBodyDispatch')
    assert after[11:29]==bytes([0x4c,target&255,target>>8])+bytes([0xea])*15
    allowed.append(('S2BoundaryBody foreign tail only; Own remains byte exact',at+11,at+29))
    allowed.extend(('actual Core imported operand relocation',off,off+1)for off in[590639,590644,591593])
    changed=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
    assert len(old['raw'])==len(new['raw']) and len(changed)==2937
    assert all(any(lo<=i<hi for _,lo,hi in allowed)for i in changed)
    points={}
    for name,want in [('KbBodyDispatch',0xabdc),('KbWeaponsDispatch',0xabbd),('S2HostAudioBegin',0xbcb7),('S2BoundaryBody',0xbf03),('S2BoundaryA74End',0xbf75)]:
        assert address(old,name)==address(new,name)==want,(name,address(new,name))
        points[name]=hex(want)
    qmain=json.loads((O/'Main-CPU.json').read_text());qforeign=json.loads((O/'foreign-body-CPU.json').read_text())
    assert qmain['interrupts']['minimum_ISR_SP']==138 and qmain['interrupts']['reserve_above_SMC']==15
    assert qforeign['actual_foreign_body_AXY_realflags_SP_SMC33_maps_R0_R7_full_state_pairs']==1152
    q=dict(passed=True,source_CPU=True,native_emulator=False,installed=False,ROM_sha256=K.PIN,
      base_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),changed_bytes=len(changed),
      exact_authorized_intervals=[dict(source_role=n,file_start=lo,file_end_exclusive=hi,CPU_start=hex(0xa000+lo-b74)if b74<=lo<b74+8192 else None)for n,lo,hi in allowed],
      header_CHR_and_every_other_ROM_byte_exact=True,public_endpoints=points,
      owner_link_wording_clarification='The older boolean B74_after_weapon_exact_except_body_tail_and_two_native_operands is a narrow historical name. Its actual range assertion allows and audits the FULL 64-byte KbBodyDispatch ABDC..AC1B rewrite, besides the weapons island, dispatch JMP operand, S2 foreign tail, and three Core operand bytes. This receipt records the precise closure without changing that original receipt.',
      public_imports={n:dict(old=hex(address(old,n)),new=hex(address(new,n)))for n in['KbWeapons','KbDropCopy','KbAbilityMove','KbBodyContact']},
      new_export='KbBodyDispatch (existing fixed-address label, now exported for the Doki-owned same-bank JMP)',
      owner_layout='KIRBY_ABILITIES 8188 bytes; source weapon cut ABBD, one EA pad; all segment extents preserved by owner-link proof.',
      real_parent_caller=qmain['actual_Main_caller'],IRQ_NMI_cases=qmain['interrupts']['cases'],minimum_ISR_SP=138,reserve_above_live_SMC=15,
      current_proof_hashes=proofs,validated_bindings=validated,
      limits='Disclosed flat scene and NPC placement; source CPU and parent separate three-case native evidence. Not a full-level or all-character/all-hazard playthrough. Firebar anchor in guard check does not establish a collision. Old-owner closure is byte equality outside authorized source intervals plus 1152 actual foreign body ABI pairs; not a broad gameplay claim.',
      bindings={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/audit/check_kirby_owner_main_1101_v2.py',O/'candidate.nes',O/'candidate.dbg',O/'rollback-witness.json']+[O/n for n in proofs]})
    (O/'source-closure.json').write_text(json.dumps(q,indent=2)+'\n')
    (O/'HANDOFF.md').write_text('''Kirby owning-source repair, final candidate c864e46a8f333ab7a936c8d8f330944041a3eff12bc6dd4d9ba96892144ff3c7.

Reproduce using tools/audit/prepare_kirby_owner_main_1101_v2.py under the bounded runner. The recipe rebuilds the real Main owner with private first-include kirby_weapons.s and kirby_dispatch.s overrides, and the original Doki component with private kb-body-boundary.s. All other linked objects remain read-only. The source changes are emitted through prepare_kirby_body_ingress_1101_v2.py; reapply the existing deterministic CV3 DMC mirror after link. No whole source tree is duplicated. Production integration must use this actual owner recipe, not merely edit an unused canonical src file.

The body routing defect was an existing Doki foreign shortcut that bypassed KbBodyDispatch. The 49-byte S2BoundaryBody keeps its first11 bytes and Own branch byte exact; only its foreign18 bytes become JMP KbBodyDispatch plus15 EA. The full64-byte guard ABDC..AC1B is also repaired to save/restore incoming A/P before either child, funded by two near branches. Later endpoints remain fixed. The older owner-link boolean has a narrow historical name; source-closure.json explicitly audits the full guard rewrite. Three Core bytes relocate actual imports; all other outside-owner bytes, CHR and header match99bf.

Inhale guards now apply on the first valid held-B/front-contact frame while capture retains its warmup. Ordinary/released-B/rear contacts still hurt; actual Select Meta remains ordinary when unarmed. Green/red shell copies use native enemy boxes at the displayed height and3px movement. Red reversal is32 rather than24 updates, preserving outward reach93px versus original92px; expiry90 and return3 are unchanged. No new RAM/CHR/mapper lease.

Final source CPU checks: real Select/Start/parser; firstB old injury versus fixed6HP;8 naturally earned green/red x facing x Goomba/Koopa defeats;160 IRQ/lag-NMI cuts; all33 SMC operands, live page1 and foreground exact. True Start JSR IdleLoop plus IdleLoop PHA/JSR enters Main at FA, independently observed on965 native updates. Minimum ISR SP138 leaves15 bytes over highest liveSMC123, above required12. A historical API wrapper used arbitrary E0 and an extra FarCallCommon for fixed Main; its conservative failure is retained, not used as acceptance. No stack limit was relaxed.

Foreign source CPU check covers1152 actual S2BoundaryBody/GuestBodyContact calls for36 other IDs, four enemy types, two slots/A/flags; returned AXYP/SP, all33 SMC, maps, R0..7 and native/source state are equal. Foreign contact costs25 additional CPU cycles. This is not a full roster gameplay claim.

Parent owns separate native qualification and delivery. Parent reports the exact final candidate passed the unchanged three-case fresh inhale/spit, earned green-right and earned red-left fixture:1383 frames,965 Main updates, no injury, real native defeats. Those native files are external bindings, not generated by this component. No full1-1 playthrough, all-hazard validation or new video is claimed. Main CPU explicitly stops after the real parent PLA before catch-up handling; legitimate lag-NMI audio and NmiSkipped changes are not confused with foreground corruption.

New source files to preserve: prepare_kirby_owner_main_1101_v2.py; prepare_kirby_body_ingress_1101_v2.py; check_kirby_owner_main_1101_v2.py; check_kirby_foreign_body_1101_v2.py; check_kirby_body_guards_1101_v2.py; check_kirby_owner_closure_1101_v2.py, all under tools/audit. Preserve generated .s/.cfg, compact receipts and rollback witness with parent source packet. Do not archive full DBG/object/ROM copies. Frozen v1 source/proof packet remains unchanged. No O/shared source or nightly was mutated by this subagent; no read lease remains.
''')
    print(json.dumps(dict(passed=True,changed_bytes=len(changed),validated_bindings=validated,minimum_ISR_SP=138,reserve=15,closure_sha256=sha(O/'source-closure.json'),handoff_sha256=sha(O/'HANDOFF.md'))))

if __name__=='__main__':main()
