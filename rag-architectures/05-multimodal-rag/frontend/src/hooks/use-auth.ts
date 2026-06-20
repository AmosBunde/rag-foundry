"use client";

import { useEffect, useState } from "react";

import { clearToken, getToken, setToken } from "@/lib/auth";

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    setIsAuthenticated(!!getToken());
  }, []);

  const login = (token: string) => {
    setToken(token);
    setIsAuthenticated(true);
  };

  const logout = () => {
    clearToken();
    setIsAuthenticated(false);
    window.location.href = "/login";
  };

  return { isAuthenticated, login, logout };
}
