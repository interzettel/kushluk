# Local first-run setup (F-008 first slice)

**Feature:** F-008 · **Issues:** [#5](https://github.com/interzettel/kushluk/issues/5), [#12](https://github.com/interzettel/kushluk/issues/12) · **Release target:** proposed v1.0.0, but implementation is partial.

Kuşluk can create an owner-owned local profile without cloud accounts, automation services, identity tracking, RSS feed activation, or paid inference. The CLI runs **offline**. Use interactive prompts:

```bash
kushluk setup
# Home label, latitude, longitude, IANA timezone; optional printer via flag
```

Or use explicit values without prompts (suitable for local scripting):

```bash
kushluk setup --non-interactive \
  --home-name "My Home" \
  --latitude 52.52 --longitude 13.405 \
  --timezone "Europe/Berlin"
```

The example location is illustrative. Choose **your own approximate coordinates** for localized weather; exact home address is not needed.

Profile file: `~/.config/kushluk/profile.json` or `$XDG_CONFIG_HOME/kushluk/profile.json`. `--output OTHER_PATH` creates an alternate file; select it on future runs using `KUSHLUK_PROFILE_FILE=OTHER_PATH`. Only the display label, numeric latitude/longitude, IANA timezone, and an optional CUPS printer queue name are saved. It is a **mode-0600 local create-only file**, never overwritten by a repeat setup run. It does not contain SMTP credentials, RSS feed URLs, personal articles, mailbox secrets, permission records or outside-service tokens. Output is JSON status that does not repeat your location coordinates.

Normal existing settings support is preserved. Once created, `Settings.from_env()` uses local profile values as defaults; **explicit environment variables still override them**: `KUSHLUK_HOME_NAME`, `KUSHLUK_LATITUDE`, `KUSHLUK_LONGITUDE`, `KUSHLUK_TIMEZONE`, `KUSHLUK_PRINTER`. An older installation without a profile retains its historical defaults. A malformed/tampered profile errors rather than being ignored. You can modify or remove your own local profile manually, with a backup, to restart setup.

**This is not the finished onboarding experience.** It does not automatically detect your location, manage calendars/newsletters, set up actual CUPS printers or launch a scheduled service. Use [OPML and approved sources](OPML.md) for explicit subscription permissions, then `kushluk sources-preflight` for offline inventory and optional `--network` health checks. Use `kushluk doctor` for installed PDF/driver checks, and [FIELD_ACCEPTANCE.md](FIELD_ACCEPTANCE.md) for real physical printer and reboot acceptance. Storing coordinates locally is your choice; do not upload private profile files as issue attachments.

## Browser setup — first local UI slice

On the computer where Kuşluk is installed, run:

```bash
kushluk setup-web
# Or keep the browser closed and open the printed local URL yourself:
kushluk setup-web --no-open
```

This starts a **temporary local HTTP page**, accessible at a randomly selected `http://127.0.0.1:PORT/` URL. It binds exclusively to numeric IPv4 loopback, not the LAN or a public address. A simple responsive form explains what is saved, asks for an approximate location and IANA timezone, and lets you name an optional printer queue. Only the existing `profile.json` is created, with owner-only permissions. The browser never contacts a provider, imports feeds, runs a scheduler, prints a document, or checks any subscription. The process is stopped with **Ctrl+C** in its terminal.

Safety properties: exact loopback Host and form Origin checks, a random per-server CSRF token, strict accepted form fields and 4-KiB POST limit, explicit no-cache/CSP/referrer headers, no remote JavaScript/fonts/images, no cookies or third-party analytics, sanitized error messages, and no profile overwrite. Its threat boundary is a trusted personal computer; this is not a remote multi-user administration server. **Do not port-forward or reverse-proxy it.** The form does not edit previously saved settings; if a profile already exists, the page instructs you to manage the local file rather than silently overwrite it.

Browser setup is one improved step, not complete F-008 acceptance. It still needs installation packaging, an accessible/source consent walkthrough, actual printer hardware detection/driver setup and observed nontechnical first-run usability testing.

## Next step — review source feeds in the browser

With the same local `kushluk setup-web` process running, follow **Review your sources** or open the browser's `/sources` page. This is **not** a public website.

1. Paste a small OPML reading list (up to **50 feeds** per review). Kuşluk validates it **entirely offline** and holds it as a temporary, unapproved browser-session proposal. It does not save the pasted OPML or contact the feeds.
2. Review the proposed feed titles and hosts. Kuşluk intentionally hides private feed URLs/query tokens from the browser preview. Explicitly tick the per-feed acknowledgement, then press **Approve this feed only**. A new approval is stored in the existing local, private source registry as **reference-only**. No article text copying, synthesis or public distribution right is inferred.
3. Under **Your approved feeds**, you can **Pause** any approved feed immediately. **Resume** requires a fresh explicit permission acknowledgement. `derivative` and `private-direct` remain disabled, not selectable through this browser.
4. Your review list lasts only as long as the local setup process; closing/restarting it clears unapproved proposals. Previously approved registry entries persist. Refreshing does not start requests. CLI import/approval workflows remain supported.

The browser applies loopback-only Host and Origin checks, CSRF validation, bounded form bodies, XML DTD/ENTITY rejection, and escaped user-supplied titles. There is **no background feed fetching**: use `kushluk sources-preflight --network` later if you deliberately want to test connectivity. A site that grants RSS access still might prohibit copying its full articles. This UI does not make that determination.

**Still outstanding:** assistive-technology/novice usability testing, a real print-driver wizard, source/provider-specific rights evidence, and observed hardware/reliability acceptance. Do not enable a new source without access authorization.

For a reproducible independent novice trial, use [FIRST_READER_PILOT.md](FIRST_READER_PILOT.md) and the blank [FIRST_READER_TEMPLATE.json](FIRST_READER_TEMPLATE.json). Do not count authored instructions or simulated CI as an observed participant.
