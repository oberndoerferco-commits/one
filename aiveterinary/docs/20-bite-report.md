# 20 — Dog-bite report letter (CH, IT)

Research for the TODO item "Dog-bite report letter (CH, IT)". Implementation: `app/src/bite-report.ts` (`buildBiteReport`, `renderBiteReport`), tests in `app/test/bite-report.test.ts`. All sources opened on **23 Oct 2026** unless noted.

## Summary

| | Switzerland | Italy |
|---|---|---|
| Who must report | Vets, doctors, shelter managers, pet-care providers, dog trainers, customs officers (TSchV art. 78 para. 1). Cantons may add others (para. 2); ZH adds municipalities, police, prosecutors, courts and shelters (§ 16 HuG ZH, quoted on the ZH form). | No single national provision found that obliges vets to report every bite. O.M. 6 Aug 2013 art. 1 c. 6: the private vet *reports to the ASL veterinary service* dogs among their patients that need a behavioural assessment. Regional instructions (Emilia-Romagna, 2026) say **all** bites by kept animals must be reported promptly to the ASL veterinary service by doctors and private vets, including when the victim is an animal. |
| What | A dog that (a) **injured people or animals significantly** or (b) **shows excessive aggression**. ZH form: "significant" = any bite that needs medical or veterinary attention, whatever the severity. | Bite or aggression episodes (morsicatura, aggressione). Suspected rabies: separate notification within **12 hours**. |
| To whom | The competent **cantonal office** (Veterinäramt / service vétérinaire / Ufficio del veterinario cantonale). It checks the report and records it in ASAN (art. 79). | The **ASL veterinary service** (Servizio veterinario / Sanità animale) of the competent ASL. |
| Deadline | None in art. 78 or on the forms opened. | "Tempestivamente" (ER note). Suspected rabies: without delay, no later than 12 h (Reg. (EU) 2016/429 art. 18 with D.Lgs. 136/2022, per the ER note). |
| Form | Cantonal forms (see below), sent by post or e-mail. | ASL-specific; no national form. AUSL Valle d'Aosta: by PEC to the Sanità animale clinic. |
| Observation | Not covered here (CH rabies rules not researched). | ER note: with risk factors, visit the biting animal as soon as possible and again **10 days after the bite**; with founded suspicion of rabies, observation of **at least 10 days** from the bite in an approved facility. DPR 320/1954 arts. 86–87 (the old 10-day rule) were **repealed** by D.Lgs. 136/2022 with effect from 27 Sep 2022. |

**Correction to the brief.** The task cited "DPR 320/1954 art. 86/87" for the 10-day observation. Normattiva shows both articles in force only from 9 Jul 1954 to 26 Sep 2022, then "PROVVEDIMENTO ABROGATO DAL D.LGS. 5 AGOSTO 2022, N. 136". The O.M. 2013 art. 3 c. 1 still opens "Fatto salvo quanto stabilito dagli articoli 86 e 87 del DPR 320/1954", because each yearly extension only prolongs the 2013 text. The 10-day period now comes from Ministry/regional rabies guidance (Ministry note prot. 0016351 of 4 Jun 2025, which I did not open; quoted in the ER note). The module therefore never computes an end date and only prints dates the vet types.

## Switzerland

### Federal law

**TSchV (SR 455.1), as of 1 Feb 2026.** Art. 78 "Meldung von Vorfällen" (wording of 20 Dec 2024, in force since 1 Feb 2025, AS 2025 21):

> 1 Tierärztinnen und Tierärzte, Ärztinnen und Ärzte, Tierheimverantwortliche, Anbieterinnen und Anbieter von Tierbetreuungsdiensten, Hundeausbildnerinnen und Hundeausbildner sowie Zollorgane sind verpflichtet, der zuständigen kantonalen Stelle Vorfälle zu melden, bei denen ein Hund: a. Menschen oder Tiere erheblich verletzt hat; oder b. ein übermässiges Aggressionsverhalten zeigt.
> 2 Die Kantone können die Meldepflicht auf weitere Personenkreise ausdehnen.

Art. 79: the cantonal office checks the facts (may call in experts), orders measures if the dog shows a behavioural problem, and records reports and measures in ASAN.

Italian text (OPAn) art. 78: "I veterinari, i medici, … sono tenuti a notificare all'autorità cantonale competente i casi in cui un cane: a. ha ferito gravemente una persona o un animale; oppure b. ha mostrato un comportamento oltremodo aggressivo." Used for the Ticino heading.

- DE: https://fedlex.data.admin.ch/filestore/fedlex.data.admin.ch/eli/cc/2008/416/20260201/de/html/fedlex-data-admin-ch-eli-cc-2008-416-20260201-de-html-2.html
- IT: https://fedlex.data.admin.ch/filestore/fedlex.data.admin.ch/eli/cc/2008/416/20260201/it/html/fedlex-data-admin-ch-eli-cc-2008-416-20260201-it-html-2.html

### Cantonal forms (fields)

**Zürich**, Veterinäramt, "Meldung von Vorfällen mit Hunden gemäss Art. 78 Tierschutzverordnung" (Ausgabedatum 30.06.2017). Filled in completely, signed, sent by post or brought to the counter; the page also lists an e-mail address. Fields:
- Meldegrund: Verletzung Mensch / Verletzung Tier / Aggressionsverhalten
- A. Injured / affected person or keeper of the injured animal: name, sex, address, phone, date of birth
- B. Injured animal: species/breed, weight, sex, neutered
- C. Injury: number of bites (1 / 2 / 3+), type (Prellung … Fraktur), location, treatment (*"Für diese Angaben ist das Einverständnis der Person oder dasjenige ihres rechtlichen Vertreters notwendig"*)
- D. Incident: date, time, municipality, place (at the dog's home / public), police report yes/no, own/known/unknown dog, description
- E. Keeper of the biting dog (if known): name, address, phone
- F. Biting dog (if known): breed(s), microchip no., sex, neutered, size class klein/mittel/gross/Riese (BLV definitions on p. 2)
- G. Reporting person or institution: name, address, date/signature
- Page 2 quotes TSchV art. 78 and § 16 HuG ZH and defines "erhebliche Verletzung" as any bite needing medical/veterinary consultation regardless of severity.
- Page: https://www.zh.ch/de/umwelt-tiere/tiere/haustiere-heimtiere/hunde/vorfaelle-mit-hunden-melden.html
- Form: https://www.zh.ch/content/dam/zhweb/bilder-dokumente/themen/umwelt-tiere/tiere/veterinaeramt/hunde/formulare-merkblaetter/hu_fo_huak_meldungvorfaelle_def1.pdf

**Bern**, Amt für Veterinärwesen (AVET). Three forms, "Das Dokument ist an die obige Adresse zu mailen":
- 771x22 "Meldung von Hundebissverletzungen beim Tier" (V260810), *"Meldungen mit diesem Formular sind Tierärzten vorbehalten"*: owner of the bitten dog; bitten animal (species, age, breed, ID no. (TVD – AGATE), sex, neutered, weight; "Angaben obligatorisch"); police report; date/time; place (public, at the dog's home, in the bitten/biting dog's territory); relationship; one/several bites; type of injury; location; **Schweregrad** (Bagatell / leicht / mittel / schwer); keeper of the biting dog; description of the biting dog (whether it comes from a person present; breed/mix, microchip, sex, colour, size class); date, place, name/stamp of sender.
  https://www.weu.be.ch/content/dam/weu/dokumente/avet/de/hunde/771x22-FO-Meldung-Hundebissverletzung-Tier-de.pdf
- 771x21 "… beim Menschen" (V260810), reserved for doctors; anonymised victim data (sex, age) are archived.
  https://www.weu.be.ch/content/dam/weu/dokumente/avet/de/hunde/771x21-FO-Meldung-Hundebissverletzung-Mensch-de.pdf
- 771x20 "Meldung eines Hundes, welcher Anzeichen eines auffälligen Verhaltens zeigt" (V211101), for vets, trainers, shelters, police, municipalities: reporter's function and identity; police report; date/time; place; what happened (own observation / third-party account); keeper; dog description.
  https://www.weu.be.ch/content/dam/weu/dokumente/avet/de/hunde/771x20-FO-Meldung-aggressive-Hunde-de.pdf

**Vaud**, DGAV – Affaires vétérinaires, Police des chiens. "Formulaire pour l'annonce de blessures par morsure de chien chez l'animal (Annonce faite par le / la vétérinaire)", headed "FORMULAIRE OFFICIEL (art. 78 al. 1 lit b. de l'Ordonnance sur la protection des animaux)" [sic: lit. a covers injuries]. Sent by post or to the e-mail on the form. Owner of the bitten animal *"ne remplir qu'avec l'accord explicite du propriétaire"*; bitten animal (species, age, breed, ID no. (BDTA-ANIS), sex, neutered, weight; mandatory); police complaint; date/time; place; one/several bites; type; location; **gravité** (légère / moyenne / grave); keeper of the biting dog; description (breed, pedigree, colour, coat, size class, sex, neutered, distinctive signs); date, signature and stamp of the vet.
- https://www.vd.ch/fileadmin/user_upload/themes/vie_privee/animaux/fichiers_pdf/2022/Pol_chiens/DGAV_FORM_morsure_chien_cong%C3%A9n%C3%A8re.pdf
- Loi sur la police des chiens (LPolC, RSV 133.75, 31 Oct 2006), art. 24: vets, doctors, municipalities, police and dog educators must report to the service dogs that (a) injured or attacked people or animals, (b) show behavioural disorders. The PDF opened is the **original 2006 text** from vd.ch; I did not check the consolidated version. https://www.vd.ch/fileadmin/user_upload/themes/vie_privee/animaux/fichiers_pdf/Loi_sur_la_police_des_chiens.pdf

**Common to the CH forms.** All three ask for the same core fields: reason, incident date/time/place, police report, injury type and location, a severity grade or size class as tick boxes, keeper of the biting dog, the dog's breed/chip/sex/colour, and the reporter's identity with signature. ZH and VD require the injured party's consent before their identity or treatment details are passed on.

## Italy

**O.M. 6 agosto 2013**, "Ordinanza contingibile ed urgente concernente la tutela dell'incolumità pubblica dall'aggressione dei cani" (GU SG n. 209 of 6 Sep 2013), as amended by O.M. 3 Aug 2015 (art. 1 c. 5 only, owner training courses):
- art. 1 c. 6: "Il medico veterinario libero professionista informa i proprietari di cani in merito alla disponibilità di percorsi formativi e, nell'interesse della salute pubblica, segnala ai servizi veterinari dell'azienda sanitaria locale la presenza, tra i suoi assistiti, di cani che richiedono una valutazione comportamentale in quanto impegnativi per la corretta gestione ai fini della tutela dell'incolumità pubblica."
- art. 1 c. 7: after bites, aggression or other risk criteria, the municipality decides on the vet services' advice which owners must attend courses.
- art. 3 c. 1: "Fatto salvo quanto stabilito dagli articoli 86 e 87 del DPR 320/1954 …, a seguito di morsicatura o aggressione i servizi veterinari attivano un percorso mirato all'accertamento delle condizioni psicofisiche dell'animale e della corretta gestione da parte del proprietario." c. 2–4: high-risk dogs, register, liability insurance, leash and muzzle.
- Text (IZS copy of the GU text): https://www.izs.it/IZS/Engine/RAServeFile.php/f/pdf_normativa/Iuvene_normativa_nazionale_animali_affezione/Ordinanza_06_agosto_2013.pdf
- 2013–2024 compilation (OIPA): https://oipa.org/italia/leggi/LEGGI_NAZIONALI/ANIMALI_DI_PROPRIETA/Ordinanza%20aggressione%20cani_2013-2024.pdf

**In force in 2026: O.M. 16 luglio 2026**, "Proroga dell'ordinanza contingibile e urgente 6 agosto 2013 e successive modificazioni…", GU SG **n. 206 of 5 Sep 2026** (pp. 3–4), registered at the Corte dei conti on 24 Aug 2026. Art. 1: the 2013 ordinance, last extended by O.M. 10 Jul 2025 (GU n. 192 of 20 Aug 2025), is extended by **12 months from 5 Sep 2026**. No change to the text. Opened as the GU page reproduced by Certifico: https://www.certifico.com/component/attachments/download/63512

**DPR 320/1954 arts. 86–87.** Normattiva (session-loaded article views): art. 86 (biting dogs and cats isolated and observed for 10 days, home observation on request) and art. 87 (animals bitten by rabid/unknown animals) were in force 9 Jul 1954 – 26 Sep 2022; from 27 Sep 2022 both read "PROVVEDIMENTO ABROGATO DAL D.LGS. 5 AGOSTO 2022, N. 136". https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1954-02-08;320

**Regional/ASL practice.**
- Regione Emilia-Romagna, Direzione generale cura della persona, salute e welfare, note to the AUSLs, Ordini dei medici and Ordini dei veterinari, after the confirmed rabies case in a dog in Vittorio Veneto (Ministry note prot. 0017128 of 8 Jun 2026). It says: *"È essenziale che tutti gli episodi di morsicatura da parte di animali detenuti siano tempestivamente segnalati al Servizio Veterinario della AUSL dai medici e dai veterinari libero professionisti che ne vengano a conoscenza. La segnalazione dell'episodio di morsicatura deve essere effettuata anche nel caso in cui il morsicato sia un animale."* The service assesses risk (traceability, valid rabies vaccination, wildlife contact, travel in the last 6 months, unprovoked bite or behaviour change followed by death within 10 days). With risk factors: first visit as soon as possible, second visit 10 days after the bite. With founded suspicion: observation ≥ 10 days from the bite in an approved shelter. Owners, keepers and private vets notify any suspected rabies case within 12 hours (Reg. (EU) 2016/429 art. 18; D.Lgs. 136/2022 art. 2 c. 1 lett. g). Opened via OMCeO Parma: https://www.omceopr.it/wp-content/uploads/2026/07/Circolare-Ministero-della-Salute.pdf
- AUSL Valle d'Aosta, "Gestione responsabile animali d'affezione" (2026 version): after a bite the owner/keeper must contact the veterinary service; the biting or bitten animal is examined and may be observed for a period that varies by case; the bite report goes to the Ambulatorio veterinario della S.C. Sanità animale by PEC. https://www.ausl.vda.it/Media/AUSL/Hierarchy/66/6655/Gestione%20responabile%20animali%20daffezione%20versione%202026.pdf

**Fields.** There is no national form. The letter uses the same core fields as the Swiss forms, plus the observation dates and the rabies line. ASLs typically ask for their own form.

## What the module does with this

- `opts.to` is the office **the vet names**. No cantonal or ASL address is hard-coded, although ZH, BE and VD print theirs on the forms.
- `opts.reason` covers injury to a person, injury to an animal, or aggression, matching the ZH Meldegrund boxes. `opts.patient_role` says whether the record's patient is the biting dog or the injured animal. Only then do header/ctx identity (chip, breed, sex, age, weight, owner) go to that animal. The other animal holds only what the vet typed.
- The severity grade, the size class and the injury-type boxes are **not** filled. They are listed in `left_to_vet`, and the vet ticks them on the official form. The vet's own severity description is printed.
- CH: if the injured party's identity or treatment details are entered without `injured.consent === true`, they are not printed. A warning is added and `injured.consent` goes into `missing` (ZH footnote, VD form).
- IT: the observation start and end are listed as missing until the vet types them, and an end date is never computed. The rabies 12-hour line is printed as a static note.
- Languages: CH in German (default) or Italian (Ticino, OPAn wording), IT in Italian, and EN for reference. No FR, because the site has no French. The Vaud form exists only in French; a vet in Vaud would transcribe onto it.

## Could not open / not checked

- **Ticino** forms (Formulario notifica morsi animali / persone, Direttiva UFV notifica cani pericolosi on www4.ti.ch): the connection was reset each time. I know them only from search snippets, so the module cites nothing from them.
- Basel-Landschaft "Vorfälle mit Hunden" page: HTTP 403.
- Vaud "annonce chien agressif" professional form (2018 URL): 404. The current consolidated LPolC was not checked.
- Lombardia R.R. 13 aprile 2017 n. 2 (bite provisions): the ATS Brescia link gave a 404 and the Monza mirror was refused by the proxy.
- Regione Piemonte determinazione 2026 on suspected rabies: the connection was reset.
- Ministry notes prot. 0016351 of 4 Jun 2025 and prot. 0017128 of 8 Jun 2026: known only as quoted in the ER note.
- D.Lgs. 136/2022 itself (to confirm which article, if any, carries a bite-observation rule): not opened.
- The GU issue of 5 Sep 2026 directly on gazzettaufficiale.it: the connection was reset. I read the same GU pages through Certifico's copy.
- CH rabies/observation rules (TSV): not researched. Switzerland is officially rabies-free, and TSchV art. 78 does not deal with observation.
- Austria: out of scope here; see `docs/19` §5b.
