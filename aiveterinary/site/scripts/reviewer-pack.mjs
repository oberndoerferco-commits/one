// Reviewer pack: one printable document per language for a practising vet who reviews and signs articles.
//
//   node scripts/reviewer-pack.mjs [--lang en|it|de] [--out <dir>] [--no-pdf]
//
// Writes reviewer-pack-<lang>.html (and .pdf, when Chromium can print it through Playwright) to
// ../../reviewer-pack/ (aiveterinary/reviewer-pack, not committed). Read-only on the articles: it never
// changes a file in src/content. Contents per language: cover letter, reviewer details form, list of
// articles, then every article waiting for review (emergency first, then today, then the rest) with its
// urgency, go-now section, full text with file line numbers, sources and a review checklist.
// Each article carries the short fingerprint of the text it shows (the same hash scripts/review.mjs signs),
// so the signature can be checked against the exact version the vet read.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { ROOT, walk, parseText, contentHash, reviewQueue, URGENCY_ORDER } from './review.mjs';
import { findSection } from '../src/components/article-sections.ts';
import { ANIMALS } from '../src/lib/animals-i18n.ts';

const SITE = 'https://aiveterinary.org';
const CONTACT = 'hello@aiveterinary.org';   // as on the editorial policy and legal notice pages
const PRIVACY = 'privacy@aiveterinary.org'; // as on the privacy page
const HERE = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const opt = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : undefined; };
const OUT = resolve(opt('--out') ?? join(HERE, '../../reviewer-pack'));
const LANGS = opt('--lang') ? [opt('--lang')] : ['en', 'it', 'de'];
const CHROMIUM = process.env.CHROMIUM_PATH ?? '/opt/pw-browsers/chromium';
const today = new Date().toISOString().slice(0, 10);

// ---------- text ----------

const T = {
  en: {
    docTitle: 'AI Veterinary: reviewer pack (English articles)',
    packFor: 'Reviewer pack · English articles',
    urg: { emergency: 'Emergency', today: 'Today', 'this-week': 'This week', routine: 'Routine', none: 'No urgency set' },
    species: { dog: 'dog', cat: 'cat', rabbit: 'rabbit', 'guinea-pig': 'guinea pig', ferret: 'ferret', horse: 'horse', bird: 'bird', reptile: 'reptile', general: 'general' },
    cover: (s) => `
      <p>Dear colleague,</p>
      <p>thank you for considering a review for AI Veterinary. This pack contains the ${s.n} English articles that are still waiting for a veterinarian, the most urgent first. You can review as many or as few as you like: even five emergency articles make a real difference.</p>
      <h2>What AI Veterinary is</h2>
      <p>A free, non-commercial information site for animal owners, in English, Italian and German (${SITE}). It explains symptoms, conditions and first aid in plain language, and above all tells owners when to go to a vet now. There is no advertising, no sponsorship and no affiliate link. The articles were drafted with AI assistance from veterinary guidelines and textbooks (WSAVA, ESCCAP, ISFM, national bodies), and every one of them is currently labelled on the site as <em>"Draft written with AI help, awaiting vet review"</em>.</p>
      <h2>What reviewing means</h2>
      <p>You read an article, correct it, and approve it. Once signed, the article shows <strong>your name, your registration (Ordine, Tierärztekammer or equivalent) and the review date</strong>, and a next-review date one year later, as our <a href="${SITE}/editorial">editorial policy</a> describes. You share responsibility for its veterinary content; the founder stays responsible for publishing it. Before you start, please declare any ties to animal-health companies (form on the next page): a reviewer with a tie to a product does not review articles about that product class.</p>
      <p>The articles never give a diagnosis or a medication dose. If you find one, please strike it.</p>
      <h2>Time needed</h2>
      <p>Estimated from word counts (about 130 words a minute of careful reading, plus 4 minutes per article for the checklist and the sources):</p>
      ${s.timeTable}
      <h2>How to review and send corrections</h2>
      <ol>
        <li>Each article has a number (for example <strong>${s.example}</strong>). Line numbers are the lines of the source file, so a correction can say "${s.example}, line 42: replace … with …".</li>
        <li>Start with the urgency and the go-now section: they decide whether an owner goes to a clinic tonight. Then read the full text and the sources, and tick the checklist.</li>
        <li>Write on the printout, or annotate the PDF, and fill in the box at the end of each article. Send a scan, photo or the annotated PDF to <strong>${CONTACT}</strong>, or write the corrections in an email with the article number and line number.</li>
        <li>We make your corrections and send you the corrected text. Only when you confirm it by email do we sign the article in your name. Nothing is published under your name that you have not seen in its final form.</li>
      </ol>
      <h2>Our promise: no change after you sign</h2>
      <p>When an article is signed, we record a fingerprint (SHA-256 hash) of everything a reader relies on: title, summary, species, topic, urgency, sources and the full text. Every build of the website checks every signed article against its fingerprint, and the site cannot be published if a single character has changed since you signed. So no later edit, by a person or by AI, can appear under your name. If a signed article ever needs a change, we send you the exact changes first, and the article is published again only after you (or another veterinarian) have reviewed and signed the new version. The fingerprint of the version in this pack is printed under each article title.</p>
      <h2>Your data (GDPR)</h2>
      ${s.gdpr}
      <p class="signoff">With thanks,<br />[Founder name], AI Veterinary<br />${CONTACT}</p>`,
    gdpr: `<ul>
        <li><strong>Who:</strong> [Company name], [address], [country] is responsible for your data. Contact: ${PRIVACY}.</li>
        <li><strong>What we store:</strong> your name and title as you want them shown; your registration (body and number), which we check against the public register; which version of which article you approved and when; your declaration of interests; and your email address and our correspondence about the reviews.</li>
        <li><strong>What is public:</strong> name, registration and review date, on each article you signed. Nothing else.</li>
        <li><strong>Why:</strong> publishing your name is based on your consent (Art. 6(1)(a) GDPR). Keeping the record of who approved which version is needed to show that a veterinarian reviewed the text (Art. 6(1)(f) GDPR; transparency rules for AI-assisted text, EU AI Act Art. 50).</li>
        <li><strong>How long:</strong> your name stays on the articles while you agree. You can withdraw at any time by email: we remove your name within 7 days and the article goes back to "awaiting vet review". The internal record of what you signed is kept for [retention period] after that, then deleted. Signed forms and emails are kept for the same period.</li>
        <li><strong>Never:</strong> we do not sell your data, use it for marketing, add you to the newsletter or use it to train AI.</li>
        <li><strong>Your rights:</strong> access, correction, deletion, restriction, objection and data portability, and a complaint to your data protection authority.</li>
      </ul>`,
    formTitle: 'Reviewer details',
    form: [['Name and title, as it should appear on the articles', 2], ['Registration (Ordine, Tierärztekammer or equivalent) and number', 1], ['Email address for the corrected texts', 1], ['Declaration of interests: employment, consulting, shareholdings in animal-health companies (or "none")', 3]],
    consent: 'I agree that my name, registration and the review date are published on the articles I sign. I can withdraw this at any time.',
    signature: 'Signature',
    date: 'Date',
    contents: 'Articles in this pack',
    cols: ['No.', 'Article', 'Urgency', 'Animal', 'Words', 'Minutes'],
    total: 'Total',
    timeCols: ['Group', 'Articles', 'Words', 'Time'],
    allRow: 'All articles in this pack',
    perArticle: (m) => `On average one article takes about ${m} minutes.`,
    meta: (a) => `${a.species} · ${a.category} · ${a.words} words · about ${a.minutes} min · file ${a.file}`,
    online: 'Draft online at',
    fingerprint: 'Text fingerprint (review hash)',
    urgencyShown: 'Urgency shown at the top of the page',
    goNow: 'Go-now section',
    goNowMissing: 'This article has no go-now section. Should it have one?',
    summary: 'Summary shown under the title and in search results',
    fullText: 'Full text (numbers are lines of the source file)',
    sources: 'Sources',
    noSources: 'No sources listed. That alone is a reason not to sign yet.',
    checklist: 'Review checklist',
    yes: 'Yes', no: 'No',
    checks: (u) => [
      `Is the urgency correct? (currently: ${u})`,
      'Are the go-now signs complete and correct?',
      'Is anything unsafe, wrong or missing?',
      'Does local practice differ (Italy, Germany, Austria, Switzerland, UK or your country)?',
      'Are the sources adequate and cited correctly?',
    ],
    notes: 'Notes',
    decision: ['Approve as it is', 'Approve with the corrections marked', 'Do not publish yet'],
    fields: ['Name', 'Registration (Ordine / Kammer) and number', 'Date', 'Signature', 'Comments'],
    footer: 'AI Veterinary · reviewer pack (EN)',
    generated: (d, n) => `Generated ${d} · ${n} articles waiting for review`,
  },
  it: {
    docTitle: 'AI Veterinary: pacchetto per la revisione (articoli in italiano)',
    packFor: 'Pacchetto per la revisione · Articoli in italiano',
    urg: { emergency: 'Emergenza', today: 'Oggi', 'this-week': 'Questa settimana', routine: 'Routine', none: 'Urgenza non indicata' },
    species: { dog: 'cane', cat: 'gatto', rabbit: 'coniglio', 'guinea-pig': 'cavia', ferret: 'furetto', horse: 'cavallo', bird: 'uccelli', reptile: 'rettili', general: 'generale' },
    cover: (s) => `
      <p>Gentile collega,</p>
      <p>grazie per aver preso in considerazione una revisione per AI Veterinary. Questo pacchetto contiene i ${s.n} articoli in italiano che aspettano ancora un medico veterinario, a partire dai più urgenti. Può rivederne quanti desidera: anche cinque articoli di emergenza fanno una differenza reale.</p>
      <h2>Che cos'è AI Veterinary</h2>
      <p>Un sito di informazione gratuito e non commerciale per chi ha animali, in italiano, inglese e tedesco (${SITE}/it). Spiega sintomi, malattie e primo soccorso in parole semplici e, soprattutto, dice al proprietario quando andare subito dal veterinario. Non ci sono pubblicità, sponsorizzazioni né link di affiliazione. Gli articoli sono stati redatti con l'aiuto dell'IA a partire da linee guida e testi veterinari (WSAVA, ESCCAP, ISFM, enti nazionali) e oggi ognuno è indicato sul sito come <em>"Bozza scritta con l'aiuto dell'IA, in attesa di revisione veterinaria"</em>.</p>
      <h2>Che cosa significa revisionare</h2>
      <p>Lei legge un articolo, lo corregge e lo approva. Dopo la firma l'articolo riporta <strong>il Suo nome, la Sua iscrizione all'Ordine (o equivalente) e la data della revisione</strong>, con la data della revisione successiva un anno dopo, come descritto nella nostra <a href="${SITE}/it/editorial">politica editoriale</a>. Lei condivide la responsabilità del contenuto veterinario; la responsabilità della pubblicazione resta del fondatore. Prima di iniziare La preghiamo di dichiarare eventuali legami con aziende del settore della salute animale (modulo alla pagina seguente): chi ha un legame con un prodotto non rivede articoli su quella classe di prodotti.</p>
      <p>Gli articoli non danno mai una diagnosi né una posologia. Se ne trova una, La preghiamo di cancellarla.</p>
      <h2>Tempo necessario</h2>
      <p>Stima basata sul numero di parole (circa 130 parole al minuto di lettura attenta, più 4 minuti per articolo per la checklist e le fonti):</p>
      ${s.timeTable}
      <h2>Come revisionare e inviare le correzioni</h2>
      <ol>
        <li>Ogni articolo ha un numero (per esempio <strong>${s.example}</strong>). I numeri di riga sono le righe del file sorgente, quindi una correzione può dire "${s.example}, riga 42: sostituire … con …".</li>
        <li>Cominci dall'urgenza e dalla sezione "vai subito": decidono se il proprietario va in clinica stasera. Poi legga il testo completo e le fonti e compili la checklist.</li>
        <li>Scriva sulla stampa, o annoti il PDF, e compili il riquadro alla fine di ogni articolo. Invii una scansione, una foto o il PDF annotato a <strong>${CONTACT}</strong>, oppure scriva le correzioni in un'email indicando numero dell'articolo e riga.</li>
        <li>Apportiamo le Sue correzioni e Le inviamo il testo corretto. Firmiamo l'articolo a Suo nome solo dopo la Sua conferma via email. Sotto il Suo nome non viene pubblicato nulla che Lei non abbia visto nella forma definitiva.</li>
      </ol>
      <h2>Il nostro impegno: nessuna modifica dopo la firma</h2>
      <p>Alla firma registriamo un'impronta digitale (hash SHA-256) di tutto ciò su cui il lettore fa affidamento: titolo, sommario, specie, argomento, urgenza, fonti e testo completo. Ogni compilazione del sito confronta ogni articolo firmato con la sua impronta, e il sito non può essere pubblicato se anche un solo carattere è cambiato dopo la firma. Nessuna modifica successiva, di una persona o di un'IA, può quindi comparire sotto il Suo nome. Se un articolo firmato deve cambiare, Le inviamo prima le modifiche esatte, e l'articolo torna online solo dopo che Lei (o un altro medico veterinario) ha rivisto e firmato la nuova versione. L'impronta della versione contenuta in questo pacchetto è stampata sotto il titolo di ogni articolo.</p>
      <h2>I Suoi dati (GDPR)</h2>
      ${s.gdpr}
      <p class="signoff">Con i migliori saluti,<br />[Nome del fondatore], AI Veterinary<br />${CONTACT}</p>`,
    gdpr: `<ul>
        <li><strong>Titolare:</strong> [Ragione sociale], [indirizzo], [paese]. Contatto: ${PRIVACY}.</li>
        <li><strong>Cosa conserviamo:</strong> nome e titolo come desidera che compaiano; l'iscrizione (Ordine e numero), che verifichiamo nell'albo pubblico; quale versione di quale articolo ha approvato e quando; la Sua dichiarazione di interessi; il Suo indirizzo email e la corrispondenza sulle revisioni.</li>
        <li><strong>Cosa è pubblico:</strong> nome, iscrizione e data della revisione, su ogni articolo che ha firmato. Nient'altro.</li>
        <li><strong>Perché:</strong> la pubblicazione del nome si basa sul Suo consenso (art. 6, par. 1, lett. a GDPR). Conservare la traccia di chi ha approvato quale versione serve a dimostrare che un medico veterinario ha rivisto il testo (art. 6, par. 1, lett. f GDPR; regole di trasparenza sui testi assistiti da IA, art. 50 del regolamento UE sull'IA).</li>
        <li><strong>Per quanto tempo:</strong> il Suo nome resta sugli articoli finché Lei è d'accordo. Può revocare il consenso in qualsiasi momento via email: rimuoviamo il nome entro 7 giorni e l'articolo torna "in attesa di revisione veterinaria". La traccia interna di ciò che ha firmato viene conservata per [periodo di conservazione] e poi cancellata. Moduli firmati ed email sono conservati per lo stesso periodo.</li>
        <li><strong>Mai:</strong> non vendiamo i Suoi dati, non li usiamo per il marketing, non La iscriviamo alla newsletter e non li usiamo per addestrare l'IA.</li>
        <li><strong>I Suoi diritti:</strong> accesso, rettifica, cancellazione, limitazione, opposizione e portabilità, e reclamo al Garante per la protezione dei dati personali.</li>
      </ul>`,
    formTitle: 'Dati del revisore',
    form: [['Nome e titolo, come devono comparire sugli articoli', 2], ["Iscrizione all'Ordine dei Medici Veterinari (provincia e numero)", 1], ['Indirizzo email per ricevere i testi corretti', 1], ['Dichiarazione di interessi: rapporti di lavoro, consulenze, partecipazioni in aziende della salute animale (oppure "nessuno")', 3]],
    consent: "Acconsento alla pubblicazione del mio nome, della mia iscrizione all'Ordine e della data di revisione sugli articoli che firmo. Posso revocare il consenso in qualsiasi momento.",
    signature: 'Firma',
    date: 'Data',
    contents: 'Articoli in questo pacchetto',
    cols: ['N.', 'Articolo', 'Urgenza', 'Animale', 'Parole', 'Minuti'],
    total: 'Totale',
    timeCols: ['Gruppo', 'Articoli', 'Parole', 'Tempo'],
    allRow: 'Tutti gli articoli del pacchetto',
    perArticle: (m) => `In media un articolo richiede circa ${m} minuti.`,
    meta: (a) => `${a.species} · ${a.category} · ${a.words} parole · circa ${a.minutes} min · file ${a.file}`,
    online: 'Bozza online su',
    fingerprint: 'Impronta del testo (review hash)',
    urgencyShown: "Urgenza mostrata in cima alla pagina",
    goNow: 'Sezione "vai subito"',
    goNowMissing: 'Questo articolo non ha una sezione "vai subito". Dovrebbe averla?',
    summary: 'Sommario mostrato sotto il titolo e nei risultati di ricerca',
    fullText: 'Testo completo (i numeri sono le righe del file sorgente)',
    sources: 'Fonti',
    noSources: 'Nessuna fonte indicata: già questo è un motivo per non firmare ancora.',
    checklist: 'Checklist di revisione',
    yes: 'Sì', no: 'No',
    checks: (u) => [
      `L'urgenza è corretta? (attuale: ${u})`,
      'I segni per cui andare subito sono completi e corretti?',
      "C'è qualcosa di pericoloso, errato o mancante?",
      'Ci sono differenze con la pratica in Italia (farmaci autorizzati, servizi di pronto soccorso, normative, consuetudini)?',
      'Le fonti sono adeguate e citate correttamente?',
    ],
    notes: 'Note',
    decision: ['Approvo così com\'è', 'Approvo con le correzioni segnate', 'Da non pubblicare per ora'],
    fields: ['Nome', "Iscrizione all'Ordine (provincia e numero)", 'Data', 'Firma', 'Commenti'],
    footer: 'AI Veterinary · pacchetto per la revisione (IT)',
    generated: (d, n) => `Generato il ${d} · ${n} articoli in attesa di revisione`,
  },
  de: {
    docTitle: 'AI Veterinary: Prüfunterlagen (deutsche Artikel)',
    packFor: 'Prüfunterlagen · Deutsche Artikel',
    urg: { emergency: 'Notfall', today: 'Heute', 'this-week': 'Diese Woche', routine: 'Routine', none: 'Keine Dringlichkeit angegeben' },
    species: { dog: 'Hund', cat: 'Katze', rabbit: 'Kaninchen', 'guinea-pig': 'Meerschweinchen', ferret: 'Frettchen', horse: 'Pferd', bird: 'Vögel', reptile: 'Reptilien', general: 'allgemein' },
    cover: (s) => `
      <p>Liebe Kollegin, lieber Kollege,</p>
      <p>vielen Dank, dass Sie eine Prüfung für AI Veterinary in Betracht ziehen. Diese Unterlagen enthalten die ${s.n} deutschen Artikel, die noch auf eine Tierärztin oder einen Tierarzt warten, die dringendsten zuerst. Sie können so viele oder so wenige prüfen, wie Sie möchten: Schon fünf Notfallartikel machen einen echten Unterschied.</p>
      <h2>Was AI Veterinary ist</h2>
      <p>Eine kostenlose, nicht kommerzielle Informationsseite für Tierhalterinnen und Tierhalter, auf Deutsch, Italienisch und Englisch (${SITE}/de). Sie erklärt Symptome, Erkrankungen und Erste Hilfe in verständlicher Sprache und sagt vor allem, wann man sofort in die Praxis sollte. Es gibt keine Werbung, kein Sponsoring und keine Affiliate-Links. Die Artikel wurden mit KI-Unterstützung aus tierärztlichen Leitlinien und Lehrbüchern (WSAVA, ESCCAP, ISFM, nationale Stellen) entworfen und sind auf der Seite derzeit alle als <em>„Mit KI-Hilfe verfasster Entwurf, tierärztliche Prüfung ausstehend"</em> gekennzeichnet.</p>
      <h2>Was Prüfen bedeutet</h2>
      <p>Sie lesen einen Artikel, korrigieren ihn und geben ihn frei. Nach der Freigabe stehen auf dem Artikel <strong>Ihr Name, Ihre Kammerzugehörigkeit (Tierärztekammer oder Entsprechendes) und das Prüfdatum</strong>, dazu der nächste Prüftermin ein Jahr später, wie in unseren <a href="${SITE}/de/editorial">redaktionellen Grundsätzen</a> beschrieben. Sie tragen die Verantwortung für den tierärztlichen Inhalt mit; für die Veröffentlichung bleibt der Gründer verantwortlich. Bitte geben Sie vorab Verbindungen zu Unternehmen der Tiergesundheit an (Formular auf der nächsten Seite): Wer mit einem Produkt verbunden ist, prüft keine Artikel über diese Produktklasse.</p>
      <p>Die Artikel stellen nie eine Diagnose und nennen keine Dosierungen. Falls Sie doch eine finden, streichen Sie sie bitte.</p>
      <h2>Zeitaufwand</h2>
      <p>Geschätzt aus der Wortzahl (etwa 130 Wörter pro Minute bei sorgfältigem Lesen, dazu 4 Minuten pro Artikel für Checkliste und Quellen):</p>
      ${s.timeTable}
      <h2>So prüfen Sie und senden Korrekturen</h2>
      <ol>
        <li>Jeder Artikel hat eine Nummer (zum Beispiel <strong>${s.example}</strong>). Die Zeilennummern sind die Zeilen der Quelldatei; eine Korrektur kann also lauten: „${s.example}, Zeile 42: … ersetzen durch …".</li>
        <li>Beginnen Sie mit der Dringlichkeit und dem Abschnitt „sofort in die Praxis": Sie entscheiden, ob ein Halter heute Nacht in die Klinik fährt. Lesen Sie dann den vollständigen Text und die Quellen und füllen Sie die Checkliste aus.</li>
        <li>Schreiben Sie auf den Ausdruck oder kommentieren Sie das PDF und füllen Sie das Feld am Ende jedes Artikels aus. Senden Sie einen Scan, ein Foto oder das kommentierte PDF an <strong>${CONTACT}</strong>, oder schreiben Sie die Korrekturen mit Artikel- und Zeilennummer in eine E-Mail.</li>
        <li>Wir übernehmen Ihre Korrekturen und senden Ihnen den korrigierten Text. Erst wenn Sie ihn per E-Mail bestätigen, zeichnen wir den Artikel in Ihrem Namen ab. Unter Ihrem Namen erscheint nichts, was Sie nicht in der endgültigen Fassung gesehen haben.</li>
      </ol>
      <h2>Unser Versprechen: keine Änderung nach Ihrer Freigabe</h2>
      <p>Bei der Freigabe speichern wir einen Fingerabdruck (SHA-256-Hash) von allem, worauf sich Leserinnen und Leser verlassen: Titel, Zusammenfassung, Tierart, Thema, Dringlichkeit, Quellen und vollständiger Text. Bei jedem Erstellen der Website wird jeder freigegebene Artikel mit seinem Fingerabdruck verglichen, und die Seite kann nicht veröffentlicht werden, wenn sich seit Ihrer Freigabe auch nur ein Zeichen geändert hat. Keine spätere Änderung, ob von einem Menschen oder einer KI, kann so unter Ihrem Namen erscheinen. Muss ein freigegebener Artikel geändert werden, senden wir Ihnen zuerst die genauen Änderungen, und er erscheint erst wieder, wenn Sie (oder eine andere Tierärztin, ein anderer Tierarzt) die neue Fassung geprüft und freigegeben haben. Der Fingerabdruck der Fassung in diesen Unterlagen steht unter jedem Artikeltitel.</p>
      <h2>Ihre Daten (DSGVO)</h2>
      ${s.gdpr}
      <p class="signoff">Mit herzlichem Dank<br />[Name des Gründers], AI Veterinary<br />${CONTACT}</p>`,
    gdpr: `<ul>
        <li><strong>Verantwortlich:</strong> [Firmenname], [Anschrift], [Land]. Kontakt: ${PRIVACY}.</li>
        <li><strong>Was wir speichern:</strong> Ihren Namen und Titel so, wie sie erscheinen sollen; Ihre Kammerzugehörigkeit (Kammer und ggf. Nummer), die wir im öffentlichen Verzeichnis prüfen; welche Fassung welches Artikels Sie wann freigegeben haben; Ihre Erklärung zu Interessenkonflikten; Ihre E-Mail-Adresse und unsere Korrespondenz zu den Prüfungen.</li>
        <li><strong>Was öffentlich ist:</strong> Name, Kammer und Prüfdatum, auf jedem Artikel, den Sie freigegeben haben. Sonst nichts.</li>
        <li><strong>Warum:</strong> Die Nennung Ihres Namens beruht auf Ihrer Einwilligung (Art. 6 Abs. 1 lit. a DSGVO). Die Aufzeichnung, wer welche Fassung freigegeben hat, brauchen wir als Nachweis der tierärztlichen Prüfung (Art. 6 Abs. 1 lit. f DSGVO; Transparenzregeln für KI-gestützte Texte, Art. 50 KI-Verordnung).</li>
        <li><strong>Wie lange:</strong> Ihr Name bleibt auf den Artikeln, solange Sie einverstanden sind. Sie können jederzeit per E-Mail widerrufen: Wir entfernen Ihren Namen innerhalb von 7 Tagen, und der Artikel ist wieder „tierärztliche Prüfung ausstehend". Die interne Aufzeichnung Ihrer Freigaben bewahren wir danach [Aufbewahrungsfrist] auf und löschen sie dann. Unterschriebene Formulare und E-Mails ebenso.</li>
        <li><strong>Niemals:</strong> Wir verkaufen Ihre Daten nicht, nutzen sie nicht für Werbung, tragen Sie nicht in den Newsletter ein und trainieren damit keine KI.</li>
        <li><strong>Ihre Rechte:</strong> Auskunft, Berichtigung, Löschung, Einschränkung, Widerspruch und Datenübertragbarkeit sowie Beschwerde bei Ihrer Datenschutzaufsichtsbehörde.</li>
      </ul>`,
    formTitle: 'Angaben zur prüfenden Person',
    form: [['Name und Titel, wie sie auf den Artikeln erscheinen sollen', 2], ['Tierärztekammer (oder Entsprechendes) und ggf. Mitgliedsnummer', 1], ['E-Mail-Adresse für die korrigierten Texte', 1], ['Interessenkonflikte: Anstellung, Beratung, Beteiligungen an Unternehmen der Tiergesundheit (oder „keine")', 3]],
    consent: 'Ich bin einverstanden, dass mein Name, meine Kammer und das Prüfdatum auf den von mir freigegebenen Artikeln veröffentlicht werden. Ich kann das jederzeit widerrufen.',
    signature: 'Unterschrift',
    date: 'Datum',
    contents: 'Artikel in diesen Unterlagen',
    cols: ['Nr.', 'Artikel', 'Dringlichkeit', 'Tier', 'Wörter', 'Minuten'],
    total: 'Gesamt',
    timeCols: ['Gruppe', 'Artikel', 'Wörter', 'Zeit'],
    allRow: 'Alle Artikel in diesen Unterlagen',
    perArticle: (m) => `Ein Artikel dauert im Schnitt etwa ${m} Minuten.`,
    meta: (a) => `${a.species} · ${a.category} · ${a.words} Wörter · etwa ${a.minutes} Min. · Datei ${a.file}`,
    online: 'Entwurf online unter',
    fingerprint: 'Fingerabdruck des Textes (Review-Hash)',
    urgencyShown: 'Dringlichkeit, oben auf der Seite angezeigt',
    goNow: 'Abschnitt „sofort in die Praxis"',
    goNowMissing: 'Dieser Artikel hat keinen Abschnitt „sofort in die Praxis". Sollte er einen haben?',
    summary: 'Zusammenfassung unter dem Titel und in Suchergebnissen',
    fullText: 'Vollständiger Text (Nummern = Zeilen der Quelldatei)',
    sources: 'Quellen',
    noSources: 'Keine Quellen angegeben: schon das ist ein Grund, noch nicht freizugeben.',
    checklist: 'Prüf-Checkliste',
    yes: 'Ja', no: 'Nein',
    checks: (u) => [
      `Ist die Dringlichkeit richtig? (derzeit: ${u})`,
      'Sind die Anzeichen für „sofort in die Praxis" vollständig und richtig?',
      'Ist etwas gefährlich, falsch oder fehlt etwas?',
      'Weicht die Praxis in Deutschland, Österreich oder der Schweiz ab (zugelassene Mittel, Notdienste, Rechtslage, Gepflogenheiten)?',
      'Sind die Quellen angemessen und richtig zitiert?',
    ],
    notes: 'Anmerkungen',
    decision: ['Freigabe ohne Änderungen', 'Freigabe mit den markierten Korrekturen', 'Noch nicht veröffentlichen'],
    fields: ['Name', 'Kammer und ggf. Nummer', 'Datum', 'Unterschrift', 'Kommentare'],
    footer: 'AI Veterinary · Prüfunterlagen (DE)',
    generated: (d, n) => `Erstellt am ${d} · ${n} Artikel warten auf Prüfung`,
  },
};

// ---------- Markdown (the small subset the articles use) ----------

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const abs = (u) => (u.startsWith('/') ? SITE + u : u);
function inline(s) {
  return esc(s)
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, t, u) => `<a href="${abs(u)}">${t}</a>${u.startsWith('/') ? ` <span class="href">(${abs(u)})</span>` : ''}`)
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*\w])\*([^*\s][^*]*)\*(?!\w)/g, '$1<em>$2</em>')
    .replace(/(^|[^\w])_([^_\s][^_]*)_(?!\w)/g, '$1<em>$2</em>');
}
const slug = (s) => s.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-|-$/g, '');
const cells = (l) => l.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
const isTableSep = (l) => /^\|?[\s:|-]+\|?$/.test(l.trim()) && l.includes('-');

/** Markdown body to HTML with h2 ids, for finding the go-now section with the site's own rules. */
function render(md) {
  const lines = md.replace(/\r\n/g, '\n').split('\n');
  const out = [];
  let para = [], list = null, table = null;
  const flush = () => {
    if (para.length) out.push(`<p>${inline(para.join(' '))}</p>`); para = [];
    if (list) out.push(`<${list.tag}>${list.items.map((i) => `<li>${inline(i)}</li>`).join('')}</${list.tag}>`); list = null;
    if (table) out.push(`<table class="md"><thead><tr>${table[0].map((c) => `<th>${inline(c)}</th>`).join('')}</tr></thead><tbody>${table.slice(1).map((r) => `<tr>${r.map((c) => `<td>${inline(c)}</td>`).join('')}</tr>`).join('')}</tbody></table>`); table = null;
  };
  for (const l of lines) {
    let m;
    if (!l.trim()) { flush(); continue; }
    if ((m = l.match(/^(#{2,4})\s+(.*)$/))) { flush(); const n = m[1].length; out.push(`<h${n}${n === 2 ? ` id="${slug(m[2])}"` : ''}>${inline(m[2])}</h${n}>`); continue; }
    if (l.trim().startsWith('|')) { if (!table) { flush(); table = []; } if (!isTableSep(l)) table.push(cells(l)); continue; }
    if ((m = l.match(/^\s*[-*]\s+(.*)$/)) || (m = l.match(/^\s*\d+[.)]\s+(.*)$/))) {
      const tag = /^\s*\d/.test(l) ? 'ol' : 'ul';
      if (para.length || table || (list && list.tag !== tag)) flush();
      list ??= { tag, items: [] };
      list.items.push(m[1]);
      continue;
    }
    if (list) { list.items[list.items.length - 1] += ' ' + l.trim(); continue; }
    para.push(l.trim());
  }
  flush();
  return out.join('\n');
}

/** One row per source line, numbered as in the file. */
function numbered(body, firstLine) {
  return body.replace(/\r\n/g, '\n').split('\n').map((l, i) => {
    const n = firstLine + i;
    let cls = '', html;
    let m;
    if (!l.trim()) { cls = 'blank'; html = ''; }
    else if ((m = l.match(/^(#{2,4})\s+(.*)$/))) { cls = `hd h${m[1].length}`; html = inline(m[2]); }
    else if (isTableSep(l) && l.trim().startsWith('|')) { cls = 'sep'; html = '<span class="muted">(table)</span>'; }
    else if (l.trim().startsWith('|')) { cls = 'tr'; html = cells(l).map(inline).join(' <span class="pipe">|</span> '); }
    else if ((m = l.match(/^\s*[-*]\s+(.*)$/))) { cls = 'li'; html = `<span class="bullet">•</span> ${inline(m[1])}`; }
    else if ((m = l.match(/^\s*(\d+[.)])\s+(.*)$/))) { cls = 'li'; html = `<span class="bullet">${m[1]}</span> ${inline(m[2])}`; }
    else html = inline(l);
    return `<tr class="${cls}"><td class="n">${n}</td><td class="t">${html}</td></tr>`;
  }).join('\n');
}

// ---------- the pack ----------

const fmtHours = (min, lang) => {
  const h = min / 60;
  const s = h < 1 ? `${min} min` : `${(Math.round(h * 10) / 10).toLocaleString(lang === 'en' ? 'en-GB' : lang)} h`;
  return s;
};

function articleData(entry, lang, i) {
  const raw = readFileSync(entry.file, 'utf8');
  const a = parseText(raw, entry.file);
  const lines = raw.split('\n');
  const fmLen = raw.length - a.body.length;
  const firstBodyLine = raw.slice(0, fmLen).split('\n').length;
  const lineOf = (key) => lines.findIndex((l) => l.startsWith(`${key}:`)) + 1;
  const html = render(a.body);
  const sec = findSection(html, lang, 'gonow');
  const prefix = lang === 'en' ? '' : `/${lang}`;
  return {
    ...entry,
    no: `${lang.toUpperCase()}-${String(i + 1).padStart(3, '0')}`,
    a, firstBodyLine, sec,
    titleLine: lineOf('title'), descLine: lineOf('description'), urgLine: lineOf('urgency'),
    url: `${SITE}${prefix}/animals/${basename(entry.file, '.md')}`,
    hash: contentHash(a),
    species: T[lang].species[a.data.species] ?? a.data.species,
    category: a.data.category,
  };
}

const CSS = `
:root { --ink: #1d2320; --muted: #5d6762; --line: #c9d0cc; --soft: #f3f6f4; --accent: #1f6b4f; --emergency: #a3231b; --today: #8a5300; }
* { box-sizing: border-box; }
html { background: #fff; }
body { margin: 0; color: var(--ink); background: #fff; font: 10.5pt/1.45 "Helvetica Neue", Arial, "Liberation Sans", sans-serif; }
main { max-width: 180mm; margin: 0 auto; padding: 12mm 0; }
h1, h2, h3 { font-family: Georgia, "Times New Roman", serif; line-height: 1.2; }
h1 { font-size: 21pt; margin: 0 0 4mm; }
h2 { font-size: 13.5pt; margin: 6mm 0 2mm; }
h3 { font-size: 11.5pt; margin: 5mm 0 2mm; }
a { color: var(--accent); }
.page { break-before: page; }
.cover .kicker { color: var(--muted); text-transform: uppercase; letter-spacing: .06em; font-size: 9pt; margin: 0 0 2mm; }
.cover p, .cover li { max-width: 165mm; }
.signoff { margin-top: 6mm; }
table { border-collapse: collapse; width: 100%; }
.data th, .data td { border-bottom: 1px solid var(--line); padding: 1.2mm 2mm; text-align: left; vertical-align: top; font-size: 9.5pt; }
.data td.num, .data th.num { text-align: right; white-space: nowrap; }
.data tfoot td { font-weight: 700; border-bottom: 0; }
.badge { display: inline-block; border-radius: 3px; padding: 0 2mm; font-size: 8.5pt; font-weight: 700; color: #fff; background: var(--muted); white-space: nowrap; }
.badge.emergency { background: var(--emergency); } .badge.today { background: var(--today); } .badge.this-week { background: var(--accent); }
.field { border-bottom: 1px solid var(--ink); height: 9mm; }
.field.tall { height: 18mm; } .field.xtall { height: 27mm; }
.label { font-size: 9pt; color: var(--muted); margin-top: 3mm; }
.tick { display: inline-block; width: 3.6mm; height: 3.6mm; border: 1.2px solid var(--ink); border-radius: 1px; vertical-align: -0.6mm; margin-right: 1.4mm; }
.consent { margin-top: 5mm; }
.art-head { border-bottom: 2px solid var(--ink); padding-bottom: 2mm; margin-bottom: 3mm; }
.art-no { font-weight: 700; font-size: 10pt; letter-spacing: .04em; }
.art-head h2 { font-size: 16pt; margin: 1mm 0 1.5mm; }
.meta { color: var(--muted); font-size: 8.5pt; margin: 0; word-break: break-all; }
.box { border: 1px solid var(--line); background: var(--soft); border-radius: 2mm; padding: 2.5mm 4mm; margin: 3mm 0; }
.box h3 { margin: 0 0 1.5mm; font-size: 10.5pt; font-family: inherit; }
.gonow { border-color: var(--emergency); background: #fff6f5; }
.gonow h4 { margin: 0 0 1.5mm; font-size: 10.5pt; }
.box ul, .box ol { margin: 1mm 0; padding-left: 5mm; }
table.md { margin: 2mm 0; } table.md th, table.md td { border: 1px solid var(--line); padding: 1mm 1.5mm; font-size: 9pt; text-align: left; }
.lines { font-size: 9.5pt; line-height: 1.38; table-layout: fixed; }
.lines col.n { width: 12mm; }
.lines td { vertical-align: top; padding: 0.3mm 0; }
.lines td.n { padding-right: 3mm; text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; font-size: 8pt; padding-top: 0.7mm; user-select: none; }
.lines tr.blank td { height: 1.6mm; padding: 0; font-size: 1pt; line-height: 1; }
.lines tr.blank td.n { visibility: hidden; }
.lines tr.hd td.t { font-weight: 700; font-family: Georgia, serif; font-size: 11pt; padding-top: 1.5mm; }
.lines tr.h3 td.t { font-size: 10pt; }
.lines tr.li td.t { padding-left: 5mm; }
.lines tr.li .bullet { margin-left: -5mm; width: 5mm; min-width: 0; }
.lines tr.tr td.t { font-size: 9pt; }
.bullet { display: inline-block; min-width: 3mm; }
.pipe, .muted, .href { color: var(--muted); }
.href { font-size: 8pt; word-break: break-all; }
.refs { padding-left: 6mm; } .refs li { margin-bottom: 1mm; } .refs .url { font-size: 8.5pt; word-break: break-all; }
.check { break-inside: avoid; border: 1.5px solid var(--ink); border-radius: 2mm; padding: 3mm 4mm; margin-top: 5mm; }
.check h3 { margin: 0 0 2mm; font-family: inherit; font-size: 11pt; }
.check ol { margin: 0; padding-left: 5mm; }
.check li { margin: 0 0 1.5mm; }
.yn { white-space: nowrap; margin-left: 2mm; }
.noteline { border-bottom: 1px solid var(--line); height: 6.5mm; }
.decision { margin: 3mm 0 1mm; display: flex; flex-wrap: wrap; gap: 2mm 7mm; }
.signbox { display: grid; grid-template-columns: 1fr 1fr; gap: 0 6mm; }
.signbox .wide { grid-column: 1 / -1; }
.toc td:nth-child(2) { width: 60%; }
.warn { color: var(--emergency); font-weight: 700; }
@page { size: A4; margin: 14mm 14mm 16mm; }
@media screen { main { padding: 12mm 16px; } .page { border-top: 1px dashed var(--line); margin-top: 12mm; padding-top: 8mm; } }
@media print { a { color: inherit; } }
`;

function build(lang) {
  const t = T[lang];
  const queue = reviewQueue(walk(ROOT), { lang });
  const items = queue.map((e, i) => articleData(e, lang, i));
  const n = items.length;
  const urg = (u) => t.urg[u ?? 'none'];
  const badge = (u) => `<span class="badge ${u ?? 'none'}">${esc(urg(u))}</span>`;

  // Time per urgency group, from word counts
  const groups = URGENCY_ORDER.map((u) => ({ u, list: items.filter((x) => (x.urgency ?? null) === u) })).filter((g) => g.list.length);
  const sum = (l, k) => l.reduce((s, x) => s + x[k], 0);
  const timeTable = `<table class="data"><thead><tr>${t.timeCols.map((c, i) => `<th${i ? ' class="num"' : ''}>${c}</th>`).join('')}</tr></thead><tbody>${groups.map((g) => `<tr><td>${badge(g.u)}</td><td class="num">${g.list.length}</td><td class="num">${sum(g.list, 'words').toLocaleString(lang === 'en' ? 'en-GB' : lang)}</td><td class="num">${fmtHours(sum(g.list, 'minutes'), lang)}</td></tr>`).join('')}</tbody><tfoot><tr><td>${t.allRow}</td><td class="num">${n}</td><td class="num">${sum(items, 'words').toLocaleString(lang === 'en' ? 'en-GB' : lang)}</td><td class="num">${fmtHours(sum(items, 'minutes'), lang)}</td></tr></tfoot></table><p>${t.perArticle(n ? Math.round(sum(items, 'minutes') / n) : 0)}</p>`;

  const cover = `<section class="cover">
    <p class="kicker">${t.packFor}</p>
    <h1>AI Veterinary</h1>
    <p class="meta">${t.generated(today, n)}</p>
    ${t.cover({ n, timeTable, example: items[0]?.no ?? `${lang.toUpperCase()}-001`, gdpr: t.gdpr })}
  </section>`;

  const form = `<section class="page">
    <h2>${t.formTitle}</h2>
    ${t.form.map(([l, h]) => `<div class="label">${l}</div><div class="field${h === 2 ? ' tall' : h === 3 ? ' xtall' : ''}"></div>`).join('')}
    <p class="consent"><span class="tick"></span>${t.consent}</p>
    <div class="signbox"><div><div class="label">${t.date}</div><div class="field"></div></div><div><div class="label">${t.signature}</div><div class="field"></div></div></div>
  </section>`;

  const toc = `<section class="page">
    <h2>${t.contents}</h2>
    <table class="data toc"><thead><tr>${t.cols.map((c, i) => `<th${i >= 4 ? ' class="num"' : ''}>${c}</th>`).join('')}</tr></thead>
    <tbody>${items.map((x) => `<tr><td>${x.no}</td><td><a href="#${x.no}">${esc(x.title)}</a></td><td>${badge(x.urgency)}</td><td>${esc(x.species)}</td><td class="num">${x.words}</td><td class="num">${x.minutes}</td></tr>`).join('')}</tbody>
    <tfoot><tr><td></td><td>${t.total}</td><td></td><td></td><td class="num">${sum(items, 'words')}</td><td class="num">${sum(items, 'minutes')}</td></tr></tfoot></table>
  </section>`;

  const articles = items.map((x) => {
    const d = x.a.data;
    const refs = d.references ?? [];
    const urgText = d.urgency ? ANIMALS[lang].urgency[d.urgency] : null;
    return `<section class="page article" id="${x.no}" aria-labelledby="${x.no}-t">
    <header class="art-head">
      <div class="art-no">${x.no} · ${badge(x.urgency)}</div>
      <h2 id="${x.no}-t">${esc(d.title)}</h2>
      <p class="meta">${esc(t.meta({ ...x, species: x.species, category: x.category }))}</p>
      <p class="meta">${t.online} <a href="${x.url}">${x.url}</a> · ${t.fingerprint}: ${x.hash.slice(0, 12)}</p>
    </header>
    <div class="box"><h3>${t.urgencyShown}${x.urgLine ? ` <span class="muted">(${lang === 'de' ? 'Zeile' : lang === 'it' ? 'riga' : 'line'} ${x.urgLine})</span>` : ''}</h3><p>${badge(x.urgency)} ${urgText ? esc(urgText) : ''}</p></div>
    <div class="box"><h3>${t.summary} <span class="muted">(${lang === 'de' ? 'Zeile' : lang === 'it' ? 'riga' : 'line'} ${x.descLine})</span></h3><p>${inline(d.description ?? '')}</p></div>
    <div class="box gonow"><h3>${t.goNow}</h3>${x.sec ? `<h4>${esc(x.sec.text)}</h4>${x.sec.html}` : `<p class="warn">${t.goNowMissing}</p>`}</div>
    <h3>${t.fullText}</h3>
    <table class="lines"><colgroup><col class="n" /><col /></colgroup><tbody>${numbered(x.a.body, x.firstBodyLine)}</tbody></table>
    <h3>${t.sources}</h3>
    ${refs.length ? `<ol class="refs">${refs.map((r) => `<li>${esc(r.title)}${r.url ? `<br /><a class="url" href="${esc(r.url)}">${esc(r.url)}</a>` : ''}</li>`).join('')}</ol>` : `<p class="warn">${t.noSources}</p>`}
    <div class="check">
      <h3>${t.checklist} · ${x.no}</h3>
      <ol>${t.checks(urg(x.urgency)).map((c) => `<li>${esc(c)} <span class="yn"><span class="tick"></span>${t.yes} <span class="tick" style="margin-left:3mm"></span>${t.no}</span><div class="noteline"></div></li>`).join('')}</ol>
      <div class="decision">${t.decision.map((c) => `<span><span class="tick"></span>${esc(c)}</span>`).join('')}</div>
      <div class="signbox">
        <div><div class="label">${t.fields[0]}</div><div class="field"></div></div>
        <div><div class="label">${t.fields[1]}</div><div class="field"></div></div>
        <div><div class="label">${t.fields[2]}</div><div class="field"></div></div>
        <div><div class="label">${t.fields[3]}</div><div class="field"></div></div>
        <div class="wide"><div class="label">${t.fields[4]}</div><div class="field xtall"></div></div>
      </div>
    </div>
  </section>`;
  }).join('\n');

  const html = `<!doctype html>
<html lang="${lang}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="robots" content="noindex" />
<title>${esc(t.docTitle)}</title>
<style>${CSS}</style>
</head>
<body>
<main>
${cover}
${form}
${toc}
${articles}
</main>
</body>
</html>
`;
  return { html, n, words: sum(items, 'words'), minutes: sum(items, 'minutes'), emergency: items.filter((x) => x.urgency === 'emergency').length, noGoNow: items.filter((x) => !x.sec).map((x) => x.no) };
}

async function loadPlaywright() {
  try { return await import('playwright'); } catch {}
  for (const base of ['/opt/node22/lib/node_modules/', process.env.NODE_PATH].filter(Boolean)) {
    try { return createRequire(join(base, 'noop.js'))('playwright'); } catch {}
  }
  return null;
}
const pdfPages = (file) => (readFileSync(file, 'latin1').match(/\/Type\s*\/Page(?![s\w])/g) ?? []).length;

mkdirSync(OUT, { recursive: true });
const results = [];
for (const lang of LANGS) {
  if (!T[lang]) { console.error(`Unknown language ${lang}`); process.exit(2); }
  const r = build(lang);
  const htmlFile = join(OUT, `reviewer-pack-${lang}.html`);
  writeFileSync(htmlFile, r.html);
  results.push({ lang, htmlFile, ...r });
  console.log(`${lang}: ${r.n} articles (${r.emergency} emergency), ${r.words} words, about ${Math.round(r.minutes / 6) / 10} h → ${htmlFile}`);
  if (r.noGoNow.length) console.log(`   no go-now section found: ${r.noGoNow.join(', ')}`);
}

if (!args.includes('--no-pdf')) {
  const pw = await loadPlaywright();
  let browser = null;
  if (pw) { try { browser = await pw.chromium.launch({ executablePath: CHROMIUM }); } catch (e) { console.warn(`PDF skipped: Chromium did not start (${e.message.split('\n')[0]})`); } }
  else console.warn('PDF skipped: Playwright is not installed. Open the HTML file and print it to PDF instead.');
  if (browser) {
    try {
      for (const r of results) {
        const page = await browser.newPage();
        page.setDefaultTimeout(10 * 60_000);
        await page.goto(pathToFileURL(r.htmlFile).href, { waitUntil: 'load' });
        const pdfFile = r.htmlFile.replace(/\.html$/, '.pdf');
        await page.pdf({
          path: pdfFile, format: 'A4', printBackground: true, preferCSSPageSize: true, displayHeaderFooter: true,
          headerTemplate: '<span></span>',
          footerTemplate: `<div style="font: 7.5px Arial, sans-serif; color: #5d6762; width: 100%; padding: 0 14mm; display: flex; justify-content: space-between;"><span>${esc(T[r.lang].footer)} · ${today}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`,
        });
        await page.close();
        console.log(`${r.lang}: ${pdfPages(pdfFile)} pages → ${pdfFile}`);
      }
    } finally { await browser.close(); }
  }
}
