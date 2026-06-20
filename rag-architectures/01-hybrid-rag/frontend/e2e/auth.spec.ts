import { test, expect } from "@playwright/test";

test.describe("authentication", () => {
  test("login page renders with form fields", async ({ page }) => {
    await page.goto("/login");

    await expect(page.getByRole("heading", { name: "Hybrid RAG" })).toBeVisible();

    const username = page.getByLabel(/username/i);
    const password = page.getByLabel(/password/i);
    const submit = page.getByRole("button", { name: /sign in/i });

    await expect(username).toBeVisible();
    await expect(password).toBeVisible();
    await expect(submit).toBeVisible();
    await expect(submit).toBeEnabled();
  });
});
