from pathlib import Path
D=Path(__file__).resolve().parent;t=(D/'build_mmc3_static_call_v29.py').read_text();t=t.replace("O=D/'mmc3-static-call-v29'","O=D/'mmc3-static-call-v30'")
anchor="add('src/mmc3.s',old,new);recipe.write_text(json.dumps(m,indent=2));source=O/'source'"
replacement='''tiny,common=new.split('.segment "LOWCODE"\\n',1)
assert common.startswith('FarCallCommon:')
common=common.replace('FarCallCommon:','::FarCallCommon:',1)
add('src/mmc3.s',old,tiny)
# Reuse the unreachable48-byte status wrapper tail. Its49-byte dispatcher
# needs one additional byte; remove one unreachable side-query NOP so the
# following FIXED labels, DPCM start and tail helpers retain their old layout.
add('src/characters.s','  .res 48,$ea\\n  .assert *-CrossoverPatchStatusName=66,error,"Status wrapper original span"',common+'  .assert *-CrossoverPatchStatusName=67,error,"MMC3 resident bank dispatcher uses status tail"')
add('src/characters.s','  farcall TnFastSideGate,jmp\\n  .res 10,$ea','  farcall TnFastSideGate,jmp\\n  .res 9,$ea')
add('src/characters.s','  .assert *-CrossoverSourceSideProbe=28,error,"Original side leaf footprint"','  .assert *-CrossoverSourceSideProbe=27,error,"One unreachable byte funds resident dispatcher"')
recipe.write_text(json.dumps(m,indent=2));source=O/'source' '''
assert t.count(anchor)==1;t=t.replace(anchor,replacement);t=t.replace('resident immutable bank dispatcher','resident immutable bank dispatcher in the existing status tail');t=t.replace('resident LOWCODE bank','resident status-tail bank');(D/'build_mmc3_static_call_v30.py').write_text(t)
