---
id: CR-1
type: change-request
title: "Personas koda pārbaude iesniegumā"
status: READY
priority: high
reporter: "Reģistrācijas nodaļa (izdomāts)"
owner: "@<github-lietotājvārds>"
contract: "docs/openapi.yaml · POST /submissions · personalCode"
depends_on: []
exported: "2026-09-30 · Ezermalas pieteikumu sistēma (simulācija)"
data_check: "Nav personas datu, iekšējo adrešu vai pielikumu"
---

# CR-1 · Personas koda pārbaude iesniegumā

> Noteikumi vienkāršoti mācību vajadzībām.

## Apraksts (description)

Iesniegumos bieži ir nepareizi personas kodi. Sistēmai jāpārbauda, vai personas kods ir derīgs, un nederīgi iesniegumi jānoraida.

## Pieņemšanas kritēriji (acceptance criteria)

| # | Ievade (`personalCode`) | Sagaidāmais rezultāts |
|---|---|---|
| 1 | Vecais formāts, derīgs (01.01.1990): `01019012349` un `010190-12349` | 201 |
| 2 | Jaunais formāts, derīgs kontrolcipars: `32123456785` un `321234-56785` | 201 |
| 3 | Atstarpes sākumā un beigās: `" 010190-12349 "` | 201 (atstarpes nogrieztas) |
| 4 | Nepareizs kontrolcipars: `01019012340`, `32123456780` | 400 `VALIDATION_ERROR`, lauks `personalCode`, `INVALID_FORMAT` |
| 5 | Neeksistējošs datums (29.02.1901): `29020112341` | 400 `VALIDATION_ERROR`, lauks `personalCode`, `INVALID_FORMAT` |
| 6 | Datums nākotnē (01.01.2030): `01013021236` | 400 `VALIDATION_ERROR`, lauks `personalCode`, `INVALID_FORMAT` |
| 7 | Vecais formāts, dzimis 2020. gadā vai vēlāk (01.01.2025): `01012521239`; gadsimta cipars `0` (1800. gadi) | 400 `VALIDATION_ERROR`, lauks `personalCode`, `INVALID_FORMAT` |
| 8 | Nepareizs garums, burti vai citi sākuma cipari: `0101901234`, `01019O12349` | 400 `VALIDATION_ERROR`, lauks `personalCode`, `INVALID_FORMAT` |
| 9 | Lauka nav, `""` vai tikai atstarpes | 400 `VALIDATION_ERROR`, lauks `personalCode`, `REQUIRED` |
| 10 | `010190-12349` | Saglabāts normalizēts: `01019012349` (`GET /submissions/{id}` un OMD pieprasījumā) |
| 11 | Testa kods `32000000001`, `ALLOW_TEST_PERSONAL_CODES=true` | 201 |
| 12 | Testa kods `32000000001`, iestatījums nav uzstādīts (noklusējums) | 400 `VALIDATION_ERROR`, lauks `personalCode`, `INVALID_FORMAT` |
| 13 | `32000000003` (nav sarakstā), `ALLOW_TEST_PERSONAL_CODES=true` | 400 `VALIDATION_ERROR`, lauks `personalCode`, `INVALID_FORMAT` |

## Precizējumi (clarifications)

| Jautājums | Atbilde | Kas atbildēja, kad |
|---|---|---|
| Vai defise ir atļauta? | Jā, abos formātos: `DDMMGG-CNNNN`, `32NNNN-NNNNN` un 11 cipari bez defises | <programmer>, 2026-10-05 |
| Kuri kodu veidi ir derīgi? | Vecais (sākas ar dzimšanas datumu) un jaunais (sākas ar `32`) | <programmer>, 2026-10-05 |
| Kā pārbaudīt kontrolciparu? | Abos formātos: svari 1,6,3,7,9,10,5,8,4,2; (1101 − summa) mod 11 = 11. cipars | <programmer>, 2026-10-05 |
| Gadsimta cipars vecajā formātā? | `1` = 1900. gadi, `2` = 2000. gadi; `0` (1800. gadi) nav derīgs | <programmer>, 2026-10-05 |
| Datuma pārbaude vecajā formātā? | Datumam jāeksistē, nedrīkst būt nākotnē; dzimušajiem no 2020-01-01 ir tikai `32` kodi | <programmer>, 2026-10-05 |
| Atstarpes sākumā un beigās? | Nogriezt | <programmer>, 2026-10-05 |
| Tukšs lauks vai tikai atstarpes? | `REQUIRED` | <programmer>, 2026-10-05 |
| Kur pārbaudīt? | API un formā (`ui/index.html`) pirms nosūtīšanas | <programmer>, 2026-10-05 |
| Kā glabāt? | Normalizēti: 11 cipari bez defises un atstarpēm | <programmer>, 2026-10-05 |
| Ko darīt ar esošajiem sintētiskajiem `32…` kodiem, kuri neiztur kontrolciparu? | Izņēmums: fiksēts saraksts (`32000000001`, `002`, `101`, `102`, `103`, `404`, `408`, `500`, `503`, `999`), derīgs tikai ar `ALLOW_TEST_PERSONAL_CODES=true`; noklusējumā izslēgts, ražošanā netiek ieslēgts | <programmer>, 2026-10-05 |

## Ārpus tvēruma (out of scope)

- Pārbaude, vai persona tiešām eksistē reģistrā
- Esošo sintētisko kodu nomaiņa (tiek lietots izņēmumu saraksts)

## Komentāri (comments)

- 2026-09-28 · Reģistrācijas nodaļa: "Vakar 12 iesniegumi ar nepareizu kodu. Visi jālabo ar roku."
