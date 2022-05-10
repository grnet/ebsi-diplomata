import { useMemo } from "react";
import useSWR from "swr";

export type UserInfo = { name: string, value: string }[];
export interface UserDetails {
  user: UserInfo | null;
  processing: boolean;
  error?: string;
}

export const TOKEN_KEY = 'ebsi-auth-token';

export function useAuthToken(): string {
  return window.localStorage.getItem(TOKEN_KEY) as string;
}

export function fetchUserFromToken(token): Promise<UserInfo | null> {
  const headers = new Headers();
  headers.append('Authorization', 'Token ' + token)
  return window.fetch('/api/v1/users/current/', {
    headers: headers,
  }).then((resp) => {
    return resp.json().then((data) => {
      if (data && data.errors) {
        //window.localStorage.removeItem(TOKEN_KEY)
        return null;
      }
      return Object.keys(data.data).map((key) => {
        return {
          name: key, 
          value: data.data[key],
        }
      }).filter((item) => item.value !== undefined);
    }).catch(() => {
      return null;
    })
  })
}

export function fetchTokenFromCode(code: string): Promise<string | null> {
  return window.fetch('/api/v1/token/?code=' + code).then((resp) => {
    return resp.json().then((data) => {
      if (data && data.errors) {
        return null;
      }
      return data.data.token;
    })
  })
}

type TokenInfo = {
  processing: boolean;
  token: string | null;
  error?: any;
};

export function useTokenFromCode(code): TokenInfo {
  const { data, error } = useSWR<string | null>(code, fetchTokenFromCode)
  const state = useMemo<TokenInfo>(() => {
    const processing = code ? (data === undefined && !error) : false;
    return {
      token: data || null,
      processing: processing,
      error: error
    }
  }, [code, data, error]);
  return state;
}

export function useUserDetails(): UserDetails {
  const token = useAuthToken();
  const { data, error } = useSWR<UserInfo | null>(token, fetchUserFromToken)
  const state = useMemo<UserDetails>(() => {
    const processing = token ? (data === undefined && !error) : false;
    return {
      user: data || null,
      processing: processing,
      error: error
    }
  }, [token, data, error]);
  return state
}