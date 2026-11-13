"""Aggregate learner scores, verify metadata and prepare unscored coherence samples."""
import json
import re
import sys
from collections import Counter
from pathlib import Path

from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'starter'))
from src.ingestion import normalize_text


def read(path): return json.loads((ROOT/path).read_text(encoding='utf-8'))
def write(path,value):
    target=ROOT/path
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    grounding=read('results/test/student_review/grounding_scores.json')
    student=grounding['reviewer']
    records=grounding['questions']
    if [q['question_id'] for q in records]!=read('benchmark/manifest.json')['splits']['test']:
        raise ValueError('Incomplete learner grounding scores')
    summary=[]
    for strategy in ('A','B','C'):
        scores=[q['scores'][strategy] for q in records]
        if any(type(s) is not int or s not in (0,1,2) for s in scores): raise ValueError('Invalid grounding score')
        counts=Counter(scores)
        summary.append({'strategy':strategy,'score_counts':{str(i):counts[i] for i in (0,1,2)},'sum':sum(scores),'questions':len(scores),'mean_out_of_2':sum(scores)/len(scores)})
    write('results/test/student_review/grounding_summary.json',{'reviewer':student,'metrics':summary,'score_source':'learner chat submission','independent_blind_assessment':False})
    lines=['# Grounding test — kết quả chấm của học viên','',f'Người chấm: **{student}**. Ngày ghi nhận: 13/11/2026.','',
           'Điểm và lý do do học viên gửi qua chat; Codex chỉ ghi lại và tính tổng hợp. Một điểm cho cả bộ top-3. Học viên là tác giả bài làm, không phải người chấm độc lập/mù.','',
           '| Câu | A /2 | B /2 | C /2 | Lý do của học viên |','|---|---:|---:|---:|---|']
    for q in records: lines.append(f"| {q['question_id']} | {q['scores']['A']} | {q['scores']['B']} | {q['scores']['C']} | {q['reason']} |")
    lines += ['','## Tổng hợp','','| Strategy | Điểm 0 | Điểm 1 | Điểm 2 | Tổng điểm | Trung bình /2 |','|---|---:|---:|---:|---:|---:|']
    for m in summary: lines.append(f"| {m['strategy']} | {m['score_counts']['0']} | {m['score_counts']['1']} | {m['score_counts']['2']} | {m['sum']} | {m['mean_out_of_2']:.1f} |")
    lines += ['','Trung bình = tổng điểm / 5. Giữ nguyên các nhãn 1 của học viên cho bằng chứng một phần; không tự chuyển từ Hit@3 hoặc similarity sang điểm grounding.','',
              'Các điểm này đánh giá mức hỗ trợ của top-3, không phải độ chính xác câu trả lời LLM. Không chỉnh cấu hình hoặc chọn lại C theo test. Nguồn: [trace test](../results/test/traces.jsonl) và [báo cáo evidence của học viên](test_evidence_review_student.md).']
    (ROOT/'report/grounding_review_student.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

    manifest=read('data/manifest.json')
    pdf=PdfReader(ROOT/manifest['local_path'])
    pages={}
    traces=[json.loads(line) for line in (ROOT/'results/test/traces.jsonl').read_text(encoding='utf-8').splitlines()]
    metadata_rows=[]
    for t in traces:
        for hit in t['hits']:
            p=hit['page']
            if p not in pages: pages[p]=normalize_text(pdf.pages[p-1].extract_text() or '')
            sections=[item['section'] for item in manifest['content_page_ranges'] if item['start']<=p<=item['end']]
            checks={'document_id':hit['document_id']==manifest['source_id'],'source':hit['source']==manifest['source_path_or_url'],
                    'page_text_slice':hit['text']==pages[p][hit['metadata']['start_char']:hit['metadata']['end_char']],
                    'section':len(sections)==1 and hit['metadata']['section']==sections[0]}
            if not all(checks.values()): raise ValueError(f"Metadata mismatch {t['question_id']}/{t['strategy']}/{hit['rank']}")
            metadata_rows.append({'question_id':t['question_id'],'strategy':t['strategy'],'rank':hit['rank'],'chunk_id':hit['chunk_id'],'page':p,
                'section':hit['metadata']['section'],'learner_verdict':'đủ và đúng','reviewer':student,'checks_against_source':checks})
    write('results/test/student_review/metadata_audit.json',{'reviewer':student,'learner_reported_counts':{'A':'15/15','B':'15/15','C':'15/15'},
        'learner_reported_errors':[],'technical_check':'45/45 text slices and source/page/section agree with original PDF and manifest',
        'filter_note':'A/B intentionally have no applied filter; this is not a metadata error','records':metadata_rows})
    text=f'''# Audit metadata test — kết quả kiểm tra của học viên

Người kiểm tra: **{student}**. Ngày ghi nhận: 13/11/2026.

Học viên báo đã kiểm tra đủ 45 bản ghi, không phát hiện lỗi. Codex ghi nhận kết quả
và kiểm tra kỹ thuật bổ sung trên PDF gốc/manifest, không thay đổi nhận xét của học viên.

| Strategy | Metadata đủ và đúng | Lỗi được học viên báo |
|---|---|---|
| A | 15/15 (100%) | Không |
| B | 15/15 (100%) | Không |
| C | 15/15 (100%) | Không |

Kiểm tra document_id, source, page và metadata.section. Tất cả ID tài liệu là
esmap-annual-report-2021, source khớp source_path_or_url, section khớp khoảng trang
content_page_ranges. Codex cũng đối chiếu từng text với lát cắt trang PDF gốc theo
offset: 45/45 khớp. Bản ghi chi tiết: results/test/student_review/metadata_audit.json.

Học viên nêu quy đổi trang in Ả Rập = trang PDF vật lý - 8 (ví dụ PDF 38 → 30,
PDF 41 → 33, PDF 62 → 54). Quy đổi dùng để đối chiếu với PDF; không phải chunk nào
cũng chứa số trang in, vì chunking có thể tách phần thân văn bản khỏi header/footer.

## Filter và tính hữu dụng

Học viên lưu ý q20 A/B có applied_filter=null và trả chunk ngoài section yêu cầu.
Đây là **đúng thiết kế A/B không filter**, không phải lỗi triển khai. Metadata từng
chunk vẫn có thể đúng dù chunk không liên quan câu hỏi hoặc không tuân thủ phạm vi.
Theo trace, trên hai câu test có filter: A=1/2, B=1/2, C=2/2 lượt có top-3 tuân thủ.

Phân tích của Codex bổ sung từ kết quả học viên: source/page giúp truy về tài liệu
để xác minh, section giúp C giới hạn phạm vi. Hạn chế: metadata đúng/đủ không bảo đảm
chunk chứa đủ evidence; C ở q20 vẫn thiếu điều kiện sau khi đánh giá kỹ thuật hoàn tất.
Tỷ lệ 100% chỉ áp dụng 45 bản ghi đã kiểm tra, không suy rộng mọi dữ liệu.

Đã giữ nguyên baseline, cấu hình và lựa chọn C. Không chạy lại test.
'''
    (ROOT/'report/metadata_review_student.md').write_text(text,encoding='utf-8')

    corpus={r['page']:r for r in map(json.loads,(ROOT/'data/processed/esmap_pages.jsonl').read_text(encoding='utf-8').splitlines())}
    selected=sorted(corpus)[:10]
    anchors={23:'Although the world',24:'SDG 7 is one',25:'RISE is the first',27:'The world must',28:'In Kenya, for example',
             29:'In FY2021, the MARCOT program',30:'In Sudan, the Energy',31:'The outcomes achieved',32:'ESMAP has built',33:'In collaboration with the Gender team'}
    if selected!=list(anchors): raise ValueError('Coherence sample page rule no longer matches')
    chunks={s:[json.loads(line) for line in (ROOT/f'results/chunking/chunks_{s}.jsonl').read_text(encoding='utf-8').splitlines()] for s in ('A','B')}
    samples=[]
    lines=['# 10 mẫu coherence để học viên chấm','',
           'Chưa có điểm. Chọn 10 trang đầu corpus theo thứ tự tăng dần; mỗi trang lấy điểm bắt đầu đoạn văn chính được ghi bằng anchor bên dưới. Chọn trước khi nhận điểm coherence, không chọn theo kết quả chấm. Nội dung đã từng được dùng trong pipeline/dev nên không coi đây là chọn mù.','',
           'Nếu nhiều chunk bao phủ điểm nguồn, chọn chunk có start_char nhỏ nhất. Offset bắt đầu từ 0, cuối loại trừ. C dùng đúng chunk B; có thể dùng cùng điểm nếu bạn xác nhận.','',
           '**Thang điểm:** 0 = bị cắt/thiếu chủ thể làm khó hiểu; 1 = hiểu một phần nhưng thiếu ngữ cảnh; 2 = tự hiểu và giữ trọn ý. Chấm nội dung thực tế, không chấm theo việc trả lời câu hỏi benchmark.','']
    for i,p in enumerate(selected,1):
        page=corpus[p]
        pos=page['text'].index(anchors[p])
        sample={'sample_id':f'{i:02d}','page':p,'anchor':anchors[p],'source_position':pos,'chunks':{},'score_status':'awaiting learner'}
        lines += [f'## Mẫu {i:02d} — PDF {p} (trang in {p-8})','',f"Section: {page['metadata']['section']}",f"\nVị trí nguồn: ký tự {pos}, bắt đầu bằng **{anchors[p]}**.",'',
                  '<details>','<summary>Xem toàn bộ văn bản trang nguồn để đối chiếu</summary>','','```text',page['text'],'```','','</details>','']
        for s in ('A','B'):
            covering=[c for c in chunks[s] if c['page']==p and c['metadata']['start_char']<=pos<c['metadata']['end_char']]
            if not covering: raise ValueError('No chunk covers coherence anchor')
            chosen=min(covering,key=lambda c:c['metadata']['start_char'])
            if chosen['text']!=page['text'][chosen['metadata']['start_char']:chosen['metadata']['end_char']]:raise ValueError('Sample offsets mismatch')
            sample['chunks'][s]=chosen
            lines += [f"### {s} — {len(chosen['text'])} ký tự",'',f"Chunk ID: `{chosen['chunk_id']}`",'', '```text',chosen['text'],'```','']
        sample['C_uses']='same chunk as B'
        samples.append(sample)
        lines += ['**Bạn gửi vào chat:**',f'`Mẫu {i:02d}: A=..., B=..., C=...; lý do A: ...; lý do B/C: ...`','']
    write('results/coherence/samples.json',{'selection_rule':'first 10 selected physical pages, explicit main-prose anchor, covering chunk with smallest start_char',
        'scores_exist':False,'same_source_positions_for_all_strategies':True,'samples':samples})
    (ROOT/'report/coherence_samples_for_student.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'grounding':summary,'metadata':'45/45 source checks pass; student reports no errors','coherence':'10 unscored source positions prepared; awaiting learner'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
