# Installing Tag Team in ChatGPT

Two pieces: turn on developer mode, then install the plugin. Signing in to Tag Team happens on
first use.

## Step 1. Turn on developer mode

Plugins in ChatGPT sit behind developer mode.

- **Business:** an admin turns it on for the workspace. Members cannot turn it on for themselves.
- **Enterprise or Edu:** an admin grants access, then you turn it on under Settings, Security and
  login, Developer mode.
- **Pro:** Settings, Security and login, Developer mode.

## Step 2. Install the plugin

Pick the route that matches how you received it.

**From the BotBuilders marketplace (a folder or GitHub repo containing `.agents/plugins/marketplace.json`).**
Add that marketplace in ChatGPT's Plugins area, then install **Tag Team** from the Plugins
Directory. The plugin brings its own connection to the Tag Team server; there is nothing else to
add.

**From the universal directory.** If BotBuilders has published Tag Team to ChatGPT's plugin
directory, find it there and install it. Same result.

## Step 3. Sign in once

The first time Tag Team reaches the server, ChatGPT opens a Tag Team sign-in and a consent screen
naming the permissions. Approve it once per account.

## Step 4. Wake it up

Start a new conversation with the plugin enabled and say:

- **whoomp** — loads your context: your instructions, your skills, your settings, your pending work.
- **tag** — later in the same conversation, pulls in anything that changed since.

Then just talk to it. There are no commands to learn.

## If something looks wrong

**"It answers like it has never met me."** It did not load your context. Say **whoomp** and see
whether it signs you in. If nothing happens, the plugin is not enabled for that conversation.

**"There is no Plugins area" or "developer mode is greyed out."** Your plan or workspace policy
does not allow it yet. On Business, ask your admin to turn on developer mode for the workspace.

**"It keeps asking me to sign in."** Normal on a new device or after being signed out. If it loops,
remove the plugin, install it again, and approve the consent screen when it appears.

**"I see two of every tool."** You have Tag Team and a BotBuilders product plugin installed at the
same time. Remove one.

Questions: support@botbuilders.com
