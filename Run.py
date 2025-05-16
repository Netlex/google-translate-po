import os
import polib
from deep_translator import GoogleTranslator

def preflight_check(src_dir, dest_dir, src_lang, dest_lang):
    print("🔍 Запуск предварительной проверки...")

    # Проверка прав на запись
    try:
        os.makedirs(dest_dir, exist_ok=True)
        test_file = os.path.join(dest_dir, "__test__.txt")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print("✅ Права на запись в папку сохранения есть.")
    except Exception as e:
        print(f"❌ Ошибка доступа к '{dest_dir}': {e}")
        exit(1)

    # Проверка переводчика
    try:
        translator = GoogleTranslator(source=src_lang, target=dest_lang)
        test_translation = translator.translate("Test")
        if not isinstance(test_translation, str):
            raise Exception("Некорректный ответ от переводчика.")
        print(f"✅ Перевод работает: 'Test' → '{test_translation}'")
    except Exception as e:
        print(f"❌ Ошибка при тестовом переводе: {e}")
        exit(1)

    # Проверка первого .po файла
    sample_file = next((f for f in os.listdir(src_dir) if f.endswith(".po")), None)
    if sample_file:
        path = os.path.join(src_dir, sample_file)
        po = polib.pofile(path)
        print(f"📄 Проверка файла: {sample_file}")
        for entry in po[:2]:
            print(f"→ '{entry.msgid}' → '{translator.translate(entry.msgid)}'")
    else:
        print("⚠️ Нет .po файлов для проверки.")
        exit(1)

    print("✅ Предварительная проверка завершена успешно.\n")

def translate_po_file(src_path, dest_path, src_lang, dest_lang):
    po = polib.pofile(src_path)
    translator = GoogleTranslator(source=src_lang, target=dest_lang)

    total = len(po)
    translated_count = 0

    for i, entry in enumerate(po, 1):
        if (not entry.translated()) or (entry.msgstr.strip() == entry.msgid.strip()):
            try:
                translated_text = translator.translate(entry.msgid)
                if translated_text:
                    entry.msgstr = translated_text
                    translated_count += 1
                    print(f"[{i}/{total}] Переведено: '{entry.msgid}' → '{translated_text}'")
                else:
                    print(f"[{i}/{total}] ⚠️ Пустой перевод для: '{entry.msgid}'")
            except Exception as e:
                print(f"[{i}/{total}] ❌ Ошибка перевода '{entry.msgid}': {e}")
        else:
            print(f"[{i}/{total}] ⏩ Пропущено: '{entry.msgid}'")

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    po.save(dest_path)
    print(f"💾 Сохранено в: {dest_path}")
    print(f"✅ Готово: {translated_count} из {total} строк переведено.\n")

def translate_po_directory(src_dir, dest_dir, src_lang, dest_lang):
    preflight_check(src_dir, dest_dir, src_lang, dest_lang)
    for filename in os.listdir(src_dir):
        if filename.endswith(".po"):
            src_path = os.path.join(src_dir, filename)
            dest_path = os.path.join(dest_dir, filename)
            translate_po_file(src_path, dest_path, src_lang, dest_lang)

translate_po_directory("./untranslated", "./translated", src_lang="en", dest_lang="ru")