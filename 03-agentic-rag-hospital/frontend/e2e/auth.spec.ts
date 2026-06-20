import { test, expect } from "@playwright/test";

test.describe("authentication", () => {
  test("login page renders and validates empty submission", async ({ page }) => {
    await page.goto("/login");

    await expect(page.getByRole("heading", { name: "Agentic RAG Hospital" })).toBeVisible();

    await page.getByRole("button", { name: /sign in/i }).click();

    await expect(page.getByText(/username is required/i)).toBeVisible();
    await expect(page.getByText(/password is required/i)).toBeVisible();
  });
});
