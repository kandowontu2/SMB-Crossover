"""Compact immutable source/native-power seam checkpoint; no ROM or capture forest."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json
import prepare_mini_mario_native_power_1103_v56 as P
O,R=P.O,P.R
def main():
 q=json.loads((O/'mini-host-v56.json').read_text());i=json.loads((O/'native-power-v57-ISR.json').read_text())
 assert q['passed']and i['passed']and q['SHA256']==i['kernel_SHA256']==P.W.sha((O/'mini-host-v56.bin').read_bytes())
 source_names=['prepare_mini_mario_power_contract_1103_v51.py','prepare_mini_mario_earned_mushroom_1103_v52.py','prepare_mini_mario_earned_mushroom_1103_v54.py','prepare_mini_mario_power_diagnostic_1103_v55.py','prepare_mini_mario_native_power_1103_v56.py','check_mini_mario_native_power_interrupts_1103_v57.py','prepare_mini_mario_earned_power_1103_v58.py',Path(__file__).name]
 sources=[R/'tools/audit'/n for n in source_names]
 files=sources+[O/f'mini-host-v56.{x}'for x in ['s','cfg','bin','lbl','json']]+[O/n for n in ['power-contract-v51.json','power-inputs-v51.zip','observer-hook-name-v54.json','power-diagnostic-v55.json','native-power-v57-ISR.json','earned-power-v58.json','earned-mushroom/capture/result.json','earned-mushroom54/capture/result.json','earned-mushroom55/capture/result.json','earned-mushroom58/controller.lua','earned-mushroom58/run.py','earned-mushroom58/ready.json']]
 raw=P.P.ROM.read_bytes();assert P.W.sha(raw)==q['parent_ROM_SHA256']
 direct={f'direct-native-inputs/ca90-PRG{bank}.bin':raw[16+bank*8192:16+(bank+1)*8192]for bank in [3,10,59,65,124,126,127]}
 members={p.relative_to(R).as_posix():dict(bytes=p.stat().st_size,SHA256=P.W.sha(p.read_bytes()))for p in files}
 archive=O/'mini-native-power-v59.zip';assert not archive.exists()
 with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=9)as z:
  for p in files:z.writestr(p.relative_to(R).as_posix(),p.read_bytes())
  for name,data in direct.items():z.writestr(name,data);members[name]=dict(bytes=len(data),SHA256=P.W.sha(data))
 out=dict(passed=True,source_CPU_only=True,ROM_written=False,native_admitted=False,archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,archive_SHA256=P.W.sha(archive.read_bytes()),kernel=dict(path=(O/'mini-host-v56.bin').relative_to(R).as_posix(),bytes=q['bytes'],SHA256=q['SHA256'],spare=q['five_pages_spare']),expected_ROM_memory_SHA256=q['expected_memory_only_ROM_SHA256'],cookie=q['cookie'],exact_patch_manifest=(O/'mini-host-v56.json').relative_to(R).as_posix(),ISR=dict(receipt=(O/'native-power-v57-ISR.json').relative_to(R).as_posix(),counts=i['actual_ISR_counts'],minimum_SP=i['minimum_ISR_SP']),native_packet=(O/'earned-mushroom58/ready.json').relative_to(R).as_posix(),git_source_files=[p.relative_to(R).as_posix()for p in sources],unchanged_source_retention='Retain durable mini-end-v50/world21/art12/host43 checkpoints. Original motion/world/renderer/end48 unchanged; only vectors24/33 and38-byte native bridges added. No prior tree rehydration.',scope='Actual ca90 negative:12 genuine mature contacts never called whole collector. New source56 executes native erase/score/Sfx/constructor and60update pipeline. Exact new-leaf/FarCall IRQ/FF and deepest lag-handler nestedIRQ pass, minimumSP127. Read-only earned58 packet ready but hardware result pending. Generic native60update/+1 status target is explicitly a host adaptation; original30/35 timing, ChangeSize clip, directflower2 and fireprojectiles remain future work.',members=members)
 (O/'mini-native-power-v59.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k]for k in ['passed','archive_bytes','archive_SHA256','kernel','git_source_files']}))
if __name__=='__main__':main()
