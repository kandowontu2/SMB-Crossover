"""Retain exact source OAM and pixel differences for the growth failure."""
from pathlib import Path

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/smb3plus_growth_source_probe_1031_v1.py'
    text=prior.read_text().replace("O=R/'build/smb3plus-growth-source-probe-1031-v1'",
        "O=R/'build/smb3plus-growth-source-probe-1031-v2'")
    old="host_grow=q.get('M3Growth'),exact=actual==expected)"
    assert text.count(old)==1
    text=text.replace(old,"host_grow=q.get('M3Growth'),exact=actual==expected,source_OAM=oam.hex(),host_parts=parts,source_pixels=len(expected),host_pixels=len(actual),mismatch=list(sorted(set(expected.items())^set(actual.items())))[:12])")
    namespace={'__file__':str(Path(__file__).resolve()),'__name__':'private_growth_diagnostics'}
    exec(compile(text,str(prior),'exec'),namespace);namespace['main']()


if __name__=='__main__':main()
