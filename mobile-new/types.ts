// types.ts
export interface User {
  id: number;
  username: string;
  createdAt: string;
}

export interface Message {
  id: number;
  text: string;
  username: string;
  userId: number;
  sentiment: string;
  sentimentScore: number;
  createdAt: string;
}

export interface RegisterResponse {
  userId: number;
  username: string;
  isNew: boolean;
  message: string;
}