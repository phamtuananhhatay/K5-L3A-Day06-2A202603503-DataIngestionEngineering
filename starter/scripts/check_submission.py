"""Read-only submission consistency/secret checks; never rerun or relabel holdout."""
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def read(path): return json.loads((ROOT/path).read_text(encoding='utf-8'))


def main():
    required=['STUDENT.md','README.md','data/manifest.json','benchmark/questions.json',
              'artifacts/experiment_log.csv','artifacts/experiment_log_README.md',
              'report/individual/2A202603503_PhamTuanAnh.md','report/submission_checklist.md',
              'report/coherence_review_student.md','report/metadata_review_student.md','report/grounding_review_student.md']
    errors=[]
    for p in required:
        if not (ROOT/p).is_file() or not (ROOT/p).stat().st_size: errors.append('Missing/empty '+p)
    student=(ROOT/'STUDENT.md').read_text(encoding='utf-8')
    for value in ['Phạm Tuấn Anh','2A202603503','L3A']:
        if value not in student:errors.append('Student information mismatch')
    with (ROOT/'artifacts/experiment_log.csv').open(encoding='utf-8-sig',newline='') as stream:
        log=list(csv.DictReader(stream))
    dev={r['strategy']:r for r in read('results/dev/reviewed/summary.json')['metrics']}
    test={r['strategy']:r for r in read('results/test/student_review/summary.json')['metrics']}
    if [r['strategy'] for r in log]!=['A','B','C']:errors.append('Experiment log requires A/B/C')
    for row in log:
        for split,summary in [('dev',dev),('test',test)]:
            for suffix,key in [('hit1','hit_at_1'),('hit3','evidence_hit_at_3')]:
                r=summary[row['strategy']][key]
                try:valid=abs(float(row[f'{split}_{suffix}'])-r['numerator']/r['denominator'])<1e-12
                except (ValueError,TypeError):valid=False
                if not valid:errors.append(f"Experiment log mismatch: {row['strategy']}/{split}/{suffix}")
    for split,n in [('dev',45),('test',15)]:
        traces=[json.loads(line) for line in (ROOT/f'results/{split}/traces.jsonl').read_text(encoding='utf-8').splitlines()]
        if len(traces)!=n or any(t['split']!=split for t in traces):errors.append('Trace coverage mismatch '+split)
    coherence=read('results/coherence/summary.json')
    if coherence['strategy_labels']!=30:errors.append('Coherence review incomplete')
    if len(read('results/test/student_review/metadata_audit.json')['records'])!=45:errors.append('Metadata audit incomplete')
    if len(read('results/test/student_review/grounding_scores.json')['questions'])!=5:errors.append('Grounding review incomplete')
    for p in ['README.md','report/individual/2A202603503_PhamTuanAnh.md','report/submission_checklist.md','results/README.md']:
        text=(ROOT/p).read_text(encoding='utf-8')
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
            if target.startswith(('https://','http://','#','mailto:')):continue
            target=target.split('#')[0]
            if target and not ((ROOT/p).parent/target).exists():errors.append(f'Broken relative link: {p} -> {target}')
    candidate_files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
    secret_findings=[]
    patterns=[re.compile(r'\bsk-[A-Za-z0-9_-]{24,}'),re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}'),re.compile(r'\bhf_[A-Za-z0-9]{25,}'),re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
    for p in candidate_files:
        parts=Path(p).parts
        if (Path(p).name=='.env' or any(part in ('.venv','models') for part in parts)
                or (p.startswith('data/raw/') and p.endswith('.pdf'))):
            secret_findings.append({'path':p,'type':'excluded local/private/large artifact is a Git candidate'})
        path=ROOT/p
        if path.suffix.lower() in ('.npz','.png','.jpg','.pdf') or not path.is_file():continue
        text=path.read_text(encoding='utf-8',errors='replace')
        for line_num,line in enumerate(text.splitlines(),1):
            if any(pattern.search(line) for pattern in patterns):
                secret_findings.append({'path':p,'line':line_num,'type':'credential/private-key pattern; value suppressed'})
    if secret_findings:errors.append('Potential secrets/ignored artifacts need review')
    frozen=read('artifacts/frozen_pipeline.json')
    changed=[]
    for p,digest in frozen['file_sha256'].items():
        with (ROOT/p).open('rb') as stream: actual=hashlib.file_digest(stream,'sha256').hexdigest()
        if actual!=digest:changed.append(p)
    if changed:errors.append('Frozen files changed')
    result={'status':'pass' if not errors else 'fail','student':{'name':'Phạm Tuấn Anh','id':'2A202603503','class':'L3A'},
            'required_files_present':not any(e.startswith('Missing') for e in errors),'experiment_log_matches_metrics':not any('Experiment log' in e for e in errors),
            'dev_traces':45,'test_traces':15,'ranked_chunks':180,'coherence_labels':30,'metadata_records':45,'grounding_labels':15,
            'relative_links_checked':True,'secret_pattern_findings':secret_findings,'git_candidate_files_scanned':len(candidate_files),
            'secret_scan_limit':'Pattern scan of Git candidate text files, not a guarantee of absence of all sensitive content',
            'frozen_files_checked':len(frozen['file_sha256']),'frozen_files_changed':changed,
            'external_steps_pending':['Commit completed work','Push to origin','Verify grader access','Submit repository link on class channel'],
            'errors':errors}
    (ROOT/'results/submission_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)


if __name__=='__main__':main()
