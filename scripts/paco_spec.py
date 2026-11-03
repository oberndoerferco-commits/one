#!/usr/bin/env python3
"""The one-page sheet that goes to the producer with the logo files."""
import argparse
import pymupdf

MM = 72.0 / 25.4
H0, GAP = 0.248, 0.88          # thinnest stroke and tightest gap, at 50 mm


def sheet(out, details, scratch):
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
    txt(20, 28, 'What the artwork can hold, and at what size.', 8.5, (.35, .35, .35))

    y = 38
    txt(20, y, 'The smallest feature depends only on the size', 10, font='hebo'); y += 7
    y = para(y, [
        'At 50 mm the thinnest stroke is 0.25 mm and the tightest gap, between the O and the bar under',
        'it, is 0.88 mm. Making the strokes heavier does not help on its own: every 0.1 mm added to a',
        'stroke is 0.1 mm taken from the gap beside it, because both edges move. The two meet in the',
        'middle, so the best this logo can do is half of what the stroke and the gap add up to, which',
        'scales to one millimetre for every 88 mm of width:'])

    y += 3
    for w in (50, 60, 70, 80, 88.7, 100):
        m = (H0 + GAP) / 2 * (w / 50.0)
        mark = '     <-  1.00 mm needs 88.7 mm' if abs(m - 1.0) < 0.01 else ''
        txt(30, y, f'{w:5.1f} mm wide', 8.5, (.3, .3, .3))
        txt(62, y, f'smallest feature {m:.2f} mm', 8.5); txt(108, y, mark, 8.5, (.45, .45, .45))
        y += 5.6

    y += 4; rule(y); y += 9
    txt(20, y, 'The O and the bar, at 4x', 10, font='hebo'); y += 5
    x = 20
    for lab, img, sub in details:
        pg.insert_image(pymupdf.Rect(x * MM, (y + 4) * MM, (x + 36) * MM, (y + 28) * MM),
                        filename=img, keep_proportion=True)
        txt(x, y + 2, lab, 7.5, (.2, .2, .2))
        txt(x, y + 32, sub, 7, (.4, .4, .4))
        x += 43
    y += 38

    rule(y); y += 9
    txt(20, y, 'The two files', 10, font='hebo'); y += 8
    txt(70, y, '90 mm', 8.5, font='hebo'); txt(126, y, '50 mm', 8.5, font='hebo'); y += 6
    for a, b, c in [('Thinnest stroke', '1.02 mm', '0.57 mm'),
                    ('O-to-bar gap', '1.02 mm', '0.57 mm'),
                    ('Next tightest gap, C to O', '2.21 mm', '1.23 mm'),
                    ('Shapes / counters', '6 / 12', '6 / 12'),
                    ('Drawing changed?', 'nothing moved', 'nothing moved')]:
        txt(24, y, a, 8.5, (.3, .3, .3)); txt(70, y, b, 8.5); txt(126, y, c, 8.5); y += 5.8

    y += 5; rule(y); y += 9
    txt(20, y, 'Which to use', 10, font='hebo'); y += 7.5
    y = para(y, [
        'If the minimum is 1 mm, the logo must run at 88.7 mm or wider. The 90 mm file does that with',
        'nothing moved: every stroke 1.02 mm, every gap 1.02 mm or more.',
        '',
        'The 50 mm file is the most this logo can give at that size, 0.57 mm. Use it only if the producer',
        'confirms they hold 0.57 mm; otherwise work to the width in the table.',
        '',
        'In both, the O is joined to the bar by a stem of the bar\'s own weight, so they deboss as one',
        'piece. The slivers at the diamond\'s inner facets and the crook of the ampersand still taper',
        'below these figures; they are wedges, they measure the same as supplied, and they round off.'])
    doc.save(out)
    doc[0].get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2)).save(scratch)
    return y


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--scratch', required=True)
    a.add_argument('--out', default='assets/paco/paco-bold-spec.pdf')
    o = a.parse_args()
    S = o.scratch.rstrip('/') + '/'
    print('bottom at', sheet(o.out, [
        ('as supplied', S + 'e_orig.png', 'stroke 0.25 mm,  gap 0.88 mm'),
        ('90 mm file', S + 'e_90.png', 'stroke 1.02 mm,  gap 1.02 mm'),
        ('50 mm file', S + 'e_50.png', 'stroke 0.57 mm,  gap 0.57 mm')],
        S + 'spec3.png'))
