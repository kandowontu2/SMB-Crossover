"""Emit exactly one root-approved b684 native test ROM after current CPU gates."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_strike_cold_1103_v131 as C
O=C.O;sha=C.M.M.sha


def main():
 grant_path=R/'docs/qa/allocations/prince-current-frontend-1103-v105.json';grant=json.loads(grant_path.read_text());assert grant['private_candidate_menu_admission_authorized']and not grant['nightly_installation_authorized'];C.M.M.validate(grant)
 proof_names=['current-shared-cold-CPU-v131.json','current-foreign-hot-CPU-v132.json','post-return-respawn-CPU-v133.json','actual-strike-CPU-v134.json','current-game-loop-ISR-CPU-v135.json','post-return-nested-IRQ-CPU-v136.json','frontend-proposal-v137.json','current-native-ingress-CPU-v138.json']
 proofs=[]
 for name in proof_names:
  p=O/name;q=json.loads(p.read_text());assert q['passed'],name;C.M.M.validate(q);proofs.append(p)
 base,manifest=C.image();q=json.loads((O/'frontend-proposal-v137.json').read_text());raw=bytearray(base['raw']);assert sha(raw)==grant['reviewed_component_memory_SHA256']==q['parent_memory_SHA256']
 for row,allowed in zip(q['patches'],grant['approved_exact_patches']):
  assert all(row[k]==allowed[k]for k in allowed);at=row['file_offset'];before=bytes.fromhex(row['old_hex']);after=bytes.fromhex(row['new_hex']);assert raw[at:at+len(before)]==before;raw[at:at+len(after)]=after
 assert sha(raw)==q['expected_memory_only_SHA256']==grant['expected_candidate_SHA256']
 rom=O/'prince-private-v140.nes';assert not rom.exists(),'One private candidate only; do not overwrite a tested input';rom.write_bytes(raw)
 # Minimal debug/labels retain exact native consumers and private entry names,
 # not a duplicate full source/debug tree. CPU tests keep their scoped bundle.
 native_names=['CrossoverMenuState','CrossoverMenuIndex','CrossoverMenuButtons','OperMode','OperMode_Task','SelectedCharacter','FmGroups','FmAlts','VRAM_Buffer1_Offset','VRAM_Buffer1','GameEngineSubroutine','Player_PageLoc','Player_X_Position','Player_Y_Position','Player_Y_HighPos','Player_State','NumberofLives','CurrentBank','CurrentBankC','FrameCounter','NmiDisable','NmiSkipped','SavedJoypad1Bits','SavedJoypadBits','ScreenLeft_PageLoc','ScreenLeft_X_Pos','Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_Y_Position','Enemy_PageLoc','Enemy_Y_HighPos','Enemy_BoundBoxCtrl','GameLoop','GameCoreRoutine','EnemiesAndLoopsCore','PlayerGfxHandler','KillPlayer','ShellOrBlockDefeat','IrqScrollSplit','NrWeapons','HuWeapons','NrDeathStart','HuDeathStart','NrPickupCollision','NrPickup','HuPickup','PowerUpObjHandler','PlayerEnemyCollision','MenuResolveCharacter','QueueSelection','FmQueueName','FmNames','FmPending','FmStartRetireFlags']
 entries={n:base['syms'][n]for n in native_names if n in base['syms']};assert len(entries)>50
 private=json.loads((O/'native-labels-v122.json').read_text());private={n:v for n,v in private.items()if n.startswith('PpNative')or n in ['PpHostDraw']}
 owner=C.C.M.A.L.P.T.labels(O/'post-owner-v130.lbl');private.update({n:owner[n]for n in ['CoCold','CoRetire','CoCheckCode','PrTypedWorker','PrCookie','CoBBCookie','CoExCookie']})
 labels={n:int(d['val'],0)for n,d in entries.items()};labels.update(private)
 rom.with_suffix('.lbl').write_text(''.join(f'al {v:06X} .{n}\n'for n,v in sorted(labels.items())),encoding='utf-8')
 segments={d['seg']:base['segs'][d['seg']]for d in entries.values()if 'seg'in d};lines=['version\tmajor=2,minor=0']
 lines.append(f'info\tcsym=0,file=0,lib=0,line=0,mod=0,scope=0,seg={len(segments)},span=0,sym={len(entries)+len(private)},type=0')
 for ident,d in segments.items():lines.append('seg\t'+','.join(f'{k}={v}'for k,v in d.items()if k in ['id','name','start','size','ooffs','type','addrsize']))
 for ident,(n,d)in enumerate(entries.items()):
  lines.append(f'sym\tid={ident},name="{n}",val={d["val"]},type=lab'+(f',seg={d["seg"]}'if'seg'in d else''))
 for ident,(n,v)in enumerate(private.items(),len(entries)):lines.append(f'sym\tid={ident},name="{n}",val=0x{v:X},type=lab')
 rom.with_suffix('.dbg').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 paths=[Path(__file__),grant_path,*proofs,O/'strike-manifest-v130.json',rom,rom.with_suffix('.lbl'),rom.with_suffix('.dbg')]
 receipt=dict(passed=True,private_native_candidate_only=True,ROM_written=True,installed=False,nightly_changed=False,native_emulator=False,ROM=rom.relative_to(R).as_posix(),ROM_SHA256=sha(raw),parent_ROM_SHA256=C.M.PIN,component_memory_SHA256=manifest['expected_memory_only_SHA256'],Prince_cookie=manifest['details']['Prince_cookie'],Bub_cookie=manifest['details']['Bub_cookie'],native_debug_symbols=len(labels),debug_scope='Minimal concrete native consumers and private entry labels; exact CPU bundle retained read-only by131.image.',source_backing_bytes=44476,physical_spare=580,required='Root single Mesen queue: real cold menu, initialEx37/SelectPrince38/name/portrait/no marker, lives/cold, idle/walk/left/unarmedjump, earned sword/strike, native contact/death/respawn/render. Full1-1/native audio/helpers unqualified. No Downloads/Git/installation by this helper.',bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in paths})
 (O/'candidate-v140.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='bindings'}))


if __name__=='__main__':main()
