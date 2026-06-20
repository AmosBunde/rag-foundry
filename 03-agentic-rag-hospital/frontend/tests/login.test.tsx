import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LoginPage from "@/app/login/page";

const pushMock = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock }),
}));

vi.mock("@/lib/api", () => ({
  login: vi.fn(),
}));

import { login } from "@/lib/api";

const mockedLogin = vi.mocked(login);

describe("LoginPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it("submits valid credentials and stores the token", async () => {
    mockedLogin.mockResolvedValueOnce({
      access_token: "test-token",
      token_type: "bearer",
    });

    render(<LoginPage />);

    const username = screen.getByLabelText(/username/i);
    const password = screen.getByLabelText(/password/i);
    const submit = screen.getByRole("button", { name: /sign in/i });

    await userEvent.type(username, "demo");
    await userEvent.type(password, "demo");
    await userEvent.click(submit);

    await waitFor(() => {
      expect(mockedLogin).toHaveBeenCalledWith("demo", "demo");
    });
    expect(localStorage.getItem("agentic_rag_hospital_token")).toBe("test-token");
    expect(pushMock).toHaveBeenCalledWith("/chat");
  });

  it("shows validation errors for empty fields", async () => {
    render(<LoginPage />);

    const submit = screen.getByRole("button", { name: /sign in/i });
    await userEvent.click(submit);

    expect(await screen.findByText(/username is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/password is required/i)).toBeInTheDocument();
    expect(mockedLogin).not.toHaveBeenCalled();
  });
});
