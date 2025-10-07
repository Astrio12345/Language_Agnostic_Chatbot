from deep_translator import GoogleTranslator

# Map unsupported fastText codes → supported GoogleTranslator codes
LANGUAGE_CODE_MAP = {
    "bpy": "bn",   # Bishnupriya Manipuri → Bengali
    "bh": "bho",   # Bhojpuri → Bho
    "mai": "hi",   # Maithili → Hindi (fallback)
    # Add more mappings if needed
}

def normalize_lang_code(lang_code: str) -> str:
    """Ensure lang_code is supported by deep_translator."""
    return LANGUAGE_CODE_MAP.get(lang_code, lang_code)

def translate_to_english(text, source_lang):
    if source_lang == "en":
        return text
    try:
        src = normalize_lang_code(source_lang)
        return GoogleTranslator(source=src, target="en").translate(text)
    except Exception as e:
        print(f"⚠️ Translation failed for {source_lang}: {e}")
        # Fallback → auto-detect
        return GoogleTranslator(source="auto", target="en").translate(text)

def translate_to_original(text, target_lang):
    if target_lang == "en":
        return text
    try:
        tgt = normalize_lang_code(target_lang)
        return GoogleTranslator(source="en", target=tgt).translate(text)
    except Exception as e:
        print(f"⚠️ Back-translation failed for {target_lang}: {e}")
        return text
