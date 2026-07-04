from pathlib import Path

files = {
    'yaml': Path('防DNS泄露.yaml'),
    'js': Path('防DNS泄露.js'),
    'stash': Path('stash.stoverride'),
}
text = {k: p.read_text(encoding='utf-8') for k, p in files.items()}
base = 'https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo'
providers = {
    'twitter': ('Meta / X', 'geosite'),
    'facebook': ('Meta / X', 'geosite'),
    'steam': ('游戏平台', 'geosite'),
    'category-games': ('游戏平台', 'geosite'),
}

# YAML providers
if '  twitter:\n    <<: *meta_domain' not in text['yaml']:
    insert = ''
    for name, (_, kind) in providers.items():
        insert += f'  {name}:\n    <<: *meta_domain\n    url: "{base}/{kind}/{name}.mrs"\n    path: "./ruleset/metacubex/{name}.mrs"\n'
    anchor = '    path: "./ruleset/metacubex/telegramcidr.mrs"\n'
    text['yaml'] = text['yaml'].replace(anchor, anchor + insert, 1)

# JS providers
if '  twitter: {\n    ...META_DOMAIN_PROVIDER' not in text['js']:
    insert = ''
    for name, (_, kind) in providers.items():
        q = f'"{name}"' if '-' in name else name
        insert += f'  {q}: {{\n    ...META_DOMAIN_PROVIDER,\n    url: "{base}/{kind}/{name}.mrs",\n    path: "./ruleset/metacubex/{name}.mrs",\n  }},\n'
    anchor = '    path: "./ruleset/metacubex/telegramcidr.mrs",\n  },\n'
    text['js'] = text['js'].replace(anchor, anchor + insert, 1)

# Stash providers
if '  twitter:\n    type: http' not in text['stash']:
    insert = ''
    for name, (_, kind) in providers.items():
        insert += f'  {name}:\n    type: http\n    behavior: domain\n    format: mrs\n    interval: 86400\n    url: {base}/{kind}/{name}.mrs\n    path: ./ruleset/metacubex/{name}.mrs\n'
    anchor = '    path: ./ruleset/metacubex/telegramcidr.mrs\n'
    text['stash'] = text['stash'].replace(anchor, anchor + insert, 1)

# Rules
rule_pairs = [
    ('RULE-SET,twitter,Meta / X', 'DOMAIN-SUFFIX,whatsapp.net,Meta / X'),
    ('RULE-SET,facebook,Meta / X', 'RULE-SET,twitter,Meta / X'),
    ('RULE-SET,steam,游戏平台', 'DOMAIN-SUFFIX,ea.com,游戏平台'),
    ('RULE-SET,category-games,游戏平台', 'RULE-SET,steam,游戏平台'),
]
for key in ('yaml', 'js', 'stash'):
    quoted = key == 'yaml'
    pref = '  - ' if key in ('yaml', 'stash') else ''
    for rule, after in rule_pairs:
        if rule in text[key]:
            continue
        old_line = f'{pref}"{after}"' if quoted else f'{pref}{after}'
        new_line = f'{pref}"{rule}"' if quoted else f'{pref}{rule}'
        text[key] = text[key].replace(old_line, old_line + '\n' + new_line, 1)

for key, value in text.items():
    for must in ['twitter', 'facebook', 'steam', 'category-games', 'RULE-SET,twitter,Meta / X', 'RULE-SET,facebook,Meta / X', 'RULE-SET,steam,游戏平台', 'RULE-SET,category-games,游戏平台']:
        if must not in value:
            raise SystemExit(f'{key} missing {must}')

for k, p in files.items():
    p.write_text(text[k], encoding='utf-8')
