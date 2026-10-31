"""Locate the first animation divergence inside the complete donor update."""
from pathlib import Path

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/smb3plus_whole_controller_probe_1031_v1.py';text=prior.read_text()
    text=text.replace("O=R/'build/smb3plus-whole-controller-probe-1031-v1'",
        "O=R/'build/smb3plus-whole-controller-trace-1031-v1'")
    text=text.replace('itertools.product(range(4),[0,1],[0,1],[0,128])','[(3,1,1,128)]')
    text=text.replace('path=[]','path=[];events=[]')
    text=text.replace('            cpu.step()','''            if bank>=29 or cpu.pc==0xb0a0:
                events.append(dict(bank=bank,PC=cpu.pc,VY=bus.ram[0xcf],frame=bus.ram[0xee],
                    expired=bus.ram[0x7ae4],timer=bus.ram[0x7ae5],ready=bus.ram[0x7ae7]))
            before=bus.ram[0xee]
            cpu.step()
            if bus.ram[0xee]!=before:
                events.append(dict(frame_writer=True,bank=bank,PC=path[-1][1],
                    before=before,after=bus.ram[0xee],VY=bus.ram[0xcf]))''')
    text=text.replace("source_ready=bus.ram[0x7ae7],source_VY=bus.ram[source['Player_YVel']]))",
        "source_ready=bus.ram[0x7ae7],source_VY=bus.ram[source['Player_YVel']],source_events=events))")
    namespace={'__file__':str(Path(__file__).resolve()),'__name__':'private_controller_first_divergence'}
    exec(compile(text,str(prior),'exec'),namespace);namespace['main']()


if __name__=='__main__':main()
