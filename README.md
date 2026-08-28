# Tag Team

Your AI teammate, in Claude Code. It keeps your operating instructions, your memory, your skills
and your pending work on the server, and loads them into a session when you ask it to.

## Install

```bash
claude plugin marketplace add BotBuilders/tag-team-plugin
claude plugin install tag-team@tag-team
```

Restart Claude Code. The first time the connection is used you will be asked to sign in to
Tag Team in your browser and approve access. That is a one-time step per machine.

## Use it

- Say **whoomp** to wake it up at the start of a session.
- Say **tag** later on to pull in anything that changed.
- Or type **/tag-in** to do it explicitly.

## Install this or a product plugin, not both

Tag Team and the BotBuilders product plugins (AI CMO and friends) connect to two different
Tag Team hosts. Your tools are decided by your account, not by which plugin you installed, so
installing both means signing in twice and then seeing two copies of the same tools under two
different names. Pick one.

## Uninstall

```bash
claude plugin uninstall tag-team@tag-team
claude plugin marketplace remove tag-team
```

## Requirements

Claude Code 2.1.247 or newer.
