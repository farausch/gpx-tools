import NextAuth from "next-auth";
import { authOptions } from "@/lib/authOptions";

export const POST = NextAuth(authOptions);
export const GET = NextAuth(authOptions);