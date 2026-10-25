"""Build the Vietnamese topic-5 presentation from verified experiment outputs.

Run from any directory: python3 presentation/create_presentation.py
Requires python-pptx. All slide graphics and text are editable PowerPoint shapes.
"""

import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
RESULT = json.loads((ROOT / "outputs/results.json").read_text())
OUT = ROOT / "De_5_Ensemble_Learning.pptx"

prs = Presentation()
prs.slide_width = Inches(13.333333)
prs.slide_height = Inches(7.5)
prs.core_properties.title = "Đề 5 — Ensemble Learning"
prs.core_properties.subject = "Tiểu luận giữa kỳ — Nhập môn học máy"
prs.core_properties.author = "Nhóm trình bày (bổ sung tên thành viên)"
prs.core_properties.keywords = "Ensemble Learning, Bagging, Voting, Boosting, Stacking"
prs.core_properties.comments = "Generated from verified local experiment results; speaker notes included."

NAVY = "102537"
TEAL = "087E83"
MINT = "79E2CC"
ORANGE = "E67B47"
CREAM = "F7F5EE"
WHITE = "FFFFFF"
INK = "173246"
GRAY = "566A76"
PALE = "E9EFEC"
LINE = "D3DFDA"
RED = "AD493B"
FONT = "Noto Sans"
MONO = "DejaVu Sans Mono"
notes = []


def rect(slide, x, y, w, h, fill, line=None, radius=False):
    obj = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h),
    )
    obj.fill.solid()
    obj.fill.fore_color.rgb = RGBColor.from_string(fill)
    obj.line.fill.background() if line is None else None
    if line:
        obj.line.color.rgb = RGBColor.from_string(line)
    if radius:
        obj.adjustments[0] = 0.12
    return obj


def text(slide, x, y, w, h, content, size=20, color=INK,
         bold=False, align=PP_ALIGN.LEFT, font=FONT, valign=MSO_ANCHOR.TOP):
    obj = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = obj.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.01)
    tf.margin_top = tf.margin_bottom = Inches(0.01)
    tf.vertical_anchor = valign
    for i, line in enumerate(str(content).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.alignment = align
        p.font.name = font
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = RGBColor.from_string(color)
        p.space_after = Pt(5)
    return obj


def line(slide, x1, y1, x2, y2, color=LINE, width=1.5):
    obj = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2)
    )
    obj.line.color.rgb = RGBColor.from_string(color)
    obj.line.width = Pt(width)
    return obj


def arrow(slide, x, y, w=0.42, h=0.25, color=TEAL):
    obj = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    obj.fill.solid()
    obj.fill.fore_color.rgb = RGBColor.from_string(color)
    obj.line.fill.background()
    return obj


def circle(slide, x, y, diameter, fill, label="", size=22, color=WHITE):
    obj = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(diameter), Inches(diameter))
    obj.fill.solid()
    obj.fill.fore_color.rgb = RGBColor.from_string(fill)
    obj.line.fill.background()
    if label:
        text(slide, x, y + diameter * .21, diameter, diameter * .58, label, size, color, True, PP_ALIGN.CENTER)
    return obj


def tag(slide, x, y, label, color=TEAL, w=1.8):
    rect(slide, x, y, w, .32, color, radius=True)
    text(slide, x + .08, y + .035, w - .16, .25, label, 10, WHITE, True)


def card(slide, x, y, w, h, title, body, accent=TEAL, dark=False):
    rect(slide, x, y, w, h, "1C384B" if dark else WHITE, radius=True)
    rect(slide, x + .22, y + .25, .42, .055, accent)
    text(slide, x + .25, y + .46, w - .5, .75, title, 23, WHITE if dark else INK, True)
    text(slide, x + .25, y + 1.28, w - .5, h - 1.4, body, 18, "C9D8DF" if dark else GRAY)


def slide(title, section, dark=False, source="", subtitle=None):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = RGBColor.from_string(NAVY if dark else CREAM)
    rect(s, .55, .35, .35, .06, MINT if dark else TEAL)
    text(s, 1.03, .25, 11.2, .3, section.upper(), 10, MINT if dark else TEAL, True)
    text(s, .55, .75, 12.1, .8, title, 30, WHITE if dark else INK, True)
    if subtitle:
        text(s, .58, 1.5, 12, .5, subtitle, 16, "C9D8DF" if dark else GRAY)
    line(s, .55, 7.05, 12.75, 7.05, "375161" if dark else LINE, .7)
    text(s, .57, 7.13, 4.8, .2, "ĐỀ 5  /  ENSEMBLE LEARNING", 8, "AFC4CF" if dark else GRAY)
    text(s, 5.0, 7.13, 7.2, .2, source, 8, "AFC4CF" if dark else GRAY, align=PP_ALIGN.RIGHT)
    text(s, 12.3, 7.1, .45, .25, f"{len(prs.slides):02d}", 10, MINT if dark else TEAL, True, PP_ALIGN.RIGHT)
    return s


def note(s, content):
    s.notes_slide.notes_text_frame.text = content
    notes.append((len(prs.slides), s.shapes[2].text if s.shapes[2].has_text_frame else "", content))


def table(s, x, y, widths, row_h, rows, highlight=None, font_size=17):
    for r, values in enumerate(rows):
        xx = x
        for c, (val, width) in enumerate(zip(values, widths)):
            fill = NAVY if r == 0 else ("DDF1E9" if r == highlight else WHITE)
            rect(s, xx, y + r * row_h, width - .025, row_h - .025, fill)
            text(s, xx + .15, y + r * row_h + .12, width - .3, row_h - .16,
                 val, font_size, WHITE if r == 0 else INK, r == 0 or r == highlight,
                 PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER)
            xx += width


# 01 — title
s = slide("", "Tiểu luận giữa kỳ • Nhập môn học máy", dark=True)
text(s, .65, 1.45, 8.0, 1.85, "ENSEMBLE\nLEARNING", 55, WHITE, True)
text(s, .68, 3.65, 7.7, 1.0, "Từ cây quyết định\nđến mô hình tổ hợp", 27, MINT)
text(s, .68, 5.05, 7.7, .5, "Đề 5  •  Bagging và bỏ phiếu đa số", 19, WHITE)
text(s, .68, 6.15, 8.5, .55, "Nhóm: [Điền tên thành viên]   |   Lớp: [Điền lớp]", 14, "C9D8DF")
for xx, yy, lab, col in [(9.4, 1.55, "h₁", TEAL), (10.85, 2.75, "h₂", TEAL), (9.4, 3.95, "h₃", TEAL)]:
    circle(s, xx, yy, 1, col, lab, 28)
line(s, 10.4, 2.05, 11.45, 5.6, MINT, 2)
line(s, 11.35, 3.75, 11.45, 5.6, MINT, 2)
line(s, 10.4, 4.45, 11.45, 5.6, MINT, 2)
circle(s, 10.83, 5.3, 1.25, ORANGE, "H", 34)
note(s, "Mở đầu: Một cây quyết định có thể thay đổi đáng kể khi dữ liệu huấn luyện thay đổi. Ensemble Learning kết hợp nhiều mô hình để giảm tác động của những sai lệch riêng. Bài này giới thiệu các họ phương pháp, sau đó đi sâu vào bootstrap và hard voting qua Bagging tự triển khai. Mã cây cơ sở dùng scikit-learn; phần lấy mẫu và tổng hợp phiếu do nhóm tự viết. Trước khi nộp, điền tên thành viên và lớp trên trang bìa. Gợi ý thời lượng phần chính khoảng 15–20 phút; hai trang cuối là phụ lục.")

# 02 — road map / thesis
s = slide("Nhiều mô hình chỉ hữu ích khi có sự đa dạng", "01 • Ý tưởng", source="[1], [2], [3]")
text(s, .65, 1.95, 5.8, 1.4, "Một mô hình có thể sai.\nMột tập mô hình có thể bù lỗi cho nhau.", 28, INK, True)
text(s, .65, 3.75, 5.3, 1.25, "Điều kiện: mô hình cơ sở đủ tốt\nvà lỗi không hoàn toàn giống nhau.", 20, GRAY)
for yy, lab, vote in [(2.0, "Cây 1", "Ác tính"), (3.2, "Cây 2", "Lành tính"), (4.4, "Cây 3", "Ác tính")]:
    rect(s, 7, yy, 2.1, .8, WHITE, radius=True)
    text(s, 7.15, yy+.2, 1.8, .4, lab, 19, INK, True)
    arrow(s, 9.25, yy+.27)
    text(s, 9.85, yy+.15, 2.5, .5, vote, 21, TEAL if vote == "Ác tính" else GRAY, True)
rect(s, .65, 5.85, 11.95, .72, NAVY, radius=True)
text(s, .9, 6.02, 11.5, .4, "Lộ trình: Nguyên lý  →  Ví dụ từng bước  →  Mã nguồn  →  Thực nghiệm", 19, WHITE)
note(s, "Ba phiếu trên trang chỉ minh họa ý tưởng, không phải dự đoán thật của chương trình. Nếu các cây cùng mắc một lỗi thì thêm cây không giải quyết được vấn đề. Hai yếu tố cần cân bằng là chất lượng mô hình cơ sở và tính đa dạng của chúng. Chúng ta sẽ lần lượt trả lời: ensemble kết hợp như thế nào; bootstrap tạo đa dạng ra sao; mã thực hiện phần nào; và kết quả trên dữ liệu độc lập có cải thiện hay không.")

# 03 — taxonomy
s = slide("Bốn cách kết hợp thường gặp", "01 • Bản đồ phương pháp", source="[3]")
items = [
    ("BAGGING", "Song song", "Nhiều mẫu bootstrap\n→ nhiều mô hình\n→ tổng hợp dự đoán", "Ví dụ: Bagged Trees"),
    ("BOOSTING", "Tuần tự", "Mô hình sau tập trung\nvào sai sót / phần dư\ncủa mô hình trước", "Ví dụ: AdaBoost, GBM"),
    ("VOTING", "Quy tắc kết hợp", "Kết hợp nhãn dự đoán\nhoặc xác suất lớp\ncủa nhiều mô hình", "Hard / Soft Voting"),
    ("STACKING", "Học cách kết hợp", "Dự đoán ngoài fold\n→ tạo đặc trưng mới\n→ mô hình tầng hai", "Meta-model"),
]
for i, (name, sub, body, example) in enumerate(items):
    x = .6 + i * 3.08
    card(s, x, 1.95, 2.88, 4.6, name, "", TEAL if i != 1 else ORANGE)
    tag(s, x+.24, 3.15, sub, TEAL if i != 1 else ORANGE, 2.35)
    text(s, x+.25, 3.85, 2.38, 1.6, body, 18, GRAY)
    text(s, x+.25, 5.75, 2.4, .55, example, 13, TEAL, True)
note(s, "Đây là các hướng tiếp cận phổ biến, không phải bốn nhóm tách rời tuyệt đối: Bagging cũng cần một quy tắc tổng hợp như voting. Bagging tạo đa dạng bằng lấy mẫu; Boosting xây dãy mô hình để xử lý sai sót; Voting có thể kết hợp các mô hình khác loại; Stacking học bộ kết hợp từ dự đoán ngoài mẫu. Trọng tâm triển khai của bài là Bagging, nhưng cần hiểu vị trí của nó trong toàn bộ Ensemble Learning. Random Forest là một mở rộng của ý tưởng Bagging cây với ngẫu nhiên hóa đặc trưng.")

# 04 — variance
s = slide("Đa dạng giúp giảm phương sai", "01 • Cơ sở lý thuyết", True, "[1], [2]")
text(s, .65, 1.9, 11.8, .65, "Var(trung bình) = σ² [ ρ + (1 − ρ) / B ]", 29, MINT, True)
text(s, .67, 2.75, 5.45, 1.35, "B: số mô hình\nσ²: phương sai của mỗi mô hình\nρ: tương quan giữa hai mô hình", 20, WHITE)
text(s, .67, 4.5, 5.2, 1.6, "Thêm mô hình giảm phần (1 − ρ)/B.\nPhần ρ vẫn tạo ra giới hạn:\ncác mô hình quá giống nhau ít có lợi.", 21, "C9D8DF")
for y, rho, ratio in [(3.1, "ρ = 0,2", .2+.8/51), (4.55, "ρ = 0,8", .8+.2/51)]:
    text(s, 6.65, y, 5.4, .4, f"B = 51, {rho}  →  {ratio:.3f} σ²".replace("0.", "0,"), 20, WHITE, True)
    rect(s, 6.65, y+.6, 5.3, .28, "28485A", radius=True)
    rect(s, 6.65, y+.6, 5.3*ratio, .28, MINT if y <4 else ORANGE, radius=True)
text(s, 6.65, 6.05, 5.65, .65, "Giả thiết: cùng phương sai và tương quan cặp chung; áp dụng cho trung bình dự đoán số.", 13, "C9D8DF")
note(s, "Công thức này giải thích trực giác giảm phương sai khi lấy trung bình các dự đoán số. Giả thiết các mô hình có phương sai như nhau σ bình phương và tương quan cặp chung rho. Với 51 mô hình, rho bằng 0,2 cho phương sai trung bình khoảng 0,216 lần phương sai riêng, còn rho bằng 0,8 chỉ giảm xuống khoảng 0,804. Đây không phải công thức trực tiếp của tỷ lệ lỗi phân lớp. Với hard voting, hiệu quả còn phụ thuộc mô hình cơ sở và cấu trúc lỗi. Không thể nói ensemble luôn tốt hơn.")

# 05 — voting
s = slide("Hard Voting và Soft Voting có thể cho kết quả khác", "01 • Quy tắc kết hợp", source="[3]")
table(s, .65, 1.9, [3.15, 2.55, 2.55, 3.75], .73, [
    ["Quan sát x", "Mô hình 1", "Mô hình 2", "Mô hình 3"],
    ["P(ác tính | x)", "0,51", "0,51", "0,01"],
    ["Nhãn dự đoán", "Ác tính", "Ác tính", "Lành tính"],
], font_size=18)
card(s, .65, 4.4, 5.8, 2.1, "HARD → ÁC TÍNH", "Đếm nhãn: 2 phiếu ác tính / 3 phiếu.")
card(s, 6.65, 4.4, 6, 2.1, "SOFT → LÀNH TÍNH", "Trung bình P(ác tính) = 1,03 / 3 ≈ 0,343.", ORANGE)
note(s, "Đây là ví dụ tính tay giả định. Hard voting chỉ dùng nhãn cuối cùng, nên hai trong ba mô hình chọn ác tính thì cả tổ hợp chọn ác tính. Soft voting lấy trung bình xác suất: 0,51 cộng 0,51 cộng 0,01 bằng 1,03; chia ba xấp xỉ 0,343. Xác suất lành tính trung bình khi đó xấp xỉ 0,657, nên chọn lành tính. Với trọng số, thay trung bình đều bằng tổng có trọng số chuẩn hóa. Soft voting cần xác suất đáng tin cậy; không tự động tốt hơn hard voting. Trong mã, ManualBagging dùng hard voting; sklearn Random Forest dùng trung bình xác suất.")

# 06 — bagging pipeline
s = slide("Bagging: lấy mẫu lại, học độc lập, rồi tổng hợp", "02 • Quy trình", source="[1], [3]")
steps = [
    ("01", "Tập train", "N quan sát\nGiữ riêng test"),
    ("02", "Bootstrap", "B mẫu; mỗi mẫu\nN lượt có hoàn lại"),
    ("03", "Huấn luyện", "Một cây / mẫu\nĐộc lập với nhau"),
    ("04", "Tổng hợp", "Phiếu từng cây\n→ lớp đa số"),
]
for i, (num, title_, body) in enumerate(steps):
    x = .65 + i*3.09
    rect(s, x, 2.15, 2.75, 3.35, WHITE, radius=True)
    circle(s, x+.25, 2.42, .64, TEAL, num, 17)
    text(s, x+.25, 3.38, 2.25, .55, title_, 23, INK, True)
    text(s, x+.25, 4.17, 2.25, 1.0, body, 18, GRAY)
    if i<3:
        arrow(s, x+2.79, 3.5, .25, .22)
text(s, .7, 6.05, 11.8, .5, "Thực nghiệm: N = 426 mẫu train  •  B = 51 cây  •  max_depth = 3", 22, TEAL, True)
note(s, "Bagging là viết tắt của bootstrap aggregating. Mỗi cây nhận 426 lượt lấy mẫu từ 426 mẫu train; một quan sát có thể lặp lại nhiều lần, một số quan sát không xuất hiện. Không chia train thành 51 tập rời nhau. Các cây có thể học song song về mặt thuật toán; bản mã minh họa đang huấn luyện tuần tự để đơn giản và tiết kiệm tài nguyên. Test hoàn toàn không tham gia bootstrap. Sau huấn luyện, gửi cùng một quan sát mới qua tất cả các cây rồi đếm phiếu. Bằng cách thay đổi mẫu, các cây có thể học những ranh giới quyết định khác nhau.")

# 07 — bootstrap worked
s = slide("Ví dụ bootstrap: 5 quan sát, 5 lượt lấy mẫu", "02 • Tính từng bước", source="Ví dụ minh họa; lý thuyết bootstrap: [1]")
text(s, .65, 1.85, 11.8, .4, "Tập gốc có chỉ số [0, 1, 2, 3, 4]. Mỗi dòng là một mẫu huấn luyện mới.", 19, GRAY)
table(s, .65, 2.65, [1.6, 5.5, 2.25], .8, [
    ["Cây", "Chỉ số bootstrap", "Không có mặt"],
    ["h₁", "[0, 0, 2, 4, 1]", "3"],
    ["h₂", "[1, 3, 3, 2, 0]", "4"],
    ["h₃", "[4, 2, 4, 1, 3]", "0"],
], font_size=19)
rect(s, 10.3, 2.65, 2.35, 3.18, TEAL, radius=True)
text(s, 10.53, 2.95, 1.9, .5, "CÓ LẶP", 23, WHITE, True)
text(s, 10.53, 3.85, 1.9, 1.5, "Cùng N lượt,\nnhưng không đủ\nN mẫu khác nhau.", 17, WHITE)
text(s, .7, 6.15, 12, .5, "P(một mẫu không được chọn) = (1 − 1/N)ᴺ  →  e⁻¹ ≈ 36,8% khi N lớn", 19, TEAL, True)
note(s, "Chỉ số 0 xuất hiện hai lần trong mẫu của cây 1, trong khi chỉ số 3 không có mặt. Các quan sát không được chọn gọi là out-of-bag đối với cây đó. Với một quan sát cố định, xác suất không chọn ở một lượt là 1 trừ 1/N; qua N lượt độc lập là lũy thừa N. Khi N lớn, xác suất tiến đến e mũ âm một, khoảng 36,8%. Với N bằng 5 trong ví dụ nhỏ, xác suất chính xác là 0,8 mũ 5 bằng 32,768%, không phải đúng 36,8%. Chương trình chưa tính điểm OOB; bài dùng test riêng để đánh giá.")

# 08 — tree math
s = slide("Một cây học phép chia như thế nào?", "02 • Ví dụ tính Gini", source="Ví dụ tính tay; cây quyết định: [5]")
table(s, .65, 1.95, [2.5, 1.8, 1.8, 1.8, 1.8, 2.2], .68, [
    ["Dữ liệu minh họa", "0", "1", "2", "3", "4"],
    ["Đặc trưng x", "1", "2", "3", "4", "5"],
    ["Nhãn", "Lành", "Lành", "Ác", "Ác", "Ác"],
], font_size=17)
text(s, .7, 4.18, 5.4, .75, "Bootstrap h₁: [0, 0, 2, 4, 1]\n→ 3 lành tính, 2 ác tính", 21, INK, True)
text(s, .7, 5.25, 5.4, 1.0, "Gini trước chia\n= 1 − (3/5)² − (2/5)² = 0,48", 21, TEAL, True)
rect(s, 6.65, 4.15, 5.95, 2.4, WHITE, radius=True)
text(s, 6.9, 4.35, 5.4, .6, "Chọn ngưỡng x ≤ 2,5", 24, INK, True)
text(s, 6.9, 5.05, 5.35, 1.05, "Trái: 3 lành  →  Gini = 0\nPhải: 2 ác  →  Gini = 0\nGini sau chia = 0  |  Giảm = 0,48", 19, GRAY)
note(s, "Đây là dữ liệu một chiều giả lập để có thể tính tay, không phải các quan sát của Breast Cancer. Cây 1 dùng bootstrap [0,0,2,4,1], tức là các cặp (1,lành), (1,lành), (3,ác), (5,ác), (2,lành). Gini trước chia bằng 0,48. Với ngưỡng 2,5, nhánh trái có ba mẫu đều lành, nhánh phải có hai mẫu đều ác. Gini mỗi nhánh bằng 0; trung bình có trọng số 3/5 nhân 0 cộng 2/5 nhân 0 cũng bằng 0. Mức giảm là 0,48. Thực tế cây thử các ngưỡng trên nhiều đặc trưng và lặp lại các phép chia đến điều kiện dừng. Trong thí nghiệm độ sâu tối đa là 3.")

# 09 — aggregation formula
s = slide("Từ phiếu riêng lẻ đến quyết định của tổ hợp", "02 • Tính phép tổng hợp", True, "Ví dụ phiếu giả định; không phải đầu ra thí nghiệm")
text(s, .7, 1.85, 12, .7, "H(x) = argmax꜀  Σᵦ  I[hᵦ(x) = c]", 32, MINT, True)
for xx, label, vote in [(1.0, "h₁(x)", "ÁC"), (4.0, "h₂(x)", "LÀNH"), (7.0, "h₃(x)", "ÁC")]:
    text(s, xx, 3.0, 2.2, .5, label, 22, WHITE, True, PP_ALIGN.CENTER)
    circle(s, xx+.35, 3.8, 1.45, TEAL if vote == "ÁC" else "496273", vote, 23)
arrow(s, 9.45, 4.35, .6, .35, MINT)
text(s, 10.45, 3.8, 2.1, .8, "2 : 1", 37, MINT, True)
text(s, 10.45, 4.75, 2.1, .5, "→ Ác tính", 23, WHITE, True)
text(s, .75, 6.15, 11.9, .45, "Mã hóa: ác tính = 0, lành tính = 1.  51 cây tránh hòa phiếu ở bài toán hai lớp.", 18, "C9D8DF")
note(s, "I là hàm chỉ thị: đúng thì nhận 1, sai thì nhận 0. Cộng theo tất cả cây cho từng lớp c. Với ba dự đoán giả định [0,1,0], lớp 0 có hai phiếu còn lớp 1 có một phiếu, nên argmax chọn 0, tức ác tính. Đây là ví dụ riêng để tính phép tổng hợp, không khẳng định là đầu ra của ba cây trong ví dụ chia nút trước đó. Trong triển khai dùng 51 cây cho hai lớp nên không hòa phiếu. Nếu áp dụng đa lớp thì số cây lẻ vẫn có thể hòa; hàm argmax khi hòa chọn chỉ số lớp đầu tiên.")

# 10 — boosting
s = slide("Boosting: mô hình sau tập trung vào sai sót trước", "03 • Mở rộng cách kết hợp", source="[3], [6]")
for i, lab in enumerate(["Mô hình 1", "Tăng trọng số\nmẫu dự đoán sai", "Mô hình 2", "Tổ hợp\ncó trọng số"]):
    x = .65 + 3.09*i
    rect(s, x, 1.95, 2.75, 1.0, TEAL if i%2==0 else NAVY, radius=True)
    text(s, x+.15, 2.13, 2.45, .75, lab, 19, WHITE, True, PP_ALIGN.CENTER)
    if i<3:
        arrow(s, x+2.8, 2.35, .24, .2)
text(s, .7, 3.55, 5.55, .8, "Ví dụ AdaBoost nhị phân\nε = 0,20  →  α = ½ ln(0,8/0,2) ≈ 0,693", 21, INK, True)
text(s, .7, 4.75, 5.55, 1.45, "Mẫu sai: nhân exp(+α) ≈ 2\nMẫu đúng: nhân exp(−α) ≈ 0,5\nSau đó chuẩn hóa tổng trọng số về 1.", 20, GRAY)
card(s, 6.8, 3.55, 5.8, 2.95, "20% → 50%", "Khối lượng trọng số nhóm sai:\n0,2 × 2 / (0,2 × 2 + 0,8 × 0,5) = 0,5.", ORANGE)
note(s, "AdaBoost là ví dụ để giải thích Boosting chứ chưa được triển khai trong mã thực nghiệm này. Nhãn và dự đoán trong công thức cập nhật cổ điển được mã hóa âm một và dương một. Sai số epsilon là tổng trọng số của các mẫu sai, không nhất thiết là tỷ lệ đếm mẫu. Nếu epsilon bằng 0,2, trọng số mô hình alpha bằng một nửa log tự nhiên của bốn, khoảng 0,693. Nhóm sai nhân hai, nhóm đúng nhân một phần hai; chuẩn hóa xong tổng trọng số nhóm sai tăng từ 0,2 lên 0,5. Gradient Boosting lại xây mô hình theo hướng giảm loss, thường khớp gradient âm; không mô tả mọi Boosting bằng duy nhất cập nhật AdaBoost này.")

# 11 — stacking
s = slide("Stacking học một mô hình để kết hợp các mô hình", "03 • Mở rộng cách kết hợp", source="[3], [7]")
card(s, .65, 2.05, 3.5, 3.9, "TẦNG CƠ SỞ", "Cây / SVM / Logistic…\nHuấn luyện theo K fold.\nMỗi mẫu chỉ lấy dự đoán\ntừ mô hình chưa thấy nó.")
arrow(s, 4.28, 3.8, .5, .32)
card(s, 4.95, 2.05, 3.5, 3.9, "ĐẶC TRƯNG OOF", "Một cột / mô hình cơ sở.\nCác dự đoán ngoài fold\ntạo đầu vào cho\nmô hình tầng hai.")
arrow(s, 8.58, 3.8, .5, .32)
card(s, 9.25, 2.05, 3.4, 3.9, "META-MODEL", "Học cách phối hợp\ncác mô hình cơ sở.\nTest chỉ dùng để\nđánh giá cuối cùng.", ORANGE)
text(s, .7, 6.25, 11.9, .45, "Tránh rò rỉ: không huấn luyện tầng hai bằng dự đoán in-sample của tầng cơ sở.", 19, TEAL, True)
note(s, "OOF nghĩa là out-of-fold. Chia train thành K fold. Với mỗi mô hình cơ sở, huấn luyện trên K trừ một fold và dự đoán fold còn lại; ghép các dự đoán để mỗi mẫu train có một dự đoán từ mô hình chưa thấy nó. Các cột OOF này, cùng nhãn train, huấn luyện meta-model. Khi dự đoán dữ liệu mới, mô hình cơ sở được huấn luyện lại trên toàn train, tạo đầu vào cho meta-model đã học. Nếu dùng dự đoán in-sample quá tốt để học meta-model thì tầng hai có thể học một tín hiệu không phản ánh khả năng tổng quát. Stacking ở đây là nội dung lý thuyết mở rộng, chưa chạy thực nghiệm.")

# 12 — data
s = slide("Bài toán: phân loại mẫu khối u vú", "04 • Ứng dụng minh họa", source="[4] • Breast Cancer Wisconsin Diagnostic")
for xx, num, label in [(.65,"569","quan sát"),(3.7,"30","đặc trưng số"),(6.75,"212","ác tính (nhãn 0)"),(9.8,"357","lành tính (nhãn 1)")]:
    text(s, xx, 1.95, 2.8, 1.1, num, 48, TEAL, True)
    text(s, xx, 3.05, 2.8, .7, label, 18, GRAY)
rect(s, .65, 4.15, 5.8, 1.9, WHITE, radius=True)
text(s, .9, 4.4, 5.3, .45, "ĐẦU VÀO", 15, TEAL, True)
text(s, .9, 5.0, 5.15, .75, "Đặc trưng nhân tế bào: radius,\ntexture, perimeter, area…", 20, INK)
arrow(s, 6.55, 4.9, .45, .3)
rect(s, 7.15, 4.15, 5.45, 1.9, NAVY, radius=True)
text(s, 7.4, 4.4, 4.9, .45, "ĐẦU RA", 15, MINT, True)
text(s, 7.4, 5.0, 4.9, .75, "Dự đoán ác tính hoặc lành tính\ncho một quan sát mới.", 20, WHITE)
text(s, .7, 6.45, 11.9, .35, "Mục đích học thuật; chưa xác thực lâm sàng. Dữ liệu có sẵn trong scikit-learn.", 14, GRAY)
note(s, "Dữ liệu Breast Cancer Wisconsin Diagnostic có 569 quan sát và 30 đặc trưng số trích từ ảnh nhân tế bào. Hai nhãn của thư viện là 0 cho malignant, tức ác tính, và 1 cho benign, tức lành tính. Tổng thể có 212 mẫu ác tính và 357 mẫu lành tính. Bài không huấn luyện trực tiếp từ ảnh; đầu vào là bộ đặc trưng đã được chuẩn bị. Các cây không yêu cầu chuẩn hóa thang đo như một số phương pháp khoảng cách. Đây là minh họa học thuật, không phải một hệ thống chẩn đoán đã được xác thực.")

# 13 — design
s = slide("Thiết kế thí nghiệm giữ test ngoài quá trình chọn độ sâu", "04 • Quy trình đánh giá", source="Nguồn: outputs/results.json • seed = 42")
rect(s, .65, 1.95, 8.75, .75, TEAL, radius=True)
rect(s, 9.55, 1.95, 3.05, .75, NAVY, radius=True)
text(s, .9, 2.13, 8.2, .4, "TRAIN 75% • 426 mẫu (159 ác / 267 lành)", 19, WHITE, True)
text(s, 9.75, 2.13, 2.6, .4, "TEST • 143 mẫu", 17, WHITE, True)
text(s, .7, 3.15, 6.3, .5, "CV phân tầng 5 fold trên train", 23, INK, True)
for i, (d, score) in enumerate(RESULT["depth_selection_train_cv_balanced_accuracy"].items()):
    x = .85+i*1.18
    h = (score-.90)*40
    rect(s, x, 5.7-h, .7, h, TEAL if d=="3" else "B7CFC7", radius=True)
    text(s, x-.15, 5.8, 1.0, .4, d, 18, INK, True, PP_ALIGN.CENTER)
    text(s, x-.2, 5.3-h, 1.15, .4, f"{100*score:.2f}%".replace(".",","), 13, TEAL if d=="3" else GRAY, True, PP_ALIGN.CENTER)
text(s, .75, 6.35, 6.15, .4, "Trục độ sâu 2–6; cột hiển thị phần vượt 90% CV.", 12, GRAY)
card(s, 7.35, 3.1, 5.25, 3.55, "CHỌN max_depth = 3", "Balanced accuracy CV = 93,73%.\nChọn bằng cây đơn, dùng chung\ncho cả ba mô hình.\nKhông tối ưu riêng từng ensemble.")
note(s, "Chia dữ liệu bằng train_test_split với stratify bằng nhãn và random_state 42. Test có 53 ca ác tính và 90 ca lành tính. Trong train, thử max_depth từ 2 đến 6 bằng StratifiedKFold năm fold, chọn theo balanced accuracy trung bình. Độ sâu 3 đạt khoảng 93,73%, cao nhất trong các ứng viên. Biểu đồ cột chỉ thể hiện phần vượt 90% để nhìn khác biệt; đây không phải trục bắt đầu từ 0. Độ sâu được chọn trên cây đơn và dùng chung cho Bagging và Random Forest. Thiết kế giúp minh họa đơn giản nhưng không phải tìm cấu hình tối ưu riêng cho từng mô hình. Test chỉ được xem sau khi chốt cấu hình.")

# 14 — code
s = slide("Tự viết hai phần cốt lõi: bootstrap và voting", "05 • Triển khai Python", source="Trích lược de_5_ensemble_learning.py • NumPy + scikit-learn")
rect(s, .65, 1.95, 6.2, 4.25, NAVY, radius=True)
rect(s, 7.05, 1.95, 5.55, 4.25, NAVY, radius=True)
text(s, .9, 2.15, 5.7, .4, "01  LẤY MẪU & HUẤN LUYỆN", 15, MINT, True)
code1 = "indices = rng.integers(\n    0, len(X), size=len(X)\n)\ntree = DecisionTreeClassifier(\n    max_depth=self.max_depth,\n    random_state=...\n)\ntree.fit(X[indices], encoded[indices])\nself.trees_.append(tree)"
text(s, .9, 2.9, 5.75, 2.9, code1, 14, WHITE, font=MONO)
text(s, 7.3, 2.15, 5.0, .4, "02  ĐẾM PHIẾU & CHỌN LỚP", 15, MINT, True)
code2 = "predictions = np.asarray([\n    tree.predict(X)\n    for tree in self.trees_\n])\n# Với mỗi lớp, đếm số cây chọn lớp đó\nnp.sum(predictions == label, axis=0)\n\n# Dự đoán cuối cùng\nself.classes_[votes.argmax(axis=1)]"
text(s, 7.3, 2.9, 5.0, 2.9, code2, 13.2, WHITE, font=MONO)
text(s, .7, 6.4, 11.9, .4, "Cây cơ sở dùng thư viện; quy trình Bagging và hard voting do mã minh họa triển khai.", 18, TEAL, True)
note(s, "Đây là mã trích lược để vừa slide; dấu ba chấm thay phần cấp seed riêng cho mỗi cây, còn mã đầy đủ nằm trong file Python. rng.integers tạo len(X) chỉ số trong khoảng từ 0 đến len(X) trừ một, cho phép trùng chỉ số. encoded là nhãn đã ánh xạ sang chỉ số lớp bởi np.unique. Mỗi cây dùng các hàng X và nhãn theo cùng indices. Phần voting tạo ma trận số cây nhân số quan sát; so sánh với một lớp và cộng dọc theo trục cây để đếm số phiếu. Cuối cùng argmax lấy lớp có nhiều phiếu, rồi ánh xạ về nhãn gốc. Không nhận phần cài cây quyết định là tự viết.")

# 15 — RF exact difference
s = slide("Bagging tự viết và Random Forest khác nhau ở đâu?", "05 • Mô hình đối chiếu", source="[2], [3] • RandomForestClassifier mặc định max_features='sqrt'")
table(s, .65, 2.0, [3.1, 4.5, 4.4], .85, [
    ["Thành phần", "Manual Bagging", "Random Forest (sklearn)"],
    ["Lấy mẫu train", "Bootstrap", "Bootstrap"],
    ["Đặc trưng khi chia", "Xét toàn bộ 30 đặc trưng", "Tập con ngẫu nhiên (√30 → 5)"],
    ["Kết hợp cây", "Đa số nhãn dự đoán", "Trung bình xác suất lớp"],
    ["Cấu hình thí nghiệm", "51 cây, max_depth = 3", "51 cây, max_depth = 3"],
], font_size=16)
text(s, .75, 6.5, 11.8, .35, "Ngẫu nhiên hóa đặc trưng giúp giảm tương quan; không bảo đảm mọi cây sẽ có lỗi khác nhau.", 15, TEAL, True)
note(s, "Cả hai phương pháp sử dụng bootstrap nhưng Random Forest ngẫu nhiên hóa cả việc chọn đặc trưng ở từng phép chia. Với mặc định max_features bằng sqrt và 30 đặc trưng, giá trị mục tiêu là 5. Thư viện có thể xem thêm đặc trưng để tìm phép chia hợp lệ, nên không hiểu là giới hạn cứng tuyệt đối trong mọi trường hợp. Khác biệt quan trọng nữa là quy tắc kết hợp: ManualBagging đếm nhãn cứng, RandomForestClassifier lấy trung bình xác suất của các cây rồi chọn lớp lớn nhất. Vì vậy không mô tả thí nghiệm như thể chỉ thay đổi một yếu tố đặc trưng. Đây là hai baseline để đối chiếu, không phải nghiên cứu tách riêng tác động từng thành phần.")

# 16 — results
s = slide("Bagging cải thiện nhẹ trên lần chia test này", "06 • Kết quả thực nghiệm", source="Nguồn: outputs/results.json • test n = 143 • số liệu đã làm tròn")
rows = [["Mô hình", "Accuracy", "Precision*", "Recall*", "F1*"]]
for name, row in zip(["Cây quyết định đơn", "Bagging tự viết", "Random Forest"], RESULT["test_metrics"]):
    rows.append([name] + [f"{row[k]*100:.2f}%".replace(".",",") for k in ["accuracy","precision_malignant","recall_malignant","f1_malignant"]])
table(s, .65, 2.0, [4.0, 2.0, 2.0, 2.0, 2.0], .85, rows, highlight=2, font_size=18)
text(s, .75, 5.6, 11.8, .4, "* Lớp dương: ác tính = 0. Precision, Recall và F1 đều tính cho lớp này.", 17, GRAY)
text(s, .75, 6.25, 11.8, .45, "Accuracy tăng 0,70 điểm phần trăm; không suy ra ưu thế tổng quát từ một lần chia.", 19, TEAL, True)
note(s, "Cây đơn đạt accuracy 94,41%, Bagging và Random Forest cùng đạt 95,10%. Precision, recall và F1 trên bảng đều lấy ác tính làm lớp dương, mặc dù mã nhãn là 0; cần nêu rõ vì nhiều thư viện mặc định lớp 1 là dương. Accuracy của Bagging tương đương dự đoán đúng 136 trên 143 mẫu, cao hơn cây đơn đúng một mẫu. Mức chênh là khoảng 0,70 điểm phần trăm, không phải 0,70% cải thiện tương đối. Hai mô hình có cùng chỉ số tổng hợp không đủ để suy ra giống nhau trên mọi quan sát hoặc mọi dữ liệu. Cần đánh giá lặp lại nếu muốn so sánh chắc chắn.")

# 17 — confusion matrices
s = slide("Nhìn vào ca bỏ sót, không chỉ accuracy", "06 • Phân tích lỗi", source="Hàng = nhãn thật • Cột = dự đoán • Lớp dương = ác tính (0)")
for x, label, matrix in [(1.3,"CÂY ĐƠN",[[48,5],[3,87]]),(7.3,"BAGGING",[[49,4],[3,87]])]:
    text(s, x, 1.88, 4.4, .5, label, 22, TEAL, True, PP_ALIGN.CENTER)
    text(s, x+.8, 2.55, 1.6, .35, "Dự đoán ác", 13, GRAY, align=PP_ALIGN.CENTER)
    text(s, x+2.6, 2.55, 1.6, .35, "Dự đoán lành", 13, GRAY, align=PP_ALIGN.CENTER)
    for r in range(2):
        text(s, x-.65, 3.32+1.08*r, 1.35, .6, "Thật ác" if r==0 else "Thật lành", 13, GRAY, align=PP_ALIGN.RIGHT)
        for c in range(2):
            xx=x+.8+1.8*c; yy=3.05+1.08*r
            rect(s, xx, yy, 1.7, 1.0, TEAL if r==c else ("F4DDD1" if r==0 else WHITE), radius=True)
            text(s, xx, yy+.16, 1.7, .65, str(matrix[r][c]), 29, WHITE if r==c else RED, True, PP_ALIGN.CENTER)
text(s, .75, 5.65, 11.8, .55, "Bỏ sót ác tính: 5/53 → 4/53  |  Recall: 90,57% → 92,45%", 25, INK, True, PP_ALIGN.CENTER)
text(s, .75, 6.45, 11.8, .35, "Bagging vẫn bỏ sót 4 ca; chưa đủ cơ sở sử dụng cho quyết định lâm sàng.", 15, GRAY, align=PP_ALIGN.CENTER)
note(s, "Trong ma trận này hàng là nhãn thật, cột là nhãn dự đoán; thứ tự cả hai trục là ác tính rồi lành tính. Vì ác tính là lớp dương, ô trên trái là TP, ô trên phải là FN. Cây đơn có TP 48 và FN 5; Bagging có TP 49 và FN 4. Cả hai có FP 3 và TN 87. Recall Bagging bằng 49 chia 53, khoảng 92,45%. Precision bằng 49 chia 52, khoảng 94,23%. Giảm được một ca bỏ sót trên tập test này là một quan sát thực nghiệm, chưa chứng minh lợi ích đáng tin cậy khi triển khai thực tế. Ma trận của Random Forest trùng các số đếm tổng hợp của Bagging trong lần chạy.")

# 18 — actual trace
s = slide("Theo dấu một dự đoán thật trong chương trình", "06 • Minh họa đầu ra", True, "Nguồn: outputs/results.json → worked_example")
text(s, .7, 1.85, 11.8, .5, "Quan sát đầu tiên của test  •  Nhãn thật: lành tính", 23, WHITE, True)
rect(s, .7, 2.75, 7.1, 2.8, "1C384B", radius=True)
text(s, .95, 3.0, 6.6, .4, "10 chỉ số train đầu trong bootstrap cây 1", 17, MINT, True)
text(s, .95, 3.7, 6.55, 1.0, "[38, 329, 278, 186, 184,\n 365, 36, 297, 85, 40]", 21, WHITE, font=MONO)
text(s, .95, 4.85, 6.55, .4, "Cả 5 cây đầu đều bỏ phiếu lành tính.", 17, "C9D8DF")
text(s, 8.7, 2.75, 3.3, .65, "TỔNG 51 CÂY", 20, MINT, True)
text(s, 8.7, 3.55, 3.3, .9, "0 : 51", 48, WHITE, True)
text(s, 8.7, 4.6, 3.5, .55, "Ác tính : Lành tính", 18, "C9D8DF")
text(s, .75, 6.15, 11.8, .5, "Dự đoán tổ hợp: lành tính  →  Đúng với nhãn thật của quan sát này.", 22, MINT, True)
note(s, "Phân biệt với các ví dụ giả định trước: đây là trace thật đã lưu trong results.json. Với quan sát test đầu tiên, nhãn thật là benign, tức lành tính. Mười chỉ số trên là vị trí hàng trong X_train, không phải mã bệnh nhân hay chỉ số gốc của toàn bộ dataset. Cây 1 thực tế lấy 426 chỉ số; slide chỉ hiển thị mười chỉ số đầu để dễ đọc. Cả năm cây đầu đều dự đoán lành tính; tổng cả 51 cây có không phiếu ác tính và 51 phiếu lành tính. Chương trình dự đoán đúng quan sát này. Một quan sát đúng không thay thế đánh giá toàn bộ test.")

# 19 — limitations
s = slide("Kết quả có ích, nhưng phạm vi kết luận còn hẹp", "07 • Nhận xét và hướng phát triển", source="Phân tích từ thiết kế thí nghiệm hiện tại")
card(s, .65, 1.95, 3.85, 4.6, "ĐÃ KIỂM CHỨNG", "Mã chạy được.\nBootstrap và hard voting\nđược triển khai rõ ràng.\nCó test độc lập.\nCó số đo và phân tích lỗi.")
card(s, 4.75, 1.95, 3.85, 4.6, "GIỚI HẠN", "Một seed, một test split.\nChọn depth bằng cây đơn.\nChưa đánh giá OOB.\nChưa kiểm định ngoài mẫu\ntrên quần thể độc lập.", ORANGE)
card(s, 8.85, 1.95, 3.8, 4.6, "PHÁT TRIỂN", "Lặp lại nhiều seed.\nBáo cáo độ biến thiên.\nTuning riêng bằng CV.\nSo sánh AdaBoost, GBM.\nĐánh giá đánh đổi lỗi.")
note(s, "Mức cải thiện nhỏ nên cần tránh khẳng định mạnh. Thiết kế chọn độ sâu bằng cây đơn có thể không phải tốt nhất cho Bagging hay Random Forest. Những mở rộng như nhiều seed, cross-validation lặp lại hoặc tuning riêng cần giữ dữ liệu đánh giá độc lập với quá trình chọn cấu hình. Nếu nghiên cứu độ nhạy theo số cây thì chọn dãy số cây bằng train/CV, không nhìn test rồi chọn số cây tốt nhất. Boosting và Stacking mới được giải thích lý thuyết trong bài này, chưa phải các mô hình đã được đo trong bảng kết quả. Muốn đi tới ứng dụng y tế cần dữ liệu và quy trình xác thực phù hợp hơn nhiều.")

# 20 — demo
s = slide("Demo: chạy một lệnh, xem ba loại đầu ra", "07 • Trình diễn mã", source="Mã nguồn: de_5_ensemble_learning.py • Phiên bản thư viện: requirements.txt")
rect(s, .65, 1.95, 12, 1.3, NAVY, radius=True)
text(s, .95, 2.22, 11.4, .8, "cd /workspace/hocmaygk\npython3 de_5_ensemble_learning.py", 20, MINT, font=MONO)
for i, (title_, body) in enumerate([
    ("metrics.csv", "Bảng accuracy, precision,\nrecall, F1 của ba mô hình."),
    ("results.json", "Cấu hình, điểm CV,\ntrace bootstrap và voting."),
    ("Ma trận nhầm lẫn", "confusion_matrices.png\nĐọc nhãn và thứ tự trục."),
]):
    card(s, .65+i*4.08, 3.8, 3.83, 2.55, title_, body)
text(s, .7, 6.55, 11.8, .3, "Cài dependencies theo README trước khi chạy. Không cần tải dữ liệu hoặc khóa API.", 13, GRAY)
note(s, "Nếu demo trực tiếp, mở terminal tại kho và chạy bằng Python của môi trường đã cài requirements.txt. Trong workspace hiện tại, các thư viện đã có sẵn và mã đã chạy thành công. Với môi trường mới làm theo README để tạo venv và cài dependencies. Mở results.json để chỉ ra selected_depth bằng 3, train_size bằng 426 và test_size bằng 143; sau đó chỉ vào all_51_votes. Cuối cùng mở metrics.csv hoặc ảnh ma trận lỗi. Đầu ra được tạo lại vào thư mục outputs. Nếu thời gian thuyết trình ngắn, dùng các số liệu và trace đã nhúng trong slide thay cho chờ chạy trực tiếp.")

# 21 — closing
s = slide("Ba điều cần nhớ", "08 • Kết luận", True, "Kết luận trong phạm vi thí nghiệm hiện tại")
for yy, num, title_, body in [
    (1.95,"1","Đa dạng trước, tổng hợp sau","Nhiều mô hình giống nhau không tự tạo ra một tổ hợp tốt."),
    (3.45,"2","Bagging = Bootstrap + Aggregating","Mẫu có hoàn lại tạo các cây khác nhau; voting kết hợp dự đoán."),
    (4.95,"3","Đọc lỗi cụ thể, giữ kết luận có giới hạn","Bagging đạt 95,10% accuracy và bỏ sót 4/53 ca ác tính trên test này."),
]:
    circle(s, .75, yy, .75, TEAL, num, 22)
    text(s, 1.8, yy-.02, 10.7, .6, title_, 26, WHITE, True)
    text(s, 1.8, yy+.7, 10.7, .55, body, 18, "C9D8DF")
note(s, "Kết lại ba ý. Một: hiệu quả ensemble đến từ cả chất lượng mô hình cơ sở lẫn sự đa dạng, không đơn giản là càng nhiều mô hình càng tốt. Hai: Bagging gồm lấy mẫu có hoàn lại, học độc lập và tổng hợp; trong bài nhóm làm rõ hai phần bootstrap và hard voting bằng mã. Ba: kết quả tốt hơn nhẹ trên test hiện tại nhưng vẫn có ca ác tính bị bỏ sót và chưa có bằng chứng tổng quát hóa rộng. Chuyển sang trang tài liệu tham khảo hoặc phần câu hỏi. Nếu nhóm ba thành viên, có thể chia các trang 1–9 cho người thứ nhất, 10–15 cho người thứ hai, 16–22 cho người thứ ba; đây chỉ là gợi ý, không phải phân công đã xác nhận.")

# 22 — sources
s = slide("Tài liệu tham khảo", "08 • Nguồn và khả năng tái lập")
refs = [
    ("[1] Breiman (1996). Bagging Predictors. Machine Learning 24, 123–140.", "https://doi.org/10.1007/BF00058655"),
    ("[2] Breiman (2001). Random Forests. Machine Learning 45, 5–32.", "https://doi.org/10.1023/A:1010933404324"),
    ("[3] scikit-learn — Ensemble methods (Voting, Bagging, RF, Boosting, Stacking).", "https://scikit-learn.org/stable/modules/ensemble.html"),
    ("[4] scikit-learn — Breast Cancer Wisconsin Diagnostic dataset.", "https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html"),
    ("[5] scikit-learn — Decision Trees (Gini impurity, splitting criteria).", "https://scikit-learn.org/stable/modules/tree.html"),
    ("[6] Freund & Schapire (1997). A Decision-Theoretic Generalization…", "https://doi.org/10.1006/jcss.1997.1504"),
    ("[7] Wolpert (1992). Stacked Generalization. Neural Networks 5(2), 241–259.", "https://doi.org/10.1016/S0893-6080(05)80023-1"),
]
for i, (label, url) in enumerate(refs):
    yy = 1.85+i*.66
    text(s, .7, yy, 11.9, .33, label, 15, INK, True)
    obj = text(s, .7, yy+.31, 11.9, .27, url, 10, TEAL)
    obj.text_frame.paragraphs[0].runs[0].hyperlink.address = url
text(s, .7, 6.65, 11.9, .25, "Số liệu thực nghiệm: outputs/results.json • Seed 42 • NumPy 2.3.5 / scikit-learn 1.8.0", 11, GRAY)
note(s, "Các nguồn 1 và 2 là các bài báo gốc về Bagging và Random Forest. Nguồn 6 cho AdaBoost và nguồn 7 cho Stacking. Tài liệu scikit-learn giải thích các lớp thư viện và đặc tính dataset. Số liệu thực nghiệm trong bài được lấy từ outputs/results.json của kho, không lấy từ các bài báo hoặc benchmark bên ngoài. Mã và requirements.txt đi kèm để tái lập; sử dụng cùng seed và phiên bản giúp giảm khác biệt do môi trường. Các URL có thể bấm trong PowerPoint. PDF đề bài yêu cầu đủ nguyên lý, quy trình, ứng dụng và mã nguồn; phần trình bày đã lần lượt bao phủ các nội dung này.")

# 23 — Q&A appendix
s = slide("Câu hỏi thường gặp khi bảo vệ", "Phụ lục A • Dùng khi hỏi đáp", source="Gợi ý trả lời dựa trên mã và thiết kế hiện tại")
questions = [
    ("Vì sao 51 cây?", "Minh họa tổ hợp đủ lớn, tránh hòa ở hai lớp; chưa tối ưu số cây."),
    ("Vì sao không chuẩn hóa?", "Các cây dùng phép chia theo ngưỡng, không dựa vào khoảng cách Euclid."),
    ("Test có bị dùng để tuning?", "Không. Độ sâu chọn bằng CV trên train; test chỉ đánh giá cuối."),
    ("Bagging có luôn tốt hơn?", "Không. Lỗi tương quan cao và mô hình cơ sở yếu có thể làm lợi ích thấp."),
    ("Vì sao nhấn mạnh recall?", "Recall ác tính phản ánh tỷ lệ phát hiện và số ca ác tính bị bỏ sót."),
]
for i, (q, a) in enumerate(questions):
    yy=1.95+i*.9
    rect(s, .65, yy, 12, .77, WHITE, radius=True)
    text(s, .85, yy+.15, 3.6, .48, q, 18, TEAL, True)
    text(s, 4.6, yy+.14, 7.8, .55, a, 16, INK)
note(s, "Đây là phụ lục cho hỏi đáp, không bắt buộc trình bày hết. Nếu được hỏi số cây có tối ưu không, trả lời trung thực là chưa; 51 là cấu hình minh họa cố định, không chọn dựa trên test. Nếu được hỏi bootstrap có mất dữ liệu không, mỗi cây có thể không thấy một phần dữ liệu nhưng các cây sử dụng các mẫu khác nhau; không đảm bảo mọi mẫu đều được thấy ở mọi cây. Nếu được hỏi vì sao Random Forest bằng Bagging, các số liệu tổng hợp trùng nhau trong lần chạy không chứng minh hai mô hình tương đương. Nếu được hỏi có thể chẩn đoán không, trả lời chưa có kiểm định lâm sàng và thí nghiệm vẫn bỏ sót ca ác tính.")

# 24 — metrics appendix
s = slide("Cách tính chỉ số với ác tính là lớp dương", "Phụ lục B • Kiểm tra phép tính", source="Số đếm của Bagging: TP = 49, FN = 4, FP = 3, TN = 87")
table(s, .65, 1.95, [3.0, 4.0, 5.0], .85, [
    ["Chỉ số", "Công thức", "Thay số Bagging"],
    ["Accuracy", "(TP + TN) / N", "(49 + 87) / 143 = 95,10%"],
    ["Precision ác tính", "TP / (TP + FP)", "49 / (49 + 3) = 94,23%"],
    ["Recall ác tính", "TP / (TP + FN)", "49 / (49 + 4) = 92,45%"],
    ["F1 ác tính", "2TP / (2TP + FP + FN)", "98 / (98 + 3 + 4) = 93,33%"],
], font_size=17)
text(s, .75, 6.5, 11.8, .35, "Balanced accuracy dùng trong CV = (Recall ác tính + Recall lành tính) / 2.", 17, TEAL, True)
note(s, "Dùng trang này khi cần giải thích cụ thể các con số. Quy ước dương là ác tính dù mã nhãn bằng 0. TP là ca ác được dự đoán ác; FN là ca ác bị dự đoán lành; FP là ca lành bị dự đoán ác; TN là ca lành được dự đoán lành. Tổng mẫu bằng 49 cộng 4 cộng 3 cộng 87 bằng 143. F1 là trung bình điều hòa của precision và recall, tương đương công thức hai TP chia hai TP cộng FP cộng FN. Balanced accuracy trung bình recall của hai lớp được dùng để chọn độ sâu trong CV, khác accuracy thường ở bảng test. Nếu mẫu test thiếu một lớp thì cần xem lại cách diễn giải; ở đây cả hai lớp đều có mặt.")

prs.save(OUT)
md = ["# Lời thuyết trình — Đề 5: Ensemble Learning", "", "24 slide: 22 trang chính và 2 trang phụ lục. Gợi ý khoảng 15–20 phút cho phần chính.", "", "Trước khi trình bày: bổ sung tên thành viên và lớp tại slide 1.", ""]
for idx, title_, content in notes:
    md.extend([f"## Slide {idx:02d} — {title_}", "", content, ""])
(ROOT / "presentation/loi_thuyet_trinh.md").write_text("\n".join(md), encoding="utf-8")
print(f"Saved {OUT} ({len(prs.slides)} slides)")
