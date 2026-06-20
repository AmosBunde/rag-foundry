import { test, expect } from "@playwright/test";

test.describe("authentication", () => {
  test("login page renders and validates empty submission", async ({ page }) => {
    await page.goto("/login");

    await expect(page.getByRole("heading", { name: "Corrective RAG" })).toBeVisible();

    const submit = page.getByRole("button", { name: /sign in/i });
    await expect(submit).toBeVisible();
    await submit.click();

    await expect(page.getByText(/username is required/i)).toBeVisible();
    await expect(page.getByText(/password is required/i)).toBeVisible();
  });
});
