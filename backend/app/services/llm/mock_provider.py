import re
from typing import Optional, List, Dict, Any
from backend.app.services.llm.base import LLMProvider, StructuredExtraction

ACK_TERMS = {
    # English
    "ok", "okay", "alright", "sure", "got it", "thank you", "thanks", "fine", "understood", "yes", "k", "okk",
    # Hindi (Latin & Devanagari)
    "theek hai", "theek", "thik hai", "thik", "accha", "achha", "dhanyawad", "shukriya", "dhanyavaad", "sahi hai",
    "theek h", "thik h", "theek he", "thik he", "thek hai", "thek",
    "ठीक है", "ठीक", "अच्छा", "धन्यवाद", "शुक्रिया", "सही है",
    # Marathi (Latin & Devanagari) — "ho"/"हो" only matched as standalone Marathi YES (exact)
    "thik ahe", "thik aahe", "theek ahe", "theek aahe", "thik ahay", "bar ahe", "bara ahe",
    "hoy", "bar", "bara", "samajle", "samajla",
    "ठीक आहे", "ठीक", "होय", "बरं आहे", "बरं", "बरे आहे", "धन्यवाद", "समजले", "कळले"
}

def is_acknowledgment_message(text: str) -> bool:
    if not text:
        return False
    cleaned = re.sub(r'[^\w\s\u0900-\u097F]', ' ', text).strip().lower()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    if not cleaned:
        return False
    # A message with more than 4 words is never a simple acknowledgment;
    # it is describing symptoms or asking a question — never treat as ack.
    words = cleaned.split()
    if len(words) > 4:
        return False
    # "ho" / "हो" are valid standalone Marathi YES but must only match exact / full-phrase
    standalone_marathi_yes = {"ho", "हो"}
    if cleaned in standalone_marathi_yes:
        return True
    for term in ACK_TERMS:
        if cleaned == term:
            return True
        # Multi-word ACK terms: allow sub-phrase match
        if " " in term and (cleaned.startswith(term) or cleaned.endswith(term) or f" {term} " in cleaned):
            return True
        # Single-word terms: match only as whole words, not substrings
        if " " not in term and term not in standalone_marathi_yes and re.search(
            rf'(?<![\w\u0900-\u097F]){re.escape(term)}(?![\w\u0900-\u097F])', cleaned
        ):
            return True
    return False

class MockLocalLLMProvider(LLMProvider):
    """
    Deterministic, zero-dependency local LLM provider.
    Extracts structured clinical information from English, Hindi, Marathi, and mixed input.
    Guarantees unknown values remain None, fulfilling Section 7 requirements.
    Supports both Romanized/transliterated and native Devanagari scripts.
    """

    BODY_PARTS = {
        "finger": ["finger", "ungli", "ungliyan", "bota", "bot", "उंगली", "उंगलियां", "बोट", "बोटे"],
        "hand": ["hand", "haath", "haat", "palm", "hatheli", "हाथ", "हातातून", "हात", "हथेली"],
        "leg": ["leg", "pair", "tang", "paay", "पैर", "टांग", "पाय"],
        "foot": ["foot", "feet", "panja", "paaul", "पंजा", "पाऊल"],
        "arm": ["arm", "bahu", "dand", "बांह", "दंड"],
        "head": ["head", "sir", "sar", "matha", "doke", "सिर", "सर", "माथा", "डोके"],
        "nose": ["nose", "naak", "nak", "नाक"],
        "chest": ["chest", "seena", "chhati", "chhatiye", "सीना", "छाती", "छातीत"],
        "stomach": ["stomach", "belly", "abdomen", "pet", "पेट"],
        "knee": ["knee", "ghutna", "dhingar", "gudgha", "घुटने", "गुडघा"],
        "ankle": ["ankle", "takhna", "ghota", "टखना", "घोटा"],
        "eye": ["eye", "aankh", "dola", "आंख", "डोळा"]
    }

    CHIEF_COMPLAINTS = {
        "cut": ["cut", "scratch", "scrape", "laceration", "wound", "cheera", "ghav", "jakhmi", "chot", "कट", "घाव", "जखमी", "जखम", "चोट"],
        "bleeding": ["bleed", "bleeding", "blood", "khoon", "rakt", "rakta", "खून", "रक्त", "रक्तस्त्राव"],
        "burn": ["burn", "burned", "burning", "scald", "jal gaya", "jala", "bhajla", "pola", "जल", "जला", "भाजले", "भाजला"],
        "sprain": ["sprain", "twisted", "twist", "swelling", "moch", "mar", "lagli", "मोच", "मार", "लागली"],
        "fever": ["fever", "temperature", "chills", "bukhar", "taap", "बुखार", "ताप"],
        "dizziness": ["dizzy", "dizziness", "faint", "fainted", "blackout", "chakkar", "bhraman", "चक्कर", "बेशुद्ध"],
        "nosebleed": ["nosebleed", "nose bleed", "nak se khoon", "nakatun rakt", "नाक से खून", "नाकातून रक्त"],
        "allergic_reaction": ["allergy", "allergic", "rash", "itching", "hives", "khujli", "एलर्जी", "खाज", "खुजली", "पुरळ"],
        "pain": ["pain", "leg pain", "back pain", "body pain", "arm pain", "ache", "aching", "hurts", "sore", "dard", "dukhna", "dukhne", "vedana", "दर्द", "दुखणे", "वेदना", "कळ"],
        "headache": ["headache", "sir dard", "sar dard", "matha dard", "doke dukhne", "डोकेदुखी", "सिरदर्द"],
        "stomach_ache": ["stomach pain", "belly ache", "abdomen pain", "pet dard", "potat dukhne", "cramps", "पेट दर्द", "पोटदुखी"],
        "cough_cold": ["cough", "cold", "sore throat", "khansi", "jukham", "khokla", "sardi", "खांसी", "जुकाम", "खोकला", "सर्दी"],
        "weakness": ["weakness", "tired", "fatigue", "kamzori", "thakan", "ashaktapana", "कमजोरी", "थकावट", "अशक्तपणा"],
        "nausea_vomiting": ["vomit", "vomiting", "nausea", "ulti", "mitali", "उल्टी", "मळमळ"]
    }

    SYMPTOM_KEYWORDS = {
        "bleeding": ["bleed", "bleeding", "blood", "khoon", "rakt", "खून", "रक्त", "रक्तस्त्राव"],
        "pain": ["pain", "hurts", "aching", "dard", "dukhne", "vedana", "दर्द", "दुखणे", "वेदना"],
        "swelling": ["swelling", "swollen", "soojan", "sujan", "sujla", "सूजन", "सूज"],
        "chills": ["chills", "shivering", "thand", "kampa", "thandi", "ठंड", "कंप", "थंडी"],
        "dizziness": ["dizzy", "lightheaded", "chakkar", "चक्कर"],
        "difficulty_breathing": ["difficulty breathing", "shortness of breath", "breathless", "sans lene", "shwas", "सांस", "श्वास"],
        "blisters": ["blister", "blisters", "foda", "chhala", "chhale", "छाले", "फोड"],
        "itching": ["itching", "itchy", "khujli", "kharaj", "खुजली", "खाज"],
        "fever": ["fever", "bukhar", "taap", "बुखार", "ताप"],
        "cough": ["cough", "khansi", "khokla", "खांसी", "खोकला"]
    }

    def _match_keyword(self, text: str, keyword: str) -> bool:
        # If keyword has non-ascii characters (e.g. Devanagari), regex \b might not match on Devanagari boundaries
        if any(ord(c) > 127 for c in keyword):
            return keyword in text
        return bool(re.search(rf"\b{re.escape(keyword)}\b", text))

    async def extract_information(
        self,
        text: str,
        conversation_history: List[Dict[str, str]],
        current_language: str = "en"
    ) -> StructuredExtraction:
        full_text = text.lower()
        
        # 1. Detect language
        detected_language = current_language
        if any(c in full_text for c in ["है", "हो", "था", "थी", "गई", "गया"]) or any(w in full_text for w in ["hai", "ho", "mera", "meri", "dard", "khoon", "bukhar", "chot"]):
            detected_language = "hi"
        elif any(c in full_text for c in ["आहे", "होता", "झाली", "झाला"]) or any(w in full_text for w in ["ahe", "hota", "majhya", "majha", "dukhate", "rakt", "taap"]):
            detected_language = "mr"

        # 2. Extract Chief Complaint
        chief_complaint = None
        for cc, keywords in self.CHIEF_COMPLAINTS.items():
            if any(self._match_keyword(full_text, k) for k in keywords):
                chief_complaint = cc
                break

        # 3. Extract Body Part
        body_part = None
        for bp, aliases in self.BODY_PARTS.items():
            if any(self._match_keyword(full_text, a) for a in aliases):
                body_part = bp
                break

        # 4. Extract Symptoms
        symptoms = []
        for sym, kw_list in self.SYMPTOM_KEYWORDS.items():
            if any(self._match_keyword(full_text, k) for k in kw_list):
                symptoms.append(sym)

        # 5. Extract Duration
        duration = None
        duration_match = re.search(
            r"(\d+\s*(?:minute|min|hour|hr|day|week|sec|second)s?|\d+\s*(?:ghante|din|minute|mints)|kuchh\s*der|thodya\s*vela|\d+\s*(?:मिनट|घंटे|दिन|तास))",
            full_text
        )
        if duration_match:
            duration = duration_match.group(1).strip()

        # 6. Extract Severity
        severity = None
        if any(w in full_text for w in ["severe", "unbearable", "bahut zyada", "khup jast", "extreme", "तीव्र", "खूप"]):
            severity = "severe"
        elif any(w in full_text for w in ["moderate", "medium", "theek theek", "madhyam", "मध्यम"]):
            severity = "moderate"
        elif any(w in full_text for w in ["little", "mild", "slight", "halka", "thoda", "kam", "थोड़ा", "हल्का", "कमी"]):
            severity = "mild"

        # 7. Additional structured fields
        additional_fields = {}
        if body_part:
            additional_fields["body_part"] = body_part
        if any(w in full_text for w in ["spurting", "pulsat", "fountain"]):
            additional_fields["bleeding_rate"] = "spurting"
            additional_fields["bleeding_status"] = "spurting"
        elif any(w in full_text for w in ["little", "slow", "thoda", "थोड़ा", "कमी", "controlled"]):
            additional_fields["bleeding_rate"] = "slow"
            additional_fields["bleeding_status"] = "controlled"

        pain_match = re.search(r"(?:pain|scale|dard|vedana|दर्द|वेदना)?\s*(\d{1,2})\s*(?:/10|out of 10)?", full_text)
        if pain_match:
            try:
                p_val = int(pain_match.group(1))
                if 1 <= p_val <= 10:
                    additional_fields["pain_level"] = p_val
            except ValueError:
                pass

        if any(w in full_text for w in ["blister", "chhala", "foda", "छाले", "फोड"]):
            additional_fields["blisters_present"] = "yes"

        if any(w in full_text for w in ["can't walk", "cannot walk", "vajan nahi", "bhar deta yet nahi"]):
            additional_fields["weight_bearing"] = "unable"

        return StructuredExtraction(
            chief_complaint=chief_complaint,
            body_part=body_part,
            symptoms=symptoms,
            duration=duration,
            severity=severity,
            additional_fields=additional_fields,
            detected_language=detected_language
        )

    async def generate_response(
        self,
        patient_message: str,
        conversation_history: List[Dict[str, str]],
        next_question: Optional[str],
        guidance_steps: Optional[List[Dict[str, Any]]],
        alert_instruction: Optional[str],
        language: str = "en"
    ) -> str:
        parts = []

        if alert_instruction:
            parts.append(f"⚠️ {alert_instruction}")
            if language == "hi":
                parts.append("कृपया शांत बैठें। हमारी आपातकालीन चिकित्सा टीम को तुरंत सूचित कर दिया गया है और वे आपके पास आ रहे हैं।")
            elif language == "mr":
                parts.append("कृपया शांत बसा. आमच्या आपत्कालीन वैद्यकीय पथकाला त्वरित माहिती देण्यात आली असून ते आपल्याकडे येत आहेत.")
            else:
                parts.append("Please remain calm and seated. A member of our clinical team is on their way to assist you.")
            return "\n\n".join(parts)

        p_text = patient_message.strip().lower()
        is_ack = is_acknowledgment_message(patient_message)

        # Build combined text (current + history) for disease-category detection
        _all_text = p_text + " " + " ".join(
            m.get("content", "").lower() for m in conversation_history
        )

        if is_ack and not next_question:
            # Brief, natural ack - no long canned welcome message
            if language == "hi":
                return (
                    "ठीक है। आपकी जानकारी डॉक्टर और नर्सिंग स्टाफ के पास पहुंच गई है। "
                    "कृपया प्रतीक्षा कक्ष में आराम से बैठें — डॉक्टर जल्द आएंगे।"
                )
            elif language == "mr":
                return (
                    "ठीक आहे। आपली माहिती डॉक्टरांना दिली आहे। "
                    "कृपया प्रतीक्षा कक्षात शांतपणे बसा — डॉक्टर लवकरच येतील."
                )
            else:
                return (
                    "Noted! Your details have been passed to the medical team. "
                    "Please rest comfortably in the waiting area - the doctor will be with you shortly."
                )

        is_negative_reply = any(w in p_text for w in ["no", "nope", "not yet", "haven't", "dont know", "nahi", "nahin", "nahi pata", "naahi", "nako"])
        is_initial_message = (len(conversation_history) <= 1)

        if next_question:
            if is_initial_message:
                if language == "hi":
                    acknowledgment = "आपकी परेशानी के बारे में सुनकर दुख हुआ। डॉक्टर और नर्सिंग स्टाफ की सहायता के लिए आइए कुछ बुनियादी जानकारी दर्ज कर लेते हैं।"
                elif language == "mr":
                    acknowledgment = "आपल्या त्रासाबद्दल ऐकून वाईट वाटले. डॉक्टरांच्या मदतीसाठी कृपया ही प्राथमिक माहिती सांगा."
                else:
                    acknowledgment = "I'm sorry to hear that you are experiencing this discomfort. Let me ask a few quick questions to help the doctors assess you properly."
            elif is_negative_reply:
                if language == "hi":
                    acknowledgment = "समझ गया, कोई बात नहीं कि आपने अभी यह विवरण नहीं देखा है।"
                elif language == "mr":
                    acknowledgment = "समजले, काही हरकत नाही."
                else:
                    acknowledgment = "Understood, that is completely fine that you haven't checked or don't know yet."
            elif is_ack:
                if language == "hi":
                    acknowledgment = "ठीक है, आइए आगे बढ़ते हैं।"
                elif language == "mr":
                    acknowledgment = "ठीक आहे, पुढे जाऊया."
                else:
                    acknowledgment = "Alright, let's continue."
            else:
                if language == "hi":
                    acknowledgment = "जानकारी के लिए धन्यवाद, मैंने यह दर्ज कर लिया है।"
                elif language == "mr":
                    acknowledgment = "माहिती दिल्याबद्दल धन्यवाद, मी नोंदवून घेतले आहे."
                else:
                    acknowledgment = "Thank you, I've noted that down for the medical team."

            parts.append(f"{acknowledgment}\n\n{next_question}")

        elif guidance_steps:
            if language == "hi":
                intro = "सभी विवरण साझा करने के लिए धन्यवाद। आपकी ओपीडी ट्राइएज फ़ाइल अपडेट कर दी गई है।\n\nडॉक्टर द्वारा बुलाए जाने तक, कृपया अस्पताल द्वारा अनुमोदित इन प्राथमिक उपचार निर्देशों का पालन करें (DEMO FIRST-AID GUIDANCE):"
                closing = "कृपया आराम से प्रतीक्षा करें। नर्सिंग स्टाफ जल्द ही आपकी जांच करेंगे।"
            elif language == "mr":
                intro = "माहिती दिल्याबद्दल धन्यवाद. आपली ओपीडी ट्रायज नोंद अद्ययावत करण्यात आली आहे.\n\nवैद्यकीय कर्मचाऱ्यांकडून बोलावणे येईपर्यंत कृपया खालील प्रथमोपचार मार्गदर्शन पाळा (DEMO FIRST-AID GUIDANCE):"
                closing = "कृपया विश्रांती घ्या. आरोग्य कर्मचारी लवकरच आपली तपासणी करतील."
            else:
                intro = "Thank you for providing those details. I have updated your OPD intake record for the doctor and triage team.\n\nWhile you wait comfortably to be called, please follow these hospital-approved first-aid steps (DEMO / REQUIRES CLINICAL VALIDATION):"
                closing = "Please rest comfortably. Healthcare staff will inspect you shortly."

            parts.append(intro)
            for step in guidance_steps:
                parts.append(f"{step.get('step')}. {step.get('instruction')}")
            parts.append(closing)

        else:
            # ——————————————————————————————————————————
            # Disease-Specific Quick Guidance Dispatcher
            # Triggered when no more protocol questions remain AND
            # no pre-built guidance_steps from protocol are available.
            # Each branch gives natural, targeted, compassionate guidance.
            # ——————————————————————————————————————————

            def _has(*keywords):
                return any(kw in _all_text for kw in keywords)

            # 1. Severe pain + no staff nearby
            if _has("koi nurse nahi", "nurse nahi", "nurse nahin", "koi nahi", "कोई नर्स नहीं", "no nurse", "no staff") and \
               _has("pen", "pain", "dard", "dukhne", "दर्द", "vedana"):
                if language == "hi":
                    parts.append(
                        "आपकी सतर्कता संदेश मिल गया है। प्रतीक्षा कक्ष से बाहर निकलें और डेस्क पर बेल बजाएं या रिसेप्शन पर अपनी स्थिति बताएं। "
                        "तब तक आराम से बैठें, लेटें नहीं। उन्हें अब सूचित किया जा रहा है।"
                    )
                elif language == "mr":
                    parts.append(
                        "आपला तक्रार संदेश पोचला आहे। प्रतीक्षा कक्षाबाहेर जा आणि डेस्कवरील घंटी वाजवा किंवा रिसेप्शनला आपली स्थिती सांगा। "
                        "तोपर्यंत शांतपणे बसा, झोपू नका। निरोप सूचित केले आहे."
                    )
                else:
                    parts.append(
                        "Your alert has been sent. Please walk to the reception desk or press the call bell to notify staff. "
                        "Until then, sit upright and stay calm. Help is being dispatched now."
                    )

            # 2. Fever / Temperature
            elif _has("fever", "bukhar", "taap", "temperature", "chills", "thand", "बुखार", "ताप", "thandi"):
                if language == "hi":
                    parts.append(
                        "बुखार के लिए कुछ जरूरी सलाह:\n"
                        "• ठंडा पानी पिएं — हर घंटे एक गिलास (ओआरएस या सादा पानी)।\n"
                        "• बहुत मोटे कंबल ना ओढ़ें।\n"
                        "• माथे पर ठंडी पट्टी रखें यदि बुखार 101°F से ज़्यादा हो।\n"
                        "• डॉक्टर की सलाह के बिना कोई दवाई ना लें।\n"
                        "• डॉक्टर इसी दौरे आपकी जांच करेंगे।"
                    )
                elif language == "mr":
                    parts.append(
                        "तापासाठी महत्त्वाचे मार्गदर्शन:\n"
                        "• थंड पाणी प्या — दर तासाला एक ग्लास (ओआरएस किंवा सादे पाणी)।\n"
                        "• जाड रजई ओढ़ू नका।\n"
                        "• ताप 101°F पेक्षा जास्त असल्यास कपाळावर थंड पट्टी ठेवा।\n"
                        "• डॉक्टरांच्या सल्ल्याशिवाय कोणतीही औषधे घेऊ नका।\n"
                        "• डॉक्टर लवकरच तपासणी घेतील."
                    )
                else:
                    parts.append(
                        "For fever, here is what you can do while you wait:\n"
                        "• Drink cool water or ORS every hour to stay hydrated.\n"
                        "• Remove heavy blankets; wear light clothing.\n"
                        "• Place a cool damp cloth on your forehead if fever is above 101°F.\n"
                        "• Do not take any medication without the doctor's instruction.\n"
                        "• The doctor will examine you shortly."
                    )

            # 3. Cough / Cold / Sore Throat
            elif _has("cough", "khansi", "khokla", "cold", "sardi", "sore throat", "throat", "gala", "jukham", "खांसी", "सर्दी"):
                if language == "hi":
                    parts.append(
                        "खांसी/जुकाम के लिए राहत के उपाय:\n"
                        "• गरम पानी में नमक डालकर गरारा करें — गले को आराम मिलेगा।\n"
                        "• हल्का गरम पानी या शहद वाला पानी पिएं।\n"
                        "• ऐसी जगह बैठें जहां रोशनी कम हो और ठंडी हवा ना आए।\n"
                        "• अन्य मरीज़ों से सुरक्षा के लिए सर्जिकल मास्क पहनें।\n"
                        "• डॉक्टर जल्द आकर आपकी जांच करेंगे।"
                    )
                elif language == "mr":
                    parts.append(
                        "खोकला/सर्दीसाठी आराम\n"
                        "• गरम पाण्यात मीठ घालून गुळण्या करा — घशाला बरे वाटेल.।\n"
                        "• कोमट गरम पाणी किंवा मधाचे पाणी प्या।\n"
                        "• थंड हवेपासून दूर राहा।\n"
                        "• इतर रुग्णांपासून संरक्षणासाठी सर्जिकल मास्क घाला.।\n"
                        "• डॉक्टर लवकरच तपासणी घेतील."
                    )
                else:
                    parts.append(
                        "For cough and cold relief while you wait:\n"
                        "• Gargle with warm salt water — it soothes the throat.\n"
                        "• Sip warm water or honey-water gently.\n"
                        "• Sit away from cold air vents or direct fans.\n"
                        "• Wear a surgical mask to protect others in the waiting area.\n"
                        "• The doctor will examine you shortly."
                    )

            # 4. Stomach / Abdominal Pain
            elif _has("stomach", "belly", "abdomen", "pet dard", "potat", "pet", "ulti", "nausea", "vomit", "cramps", "पेट दर्द", "पोटदुखी"):
                if language == "hi":
                    parts.append(
                        "पेट दर्द के लिए राहत:\n"
                        "• अभी कुछ ना खाएं — खाली पेट में तले हुए मसालेदार खाना ना खाएं।\n"
                        "• घुटने सीने से लगाकर बैठें (foetal position) — इससे दर्द कम हो सकता है।\n"
                        "• डॉक्टर की सलाह के बिना दर्द निवारक गोली ना लें।\n"
                        "• डॉक्टर जल्द आकर आपकी जांच करेंगे।"
                    )
                elif language == "mr":
                    parts.append(
                        "पोटदुखीसाठी आराम:\n"
                        "• आता काहीही खाऊ नका — रिकाम्या पोटावर तेलकट मसालेदार औषध घेऊ नका.।\n"
                        "• गुडघे छातीशी लावून बसा (foetal position) — वेदना कमी होते.।\n"
                        "• डॉक्टरांना न सांगता वेदनाशामक औषध घेऊ नका.।\n"
                        "• डॉक्टर लवकरच तपासणी घेतील."
                    )
                else:
                    parts.append(
                        "For stomach pain relief while waiting:\n"
                        "• Avoid eating anything right now — especially heavy or spicy food.\n"
                        "• Try sitting in a curled-up position (knees to chest) — it can ease the pain.\n"
                        "• Do not take any painkiller without the doctor's advice.\n"
                        "• The doctor will examine you shortly."
                    )

            # 5. Headache / Dizziness
            elif _has("headache", "sir dard", "sar dard", "doke dukhne", "dizzy", "chakkar", "ghabrahat", "सिरदर्द", "चक्कर", "डोकेदुखी"):
                if language == "hi":
                    parts.append(
                        "सिरदर्द / चक्कर के लिए:\n"
                        "• तुरंत बैठ जाएं — अचानक खड़े होने से गिरने का खतरा है।\n"
                        "• ठंडा पानी पिएं और आंखें बंद करके आराम करें।\n"
                        "• तेज़ रोशनी से दूर रहें।\n"
                        "• आंखें बंद करके धीरे-धीरे सांस लें।\n"
                        "• डॉक्टर आपका बलडप्रेशर और स्थिति की जांच करेंगे।"
                    )
                elif language == "mr":
                    parts.append(
                        "डोकेदुखी / चक्करसाठी:\n"
                        "• लगेच बसा — अचानक उभे राहिल्यास पडण्याचा धोका आहे.।\n"
                        "• थंड पाणी प्या आणि डोळे बंद करून विश्रांती घ्या.।\n"
                        "• तीव्र प्रकाशपासून दूर राहा.।\n"
                        "• डॉक्टर रक्तदाब आणि आरोग्य तपासणी घेतील."
                    )
                else:
                    parts.append(
                        "For headache or dizziness, while you wait:\n"
                        "• Sit down immediately — sudden standing can cause a fall.\n"
                        "• Sip cool water and close your eyes to rest.\n"
                        "• Stay away from bright lights and noise.\n"
                        "• Breathe slowly and steadily.\n"
                        "• The doctor will check your blood pressure and condition shortly."
                    )

            # 6. Body / Musculoskeletal / Back / Joint Pain
            elif _has("body pain", "back pain", "leg pain", "arm pain", "joint", "body dard", "kamar dard", "haddi", "कमर दर्द", "हाड दुखते", "moch", "sprain"):
                if language == "hi":
                    parts.append(
                        "शरीर / कमर दर्द के लिए:\n"
                        "• प्रभावित हिस्से पर वजन ना डालें।\n"
                        "• आराम से कुर्सी पर बैठें।\n"
                        "• खिंचाइला ना खिंचें और ना दें।\n"
                        "• सूजन हो तो ठंडा कपड़ा हल्के से लगाएं।\n"
                        "• डॉक्टर जल्द आकर आपकी जांच करेंगे।"
                    )
                elif language == "mr":
                    parts.append(
                        "शरीरदुखी / कंबरदुखीसाठी:\n"
                        "• दुखणाऱ्या भागावर वजन ठेवू नका.।\n"
                        "• स्वस्थ खुर्चीवर बसा.।\n"
                        "• ताणू नका किंवा झतकू नका.।\n"
                        "• सूज असल्यास थंड फडके हलकेच लावा.।\n"
                        "• डॉक्टर लवकरच तपासणी घेतील."
                    )
                else:
                    parts.append(
                        "For body or joint pain relief:\n"
                        "• Do not put weight on the affected area.\n"
                        "• Sit in a comfortable chair and rest.\n"
                        "• Avoid stretching or sudden movements.\n"
                        "• If swollen, gently place a cool cloth on it.\n"
                        "• The doctor will examine you shortly."
                    )

            # 7. Cut / Wound / Bleeding
            elif _has("cut", "bleeding", "blood", "wound", "ghav", "khoon", "rakt", "खून", "घाव", "रक्त"):
                if language == "hi":
                    parts.append(
                        "कटने / खून आने पर तुरंत यह करें:\n"
                        "• साफ कपड़े या रूमाल से जख्म पर सीधा दबाव डालें — खून बंद होगा।\n"
                        "• हाथ / पैर को ऊंचा उठाकर रखें।\n"
                        "• घरेलू नुसखे (haldi, powder) ना लगाएं — इनफेक्शन हो सकता है।\n"
                        "• डॉक्टर जल्द आकर आपकी ड्रेसिंग करेंगे।"
                    )
                elif language == "mr":
                    parts.append(
                        "जखम / रक्तस्त्रावासाठी:\n"
                        "• स्वच्छ कपड़्याने सीधा दाब द्या — रक्तस्त्राव थांबेल.।\n"
                        "• हात / पाय उचलून धरा.।\n"
                        "• हळद, पावडर लावू नका — इन्फेक्शन होईल.।\n"
                        "• डॉक्टर लवकरच तपासणी घेतील."
                    )
                else:
                    parts.append(
                        "For a cut or bleeding wound:\n"
                        "• Apply firm, direct pressure with a clean cloth or bandage — do not remove it.\n"
                        "• Elevate the hand or foot above heart level if possible.\n"
                        "• Do NOT apply home remedies (turmeric, powder) — they can cause infection.\n"
                        "• The medical team will dress and assess the wound shortly."
                    )

            # 8. Burns
            elif _has("burn", "jal", "bhajle", "bhajla", "pola", "scald", "जला", "भाजले"):
                if language == "hi":
                    parts.append(
                        "जलने / झुलसने पर तुरंत यह करें:\n"
                        "• ठंडे बहते नल के पानी से 15 मिनट तक धोएं — आइस नहीं लगाएं।\n"
                        "• टूथपेस्ट, मक्खन, हल्दी ना लगाएं — जलन बढ़ाते हैं।\n"
                        "• छाले ने फोड़ें नहीं।\n"
                        "• डॉक्टर जल्द आकर ड्रेसिंग करेंगे।"
                    )
                elif language == "mr":
                    parts.append(
                        "भाजणे / जळणेसाठी:\n"
                        "• थंड वाहत्या नळाच्या पाण्याखाली 15 मिनिटे धरा — बरफ नको.।\n"
                        "• टूथपेस्ट, लोणी, हळद लावू नका — धोका वाढतो.।\n"
                        "• फोड फोडू नका.।\n"
                        "• डॉक्टर लवकरच तपासणी घेतील."
                    )
                else:
                    parts.append(
                        "For burns, do this immediately:\n"
                        "• Hold the area under cool (not ice cold) running water for at least 15 minutes.\n"
                        "• Do NOT apply toothpaste, butter, or turmeric — they trap heat.\n"
                        "• Do not burst any blisters.\n"
                        "• The doctor will assess and dress the burn shortly."
                    )

            # Default fallback (general triage)
            else:
                if language == "hi":
                    parts.append(
                        "आपकी जानकारी डॉक्टर और नर्सिंग स्टाफ को मिल गई है। "
                        "कृपया आराम से बैठें — डॉक्टर जल्द आएंगे। यदि दर्द तेज़ हो तो नजदीकी नर्स को सूचित करें।"
                    )
                elif language == "mr":
                    parts.append(
                        "आपली माहिती डॉक्टर आणि नर्सिंग स्टाफना दिली आहे। "
                        "कृपया शांत बसा — डॉक्टर लवकरच येतील. वेदना वाढल्यास नजीकच्या परिचारिकेला सांगा."
                    )
                else:
                    parts.append(
                        "Your information has been recorded and clinical staff have been notified. "
                        "Please rest comfortably — the doctor will be with you shortly. "
                        "If pain worsens, please alert the nearby nurse."
                    )


        return "\n\n".join(parts)
