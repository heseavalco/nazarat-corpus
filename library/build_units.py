# -*- coding: utf-8 -*-
"""ساخت واحدهای ایراد (objection units) از نامه‌های شورای نگهبان + برچسب‌های اولیه."""
import json, os, re, collections
items = {str(i['id']): i for i in (json.loads(l) for l in open('text/items.jsonl', encoding='utf-8'))}
recs = [json.loads(l) for l in open('library/gc_letters_all.jsonl', encoding='utf-8')]
# نظارت شرعی rows (path 7) typed "نظارت شرعی"
for iid, it in items.items():
    if it['_path'] != '7': continue
    d = json.load(open(f'text/details/{iid}.json', encoding='utf-8'))
    for r in d['result']:
        if (r['type'] or '').strip() == 'نظارت شرعی':
            fn = f"text/letters/{r['id']}.json"
            if os.path.exists(fn):
                L = json.load(open(fn, encoding='utf-8'))
                recs.append({'itemId': iid, 'category': it['_pathName'], 'path': '7', 'title': it['title'], 'item_date': it['date'],
                             'lastadj': it['lastadj'], 'letterId': r['id'], 'order': r['order'], 'type': 'نظارت شرعی', 'date': r['displayDate'],
                             'law': r['law'] or '', 'text': L['text']})
NEG = re.compile(r'(شناخته\s*نشد|مغایر\s*(?:با\s*)?(?:موازین\s*)?شرع\s*(?:و\s*قانون\s*اساسی\s*)?(?:شناخته\s*)?نشد|نمی‌باشد|نیست)')
POS = re.compile(r'(خلاف|مغایر)\s*(?:با\s*)?(?:موازین\s*)?(?:شرع|شرعی)')
def sharia_letter(r):
    t = r['type']
    if 'شرع' in t: return True
    if r['path'] in ('3', '4', '7'): return True
    if t.endswith('همه موارد') or t.endswith('سایر') or t.endswith('ابهام'):
        for m in POS.finditer(r['text']):
            tail = r['text'][m.end():m.end()+25]
            if not NEG.match(tail.strip()): return True
    return False
sel = [r for r in recs if sharia_letter(r)]
print('letters selected', len(sel), 'of', len(recs))
HDR = re.compile(r'^\s*(شماره|تاریخ|پیوست|باسمه|بسم\s*الله|بسمه|رئیس محترم|ریاست محترم|حضرت|جناب|دبیر محترم|عطف به|پیرو|با سلام)')
UNIT = re.compile(r'^\s*(?:\(?\d{1,3}\s*[-ـ–—.)]|[-–ـ—•]\s|\(?[الف-ی]\s*[-ـ–—)]\s)')
NOTE = re.compile(r'^\s*(تذکر|تذکرات|یادآوری)\b')
SIGN = re.compile(r'(دبیر شورای نگهبان|قائم\s*مقام دبیر|قائم‌مقام دبیر|شورای نگهبان\s*$)')
REF_MADE = re.compile(r'(?:ماده|مادّه|مواد)\s*\(?\s*(\d+)')
REF_TABS = re.compile(r'تبصره\s*\(?\s*(\d+)')
REF_BAND = re.compile(r'بند\s*\(?\s*«?([\dالف-ی]{1,3})»?\s*\)?')
REF_ASL = re.compile(r'اصل\s*\(?\s*(\d+)')
TOPICS = {
 '۴.۱ ربا و بانک': r'ربا|بهره|سود\s*(?:بانکی|تسهیلات|سپرده)|خسارت تأخیر|خسارت تاخیر|جریمه دیرکرد|وجه التزام|تسهیلات|بانک|ارز|تورم|کاهش ارزش پول|قرض',
 '۴.۲ بیع و معاملات': r'بیع|معامل|قرارداد|شرط|غرر|انحصار|قیمت|فروش|خرید|مزایده|مناقصه|واگذاری|عقد|احتکار|تنظیم بازار|بورس|سهام|اوراق',
 '۴.۳ اجاره و سرقفلی': r'اجاره|سرقفلی|موجر|مستأجر|مستاجر|حق کسب',
 '۴.۴ ضمان، بیمه، تأمین اجتماعی': r'ضمان|خسارت|مسئولیت|بیمه|تأمین اجتماعی|تامین اجتماعی|بازنشست|مستمری|دیه|عدم\s*النفع|تفویت',
 '۴.۵ اموال عمومی، اراضی، عوارض، مالیات، وقف': r'اراضی|زمین|املاک|عوارض|شهرداری|مالیات|وقف|موقوف|معدن|معادن|انفال|مصادره|تملک|تصرف|اموال عمومی|بیت\s*المال|مالکیت|جنگل|مرتع|آب|حریم|ملی',
 '۴.۶ خانواده و ارث': r'ارث|زوج|مهریه|طلاق|حضانت|نکاح|ازدواج|نفقه|همسر|فرزند|ولایت\s*(?:پدر|قهری)|وصیت|محجور|سرپرست',
 '۴.۷ قضا و دادرسی': r'قاضی|قضات|دادگاه|دادرسی|وکالت|وکیل|اعسار|شهادت|شاهد|سوگند|اقرار|داوری|حکم|رأی|رای|مرور زمان|دیوان|اجرای احکام|هیئت منصفه',
 '۴.۸ کیفری': r'مجازات|جرم|حد\b|حدود|قصاص|تعزیر|زندان|حبس|شلاق|جزای نقدی|کیفر|جرائم|جریمه',
 '۴.۹ حکومت، انتخابات، اقلیت‌ها': r'انتخابات|شورا(?:ی|های)\s*(?:اسلامی|شهر)|مجلس|دولت|اقلیت|تابعیت|رهبری|ولی فقیه|حاکم|حکومت|اصل\s*\d+|قانون اساسی|مجمع تشخیص|قوه|وزیر|صلاحیت',
 '۴.۱۰ کار و استخدام': r'استخدام|کارمند|کارگر|کارکنان|اشتغال|حقوق و مزایا|مزد|بازخرید|اخراج|مرخصی|پرسنل',
 '۴.۱۱ تحصیل، پزشکی، مستحدثه، مالکیت فکری': r'تحصیل|دانشجو|دانشگاه|پزشک|درمان|دارو|مالکیت (?:فکری|معنوی|صنعتی)|فضای مجازی|رایانه|اینترنت|رسانه|سقط|پیوند',
 '۴.۱۲ عبادات، شعائر، تعطیلات': r'تعطیل|نماز|روزه|حج|زکات|خمس|شعائر|عزاداری|مسجد|حجاب|عفاف|حق\s*التحریر|جمعه',
}
TOPIC_RE = {k: re.compile(v) for k, v in TOPICS.items()}
def split_units(text):
    lines = [l.rstrip() for l in text.split('\n')]
    body = []
    started = False
    for l in lines:
        if not l.strip(): continue
        if not started and HDR.match(l): continue
        started = True
        body.append(l)
    # drop signature lines at the end (last 3 lines matching a name/role)
    while body and (SIGN.search(body[-1]) or len(body[-1]) < 30 and not UNIT.match(body[-1]) and not re.search(r'شرع|اصل|ماده', body[-1])):
        body.pop()
    units, cur, section = [], None, 'ایرادات'
    for l in body:
        if NOTE.match(l) and len(l.strip()) < 25:
            if cur: units.append(cur); cur = None
            section = 'تذکرات'; continue
        if UNIT.match(l):
            if cur: units.append(cur)
            cur = {'section': section, 'text': l.strip()}
        else:
            if cur is None:
                cur = {'section': section, 'text': l.strip(), 'intro': True}
            else:
                cur['text'] += '\n' + l.strip()
    if cur: units.append(cur)
    return units
out = []
n_letters = 0
for r in sel:
    units = split_units(r['text'])
    if not units: continue
    n_letters += 1
    # intro unit (before first numbered) — keep if it carries a ruling itself (single-ruling letters)
    for k, u in enumerate(units):
        t = u['text']
        if u.get('intro') and len(units) > 1 and not POS.search(t):
            continue  # pure intro line, skip
        sh = bool(POS.search(t) or re.search(r'موازین شرع|فقه|شرعاً|شرعی', t))
        neg = bool(NEG.search(t)) and not re.search(r'(خلاف|مغایر)\s*(?:با\s*)?(?:موازین\s*)?شرع\s*(?:شناخته شد|است|می‌باشد|دانسته شد|تشخیص)', t)
        topics = [k2 for k2, rx in TOPIC_RE.items() if rx.search(t + ' ' + r['title'])]
        out.append({'unitId': f"{r['letterId']}#{k+1}", 'letterId': r['letterId'], 'itemId': r['itemId'], 'category': r['category'],
                    'title': r['title'], 'letter_type': r['type'], 'date': r['date'], 'law': r['law'], 'lastadj': r['lastadj'],
                    'section': u['section'], 'sharia': sh, 'negative': neg, 'ambiguity': bool(re.search(r'ابهام|مبهم', t)),
                    'constitution': bool(REF_ASL.search(t)) or 'قانون اساسی' in t,
                    'refs': {'ماده': REF_MADE.findall(t)[:6], 'تبصره': REF_TABS.findall(t)[:6], 'بند': REF_BAND.findall(t)[:6], 'اصل': REF_ASL.findall(t)[:6]},
                    'topics': topics, 'text': t})
with open('library/units_all.jsonl', 'w', encoding='utf-8') as f:
    for u in out: f.write(json.dumps(u, ensure_ascii=False) + '\n')
sh_units = [u for u in out if u['sharia'] and u['section'] == 'ایرادات']
with open('library/units_sharia.jsonl', 'w', encoding='utf-8') as f:
    for u in sh_units: f.write(json.dumps(u, ensure_ascii=False) + '\n')
print('letters with units', n_letters, '| units', len(out), '| sharia units', len(sh_units), '| chars', sum(len(u['text']) for u in sh_units))
print('sharia units by category:', dict(collections.Counter(u['category'] for u in sh_units)))
tc = collections.Counter(t for u in sh_units for t in u['topics']); print('topic hits:', tc.most_common())
print('untagged sharia units:', sum(1 for u in sh_units if not u['topics']))
