#!/usr/bin/env python3
"""Ergaenzt den trustedDialog Preview Builder um ein optionales 4. Mockup: "Geoeffnete E-Mail".

Aufruf (im Ordner der aktuellen app.py):
    python add_open_mail_mockup.py            # app.py aendern (Backup: app.before_open_mail.py)
    python add_open_mail_mockup.py --check    # nur pruefen, nichts schreiben
    python add_open_mail_mockup.py --restore  # Backup zurueckspielen

Sicherheitsnetz:
  * Alle Aenderungsstellen werden VOR dem ersten Schreiben geprueft. Fehlt eine, bricht das Skript ab, ohne app.py zu veraendern.
  * Danach wird die Syntax geprueft; bei einem Fehler wird automatisch das Backup zurueckgespielt.
  * Mehrfaches Ausfuehren ist harmlos (erkennt den Marker "OPEN_MAIL_MOCKUP").
  * Die drei bestehenden Mockups werden nicht veraendert. Ohne Haken "Geoeffnete E-Mail" ist die Ausgabe identisch.
"""
import argparse
import py_compile
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT / 'app.py'
BACKUP = ROOT / 'app.before_open_mail.py'
MARKER = 'OPEN_MAIL_MOCKUP'

# ---------------------------------------------------------------------------------------------------------------------
# 1) CSS (wird an PHONE_CSS angehaengt; PHONE_CSS ist ein normaler String, daher einfache geschweifte Klammern)
# ---------------------------------------------------------------------------------------------------------------------
CSS_BLOCK = r"""
/* OPEN_MAIL_MOCKUP: 4. Geraet "Geöffnete E-Mail" */
.om-band{left:0;top:89px;width:297.5px;height:44px;background:#F3F3F3}
.om-pill{position:absolute;left:11px;top:17px;height:20px;padding:0 9px;border:1px solid #ebebeb;border-radius:10px;background:#fff;color:#1667C7;font:500 9.6px/18px Roboto,Arial,sans-serif;white-space:nowrap;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.om-unsub{position:absolute;right:14px;top:17px;height:20px;display:flex;align-items:center;gap:6px;color:#1667C7;font:500 11.3px/20px Roboto,Arial,sans-serif;white-space:nowrap}
.om-unsub svg{display:block;flex:0 0 auto}
.om-msg{position:absolute;left:0;top:143px;width:297.5px;height:200px}
.om-nl{position:absolute;left:59.5px;top:8px;height:16px;max-width:186px;display:flex;align-items:center;white-space:nowrap}
.om-sender{font:700 14px/16px Roboto,Arial,sans-serif;color:#2F6FBF;min-width:0;flex:0 1 auto;overflow:hidden;white-space:nowrap}
.om-date{position:absolute;left:59.5px;top:28px;font:400 10.4px/12px Roboto,Arial,sans-serif;color:#8e8e93;white-space:nowrap}
.om-thread{position:absolute;right:12px;top:10px;display:flex;align-items:center;gap:6px;font:400 11px/12px Roboto,Arial,sans-serif;color:#9a9a9a}
.om-line{position:absolute;left:59.5px;right:36px;top:49px;height:1px;background:#ececec}
.om-star{position:absolute;right:14px;top:53px;display:block}
.om-subject{position:absolute;left:16.5px;right:16px;top:74px;max-height:54px;overflow:hidden;font:700 14.5px/18px Roboto,Arial,sans-serif;color:#2a2a2a;word-break:break-word}
.om-content{left:16.5px;right:16px;top:290px;height:300px;overflow:hidden}
.om-bar{left:18px;top:599px;width:200px;height:44px;border-radius:22px;background:#fff;box-shadow:0 1px 8px rgba(0,0,0,.10);display:flex;align-items:center;justify-content:space-around;padding:0 4px}
.om-bar svg{display:block}
.om-compose{left:232px;top:599px;width:44px;height:44px;border-radius:50%;background:#fff;box-shadow:0 1px 8px rgba(0,0,0,.10);display:flex;align-items:center;justify-content:center}
"""

# ---------------------------------------------------------------------------------------------------------------------
# 2) Template + Funktion (wird direkt hinter PHONE_CLOSE eingefuegt; OTHER_ROWS/TD_ROW werden erst beim Aufruf gelesen)
# ---------------------------------------------------------------------------------------------------------------------
OPEN_MAIL_DEFS = r"""
# OPEN_MAIL_MOCKUP ------------------------------------------------------------------------------------------------------
# 4. Mockup: geöffnete E-Mail. Status-Leiste, Gerätehülle und Home-Indikator stammen aus den bestehenden Bausteinen.
OPEN_MAIL_CONTENT = ''   # <- HIER kommt im nächsten Schritt der interaktive E-Mail-Inhalt (HTML) hinein
OPEN_MAIL_STATUS = PHONE_HEAD.split('<span class="abs round" style="left:3px">', 1)[0]   # nur die Status-Leiste (Uhrzeit, Insel, Akku)
OPEN_MAIL_TEMPLATE = r'''<span class="abs round" style="left:3px"><svg class="hicon" width="16" height="16" viewBox="0 0 16 16"><path d="M11 1.6 4.6 8l6.4 6.4"/></svg></span>
<span class="t title">__COUNT__</span><span class="t mail">trusteddialog99@gmx.net</span>
<span class="abs round" style="left:210.5px"><svg class="hicon" width="16" height="16" viewBox="0 0 16 16"><path d="M3.4 10.2 8 5.6l4.6 4.6"/></svg></span>
<span class="abs round" style="left:255px"><svg class="hicon" width="16" height="16" viewBox="0 0 16 16"><path d="M3.4 5.8 8 10.4l4.6-4.6"/></svg></span>
<div class="abs om-band"><span class="om-pill">Newsletter</span><span class="om-unsub">Newsletter abbestellen<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1667C7" stroke-width="2.6"><path d="M4.4 9.2V4.6h9.4"/><path d="M18.6 9.6v12H14.8"/><circle cx="7.2" cy="15.4" r="5"/><path d="M5 15.4h4.4"/><path d="M19.4.4l1.1 2.7 2.7 1.1-2.7 1.1-1.1 2.7-1.1-2.7-2.7-1.1 2.7-1.1z" fill="#1667C7" stroke="none"/></svg></span></div>
<div class="abs om-msg">__AV__<div class="om-nl"><span class="om-sender fit">__SENDER__</span>__SEAL__</div><div class="om-date">Heute um <span data-off="__OFFSET__"></span></div><span class="om-thread">1<svg width="7" height="11" viewBox="0 0 7 11"><path d="M1.2 1.2 5.6 5.5 1.2 9.8" fill="none" stroke="#aaa" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></span><span class="om-line"></span><svg class="om-star" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#c9c9c9" stroke-width="2" stroke-linejoin="round"><path d="M12 2.8l2.8 5.9 6.4.8-4.7 4.4 1.2 6.4L12 17.2 6.3 20.3l1.2-6.4L2.8 9.5l6.4-.8z"/></svg><div class="om-subject">__SUBJECT__</div></div>
<div class="abs om-content">__CONTENT__</div>
<div class="abs om-bar"><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="#111" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2.2 9h8.4M7.6 5.9 10.7 9l-3.1 3.1"/><path d="M8.6 3.6h6a1.2 1.2 0 0 1 1.2 1.2v8.4a1.2 1.2 0 0 1-1.2 1.2h-6"/></svg><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="#111" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3.2 4.8h11.6M6.9 4.8V3.2h4.2v1.6M4.6 4.8l.6 9.6h7.6l.6-9.6M7.5 7.4v4.8M10.5 7.4v4.8"/></svg><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="#111" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M7.6 3.8 3 8.4l4.6 4.6"/><path d="M3.3 8.4H10a4.6 4.6 0 0 1 4.6 4.6v.9"/></svg><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="#111" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><g stroke="#5856D6"><circle cx="9" cy="10" r="5.4"/><path d="M9 7.2V10l1.9 1.2M2.7 4.2 5 2.4M15.3 4.2 13 2.4"/></g></svg><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="#111" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="3.5" cy="9" r="1.4" fill="#111" stroke="none"/><circle cx="9" cy="9" r="1.4" fill="#111" stroke="none"/><circle cx="14.5" cy="9" r="1.4" fill="#111" stroke="none"/></svg></div>
<div class="abs om-compose"><svg width="19" height="19" viewBox="0 0 19 19"><path d="M8.5 3.2H4.2A1.7 1.7 0 0 0 2.5 4.9v9.9a1.7 1.7 0 0 0 1.7 1.7h9.9a1.7 1.7 0 0 0 1.7-1.7v-4.3" fill="none" stroke="#111" stroke-width="2" stroke-linecap="round"/><path d="M14.6 1.7a1.6 1.6 0 0 1 2.3 2.3l-7.2 7.2-3.2.9.9-3.2z" fill="#111"/></svg></div>
<div class="abs home"></div>'''
def open_mail_html(avatar, sender, subject, content=''):
    # Zähler = Anzahl der Mails in der Maillist (erste Mail + die weiteren Zeilen aus OTHER_ROWS), aktuell also "1 von 5".
    count = '1 von %d' % (1 + OTHER_ROWS.count('class="row"'))
    # "Heute um ..." nutzt denselben Zeitversatz wie die erste Mail (tD-Zeile), damit beide Uhrzeiten immer übereinstimmen.
    found = re.search(r'class="tm"[^>]*data-off="(-?\d+)"', TD_ROW)
    offset = found.group(1) if found else '-3'
    seal = f'<img class="seal" src="{SEAL}" alt="trustedDialog Siegel">'
    body = (OPEN_MAIL_TEMPLATE.replace('__COUNT__', count).replace('__OFFSET__', offset).replace('__AV__', avatar)
            .replace('__SEAL__', seal).replace('__SENDER__', sender).replace('__SUBJECT__', subject)
            .replace('__CONTENT__', content))
    return PHONE_OPEN + OPEN_MAIL_STATUS + body + PHONE_CLOSE
"""

# ---------------------------------------------------------------------------------------------------------------------
# 3) Zusatz in build_board_html (vor dem Kommentar "# Kontrastregel auch ...")
# ---------------------------------------------------------------------------------------------------------------------
BUILD_BLOCK = """    # OPEN_MAIL_MOCKUP: optionales 4. Gerät (geöffnete E-Mail) mit demselben Avatar, Absender und Betreff wie die Mailliste
    show_open_mail = bool(show_open_mail)
    board_w = BOARD_W + 380 if show_open_mail else BOARD_W          # 344 px Gerät + 36 px Abstand
    open_col = ('<div class="col" id="col4"><div class="ptitle">Geöffnete E-Mail</div>'
                + open_mail_html(logo, texts[0], texts[1], OPEN_MAIL_CONTENT) + '</div>') if show_open_mail else ''
    all_label = ('Alle 4 Mockups als eine PNG-Grafik herunterladen' if show_open_mail
                 else 'Alle 3 Mockups als eine PNG-Grafik herunterladen')
    open_button = ('<button class="downloadbtn" onclick="downloadOpenMail(this)">Nur Mockup 4 (geöffnete E-Mail)</button>'
                   if show_open_mail else '')
"""

JS_BLOCK = ("function downloadOpenMail(button){return exportNode(document.querySelector('#col4 .phonewrap'),344,701,"
            "'GMX_trustedDialog_GeoeffneteMail_'+safeSender()+'.png',button,null);}\n")

UI_BLOCK = """{i}st.subheader('5. Geöffnete E-Mail (optional)')
{i}with st.container(border=True):
{i}    st.checkbox('Geöffnete E-Mail als 4. Mockup anzeigen', key='show_open_mail',
{i}                help='Ergänzt rechts ein viertes Gerät mit der geöffneten E-Mail: Marke, Avatar, Betreff und die Uhrzeit der '
{i}                     'ersten Mail. Die drei bisherigen Mockups bleiben unverändert.')
"""


def fail(messages):
    print('ABBRUCH - app.py wurde NICHT verändert. Folgende Stellen wurden nicht (eindeutig) gefunden:')
    for message in messages:
        print('  - ' + message)
    print('Bitte die aktuelle app.py an Copilot schicken; die Ankerstellen werden dann angepasst.')
    sys.exit(2)


def apply(source):
    problems, s = [], source

    def count(needle):
        return s.count(needle)

    def replace_once(old, new, label):
        nonlocal s
        n = s.count(old)
        if n != 1:
            problems.append(f'{label} (gefunden: {n}x, erwartet: 1x)')
            return
        s = s.replace(old, new, 1)

    # a) Session-Default
    replace_once("'motif_hint': ''}.items():", "'motif_hint': '', 'show_open_mail': False}.items():", 'Session-Defaults')
    # b) CSS
    replace_once('.downloadbtn:disabled{opacity:.6;cursor:wait}', '.downloadbtn:disabled{opacity:.6;cursor:wait}' + CSS_BLOCK.rstrip('\n'),
                 'CSS-Anker .downloadbtn:disabled')
    # c) Template + Funktion hinter PHONE_CLOSE
    close = "PHONE_CLOSE = '</div></div></div>'"
    replace_once(close, close + '\n' + OPEN_MAIL_DEFS.strip('\n'), 'PHONE_CLOSE')
    # d) Board-Template: 4. Spalte, Button-Beschriftung, Zusatz-Button, JS
    replace_once('<div class="ptitle">Mit trustedDialog Preview</div>__PHONE3__</div>',
                 '<div class="ptitle">Mit trustedDialog Preview</div>__PHONE3__</div>\n__PHONE4__', 'Board-Template (3. Spalte)')
    replace_once('Alle 3 Mockups als eine PNG-Grafik herunterladen</button>', '__ALLLABEL__</button>', 'Download-Button-Beschriftung')
    replace_once('Nur Mockup 3 (mit Preview)</button>', 'Nur Mockup 3 (mit Preview)</button>__EXTRABTN__', 'Button "Nur Mockup 3"')
    replace_once("</script></body></html>'''", JS_BLOCK + "</script></body></html>'''", 'Template-Ende </script></body></html>')
    # e) build_board_html: Signatur, Zusatzblock, Tokens, Breite
    replace_once("promo_label='', promo_code='', show_promo=False):", "promo_label='', promo_code='', show_promo=False, show_open_mail=False):",
                 'Signatur build_board_html')
    comment = re.search(r'^( *)# Kontrastregel auch für die Beispiel-Mails', s, re.M)
    if not comment or len(re.findall(r'^ *# Kontrastregel auch für die Beispiel-Mails', s, re.M)) != 1:
        problems.append('Kommentar "# Kontrastregel auch für die Beispiel-Mails" in build_board_html')
    else:
        s = s[:comment.start()] + BUILD_BLOCK + s[comment.start():]
    replace_once("'__PHONE3__': phones[2],", "'__PHONE3__': phones[2], '__PHONE4__': open_col, '__ALLLABEL__': all_label, '__EXTRABTN__': open_button,",
                 'Token-Dictionary')
    replace_once("'__BW__': str(BOARD_W)", "'__BW__': str(board_w)", 'Board-Breite')
    # f) Aufruf mit neuem Parameter
    replace_once('bool(st.session_state.promo_show))', 'bool(st.session_state.promo_show),\n                     bool(st.session_state.show_open_mail))',
                 'Aufruf build_board_html')
    # g) UI: Haken als eigener Abschnitt direkt hinter dem Feld "Code"
    code_line = re.search(r"^[ \t]*st\.text_input\('Code', key='promo_code'.*\n", s, re.M)
    heading = re.search(r"^([ \t]*)st\.subheader\('4\. trustedDialog Preview-Grafik'\)", s, re.M)
    if not code_line or len(re.findall(r"st\.text_input\('Code', key='promo_code'", s)) != 1:
        problems.append("Eingabefeld st.text_input('Code', key='promo_code', ...)")
    else:
        indent = heading.group(1) if heading else '    '
        s = s[:code_line.end()] + UI_BLOCK.format(i=indent) + s[code_line.end():]
    # h) Fußzeile (optional, rein kosmetisch)
    s = s.replace('Export: eine Grafik mit allen 3 Mockups', 'Export: eine Grafik mit allen Mockups (3 + optional geöffnete E-Mail)', 1)
    return s, problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='nur prüfen, nichts schreiben')
    parser.add_argument('--restore', action='store_true', help='Backup zurückspielen')
    args = parser.parse_args()
    if args.restore:
        if not BACKUP.exists():
            sys.exit('Kein Backup gefunden.')
        shutil.copy2(BACKUP, APP)
        print('app.py aus app.before_open_mail.py wiederhergestellt.')
        return
    if not APP.exists():
        sys.exit('app.py muss im selben Ordner wie dieses Skript liegen.')
    source = APP.read_text(encoding='utf-8')
    if MARKER in source:
        print('app.py enthält das 4. Mockup bereits - nichts zu tun.')
        return
    patched, problems = apply(source)
    if problems:
        fail(problems)
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / 'app_probe.py'
        probe.write_text(patched, encoding='utf-8')
        try:
            py_compile.compile(str(probe), doraise=True)
        except py_compile.PyCompileError as error:
            fail([f'Syntaxprüfung des Ergebnisses fehlgeschlagen: {error.msg}'])
    if args.check:
        print('OK (Prüfung): alle Ankerstellen eindeutig gefunden, Ergebnis kompiliert. Es wurde nichts geschrieben.')
        return
    shutil.copy2(APP, BACKUP)
    APP.write_text(patched, encoding='utf-8')
    print('OK: 4. Mockup "Geöffnete E-Mail" ergänzt. Backup: app.before_open_mail.py')
    print('Starten: streamlit run app.py  ->  Abschnitt "5. Geöffnete E-Mail (optional)" -> Haken setzen.')


if __name__ == '__main__':
    main()
