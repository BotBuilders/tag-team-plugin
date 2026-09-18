---
name: tag-in
description: Loads this account's Tag Team context — operating instructions, skills index, settings, and pending work — from the Tag Team server. Use at the start of a session, when the user says "whoomp" or "tag", when they mention Tag Team, their Clone, their memory, or their pending jobs, or before acting on anything that depends on their saved context.
---

# Tag In

Nothing about this account is known until you call `tag_in`. It is the only source of the
account's operating instructions, its skills index, and its pending work.

## Do this first

Call `tag_in` before any other reply or action — including clarifying questions. It takes no
arguments.

Call it again when the user says "tag", or mentions Tag Team or their Clone. That re-syncs
instructions, skills and jobs that changed since the last call.

## What comes back

| Field | What it is | What to do with it |
|---|---|---|
| `user` | Who this is, and their organization | Address them by name; never guess their pronouns |
| `instructions` | Full bodies of the account's Tag-In skills | **Binding.** These override your defaults |
| `skills` | An index only — name, type, description | Fetch a body with `get_skill` before relying on it |
| `jobs` | The next pending job and the last completed one | Report status; don't invent progress |
| `gate` | Pending counts and open captures | See the warning below |
| `settings` | Resolved account settings | Follow them |

## Two things that will trip you up

**`skills` has no bodies.** Names and descriptions only. Acting on a skill you have not fetched
with `get_skill` means acting on a one-line summary.

**`gate.pending_total` is not the sum of `gate.pending_by_kind`.** It deliberately includes open
captures, which are not a job kind. Report the two separately or you will contradict yourself.

## Memory is not in the bundle

The bundle carries no memory index — that omission is deliberate, not a bug. To see what this
account remembers, call the `memory` tool with `command: "view"` and no path.

## Red flags

- Answering a question about this account's work before calling `tag_in`
- Treating a `skills` entry as if you had read it
- Reporting `pending_total` as the job count
- Re-calling `tag_in` on every message instead of on "tag"
