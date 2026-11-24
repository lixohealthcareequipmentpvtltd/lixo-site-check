# lixo-site-check

Outside check of the Lixo live site (outage 24-Nov-2026, plan item 8). It works even when both the server and
the office Mac are down.

- **Every 30 minutes**, GitHub's own runner opens `https://erp.lixo.co.in/health/ready`. That page answers 200
  only when the database answers too.
- **Down 2 tries in a row** (20 s apart): the run goes red, and GitHub e-mails the owner. One issue
  **"Live site check failing"** opens, and GitHub e-mails the repo watchers. While that issue is open, no new
  issue is made.
- **Back:** a "back" comment is added and the issue closes by itself.
- **Fire drill:** Actions → site-check → *Run workflow*, with a wrong page (for example
  `https://erp.lixo.co.in/health/nope`). Expect a red run, the issue and the e-mail. Then run it again with the
  default page: a "back" comment, and the issue closes.

**Why public:** public repos get free Actions minutes, so this never uses the 2,000 private minutes that
lixo-agents CI needs. This repo holds no code and no secrets, only the public URL.

**Keep-alive:** GitHub pauses scheduled runs after 60 days with no commit, so a monthly job commits `.keepalive`.

**Who gets the e-mails:**
- red runs: the account that last changed the schedule line, shown under GitHub → Settings → Notifications → Actions;
- issues: everyone who watches this repo.

Turn off: Actions → site-check → "Disable workflow".

Part of the plan in lixo-agents (`deploy/RESTORE.md`). The other alarms are the server disk alarm (item 2) and the
Mac watchdog (item 3).
