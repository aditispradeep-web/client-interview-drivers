# How to talk about this project in an interview

## The 60-second version
"I did a practice project for a career coaching business. The question was which job-search habits lead to interviews, and how to spot clients who are about to go quiet. I built an example data set of 80 clients, cleaned it in Python and SQL, built a one-page funnel dashboard (a Power BI version is in progress), and fitted a simple model on first-two-week behaviour. The main findings: a third of sign-ups never sent a first application, and clients who followed up within 4 days got about five times the interview rate of clients who never followed up. CV quality mattered more than volume. I recommended a 48-hour first-application target, earlier follow-up prompts, and a day-14 check-in rule that would have caught 15 of the 16 clients who went quiet."

## Questions you will probably get

**Why make the data messy?** Real exports are messy. I added mixed date formats, inconsistent channel labels, missing values, a duplicated row and impossible values (31+ active days, negative gaps), then cleaned them. Cleaning steps are at the top of the notebook.

**How did you handle missing values?** I left them out of the specific cut instead of filling them in. Filling a CV match score with an average would have blurred the exact relationship I was measuring.

**Why logistic regression?** It's simple, it's explainable, and the weights tell a coach what to act on. With 60 active clients, a complex model would overfit. I used 5-fold cross-validation and balanced class weights, because only 16 clients went quiet.

**Your AUC is 0.94. Isn't that too good?** Yes. It's example data, so the signal is cleaner than real life. That's why I also gave a plain rule (fewer than 5 applications and no follow-up by day 14) that a coach can use without a model.

**Correlation or causation?** Correlation. Motivated clients may follow up faster and also do everything else better. To prove it, I'd A/B test moving the follow-up reminder earlier and compare interview rates.

**What would you do next with real data?** Add time-based features (week-by-week activity), check the role and sector mix, and track whether flagged clients who got a check-in actually re-engaged.

## Where it goes on your CV
In a **Projects** section, never under work experience:
> **What makes a client land interviews** (practice project, example data). Python, SQL, Excel, Jira. Wrote the BRD and user stories, built a funnel dashboard and a day-14 early-warning model for client drop-off. Found that follow-up within 4 days was associated with about 5x the interview rate. Recommended 3 product changes. github.com/aditispradeep-web/client-interview-drivers
>
> Add Power BI to this line only once the Power BI version is built.

## LinkedIn post (as published)
> I've just finished a practice business analysis project: what makes a job seeker land interviews?
> Using an example data set of 80 clients (made-up numbers, built from a real business brief), I worked through it end to end, the way a BA would:
> • Requirements in a BRD, with a process map of the client journey
> • A Jira backlog of user stories with acceptance criteria
> • Data cleaning and analysis in Python and SQL, plus an Excel model
> • A one-page dashboard (Power BI version in progress), and a simple model that flags clients at risk of going quiet
> Three things stood out:
> 1. A third of sign-ups never sent a first application. That's the biggest drop-off.
> 2. Following up within 4 days was linked to about 5x the interview rate of never following up.
> 3. CV match quality mattered more than application volume.
> Everything is on GitHub: https://github.com/aditispradeep-web/client-interview-drivers
> Thanks to Dylan Corrigan for the brief and feedback.
> #BusinessAnalysis #DataAnalytics #PowerBI #SQL #Jira #Python
