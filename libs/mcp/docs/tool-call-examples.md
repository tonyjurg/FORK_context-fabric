# MCP Tool Call Examples

Examples from BHSA corpus (`/Users/cody/github/etcbc/bhsa/tf/2021`).

---

## Entry Point

### context_fabric_usage_guide

Get system overview and workflow patterns. Call this first.

**Request:**
```json
{}
```

**Response:**
```json
{
  "description": "Context Fabric exposes Text-Fabric corpora for structured analysis. Corpora contain hierarchical objects (e.g., words, sentences, documents) with arbitrary annotations. A corpus can be annotated for almost anything: linguistics, music, manuscripts, DNA sequences, legal documents, etc.",
  "capabilities": [
    "Search for patterns using structural templates",
    "Filter by any annotated feature on any object type",
    "Analyze feature distributions across search results",
    "Retrieve passages by section reference",
    "Explore hierarchical relationships between objects"
  ],
  "workflows": [
    {
      "goal": "Explore corpus structure",
      "description": "Understand what's in the corpus before searching",
      "steps": [
        "describe_corpus() - Get node types and section structure",
        "list_features(node_types=[...]) - See features for a node type",
        "describe_feature('feature_name') - Get sample values for a feature"
      ]
    },
    {
      "goal": "Understand text encoding",
      "description": "Learn how text is encoded before lexical searches",
      "steps": [
        "get_text_formats() - See original script and transliteration samples",
        "Use samples to construct accurate search patterns"
      ],
      "note": "Critical for lexical searches (lex=...) or surface text queries"
    },
    {
      "goal": "Search for patterns",
      "description": "Find patterns matching structural templates",
      "steps": [
        "search_syntax_guide() - Learn search template syntax",
        "search(template, return_type='count') - Check result count",
        "search(template) - Get actual results (validation errors returned automatically)"
      ]
    },
    {
      "goal": "Analyze distributions",
      "description": "Understand feature patterns across results",
      "steps": [
        "search(template, return_type='statistics', aggregate_features=[...])"
      ]
    },
    {
      "goal": "Read passages",
      "description": "Retrieve text by section reference",
      "steps": [
        "get_passages([[section_ref], ...])"
      ]
    }
  ],
  "tips": [
    "Start with describe_corpus() to understand the structure",
    "Use list_features(node_types=[...]) to find relevant features",
    "Call get_text_formats() before lexical/surface text searches",
    "Use search(..., return_type='count') before fetching full results",
    "Invalid templates return detailed error messages automatically"
  ],
  "next_step": "Call describe_corpus() to see node types and section structure"
}
```

---

## Discovery Tools

### list_corpora

List all loaded corpora.

**Request:**
```json
{}
```

**Response:**
```json
{
  "corpora": ["bhsa"],
  "current": "bhsa"
}
```

---

### describe_corpus

Get corpus structure overview (node types, sections).

**Request:**
```json
{}
```

**Response:**
```json
{
  "name": "bhsa",
  "node_types": [
    {"type": "book", "count": 39, "is_slot_type": false},
    {"type": "chapter", "count": 929, "is_slot_type": false},
    {"type": "lex", "count": 9230, "is_slot_type": false},
    {"type": "verse", "count": 23213, "is_slot_type": false},
    {"type": "half_verse", "count": 45179, "is_slot_type": false},
    {"type": "sentence", "count": 63717, "is_slot_type": false},
    {"type": "sentence_atom", "count": 64514, "is_slot_type": false},
    {"type": "clause", "count": 88131, "is_slot_type": false},
    {"type": "clause_atom", "count": 90704, "is_slot_type": false},
    {"type": "phrase", "count": 253203, "is_slot_type": false},
    {"type": "phrase_atom", "count": 267532, "is_slot_type": false},
    {"type": "subphrase", "count": 113850, "is_slot_type": false},
    {"type": "word", "count": 426590, "is_slot_type": true}
  ],
  "sections": {
    "levels": ["book", "chapter", "verse"]
  }
}
```

---

### list_features

Browse features with optional node_type filter.

**Request (all features):**
```json
{}
```

**Response (truncated):**
```json
{
  "features": [
    {"name": "book", "kind": "node", "value_type": "str", "description": "✅ book name in Latin (Genesis; Numeri; Reges1; ...)"},
    {"name": "book@am", "kind": "node", "value_type": "str", "description": "✅ book name in amharic (ኣማርኛ)"},
    {"name": "book@ar", "kind": "node", "value_type": "str", "description": "✅ book name in arabic (العَرَبِية)"},
    {"name": "book@bn", "kind": "node", "value_type": "str", "description": "✅ book name in bengali (বাংলা)"},
    {"name": "book@da", "kind": "node", "value_type": "str", "description": "✅ book name in danish (Dansk)"},
    "..."
  ]
}
```

**Request (filtered by node type):**
```json
{"node_types": ["word"]}
```

**Response (truncated):**
```json
{
  "features": [
    {"name": "freq_lex", "kind": "node", "value_type": "int", "description": "✅ frequency of lexemes"},
    {"name": "freq_occ", "kind": "node", "value_type": "int", "description": "✅ frequency of occurrences"},
    {"name": "g_cons", "kind": "node", "value_type": "str", "description": "✅ word consonantal-transliterated (B R>CJT BR> >LHJM ...)"},
    {"name": "g_cons_utf8", "kind": "node", "value_type": "str", "description": "✅ word consonantal-Hebrew (ב ראשׁית ברא אלהים)"},
    {"name": "g_lex", "kind": "node", "value_type": "str", "description": "✅ lexeme pointed-transliterated (B.:- R;>CIJT B.@R@> >:ELOH ...)"},
    {"name": "g_lex_utf8", "kind": "node", "value_type": "str", "description": "✅ lexeme pointed-Hebrew (בְּ רֵאשִׁית בָּרָא אֱלֹה)"},
    "..."
  ],
  "node_types": ["word"]
}
```

---

### describe_feature

Get detailed info about a feature with sample values.

**Request:**
```json
{"feature": "sp"}
```

**Response:**
```json
{
  "name": "sp",
  "kind": "node",
  "value_type": "str",
  "description": "✅ part-of-speech (art; verb; subs; nmpr, ...)",
  "node_types": ["lex", "word"],
  "unique_values": 14,
  "sample_values": [
    {"value": "subs", "count": 125583},
    {"value": "verb", "count": 75451},
    {"value": "prep", "count": 73298},
    {"value": "conj", "count": 62737},
    {"value": "nmpr", "count": 35607},
    {"value": "art", "count": 30387},
    {"value": "adjv", "count": 10141},
    {"value": "nega", "count": 6059},
    {"value": "prps", "count": 5035},
    {"value": "advb", "count": 4603},
    {"value": "prde", "count": 2678},
    {"value": "intj", "count": 1912},
    {"value": "inrg", "count": 1303},
    {"value": "prin", "count": 1026}
  ]
}
```

---

### get_text_formats

Get text encoding samples (cached).

**Request:**
```json
{}
```

**Response (truncated samples):**
```json
{
  "description": "Shows how text values are encoded in this corpus. Samples provide exhaustive character coverage for understanding the relationship between original script and transliterated forms.",
  "formats": [
    {
      "name": "lex-full",
      "original_script": "{g_lex_utf8} ",
      "transliteration": "{g_lex} ",
      "samples": [
        {"original": "בְּ", "transliterated": "B.:-"},
        {"original": "רֵאשִׁית", "transliterated": "R;>CIJT"},
        {"original": "בָּרָא", "transliterated": "B.@R@>"},
        {"original": "אֱלֹה", "transliterated": ">:ELOH"},
        {"original": "הַ", "transliterated": "HA-"},
        {"original": "שָּׁמַי", "transliterated": "C.@MAJ"},
        {"original": "וְ", "transliterated": "W:-"},
        {"original": "אָרֶץ", "transliterated": ">@REY"},
        {"original": "חֹשֶׁךְ", "transliterated": "XOCEK:"},
        {"original": "עַל", "transliterated": "<AL"},
        {"original": "פְּן", "transliterated": "P.:N"},
        {"original": "תְהֹום", "transliterated": "T:HOWM"},
        {"original": "רַחֶף", "transliterated": "RAXEP"},
        {"original": "כִּי", "transliterated": "K.IJ"},
        {"original": "טֹוב", "transliterated": "VOWB"},
        {"original": "בְדֵּל", "transliterated": "B:D.;L"},
        {"original": "קְרָא", "transliterated": "Q:R@>"},
        {"original": "עַשׂ", "transliterated": "<AF"},
        {"original": "אֲשֶׁר", "transliterated": ">:ACER"},
        {"original": "שֵׁנִי", "transliterated": "C;NIJ"},
        {"original": "זְרִיעַ", "transliterated": "Z:RIJ<A"},
        {"original": "וצֵא", "transliterated": "WY;>"},
        {"original": "גְּדֹל", "transliterated": "G.:DOL"},
        {"original": "כֻלּ", "transliterated": "KUL."},
        {"original": "סֹּבֵב", "transliterated": "S.OB;B"},
        {"original": "לֻקֳח", "transliterated": "LUQ:@X"},
        {"original": "תּוּבַל קַיִן", "transliterated": "T.W.BAL_QAJIN"},
        {"original": "כָּֿל", "transliterated": "K.,@L"}
      ],
      "unique_characters": 43,
      "total_samples": 28
    },
    {
      "name": "lex-plain",
      "original_script": "{lex_utf8} ",
      "transliteration": "{lex} ",
      "samples": [
        {"original": "ב", "transliterated": "B"},
        {"original": "ראשׁית", "transliterated": "R>CJT/"},
        {"original": "אלהים", "transliterated": ">LHJM/"},
        {"original": "שׁמים", "transliterated": "CMJM/"},
        {"original": "ו", "transliterated": "W"},
        {"original": "ארץ", "transliterated": ">RY/"},
        {"original": "חשׁך", "transliterated": "XCK/"},
        {"original": "על", "transliterated": "<L"},
        {"original": "פנה", "transliterated": "PNH/"},
        {"original": "רחף", "transliterated": "RXP["},
        {"original": "כי", "transliterated": "KJ"},
        {"original": "טוב", "transliterated": "VWB["},
        {"original": "בדל", "transliterated": "BDL["},
        {"original": "בין", "transliterated": "BJN/"},
        {"original": "קרא", "transliterated": "QR>["},
        {"original": "עשׂה", "transliterated": "<FH["},
        {"original": "זרע", "transliterated": "ZR<["},
        {"original": "יצא", "transliterated": "JY>["},
        {"original": "גדול", "transliterated": "GDWL/"},
        {"original": "סבב", "transliterated": "SBB["},
        {"original": "תובל קין", "transliterated": "TWBL_QJN/"}
      ],
      "unique_characters": 30,
      "total_samples": 21
    },
    {
      "name": "text-full",
      "original_script": "{qere_utf8/g_word_utf8}{qere_trailer_utf8/trailer_utf8}",
      "transliteration": "{qere/g_word}{qere_trailer/trailer}",
      "samples": [
        {"original": "בְּ", "transliterated": "B.:-"},
        {"original": "רֵאשִׁ֖ית", "transliterated": "R;>CI73JT"},
        {"original": "בָּרָ֣א", "transliterated": "B.@R@74>"},
        {"original": "אֱלֹהִ֑ים", "transliterated": ">:ELOHI92JM"},
        {"original": "אֵ֥ת", "transliterated": ">;71T"},
        {"original": "הַ", "transliterated": "HA-"},
        {"original": "שָּׁמַ֖יִם", "transliterated": "C.@MA73JIM"},
        {"original": "וְ", "transliterated": "W:-"},
        {"original": "אָֽרֶץ׃", "transliterated": ">@75REY00"},
        {"original": "אָ֗רֶץ", "transliterated": ">@81REY"},
        {"original": "תֹ֨הוּ֙", "transliterated": "TO33HW.03"},
        {"original": "בֹ֔הוּ", "transliterated": "BO80HW."},
        {"original": "חֹ֖שֶׁךְ", "transliterated": "XO73CEK:"},
        {"original": "עַל־", "transliterated": "<AL&"},
        {"original": "פְּנֵ֣י", "transliterated": "P.:N;74J"},
        {"original": "יַּ֧רְא", "transliterated": "J.A94R:>"},
        {"original": "אֱלֹהִ֛ים", "transliterated": ">:ELOHI91JM"},
        {"original": "כִּי־", "transliterated": "K.IJ&"},
        {"original": "טֹ֑וב", "transliterated": "VO92WB"},
        {"original": "יַּבְדֵּ֣ל", "transliterated": "J.AB:D.;74L"},
        {"original": "בֵּ֥ין", "transliterated": "B.;71JN"},
        {"original": "יִּקְרָ֨א", "transliterated": "J.IQ:R@63>"},
        {"original": "אֱלֹהִ֤ים׀", "transliterated": ">:ELOHI70JM05"},
        {"original": "אֶחָֽד׃ פ", "transliterated": ">EX@75D00_P"},
        {"original": "יַּ֣עַשׂ", "transliterated": "J.A74<AF"},
        {"original": "אֱלֹהִים֮", "transliterated": ">:ELOHIJM02"},
        {"original": "רָקִיעַ֒", "transliterated": "R@QIJ<A01"},
        {"original": "אֲשֶׁר֙", "transliterated": ">:ACER03"},
        {"original": "מַּ֜יִם", "transliterated": "M.A61JIM"},
        {"original": "עֵ֚שֶׂב", "transliterated": "10<;FEB"},
        {"original": "מַזְרִ֣יעַ", "transliterated": "MAZ:RI74J<A"},
        {"original": "פְּרִ֞י", "transliterated": "P.:RI62J"},
        {"original": "תֹּוצֵ֨א", "transliterated": "T.OWY;63>"},
        {"original": "דֶּ֠שֶׁא", "transliterated": "14D.ECE>"},
        {"original": "הַבְדִּ֕יל", "transliterated": "HAB:D.I85JL"},
        {"original": "גְּדֹלִ֑ים", "transliterated": "G.:DOLI92JM"},
        {"original": "עֹוף֙", "transliterated": "<OWP03"},
        {"original": "רֹמֶ֡שֶׂת", "transliterated": "ROME83FET"},
        {"original": "אֲשֶׁר֩", "transliterated": ">:ACER04"},
        {"original": "כִבְשֻׁ֑הָ", "transliterated": "KIB:CU92H@"},
        {"original": "סֹּבֵ֗ב", "transliterated": "S.OB;81B"},
        {"original": "לֻֽקֳחָה־", "transliterated": "LU45Q:@X@H&"},
        {"original": "בֵינֶֽיׄךָ׃", "transliterated": "B;JNE75J52K@00"},
        {"original": "יִּתְמַהְמָ֓הּ׀", "transliterated": "J.IT:MAH:M@65H.05"},
        {"original": "יּוּשַׂ֤ם", "transliterated": "J.W.FA70m"},
        {"original": "לֹ֦ו", "transliterated": "LO72W"},
        {"original": "יִֽשְׁתַּחֲו֤וּ", "transliterated": "JI45C:T.AX:AW70W."},
        {"original": "תִּֿרְצָֽ֖ח׃ ס", "transliterated": "T.,IR:Y@7375X00_S"},
        {"original": "פֶּ֝תַח", "transliterated": "11P.ETAX"},
        {"original": "אַלְפַּ֪יִם", "transliterated": ">AL:P.A93JIM"},
        {"original": "אַמָּ֟ה", "transliterated": ">AM.@84H"},
        {"original": "אָנֹ֘כִי֮", "transliterated": ">@NO82KIJ02"},
        {"original": "עֲצַ֢ת", "transliterated": "<:AYA97T"},
        {"original": "רְשָׁ֫עִ֥ים", "transliterated": "R:C@60<I71JM"},
        {"original": "חַ֭טָּאִים", "transliterated": "13XAV.@>IJM"},
        {"original": "יִתֵּ֬ן", "transliterated": "JIT.;64N"},
        {"original": "לׅׄוּלֵׅ֗ׄאׅׄ", "transliterated": "L5253W.L;815253>5253"},
        {"original": "יִנֹּ97ון", "transliterated": "JIN.O97Wn"},
        {"original": "שְּׁחִיתֹותָֽם׃ ׆", "transliterated": "C.:XIJTOWT@75M00_N"}
      ],
      "unique_characters": 84,
      "total_samples": 59
    },
    {
      "name": "text-full-ketiv",
      "original_script": "{g_word_utf8}{trailer_utf8}",
      "transliteration": "{g_word}{trailer}",
      "samples": [
        {"original": "בְּ", "transliterated": "B.:-"},
        {"original": "רֵאשִׁ֖ית", "transliterated": "R;>CI73JT"},
        {"original": "בָּרָ֣א", "transliterated": "B.@R@74>"},
        {"original": "אֱלֹהִ֑ים", "transliterated": ">:ELOHI92JM"},
        {"original": "אֵ֥ת", "transliterated": ">;71T"},
        {"original": "הַ", "transliterated": "HA-"},
        {"original": "שָּׁמַ֖יִם", "transliterated": "C.@MA73JIM"},
        {"original": "וְ", "transliterated": "W:-"},
        {"original": "אָֽרֶץ׃", "transliterated": ">@75REY00"},
        {"original": "אָ֗רֶץ", "transliterated": ">@81REY"},
        {"original": "תֹ֨הוּ֙", "transliterated": "TO33HW.03"},
        {"original": "בֹ֔הוּ", "transliterated": "BO80HW."},
        {"original": "חֹ֖שֶׁךְ", "transliterated": "XO73CEK:"},
        {"original": "עַל־", "transliterated": "<AL&"},
        {"original": "פְּנֵ֣י", "transliterated": "P.:N;74J"},
        {"original": "יַּ֧רְא", "transliterated": "J.A94R:>"},
        {"original": "אֱלֹהִ֛ים", "transliterated": ">:ELOHI91JM"},
        {"original": "כִּי־", "transliterated": "K.IJ&"},
        {"original": "טֹ֑וב", "transliterated": "VO92WB"},
        {"original": "יַּבְדֵּ֣ל", "transliterated": "J.AB:D.;74L"},
        {"original": "בֵּ֥ין", "transliterated": "B.;71JN"},
        {"original": "יִּקְרָ֨א", "transliterated": "J.IQ:R@63>"},
        {"original": "אֱלֹהִ֤ים׀", "transliterated": ">:ELOHI70JM05"},
        {"original": "אֶחָֽד׃ פ", "transliterated": ">EX@75D00_P"},
        {"original": "יַּ֣עַשׂ", "transliterated": "J.A74<AF"},
        {"original": "אֱלֹהִים֮", "transliterated": ">:ELOHIJM02"},
        {"original": "רָקִיעַ֒", "transliterated": "R@QIJ<A01"},
        {"original": "אֲשֶׁר֙", "transliterated": ">:ACER03"},
        {"original": "מַּ֜יִם", "transliterated": "M.A61JIM"},
        {"original": "עֵ֚שֶׂב", "transliterated": "10<;FEB"},
        {"original": "מַזְרִ֣יעַ", "transliterated": "MAZ:RI74J<A"},
        {"original": "פְּרִ֞י", "transliterated": "P.:RI62J"},
        {"original": "תֹּוצֵ֨א", "transliterated": "T.OWY;63>"},
        {"original": "דֶּ֠שֶׁא", "transliterated": "14D.ECE>"},
        {"original": "הַבְדִּ֕יל", "transliterated": "HAB:D.I85JL"},
        {"original": "גְּדֹלִ֑ים", "transliterated": "G.:DOLI92JM"},
        {"original": "עֹוף֙", "transliterated": "<OWP03"},
        {"original": "רֹמֶ֡שֶׂת", "transliterated": "ROME83FET"},
        {"original": "אֲשֶׁר֩", "transliterated": ">:ACER04"},
        {"original": "כִבְשֻׁ֑הָ", "transliterated": "KIB:CU92H@"},
        {"original": "סֹּבֵ֗ב", "transliterated": "S.OB;81B"},
        {"original": "לֻֽקֳחָה־", "transliterated": "LU45Q:@X@H&"},
        {"original": "בֵינֶֽיׄךָ׃", "transliterated": "B;JNE75J52K@00"},
        {"original": "יִּתְמַהְמָ֓הּ׀", "transliterated": "J.IT:MAH:M@65H.05"},
        {"original": "לֹ֦ו", "transliterated": "LO72W"},
        {"original": "תִּֿרְצָֽ֖ח׃ ס", "transliterated": "T.,IR:Y@7375X00_S"},
        {"original": "פֶּ֝תַח", "transliterated": "11P.ETAX"},
        {"original": "אַלְפַּ֪יִם", "transliterated": ">AL:P.A93JIM"},
        {"original": "אַמָּ֟ה", "transliterated": ">AM.@84H"},
        {"original": "אָנֹ֘כִי֮", "transliterated": ">@NO82KIJ02"},
        {"original": "עֲצַ֢ת", "transliterated": "<:AYA97T"},
        {"original": "רְשָׁ֫עִ֥ים", "transliterated": "R:C@60<I71JM"},
        {"original": "חַ֭טָּאִים", "transliterated": "13XAV.@>IJM"},
        {"original": "יִתֵּ֬ן", "transliterated": "JIT.;64N"},
        {"original": "לׅׄוּלֵׅ֗ׄאׅׄ", "transliterated": "L5253W.L;815253>5253"},
        {"original": "שְּׁחִיתֹותָֽם׃ ׆", "transliterated": "C.:XIJTOWT@75M00_N"}
      ],
      "unique_characters": 80,
      "total_samples": 56
    },
    {
      "name": "text-plain",
      "original_script": "{g_cons_utf8}{trailer_utf8}",
      "transliteration": "{g_cons}{trailer}",
      "samples": [
        {"original": "ב", "transliterated": "B"},
        {"original": "ראשׁית", "transliterated": "R>CJT"},
        {"original": "אלהים", "transliterated": ">LHJM"},
        {"original": "שׁמים", "transliterated": "CMJM"},
        {"original": "ו", "transliterated": "W"},
        {"original": "ארץ׃", "transliterated": ">RY00"},
        {"original": "חשׁך", "transliterated": "XCK"},
        {"original": "על־", "transliterated": "<L&"},
        {"original": "פני", "transliterated": "PNJ"},
        {"original": "כי־", "transliterated": "KJ&"},
        {"original": "טוב", "transliterated": "VWB"},
        {"original": "יבדל", "transliterated": "JBDL"},
        {"original": "בין", "transliterated": "BJN"},
        {"original": "יקרא", "transliterated": "JQR>"},
        {"original": "אלהים׀", "transliterated": ">LHJM05"},
        {"original": "אחד׃ פ", "transliterated": ">XD00_P"},
        {"original": "יעשׂ", "transliterated": "J<F"},
        {"original": "מזריע", "transliterated": "MZRJ<"},
        {"original": "תוצא", "transliterated": "TWY>"},
        {"original": "גדלים", "transliterated": "GDLJM"},
        {"original": "עוף", "transliterated": "<WP"},
        {"original": "סבב", "transliterated": "SBB"},
        {"original": "שׁחיתותם׃ ׆", "transliterated": "CXJTWTM00_N"}
      ],
      "unique_characters": 34,
      "total_samples": 23
    }
  ]
}
```

---

## Search Tools

### search_syntax_guide

Get search syntax documentation (section-based).

**Request (default - get overview):**
```json
{}
```

**Response:**
```json
{
  "summary": "Templates: node_type feature=value. Indentation=containment. Relations: < > <: :> =: for ordering/position.",
  "sections": ["basics", "structure", "relations", "quantifiers", "examples"],
  "hint": "Call with section='relations' to get detailed info on a specific section"
}
```

**Request (specific section):**
```json
{"section": "relations"}
```

**Response:**
```json
{
  "section": "relations",
  "content": "## Relations\n\n### Default Relations\n- Indented items are contained by their parent (`:` relation)\n- Items at same level follow each other in order\n\n### Explicit Relations\n```\nclause\n  word sp=verb\n  < word sp=noun             # noun comes BEFORE verb\n  > word sp=adj              # adjective comes AFTER verb\n  <: word sp=prep            # preposition immediately before verb\n  :> word sp=adv             # adverb immediately after verb\n```\n\n### Relation Operators\n- `<` - comes before (canonical node ordering)\n- `>` - comes after (canonical node ordering)\n- `<:` - immediately before (adjacent)\n- `:>` - immediately after (adjacent)\n- `<<` - completely before (slot ordering)\n- `>>` - completely after (slot ordering)\n- `[[` - left embeds right\n- `]]` - left embedded in right\n- `=:` - start at same slot\n- `:=` - end at same slot\n- `::` - start and end at same slot (co-extensive)\n- `==` - occupy same slots"
}
```

---

### search (return_type='count')

Get total count of matches.

**Request:**
```json
{
  "template": "word sp=verb vt=perf",
  "return_type": "count"
}
```

**Response:**
```json
{
  "total_count": 10000,
  "template": "word sp=verb vt=perf"
}
```

---

### search (return_type='results')

Get paginated results with cursor.

**Request:**
```json
{
  "template": "word sp=verb vt=perf",
  "return_type": "results",
  "limit": 3
}
```

**Response:**
```json
{
  "results": [
    [{"node": 3, "otype": "word", "text": "בָּרָ֣א ", "section_ref": "Genesis 1:1"}],
    [{"node": 15, "otype": "word", "text": "הָיְתָ֥ה ", "section_ref": "Genesis 1:2"}],
    [{"node": 47, "otype": "word", "text": "טֹ֑וב ", "section_ref": "Genesis 1:4"}]
  ],
  "total_count": 10000,
  "template": "word sp=verb vt=perf",
  "cursor": {
    "id": "3ab73d31-2b49-48bc-95a6-c953586ce951",
    "offset": 0,
    "limit": 3,
    "has_more": true,
    "expires_at": 1767730334.3732748
  }
}
```

---

### search (return_type='statistics')

Get feature distributions across results.

**Request:**
```json
{
  "template": "word sp=verb",
  "return_type": "statistics",
  "aggregate_features": ["vt", "vs"],
  "top_n": 5
}
```

**Response:**
```json
{
  "total_count": 10000,
  "template": "word sp=verb",
  "nodes": {
    "0_word": {
      "type": "word",
      "count": 10000,
      "distributions": {
        "vt": [
          {"value": "wayq", "count": 3139},
          {"value": "perf", "count": 2673},
          {"value": "impf", "count": 1829},
          {"value": "infc", "count": 864},
          {"value": "ptca", "count": 706}
        ],
        "vs": [
          {"value": "qal", "count": 7120},
          {"value": "hif", "count": 1114},
          {"value": "piel", "count": 989},
          {"value": "nif", "count": 498},
          {"value": "hof", "count": 97}
        ]
      }
    }
  }
}
```

---

### search (return_type='passages')

Get formatted text passages.

**Request:**
```json
{
  "template": "word lex=BR>[",
  "return_type": "passages",
  "limit": 3
}
```

**Response:**
```json
{
  "total_count": 48,
  "template": "word lex=BR>[",
  "passages": [
    {"reference": "Genesis 1:1", "text": "בָּרָ֣א ", "node": 3, "type": "word"},
    {"reference": "Genesis 1:21", "text": "יִּבְרָ֣א ", "node": 381, "type": "word"},
    {"reference": "Genesis 1:27", "text": "יִּבְרָ֨א ", "node": 535, "type": "word"}
  ],
  "has_more": true
}
```

---

### search_continue

Continue paginated search with cursor.

**Request:**
```json
{
  "cursor_id": "3ab73d31-2b49-48bc-95a6-c953586ce951",
  "offset": 3,
  "limit": 2
}
```

**Response:**
```json
{
  "results": [
    [{"node": 538, "otype": "word", "text": "בָּרָ֥א ", "section_ref": "Genesis 1:27"}],
    [{"node": 540, "otype": "word", "text": "בָּרָ֖א ", "section_ref": "Genesis 1:27"}]
  ],
  "total_count": 10000,
  "template": "word sp=verb vt=perf",
  "cursor": {
    "id": "3ab73d31-2b49-48bc-95a6-c953586ce951",
    "offset": 3,
    "limit": 2,
    "has_more": true,
    "expires_at": 1767730334.3732748
  }
}
```

---

## Data Access Tools

### get_passages

Get text by section references.

**Request:**
```json
{
  "sections": [["Genesis", 1, 1], ["Exodus", 20, 1]]
}
```

**Response:**
```json
{
  "passages": [
    {
      "node": 1414389,
      "otype": "verse",
      "text": "בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ׃ ",
      "section_ref": "Genesis 1:1"
    },
    {
      "node": 1416441,
      "otype": "verse",
      "text": "וַיְדַבֵּ֣ר אֱלֹהִ֔ים אֵ֛ת כָּל־הַדְּבָרִ֥ים הָאֵ֖לֶּה לֵאמֹֽר׃ ס ",
      "section_ref": "Exodus 20:1"
    }
  ],
  "total": 2,
  "found": 2
}
```

**Request (with language code):**
```json
{
  "sections": [["Genesis", 1, 1]],
  "lang": "en"
}
```

Note: The `lang` parameter accepts ISO 639 language codes (e.g., `"en"` for English book names). Available language codes depend on the corpus features (check `list_features()` for `book@<lang>` patterns). Defaults to `"en"`.

---

### get_node_features

Get feature values for specific nodes.

**Request:**
```json
{
  "nodes": [3, 15, 100],
  "features": ["sp", "vt", "lex", "gloss"]
}
```

**Response:**
```json
{
  "nodes": [
    {"node": 3, "type": "word", "sp": "verb", "vt": "perf", "lex": "BR>[", "gloss": "create"},
    {"node": 15, "type": "word", "sp": "verb", "vt": "perf", "lex": "HJH[", "gloss": "be"},
    {"node": 100, "type": "word", "sp": "subs", "vt": "NA", "lex": "RQJ</", "gloss": "firmament"}
  ],
  "features_requested": ["sp", "vt", "lex", "gloss"],
  "total": 3
}
```
