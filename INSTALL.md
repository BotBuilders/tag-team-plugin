# Installing Tag Team

About two minutes, most of it waiting.

## Before you start

You need Claude Code on your computer. If you don't have it yet, get it at
[claude.com/code](https://claude.com/code) and sign in. If you already have it, make sure it's
up to date — run `claude update`.

## Step 1 — Run two commands

Open your terminal and paste these one at a time:

```
claude plugin marketplace add BotBuilders/tag-team-plugin
```

```
claude plugin install tag-team@tag-team
```

The first tells Claude where to find Tag Team. The second installs it.

## Step 2 — Restart Claude Code

Quit it and start it again. Plugins only load at startup.

## Step 3 — Sign in once

The first time Tag Team reaches for your account, a browser window opens asking you to sign in and
approve access. Do that once per computer and you're done.

## Using it

Three ways to wake it up:

| Say this | What happens |
|---|---|
| **whoomp** | Wakes it up and loads everything — your notes, your instructions, what's waiting on you |
| **tag** | Later in the same conversation, pulls in anything that changed |
| **/tag-in** | Same as whoomp, if you'd rather type a command |

Start a session with **whoomp** and it knows who you are, what you've told it before, and what's
in its queue. Skip that and it's just a generic assistant.

## Don't install this next to AI CMO

Tag Team and the BotBuilders product plugins (AI CMO and friends) sign in to two different places.
Install both and you'll be asked to sign in twice, and then you'll see two copies of the same tools
with slightly different names — confusing for you and for Claude. Pick whichever one you actually
use.

## If something looks wrong

**"It doesn't remember anything about me."** You probably didn't say **whoomp**. Nothing loads until
you do.

**"It's asking me to sign in again."** Normal on a new computer. Also happens if you were signed
out.

**"It says a tool isn't available on my plan."** Tag Team is the full version of the product. If
your account is on the skills-library-only plan, some tools are switched off —
email support@botbuilders.com.

## Removing it

```
claude plugin uninstall tag-team@tag-team
claude plugin marketplace remove tag-team
```

---

Questions: support@botbuilders.com
