import { test, expect } from "@playwright/test";

test("login page renders", async ({ page }) => {
  await page.goto("/login");
  await expect(page.locator("text=Graph RAG")).toBeVisible();
  await expect(page.locator("button:has-text('Sign in')")).toBeVisible();
});
