import test from "node:test";
import assert from "node:assert/strict";
import {emails} from "./data.js";
test("dataset has 50 unique synthetic emails",()=>{assert.ok(emails.length>=50);assert.equal(new Set(emails.map(e=>e.id)).size,emails.length);});
test("emails have supported risk levels",()=>{assert.ok(emails.every(e=>["low","medium","high"].includes(e.risk)));});
