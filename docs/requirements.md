# Requirements

- **Built in about an hour, live.** Why: it is a build-in-public event.
- **Shareable while live.** The demo runs in a GitHub Codespace with its
  port set to public. Why: no paid hosting; the link only needs to work
  during the event.
- **One app, one toolchain.** Python only; no Node build step. Why:
  fewer moving parts on stream.
- **No third-party hosts at runtime.** Assets are served by the app.
  Why: the demo should not break because a CDN does.
- **No Anthropic or Claude branding.** Why: the page is public and must
  not pass for an official product.
