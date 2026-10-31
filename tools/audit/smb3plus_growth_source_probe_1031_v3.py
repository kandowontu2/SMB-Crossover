"""Put the donor's actual sprite origin in the same visible test viewport.

The float seed has a scrolled vertical high byte; setting Player_YHi0 while
leaving that high byte1 made the original renderer correctly hide the player.
Do not normalize any output pixels or banks. Retain both earlier probes.
"""
from pathlib import Path

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/smb3plus_growth_source_probe_1031_v1.py'
    text=prior.read_text().replace("O=R/'build/smb3plus-growth-source-probe-1031-v1'",
        "O=R/'build/smb3plus-growth-source-probe-1031-v3'")
    old='0x87:0,0x543:0';assert text.count(old)==1
    text=text.replace(old,'0x87:0,0x542:0,0x58e:0,0x543:0')
    old="host_grow=q.get('M3Growth'),exact=actual==expected)"
    text=text.replace(old,"host_grow=q.get('M3Growth'),exact=actual==expected,source_OAM=oam.hex(),host_parts=parts,source_pixels=len(expected),host_pixels=len(actual),mismatch=list(sorted(set(expected.items())^set(actual.items())))[:12])")
    namespace={'__file__':str(Path(__file__).resolve()),'__name__':'private_visible_growth_probe'}
    exec(compile(text,str(prior),'exec'),namespace);namespace['main']()


if __name__=='__main__':main()
