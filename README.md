# Expense Tracker Local

A privacy-first, dependency-free Python CLI for recording, searching, summarizing, and exporting personal expenses in a local SQLite database.

## English

### Why it exists
Small expense logs should not require an account, cloud service, or spreadsheet gymnastics. Expense Tracker Local keeps the database on your machine and provides predictable CLI commands suitable for people and scripts.

### Features
- Record date, amount, ISO-style 3-letter currency, category, merchant, and notes.
- Exact two-decimal money handling; no binary floating-point arithmetic.
- Search by merchant/category/note and filter by currency, category, or date range.
- Summaries grouped by **currency and category**, deliberately never adding unlike currencies together.
- JSON output plus atomic CSV/JSON exports with overwrite protection.
- SQLite indexes and WAL mode for a durable local store.
- Explicit confirmation for destructive deletion.
- No network calls, telemetry, accounts, API keys, or runtime dependencies.

### Requirements & installation
Python 3.10+.

```bash
git clone https://github.com/rad03i2/expense-tracker-local.git
cd expense-tracker-local
python -m pip install -e .
```

For development/tests:
```bash
python -m pip install pytest
pytest
```

### Usage
```bash
expense-tracker add 12.50 --currency USD --category Food --merchant "Coffee shop" --note "Lunch"
expense-tracker add 5000 --currency IQD --category Transport --date 2026-09-21
expense-tracker list
expense-tracker list --currency USD --start 2026-09-01 --end 2026-09-30
expense-tracker list --query coffee --json
expense-tracker summary
expense-tracker export expenses.csv --format csv
expense-tracker export backup.json --format json
expense-tracker show 1
expense-tracker delete 1 --yes
```

### Configuration
The default database is `~/.expense-tracker-local/expenses.sqlite3`. Override it with `EXPENSE_TRACKER_DB` or per command with `--db PATH`.

### Project structure
```text
src/expense_tracker/core.py   validation, SQLite storage, reports, exports
src/expense_tracker/cli.py    command-line interface
src/expense_tracker/__init__.py
tests/test_core.py            functional unit tests
.github/workflows/ci.yml      cross-platform CI
```

### Preview guidance
A useful repository screenshot can show `expense-tracker list` beside `expense-tracker summary`; no screenshot is committed because generated terminal captures are environment-specific.

### Testing
`pytest` exercises amount validation/rounding, CRUD, filters, currency-safe summaries, exports, overwrite protection, and invalid date ranges. CI runs the suite on supported Python versions across major operating systems.

### Security & privacy
All records remain in the selected local SQLite file. The database is **not encrypted**; use normal OS file permissions and full-disk encryption for sensitive financial data. Exported files are also plaintext. Never use this project as a secrets store.

### Limitations
- Amounts are fixed to two decimal places; currencies requiring other minor-unit precision are not modeled.
- No exchange-rate conversion, budgets, recurring transactions, bank import, GUI, cloud sync, or database encryption.
- CSV/JSON are export formats only; import is not implemented.
- This is a personal bookkeeping utility, not accounting/tax software.

### Optional roadmap
Budget targets, safe import with schema validation, recurring entries, and configurable currency precision are reasonable future additions.

### Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Security guidance is in [SECURITY.md](SECURITY.md).

### License
MIT — see [LICENSE](LICENSE).

### Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: [@rad03i2](https://github.com/rad03i2)

---

## العربية

### نظرة عامة
**Expense Tracker Local** أداة سطر أوامر محلية لتسجيل المصروفات والبحث فيها وتلخيصها وتصديرها، مع حفظ البيانات في SQLite على جهازك من دون حساب أو خدمة سحابية.

### لماذا المشروع؟
يوفر طريقة بسيطة وقابلة للأتمتة لمتابعة المصروفات الشخصية من دون إرسال البيانات المالية إلى طرف خارجي أو الاعتماد على جداول يدوية.

### المزايا
- تسجيل التاريخ والمبلغ والعملة والتصنيف والتاجر والملاحظات.
- حساب الأموال بدقة منزلتين عشريتين من دون أخطاء `float` الثنائية.
- البحث والتصفية حسب العملة والتصنيف والفترة والتاجر/الملاحظة.
- تلخيص حسب **العملة والتصنيف** من دون جمع عملات مختلفة معًا.
- مخرجات JSON وتصدير CSV/JSON آمن مع منع الاستبدال غير المقصود.
- SQLite مع فهارس ووضع WAL.
- تأكيد صريح للحذف.
- لا شبكة ولا تتبع ولا مفاتيح API ولا تبعيات تشغيل خارجية.

### المتطلبات والتثبيت
Python 3.10 أو أحدث:
```bash
git clone https://github.com/rad03i2/expense-tracker-local.git
cd expense-tracker-local
python -m pip install -e .
```
وللاختبارات:
```bash
python -m pip install pytest
pytest
```

### الاستخدام
```bash
expense-tracker add 12500 --currency IQD --category Food --merchant "مطعم"
expense-tracker list --currency IQD
expense-tracker summary
expense-tracker export expenses.csv --format csv
expense-tracker show 1
expense-tracker delete 1 --yes
```

### الإعداد
قاعدة البيانات الافتراضية: `~/.expense-tracker-local/expenses.sqlite3`. يمكن تغييرها بمتغير البيئة `EXPENSE_TRACKER_DB` أو الخيار `--db PATH`.

### بنية المشروع
المحرك والتحقق والتخزين والتقارير في `src/expense_tracker/core.py`، والواجهة الطرفية في `cli.py`، والاختبارات في `tests/`، والتكامل المستمر في `.github/workflows/ci.yml`.

### الاختبارات
تغطي الاختبارات التحقق من المبالغ والتقريب وعمليات الإضافة/القراءة/الحذف والتصفية والتلخيص متعدد العملات والتصدير ومنع الكتابة فوق الملفات والتحقق من نطاق التاريخ.

### الخصوصية والأمان
البيانات محلية ولا تغادر الجهاز بواسطة البرنامج، لكن SQLite وملفات التصدير **غير مشفرة**. استخدم صلاحيات النظام وتشفير القرص عند التعامل مع بيانات حساسة، ولا تستخدم الأداة لحفظ الأسرار.

### القيود
لا يوجد تحويل عملات أو ميزانيات أو مصروفات متكررة أو استيراد بنكي أو واجهة رسومية أو مزامنة سحابية أو تشفير قاعدة البيانات. المبالغ تدعم منزلتين عشريتين فقط، والأداة ليست نظام محاسبة أو ضرائب.

### التطوير الاختياري
يمكن مستقبلًا إضافة الميزانيات والاستيراد الآمن والمصروفات المتكررة ودقة العملات القابلة للضبط.

### المساهمة والترخيص
راجع [CONTRIBUTING.md](CONTRIBUTING.md) و[SECURITY.md](SECURITY.md). المشروع مرخص برخصة MIT في [LICENSE](LICENSE).

### المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: [@rad03i2](https://github.com/rad03i2)
