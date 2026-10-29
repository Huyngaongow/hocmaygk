"""Build 18 concise presentation slides + 6 backup slides from verified experiment data.

Run from any directory: python presentation/create_presentation.py
Text, diagrams, tables and charts remain editable in PowerPoint.
"""
from pathlib import Path
import json
import sys

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_MARKER_STYLE
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.xmlchemy import OxmlElement
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from examples.toy_bagging import build_toy_example


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


R = read("outputs/results.json")
E = read("outputs/extensions/analysis.json")
C = read("outputs/extensions/controlled_comparison.json")
F = read("outputs/extensions/family_comparison.json")
G = read("report/group_info.json")
T = build_toy_example()
if (R.get("seed") != 42 or R.get("n_estimators") != 51
        or R.get("selected_depth") != 3 or R.get("train_size") != 426
        or R.get("test_size") != 143
        or R.get("repeated_evaluation", {}).get("seeds") != list(range(42, 52))
        or [(m["tp"], m["fn"], m["fp"], m["tn"]) for m in R["test_metrics"]]
        != [(48, 5, 3, 87), (49, 4, 3, 87), (49, 4, 3, 87)]
        or C.get("protocol", {}).get("n_train") != 426
        or C.get("protocol", {}).get("n_test_excluded") != 143
        or any(r["n_estimators"] != 51 for r in C["summary"])
        or [r["n_estimators"] for r in E["tree_count_survey"]["summary"]]
        != [1, 5, 11, 21, 51, 101]):
    raise SystemExit("Cần kết quả mặc định: chạy de_5_ensemble_learning.py, "
                     "experiments/report_extensions.py và experiments/controlled_comparison.py trước.")
if not 1 <= len(G["members"]) <= 3:
    raise SystemExit("Kiểm tra thông tin nhóm trong report/group_info.json.")
FAMILY = {row["model"]: row for row in F["summary"]}
if (F.get("protocol", {}).get("seeds") != list(range(42, 52))
        or len(FAMILY) != 10 or any(row["n_runs"] != 10 for row in F["summary"])):
    raise SystemExit("Cần chạy experiments/ensemble_families.py đủ 10 seed mặc định.")

P = Presentation()
P.slide_width, P.slide_height = Inches(13.333333), Inches(7.5)
P.core_properties.title = "Đề 5 — Ensemble Learning | Bagging, AdaBoost, Voting và Stacking"
P.core_properties.subject = "Tiểu luận giữa kỳ — Nhập môn học máy"
P.core_properties.author = "; ".join(m["name"] for m in G["members"])
P.core_properties.keywords = "Bagging, AdaBoost, Voting, Stacking, bootstrap, OOB"
NAVY, TEAL, BLUE = "142D46", "087F82", "416DC4"
CORAL, WHITE, BG = "C86449", "FFFFFF", "F4F7FA"
INK, GRAY, LINE, MINT = "192F43", "5B6B7B", "DCE4EB", "8BE0CF"
PALE, SOFT_RED = "E9F4F1", "FAEDE8"
FONT, MONO = "Noto Sans", "DejaVu Sans Mono"
NOTES, TITLES = [], []
MAIN_SLIDES, TOTAL_SLIDES, HANDOFF = 18, 24, 11


def rgb(s):
    return RGBColor.from_string(s)


def num(v, digits=2):
    return f"{v:.{digits}f}".replace(".", ",")


def pct(v):
    return num(100 * v) + "%"


def avg(row, key="balanced_accuracy"):
    return f"{num(100 * row[key + '_mean'])} ± {num(100 * row[key + '_std'])}"


def shape(s, x, y, w, h, fill=WHITE, stroke=None, kind=MSO_SHAPE.RECTANGLE):
    obj = s.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    obj.fill.solid(); obj.fill.fore_color.rgb = rgb(fill)
    if stroke:
        obj.line.color.rgb = rgb(stroke); obj.line.width = Pt(.8)
    else:
        obj.line.fill.background()
    # Remove theme effects rather than inheriting the template's drop shadows.
    obj._element.spPr.append(OxmlElement("a:effectLst"))
    style = obj._element.find(qn("p:style"))
    if style is not None:
        effect = style.find(qn("a:effectRef"))
        if effect is not None: effect.set("idx", "0")
    if kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        obj.adjustments[0] = .08
    return obj


def txt(s, x, y, w, h, value, size=22, color=INK, bold=False,
        align=PP_ALIGN.LEFT, font=FONT, leading=1.12):
    obj = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = obj.text_frame; tf.clear(); tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.TOP
    for i, text in enumerate(str(value).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = text; p.alignment = align
        p.font.name = font; p.font.size = Pt(size)
        p.font.bold = bold; p.font.color.rgb = rgb(color)
        p.space_before = Pt(0); p.space_after = Pt(0)
        p.line_spacing = leading
    return obj


def rule(s, x1, y1, x2, y2, color=LINE, width=1):
    ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    ln.line.color.rgb = rgb(color); ln.line.width = Pt(width)
    ln._element.spPr.append(OxmlElement("a:effectLst"))
    style = ln._element.find(qn("p:style"))
    if style is not None:
        effect = style.find(qn("a:effectRef"))
        if effect is not None: effect.set("idx", "0")
    return ln


def arrow(s, x, y, width=.34, color=TEAL):
    return shape(s, x, y, width, .2, color, kind=MSO_SHAPE.RIGHT_ARROW)


def panel(s, x, y, w, h, fill=BG, stroke=None):
    return shape(s, x, y, w, h, fill, stroke, MSO_SHAPE.ROUNDED_RECTANGLE)


def slide(title, section, source="", dark=False, backup=False):
    s = P.slides.add_slide(P.slide_layouts[6])
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(NAVY if dark else WHITE)
    TITLES.append(title)
    txt(s, .62, .29, 10.8, .25, section.upper(), 10.5, MINT if dark else TEAL, True)
    txt(s, .62, .87, 12.08, .95, title, 30, WHITE if dark else NAVY, True)
    rule(s, .62, 7.02, 12.7, 7.02, "35516A" if dark else LINE, .7)
    txt(s, .62, 7.14, 3.75, .17, "ĐỀ 5 / ENSEMBLE LEARNING", 8.2, MINT if dark else GRAY)
    txt(s, 4.2, 7.14, 7.72, .17, source, 8.2, "B5CAD8" if dark else GRAY, align=PP_ALIGN.RIGHT)
    txt(s, 12.14, 7.1, .56, .25, f"{len(P.slides):02d}", 11, MINT if dark else TEAL, True, PP_ALIGN.RIGHT)
    # Quiet chapter marker, including a distinct appendix indicator.
    for i in range(4):
        shape(s, 11.67 + .27 * i, .36, .18, .035,
              (MINT if dark else TEAL) if backup or i == min((len(P.slides) - 1) // 5, 3)
              else ("35516A" if dark else LINE))
    # Standard OOXML Fade: manual advance, no automatic slide timing or sound.
    transition = OxmlElement("p:transition")
    transition.set("spd", "fast")
    transition.set("advClick", "1")
    transition.append(OxmlElement("p:fade"))
    s._element.insert_element_before(transition, "p:timing", "p:extLst")
    return s


def note(s, value):
    owner = "Nguyễn Nghĩa Hiếu" if len(P.slides) <= HANDOFF else "Trần Quốc Bảo"
    if len(P.slides) > MAIN_SLIDES: owner = "Cả hai — dự phòng khi hỏi đáp"
    value = f"Người nói gợi ý: {owner}.\n\n" + value
    s.notes_slide.notes_text_frame.text = value
    NOTES.append((len(P.slides), TITLES[-1], value))


def takeaway(s, value, dark=False, y=6.31):
    panel(s, .62, y, 12.08, .48, "213E57" if dark else PALE)
    txt(s, .82, y + .105, 11.65, .29, value, 15.5, MINT if dark else TEAL, True)


def label(s, x, y, value, color=TEAL, w=4):
    txt(s, x, y, w, .28, value.upper(), 11, color, True)


def table(s, x, y, widths, rows, row_h=.7, size=19, highlight=(), pad_y=.16):
    for ri, values in enumerate(rows):
        xx = x
        for ci, (val, w) in enumerate(zip(values, widths)):
            color = NAVY if ri == 0 else (PALE if ri in highlight else (WHITE if ri % 2 else BG))
            shape(s, xx, y + ri * row_h, w, row_h, color)
            txt(s, xx + .17, y + ri * row_h + pad_y, w - .34, row_h - pad_y - .02, val,
                size if ri else size - 1, WHITE if ri == 0 else INK, ri == 0 or ri in highlight,
                PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER)
            xx += w
        if ri > 0: rule(s, x, y + (ri + 1) * row_h, x + sum(widths), y + (ri + 1) * row_h, LINE, .55)


def stat(s, x, y, value, title, detail="", color=TEAL, w=3.7):
    txt(s, x, y, w, .85, value, 45, color, True)
    txt(s, x, y + .95, w, .5, title, 19, INK, True)
    if detail: txt(s, x, y + 1.6, w, .8, detail, 16, GRAY)


def code(s, x, y, w, value, h=4.45):
    panel(s, x, y, w, h, NAVY)
    label(s, x + .28, y + .22, "PYTHON · TRÍCH LƯỢC", MINT)
    txt(s, x + .28, y + .79, w - .56, h - .93, value, 17.3, WHITE, font=MONO, leading=1.22)


def count_chart(s, summary):
    data = CategoryChartData()
    data.categories = [str(row["n_estimators"]) for row in summary]
    data.add_series("Balanced accuracy CV", [100 * row["balanced_accuracy_mean"] for row in summary])
    chart = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(.7), Inches(2.05), Inches(7.5), Inches(3.6), data).chart
    chart.has_legend = False
    chart.has_title = False
    chart.chart_style = 2
    chart.value_axis.minimum_scale = 90; chart.value_axis.maximum_scale = 98
    chart.value_axis.major_unit = 2
    chart.value_axis.tick_labels.font.name = FONT; chart.value_axis.tick_labels.font.size = Pt(13)
    chart.category_axis.tick_labels.font.name = FONT; chart.category_axis.tick_labels.font.size = Pt(14)
    chart.value_axis.has_major_gridlines = True
    chart.value_axis.major_gridlines.format.line.color.rgb = rgb(LINE)
    series = chart.series[0]
    series.format.line.color.rgb = rgb(TEAL); series.format.line.width = Pt(2.3)
    series.marker.size = 8
    series.marker.style = XL_MARKER_STYLE.CIRCLE
    series.marker.format.fill.solid(); series.marker.format.fill.fore_color.rgb = rgb(TEAL)
    series.marker.format.line.color.rgb = rgb(WHITE)
    series.has_data_labels = True
    labels = series.data_labels
    labels.position = XL_LABEL_POSITION.ABOVE; labels.number_format = '0.00'
    labels.show_value = True
    labels.font.name = FONT; labels.font.size = Pt(14); labels.font.color.rgb = rgb(TEAL)
    for point, row in zip(series.points, summary):
        p = point.data_label.text_frame.paragraphs[0]
        p.text = num(100 * row["balanced_accuracy_mean"])
        p.font.name = FONT; p.font.size = Pt(14); p.font.color.rgb = rgb(TEAL)
    return chart


# 01 — Institutional cover with a restrained, editable ensemble diagram.
s = slide("", "Tiểu luận giữa kỳ · Nhập môn học máy")
s.shapes.add_picture(str(ROOT / "presentation/assets/tdtu_logo.png"), Inches(.63), Inches(.86), width=Inches(1.3))
txt(s, 2.2, .98, 8.8, .65, "TRƯỜNG ĐẠI HỌC TÔN ĐỨC THẮNG\nKHOA CÔNG NGHỆ THÔNG TIN", 12, GRAY, True)
txt(s, .62, 2.0, 7.2, 1.7, "ENSEMBLE\nLEARNING", 48, NAVY, True, leading=1.0)
txt(s, .67, 4.02, 7.15, 1.2, "Trọng tâm: Bagging cây quyết định\nMở rộng: AdaBoost, Voting, Stacking", 23, TEAL)
identities = [f"{m['name']}  ·  {m['student_id']}" for m in G["members"]]
identities.append("Giảng viên: " + G["lecturer"])
txt(s, .67, 5.61, 7.5, .95, "\n".join(identities), 13.5, GRAY, leading=1.35)
panel(s, 8.32, 2.02, 4.38, 4.66, NAVY)
label(s, 8.65, 2.4, "BOOTSTRAP → VOTING", MINT)
for yy, lab in [(3.02, "Cây 1"), (3.96, "Cây 2"), (4.90, "Cây B")]:
    panel(s, 8.67, yy, 1.45, .64, "27465F")
    txt(s, 8.82, yy + .16, 1.15, .32, lab, 17, WHITE)
    rule(s, 10.14, yy + .32, 11.08, 4.28, "5CAAA7", 1.5)
shape(s, 10.82, 3.79, 1.32, 1.0, TEAL, kind=MSO_SHAPE.ROUNDED_RECTANGLE)
txt(s, 10.91, 4.05, 1.14, .45, "H(x)", 25, WHITE, True, PP_ALIGN.CENTER)
txt(s, 8.67, 6.0, 3.55, .35, "Nhiều cây · Một dự đoán", 15, MINT)
note(s, "Mở đầu bằng câu hỏi: kết hợp nhiều mô hình giúp dự đoán thế nào? Bài đi sâu Bagging qua tính tay, mã tự triển khai và thực nghiệm; bổ sung AdaBoost, Voting và Stacking bằng scikit-learn để làm rõ các cách kết hợp khác. Nhóm tự viết bootstrap, hard voting và OOB; cây cơ sở dùng thư viện. Sơ đồ trên bìa minh họa cơ chế, không phải những cây đã học cụ thể. Bộ slide có 18 trang chính và 6 trang dự phòng. Luyện tập khoảng 14–17 phút rồi điều chỉnh theo thời lượng giảng viên giao; đây không phải thời lượng quy định trong đề.")

# 02 — Landscape; the scope is explicit.
s = slide("Bagging trong bức tranh học tổ hợp", "01 / Cơ sở lý thuyết", "[1], [2], [3], [6], [7]")
for i, (title, desc, end) in enumerate([
    ("Bagging", "Bootstrap\nHọc độc lập", "TRỌNG TÂM TRIỂN KHAI"),
    ("Boosting", "Học tuần tự\nGiảm sai số / loss", "AdaBoost / Gradient Boosting"),
    ("Voting", "Kết hợp nhãn\nhoặc xác suất", "Hard / Soft"),
    ("Stacking", "Dự đoán OOF\n→ học tầng hai", "Meta-model"),
]):
    x = .62 + i * 3.08
    panel(s, x, 2.14, 2.84, 3.67, PALE if i == 0 else BG)
    shape(s, x + .22, 2.48, .38, .05, TEAL if i == 0 else BLUE)
    txt(s, x + .22, 2.83, 2.4, .5, title, 26, NAVY, True)
    txt(s, x + .22, 3.68, 2.42, 1.4, desc, 20, GRAY, leading=1.3)
    txt(s, x + .22, 5.28, 2.42, .4, end, 10.7, TEAL, True)
takeaway(s, "Bagging được triển khai sâu; ba hướng còn lại có minh họa và thực nghiệm.")
note(s, "Bagging học trên các bootstrap; Boosting xây dựng mô hình tuần tự; Voting kết hợp nhãn hoặc xác suất; Stacking học bộ kết hợp từ dự đoán ngoài fold. Các hướng này không hoàn toàn tách rời: Bagging cũng dùng voting. Bài tự triển khai cơ chế Bagging và dùng scikit-learn cho AdaBoost, Voting, Stacking. Phần mở rộng là đối chiếu mô tả trên cùng các lần chia, không chứng minh một họ luôn tốt hơn. Hai slide tiếp theo giải thích cơ chế mới trước khi đi sâu Bagging.")

# 03 — Actual binary SAMME convention used by sklearn 1.8.
s = slide("AdaBoost: tăng trọng số cho mẫu sai", "01 / Boosting", "[3], [6] · AdaBoostClassifier (SAMME) · Ví dụ giả định")
for i, (headline, detail) in enumerate([
    ("Khởi tạo trọng số đều", "Mỗi quan sát train có trọng số 1/N."),
    ("Học cây nông có trọng số", "Tính sai số có trọng số ε của cây."),
    ("Tính trọng số của cây", "SAMME nhị phân: α = ln((1 − ε)/ε)."),
    ("Cập nhật rồi học tiếp", "Tăng trọng số mẫu sai, chuẩn hóa tổng = 1."),
]):
    yy = 2.05 + i * .94
    txt(s, .68, yy, .4, .4, f"{i+1}", 23, TEAL, True)
    txt(s, 1.23, yy, 5.0, .43, headline, 22, NAVY, True)
    txt(s, 1.23, yy + .48, 5.0, .4, detail, 16.5, GRAY)
label(s, 6.75, 2.12, "VÍ DỤ: ε = 0,2; LEARNING RATE = 1", TEAL, 5.7)
txt(s, 6.75, 2.68, 5.55, .6, "α = ln 4 ≈ 1,386", 29, NAVY, True)
table(s, 6.75, 3.48, [1.85, 1.1, 1.1, 1.8], [
    ["Nhóm", "Trước", "Nhân", "Chuẩn hóa"],
    ["Dự đoán sai", "20%", "×4", "50%"],
    ["Dự đoán đúng", "80%", "×1", "50%"],
], .66, 16)
txt(s, 6.75, 5.65, 5.65, .4, "Trọng số thay đổi; chưa phải accuracy tăng.", 16.5, CORAL, True)
takeaway(s, "Thực nghiệm: tối đa 51 cây một mức; tổng hợp theo trọng số của từng cây.")
note(s, "AdaBoost trong sklearn 1.8 dùng SAMME. Tại mỗi vòng, học một cây với trọng số quan sát hiện tại, tính sai số có trọng số ε, rồi gán trọng số cây α. Với hai lớp, 0<ε<0,5 và learning_rate=1, α=ln((1−ε)/ε). Nếu học hoàn hảo hoặc gặp điều kiện dừng, thư viện xử lý riêng. Ví dụ ε=0,2 cho α=ln4≈1,386. Nhóm sai có tổng trọng số 0,2 nhân 4 thành 0,8; nhóm đúng0,8 nhân 1 vẫn 0,8. Chia cho tổng 1,6: hai nhóm đều 0,5. Đây là ví dụ giả định, không phải một vòng chạy đã đo trên dữ liệu u vú. Công thức AdaBoost nhị phân dạng ±1 thường dùng nửa alpha và cập nhật cả nhóm đúng/sai; không trộn hai quy ước. Mô hình có thể dừng trước51 vòng theo điều kiện của thư viện. Cấu hình được cố định, không chọn theo test.")

# 04 — A fixed rule versus an OOF-trained combination.
s = slide("Voting dùng quy tắc; Stacking học bộ kết hợp", "01 / Voting và Stacking", "[3], [7] · VotingClassifier / StackingClassifier")
txt(s, .72, 1.98, 11.95, .55, "Cùng ba loại mô hình: cây độ sâu 3 · Logistic Regression · Gaussian NB", 20, NAVY, True)
for x, title, color in [(.68, "VOTING", TEAL), (6.88, "STACKING", BLUE)]:
    panel(s, x, 2.77, 5.78, 3.2, BG)
    label(s, x + .25, 3.03, title, color, 5.2)
txt(s, .95, 3.61, 5.2, 1.65, "Hard: đếm nhãn.\nSoft: trung bình xác suất.\nTrọng số bằng nhau.", 21, INK, leading=1.5)
txt(s, 7.14, 3.61, 5.2, 1.65, "Dự đoán ngoài fold (OOF).\nLogistic Regression tầng hai.\nHọc lại mô hình cơ sở trên train.", 21, INK, leading=1.5)
txt(s, .95, 5.43, 5.2, .38, "Quy tắc cố định, không học tầng hai.", 16.5, TEAL, True)
txt(s, 7.14, 5.43, 5.2, .38, "OOF: dự đoán cho mẫu chưa dùng để học.", 16.5, BLUE, True)
takeaway(s, "Stacking: 5 fold trong train; chuẩn hóa nằm trong pipeline.")
note(s, 'Ba loại mô hình cơ sở gồm cây độ sâu cố định3, Logistic Regression với StandardScaler và Gaussian Naive Bayes. Voting hard đếm nhãn, soft trung bình xác suất với trọng số bằng nhau. Stacking chia train thành 5 fold: mỗi mô hình chỉ học 4 fold để dự đoán fold còn lại. Ghép các dự đoán ngoài fold thành đầu vào cho Logistic Regression tầng hai. Sau đó các mô hình cơ sở được học lại trên toàn train để dự đoán dữ liệu mới. Scaler ở trong pipeline nên được fit lại trong mỗi fold, không học trên validation/test. stack_method=predict_proba, passthrough=False; sklearn nhị phân bỏ một cột xác suất dư thừa mỗi mô hình. Độ sâu3 của cây cơ sở được cố định trong phần mở rộng, khác cây chọn độ sâu bằng CV của thí nghiệm Bagging gốc. Các mô hình đơn cùng cấu hình cũng được đánh giá để kiểm tra giá trị của tổ hợp. Ví dụ bổ sung khi cần giải thích hard và soft voting: Hard voting chỉ đếm nhãn nên chọn ác với hai trong ba phiếu. Soft voting lấy trung bình xác suất: (0,51 + 0,51 + 0,01)/3 ≈ 0,3433 cho lớp ác, tương ứng khoảng 0,6567 cho lớp lành, nên chọn lành. Hai quy tắc có thể cho kết quả khác; soft không tự động tốt hơn hard. Phần đối chứng ở slide 17 kiểm tra chúng trên cùng các cây đã học thực tế.')

# 05 — Bagging flow.
s = slide("Bagging: lấy mẫu rồi bỏ phiếu", "02 / Cơ chế", "[1], [3] · ensemble_model.py")
for i, (title, body_) in enumerate([
    ("Giữ riêng test", "Chỉ lấy mẫu\ntừ tập train."),
    ("Tạo bootstrap", "N lượt lấy\ncó hoàn lại / cây."),
    ("Học B cây", "Một cây học\ntrên mỗi bootstrap."),
    ("Đếm phiếu", "Cùng một mẫu mới\n→ chọn lớp đa số."),
]):
    x = .62 + i * 3.1
    label(s, x, 2.38, f"BƯỚC {i + 1}", w=2.65)
    rule(s, x, 2.94, x + 2.65, 2.94, LINE, 2)
    txt(s, x, 3.28, 2.72, .65, title, 24, NAVY, True)
    txt(s, x, 4.27, 2.72, 1.15, body_, 21, GRAY)
    if i < 3: arrow(s, x + 2.72, 3.45, .25)
takeaway(s, "Mỗi bootstrap lấy N lượt có hoàn lại từ cùng tập train.")
note(s, "Mỗi bootstrap có N lượt lấy có hoàn lại, nên một quan sát có thể lặp hoặc không xuất hiện. Mỗi cây học trên bootstrap riêng rồi cùng dự đoán một quan sát mới. Các cây học độc lập về quy trình, không có nghĩa dự đoán của chúng độc lập thống kê. Mã minh họa huấn luyện tuần tự. Mô hình tham chiếu có N = 426, B = 51 và max_depth = 3. Số cây lẻ tránh hòa trong bài toán hai lớp; khi có nhiều lớp vẫn có thể hòa, mã chọn lớp đầu trong classes_.")

# 06 — One connected toy example, starting with the data.
s = slide("5 quan sát → 3 tập bootstrap", "02 / Ví dụ tính tay", "examples/toy_bagging.py · Dữ liệu giả lập")
label(s, .67, 1.98, "DỮ LIỆU GỐC")
for i, (x, y) in enumerate(zip(T["dataset"]["feature_values"], T["dataset"]["labels"])):
    xx = 3.0 + i * 1.87
    txt(s, xx, 1.95, 1.6, .44, f"x = {int(x)}", 22, NAVY, True, PP_ALIGN.CENTER)
    txt(s, xx, 2.48, 1.6, .35, "Lành" if y else "Ác", 17, TEAL if y else CORAL, align=PP_ALIGN.CENTER)
rows = [["Cây", "Chỉ số bootstrap (từ 0)", "Quan sát vắng mặt"]]
for i, tr in enumerate(T["trees"]):
    rows.append([f"h{i + 1}", str(tr["bootstrap_indices"]), ", ".join(str(k) for k in tr["omitted_indices"])])
table(s, .67, 3.2, [1.6, 6.5, 3.85], rows, .65, 20)
takeaway(s, "Có lặp, có quan sát vắng mặt; tổng số lượt lấy vẫn bằng N.")
note(s, "Ví dụ gồm x = [1, 2, 3, 4, 5] và y = [1, 1, 0, 0, 0], với nhãn 1 là lành, nhãn 0 là ác. Các chỉ số hàng bắt đầu từ 0. Ba bootstrap được chọn cố định để dễ tính tay: h₁ vắng hàng 3, h₂ vắng hàng 2 và h₃ vắng hàng 0. Đây là dữ liệu giả lập, không đại diện cho một đặc trưng y tế cụ thể. Trong thí nghiệm chính, bootstrap vẫn được sinh ngẫu nhiên có hoàn lại theo seed.")

# 07 — Gini and a minimal decision tree.
s = slide("Gini chọn ngưỡng 2,5", "02 / Ví dụ tính tay", "examples/toy_bagging.py · [5]")
label(s, .67, 2.1, "TRƯỚC KHI CHIA")
txt(s, .67, 2.67, 5.5, .52, "3 lành + 2 ác", 30, NAVY, True)
txt(s, .67, 3.44, 5.5, .9, "Gini = 1 − (3/5)² − (2/5)²\n        = 0,48", 24, TEAL, leading=1.3)
table(s, .67, 4.82, [2.55, 2.6], [["Ngưỡng", "Gini sau chia"], ["1,5 / 2,5 / 4,0", "0,2667 / 0 / 0,30"]], .58, 16)
panel(s, 6.8, 2.05, 5.88, 3.85, BG)
panel(s, 8.33, 2.48, 2.8, .7, NAVY)
txt(s, 8.55, 2.65, 2.36, .38, "x ≤ 2,5 ?", 24, WHITE, True, PP_ALIGN.CENTER)
rule(s, 9.0, 3.2, 8.1, 4.15, LINE, 2); rule(s, 10.45, 3.2, 11.36, 4.15, LINE, 2)
txt(s, 7.58, 3.57, 1.2, .3, "ĐÚNG", 11, TEAL, True)
txt(s, 10.7, 3.57, 1.2, .3, "SAI", 11, CORAL, True)
txt(s, 7.18, 4.26, 2.6, .48, "3 lành", 27, TEAL, True, PP_ALIGN.CENTER)
txt(s, 9.98, 4.26, 2.4, .48, "2 ác", 27, CORAL, True, PP_ALIGN.CENTER)
txt(s, 7.28, 5.05, 5.0, .4, "Cả hai nhánh: Gini = 0", 20, GRAY, align=PP_ALIGN.CENTER)
takeaway(s, "Ngưỡng 2,5: Gini giảm từ 0,48 xuống 0.")
note(s, "Bootstrap của h₁ có các giá trị [1, 1, 3, 5, 2], gồm ba nhãn lành và hai nhãn ác. Gini ban đầu bằng 0,48. Các ngưỡng ứng viên là 1,5; 2,5 và 4,0, cho Gini sau chia lần lượt 0,2667; 0 và 0,30. Ngưỡng 2,5 có mức giảm lớn nhất nên được chọn. h₂ thiếu x = 3 nên học ngưỡng 3,0; h₃ có ngưỡng 2,5. Phép tính được đối chiếu với cây một mức của scikit-learn, không phải bộ học cây do nhóm tự cài từ đầu.")

# 08 — Voting remains linked to exactly those three fitted trees.
s = slide("Tại x = 2,8: hai phiếu ác, một phiếu lành", "02 / Ví dụ tính tay", "Cùng ba bootstrap ở slide 6 · examples/toy_bagging.py")
for i, tr in enumerate(T["trees"]):
    x = .67 + i * 4.13; pred = tr["query_prediction"]
    panel(s, x, 2.22, 3.79, 2.65, BG)
    label(s, x + .25, 2.51, f"CÂY h{i + 1}")
    rel = "≤" if 2.8 <= tr["threshold"] else ">"
    txt(s, x + .25, 3.12, 3.3, .47, f"2,8 {rel} {num(tr['threshold'], 1)}", 28, NAVY, True)
    txt(s, x + .25, 3.94, 3.3, .5, "Lành tính" if pred else "Ác tính", 27, TEAL if pred else CORAL, True)
txt(s, .7, 5.17, 4.3, .8, "2 : 1", 46, CORAL, True)
txt(s, 4.72, 5.34, 7.7, .6, "Hard voting chọn ác tính (0).", 25, NAVY, True)
takeaway(s, "Ví dụ giả lập, chưa có nhãn thật; tỷ lệ phiếu không phải xác suất bệnh.")
note(s, "Đưa cùng quan sát mới x = 2,8 qua ba cây. Với h₁ và h₃, giá trị này lớn hơn ngưỡng 2,5 nên dự đoán ác, nhãn 0. Với h₂, 2,8 nhỏ hơn hoặc bằng ngưỡng 3,0 nên dự đoán lành, nhãn 1. Tổ hợp có hai phiếu ác và một phiếu lành, vì vậy chọn nhãn 0. Đây chỉ là minh họa quy tắc đa số. Mẫu mới chưa có nhãn thật, nên chưa thể kết luận dự đoán đúng hay sai; tỷ lệ phiếu cũng chưa phải xác suất bệnh.")

# 09 — Data and train-only model selection.
s = slide("569 mẫu: chọn cấu hình trên train", "03 / Dữ liệu và giao thức", "Breast Cancer Wisconsin Diagnostic · seed 42 · [4]")
for x, value, caption in [(.73, "569", "quan sát"), (4.83, "30", "đặc trưng số"), (8.93, "2", "lớp: ác (0), lành (1)")]:
    txt(s, x, 2.03, 3.4, .85, value, 44, TEAL, True)
    txt(s, x, 3.04, 3.4, .4, caption, 19, GRAY)
panel(s, .67, 3.87, 8.1, 2.13, PALE)
label(s, .94, 4.13, "TRAIN 426 MẪU · 75%", TEAL, 7.4)
txt(s, .95, 4.86, 3.0, .5, "CV 5 fold", 27, NAVY, True)
arrow(s, 4.2, 5.04, .4)
txt(s, 5.02, 4.86, 3.1, .5, "Độ sâu 3", 27, TEAL, True)
panel(s, 9.02, 3.87, 3.64, 2.13, NAVY)
label(s, 9.3, 4.13, "TEST GIỮ RIÊNG", MINT, 3.05)
txt(s, 9.3, 4.86, 3.05, .65, "143 mẫu", 30, WHITE, True)
takeaway(s, "Chọn độ sâu bằng cây đơn trên train, rồi dùng chung cho ba mô hình.")
note(s, "Dữ liệu gồm 569 quan sát, 212 mẫu ác và 357 mẫu lành, với 30 đặc trưng số đã trích xuất từ nhân tế bào. Ác tính có nhãn 0 và được quy ước là lớp dương. Seed 42 chia có phân tầng theo tỷ lệ 75/25: train 426 gồm 159 ác, 267 lành; test 143 gồm 53 ác, 90 lành. Chỉ trên train, CV phân tầng năm fold thử độ sâu 2–6; độ sâu 3 đạt balanced accuracy CV cao nhất, 93,73%. Độ sâu được chọn bằng cây đơn rồi dùng chung cho ba mô hình; chưa tối ưu riêng từng ensemble. Test không tham gia lựa chọn. Mỗi seed 42–51 lặp lại quy trình này.")

# 10 — Readable source code, one operation per slide.
s = slide("Code 1: tạo bootstrap và học cây", "04 / Triển khai", "Trích lược ensemble_model.py · ManualBagging.fit")
code(s, .67, 2.0, 8.21, '''indices = rng.integers(
    0, n_samples, size=n_samples
)
tree = DecisionTreeClassifier(
    max_depth=self.max_depth,
    random_state=int(rng.integers(0, 2**31 - 1)),
)
tree.fit(X[indices], encoded[indices])
self.estimators_.append(tree)''', 4.11)
for i, (a, b) in enumerate([("Lấy có hoàn lại", "Có thể lặp chỉ số."), ("Seed riêng từng cây", "Hỗ trợ tái lập."), ("Đúng cặp X và y", "Dùng cùng indices.")]):
    yy = 2.28 + 1.17 * i
    label(s, 9.25, yy, f"0{i+1}", TEAL, 3.1)
    txt(s, 9.25, yy + .32, 3.15, .42, a, 20, NAVY, True)
    txt(s, 9.25, yy + .85, 3.15, .35, b, 15.5, GRAY)
takeaway(s, "Tự viết bootstrap, voting và OOB; cây cơ sở dùng scikit-learn.")
note(s, "Đoạn trích nằm trong phương thức fit; X ở đây chỉ chứa train. Nhãn encoded được tạo bằng np.unique(y, return_inverse=True), giúp đưa các lớp về chỉ số liên tiếp. Bộ sinh rng khởi tạo từ random_state, rồi sinh n_samples chỉ số có hoàn lại và seed cho từng cây. Mỗi cây học X và nhãn trên cùng chỉ số bootstrap. Mã đầy đủ còn lưu estimators_samples_ để truy vết và tính OOB. Cây DecisionTreeClassifier dùng thư viện; phần nhóm tự triển khai là tổ chức lấy mẫu, nhiều cây và quản lý phiếu.")

# 11 — Voting, with the class mapping retained.
s = slide("Code 2: đếm phiếu và trả về nhãn", "04 / Triển khai", "Trích lược ensemble_model.py · votes / predict")
code(s, .67, 2.0, 8.21, '''counts = np.zeros(
    (len(X), len(self.classes_)), dtype=np.int64
)
rows = np.arange(len(X))
for tree in self.estimators_:
    predicted = tree.predict(X).astype(int)
    np.add.at(counts, (rows, predicted), 1)
labels = self.classes_[counts.argmax(axis=1)]''', 4.11)
txt(s, 9.25, 2.36, 3.12, .85, "Mỗi hàng =\nmột quan sát", 23, NAVY, True)
txt(s, 9.25, 3.72, 3.12, .85, "Mỗi cột =\nmột lớp", 23, NAVY, True)
txt(s, 9.25, 5.06, 3.12, .65, "Tổng phiếu / hàng = B", 18, TEAL, True)
takeaway(s, "Mỗi cây bỏ một phiếu; argmax chọn lớp có nhiều phiếu nhất.")
note(s, "Các cây học nhãn mã hóa nên predict trả về chỉ số cột lớp. np.add.at cộng một phiếu vào đúng hàng và cột; argmax chọn lớp nhiều phiếu nhất, rồi self.classes_ ánh xạ về nhãn gốc. Trong mã đầy đủ, votes và predict là hai phương thức riêng; slide gộp để giải thích. Bộ kiểm thử xác minh hard/soft khác nhãn, cây học một lớp, OOB, phép đo bất đồng và quy trình mở rộng. Chuyển lời cho thành viên thứ hai: từ cơ chế đã kiểm chứng, phần tiếp theo xem các cây hoạt động ra sao trên dữ liệu thực.")

# 12 — Holdout scores and error counts on one slide.
s = slide("Seed 42: Bagging đúng thêm một mẫu", "05 / Kết quả gốc", "outputs/results.json · ác tính (0) là lớp dương")
rows = [["Mô hình", "Accuracy", "Recall ác"]]
for name, m in zip(["Cây đơn", "Bagging", "Random Forest"], R["test_metrics"]):
    rows.append([name, pct(m["accuracy"]), pct(m["recall_malignant"])])
table(s, .67, 2.61, [2.8, 1.65, 1.65], rows, .66, 18.5, (2,))
label(s, 7.06, 2.03, "MA TRẬN BAGGING", TEAL, 5.4)
txt(s, 8.42, 2.61, 3.2, .3, "DỰ ĐOÁN", 11, GRAY, True, PP_ALIGN.CENTER)
for x, name in [(8.46, "Ác"), (10.07, "Lành")]:
    txt(s, x, 3.0, 1.5, .35, name, 18, INK, align=PP_ALIGN.CENTER)
for r, row in enumerate([[49, 4], [3, 87]]):
    txt(s, 7.0, 3.72 + r * .98, 1.25, .4, "Thật ác" if r == 0 else "Thật lành", 16.5, GRAY)
    for c, value in enumerate(row):
        xx, yy = 8.43 + 1.61 * c, 3.45 + .98 * r
        shape(s, xx, yy, 1.53, .92, PALE if r == c else SOFT_RED)
        txt(s, xx, yy + .16, 1.53, .55, str(value), 31, TEAL if r == c else CORAL, True, PP_ALIGN.CENTER)
txt(s, .76, 5.65, 5.9, .43, "Bỏ sót ác: 5 → 4", 25, TEAL, True)
txt(s, 7.08, 5.65, 5.25, .43, "Dương tính giả: 3", 21, GRAY)
takeaway(s, "Bagging vẫn bỏ sót 4/53 mẫu ác tính.")
note(s, "Hàng của ma trận là nhãn thật, cột là dự đoán. Bagging có TP = 49, FN = 4, FP = 3 và TN = 87; cây đơn có TP = 48, FN = 5, FP = 3 và TN = 87. Bagging đúng 136/143, cây đơn đúng 135/143, chênh khoảng 0,70 điểm phần trăm accuracy. Precision ác của Bagging là 94,23%, F1 ác là 93,33%; xem phụ lục chỉ số khi được hỏi. Random Forest có cùng chỉ số tổng hợp ở seed 42 nhưng sai trên những quan sát khác: hai mô hình khác dự đoán ở hàng 291 và 128. Không suy ra tương đương từ điểm tổng hợp. ManualBagging dùng toàn bộ đặc trưng và hard voting; RF sklearn dùng ngẫu nhiên hóa đặc trưng và trung bình xác suất.")

# 13 — Ten paired holdouts.
s = slide("10 lần chia: Bagging cao hơn cây đơn", "05 / Mười lần chia gốc", "outputs/results.json · controlled_comparison.json · seed 42–51")
rows = [["Mô hình", "Accuracy (%)", "Recall ác (%)"]]
for name, m in zip(["Cây đơn", "Bagging", "Random Forest"], R["repeated_evaluation"]["summary"]):
    rows.append([name, avg(m, "accuracy"), avg(m, "recall_malignant")])
table(s, .67, 2.1, [4.45, 3.75, 3.75], rows, .72, 21, (2,))
txt(s, .75, 5.3, 4.0, .7, "+1,96 đpt", 35, TEAL, True)
txt(s, 5.0, 5.24, 7.45, .85, "Accuracy trung bình so với cây đơn.\nSo với RF: chưa có ưu thế nhất quán.", 20, GRAY, leading=1.3)
takeaway(s, "Trung bình ± SD mẫu; các test có thể giao nhau.")
note(s, "Trung bình được trình bày theo phần trăm; SD mẫu theo điểm phần trăm. Mỗi seed đều chia lại 75/25 có phân tầng và chọn độ sâu trên train. Khi so accuracy trong cùng seed, Bagging cao hơn cây đơn 9 lần, bằng 1 lần, thấp hơn 0 lần; chênh lệch trung bình khoảng +1,96 điểm phần trăm. So với RF, các số tương ứng là 2, 4 và 4, chênh lệch trung bình −0,28 điểm phần trăm. Các holdout có thể giao nhau, nên không coi là mười phép thử độc lập hay suy ra giá trị p từ số lần thắng.")

# 14 — New heterogeneous ensembles; source JSON is freshly generated.
s = slide("Mở rộng: tổ hợp và mô hình đơn", "05 / Mở rộng các họ Ensemble", "family_comparison.json · 10 holdout seed 42–51 · trung bình ± SD mẫu")
rows = [["Mô hình", "Accuracy (%)", "Recall ác (%)"]]
for name, shown in [("Manual Bagging", "Bagging tự triển khai"),
                    ("AdaBoost", "AdaBoost"), ("Voting (hard)", "Voting hard"),
                    ("Voting (soft)", "Voting soft"), ("Stacking", "Stacking")]:
    row = FAMILY[name]
    rows.append([shown, avg(row, "accuracy"), avg(row, "recall_malignant")])
table(s, .67, 2.03, [4.45, 3.75, 3.75], rows, .55, 19, (1,), pad_y=.12)
lr = FAMILY["Logistic Regression"]
txt(s, .76, 5.53, 11.8, .5, f"LR đơn: accuracy {avg(lr, 'accuracy')}% — cao nhất trong cấu hình khảo sát.", 18, TEAL, True)
takeaway(s, "Cùng 10 lần chia; cấu hình khác nhau; phân tích hậu nghiệm.")
all_model_notes = "; ".join(f"{r['model']}: accuracy {avg(r, 'accuracy')}%, recall ác {avg(r, 'recall_malignant')}%" for r in F["summary"])
note(s, "Mọi mô hình dùng cùng train/test theo seed 42–51. Ba mô hình gốc được chạy lại và đối chiếu với kết quả cũ. Phần bổ sung dùng cấu hình cố định: AdaBoost tối đa51 cây một mức; Voting/Stacking dùng cây độ sâu 3, Logistic Regression chuẩn hóa trong pipeline và Gaussian NB. Chưa tối ưu riêng từng mô hình. Đây là mở rộng sau khi đã xem kết quả của bài gốc; giữ test ngoài huấn luyện và không tuning theo test không biến dữ liệu đã thấy thành xác nhận độc lập mới. Trung bình theo%, SD theo điểm phần trăm; các test có thể giao nhau. Không quy chênh lệch riêng cho một cơ chế vì kiến trúc/cấu hình khác nhau. Đối chiếu cả mô hình đơn: không mặc định tổ hợp phải tốt hơn Logistic Regression. Toàn bộ số liệu: " + all_model_notes)

# 15 — Editable chart, with precise scope and SD beside it.
s = slide("51 cây đạt BA CV cao nhất trong khảo sát", "06 / Khảo sát bổ sung trên train", "outputs/extensions/analysis.json · CV ngoài 5 fold · không dùng test")
survey = E["tree_count_survey"]["summary"]
count_chart(s, survey)
txt(s, .92, 1.94, 6.8, .28, "BALANCED ACCURACY CV (%)", 11, GRAY, True)
txt(s, 3.0, 5.75, 4.1, .3, "Số cây B (các cấu hình đã xét)", 13, GRAY, align=PP_ALIGN.CENTER)
panel(s, 8.77, 2.13, 3.88, 3.88, BG)
label(s, 9.05, 2.44, "51 CÂY", TEAL, 3)
txt(s, 9.05, 3.04, 3.3, .75, avg(survey[4]), 31, TEAL, True)
txt(s, 9.05, 4.0, 3.15, .6, "BA CV (%) · trung bình ± SD", 17, GRAY)
txt(s, 9.05, 4.84, 3.15, .85, "101 cây: 95,07%\nChưa cải thiện thêm.", 20, NAVY, True, leading=1.3)
takeaway(s, "Khảo sát trên train; 51 cây chưa được chứng minh tối ưu tổng quát.")
note(s, "Khảo sát chỉ dùng 426 mẫu train của seed 42, với năm fold ngoài. Trong phần học của mỗi fold, CV năm fold chọn độ sâu bằng cây đơn; các độ sâu là [2, 6, 2, 2, 6]. Các cấu hình B = [1, 5, 11, 21, 51, 101] dùng chung độ sâu và chuỗi seed tương ứng. Balanced accuracy trung bình tăng đến 95,26% ở 51 cây, rồi còn 95,07% ở 101 cây. SD tại 51 cây là 2,45 điểm phần trăm, không phải khoảng tin cậy. Đây là khảo sát bổ sung, chưa chứng minh 51 tối ưu tổng quát.")

# 16 — Error case as a balanced vote, not a confidence gauge.
s = slide("Mẫu 291: tổ hợp vẫn dự đoán sai", "06 / Phân tích mẫu 291", "outputs/extensions/analysis.json → reference_error")
label(s, .7, 2.12, "NHÃN THẬT: LÀNH TÍNH", TEAL, 7)
txt(s, .7, 2.77, 7.8, .62, "27 phiếu ác / 24 phiếu lành", 32, NAVY, True)
shape(s, .72, 3.93, 11.88 * 27 / 51, .76, CORAL)
shape(s, .72 + 11.88 * 27 / 51, 3.93, 11.88 * 24 / 51, .76, TEAL)
txt(s, .87, 4.09, 5.9, .4, "27 · Ác", 22, WHITE, True)
txt(s, 7.05, 4.09, 5.3, .4, "24 · Lành", 22, WHITE, True, PP_ALIGN.RIGHT)
txt(s, .75, 5.17, 6.9, .65, "Đa số chọn ác → dương tính giả", 25, CORAL, True)
txt(s, 9.02, 5.12, 3.3, .9, "Biên phiếu\n3/51 ≈ 5,88%", 19, GRAY, align=PP_ALIGN.RIGHT)
takeaway(s, "Mẫu đầu tiên có hai phía phiếu, được chọn theo thứ tự test.")
note(s, "Quan sát được chọn có chỉ số test 2, tức mẫu thứ ba khi bắt đầu đếm từ 0, tương ứng hàng dữ liệu 291. Nhãn thật là lành tính, nhãn 1. Bagging nhận 27 phiếu ác và 24 phiếu lành, nên chọn nhãn 0 và tạo lỗi dương tính giả. Biên phiếu bằng 3/51 ≈ 0,0588; chênh lệch hai tỷ lệ là 5,88 điểm phần trăm, chưa phải xác suất bệnh đã hiệu chỉnh. RF dự đoán đúng mẫu này nhưng sai hàng 128, nên tổng FP vẫn bằng 3. Truy vết hai cây ở slide 21.")

# 17 — Controlled comparison and its mechanism on one slide.
s = slide("Đa dạng hơn cần đi cùng cây đủ tốt", "06 / Đối chứng trên train", "controlled_comparison.json · CV 5 fold trên train · trung bình ± SD mẫu")
txt(s, .75, 1.99, 11.85, .43, "426 mẫu train · 51 cây · Cùng bootstrap và seed từng cây", 19, GRAY)
rows = [["Đặc trưng", "Phiếu", "BA CV (%)"]]
for r in C["summary"]:
    rows.append(["Toàn bộ" if r["features"] == "all" else "sqrt", r["aggregation"].capitalize(), avg(r)])
table(s, .67, 2.76, [2.15, 1.25, 3.0], rows, .58, 18, (1, 2), pad_y=.13)
all_hard, sqrt_hard = C["summary"][0], C["summary"][2]
for yy, title, metric, detail in [
    (2.81, "BẤT ĐỒNG GIỮA CÁC CÂY", "pair_disagreement", "Tăng khi dùng sqrt"),
    (4.43, "BA TRUNG BÌNH MỘT CÂY", "mean_tree_balanced_accuracy", "Giảm khi dùng sqrt"),
]:
    label(s, 7.66, yy, title, TEAL, 4.85)
    value = f"{pct(all_hard[metric + '_mean'])} → {pct(sqrt_hard[metric + '_mean'])}"
    txt(s, 7.66, yy + .43, 4.95, .63, value, 27, NAVY, True)
    txt(s, 7.66, yy + 1.08, 4.85, .31, detail, 16, GRAY)
takeaway(s, "Trong khảo sát này, sqrt tăng bất đồng nhưng chưa cải thiện tổ hợp.")
note(s, 'Đối chứng 2 × 2 tách hai yếu tố: xét toàn bộ đặc trưng hoặc sqrt; hard voting hoặc trung bình xác suất. Chỉ dùng 426 mẫu train của seed 42, không dùng test 143. Cùng năm fold ngoài, trong phần học mỗi fold, CV năm fold chọn độ sâu bằng cây đơn rồi dùng chung cho bốn cấu hình. Giữ nguyên bootstrap và seed từng cây giữa hai nhóm đặc trưng; hard/soft dùng chính cùng các cây đã học. All hard/soft đều đạt 95,26 ± 2,45%; sqrt hard 93,62 ± 3,48%, sqrt soft 93,44 ± 3,77%. All hard/soft trùng nhãn trên 426 lượt dự đoán ngoài fold; sqrt khác ở một quan sát. Giữ hard và đổi all sang sqrt, BA giảm khoảng 1,63 điểm phần trăm. Chưa có kiểm định ý nghĩa thống kê. Đây là phân tích bổ sung sau thí nghiệm gốc, chưa tối ưu riêng mỗi biến thể. D là tỷ lệ các cặp cây dự đoán khác nhãn, trung bình trên các quan sát và fold; chưa phải tương quan lỗi hay mức độc lập. Với hai lớp và 51 cây, D tối đa khoảng 50,98%. Ngẫu nhiên hóa đặc trưng làm tăng bất đồng nhưng giảm chất lượng cây cơ sở; balanced accuracy tổ hợp hard cũng giảm. Điều này chưa chứng minh xét toàn bộ đặc trưng luôn tốt hơn. Công thức phương sai σ²[ρ + (1 − ρ)/B] chỉ tạo trực giác khi các dự đoán số cùng phương sai và tương quan; không suy ρ từ D.')

# 18 — Answer the three questions, then stop the main talk.
s = slide("Ba kết luận từ thực nghiệm", "07 / Kết luận và trao đổi", "Cảm ơn thầy và các bạn · Slide 19–24 dành cho hỏi đáp", dark=True)
for i, (headline, detail) in enumerate([
    ("Bagging cải thiện so với cây đơn", "9/10 lần chia; accuracy trung bình +1,96 đpt."),
    ("Mở rộng không tự động tốt hơn", "LR đơn có accuracy trung bình cao nhất."),
    ("Đa dạng đi cùng chất lượng", "Cây cơ sở cần đủ tốt để tổ hợp có lợi."),
]):
    yy = 1.99 + i * 1.28
    txt(s, .75, yy, .6, .55, f"0{i+1}", 24, MINT, True)
    txt(s, 1.7, yy, 10.6, .52, headline, 27, WHITE, True)
    txt(s, 1.7, yy + .68, 10.6, .5, detail, 19, "C5D6E1")
takeaway(s, "Giới hạn: holdout giao nhau · chưa tối ưu riêng · chưa xác nhận ngoài.", True, y=6.43)
note(s, 'Kết thúc bằng ba ý: Bagging, phạm vi các họ và cân bằng chất lượng/đa dạng. LR đơn có accuracy trung bình cao nhất trong phần mở rộng nên không mặc định tổ hợp tốt hơn; AdaBoost/Stacking cũng chưa phải lựa chọn tối ưu tổng quát.  Bagging liên hệ bootstrap với tổng hợp dự đoán; cải thiện so với cây đơn trong các lần chia đã khảo sát; nhưng tăng số cây hoặc mức bất đồng chưa tự động tạo mô hình tốt hơn. Chưa thể khẳng định Bagging vượt trội nhất quán so với RF, 51 cây tối ưu tổng quát hay mô hình đủ hiệu quả lâm sàng. Phần trình bày chính dừng tại đây. Hai thành viên cùng tham gia hỏi đáp và chỉ mở slide dự phòng phù hợp với câu hỏi. Bộ kiểm thử tự động giúp phát hiện lỗi cài đặt, không thay thế đánh giá ngoài mẫu. Thí nghiệm gốc dùng độ sâu chọn bằng cây đơn rồi dùng chung; phần mở rộng dùng cấu hình cố định riêng từng mô hình, chưa tuning riêng. Gói nộp kèm chương trình, kết quả và báo cáo. Chạy thí nghiệm gốc để tạo results.json trước ba script bổ sung; dùng các phiên bản thư viện trong requirements.txt. Học tuần tự B cây có chi phí xấp xỉ B lần chi phí một cây; dự đoán K quan sát, độ sâu d có bậc O(KBd). Khảo sát số cây và đối chứng chỉ dùng train seed 42; so sánh các họ dùng 10 split đã xuất hiện trong thí nghiệm gốc, nên là phân tích hậu nghiệm chứ không phải xác nhận độc lập. Đây là phân tích cấu trúc, chưa đo thời gian thực. Demo nhanh lưu ở outputs/quick để giữ riêng kết quả mặc định.')

# 19 — OOB and the finite bootstrap interpretation.
s = slide("A. OOB chỉ dùng cây chưa học quan sát đó", "Phụ lục / OOB", "outputs/results.json → oob · [1]", backup=True)
panel(s, .67, 2.08, 6.06, 3.88, BG)
for j, (lab, has_seen) in enumerate([("Cây 1: có mẫu i", True), ("Cây 2: vắng mẫu i", False), ("Cây 3: vắng mẫu i", False)]):
    yy = 2.48 + j * 1.0
    txt(s, .96, yy, 3.6, .43, lab, 21, INK)
    txt(s, 4.56, yy, 1.8, .43, "Không tính" if has_seen else "Được bỏ phiếu", 16.5, GRAY if has_seen else TEAL, True)
stat(s, 7.17, 2.2, pct(R["oob"]["accuracy"]), "Accuracy OOB", "401/426 dự đoán đúng", w=5)
txt(s, 7.17, 5.0, 5.1, .8, "Coverage 100%\nMỗi mẫu: 8–34 phiếu OOB", 21, NAVY, True, leading=1.3)
takeaway(s, "OOB là đánh giá bổ sung, được tính sau chọn độ sâu.")
note(s, "Mỗi quan sát chỉ nhận phiếu OOB từ các cây chưa lấy nó vào bootstrap. Hàng chưa có phiếu được giữ không xác định, tránh dùng argmax trên hàng toàn 0. Lần tham chiếu có coverage 100% và 401/426 dự đoán đúng. Với N = 426, xác suất vắng trong một bootstrap khoảng 36,74%. Số quan sát khác nhau kỳ vọng là 269,47, thực tế trung bình 268,04; số phiếu OOB kỳ vọng mỗi mẫu là 18,74, thực tế 18,91. Coverage khác accuracy. OOB được tính sau chọn độ sâu nên chưa độc lập hoàn toàn với tuning.")

# 20 — Feature ranges, each on its own labelled scale.
s = slide("B. Mẫu 291 giữa các vùng trung tâm của hai lớp", "Phụ lục / Đặc trưng mẫu sai", "Đặc trưng chọn theo nút gốc trên train · outputs/extensions/analysis.json", backup=True)
for j, f in enumerate(E["reference_error"]["comparisons"]):
    yy = 2.1 + j * 1.29
    txt(s, .71, yy + .12, 3.75, .45, f["feature"], 19, NAVY, True)
    low, high = f["benign_q25"], f["malignant_q75"]
    def xx(v): return 5.2 + 5.6 * (v - low) / (high - low)
    rule(s, 5.0, yy + .43, 11.15, yy + .43, LINE, 1)
    for prefix, col in [("benign", TEAL), ("malignant", CORAL)]:
        q1, med, q3 = (f[prefix + k] for k in ("_q25", "_median", "_q75"))
        shape(s, xx(q1), yy + .26, xx(q3) - xx(q1), .34, PALE if prefix == "benign" else SOFT_RED)
        rule(s, xx(med), yy + .22, xx(med), yy + .64, col, 2)
    shape(s, xx(f["value"]) - .07, yy + .34, .14, .18, NAVY, kind=MSO_SHAPE.DIAMOND)
    txt(s, 11.36, yy + .11, 1.16, .42, num(f["value"], 5 if j == 1 else 2), 18, NAVY, True, PP_ALIGN.RIGHT)
    txt(s, 5.05, yy + .77, 1.2, .25, num(low, 3 if j == 1 else 1), 11, GRAY)
    txt(s, 10.0, yy + .77, 1.15, .25, num(high, 3 if j == 1 else 1), 11, GRAY, align=PP_ALIGN.RIGHT)
for x, col, lab in [(1.0, TEAL, "Lành: hộp Q1–Q3"), (4.65, CORAL, "Ác: hộp Q1–Q3"), (8.4, NAVY, "◆ Mẫu 291")]:
    shape(s, x, 6.08, .18, .12, col)
    txt(s, x + .3, 6.0, 3.6, .3, lab, 12, GRAY)
takeaway(s, "Mỗi hàng có thang riêng; ba đặc trưng chỉ cung cấp một phần giải thích.", y=6.48)
note(s, "Ba đặc trưng được chọn từ tần suất xuất hiện tại nút gốc trên train: worst perimeter ở 16 cây, worst concave points ở 14 cây và worst radius ở 9 cây. Giá trị của mẫu 291 lần lượt là 109,10; 0,14890 và 16,25, đều nằm giữa trung vị hai lớp, đồng thời giữa Q3 lớp lành và Q1 lớp ác. Hộp biểu diễn Q1–Q3, vạch là trung vị, hình thoi là mẫu lỗi. Mỗi hàng có thang đo riêng, không so chiều dài giữa các đặc trưng. Phân tích này chưa xác định nguyên nhân y khoa.")

# 21 — Backup: two true paths with honest leaf counts.
s = slide("C. Cùng mẫu 291, hai cây đi tới hai nhãn", "Phụ lục / Truy vết cây", "outputs/extensions/analysis.json · representative_paths", backup=True)
for x, title, lines, final, col in [
    (.68, "CÂY 1 → ÁC", ["worst radius ≤ 16,79500", "worst concave points > 0,14315", "worst symmetry > 0,28855"], "Lá: 18 lượt bootstrap, tất cả nhãn ác.", CORAL),
    (6.88, "CÂY 2 → LÀNH", ["mean concave points ≤ 0,04989", "worst symmetry > 0,16385", "worst perimeter ≤ 127,20000"], "Lá: 256/259 lượt nhãn lành (98,84%).", TEAL),
]:
    panel(s, x, 2.12, 5.78, 3.93, BG)
    label(s, x + .24, 2.46, title, col, 5.3)
    for j, value in enumerate(lines):
        txt(s, x + .25, 3.17 + j * .62, 5.27, .42, f"{j+1}. {value}", 17.2, NAVY)
    txt(s, x + .25, 5.33, 5.27, .55, final, 15.4, col, True)
takeaway(s, "Các lượt bootstrap có thể lặp hàng; độ thuần tại lá không bảo đảm đúng với quan sát mới.")
note(s, "Các ngưỡng trên slide đã làm tròn để dễ đọc; JSON lưu giá trị đầy đủ. Mẫu có worst radius = 16,25; worst concave points = 0,14890; worst symmetry = 0,29620; mean concave points = 0,04819 và worst perimeter = 109,10. Theo hai chuỗi điều kiện khác nhau, cây thứ nhất đến lá chứa 18 lượt nhãn ác; cây thứ hai đến lá có 256 lượt lành và 3 lượt ác. Bootstrap có thể lặp hàng nên số lượt chưa phải số bệnh nhân khác nhau. Hai đường đi chỉ giải thích hai phiếu; tổ hợp cuối dùng đủ 51 cây.")

# 22 — Backup: calculations.
s = slide("D. Tính chỉ số với ác tính là lớp dương", "Phụ lục / Kiểm tra phép tính", "Bagging seed 42 · TP=49, FN=4, FP=3, TN=87", backup=True)
table(s, .67, 2.02, [3.1, 4.35, 4.5], [
    ["Chỉ số", "Công thức", "Kết quả"],
    ["Accuracy", "(TP + TN) / N", "136/143 = 95,10%"],
    ["Precision ác", "TP / (TP + FP)", "49/52 = 94,23%"],
    ["Recall ác", "TP / (TP + FN)", "49/53 = 92,45%"],
    ["F1 ác", "2TP / (2TP + FP + FN)", "98/105 = 93,33%"],
    ["Specificity", "TN / (TN + FP)", "87/90 = 96,67%"],
    ["Balanced accuracy", "Trung bình recall hai lớp", "94,56%"],
], .56, 17.5)
takeaway(s, "Accuracy test, balanced accuracy CV và OOB là các phép đánh giá khác nhau.")
note(s, "TP và FN đọc từ hàng nhãn thật ác tính; FP và TN từ hàng nhãn thật lành tính. Với Bagging tại seed 42, TP = 49, FN = 4, FP = 3 và TN = 87. Balanced accuracy bằng (49/53 + 87/90)/2 ≈ 94,56%. Vì lớp dương có nhãn 0, các hàm tính precision, recall và F1 dùng pos_label = 0. Phân biệt accuracy test 95,10% với balanced accuracy CV 95,26% trên train: chúng thuộc hai quy trình khác nhau. Tỷ lệ phiếu cây chưa phải xác suất bệnh đã hiệu chỉnh.")

# 23 — Backup: all individual and ensemble baselines, without hiding strong singles.
s = slide("E. Đủ mười mô hình và các đối chứng đơn", "Phụ lục / Kết quả mở rộng", "family_comparison_summary.csv · 10 holdout · mean% ± SD (đpt)", backup=True)
rows = [["Mô hình / cấu hình", "Accuracy (%)", "Recall ác (%)"]]
short_names = {"Decision Tree": "Cây đơn (CV chọn độ sâu)",
               "Manual Bagging": "Bagging tự triển khai",
               "Random Forest (sklearn)": "Random Forest (sklearn)",
               "Decision Tree (depth=3)": "Cây đơn (độ sâu cố định 3)"}
for row in F["summary"]:
    rows.append([short_names.get(row["model"], row["model"]), avg(row, "accuracy"), avg(row, "recall_malignant")])
table(s, .67, 2.0, [5.45, 3.25, 3.25], rows, .38, 17, pad_y=.07)
takeaway(s, "Không mặc định tổ hợp tốt hơn mô hình đơn; chưa có kiểm định hay dữ liệu xác nhận ngoài độc lập.")
note(s, "Bảng có ba mô hình của thí nghiệm gốc và bảy cấu hình bổ sung. Cây đơn CV được chọn độ sâu 2–6 trên train từng seed; cây đơn độ sâu 3 là đối chứng cùng cấu hình cây trong Voting/Stacking. Logistic Regression dùng StandardScaler trong pipeline; Gaussian NB không chuẩn hóa. Voting và Stacking có cùng ba loại mô hình cơ sở nhưng học các bản sao theo quy trình riêng; không phải cùng các đối tượng đã fit. Với binary predict_proba, sklearn Stacking bỏ cột đầu dư thừa và giữ xác suất lớp1 lành của mỗi mô hình làm ba đặc trưng tầng hai. AdaBoost dùng tối đa 51 stumps với learning_rate=1, có thể dừng sớm. Cấu hình được cố định trước khi chạy phần bổ sung, sau khi đã xem thí nghiệm gốc; không diễn giải thành kiểm định xác nhận độc lập. " + all_model_notes)

# 24 — Backup: sources and executable commands.
s = slide("F. Tài liệu tham khảo và cách tái lập", "Phụ lục / Nguồn", "Danh mục đầy đủ và DOI nằm trong báo cáo Word/PDF", backup=True)
references = [
    "[1] Breiman (1996). Bagging Predictors. Machine Learning 24, 123–140.",
    "[2] Breiman (2001). Random Forests. Machine Learning 45, 5–32.",
    "[3] scikit-learn User Guide. Ensemble methods.",
    "[4] scikit-learn API. load_breast_cancer.",
    "[5] scikit-learn User Guide. Decision Trees.",
    "[6] Freund & Schapire (1997). An Application to Boosting. JCSS 55(1).",
    "[7] Wolpert (1992). Stacked Generalization. Neural Networks 5(2).",
]
txt(s, .73, 2.03, 11.9, 2.6, "\n".join(references), 15.8, INK, leading=1.52)
panel(s, .67, 4.93, 11.95, 1.65, NAVY)
txt(s, .93, 5.10, 11.4, 1.35, "python de_5_ensemble_learning.py\npython experiments/report_extensions.py\npython experiments/controlled_comparison.py\npython experiments/ensemble_families.py", 16.5, WHITE, font=MONO, leading=1.24)
note(s, "Tài liệu: [1] https://doi.org/10.1007/BF00058655; [2] https://doi.org/10.1023/A:1010933404324; [3] https://scikit-learn.org/stable/modules/ensemble.html; [4] https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html; [5] https://scikit-learn.org/stable/modules/tree.html; [6] https://doi.org/10.1006/jcss.1997.1504; [7] https://doi.org/10.1016/S0893-6080(05)80023-1. Mã nhóm: https://github.com/Huyngaongow/hocmaygk. Dùng Python 3.12 và requirements.txt. Chạy thí nghiệm gốc trước ba phân tích bổ sung. Kiểm thử: python -m unittest discover -s tests -v. Ví dụ: python examples/toy_bagging.py. Demo nhanh: python de_5_ensemble_learning.py --repeats 1 --output-dir outputs/quick. Dùng Python trong venv đã cài thư viện; trên Windows có thể gọi trực tiếp .venv\\Scripts\\python.exe.")

assert len(P.slides) == len(NOTES) == TOTAL_SLIDES
OUT = ROOT / "De_5_Ensemble_Learning.pptx"
P.save(OUT)
md = ["# Lời thuyết trình — Đề 5: Ensemble Learning", "",
      "24 slide: 18 slide chính và 6 slide dự phòng. Gợi ý luyện tập 14–17 phút; thời lượng thực tế theo giảng viên.", "",
      "Phân chia gợi ý: Nguyễn Nghĩa Hiếu slide 1–11; Trần Quốc Bảo slide 12–18; cả hai tham gia hỏi đáp. Đây là phương án luyện tập, không phải xác nhận lịch sử đóng góp.", "",
      "Nguồn số liệu: outputs/results.json, outputs/extensions/analysis.json, controlled_comparison.json và family_comparison.json. Khảo sát số cây/đối chứng dùng train seed 42; mở rộng các họ dùng lại10split seed 42–51, là phân tích hậu nghiệm.", ""]
for idx, title, content in NOTES:
    md.extend([f"## Slide {idx:02d} — {title}", "", content, ""])
(ROOT / "presentation/loi_thuyet_trinh.md").write_text("\n".join(md), encoding="utf-8")
print(f"Saved {OUT} ({len(P.slides)} slides; editable shapes, chart, speaker notes and manual Fade transitions)")
