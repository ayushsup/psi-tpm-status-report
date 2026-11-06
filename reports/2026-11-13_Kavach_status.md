# Weekly status – Kavach
**To:** Nirmal Finance (CTO)  
**From:** Ayush Supakar, PanScience Innovations  
**Week:** 09 Nov – 13 Nov 2026  

## Overall status: 🔴 Red
**Next milestone:** Client UAT starts – **Thu 12 Nov 2026**  
**Main point this week:** 4/50 test calls quoted a wrong EMI amount; telecom IP change needs client network approval (3 working days); AI engineer on leave Wed–Fri. Go-live Mon 16 Nov proposed as phased pilot, decision Fri 13 Nov.

## Open risks and issues (highest score first, max 6)
- **K-01 – Issue (P: High, I: High) ⚠️ OVERDUE**: Agent quoted the wrong EMI amount in 4 of 50 internal test calls. Cause unknown (data lookup vs. model reading the amount).
  - *Action:* Pull call logs, compare agent output with loan record for all 50 calls; identify cause; fix and re-run 50 calls. Arjun supports on the data side. — owner **Meera**, due Tue 10 Nov 2026
- **K-04 – Risk (P: High, I: High) ⚠️ OVERDUE**: AI engineer (Meera) on leave Wed–Fri, during final fixes, UAT and go-live preparation.
  - *Action:* All AI-side root causes closed by Tue 17:00; Meera writes a handover note; Arjun named backup; Meera reachable for one 30-min call if Sev-1. — owner **Ayush**, due Tue 10 Nov 2026
- **K-02 – Issue (P: High, I: High) ⚠️ OVERDUE**: Telecom provider changed IP addresses; client network team must approve new list; approval takes 3 working days. Without it no UAT call connects.
  - *Action:* Send IP list to Nirmal CTO Mon 10:00; get named contact; daily chase; test call from client network Wed evening. — owner **Dev**, due Wed 11 Nov 2026
- **K-03 – Issue (P: Medium, I: High) ⚠️ OVERDUE**: 2 of 50 calls dropped at ~40 seconds (suspected session/telephony timeout).
  - *Action:* Reproduce with a 3-minute scripted call; check provider session timeout and keep-alive; fix on staging; add long-call UAT case. — owner **Dev**, due Tue 10 Nov 2026
- **K-05 – Issue (P: High, I: Medium) ⚠️ OVERDUE**: AI cost of test calls is 40% above budget. Group CTO needs cause by Wed.
  - *Action:* Export per-call tokens/minutes; test hypotheses (model tier per turn, uncached long prompt, retries after drops, call length); written note to CTO Wed 10:00; set daily cost alert. — owner **Meera**, due Wed 11 Nov 2026
- **K-06 – Risk (P: Medium, I: High)**: Go-live Mon 16 Nov with MD present: only 2 UAT days to find and fix defects; reputational risk if borrowers hear wrong amounts.
  - *Action:* Propose phased go-live (pilot batch Mon, full volume Thu); go/no-go Fri 13 Nov 16:00 with client CTO; go-live checklist in T6. — owner **Ayush**, due Fri 13 Nov 2026

## Actions due in the next 7 days
- Fri 13 Nov 2026: Propose phased go-live (pilot batch Mon, full volume Thu); go/no-go Fri 13 Nov 16:00 with client CTO; go-live checklist in T6. (**Ayush**)

## Closed since last report
- None.

## Where we need you
- No action pending on your side this week; please reply if anything above is a surprise.

_Open items: 7 · Overdue: 6 · Generated 2026-11-13 from the project tracker._