"""Measure the actual native body gate from exact installed instruction spans."""
import json
from pathlib import Path
import prepare_bubble_bobble_common_cold_1102_v4 as P
from check_tmnt_render_oa import address,location
R=P.R;O=P.O


def main():
 b=P.scoped_load(P.ROM);assert P.sha(b['raw'])==P.PIN
 raw=b['raw'];at=16+74*8192+0x1f03
 expected=bytes.fromhex('0848ad0260c919f01468284cdcab')+bytes([0xea])*15+bytes.fromhex('68288d6a01a9158d6c01a9bb8d6d01a9f64c5a01')
 assert len(expected)==49 and raw[at:at+49]==expected
 tail=address(b,'S2Tail_S2MainBody');assert tail==0xabf5 and((location(b,'S2Tail_S2MainBody')-16)//8192)==63
 t=raw[location(b,'S2Tail_S2MainBody'):location(b,'S2Tail_S2MainBody')+15]
 assert t==bytes.fromhex('a9158d6c01a9bb8d6d01a9f64c5a01')
 # The actual fixed bridge names exactly this bank74 BF03 gate.
 start=location(b,'GuestBodyContactBridge');bridge=raw[start:start+18]
 assert bridge==bytes.fromhex('8d6a01a9038d6c01a9bf8d6d01a9ca205a01')
 assert raw[16+74*8192+0x1f00:16+74*8192+0x1f03]==bytes.fromhex('4c5a01')
 source='.setcpu "6502"\n'+''.join(f'{n}=${address(b,n):04x}\n'for n in['SelectedCharacter','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon'])
 source+='NativeBodyTail=$abdc\nSharedFarJump=$bf00\nBbBodyVeneer=$b0ad\n.include "bubble_bobble_contact_gate_1102_v1.inc"\n'
 lab=P.assemble('native-contact-gate',source,'MEMORY{P:start=$bf03,size=49,file=%O;}SEGMENTS{BB_CONTACT_GATE:load=P,type=ro;}')
 blob=(O/'native-contact-gate.bin').read_bytes();assert len(blob)==49
 # No current absolute source operand points into the old gate interior.
 # Literal/data coincidences are recorded, never silently treated as calls.
 bank=raw[16+74*8192:16+75*8192];refs={}
 for target in range(0xbf04,0xbf34):
  hits=[0xa000+i for i in range(8190)if bank[i]in[0x20,0x4c,0x6c]and int.from_bytes(bank[i+1:i+3],'little')==target]
  if hits:refs[hex(target)]=hits
 assert not refs,refs
 q=dict(passed=True,proposal_only=True,shared_source_written=False,ROM_written=False,granted=False,base_ROM_SHA256=P.PIN,physical_PRG=74,replaced_half_open=[0xbf03,0xbf34],replacement_used_half_open=[0xbf03,0xbf03+len(blob)],spare=49-len(blob),preimage=expected.hex(),source_tail=dict(name='S2Tail_S2MainBody',physical_PRG=63,CPU=tail,bytes=t.hex(),use='Source-backed setup sequence cloned, not cross-bank JMP'),unchanged_shared_far_jump=[74,0xbf00],actual_fixed_bridge_bytes=bridge.hex(),new_raw39_target=[193,0xb0ad],retained_foreign_target=[202,0xabdc],retained_raw25_target=[246,0xbb15],interior_absolute_jump_call_operands=refs,scope='Measured source-only proposal. Incoming A is already in the real outer farcall SafecallA_SMC; foreign path reloads it, owned setup preserves it. Both nonzero bank loads branch to unchanged adjacent JMP FarCallCommon. Exact foreign ABI/native source/IRQ tests still required; no new resident/RAM/physical page or live owner admission.')
 (O/'native-contact-gate-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in['passed','physical_PRG','spare','ROM_written','granted']}))


if __name__=='__main__':main()
