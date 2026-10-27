"""Validate, regenerate and package the topic-5 submission. Run with the venv Python."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
FINAL_REPORT = ROOT / "report/Bao_cao_Ensemble_Learning_da_hoan_thien.docx"
FINAL_REPORT_PDF = FINAL_REPORT.with_suffix(".pdf")
LEGACY_REPORT_STEM = "Bao_cao_De_5_Ensemble_Learning"


def final_report_ready():
    present = [path.is_file() for path in (FINAL_REPORT, FINAL_REPORT_PDF)]
    if any(present) and not all(present):
        raise RuntimeError("Báo cáo hoàn thiện cần đủ cả Word và PDF; không thay bằng bản nháp.")
    return all(present)


def run(*args):
    print("\n>", " ".join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), cwd=ROOT, check=True)


def convert_pdf(source, destination):
    """Convert into a fresh directory so an old PDF cannot masquerade as a new one."""
    office = shutil.which("soffice")
    if not office:
        raise RuntimeError("Cần LibreOffice (soffice) để xuất PDF từ Word và PowerPoint.")
    with tempfile.TemporaryDirectory(prefix="hocmaygk-office-") as temporary:
        folder = Path(temporary)
        profile = (folder / "profile").as_uri()
        subprocess.run(
            [office, f"-env:UserInstallation={profile}", "--headless", "--convert-to", "pdf",
             "--outdir", str(folder), str(source)],
            cwd=ROOT, check=True, timeout=120,
        )
        converted = folder / source.with_suffix(".pdf").name
        if not converted.is_file() or not converted.read_bytes().startswith(b"%PDF-"):
            raise RuntimeError(f"Không xuất được PDF mới cho {source.name}")
        shutil.copyfile(converted, destination)


def submission_name():
    info = json.loads((ROOT / "report/group_info.json").read_text(encoding="utf-8"))
    members = info.get("members", [])
    if not 1 <= len(members) <= 3:
        raise ValueError("Cần thông tin thật của 1–3 thành viên trong report/group_info.json.")
    ids = [str(member.get("student_id", "")) for member in members]
    if any(not member.get("name", "").strip() for member in members):
        raise ValueError("Thiếu tên thành viên.")
    if any(not student_id.isascii() or not student_id.isdigit() for student_id in ids):
        raise ValueError("MSSV phải là chuỗi chữ số.")
    if len(set(ids)) != len(ids):
        raise ValueError("MSSV thành viên bị trùng.")
    if sum(int(student_id[-1]) for student_id in ids) % 8 != 5:
        raise ValueError("Phần dư MSSV không tương ứng chủ đề 5; cần kiểm tra lại thông tin nhóm.")
    return "_".join(ids)


def package(name):
    use_final_report = final_report_ready()
    files = [ROOT / name for name in (
        "README.md", "HUONG_DAN_NOP_BAI.md", "requirements.txt",
        "ensemble_model.py", "de_5_ensemble_learning.py",
        "De_5_Ensemble_Learning.pptx", "De_5_Ensemble_Learning.pdf",
    )]
    allowed = {".py", ".md", ".txt", ".json", ".docx", ".pdf", ".png", ".csv"}
    for directory in ("examples", "experiments", "tests", "tools", "presentation", "report"):
        files.extend(path for path in (ROOT / directory).rglob("*")
                     if path.is_file() and path.suffix in allowed
                     and "__pycache__" not in path.parts and "rendered" not in path.parts
                     and not (use_final_report and path.stem == LEGACY_REPORT_STEM))
    # Include the actual experimental evidence even though outputs/ is Git-ignored.
    files.extend(path for path in (ROOT / "outputs").iterdir() if path.is_file())
    files.extend(path for path in (ROOT / "outputs/toy").iterdir() if path.is_file())
    extension_output = ROOT / "outputs/extensions"
    if extension_output.is_dir():
        files.extend(path for path in extension_output.iterdir() if path.is_file())
    required = ([FINAL_REPORT, FINAL_REPORT_PDF] if use_final_report else [
        ROOT / f"report/{LEGACY_REPORT_STEM}.docx",
        ROOT / f"report/{LEGACY_REPORT_STEM}.pdf",
    ]) + [ROOT / "outputs/results.json", ROOT / "outputs/toy/toy_example.json"]
    if any(not path.is_file() for path in files + required):
        raise RuntimeError("Bộ nộp còn thiếu tệp bắt buộc.")
    files = sorted(set(files))
    manifest = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in files}
    output = ROOT / "submission" / f"{name}.zip"
    output.parent.mkdir(exist_ok=True)
    # Only publish a complete archive; failed generation leaves any prior archive intact.
    temporary = output.with_suffix(".zip.tmp")
    with ZipFile(temporary, "w", compression=ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, f"{name}/{path.relative_to(ROOT).as_posix()}")
        archive.writestr(f"{name}/MANIFEST.json", json.dumps(
            {"algorithm": "SHA-256", "files": manifest}, ensure_ascii=False, indent=2))
    with ZipFile(temporary) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Kiểm tra tính toàn vẹn file nén thất bại.")
    temporary.replace(output)
    print(f"\nĐã kiểm tra và đóng gói {len(files)} tệp: {output}", flush=True)


def main():
    os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "hocmaygk-matplotlib"))
    os.environ.setdefault("XDG_CACHE_HOME", str(Path(tempfile.gettempdir()) / "hocmaygk-cache"))
    name = submission_name()
    if not shutil.which("soffice"):
        raise RuntimeError("Cài LibreOffice trước khi dựng lại toàn bộ bộ nộp.")
    if not shutil.which("pdftotext"):
        raise RuntimeError("Cài Poppler (pdftotext) để kiểm tra số trang và tạo mục lục chính xác.")
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v")
    run(sys.executable, "de_5_ensemble_learning.py")
    run(sys.executable, "examples/toy_bagging.py", "--output-dir", "outputs/toy")
    run(sys.executable, "experiments/report_extensions.py")
    run(sys.executable, "experiments/controlled_comparison.py")
    run(sys.executable, "presentation/create_presentation.py")
    if final_report_ready():
        print("Giữ nguyên báo cáo Word/PDF đã hoàn thiện theo form của nhóm.", flush=True)
    else:
        run(sys.executable, "report/create_report.py")
        convert_pdf(ROOT / f"report/{LEGACY_REPORT_STEM}.docx",
                    ROOT / f"report/{LEGACY_REPORT_STEM}.pdf")
        run(sys.executable, "report/create_report.py", "--toc-pdf",
            f"report/{LEGACY_REPORT_STEM}.pdf")
        convert_pdf(ROOT / f"report/{LEGACY_REPORT_STEM}.docx",
                    ROOT / f"report/{LEGACY_REPORT_STEM}.pdf")
    convert_pdf(ROOT / "De_5_Ensemble_Learning.pptx", ROOT / "De_5_Ensemble_Learning.pdf")
    package(name)


if __name__ == "__main__":
    main()
