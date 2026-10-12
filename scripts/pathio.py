#!/usr/bin/env python3
"""PDF and SVG operators for a (start, segments) contour."""


def fmt(v):
    t = ('%.4f' % v).rstrip('0').rstrip('.')
    return t if t not in ('', '-0') else '0'


def ops_of(contour, to):
    st, segs = contour
    x, y = to(st)
    out = ['%s %s m' % (fmt(x), fmt(y))]
    for q in segs:
        if q[0] == 'L':
            x, y = to(q[1])
            out.append('%s %s l' % (fmt(x), fmt(y)))
        else:
            a, b, c = to(q[1]), to(q[2]), to(q[3])
            out.append('%s %s %s %s %s %s c' % (fmt(a[0]), fmt(a[1]), fmt(b[0]),
                                                fmt(b[1]), fmt(c[0]), fmt(c[1])))
    out.append('h')
    return out


def svg_of(contour, to):
    st, segs = contour
    x, y = to(st)
    out = ['M%s %s' % (fmt(x), fmt(y))]
    for q in segs:
        if q[0] == 'L':
            x, y = to(q[1])
            out.append('L%s %s' % (fmt(x), fmt(y)))
        else:
            a, b, c = to(q[1]), to(q[2]), to(q[3])
            out.append('C%s %s %s %s %s %s' % (fmt(a[0]), fmt(a[1]), fmt(b[0]),
                                               fmt(b[1]), fmt(c[0]), fmt(c[1])))
    return ' '.join(out) + ' Z'
