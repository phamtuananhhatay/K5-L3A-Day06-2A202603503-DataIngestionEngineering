"""Validate and aggregate learner coherence labels for the preselected samples."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def main():
    sample_file=ROOT/'results/coherence/samples.json'
    samples=json.loads(sample_file.read_text(encoding='utf-8'))
    scores=json.loads((ROOT/'results/coherence/student_scores.json').read_text(encoding='utf-8'))
    source={s['sample_id']:s for s in samples['samples']}
    reviews=scores['reviews']
    if len(reviews)!=10 or [r['sample_id'] for r in reviews]!=list(source):
        raise ValueError('Scores must cover the same 10 preselected source positions')
    chunks={s:{c['chunk_id']:c for c in map(json.loads,(ROOT/f'results/chunking/chunks_{s}.jsonl').read_text(encoding='utf-8').splitlines())} for s in ('A','B')}
    rows=[]
    for review in reviews:
        sample=source[review['sample_id']]
        for strategy in ('A','B','C'):
            score=review['scores'][strategy]
            if type(score) is not int or score not in (0,1,2): raise ValueError('Invalid coherence score')
            physical='B' if strategy=='C' else strategy
            chunk=sample['chunks'][physical]
            if chunk != chunks[physical][chunk['chunk_id']]: raise ValueError('Coherence sample differs from stored chunk')
            if not chunk['metadata']['start_char']<=sample['source_position']<chunk['metadata']['end_char']:
                raise ValueError('Chunk does not cover chosen source position')
            rows.append({'sample_id':review['sample_id'],'strategy':strategy,'page':sample['page'],'source_position':sample['source_position'],
                         'chunk_id':chunk['chunk_id'],'score':score,
                         'reason':review['reason_A'] if strategy=='A' else review['reason_B_C'],
                         'reviewer':scores['reviewer'],'same_chunk_as_B':strategy=='C'})
    metrics=[]
    for strategy in ('A','B','C'):
        values=[r['score'] for r in rows if r['strategy']==strategy]
        counts=Counter(values)
        metrics.append({'strategy':strategy,'samples':len(values),'score_counts':{str(n):counts[n] for n in (0,1,2)},
                        'total_score':sum(values),'mean_out_of_2':sum(values)/len(values)})
    summary={'reviewer':scores['reviewer'],'recorded_at_date':scores['recorded_at_date'],'metrics':metrics,
             'sample_file_sha256':hashlib.sha256(sample_file.read_bytes()).hexdigest(),
             'status':'complete','sample_positions':10,'strategy_labels':30,'C_reuses_B':True,
             'selection_rule':samples['selection_rule'],'source_positions_validated':True,
             'independent_blind_assessment':False,'scope':'Learner coherence ratings for these 10 source positions only'}
    (ROOT/'results/coherence/summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'results/coherence/reviewed_samples.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
    lines=['# Coherence — kết quả chấm của học viên','',f"Người chấm: **{scores['reviewer']}**. Ngày ghi nhận: 13/11/2026.",'',
           'Điểm và lý do do học viên gửi trong chat. Codex chỉ ghi lại, đối chiếu mẫu và tính tổng; không thay điểm của học viên.','',
           '## Phương pháp và mẫu','',
           'Dùng cùng 10 vị trí nguồn đã chọn trước khi nhận điểm: 10 trang corpus đầu theo thứ tự tăng dần, anchor ở đoạn chính. Nếu có overlap, lấy chunk bao phủ anchor với start_char nhỏ nhất. Không đổi mẫu sau khi nhận điểm. C dùng cùng chunk B nên học viên cho cùng điểm.','',
           'Thang 0–2: 0 = khó hiểu do cắt ý/thiếu chủ thể; 1 = hiểu một phần, thiếu ngữ cảnh; 2 = tự hiểu được và giữ trọn ý. Mẫu nằm trong [coherence_samples_for_student.md](coherence_samples_for_student.md).','',
           '| Mẫu | PDF | A /2 | B /2 | C /2 | Lý do A của học viên | Lý do B/C của học viên |',
           '|---|---:|---:|---:|---:|---|---|']
    for r in reviews:
        lines.append(f"| {r['sample_id']} | {source[r['sample_id']]['page']} | {r['scores']['A']} | {r['scores']['B']} | {r['scores']['C']} | {r['reason_A']} | {r['reason_B_C']} |")
    lines += ['','## Tổng hợp','','| Strategy | Mẫu | Điểm 0 | Điểm 1 | Điểm 2 | Tổng điểm | Trung bình /2 |','|---|---:|---:|---:|---:|---:|---:|']
    for m in metrics:
        lines.append(f"| {m['strategy']} | {m['samples']} | {m['score_counts']['0']} | {m['score_counts']['1']} | {m['score_counts']['2']} | {m['total_score']} | {m['mean_out_of_2']:.1f} |")
    lines += ['','Trung bình = tổng điểm / 10. ID chunk đầy đủ, trang, offset và từng nhãn được lưu tại results/coherence/reviewed_samples.jsonl. Nhãn gốc của học viên ở results/coherence/student_scores.json.','',
              '## Nhận xét và giới hạn','',
              'Trên 10 mẫu này, học viên đánh giá B/C giữ ý tốt hơn A. A thường bị cắt giữa từ, thiếu đầu câu hoặc dính một phần heading tiếp theo. Điểm B/C giống nhau phản ánh dùng chung chunk, không phải hai bộ quan sát độc lập.','',
              'Điểm 2 của B/C là đánh giá của học viên trên mẫu đã chọn, không chứng minh toàn corpus không có lỗi. Riêng mẫu 05 vẫn giữ phần đuôi câu trang trước; học viên chấp nhận vì câu ví dụ chính đầy đủ. Một số chunk khác vẫn có header/footer. Chỉ lấy 10 trang đầu, chưa đại diện mọi section. Học viên là tác giả bài làm, đã thấy nội dung pipeline/dev và cách chia; không gọi đây là chấm mù độc lập.','',
              'Không dùng điểm coherence để chọn lại chiến lược sau test; cấu hình và lựa chọn C giữ nguyên.']
    (ROOT/'report/coherence_review_student.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
