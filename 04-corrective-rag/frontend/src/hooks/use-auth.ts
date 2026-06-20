"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clearToken, getToken, setToken } from "@/lib/auth";

export function useAuth() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    setIsAuthenticated(!!getToken());
  }, []);

  const login = (token: string) => {
    setToken(token);
    setIsAuthenticated(true);
    router.push("/chat");
  };

  const logout = () => {
    clearToken();
    setIsAuthenticated(false);
    router.push("/login");
  };

  return { isAuthenticated, login, logout };
}
