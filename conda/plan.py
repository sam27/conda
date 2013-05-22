from collections import defaultdict

import install
from config import PKGS_DIR
from naming import name_dist
from resolve import Resolve



def print_dists(dists):
    fmt = "    %-27s|%17s"
    print fmt % ('package', 'build')
    print fmt % ('-' * 27, '-' * 17)
    for dist in dists:
        print fmt % tuple(dist.rsplit('-', 1))

def display_actions(actions):
    if actions['FETCH']:
        print "\nThe following packages will be downloaded:\n"
        print_dists(actions['FETCH'])
    if actions['UNLINK']:
        print "\nThe following packages will be UN-linked:\n"
        print_dists(actions['UNLINK'])
    if actions['LINK']:
        print "\nThe following packages will be linked:\n"
        print_dists(actions['LINK'])

def plan_from_actions(actions):
    res = ['# plan',
           'PREFIX %s' % actions['PREFIX']]
    for op in ('FETCH', 'EXTRACT', 'UNLINK', 'LINK',
               'RM_EXTRACTED', 'RM_FETCHED'):
        if not actions[op]:
            continue
        res.append('PRINT %sing packages ...' % op.capitalize())
        if op != 'FETCH':
            res.append('PROGRESS %d' % len(actions[op]))
        for dist in actions[op]:
            res.append('%s %s' % (op, dist))
    return res

def install_actions(prefix, index, specs):
    linked = install.linked(prefix)
    extracted = install.extracted(PKGS_DIR)
    fetched = install.fetched(PKGS_DIR)

    r = Resolve(index)

    must_have = {}
    for fn in r.solve(specs, ['%s.tar.bz2' % d for d in linked]):
        dist = fn[:-8]
        must_have[name_dist(dist)] = dist
    sorted_must_have = sorted(must_have.values())

    actions = defaultdict(list)
    actions['PREFIX'] = prefix
    for dist in sorted_must_have:
        if dist in linked:
            continue
        actions['LINK'].append(dist)
        if dist in extracted:
            continue
        actions['EXTRACT'].append(dist)
        if dist in fetched:
            continue
        actions['FETCH'].append(dist)

    for dist in sorted(linked):
        name = name_dist(dist)
        if name in must_have and dist != must_have[name]:
            actions['UNLINK'].append(dist)

    return actions


if __name__ == '__main__':
    import sys
    import json
    with open('../tests/index.json') as fi:
        index = json.load(fi)
    display_actions(install_actions(sys.prefix, index, ['w3lib']))