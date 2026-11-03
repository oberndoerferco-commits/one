#!/usr/bin/env python3
"""The one-page sheet that goes to the producer with the logo files."""
import argparse
import pymupdf

MM = 72.0 / 25.4


def sheet(out, details, numbers, scratch):
    doc = pymupdf.open(); pg = doc.new_page(width=210 * MM, height=297 * MM)

    def txt(x, y, s, size=8.5, col=(0, 0, 0), font='helv'):
        pg.insert_text((x * MM, y * MM), s, fontsize=size, color=col, fontname=font)

    def rule(y):
        pg.draw_line(pymupdf.Point(20 * MM, y * MM), pymupdf.Point(190 * MM, y * MM),
                     color=(.78, .78, .78), width=.5)

    def para(y, lines, x=24, lead=5.0):
        for l in lines:
            if l:
                txt(x, y, l, 8.5, (.25, .25, .25))
            y += lead if l else lead * 0.7
        return y

    txt(20, 21, 'PA & CO  -  logo for debossing', 15, font='hebo')
    txt(20, 28, 'Every stroke raised to 1 mm, and the O-to-bar junction kept open.',
        8.5, (.35, .35, .35))

    y = 38
    txt(20, y, 'The two constraints', 10, font='hebo'); y += 7
    y = para(y, [
        'The thinnest stroke in the artwork is 0.26 mm. Raising it to 1 mm adds 0.37 mm to every edge.',
        '',
        'The bar sits 0.88 mm below the bowl of the O. That gap is already under 1 mm, and bolding takes',
        '0.75 mm out of it, leaving 0.13 mm, which fills in and reads as a blob. The gap cannot reach',
        '1 mm at 50 mm by any amount of bolding, because it does not start there. Either the bar moves',
        'down, or the logo runs bigger. Both are drawn below.'])

    y += 4; rule(y); y += 9
    txt(20, y, 'The junction, at 4x', 10, font='hebo'); y += 5
    x = 20
    for lab, img, sub in details:
        pg.insert_image(pymupdf.Rect(x * MM, (y + 4) * MM, (x + 36) * MM, (y + 30) * MM),
                        filename=img, keep_proportion=True)
        txt(x, y + 2, lab, 7.5, (.2, .2, .2))
        txt(x, y + 34, sub, 7, (.4, .4, .4))
        x += 43
    y += 40

    rule(y); y += 9
    txt(20, y, 'Two files, pick one', 10, font='hebo'); y += 8
    txt(62, y, 'A  -  50 mm wide', 8.5, font='hebo')
    txt(122, y, 'B  -  90 mm wide', 8.5, font='hebo'); y += 6
    for a, b, c in numbers:
        txt(24, y, a, 8.5, (.3, .3, .3)); txt(62, y, b, 8.5); txt(122, y, c, 8.5)
        y += 5.8

    y += 5; rule(y); y += 9
    txt(20, y, 'Which to use', 10, font='hebo'); y += 7.5
    y = para(y, [
        'B is the better drawing. Nothing is moved, and it keeps far more of the thick-to-thin contrast',
        'the logo is built on. Use it wherever the logo can run at 90 mm.',
        '',
        'A is for 50 mm. It holds 1 mm everywhere, but the bar sits 0.95 mm lower to keep the junction',
        'open, and taking a 0.26 mm hairline to 1 mm at this size flattens the contrast.',
        '',
        'Both keep the O joined to the bar, so each debosses as a single piece.',
        '',
        'Three places still taper below 1 mm: the two slivers where the diamond\'s inner facets meet its',
        'point, and the crook of the ampersand. These are wedges that narrow to nothing, not channels,',
        'they measure the same in the artwork as supplied, and they will simply round off a little.',
        '',
        'If the supplier can hold finer than 1 mm, both files can be redrawn lighter, which costs less of',
        'the contrast and, for A, moves the bar less.'])
    doc.save(out)
    doc[0].get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2)).save(scratch)
    return y


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--scratch', required=True)
    a.add_argument('--out', default='assets/paco/paco-bold-spec.pdf')
    a.add_argument('--b-gap', default='1.04 mm')
    o = a.parse_args()
    S = o.scratch.rstrip('/') + '/'
    details = [('as supplied', S + 'd_orig.png', 'gap 0.88 mm'),
               ('A:  bar moved down 0.95 mm', S + 'd_A.png', 'gap 1.03 mm'),
               ('B:  at 90 mm, nothing moved', S + 'd_B.png', 'gap ' + o.b_gap)]
    numbers = [('Thinnest stroke', '1.03 mm', '1.00 mm'),
               ('Heaviest stroke', '2.83 mm', '4.20 mm'),
               ('Thick-to-thin contrast', '2.7 : 1', '4.2 : 1'),
               ('   as supplied', '7.9 : 1', '7.9 : 1'),
               ('O-to-bar gap', '1.03 mm', o.b_gap),
               ('Shapes / counters', '6 / 12', '6 / 12'),
               ('Drawing changed?', 'bar lowered 0.95 mm', 'nothing moved'),
               ('Overall size', '50.0 x 35.6 mm', '90.0 x 61.9 mm')]
    print('bottom at', sheet(o.out, details, numbers, S + 'spec2.png'))
