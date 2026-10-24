import { describe, it, expect } from 'vitest';
import { parseScan, findMicrochips, toIsoDate } from '../src/scan.js';

describe('scan suggestions', () => {
  it('finds a 15-digit chip printed in groups and fixes common OCR letters', () => {
    expect(findMicrochips('Transponder: 380 26O 1OO 123 456')).toEqual(['380260100123456']);
    expect(findMicrochips('Tel 0039 02 1234 5678')).toEqual([]);
  });
  it('reads EU-style dates and rejects impossible ones', () => {
    expect(toIsoDate('03', '04', '2025')).toBe('2025-04-03');
    expect(toIsoDate('31', '02', '2025')).toBeNull();
    expect(toIsoDate('1', '7', '24')).toBe('2024-07-01');
  });
  it('turns a vaccination sticker into a suggestion with dates and batch', () => {
    const r = parseScan('Nobivac Rabies\nLot A123B45  12.03.2025\ngültig bis 11.03.2028');
    expect(r.vaccinations).toHaveLength(1);
    expect(r.vaccinations[0]).toMatchObject({ vaccine: 'Rabies', date: '2025-03-12', validUntil: '2028-03-11', batch: 'A123B45' });
  });
  it('recognises Italian and German vaccine words', () => {
    const r = parseScan('Antirabbica 01/02/2024\nTollwut 05.06.2023\nLeptospirosi 10/10/2024');
    expect(r.vaccinations.map((v) => v.vaccine)).toEqual(['Rabies', 'Rabies', 'Leptospirosis']);
  });
  it('drops an empty heading when a real entry for the same vaccine exists', () => {
    const r = parseScan('IV. Impfung gegen Tollwut\nTransponder 276 098 106 123 456\n\nx\nNobivac Rabies\nCh.-B. A12 12.03.2025');
    expect(r.vaccinations).toHaveLength(1);
    expect(r.vaccinations[0].batch).toBe('A12');
  });
  it('suggests nothing from unrelated text', () => {
    const r = parseScan('Clinica Veterinaria Navigli\nVia Roma 1, Milano');
    expect(r.vaccinations).toEqual([]);
    expect(r.microchip).toEqual([]);
  });
});
