# Tag Team (ChatGPT plugin)

Your AI teammate. It keeps your operating instructions, your memory, your skills and your pending
work on the Tag Team server, and loads them into a conversation when you ask it to.

This is the ChatGPT packaging of the same Tag Team that ships for Claude Code. Same skill, same
server, same account. Only the wrapper differs.

## What it needs

- A ChatGPT plan that allows plugins: Business, Enterprise or Edu with developer mode turned on by
  an admin, or Pro with developer mode on.
- A Tag Team account. You sign in once, in your browser, the first time the plugin reaches the
  server.

## Install

See `INSTALL-ChatGPT.md` in this folder.

## Use it

- Say **whoomp** to wake it up at the start of a conversation.
- Say **tag** later on to pull in anything that changed since.

## Install this or a product plugin, not both

Tag Team and the BotBuilders product plugins (AI CMO and friends) connect to two different Tag Team
hosts. Your tools are decided by your account, not by which plugin you installed, so installing both
means signing in twice and then seeing two copies of the same tools under two different names.
Pick one.

## Good to know

- **It starts from your context, not from nothing.** Before it answers anything about your work it
  loads what you have already told it.
- **If it says it has no context,** the sign-in did not complete. Remove the plugin, install it
  again, and approve the sign-in screen when it appears.

Questions: support@botbuilders.com
