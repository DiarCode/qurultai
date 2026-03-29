import DOMPurify from "dompurify";
import MarkdownIt from "markdown-it";

const markdown = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  typographer: true,
});

const defaultLinkOpen: NonNullable<typeof markdown.renderer.rules.link_open> =
  markdown.renderer.rules.link_open ??
  ((tokens, idx, options, _env, self) => self.renderToken(tokens, idx, options));

markdown.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  const token = tokens[idx];
  if (!token) {
    return defaultLinkOpen(tokens, idx, options, env, self);
  }
  token.attrSet("target", "_blank");
  token.attrSet("rel", "noreferrer noopener");
  return defaultLinkOpen(tokens, idx, options, env, self);
};

export function renderMarkdownHtml(source: string) {
  const normalized = source.trim();
  if (!normalized) {
    return '<p class="q-streaming-placeholder">Preparing answer…</p>';
  }

  const rendered = markdown.render(normalized);
  return DOMPurify.sanitize(rendered, { USE_PROFILES: { html: true } });
}
