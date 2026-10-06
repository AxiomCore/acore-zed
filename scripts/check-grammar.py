#!/usr/bin/env python3
"""Check compiler-validated starters and Zed queries with the Acore parser."""
from pathlib import Path
import argparse
import json
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--grammar', type=Path, default=root.parent / 'tree-sitter-acore')
parser.add_argument('--examples', type=Path, help='Optional additional .acore corpus directory')
args = parser.parse_args()
grammar = args.grammar.resolve()
rebuilt = False

def parse_source(path, edits=()):
    global rebuilt
    command = ['tree-sitter', 'parse', '--no-ranges', str(path)]
    if not rebuilt:
        command.append('--rebuild')
        rebuilt = True
    if edits:
        command.extend(['--edits', *edits])
    result = subprocess.run(command, cwd=grammar,
                            capture_output=True, text=True)
    return result.returncode, result.stdout

def assert_parsed(path, name=None):
    status, tree = parse_source(path)
    errors = [line.strip() for line in tree.splitlines() if 'ERROR' in line or 'MISSING' in line]
    assert status == 0, f'{name or path}: parse error: {"; ".join(errors[:5]) or tree[-500:]}'
    return tree

def query_captures(query, path):
    result = subprocess.run(['tree-sitter', 'query', '--captures', str(query), str(path)],
                            cwd=grammar, capture_output=True, text=True)
    assert result.returncode == 0, f'{query.name}: {result.stderr}'
    return re.findall(r'capture: \d+ - (\S+), start: .*? text: `([^`]*)`',
                      result.stdout, flags=re.DOTALL)

def assert_captures(query_name, path, expected):
    captures = query_captures(root / 'languages/acore' / query_name, path)
    missing = set(expected) - set(captures)
    assert not missing, f'{path.name} / {query_name}: missing captures {sorted(missing)}'

snippets = json.loads((root / 'snippets/acore.json').read_text())
required = [('clazz', 'functionLiteralExpr'), ('profileDeclaration', 'domainDeclaration', 'genericExpr'),
            ('domainFunction', 'domainBinding', 'domainBlock'), ('domainDeclaration', 'implicitMemberExpr')]
checks = []
profile_names = [('Settings', 'enabled', 'label', 'settings', 'transform'),
                 ('Task', 'id', 'title', 'listTasks'),
                 ('editor.ui', 'EditorApp', 'Home', 'count', 'increment', 'View'),
                 ('editor.storage', 'editor', 'app', 'tasks', 'id', 'title')]
profile_keywords = [('class',), ('profile', 'model', 'endpoint'),
                    ('module', 'app', 'route', 'page', 'state', 'action', 'view'),
                    ('module', 'database', 'schema', 'table')]
assert len(snippets) >= 13 and len(required) == len(profile_names) == len(profile_keywords) == 4
with tempfile.TemporaryDirectory(prefix='acore-grammar-') as directory:
    temporary = Path(directory)
    for (name, snippet), nodes, names, keywords in zip(
            snippets.items(), required, profile_names, profile_keywords):
        source = '\n'.join(snippet['body']) + '\n'
        source = re.sub(r'\$\{\d+:([^}]+)\}', r'\1', source)
        source = re.sub(r'\$\d+', '', source)
        path = temporary / (snippet['prefix'] + '.acore')
        path.write_text(source)
        tree = assert_parsed(path, name)
        assert all(re.search(r'\(' + node + r'[\s)]', tree) for node in nodes), f'{name}: missing structural node'
        checks.append(name)
        assert_captures('outline.scm', path, [('name', value) for value in names])
        checks.append(f'{name}: outline captures')
        assert_captures('highlights.scm', path, [('keyword', value) for value in keywords])
        checks.append(f'{name}: keyword highlights')
    for name, snippet in list(snippets.items())[4:]:
        source = '\n'.join(snippet['body']) + '\n'
        source = re.sub(r'\$\{\d+:([^}]+)\}', r'\1', source)
        source = re.sub(r'\$\d+', '', source)
        path = temporary / (snippet['prefix'] + '.acore')
        path.write_text(source)
        assert_parsed(path, name)
        for query in ['highlights.scm', 'outline.scm', 'textobjects.scm']:
            query_captures(root / 'languages/acore' / query, path)
        checks.append(f'{name}: parse and queries')
    path = temporary / 'database-contextual-column.acore'
    path.write_text('table Account { sequence: Pg.Int64(default: 9223372036854775807) }\n')
    assert_parsed(path)
    assert_captures('highlights.scm', path, [('property', 'sequence')])
    checks.append('Database contextual sequence column')
    path = temporary / 'unicode-crlf.acore'
    path.write_bytes('class Unicode { label: String = "Hello é😀" }\r\nvalue = Unicode { }\r\n'.encode())
    assert parse_source(path)[0] == 0
    checks.append('Unicode and CRLF')
    path = temporary / 'recovery.acore'
    path.write_text('label = "unfinished\n')
    assert parse_source(path)[0] != 0, 'unterminated string must have a syntax error'
    path.write_text('label = "finished"\nnext: Int = 1\n')
    assert parse_source(path)[0] == 0
    checks.append('Unfinished-string recovery')
    path = temporary / 'brace-recovery.acore'
    path.write_text('class Settings { enabled: Boolean = true\n')
    assert parse_source(path)[0] != 0, 'unfinished body must retain a syntax error'
    path.write_text('class Settings { enabled: Boolean = true }\nsettings = Settings { enabled = false }\n')
    assert_parsed(path)
    checks.append('Unfinished-body recovery')

    # Real incremental deletion/repair, with byte offsets after multibyte text.
    path = temporary / 'incremental.acore'
    source = 'label = "Hello é😀"\r\nclass Repair { value: Int = 1 }\r\n'
    path.write_bytes(source.encode())
    fresh = assert_parsed(path)
    quote = source.encode().index(b'"', source.encode().index(b'"') + 1)
    brace = source.encode().rindex(b'}')
    for label, offset, delimiter in [('string', quote, '"'), ('body', brace, '}')]:
        deletion = f'{offset} 1 '
        status, broken = parse_source(path, [deletion])
        assert status != 0 and ('ERROR' in broken or 'MISSING' in broken), label
        status, repaired = parse_source(path, [deletion, f'{offset} 0 {delimiter}'])
        assert status == 0 and repaired == fresh, f'{label}: incremental repair differs from fresh tree'
        checks.append(f'Incremental {label} deletion/repair after Unicode with CRLF')

    path = temporary / 'structure.acore'
    path.write_text('/// Structure\nclass Settings {\n  enabled: Boolean = true\n'
                    '  function next(value: Int): Int = value + 1\n}\n'
                    'values = [1, 2]\npage Home { action increment() { count = count + 1 } }\n')
    assert_parsed(path)
    assert_captures('highlights.scm', path, [('comment', '/// Structure'),
                    ('property', 'enabled'), ('constant', 'true'), ('number', '1')])
    checks.append('Literal, property and comment highlights')
    path = temporary / 'nested-catalog.acore'
    path.write_text('model Task { title: Field(type: String) }\n'
                    'endpoint get(method: GET,path: "/") { response(type: String) }\n'
                    'backfill = 1\nlabel = "Field(type: String)"\n')
    assert_parsed(path)
    assert_captures('highlights.scm', path, [('keyword', 'Field'), ('keyword', 'response')])
    captures = query_captures(root / 'languages/acore/highlights.scm', path)
    assert ('keyword', 'backfill') not in captures, 'contextual forms must not reserve ordinary binding names'
    checks.append('Nested catalog calls and ordinary binding/string exclusions')
    path = temporary / 'structure.acore'
    assert_captures('textobjects.scm', path, [('function.around', 'function next(value: Int): Int = value + 1'),
                    ('function.around', 'action increment() { count = count + 1 }')])
    objects = query_captures(root / 'languages/acore/textobjects.scm', path)
    assert {'class.around', 'class.inside', 'function.inside'} <= {kind for kind, _ in objects}
    checks.append('Class and function text objects')
    assert_captures('brackets.scm', path, [('open', '{'), ('close', '}'),
                    ('open', '['), ('close', ']'), ('open', '('), ('close', ')')])
    checks.append('Brace, list and argument bracket captures')
    indent = query_captures(root / 'languages/acore/indents.scm', path)
    assert {'indent', 'end', 'outdent'} <= {kind for kind, _ in indent}
    checks.append('Body indentation and closing-delimiter captures')

    path = temporary / 'style-quotes.acore'
    path.write_text('styles { .title { content: "{quoted}"; color: #123456 } }\n')
    assert parse_source(path)[0] == 0
    checks.append('Style braces inside quoted text')
    assert_captures('injections.scm', path,
                    [('injection.content', ' .title { content: "{quoted}"; color: #123456 } ')])
    checks.append('CSS injection content')
    for query in sorted((root / 'languages/acore').glob('*.scm')):
        result = subprocess.run(['tree-sitter', 'query', str(query), str(path)],
                                cwd=grammar, capture_output=True, text=True)
        assert result.returncode == 0, f'{query.name}: {result.stderr}'
        checks.append(query.name)
if args.examples:
    for path in sorted(args.examples.resolve().rglob('*.acore')):
        assert_parsed(path)
        checks.append(str(path.relative_to(args.examples.resolve())))
print(json.dumps({'passed': len(checks), 'checks': checks}, indent=2))
