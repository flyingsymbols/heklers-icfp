import re
import sys
from pprint import pprint as pp

from collections import defaultdict

label_re    = re.compile('^([a-zA-Z_][a-zA-Z0-9_]+):$')
id_re       = re.compile('^([a-zA-Z_][a-zA-Z0-9_]+)$')
ws_re       = re.compile('\s+')

LABEL_BLACKLIST = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

def main():
    fname = sys.argv[1]

    with open(fname, 'rb') as f:
        lines = list(f)

    label_to_def_i = {}
    label_to_refs_i = defaultdict(list)

    instr_i = 0
    clean_lines = []

    for l in lines:
        if ';' in l:
            l = l[:l.index(';')]

        l = l.strip()
        if not l:
            continue

        label_m = label_re.match(l)
        if label_m:
            label_to_def_i[label_m.group(1)] = instr_i
            continue
        
        l = l.replace(',', ' , ')

        chunks = re.split(ws_re, l)

        id_refs = []

        for thing_i, thing in enumerate(chunks[1:], start=1):
            if id_re.match(thing) and thing not in LABEL_BLACKLIST:
                id_refs.append((thing_i, thing))

        if id_refs:
            label_to_refs_i[instr_i].extend(id_refs)

        clean_lines.append(chunks)
        instr_i += 1

    # pp(list(enumerate(clean_lines)))
    # pp(label_to_def_i)
    # pp(label_to_refs_i)

    out_lines = []

    for line_ind, line_chunks in enumerate(clean_lines):
        if line_ind in label_to_refs_i:
            # need to fixup
            copy_line = list(line_chunks)

            for ref_ind, ref_str in label_to_refs_i[line_ind]:
                assert copy_line[ref_ind] == ref_str

                copy_line[ref_ind] = str(label_to_def_i[ref_str])

            out_line = ' '.join(copy_line)
        else:
            out_line = ' '.join(line_chunks)

        out_line = out_line.replace(' , ', ', ')
        out_lines.append(out_line)
    
    print '\n'.join(out_lines)

if __name__ == '__main__':
    main()
        


