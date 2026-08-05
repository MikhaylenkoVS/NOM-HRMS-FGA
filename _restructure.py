import os

# Directory restructure
moves = [
    ('spectrum', 'domain/spectrum'), ('molecule', 'domain/molecule'), ('atoms', 'domain/atoms'),
    ('_fragment_data', 'chemistry/_fragment_data'), ('fragments', 'chemistry/fragments'),
    ('fragment_combinations', 'chemistry/fragment_combinations'), ('rdkit_bridge', 'chemistry/rdkit_bridge'),
    ('raw_bridge', 'io/raw_bridge'), ('raw_thermo_adapter', 'io/raw_thermo_adapter'), ('mzml_bridge', 'io/mzml_bridge'),
]
for d in ['domain', 'chemistry', 'io']:
    os.makedirs(f'src/core/{d}', exist_ok=True)
    if not os.path.exists(f'src/core/{d}/__init__.py'):
        open(f'src/core/{d}/__init__.py', 'w').close()

for src, dst in moves:
    os.rename(f'src/core/{src}.py', f'src/core/{dst}.py')

# Import replacements: old -> new
imap = {}
for name in ['spectrum','molecule','atoms']:
    for fmt in ['from .%s import', 'from src.core.%s import']:
        imap[fmt % name] = fmt.replace('%s','domain.%s') % name
for name in ['_fragment_data','fragments','fragment_combinations','rdkit_bridge']:
    for fmt in ['from .%s import', 'from src.core.%s import']:
        imap[fmt % name] = fmt.replace('%s','chemistry.%s') % name
for name in ['raw_bridge','raw_thermo_adapter','mzml_bridge']:
    for fmt in ['from .%s import', 'from src.core.%s import']:
        imap[fmt % name] = fmt.replace('%s','io.%s') % name

# Update all Python files
for root, dirs, files in os.walk('src'):
    for fn in files:
        if not fn.endswith('.py'): continue
        fp = os.path.join(root, fn)
        c = open(fp, encoding='utf-8').read()
        nc = c
        for o, n in imap.items():
            nc = nc.replace(o, n)
        if nc != c:
            open(fp, 'w', encoding='utf-8').write(nc)

# Fix cross-package internal imports
for fp, reps in [
    ('src/core/chemistry/fragments.py', [('from .chemistry._fragment_data', 'from ._fragment_data')]),
    ('src/core/chemistry/fragment_combinations.py', [
        ('from .chemistry.fragments', 'from .fragments'),
        ('from .domain.molecule', 'from ..domain.molecule'),
    ]),
]:
    c = open(fp, encoding='utf-8').read()
    for o, n in reps:
        c = c.replace(o, n)
    open(fp, 'w', encoding='utf-8').write(c)

# Update tests
for root, dirs, files in os.walk('tests'):
    for fn in files:
        if not fn.endswith('.py'): continue
        fp = os.path.join(root, fn)
        c = open(fp, encoding='utf-8').read()
        nc = c
        for o, n in imap.items():
            nc = nc.replace(o, n)
        nc = nc.replace('logger="src.core.rdkit_bridge"', 'logger="src.core.chemistry.rdkit_bridge"')
        nc = nc.replace('import src.core.raw_bridge as', 'import src.core.io.raw_bridge as')
        if nc != c:
            open(fp, 'w', encoding='utf-8').write(nc)

print('Done')
