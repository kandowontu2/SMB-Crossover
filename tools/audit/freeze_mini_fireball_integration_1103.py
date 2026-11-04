"""Freeze compact source-funded Mini fireball/performance composition evidence."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[2]
O=R/'build/mini-fireball-integrated-1103'
P=R/'build/mini-idle-constants-1103/mini-idle-fast.nes'
FINAL=R/'build/mini-final-candidate-1103/mini-optimized.nes'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 parent=P.read_bytes();own=(O/'mini-empty-draw.nes').read_bytes();final=FINAL.read_bytes()
 assert sha(P)=='4ff069b3474077a1f3f8924b530780dee7a81c2a32d759f8fbe2defcf91e3f4c'
 assert sha(FINAL)=='f552fd7ba20d4bdee4455c1f577ef966197dd792a2b885e8ecaf2a32dd40a481'
 pos=lambda bank,pc:16+bank*8192+(pc&8191)
 page=lambda p:1048592+p*1024
 def span(bank,pc,n):return parent[pos(bank,pc):pos(bank,pc)+n]
 # Source-identical native actor, collision workers, physics and explosion.
 assert own[16:8208]==final[16:8208]==parent[16:8208]
 assert own[page(968):page(969)]==final[page(968):page(969)]==parent[page(968):page(969)]
 hot=R/'tools/reference/thomas_hot_render_1031_v3.s'
 assert '.res 226-(*-::Name),$ff' in hot.read_text()
 assert span(66,0xb487,3)==bytes.fromhex('4c5a01')
 assert span(66,0xb48a,26)==b'\xff'*26
 assert 0xb3c2+226==0xb4a4
 cheats=R/'src/cheats.s';cs=cheats.read_text()
 assert all(x in cs for x in ['.res 94-18,$ea','.res 174-18,$ea','.res 54-18,$ea'])
 assert span(20,0xbd28,76)==b'\xea'*76
 assert span(20,0xbd86,156)==b'\xea'*156
 assert span(20,0xbe34,36)==b'\xea'*36
 turtle=R/'src/tmnt_mac_probes.inc';ts=turtle.read_text()
 assert '.res 160,$ea' in ts and '.res 178,$ea' in ts
 assert span(89,0xbcc0,160)==b'\xea'*160 and span(89,0xbd72,178)==b'\xea'*178
 nr=R/'build/karnov-host-resource-base-1101-v1/new_roster_dispatch.s'
 assert '.word $ffff\n::GmOnlyCommon:' in nr.read_text()
 assert span(79,0xb83b,5)==bytes.fromhex('4c7ebfffff')
 meta=parent[page(967):page(968)]
 assert meta[0x239:0x25e]==b'\xff'*37 and meta[0x2d0:0x300]==b'\xff'*48
 assert final[page(967)+0x25e:page(967)+0x2cf]==meta[0x25e:0x2cf]
 assert final[page(967)+0x2e0:page(967)+0x300]==(O/'MINI_FB_ART.bin').read_bytes()
 cfg=R/'build/bt-ready-menu-1031-v2/joint/private.cfg';cfgtext=cfg.read_text()
 assert 'LINK_GFX_MEM:start = $c000, size = $1c00' in cfgtext
 assert 'FF_ART_MEM:start=$d000,size=$1000' in cfgtext
 assert all(span(bank,pc,n)==b'\xff'*n for bank,pc,n in [(20,0xbbce,50),(20,0xbecc,52),(66,0xbecf,49),(93,0xbff8,8)])
 proofs=[O/'fire-proof/result.json',O/'final-native-proof/result.json',R/'build/mini-fireball-enemy-cpu-1103/result.json']
 for p in proofs:assert json.loads(p.read_text())['passed']
 funding=[
  dict(bank=66,range=['B48A','B4A4'],bytes=26,used=13,source=str(hot.relative_to(R)),authority='HotPlayerGraphics fixed226B B3C2..B4A4; genuine farcall/jmp endsB48A; source .res226 tail.'),
  dict(bank=89,range=['BCC0','BD60'],bytes=160,used=160,source=str(turtle.relative_to(R)),authority='TnMacHeadProbe BCAE public18B farcall/jmp then explicit160B padding; original178B span retained.'),
  dict(bank=89,range=['BD72','BE24'],bytes=178,used=119,source=str(turtle.relative_to(R)),authority='TnMacSideProbe BD60 public18B farcall/jmp then explicit178B padding; original196B span retained.'),
  dict(bank=79,range=['B83B','B840'],bytes=5,source=str(nr.relative_to(R)),authority='Existing3B JMP plus source unlabeled .wordFFFF immediately before GmOnlyCommon. CMP41 is moved into these5B; dispatch entryB840 unchanged.'),
  dict(bank=79,range=['B53A','B54C'],bytes=18,used=13,source='src/roll_weapons.s:86',authority='Existing explicit .res18,$EA after tail farcall.'),
  dict(carrier=967,range=['D239','D25E'],bytes=37,used=37,source='tools/audit/prepare_mini_owner_payload_1103_v19.py:metadata',authority='metadata initializer fillsFF; animation352B at0, frames217B at160 end239; coldcopier begins25E.'),
  dict(carrier=967,range=['D2D0','D300'],bytes=48,used=47,source='tools/audit/prepare_mini_owner_payload_1103_v19.py:metadata',authority='Source113B coldcopier25E..2CF; explicit metadata FF until native attrs300. Life15B at2D0; exact4x4 art32B at2E0.'),
  dict(bank=20,range=['BD28','BD74'],bytes=76,source='src/cheats.s:CheatsMenuInput',authority='94B original span;18B farcall/jmp then .res76EA.'),
  dict(bank=20,range=['BD86','BE22'],bytes=156,source='src/cheats.s:QueueCheats',authority='174B original span;18B farcall/jmp then .res156EA. Root DRAW_FAST109B plus BG_WRAPPER45B disjoint.'),
  dict(bank=20,range=['BE34','BE58'],bytes=36,source='src/cheats.s:CheatsPatchPage',authority='54B original span;18B farcall/jmp then .res36EA.'),
  dict(bank=20,range=['BBCE','BC00'],bytes=50,source='src/bill_flare_lifetime.inc:BILL_ORBIT_6 + retained full DBG + private.cfg',authority='Last BillFlare segment C-viewD3CE size800 endsDBCE; LINK_GFX_MEM endsDC00 with fillFF, nextCHEATS startsBC00.'),
  dict(bank=20,range=['BECC','BF00'],bytes=52,source='src/cheats.s + retained full DBG + private.cfg',authority='CHEATS_MENU_COLD BC00+2CC endsBECC; nextfixed ROGUE_RELOC_PAGE_9 beginsBF00; memory fillFF.'),
  dict(bank=66,range=['BECF','BF00'],bytes=49,source='src/proto_palette_ack.s + tools/audit/build_karnov_gameplay_host_1101_v1.py + retained full DBG/private.cfg',authority='PROTO_PALETTE_ACK BE40+8F endsBECF, including appended26B menu-cold init; nextROGUE_RELOC_PAGE_7 beginsBF00; memory fillFF.'),
  dict(bank=93,range=['AFF3','B000'],bytes=13,source='tools/audit/resume_current_quick_cold_v11b.py + retained full DBG/private.cfg',authority='HOST_BBOX_LOCAL AFA7 size59 endsB000; live79B endsAFF6, so tail3B JMP plus source memory10B fill reused. Original bbox call retained.'),
  dict(bank=93,range=['BFF8','C000'],bytes=8,source='tools/reference/ff_fx_world_marker_v1.s + retained full DBG/private.cfg',authority='FfMuxWorldDrawEnd C-viewDFF8; FF_ART_MEM endsE000 with fillFF. A-viewBFF8 tail8B is source padding.'),
 ]
 files=[Path(__file__),R/'tools/audit/build_mini_empty_draw.py',R/'tools/reference/mini_mario_empty_draw.s',R/'tools/reference/mini_mario_fireball_1103.s',R/'tools/audit/check_mini_fireball_integrated_1103.py',hot,cheats,turtle,nr,cfg,R/'src/roll_weapons.s',R/'src/proto_palette_ack.s',R/'tools/reference/ff_fx_world_marker_v1.s',R/'tools/audit/prepare_mini_owner_payload_1103_v19.py',R/'build/roster-combined-1101-v3/candidate.dbg',*proofs]
 receipt=dict(passed=True,source_funding_only=True,parent_ROM_SHA256=sha(P),fire_composed_ROM_SHA256=sha(O/'mini-empty-draw.nes'),root_final_ROM_SHA256=sha(FINAL),funding=funding,source_files_frozen=True,native_actor_bank0_and_Mini_atlas968_exact=True,new_resources='No new ROM/RAM/CHR pages. Existing source padding and original Mini metadata only.',tests=[str(p.relative_to(R))for p in proofs],bindings={str(p.relative_to(R)):sha(p)for p in files},scope='Root owns additional direct-dispatch/performance funding and all Mesen/install proofs. All addresses are half-open; old full DBG is used only where current preimages and live boundaries are independently verified.')
 (O/'source-funding.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(passed=True,funding_spans=len(funding),root_final=receipt['root_final_ROM_SHA256'],bytes=(O/'source-funding.json').stat().st_size)))

if __name__=='__main__':main()
