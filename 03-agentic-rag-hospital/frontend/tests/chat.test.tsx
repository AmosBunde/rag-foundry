import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import userEvent from "@testing-library/user-event";
import ChatPage from "@/app/chat/page";

const pushMock = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock }),
}));

vi.mock("@/lib/api", () => ({
  queryAgent: vi.fn(),
}));

import { queryAgent } from "@/lib/api";

const mockedQuery = vi.mocked(queryAgent);

describe("ChatPage", () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem("agentic_rag_hospital_token", "token");
  });

  it("submits a query and displays reasoning", async () => {
    mockedQuery.mockResolvedValueOnce({
      query: "What is diabetes?",
      answer: "Diabetes is a chronic condition.",
      plan: ["Retrieve", "Verify", "Respond"],
      reasoning: [
        { agent: "planner", step: "created_plan", detail: {} },
        { agent: "responder", step: "generated_answer", detail: {} },
      ],
      sources: [{ id: "s1", text: "Source 1", score: 0.9, metadata: {}, source: "fusion" }],
      safety_checks_passed: true,
      disclaimer: "Disclaimer appended.",
      latency_ms: 120,
    });

    render(<ChatPage />, { wrapper });

    const input = screen.getByPlaceholderText(/ask a medical question/i);
    const submit = screen.getByRole("button", { name: /ask agent/i });

    await userEvent.type(input, "What is diabetes?");
    await userEvent.click(submit);

    await waitFor(() => {
      expect(mockedQuery).toHaveBeenCalledWith("What is diabetes?", "", 5);
    });
    expect(await screen.findByText(/Diabetes is a chronic condition/i)).toBeInTheDocument();
  });
});
