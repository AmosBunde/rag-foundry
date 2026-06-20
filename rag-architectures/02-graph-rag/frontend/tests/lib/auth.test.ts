import { describe, expect, it } from "vitest";
import { getToken, setToken, clearToken } from "@/lib/auth";

describe("auth token helpers", () => {
  it("stores and retrieves a token", () => {
    setToken("abc123");
    expect(getToken()).toBe("abc123");
  });

  it("clears the token", () => {
    setToken("abc123");
    clearToken();
    expect(getToken()).toBeNull();
  });
});
