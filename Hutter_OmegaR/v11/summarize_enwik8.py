#!/usr/bin/env python3
"""Summarize paired authentic enwik8 excerpt results, no extrapolation to enwik9."""
import hashlib,json, pathlib, sys
base=pathlib.Path(sys.argv[1])
rows=[]
for offset in (0,40,80):
  measures={}
  for mode in (0,2):
    file=base/f'report_{offset}MiB_mode{mode}.json'
    record=json.loads(file.read_text())
    if record['test_type']!='AUTHENTIC_ENWIK8_PREFIX' or not record['enwik8_whole_file_verified'] or not record['measurement']['lossless_roundtrip_verified']:
       raise SystemExit(f'Non-authentic/nonlossless result: {file}')
    measures[mode]=record['measurement']
  a,b=measures[0],measures[2]
  if a['input_sha256']!=b['input_sha256'] or a['input_bytes']!=b['input_bytes'] or a['input_offset_bytes']!=b['input_offset_bytes']:
     raise SystemExit(f'Non-comparable results: offset {offset}')
  rows.append(dict(offset_mib=offset,input_bytes=a['input_bytes'],sha256=a['input_sha256'],
    baseline_total_bytes=a['local_sum_comp_plus_archive'],candidate_total_bytes=b['local_sum_comp_plus_archive'],
    baseline_archive_bytes=a['archive_bytes'],candidate_archive_bytes=b['archive_bytes'],
    baseline_compiler_bytes=a['compressor_bytes'],candidate_compiler_bytes=b['compressor_bytes'],
    delta_total_bytes=b['local_sum_comp_plus_archive']-a['local_sum_comp_plus_archive'],
    baseline_rss_kib=a['compress']['max_rss_kib'],candidate_rss_kib=b['compress']['max_rss_kib'],
    baseline_time_s=a['compress']['time_wall_seconds'],candidate_time_s=b['compress']['time_wall_seconds']))
t=sum(x['delta_total_bytes'] for x in rows)
output=dict(official_data='enwik8 only',hutter_prize_score=None,enwik9_measured=False,comparison='OMR11_MODE2 minus OMR11_MODE0, individual archives on disjoint excerpts',
  combined_delta_bytes=t,decision='candidate_improves_enwik8_excerpts' if t<0 else ('no_change' if t==0 else 'candidate_worse_on_enwik8_excerpts'),individual=rows)
(base/'summary.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(output,indent=2),flush=True)
