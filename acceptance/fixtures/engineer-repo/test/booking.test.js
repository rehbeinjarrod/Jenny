import { test } from "node:test";
import assert from "node:assert/strict";
import { quote } from "../src/booking.js";

test("quote is exported", () => {
  assert.equal(typeof quote, "function");
});
