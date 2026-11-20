// No dependencies: execute the Cloudflare Worker handler under Node's Web APIs.
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const source = await readFile(new URL("./worker.js", import.meta.url), "utf8");
const encoded = Buffer.from(source).toString("base64");
const { default: worker } = await import(`data:text/javascript;base64,${encoded}`);
const store = new Map();
const env = {
  ALLOWED_ORIGIN: "https://sassnarep3-star.github.io",
  COUNTS: {
    async get(key) { return store.get(key) ?? null; },
    async put(key, value) { store.set(key, value); }
  }
};

async function post(body, origin = env.ALLOWED_ORIGIN) {
  return worker.fetch(new Request("https://metrics.example/collect", {
    method: "POST", headers: { "Content-Type": "application/json", Origin: origin },
    body: JSON.stringify(body)
  }), env);
}

const accepted = await post({
  event: "outbound_click", page: "products/item.html", site: "attacker",
  at: "1999-01-01T00:00:00Z",
  props: { asin: "b0cdy277d3", email: "reader@example.test", query: "private" }
});
assert.equal(accepted.status, 202);
assert.equal(accepted.headers.get("Access-Control-Allow-Origin"), env.ALLOWED_ORIGIN);
assert.equal(store.size, 1);
const [key, count] = [...store.entries()][0];
assert.equal(count, "1");
const parsedKey = JSON.parse(key);
assert.equal(parsedKey[1], "outbound_click");
assert.equal(parsedKey[2], "products/item.html");
assert.equal(parsedKey[3], "B0CDY277D3");
assert.ok(!key.includes("reader@example.test") && !key.includes("private"));
assert.notEqual(parsedKey[0], "1999-01-01");

const guide = await post({
  event: "guide_read", page: "guides/example.html",
  props: { depth: "50-89", email: "reader@example.test" }
});
assert.equal(guide.status, 202);
assert.equal(store.size, 2);
assert.ok([...store.keys()].some(k => JSON.parse(k)[4] === "50-89"));

for (const body of [
  { event: "purchase", page: "index.html" },
  { event: "page_view", page: "../private" },
  { event: "page_view", page: "index.html?email=x" }
]) {
  const response = await post(body);
  assert.equal(response.status, 422);
}

const disallowedOrigin = await worker.fetch(new Request("https://metrics.example/health", {
  headers: { Origin: "https://not-the-site.example" }
}), env);
assert.equal(disallowedOrigin.headers.get("Access-Control-Allow-Origin"), null);
console.log("Worker analytics contract: OK");
