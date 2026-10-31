"""Independent content review of the separately frozen ef2f source child."""
from pathlib import Path

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/review_cf_final_source_packets_1031_v1.py';text=prior.read_text()
    a=text.index('PACKETS=');z=text.index('\n\n\n',a)
    text=text[:a]+"""PACKETS=[('cf-cold-warm-palette-source-v1','c2de3f9c76595e5a6e11ec41cf15a02c1b9d5b41091f9f99f612b88e9d315876',9283,8345,
        R/'docs/qa/checkpoints/2026-10-31/cf-cold-warm-palette-source-v1/source-only.zip')]"""+text[z:]
    text=text.replace("name=='cf-cold-warm-source-v3'","name=='cf-cold-warm-palette-source-v1'")
    text=text.replace('cf-final-source-root-review-v1','cf-palette-successor-root-review-v1')
    ns={'__file__':str(Path(__file__).resolve()),'__name__':'private_root_ef2f_review'}
    exec(compile(text,str(prior),'exec'),ns);ns['main']()


if __name__=='__main__':main()
