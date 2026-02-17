# ADR Quality Feedback Study — Survey Instrument

## Administration Notes

- Administer via online survey tool (e.g., LimeSurvey, Qualtrics)
- Pilot with 5–10 students before full deployment
- Estimated completion time: 15–20 minutes
- All responses are anonymous; do not collect identifying information
- A third party (colleague or TA) should administer — the instructor must not know who participated until after grades are assigned

---

## SECTION A: Demographics (5 items)

**A1.** What is your current program of study?
- [ ] Bachelor's in Computer Science / Software Engineering
- [ ] Bachelor's in Information Technology
- [ ] Master's in Computer Science / Software Engineering
- [ ] Master's in Information Technology
- [ ] Other (please specify): ___________

**A2.** What year of study are you currently in?
- [ ] 1st year
- [ ] 2nd year
- [ ] 3rd year
- [ ] 4th year or above
- [ ] Graduate student

**A3.** Before this course, how many Architectural Decision Records (ADRs) had you written?
- [ ] None
- [ ] 1–2
- [ ] 3–5
- [ ] 6–10
- [ ] More than 10

**A4.** How frequently do you use AI tools (e.g., ChatGPT, GitHub Copilot) in your studies?
- [ ] Never
- [ ] Rarely (a few times per semester)
- [ ] Sometimes (weekly)
- [ ] Often (multiple times per week)
- [ ] Daily

**A5.** How would you rate your current competence in software architecture? (1 = Novice, 5 = Expert)
- [ ] 1 — Novice
- [ ] 2 — Advanced beginner
- [ ] 3 — Competent
- [ ] 4 — Proficient
- [ ] 5 — Expert

---

## SECTION B: Technology Acceptance Model (TAM) — Adapted (12 items)

*Adapted from Davis (1989). Likert scale: 1 = Strongly Disagree to 7 = Strongly Agree.*

### Perceived Usefulness (PU)

**PU1.** Using AI-generated feedback helped me improve the quality of my ADRs.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**PU2.** The AI feedback pointed out issues I would not have identified on my own.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**PU3.** The AI feedback helped me understand what makes a good ADR.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**PU4.** The AI feedback was relevant to the specific content of my ADR.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**PU5.** Using AI feedback made my ADR writing process more efficient.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**PU6.** Overall, I found the AI feedback useful for learning about ADR quality.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

### Perceived Ease of Use (PEU)

**PEU1.** The AI feedback was easy to understand.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**PEU2.** It was clear what actions I should take based on the AI feedback.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**PEU3.** The scoring dimensions used by the AI were easy to understand.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**PEU4.** The format of the AI feedback report was well-organized.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**PEU5.** I did not need additional help to interpret the AI feedback.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**PEU6.** Overall, I found the AI feedback system easy to use.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

---

## SECTION C: System Usability Scale (SUS) — Standard 10 Items

*Standard SUS (Brooke, 1996). Likert scale: 1 = Strongly Disagree to 5 = Strongly Agree.*
*SUS scoring: For odd items subtract 1; for even items subtract response from 5. Sum all items and multiply by 2.5. Score range: 0–100. Above 68 = above average.*

**SUS1.** I think that I would like to use this feedback system frequently.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐

**SUS2.** I found the feedback system unnecessarily complex.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐

**SUS3.** I thought the feedback system was easy to use.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐

**SUS4.** I think that I would need the support of a technical person to be able to use this system.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐

**SUS5.** I found the various functions in this system were well integrated.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐

**SUS6.** I thought there was too much inconsistency in this system.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐

**SUS7.** I would imagine that most people would learn to use this system very quickly.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐

**SUS8.** I found the system very cumbersome to use.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐

**SUS9.** I felt very confident using the system.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐

**SUS10.** I needed to learn a lot of things before I could get going with this system.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐

---

## SECTION D: Feedback Quality Perception (10 items)

*Likert scale: 1 = Strongly Disagree to 7 = Strongly Agree.*

**FQ1.** The feedback accurately identified the strengths of my ADR.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**FQ2.** The feedback accurately identified the weaknesses of my ADR.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**FQ3.** The improvement suggestions were specific enough to act on.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**FQ4.** The feedback helped me understand why certain aspects of my ADR needed improvement.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**FQ5.** The dimension-by-dimension scoring was more helpful than a single overall grade.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**FQ6.** I trusted the accuracy of the AI-generated scores.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**FQ7.** The feedback contained errors or hallucinations that reduced my trust.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**FQ8.** The AI feedback was comparable in quality to instructor feedback.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**FQ9.** The immediacy of the AI feedback (vs. waiting for instructor feedback) was valuable.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

**FQ10.** I would recommend this feedback tool to other students writing ADRs.
> 1 ☐  2 ☐  3 ☐  4 ☐  5 ☐  6 ☐  7 ☐

---

## SECTION E: Open-Ended Questions (5 items)

**E1.** What aspect of the AI feedback was MOST helpful for improving your ADR? Please provide a specific example if possible.

> _______________________________________________________________
> _______________________________________________________________
> _______________________________________________________________

**E2.** What aspect of the AI feedback was LEAST helpful or most problematic? Please provide a specific example if possible.

> _______________________________________________________________
> _______________________________________________________________
> _______________________________________________________________

**E3.** How does the AI feedback compare to instructor feedback you have received? What are the main differences?

> _______________________________________________________________
> _______________________________________________________________
> _______________________________________________________________

**E4.** Did you notice any errors, hallucinations, or misleading suggestions in the AI feedback? If so, please describe.

> _______________________________________________________________
> _______________________________________________________________
> _______________________________________________________________

**E5.** What improvements would you suggest for the AI feedback system?

> _______________________________________________________________
> _______________________________________________________________
> _______________________________________________________________

---

## Semi-Structured Interview Guide (8–12 participants)

*For purposive sampling across quality levels and feedback conditions.*
*Target: theoretical saturation (typically 8–12 participants).*
*Duration: 30–45 minutes per interview.*

### Opening
1. Can you describe your general experience writing ADRs in this course?
2. How confident did you feel about your ADR quality before receiving feedback?

### AI Feedback Experience
3. Walk me through how you used the AI feedback. What did you do first? What did you focus on?
4. Can you give me a specific example of a suggestion that was particularly helpful? What did you change?
5. Can you give me a specific example of a suggestion that was unhelpful, confusing, or incorrect?
6. How did the dimension-by-dimension scores (completeness, rationale depth, etc.) influence your revision process?

### Comparison with Instructor Feedback
7. How did the AI feedback compare to the instructor feedback you received? In what ways was it better or worse?
8. If you could only receive one type of feedback (AI or instructor), which would you choose and why?
9. Did the AI feedback change your expectations for instructor feedback?

### Trust and Learning
10. How much did you trust the AI scores? Were there moments where you disagreed with the AI's assessment?
11. Do you feel you learned more about ADR quality from the AI feedback, the instructor feedback, or both equally?
12. Has this experience changed how you think about using AI tools for learning?

### Closing
13. Is there anything else about your experience with the AI feedback system that you'd like to share?

---

## Scoring Instructions

### SUS Scoring
1. For odd-numbered items (SUS1, SUS3, SUS5, SUS7, SUS9): score = response - 1
2. For even-numbered items (SUS2, SUS4, SUS6, SUS8, SUS10): score = 5 - response
3. Sum all 10 adjusted scores
4. Multiply by 2.5
5. Result: 0–100 scale. >68 = above average, >80 = good, >85 = excellent

### TAM Scoring
1. Compute Cronbach's alpha for PU items (PU1–PU6) — target ≥ 0.7
2. Compute Cronbach's alpha for PEU items (PEU1–PEU6) — target ≥ 0.7
3. Report PU and PEU means with 95% confidence intervals
4. If alpha < 0.7, examine item-total correlations for potential removals

### Feedback Quality Scoring
1. Reverse-score FQ7 (higher = fewer errors)
2. Compute mean across FQ1–FQ10 for overall feedback quality score
3. Report individual item means for detailed analysis
