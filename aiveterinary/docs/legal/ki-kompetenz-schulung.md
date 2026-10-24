**Status: draft. Have it checked before you rely on it for compliance.** Date: 18 October 2026.

# AI literacy for clinic teams using AI Veterinary

A 45-minute session for vets, nurses, TFA and reception staff, with a short check at the end. It covers what the people who use the workspace need to know to use it safely. Keep the signed attendance list (last page) with the clinic's records.

## Why the clinic does this

- **EU AI Act, Article 4:** providers and deployers of AI systems take measures to ensure a sufficient level of AI literacy among the staff who use them, taking into account their knowledge, experience and the context of use. *The wording of Article 4 was amended in 2026 (Reg. (EU) 2026/1744, per our market research); check the current text before citing it.*
- **Germany:** the Federal Veterinary Chamber's AI guidance (October 2026) says that anyone who wants to use AI must first acquire AI competence (No. 1), that the vet's own final check is required (No. 5), and that training for vets and their support staff is mandatory (No. 9).
- **Italy:** D.Lgs. 179/2026 makes AI training part of the professional orders' continuing education (from 23 October 2026, per our market research; *the text has not been checked by us*).

## Part 1 (10 min): what the tool is and is not

1. The workspace turns the vet's **typed** notes into a structured record. It never listens; there is no microphone.
2. It may only use what is in the notes. Every fact in the record points back to the words it came from; hover over it to see them.
3. It does not diagnose, suggest treatment or calculate doses. If a dose, route, frequency or test result is not in the notes, the record shows **▲ Missing**, never a guess.
4. Nothing leaves the workspace until a vet approves it. A nurse can prepare and hand over; only a vet can approve.
5. Language models can produce text that reads well and is wrong. The checks catch much of it, not all of it. **The vet's own final check is what makes the record correct.**

## Part 2 (15 min): how errors look, with the demo cases

Open aiveterinary.org/vets/workspace and go through these synthetic cases together:

| Case | What to notice |
|---|---|
| A dose not given | The drug is listed; the dose is flagged as missing, not filled in |
| A pregnant owner | The notes mention the owner's pregnancy; it must not end up in a male dog's record |
| Another pet | The owner talks about a second animal; that is not this patient's history |
| Planned, not done | "Bloods next visit" is planned, not performed |
| Decimal comma | "38,9" is 38.9 °C, not 389 |

For each one, ask: what would have gone wrong on a busy day if nobody looked?

## Part 3 (10 min): your responsibilities

- **Read before you approve.** Approval means you have checked every line against the patient, not only the flagged ones.
- **Tick every medication row** against your notes. Approval is blocked until you do.
- **Mark gaps honestly.** Type the missing value if you know it; otherwise mark it "not recorded". Never type a value you did not establish.
- **Corrections are new versions.** An approved record is never overwritten; a change needs a reason and creates the next version, and documents made from the old one are listed as out of date.
- **Owners are told.** Hang up the owner notice (DE: `hinweis-ki-tierhalter-de.md`, IT: `informativa-uso-ia-it.md`) and do not remove the AI note on approved documents.
- **Secrecy.** Paste only what belongs in the record. Do not paste owner phone numbers, addresses or anything about other clients.

## Part 4 (10 min): check and sign

Each participant answers in writing; the trainer goes through the answers with the group.

1. The record shows "▲ Missing: dose" for amoxicillin. You know the dose. What do you do? *(Type the dose you actually gave or prescribed; the record keeps it as entered by you at approval.)*
2. The record says "vomiting for 3 days" and your notes say "vomiting since yesterday". What do you do? *(Do not approve as it stands. Correct it to what your notes say, and report it to AI Veterinary as an error. The automatic checks catch invented numbers in vital signs, doses and test results, but not every change of wording in free text; that is why you read every line.)*
3. Who may approve a record? *(Only a veterinarian.)*
4. An owner asks whether a computer decided their dog's treatment. What do you say? *(No. The vet decided; the tool only tidied the vet's own notes into the record.)*
5. You notice a mistake in a record approved last week. What do you do? *(Amend it: give a reason, approve the new version, regenerate the documents listed as out of date.)*

## Attendance

| Name | Role | Date | Signature |
|---|---|---|---|
| | | | |

Trainer: ____________________ · Clinic: ____________________

## To check before use

1. Current wording of Article 4 AI Act after Reg. (EU) 2026/1744.
2. D.Lgs. 179/2026, Art. 47: whether this session can count towards ECM or other continuing-education credits in Italy, and with which provider.
3. Whether the Landestierärztekammer recognises the session for continuing-education hours (ATF or chamber rules).
4. Example answer 1 assumes the workspace records values entered at approval as the vet's own; this is how it works today (`app/src/export.ts`, "Entered by the vet at approval").
